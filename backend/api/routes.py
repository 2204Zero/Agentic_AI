from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import uuid

from services.github_service import clone_repo, extract_code_files
from config.database import get_db
from config.redis_client import redis_client

from models.db_models import User, CodeSubmission, Job
from models.schemas import CodeRequest

from services.aggregator import aggregate_results, calculate_repo_score
from services.llm_aggregator import generate_final_summary
from services.vector_store import store_repo_chunks, query_repo, collection
from utils.llm import call_llm

from utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter()


# ---------------- AUTH ---------------- #

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    if len(password) > 72:
        raise HTTPException(status_code=400, detail="Password too long")

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=email,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()

    return {"message": "User created"}


# ---------------- ANALYZE CODE ---------------- #

@router.post("/analyze-code")
async def analyze_code(
    request: CodeRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    submission = CodeSubmission(code=request.code)
    db.add(submission)
    db.commit()
    db.refresh(submission)

    job = Job(
        submission_id=submission.id,
        status="pending",
        retry_count=0
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    redis_client.lpush(
        "job_queue",
        json.dumps({"job_id": job.id})
    )

    return {
        "job_id": job.id,
        "status": "queued"
    }


# ---------------- ANALYZE REPO ---------------- #

@router.post("/analyze-repo")
async def analyze_repo(
    repo_url: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # ✅ CREATE repo_id ONLY ONCE
    repo_id = str(uuid.uuid4())

    # clone + extract
    repo_path = clone_repo(repo_url)
    files = extract_code_files(repo_path)

    # ✅ STORE EMBEDDINGS (RAG)
    store_repo_chunks(repo_id, files)

    job_ids = []

    for file in files:
        submission = CodeSubmission(code=file["content"])
        db.add(submission)
        db.commit()
        db.refresh(submission)

        job = Job(
            submission_id=submission.id,
            repo_id=repo_id,
            status="pending",
            retry_count=0
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        redis_client.lpush(
            "job_queue",
            json.dumps({"job_id": job.id})
        )

        job_ids.append(job.id)

    return {
        "message": "Repo analysis started",
        "repo_id": repo_id,
        "total_files": len(job_ids),
        "job_ids": job_ids
    }


# ---------------- REPO RESULT ---------------- #

@router.get("/repo/{repo_id}")
async def get_repo_analysis(
    repo_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    jobs = db.query(Job).filter(Job.repo_id == repo_id).all()

    if not jobs:
        raise HTTPException(status_code=404, detail="Repo not found")

    total_jobs = len(jobs)
    completed_jobs = len([j for j in jobs if j.status == "completed"])
    failed_jobs = len([j for j in jobs if j.status == "failed"])

    progress = int((completed_jobs / total_jobs) * 100)

    if completed_jobs + failed_jobs < total_jobs:
        return {
            "repo_id": repo_id,
            "status": "processing",
            "progress": progress,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "total_jobs": total_jobs
        }

    results = [job.result for job in jobs if job.result]

    if not results:
        return {
            "repo_id": repo_id,
            "status": "failed",
            "message": "No valid results generated"
        }

    final_report = aggregate_results(results)

    issues_list = [i["issue"] for i in final_report.get("top_issues", [])]

    try:
        ai_summary = await generate_final_summary(issues_list)
    except Exception:
        ai_summary = {
            "summary": "Failed to generate AI summary",
            "critical_issues": [],
            "recommendations": []
        }

    score_data = calculate_repo_score(final_report)

    return {
        "repo_id": repo_id,
        "status": "completed",
        "progress": 100,
        "report": final_report,
        "ai_summary": ai_summary,
        "score": score_data
    }


# ---------------- ASK REPO (RAG) ---------------- #

@router.post("/ask-repo")
async def ask_repo(
    repo_id: str,
    question: str,
    user=Depends(get_current_user)
):
    chunks = query_repo(repo_id, question)

    # FORCE INCLUDE DB_connection FILE (critical fix)
    try:
        all_docs = collection.get(where={"repo_id": repo_id}).get("documents", [])

        for doc in all_docs:
            text = doc.lower()

            if any(keyword in text for keyword in [
                "drivermanager",
                "getconnection",
                "password",
                "jdbc",
                "connection"
            ]):
                if doc not in chunks:
                    chunks.append(doc)
                break  # only one needed
    except Exception as e:
        print("Error fetching fallback chunks:", str(e))

    # DEBUG: print FINAL chunks used
    print("----- FINAL CHUNKS USED -----")
    for c in chunks:
        print(c[:300])
        print("-----")
    print("-----------------------------")

    if not chunks:
        return {"answer": "No relevant context found"}

    # Build context
    context = "\n\n--- CODE CONTEXT ---\n\n"
    for i, chunk in enumerate(chunks):
        context += f"[Chunk {i+1}]\n{chunk}\n\n"

    prompt = f"""
You are a senior software engineer reviewing a codebase.

STRICT RULES:
- ONLY report issues that are clearly visible in the provided code
- DO NOT assume anything not present
- DO NOT include generic issues
- Every issue MUST reference actual code behavior

TASK:
- Identify multiple real issues from the code
- For EACH issue:
    1. Describe the issue
    2. Explain WHY it is a problem
    3. Reference the code behavior (evidence)
    4. Suggest a fix

IMPORTANT:
If you are not 100% sure from code → DO NOT include that issue

Context:
{context}

Question:
{question}

Answer in structured bullet points.
"""

    answer = await call_llm(prompt)

    return {
        "answer": answer,
        "chunks_used": len(chunks),
        "context_preview": chunks[:2]
    }
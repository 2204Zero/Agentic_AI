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


# ---------------- JOB STATUS ---------------- #

@router.get("/job/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "job_id": job.id,
        "status": job.status,
        "retry_count": job.retry_count
    }

    if job.status == "completed":
        response["result"] = job.result

    if job.status == "failed":
        response["error"] = job.error

    return response


@router.get("/failed-jobs")
def get_failed_jobs(user=Depends(get_current_user)):
    jobs = redis_client.lrange("failed_jobs", 0, -1)
    return [json.loads(job) for job in jobs]


@router.post("/retry-job/{job_id}")
def retry_failed_job(
    job_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "pending"
    job.retry_count = 0
    job.error = None
    db.commit()

    redis_client.lpush(
        "job_queue",
        json.dumps({"job_id": job.id})
    )

    return {"message": "Job requeued"}


# ---------------- ANALYZE REPO ---------------- #

@router.post("/analyze-repo")
async def analyze_repo(
    repo_url: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    repo_id = str(uuid.uuid4())

    repo_path = clone_repo(repo_url)
    files = extract_code_files(repo_path)

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

    # still processing
    if any(job.status != "completed" for job in jobs):
        return {
            "repo_id": repo_id,
            "status": "processing",
            "completed_jobs": len([j for j in jobs if j.status == "completed"]),
            "total_jobs": len(jobs)
        }

    # collect results
    results = [job.result for job in jobs if job.result]

    # aggregate
    final_report = aggregate_results(results)

    # LLM summary
    issues_list = [i["issue"] for i in final_report.get("top_issues", [])]
    ai_summary = await generate_final_summary(issues_list)

    score_data = calculate_repo_score(final_report)

    return {
        "repo_id": repo_id,
        "status": "completed",
        "report": final_report,
        "ai_summary": ai_summary,
        "score": score_data
    }
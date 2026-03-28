from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.db_models import User
from utils.auth import hash_password
from models.schemas import CodeRequest
from services.pipeline import run_pipeline
from config.database import get_db
from models.db_models import CodeSubmission
from models.db_models import AnalysisResult
from utils.auth import verify_password, create_access_token
from utils.auth import get_current_user
from models.db_models import CodeSubmission, Job
import json


router = APIRouter()

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"error": "User not found"}

    if not verify_password(password, user.password):
        return {"error": "Incorrect password"}

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):

    if len(password) > 72:
        return {"error": "Password too long (max 72 characters)"}

    user = User(
        email=email,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()

    return {"message": "User created"}

@router.post("/analyze-code")
async def analyze_code(
    request: CodeRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # 1. Save code submission
    submission = CodeSubmission(code=request.code)
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # 2. Create job (instead of running AI)
    job = Job(
        submission_id=submission.id,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # 3. Return job_id instead of result
    return {
        "job_id": job.id,
        "status": job.status,
        "message": "Job created. Processing will happen asynchronously."
    }


@router.get("/job/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        return {"error": "Job not found"}

    return {
        "job_id": job.id,
        "status": job.status,
        "result": job.result,
        "error": job.error
    }
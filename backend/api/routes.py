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
async def analyze_code(request: CodeRequest, db: Session = Depends(get_db),user=Depends(get_current_user)
):

    result = await run_pipeline(request.code)

    submission = CodeSubmission(code=request.code)
    db.add(submission)
    db.commit()
    db.refresh(submission)

    analysis_result = AnalysisResult(
        submission_id=submission.id,
        analysis=json.dumps(result.get("analysis")),
        issues=json.dumps(result.get("issues")),
        fixes=json.dumps(result.get("fixes")),
        explanations=json.dumps(result.get("explanations"))
    )

    db.add(analysis_result)
    db.commit()

    return result
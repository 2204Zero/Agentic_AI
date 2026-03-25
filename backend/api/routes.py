from fastapi import APIRouter
from models.schemas import CodeRequest
from services.pipeline import run_pipeline

router = APIRouter()

@router.post("/analyze-code")
async def analyze_code(request: CodeRequest):
    result = await run_pipeline(request.code)
    return result
import json
from utils.llm import call_llm


async def generate_final_summary(issues):
    prompt = f"""
    You are a senior software engineer.

    Analyze these issues found in a codebase:

    {issues}

    Return JSON with:
    1. summary (overall code quality)
    2. scores (code_quality, maintainability, readability, robustness) [1-10]
    3. critical_issues (top 3)
    4. recommendations (improvements)

    Return ONLY valid JSON.
    Do not include explanation text.
    Do not include markdown.

    Be concise.
    """

    response = await call_llm(prompt)

    try:
        return json.loads(response)
    except Exception:
        return {
            "summary": "Failed to parse AI response",
            "raw": response
        }
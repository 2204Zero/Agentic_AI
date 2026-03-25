import json
from utils.llm import call_llm

async def run(code: str):
    prompt = f"""
You are a strict Python code analyzer.

Return ONLY a valid JSON object.
Do NOT include markdown.
Do NOT include explanations outside JSON.

JSON format:
{{
  "summary": "",
  "structures": [],
  "variables": [],
  "patterns": [],
  "potential_concerns": []
}}

Analyze this code:

{code}
"""

    response = await call_llm(prompt)

    try:
        parsed = json.loads(response)
    except:
        parsed = {
            "error": "Invalid JSON from LLM",
            "raw_output": response
        }

    return parsed
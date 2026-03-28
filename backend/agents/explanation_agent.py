from utils.llm import call_llm, extract_json

async def explanation_agent(analysis: dict):
    prompt = f"""
You are a strict JSON generator.

Rules:
- Output ONLY valid JSON
- No explanation
- No markdown
- No extra text
- Response must start with {{ and end with }}

Format:
{{
  "explanation": ""
}}

Explain the following code analysis clearly:

{analysis}
"""

    response = await call_llm(prompt)

    return extract_json(response)
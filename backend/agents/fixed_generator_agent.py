from utils.llm import call_llm, extract_json

async def run(code: str, issues: dict):
    prompt = f"""
You are a Fix Generator.

Given Python code and its issues, generate fixes.

Return ONLY valid JSON.

Format:
{{
  "fixes": [
    {{
      "issue_title": "",
      "original_snippet": "",
      "fixed_snippet": ""
    }}
  ]
}}

Code:
{code}

Issues:
{issues}
"""

    response = await call_llm(prompt)

    return extract_json(response)
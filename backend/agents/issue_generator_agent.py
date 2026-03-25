from utils.llm import call_llm, extract_json

async def run(analysis: dict):
    prompt = f"""
You are a strict Issue Generator.

Return ONLY valid JSON.
No text outside JSON.

Format:
{{
  "issues": [
    {{
      "title": "",
      "description": "",
      "severity": "",
      "confidence": ""
    }}
  ]
}}

Analysis:
{analysis}
"""

    response = await call_llm(prompt)

    return extract_json(response)
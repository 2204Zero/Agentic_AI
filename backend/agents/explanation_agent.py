from utils.llm import call_llm, extract_json

async def run(issues: dict, fixes: dict):
    prompt = f"""
You are an Explanation Agent.

Explain each issue and its fix clearly.

Return ONLY JSON.

Format:
{{
  "explanations": [
    {{
      "issue_title": "",
      "what": "",
      "why": "",
      "how": ""
    }}
  ]
}}

Issues:
{issues}

Fixes:
{fixes}
"""

    response = await call_llm(prompt)

    return extract_json(response)
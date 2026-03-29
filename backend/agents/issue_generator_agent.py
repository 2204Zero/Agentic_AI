from utils.llm import call_llm, extract_json

async def issue_generator_agent(analysis: dict):
    prompt = f"""
You are a professional code reviewer AI.

STRICT RULES:
- Return ONLY JSON
- No explanation
- No markdown
- No empty fields

Return a JSON array with REAL issues found in the code.

Each issue MUST have:
- "issue": short title
- "description": clear explanation

Return at least 3 meaningful issues.

Format:
[
  {{
    "issue": "Example issue",
    "description": "Detailed explanation"
  }}
]

Code Analysis:
{analysis}
"""

    response = await call_llm(prompt)

    # FIX: handle both string and parsed output
    parsed = response if not isinstance(response, str) else extract_json(response)

    # unwrap if needed
    if isinstance(parsed, dict) and "error" in parsed:
        return parsed["error"]

    return parsed
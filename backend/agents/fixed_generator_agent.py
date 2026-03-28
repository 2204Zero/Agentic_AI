from utils.llm import call_llm, extract_json

async def fix_generator_agent(issues: list):
    prompt = f"""
You are a strict JSON generator.

Rules:
- Output ONLY valid JSON
- No explanation
- No markdown
- No extra text
- Response must start with [ and end with ]

Format:
[
  {{
    "issue": "",
    "fix": ""
  }}
]

Based on the following issues, generate fixes:

{issues}
"""

    response = await call_llm(prompt)

    return extract_json(response)
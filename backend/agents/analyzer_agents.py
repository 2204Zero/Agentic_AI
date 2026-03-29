from utils.llm import call_llm

# IMPORT correct agents (VERY IMPORTANT)
from agents.issue_generator_agent import issue_generator_agent
from agents.fixed_generator_agent import fix_generator_agent
from agents.explanation_agent import explanation_agent


# 🔹 Analyzer Agent
async def analyzer_agent(code: str):
    prompt = f"""
You are a JSON API.

STRICT RULES:
- Return ONLY JSON
- No explanation
- No markdown
- No text before or after JSON
- If you break rules, the system will fail

Your output MUST be valid JSON.
Start with {{ and end with }}.

If you cannot comply, return:
{{ "error": "invalid" }}

Format:
{{
  "summary": "",
  "structures": [],
  "variables": [],
  "patterns": [],
  "potential_concerns": []
}}

Code:
{code}
"""

    response = await call_llm(prompt)

    return response


# 🔥 PIPELINE (clean, no wrapping, no duplicates)
async def run_pipeline(code: str):
    analysis = await analyzer_agent(code)

    # DEBUG (optional, you can remove later)
    # print("ISSUE FUNCTION USED:", issue_generator_agent)

    issues = await issue_generator_agent(analysis)
    fixes = await fix_generator_agent(issues)
    explanations = await explanation_agent(analysis)

    return {
        "analysis": analysis,
        "issues": issues,
        "fixes": fixes,
        "explanations": explanations
    }
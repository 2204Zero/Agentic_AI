from agents import (
    analyzer_agents,
    issue_generator_agent,
    fixed_generator_agent,
    explanation_agent
)

async def run_pipeline(code: str):
    analysis = await analyzer_agents.run(code)

    issues = await issue_generator_agent.run(analysis)

    fixes = await fixed_generator_agent.run(code, issues)

    explanations = await explanation_agent.run(issues, fixes)

    return {
        "analysis": analysis,
        "issues": issues,
        "fixes": fixes,
        "explanations": explanations
    }
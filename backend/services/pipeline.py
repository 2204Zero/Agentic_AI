from agents import (
    analyzer_agents,
    issue_generator_agent,
    fixed_generator_agent,
    explanation_agent
)

async def run_pipeline(code: str):
    steps = []

    steps.append("Analyzing code...")
    analysis = await analyzer_agents.run(code)

    steps.append("Detecting issues...")
    issues = await issue_generator_agent.run(analysis)

    steps.append("Generating fixes...")
    fixes = await fixed_generator_agent.run(code, issues)

    steps.append("Explaining results...")
    explanations = await explanation_agent.run(issues, fixes)

    return {
        "steps": steps,
        "analysis": analysis,
        "issues": issues,
        "fixes": fixes,
        "explanations": explanations
    }
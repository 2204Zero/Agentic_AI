def aggregate_results(file_results):
    issue_counter = {}
    issue_descriptions = {}

    for result in file_results:
        if not result:
            continue

        issues = result.get("issues", [])

        for item in issues:

            # CASE 1: dict
            if isinstance(item, dict):
                issue_text = item.get("issue", "Unknown issue")
                description = item.get("description", "")

            # CASE 2: string
            elif isinstance(item, str):
                issue_text = item
                description = ""

            else:
                continue

            issue_counter[issue_text] = issue_counter.get(issue_text, 0) + 1

            if issue_text not in issue_descriptions:
                issue_descriptions[issue_text] = description

    top_issues = [
        {
            "issue": issue,
            "description": issue_descriptions.get(issue, ""),
            "count": count
        }
        for issue, count in issue_counter.items()
    ]

    top_issues.sort(key=lambda x: x["count"], reverse=True)

    return {
        "total_files": len(file_results),
        "total_unique_issues": len(issue_counter),
        "top_issues": top_issues
    }

def calculate_repo_score(report):
    score = 100

    weights = {
        "Security Vulnerability": 10,
        "Null Reference": 8,
        "Memory Leak": 9,
        "Magic Number": 3,
        "Unused Variable": 2,
        "Unused Function": 3,
        "Code Smell": 2,
        "Inconsistent Naming Convention": 2,
        "Missing Error Handling": 6
    }

    issues = report.get("top_issues", [])

    for issue in issues:
        issue_name = issue["issue"]
        count = issue.get("count", 1)

        penalty = weights.get(issue_name, 4)  # default weight
        score -= penalty * count

    score = max(0, min(100, score))

    # grading
    if score >= 85:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 50:
        grade = "C"
    else:
        grade = "D"

    return {
        "repo_score": score,
        "grade": grade,
        "verdict": get_verdict(score)
    }


def get_verdict(score):
    if score >= 85:
        return "High quality code"
    elif score >= 70:
        return "Good but can be improved"
    elif score >= 50:
        return "Moderate issues present"
    else:
        return "Poor quality, needs major fixes"
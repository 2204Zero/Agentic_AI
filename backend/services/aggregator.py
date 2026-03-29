def aggregate_results(file_results):
    """
    Smarter aggregation:
    - deduplicate issues
    - count frequency
    - return top issues
    """

    total_files = len(file_results)

    issue_map = {}  # {issue: {count, description}}

    for result in file_results:
        issues = result.get("issues", [])

        for item in issues:
            issue_text = item.get("issue")
            description = item.get("description", "")

            if issue_text in issue_map:
                issue_map[issue_text]["count"] += 1
            else:
                issue_map[issue_text] = {
                    "description": description,
                    "count": 1
                }

    # sort by frequency (most common first)
    sorted_issues = sorted(
        issue_map.items(),
        key=lambda x: x[1]["count"],
        reverse=True
    )

    # format output
    top_issues = []
    for issue, data in sorted_issues[:10]:
        top_issues.append({
            "issue": issue,
            "description": data["description"],
            "count": data["count"]
        })

    return {
        "total_files": total_files,
        "total_unique_issues": len(issue_map),
        "top_issues": top_issues
    }

def calculate_repo_score(report):
    score = 100

    issue_count = report.get("total_unique_issues", 0)

    # simple scoring
    score -= issue_count * 5

    # clamp
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
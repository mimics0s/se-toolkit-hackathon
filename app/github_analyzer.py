"""GitHub repository analyzer for mimics0s — provides lab-specific context for excuses."""

import urllib.request
import json
import os

GITHUB_USER = "mimics0s"
GITHUB_API = f"https://api.github.com/users/{GITHUB_USER}/repos"

# Cached lab data (loaded once, not on every request)
_LAB_DATA = None


def _fetch_repos():
    """Fetch repositories from GitHub API."""
    req = urllib.request.Request(
        GITHUB_API,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "ExcuseForge"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return _get_fallback_data()


def _get_fallback_data():
    """Fallback if GitHub API is unreachable."""
    return [
        {"name": "lab-01-market-product-and-git", "description": "Market product and git basics"},
        {"name": "se-toolkit-lab-2", "description": "Deploy to remote Linux VM", "language": "Python"},
        {"name": "se-toolkit-lab-3", "description": "RESTful Backend and Testing", "language": "Python"},
        {"name": "se-toolkit-lab-4", "description": "Testing, Front-end, and AI Agents", "language": "Python"},
        {"name": "se-toolkit-lab-5", "description": "Data Pipeline & Analytics Dashboard", "language": "Python"},
        {"name": "se-toolkit-lab-6", "description": "Build an Agent", "language": "Python"},
        {"name": "se-toolkit-lab-7", "description": "Telegram Bot", "language": "Python"},
        {"name": "se-toolkit-lab-8", "description": "The Agent is the Interface", "language": "Python"},
        {"name": "se-toolkit-hackathon", "description": "Hackathon rules", "language": "Python"},
    ]


def _extract_lab_number(repo_name: str) -> int | None:
    """Extract lab number from repo name like se-toolkit-lab-3."""
    parts = repo_name.lower().split("-")
    for i, part in enumerate(parts):
        if part == "lab" and i + 1 < len(parts):
            try:
                return int(parts[i + 1])
            except ValueError:
                pass
    return None


def _analyze_repo_tech(repo: dict) -> dict:
    """Analyze a single repo for tech context."""
    name = repo.get("name", "")
    desc = (repo.get("description") or "").lower()
    lang = repo.get("language", "")
    lab_num = _extract_lab_number(name)

    tech_keywords = {
        "docker": "docker" in desc or "docker" in name or "container" in desc,
        "telegram": "telegram" in desc or "telegram" in name or "bot" in desc,
        "rest": "rest" in desc or "restful" in desc or "api" in desc or "fastapi" in desc,
        "frontend": "front" in desc or "front-end" in desc or "html" in desc,
        "testing": "test" in desc,
        "data_pipeline": "data pipeline" in desc or "etl" in desc or "analytics" in desc,
        "agent": "agent" in desc or "ai agent" in desc,
        "database": "database" in desc or "sql" in desc or "postgres" in desc or "sqlite" in desc,
        "deploy": "deploy" in desc or "vm" in desc or "linux" in desc,
        "ci_cd": "ci/cd" in desc or "ci cd" in desc or "pipeline" in desc,
    }

    # Auto-detect based on lab number patterns from known curriculum
    if lab_num:
        if lab_num == 2:
            tech_keywords["deploy"] = True
            tech_keywords["linux"] = True
            tech_keywords["docker"] = True
        elif lab_num == 3:
            tech_keywords["rest"] = True
            tech_keywords["database"] = True
            tech_keywords["testing"] = True
        elif lab_num == 4:
            tech_keywords["frontend"] = True
            tech_keywords["testing"] = True
            tech_keywords["agent"] = True
        elif lab_num == 5:
            tech_keywords["data_pipeline"] = True
            tech_keywords["database"] = True
        elif lab_num == 6:
            tech_keywords["agent"] = True
            tech_keywords["ai"] = True
        elif lab_num == 7:
            tech_keywords["telegram"] = True
            tech_keywords["bot"] = True
        elif lab_num == 8:
            tech_keywords["agent"] = True
            tech_keywords["ai"] = True
        elif lab_num == 9:
            tech_keywords["agent"] = True
            tech_keywords["ai"] = True
            tech_keywords["workflow"] = True
            tech_keywords["evaluation"] = True

    return {
        "lab_number": lab_num,
        "name": name,
        "language": lang,
        "technologies": [k for k, v in tech_keywords.items() if v],
    }


def get_lab_context(lab_number: int | None = None) -> dict:
    """Get context about the user's labs from GitHub repos."""
    global _LAB_DATA

    if _LAB_DATA is None:
        repos = _fetch_repos()
        _LAB_DATA = [_analyze_repo_tech(r) for r in repos]

    if lab_number:
        for lab in _LAB_DATA:
            if lab.get("lab_number") == lab_number:
                return lab
        return {"lab_number": lab_number, "technologies": []}

    return {
        "total_labs": len([l for l in _LAB_DATA if l.get("lab_number")]),
        "labs": [l for l in _LAB_DATA if l.get("lab_number")],
        "all_technologies": list(set(
            tech for lab in _LAB_DATA for tech in lab.get("technologies", [])
        ))
    }

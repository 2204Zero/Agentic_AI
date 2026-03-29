import os
import uuid
from git import Repo

BASE_DIR = "repos"


def clone_repo(repo_url: str) -> str:
    """
    Clones a GitHub repo into a unique folder and returns local path
    """

    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    # Extract repo name
    repo_name = repo_url.split("/")[-1].replace(".git", "")

    # Create unique folder (IMPORTANT FIX)
    unique_id = str(uuid.uuid4())[:8]
    repo_folder = f"{repo_name}_{unique_id}"

    repo_path = os.path.join(BASE_DIR, repo_folder)

    # Clone repo (no deletion needed now)
    Repo.clone_from(repo_url, repo_path)

    return repo_path


# ---------------- FILE EXTRACTION ---------------- #

ALLOWED_EXTENSIONS = [".py", ".js", ".ts", ".java", ".cpp"]
IGNORE_DIRS = ["node_modules", ".git", "dist", "build", "__pycache__"]

MAX_FILES = 50


def extract_code_files(repo_path: str):
    """
    Extracts code files from repo (limited to MAX_FILES)
    """

    code_files = []

    for root, dirs, files in os.walk(repo_path):

        # remove ignored dirs
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):

                full_path = os.path.join(root, file)

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    code_files.append({
                        "file_path": full_path,
                        "content": content
                    })

                    # limit files (important for LLM + performance)
                    if len(code_files) >= MAX_FILES:
                        return code_files

                except Exception:
                    # skip unreadable files
                    continue

    return code_files
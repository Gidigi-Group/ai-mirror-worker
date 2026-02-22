import requests
import base64
import os
import json

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ORG_NAME = os.environ.get("ORG_NAME")

REPO_PREFIX = "ai-mirror-worker"
WORKFLOW_FILE = ".github/workflows/mirror.yml"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


# ---------- FILES TO SYNC ----------
FILES = [
    "mirror.py",
    "discover_models.py",
    "priority_models.py",
    "models.txt",
    WORKFLOW_FILE,
]


def get_repos():

    url = f"https://api.github.com/orgs/{ORG_NAME}/repos?per_page=100"

    r = requests.get(url, headers=headers)
    data = r.json()

    repos = []

    for repo in data:
        name = repo["name"]

        if name.startswith(REPO_PREFIX):
            repos.append(name)

    return sorted(repos)


def get_file_content(path):

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def upload_file(repo, path):

    content = get_file_content(path)

    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/contents/{path}"

    data = {
        "message": "auto sync",
        "content": content,
        "branch": "main"
    }

    r = requests.put(url, headers=headers, json=data)

    if r.status_code in [200, 201]:
        print(f"Synced {repo}: {path}")
    else:
        print(f"Failed {repo}: {path} → {r.text}")


def trigger(repo, worker_id, total):

    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/actions/workflows/mirror.yml/dispatches"

    data = {
        "ref": "main",
        "inputs": {
            "worker_id": str(worker_id),
            "total_workers": str(total)
        }
    }

    r = requests.post(url, headers=headers, json=data)

    if r.status_code in [204, 201]:
        print(f"Triggered {repo}")
    else:
        print(f"Trigger failed {repo}: {r.text}")


repos = get_repos()

total = len(repos)

print(f"Workers detected: {total}")

for i, repo in enumerate(repos):

    print(f"\n--- Syncing {repo} ---")

    for file in FILES:
        upload_file(repo, file)

    trigger(repo, i, total)

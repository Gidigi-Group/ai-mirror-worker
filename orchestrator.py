import requests
import base64
import os

GH_PAT = os.environ.get("GH_PAT")
ORG_NAME = os.environ.get("ORG_NAME")

REPO_PREFIX = "ai-mirror-worker"

headers = {
    "Authorization": f"token {GH_PAT}",
    "Accept": "application/vnd.github+json"
}


FILES = [
    "mirror.py",
    "discover_models.py",
    "priority_models.py",
    "models.txt",
]

WORKER_WORKFLOW_SOURCE = "worker_mirror.yml"
WORKER_WORKFLOW_TARGET = ".github/workflows/mirror.yml"


def get_repos():

    url = f"https://api.github.com/orgs/{ORG_NAME}/repos?per_page=100"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise Exception(r.text)

    data = r.json()

    repos = []

    for repo in data:
        name = repo["name"]
        if name.startswith(REPO_PREFIX):
            repos.append(name)

    return sorted(repos)


def read_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def get_sha(repo, path):

    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/contents/{path}"
    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        return r.json()["sha"]

    return None


def sync_file(repo, source_path, target_path):

    content = read_file(source_path)
    sha = get_sha(repo, target_path)

    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/contents/{target_path}"

    data = {
        "message": "sovereign sync",
        "content": content,
        "branch": "main"
    }

    if sha:
        data["sha"] = sha

    r = requests.put(url, headers=headers, json=data)

    if r.status_code in [200, 201]:
        print(f"✅ {repo}: {target_path}")
    else:
        print(f"❌ {repo}: {target_path}")
        print(r.text)


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
        print(f"🚀 Triggered {repo}")
    else:
        print(f"❌ Trigger failed {repo}")
        print(r.text)


# ---------- MAIN ----------
repos = get_repos()

total = len(repos)

print(f"\nWorkers detected: {total}\n")

for i, repo in enumerate(repos):

    print(f"\n--- Syncing {repo} ---")

    # Sync core files
    for file in FILES:
        sync_file(repo, file, file)

    # Sync worker workflow automatically
    sync_file(repo, WORKER_WORKFLOW_SOURCE, WORKER_WORKFLOW_TARGET)

    trigger(repo, i, total)

import requests
import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ORG_NAME = os.environ.get("ORG_NAME")

REPO_PREFIX = "ai-mirror-worker"

WORKFLOW_FILE = "mirror.yml"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


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


def trigger(repo, worker_id, total):

    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/actions/workflows/{WORKFLOW_FILE}/dispatches"

    data = {
        "ref": "main",
        "inputs": {
            "worker_id": str(worker_id),
            "total_workers": str(total)
        }
    }

    r = requests.post(url, headers=headers, json=data)

    if r.status_code in [204, 201]:
        print(f"Triggered {repo} → ID {worker_id}")
    else:
        print(f"Failed {repo}: {r.text}")


repos = get_repos()

total = len(repos)

print(f"Total workers: {total}")

for i, repo in enumerate(repos):

    trigger(repo, i, total)

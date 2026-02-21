import os
from huggingface_hub import HfApi

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_ORG = os.environ.get("HF_ORG")

api = HfApi(token=HF_TOKEN)

print("🔎 Discovering models...")

# Get existing repos in your org
existing = set()

for repo in api.list_models(author=HF_ORG):
    existing.add(repo.id.split("/")[-1])

print(f"Existing mirrored: {len(existing)}")

# Search global models
models = api.list_models(sort="downloads", direction=-1, limit=200)

queue = []

for m in models:
    model_id = m.id
    repo_name = model_id.replace("/", "_")

    if repo_name in existing:
        continue

    queue.append(model_id)

print(f"New models discovered: {len(queue)}")

# Save queue
with open("models.txt", "w") as f:
    for m in queue:
        f.write(m + "\n")

print("✅ models.txt updated")

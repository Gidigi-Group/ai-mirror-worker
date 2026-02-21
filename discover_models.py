import os
from huggingface_hub import HfApi

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_ORG = os.environ.get("HF_ORG")

api = HfApi(token=HF_TOKEN)

print("🔎 Discovering models...")

models = api.list_models(sort="downloads", direction=-1, limit=200)

queue = []

for m in models:
    queue.append(m.id)

with open("models.txt", "w") as f:
    for m in queue:
        f.write(m + "\n")

print("✅ models.txt updated")

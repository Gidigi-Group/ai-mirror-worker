import os
from huggingface_hub import HfApi
from priority_models import priority_models

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_ORG = os.environ.get("HF_ORG")

api = HfApi(token=HF_TOKEN)

print("🔎 Discovering models...")

queue = set()

# ---------- ADD PRIORITY FIRST ----------
for model in priority_models:
    queue.add(model)

print(f"Priority models added: {len(priority_models)}")

# ---------- BROAD DISCOVERY ----------
search_queries = [
    "text-generation",
    "diffusion",
    "vision",
    "audio",
    "speech",
    "embedding",
    "multimodal",
    "code",
]

for query in search_queries:
    models = api.list_models(search=query, limit=200)

    for m in models:
        queue.add(m.id)

print(f"Total models discovered: {len(queue)}")

with open("models.txt", "w") as f:
    for model_id in queue:
        f.write(model_id + "\n")

print("✅ models.txt updated")

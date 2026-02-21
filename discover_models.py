import os
from huggingface_hub import HfApi

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_ORG = os.environ.get("HF_ORG")

api = HfApi(token=HF_TOKEN)

print("🔎 Discovering models across categories...")

search_queries = [
    "text-generation",
    "llm",
    "transformer",
    "diffusion",
    "stable-diffusion",
    "vision",
    "image",
    "audio",
    "speech",
    "whisper",
    "embedding",
    "sentence",
    "multimodal",
    "clip",
    "code",
    "agent",
    "chat",
]

queue = set()

for query in search_queries:
    print(f"Searching: {query}")
    models = api.list_models(search=query, limit=200)

    for m in models:
        queue.add(m.id)

print(f"Total discovered: {len(queue)}")

with open("models.txt", "w") as f:
    for model_id in queue:
        f.write(model_id + "\n")

print("✅ models.txt updated")

from huggingface_hub import HfApi

api = HfApi()

print("🔎 Discovering datasets...")

datasets = api.list_datasets(limit=200)

with open("datasets.txt", "w") as f:
    for d in datasets:
        f.write(d.id + "\n")

print("✅ datasets.txt updated")

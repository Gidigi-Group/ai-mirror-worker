import os
import sys
import hashlib
import csv
from huggingface_hub import HfApi, model_info, hf_hub_download, upload_file

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_ORG = os.environ.get("HF_ORG")

WORKER_ID = int(os.environ.get("WORKER_ID", "0"))
TOTAL_WORKERS = int(os.environ.get("TOTAL_WORKERS", "1"))

INDEX = int(sys.argv[1])

api = HfApi(token=HF_TOKEN)

# ---------- LOAD MODELS ----------
with open("models.txt") as f:
    models = [x.strip() for x in f.readlines() if x.strip()]

models = models[WORKER_ID::TOTAL_WORKERS]

if INDEX >= len(models):
    print("No model for this index")
    sys.exit(0)

model = models[INDEX]

# ---------- UNIQUE NAME ----------
hash_id = hashlib.sha1(model.encode()).hexdigest()[:8]
serial = str(INDEX).zfill(4)
repo_name = f"gidigi_{hash_id}_{serial}"

dest_repo = f"{HF_ORG}/{repo_name}"

print(f"\n🚀 ZERO-DISK MIRROR: {model}")
print(f"Destination: {dest_repo}\n")

# ---------- CREATE DESTINATION ----------
api.create_repo(
    repo_id=dest_repo,
    repo_type="model",
    private=False,
    exist_ok=True
)

# ---------- SERVER SIDE COPY ----------
try:

    info = model_info(model, token=HF_TOKEN)

    for file in info.siblings:

        if file.rfilename is None:
            continue

        print(f"Copying {file.rfilename}")

        # Stream download single file (temporary)
        local_path = hf_hub_download(
            repo_id=model,
            filename=file.rfilename,
            token=HF_TOKEN
        )

        upload_file(
            path_or_fileobj=local_path,
            path_in_repo=file.rfilename,
            repo_id=dest_repo,
            repo_type="model",
            token=HF_TOKEN
        )

    print("\n✅ MIRROR SUCCESS\n")

except Exception as e:

    print(f"Mirror failed: {e}")
    sys.exit(0)


# ---------- SAVE MAPPING ----------
mapping_path = os.path.join(os.environ.get("GITHUB_WORKSPACE", "."), "mapping.csv")

with open(mapping_path, "a", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([repo_name, model])

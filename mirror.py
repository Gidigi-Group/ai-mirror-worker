import os
import sys
import subprocess
import hashlib
import csv
from huggingface_hub import snapshot_download, HfApi

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_ORG = os.environ.get("HF_ORG")

if not HF_TOKEN or not HF_ORG:
    raise ValueError("HF_TOKEN or HF_ORG not set")

INDEX = int(sys.argv[1])

# ---------- LOAD MODEL LIST ----------
with open("models.txt") as f:
    models = [x.strip() for x in f.readlines() if x.strip()]

if INDEX >= len(models):
    print("No model for this index")
    exit(0)

model = models[INDEX]

# ---------- UNIQUE NAME GENERATION ----------
hash_id = hashlib.sha1(model.encode()).hexdigest()[:8]
serial = str(INDEX).zfill(4)

repo_name = f"gidigi_{hash_id}_{serial}"

print(f"\n🚀 Mirroring: {model}")
print(f"Repo Name: {repo_name}\n")

local_dir = f"/tmp/{repo_name}"

# ---------- DOWNLOAD ----------
snapshot_download(
    repo_id=model,
    local_dir=local_dir,
    local_dir_use_symlinks=False,
    token=HF_TOKEN
)

# ---------- CREATE HF REPO ----------
api = HfApi(token=HF_TOKEN)

api.create_repo(
    repo_id=f"{HF_ORG}/{repo_name}",
    repo_type="model",
    private=False,
    exist_ok=True
)

# ---------- PUSH ----------
os.chdir(local_dir)

subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "lfs", "track", "*"], check=True)

subprocess.run(["hf", "lfs-enable-largefiles", "."], check=True)

subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", "mirror"], check=True)

remote = f"https://user:{HF_TOKEN}@huggingface.co/{HF_ORG}/{repo_name}"

subprocess.run(["git", "branch", "-M", "main"], check=True)
subprocess.run(["git", "remote", "add", "origin", remote], check=True)
subprocess.run(["git", "push", "--force", "origin", "main"], check=True)

# ---------- SAVE MAPPING ----------
mapping_file = "mapping.csv"

with open(mapping_file, "a", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([repo_name, model])

print(f"\n✅ SUCCESS: {repo_name} mapped to {model}\n")

import os
import sys
import subprocess
import hashlib
import csv
import shutil
from huggingface_hub import snapshot_download, HfApi

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_ORG = os.environ.get("HF_ORG")

if not HF_TOKEN or not HF_ORG:
    raise ValueError("HF_TOKEN or HF_ORG not set")

INDEX = int(sys.argv[1])

with open("models.txt") as f:
    models = [x.strip() for x in f.readlines() if x.strip()]

if INDEX >= len(models):
    print("No model for this index")
    exit(0)

model = models[INDEX]

# ---------- UNIQUE NAME ----------
hash_id = hashlib.sha1(model.encode()).hexdigest()[:8]
serial = str(INDEX).zfill(4)
repo_name = f"gidigi_{hash_id}_{serial}"

print(f"\n🚀 Mirroring: {model}")
print(f"Repo Name: {repo_name}\n")

local_dir = f"/tmp/{repo_name}"

# ---------- CLEAN BEFORE START ----------
shutil.rmtree(local_dir, ignore_errors=True)
os.makedirs(local_dir, exist_ok=True)

# ---------- DOWNLOAD ----------
snapshot_download(
    repo_id=model,
    local_dir=local_dir,
    token=HF_TOKEN
)

# ---------- CREATE REPO ----------
api = HfApi(token=HF_TOKEN)

api.create_repo(
    repo_id=f"{HF_ORG}/{repo_name}",
    repo_type="model",
    private=False,
    exist_ok=True
)

# ---------- PUSH ----------
os.chdir(local_dir)

env = os.environ.copy()
env["GIT_LFS_SKIP_SMUDGE"] = "1"

subprocess.run(["git", "init"], check=True, env=env)
subprocess.run(["git", "lfs", "track", "*"], check=True, env=env)
subprocess.run(["hf", "lfs-enable-largefiles", "."], check=True, env=env)

subprocess.run(["git", "add", "."], check=True, env=env)
subprocess.run(["git", "commit", "-m", "mirror"], check=True, env=env)

remote = f"https://user:{HF_TOKEN}@huggingface.co/{HF_ORG}/{repo_name}"

subprocess.run(["git", "branch", "-M", "main"], check=True, env=env)
subprocess.run(["git", "remote", "add", "origin", remote], check=True, env=env)

subprocess.run(
    ["git", "push", "--force", "origin", "main"],
    check=True,
    env=env
)

# ---------- CLEAN AFTER PUSH ----------
os.chdir("/")

shutil.rmtree(local_dir, ignore_errors=True)

# remove git lfs cache
subprocess.run(["rm", "-rf", "~/.cache/huggingface"], shell=True)
subprocess.run(["rm", "-rf", "~/.git-lfs"], shell=True)

# ---------- SAVE MAPPING ----------
with open("mapping.csv", "a", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([repo_name, model])

print(f"\n✅ SUCCESS: {repo_name}\n")

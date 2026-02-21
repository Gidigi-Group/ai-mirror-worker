import os
import sys
import subprocess
from huggingface_hub import snapshot_download

HF_TOKEN = os.environ["HF_TOKEN"]
HF_ORG = os.environ["HF_ORG"]

INDEX = int(sys.argv[1])

with open("models.txt") as f:
    models = [x.strip() for x in f.readlines() if x.strip()]

if INDEX >= len(models):
    print("No model for index")
    exit()

model = models[INDEX]
repo_name = model.replace("/", "_")

print(f"Mirroring {model}")

local_dir = f"/tmp/{repo_name}"

snapshot_download(
    repo_id=model,
    local_dir=local_dir,
    local_dir_use_symlinks=False,
    token=HF_TOKEN
)

os.chdir(local_dir)

subprocess.run(["git", "init"])
subprocess.run(["git", "lfs", "track", "*"])
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "mirror"])

subprocess.run([
    "huggingface-cli",
    "repo",
    "create",
    repo_name,
    "--private",
    "--type",
    "model",
    "--token",
    HF_TOKEN
], check=False)

remote = f"https://user:{HF_TOKEN}@huggingface.co/{HF_ORG}/{repo_name}"

subprocess.run(["git", "remote", "add", "origin", remote])
subprocess.run(["git", "push", "origin", "main"])

import subprocess
import os

print("Applying fix directly to git")
try:
    subprocess.check_call(["git", "push", "origin", "linux-support-1379377040747772512", "--force"])
    print("Force pushed to linux-support branch.")
except subprocess.CalledProcessError as e:
    print(f"Failed to push: {e}")

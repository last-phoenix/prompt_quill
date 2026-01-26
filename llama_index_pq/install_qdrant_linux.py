import os
import shutil
import sys
import requests
import tarfile
import zipfile
from pathlib import Path

# Setup directories
# Assume running from llama_index_pq root or handle relative paths
BASE_DIR = Path.cwd()
if (BASE_DIR / "llama_index_pq").exists():
     # running from repo root
     BASE_DIR = BASE_DIR / "llama_index_pq"

INSTALL_DIR = BASE_DIR / "installer_files"
QDRANT_DIR = INSTALL_DIR / "qdrant"

QDRANT_URL = "https://github.com/qdrant/qdrant/releases/download/v1.12.6/qdrant-x86_64-unknown-linux-gnu.tar.gz"
WEBUI_URL = "https://github.com/qdrant/qdrant-web-ui/releases/download/v0.1.33/dist-qdrant.zip"

def download_file(url, output_path):
    print(f"Downloading {url} to {output_path}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("Download complete.")

def install_qdrant():
    if not INSTALL_DIR.exists():
        INSTALL_DIR.mkdir()

    QDRANT_DIR.mkdir(parents=True, exist_ok=True)

    # Download and extract Qdrant
    tar_path = INSTALL_DIR / "qdrant-linux.tar.gz"
    if not (QDRANT_DIR / "qdrant").exists():
        download_file(QDRANT_URL, tar_path)

        print("Extracting Qdrant...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=QDRANT_DIR)

        # Cleanup tar
        if tar_path.exists():
            tar_path.unlink()

        # Make executable
        qdrant_bin = QDRANT_DIR / "qdrant"
        if qdrant_bin.exists():
            qdrant_bin.chmod(qdrant_bin.stat().st_mode | 0o111)
            print(f"Qdrant binary installed at {qdrant_bin}")
    else:
        print("Qdrant binary already exists, skipping download.")

    # Download and extract Web UI
    zip_path = INSTALL_DIR / "dist-qdrant.zip"
    static_dir = QDRANT_DIR / "static"

    if not static_dir.exists():
        download_file(WEBUI_URL, zip_path)

        print("Extracting Web UI...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(QDRANT_DIR)

        # Rename dist to static
        dist_dir = QDRANT_DIR / "dist"
        if dist_dir.exists():
            dist_dir.rename(static_dir)

        # Cleanup zip
        if zip_path.exists():
            zip_path.unlink()
        print("Web UI installed.")
    else:
        print("Web UI already installed.")

    # Note on Data:
    # The original Windows installer downloads a large (~19GB) Qdrant snapshot with pre-indexed prompts.
    # This Linux installer SKIPS that download to keep the setup lightweight and fast.
    #
    # If you want the full experience (search capabilities with 4.9M+ prompts), you can manually download
    # the latest snapshot from Civitai: https://civitai.com/models/330412
    # Look for "Data lli 3.0" or newer.
    #
    # To use it, download the zip, extract the snapshot file, and place it in the 'qdrant/snapshots' directory
    # (you may need to create it) or configure Qdrant to load it.
    print("\n[INFO] Skipping large data download (19GB).")
    print("       To enable full search features, download the prompt database from:")
    print("       https://civitai.com/models/330412")

if __name__ == "__main__":
    install_qdrant()

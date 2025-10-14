import os
import shutil
from pathlib import Path
import platform
import requests

def get_package_file_auto(source: str) -> str:
    """
    Automatically handle package manager file from either:
      - GitHub raw file URL
      - Local file path (Windows, Linux, macOS)

    Returns the absolute path to the file.
    """
    source = source.strip()
    print(f"📂 Received package file input: {source}")  # <-- NEW LINE

    # ----------------------------- URL -----------------------------
    if source.lower().startswith(("http://", "https://")):
        print("🌐 Detected input as URL")  # <-- NEW LINE
        filename = os.path.basename(source)
        if not filename:
            raise ValueError("❌ Could not determine filename from URL")

        local_path = Path.cwd() / filename
        print(f"⬇️ Downloading file from: {source}")
        try:
            response = requests.get(source, timeout=20)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"❌ Failed to download file: {e}")

        with open(local_path, "wb") as f:
            f.write(response.content)
        print(f"✅ File downloaded successfully: {local_path}")
        return str(local_path.resolve())

    # ----------------------------- Local Path -----------------------------
    else:
        print("🖥️ Detected input as local file path")  # <-- NEW LINE
        local_file = Path(source).expanduser().resolve()
        if platform.system() == "Windows":
            local_file = Path(os.path.normpath(str(local_file)))
        else:
            local_file = Path(os.path.abspath(local_file))

        if not local_file.exists():
            raise FileNotFoundError(f"❌ File not found: {local_file}")

        dest_path = Path.cwd() / local_file.name
        if local_file != dest_path:
            shutil.copy2(local_file, dest_path)
            print(f"✅ Local file copied to: {dest_path}")
        else:
            print(f"✔ File already in current directory: {dest_path}")

        return str(dest_path.resolve())

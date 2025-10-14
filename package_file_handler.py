import os
import requests
import shutil
from pathlib import Path
import platform

def get_package_file() -> str:
    """
    Ask user how they want to provide a package manager file:
    1️⃣  GitHub raw file URL
    2️⃣  Local file path

    Works on Windows, Linux, and macOS.
    
    Returns:
        str: Absolute path to the downloaded or local file.
    """
    print("\n📦 How would you like to provide the package manager file?")
    print("1️⃣  GitHub raw file link (e.g., https://raw.githubusercontent.com/user/repo/branch/file)")
    print("2️⃣  Local file upload (provide full path)")

    choice = input("👉 Enter choice (1 or 2): ").strip()

    # -----------------------------
    # OPTION 1: GitHub Raw URL
    # -----------------------------
    if choice == "1":
        raw_url = input("🔗 Enter GitHub raw file URL: ").strip()

        if not raw_url.lower().startswith(("http://", "https://")):
            raise ValueError("❌ Invalid URL. Must start with http:// or https://")

        filename = os.path.basename(raw_url)
        if not filename:
            raise ValueError("❌ Could not determine filename from URL")

        # Normalize path using Pathlib (cross-platform)
        local_path = Path.cwd() / filename

        print(f"⬇️ Downloading file from: {raw_url}")
        try:
            response = requests.get(raw_url, timeout=20)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"❌ Failed to download file: {e}")

        with open(local_path, "wb") as f:
            f.write(response.content)

        print(f"✅ File downloaded successfully: {local_path}")
        return str(local_path.resolve())

    # -----------------------------
    # OPTION 2: Local File
    # -----------------------------
    elif choice == "2":
        local_input = input("📂 Enter full local file path: ").strip()

        # Expand ~ and resolve relative paths
        local_file = Path(local_input).expanduser().resolve()

        # Handle OS-specific path normalization
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

    else:
        raise ValueError("❌ Invalid choice. Please enter 1 or 2.")

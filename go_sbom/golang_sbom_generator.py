import subprocess
from pathlib import Path
import shutil
import os
import platform

def ensure_cdxgen():
    """Ensure cdxgen is installed and available in PATH."""
    cdxgen_path = shutil.which("cdxgen")
    if cdxgen_path:
        return  # Already installed

    print("❌ cdxgen not found. Installing globally via npm...")
    subprocess.run(["npm", "install", "-g", "@cyclonedx/cdxgen"], check=True)

    # Get npm global bin
    npm_bin = subprocess.check_output(["npm", "bin", "-g"], text=True).strip()

    # Correct PATH separator based on OS
    path_sep = ";" if platform.system() == "Windows" else ":"
    if npm_bin not in os.environ["PATH"]:
        os.environ["PATH"] = f"{npm_bin}{path_sep}{os.environ['PATH']}"

    # Check again
    cdxgen_path = shutil.which("cdxgen")
    if not cdxgen_path:
        if platform.system() == "Windows":
            cdxgen_path = shutil.which("cdxgen.cmd")
        if not cdxgen_path:
            raise EnvironmentError("❌ Could not find cdxgen after installation. Make sure npm global bin is in PATH.")

def generate_sbom(repo_path: Path, output_folder: Path, output_name: str = "sbom.json"):
    """Generate SBOM using cdxgen."""
    ensure_cdxgen()
    sbom_file = output_folder / output_name
    print(f"📦 Generating SBOM using cdxgen: {sbom_file} ...")

    cmd = ["cdxgen", "-t", "go", "-o", str(sbom_file)]
    # Use shell=True only on Windows
    subprocess.run(cmd, cwd=repo_path, check=True, shell=(platform.system() == "Windows"))
    print(f"✅ SBOM generated at {sbom_file}")
    return sbom_file

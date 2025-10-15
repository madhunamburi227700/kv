import subprocess
from pathlib import Path
import shutil
import os
import platform

# -------------------- Ensure cdxgen is installed --------------------
def ensure_cdxgen():
    """Ensure cdxgen is installed and available in PATH."""
    cdxgen_path = shutil.which("cdxgen")
    if cdxgen_path:
        return

    print("❌ cdxgen not found. Installing globally via npm...")
    subprocess.run(["npm", "install", "-g", "@cyclonedx/cdxgen"], check=True)

    npm_bin = subprocess.check_output(["npm", "bin", "-g"], text=True).strip()
    path_sep = ";" if platform.system() == "Windows" else ":"
    if npm_bin not in os.environ["PATH"]:
        os.environ["PATH"] = f"{npm_bin}{path_sep}{os.environ['PATH']}"

    # Verify installation
    if not shutil.which("cdxgen"):
        if platform.system() == "Windows":
            cdxgen_path = shutil.which("cdxgen.cmd")
        if not cdxgen_path:
            raise EnvironmentError(
                "❌ Could not find cdxgen after installation. "
                "Make sure npm global bin is in PATH."
            )

# -------------------- Generate SBOM --------------------
def generate_sbom(repo_path: Path, output_folder: Path, index: int):
    """Generate SBOM using cdxgen and create a jq-readable SBOM with index-based filenames."""
    ensure_cdxgen()

    sbom_file = output_folder / f"go_sbom_{index}.json"
    print(f"📦 Generating SBOM using cdxgen: {sbom_file} ...")

    cmd = ["cdxgen", "-t", "go", "-o", str(sbom_file)]
    subprocess.run(cmd, cwd=repo_path, check=True, shell=(platform.system() == "Windows"))
    print(f"✅ SBOM generated at {sbom_file}")

    # Generate jq-readable SBOM
    jq_file = output_folder / f"go_jq_sbom_{index}.json"
    jq_path = shutil.which("jq")
    if jq_path:
        try:
            with open(jq_file, "w") as f_out:
                subprocess.run(["jq", ".", str(sbom_file)], stdout=f_out, check=True)
            print(f"📄 Readable SBOM generated → {jq_file}")
        except Exception as e:
            print(f"❌ Failed to generate jq-readable SBOM: {e}")
            jq_file = sbom_file
    else:
        print("⚠️ jq not found. Skipping jq-readable SBOM generation.")
        jq_file = sbom_file

    return jq_file

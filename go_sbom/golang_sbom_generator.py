import subprocess
from pathlib import Path

def generate_sbom(repo_path: Path, current_folder: Path, output_name: str = "sbom.json"):
    """Generate CycloneDX SBOM for a Go module"""
    print(f"📦 Generating SBOM: {output_name} ...")
    sbom_file = current_folder / output_name
    cmd = [
        "cyclonedx-gomod",
        "mod",
        "-json",
        "-output", str(sbom_file),
        "."
    ]
    subprocess.run(cmd, cwd=repo_path, check=True)
    print(f"✅ SBOM saved to {sbom_file}")
    return sbom_file

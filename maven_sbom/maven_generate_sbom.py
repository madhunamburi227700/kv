import subprocess
from pathlib import Path
from maven_sbom.maven_setup import get_mvn_path


def run_maven_sbom(pom_dir: Path, output_file: Path, mvn_bin: str | Path | None = None):
    """
    Run Maven CycloneDX plugin to generate SBOM in JSON format directly
    at the specified output_file path (repo root with custom name).
    """
    mvn_path = Path(mvn_bin) if mvn_bin else get_mvn_path()
    if not mvn_path.exists():
        raise FileNotFoundError(f"❌ Maven binary not found: {mvn_path}")

    # Prepare command
    cmd = [
        str(mvn_path),
        "org.cyclonedx:cyclonedx-maven-plugin:2.9.1:makeAggregateBom",
        "-DoutputFormat=json",
        f"-DoutputDirectory={output_file.parent}",
        f"-DoutputName={output_file.stem}"  # filename without extension
    ]

    print(f"🔧 Maven binary path: {mvn_path}")
    print(f"📁 POM directory: {pom_dir}")
    print(f"📦 Generating SBOM at: {output_file}")
    print(f"📄 Running command: {' '.join(cmd)}")

    subprocess.run(cmd, cwd=pom_dir, check=True)

    # Verify
    if not output_file.exists():
        raise FileNotFoundError(f"❌ SBOM generation failed: {output_file}")

    return output_file

def run_maven_dependency_tree(module_dir: Path, mvn_bin: str | Path | None = None, output_file: Path | str = "deps.txt"):
    """
    Run Maven dependency:tree and save the output to a file.
    """
    mvn_path = Path(mvn_bin) if mvn_bin else get_mvn_path()
    if not mvn_path.exists():
        raise FileNotFoundError(f"❌ Maven binary not found: {mvn_path}")

    output_file = Path(output_file)
    cmd = [
        str(mvn_path),
        "dependency:tree",
        f"-DoutputFile={output_file}"
    ]

    print(f"🔧 Generating dependency tree for module: {module_dir}")
    print(f"📦 Running command: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=module_dir, check=True)
    return output_file

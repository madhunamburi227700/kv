import subprocess
from pathlib import Path
import shutil

from maven_sbom.maven_setup import get_mvn_path


def run_maven_sbom(repo_path: Path, mvn_bin: str | Path | None = None):
    """
    Run Maven CycloneDX plugin to generate SBOM in JSON format.
    """
    mvn_path = Path(mvn_bin) if mvn_bin else get_mvn_path()
    if not mvn_path.exists():
        raise FileNotFoundError(f"❌ Maven binary not found: {mvn_path}")

    cmd = [
        str(mvn_path),
        "org.cyclonedx:cyclonedx-maven-plugin:2.9.1:makeAggregateBom",
        "-DoutputFormat=json"
    ]

    print(f"🔧 Maven binary path: {mvn_path}")
    print(f"📁 Working directory: {repo_path}")
    print(f"📦 Running command: {' '.join(cmd)}")

    subprocess.run(cmd, cwd=repo_path, check=True)


def copy_sbom(module_dir: Path, output_path: Path):
    """
    Copies the generated SBOM from module_dir/target/bom.json
    to the specified output_path (e.g., repo_root/sbom_1.json).
    """
    source = module_dir / "target" / "bom.json"
    if not source.exists():
        raise FileNotFoundError(f"❌ SBOM not found at {source}")

    shutil.copyfile(source, output_path)
    return output_path


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

import os
import subprocess
import platform


def get_python_exec(env_name, project_folder):
    system = platform.system()
    return os.path.join(
        project_folder,
        env_name,
        "Scripts" if system == "Windows" else "bin",
        "python.exe" if system == "Windows" else "python"
    )


def generate_sbom(env_name, project_folder, requirements_file, output_file):
    python_exec = get_python_exec(env_name, project_folder)

    print("\n🔧 Installing cyclonedx-bom in venv...")
    subprocess.run(
        ["uv", "pip", "install", "cyclonedx-bom", "--python", python_exec],
        check=True
    )

    cyclonedx_exec = os.path.join(
        project_folder,
        env_name,
        "Scripts" if platform.system() == "Windows" else "bin",
        "cyclonedx-py"
    )

    print(f"\n📦 Generating SBOM → {output_file} from {requirements_file}...")
    subprocess.run(
        [cyclonedx_exec, "requirements", requirements_file, "-o", output_file],
        check=True
    )

    print(f"✅ SBOM saved → {output_file}")

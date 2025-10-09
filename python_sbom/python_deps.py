import os
import subprocess
import platform


def install_dependencies(env_name, project_path, dep_file, all_dep_path, dets_path):
    """
    Install dependencies and generate all-dep + dets.json
    based on the detected dependency manager.
    """
    system = platform.system()
    env_path = os.path.join(os.getcwd(), env_name)
    bin_dir = "Scripts" if system == "Windows" else "bin"
    python_exec = os.path.join(env_path, bin_dir, "python.exe" if system == "Windows" else "python")
    pipgrip_exec = os.path.join(env_path, bin_dir, "pipgrip.exe" if system == "Windows" else "pipgrip")

    # 1. Install pipgrip
    print("\n🔧 Installing pipgrip inside venv...")
    try:
        subprocess.run(
            ["uv", "pip", "install", "--upgrade", "pip", "pipgrip", "--python", python_exec],
            check=True
        )
    except subprocess.CalledProcessError:
        subprocess.run(
            [python_exec, "-m", "pip", "install", "--upgrade", "pip", "pipgrip"],
            check=True
        )

    # 2. Determine pipgrip command
    pipgrip_cmd = [pipgrip_exec] if os.path.exists(pipgrip_exec) else [python_exec, "-m", "pipgrip.cli"]

    # 3. Process dependency file
    if dep_file.endswith("pyproject.toml"):
        print(f"\n📄 Processing pyproject.toml: {dep_file}")
        subprocess.run(
            ["uv", "pip", "compile", "--all-extras", dep_file, "-o", all_dep_path],
            check=True
        )
    elif dep_file.endswith("requirements.txt"):
        print(f"\n📄 Processing requirements.txt: {dep_file}")
        subprocess.run(
            ["uv", "pip", "compile", dep_file, "-o", all_dep_path],
            check=True
        )
    else:
        print(f"⚠️ Unsupported dependency file type: {dep_file}")
        return

    # 4. Generate dependency tree
    subprocess.run(
        pipgrip_cmd + ["--tree-json-exact", "-r", all_dep_path],
        stdout=open(dets_path, "w"),
        check=True
    )

    print(f"✅ all-dep.txt → {all_dep_path}")
    print(f"✅ dets.json → {dets_path}")

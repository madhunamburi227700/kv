import os
from pathlib import Path

from os_detect import detect_os

# Python SBOM
from python_sbom.python_venv_manager import setup as setup_venv, remove_venv
from python_sbom.python_deps import install_dependencies
from python_sbom.python_dep_convert import convert_json
from python_sbom.python_generate_sbom import generate_sbom
from python_sbom.python_compare import compare as compare_python

# Java SBOM
from maven_sbom.maven_setup import get_mvn_path
from maven_sbom.maven_generate_sbom import run_maven_sbom, run_maven_dependency_tree
from maven_sbom.maven_generate_dependency_tree import parse_gradle_dependencies, save_dependencies_to_json
from maven_sbom.maven_comapre import compare_sbom_and_tree

# Go SBOM
from go_sbom.golang_check import is_golang_project
from go_sbom.go_dependency_tree import prepare_dependencies, install_deptree, generate_dependency_tree
from go_sbom.golang_sbom_generator import generate_sbom as generate_go_sbom
from go_sbom.go_compare import generate_comparison

# Language detection module
from language_detector import detect_languages, detect_dependency_manager

# Package manager file handler
from package_file_handler import get_package_file

# -------------------- Python Helper --------------------
def process_python(env_name, repo_path, manager_name, dep_file, index):
    print(f"\n{'='*60}")
    print(f"▶ Processing Python ({manager_name}) → {dep_file}")
    print(f"{'='*60}\n")

    all_dep_file = f"python_all-dep_{index}.txt"
    dets_file = f"python_dets_{index}.json"
    normalized_file = f"python_normalized_deps_{index}.json"
    sbom_file = f"python_sbom_{index}.json"
    comparison_file = f"python_comparison_{index}.txt"

    venv_path = setup_venv(env_name=env_name, project_path=repo_path)
    print(f"➡ Virtual environment created at: {venv_path}")

    install_dependencies(env_name, repo_path, dep_file, all_dep_file, dets_file)

    if os.path.exists(dets_file):
        convert_json(dets_file, normalized_file)
        print(f"✅ Normalized dependencies saved → {normalized_file}")

    if os.path.exists(all_dep_file):
        generate_sbom(env_name, all_dep_file, sbom_file)
        print(f"✅ SBOM generated → {sbom_file}")

    if os.path.exists(normalized_file) and os.path.exists(sbom_file):
        compare_python(sbom_file, normalized_file, comparison_file)
        print(f"✅ Comparison completed → {comparison_file}")

    remove_venv(venv_path)
    print("🧹 Python virtual environment removed.")

# -------------------- Java Helper --------------------
def process_java(repo_path, java_files):
    mvn_path = get_mvn_path()
    if not mvn_path:
        print("❌ Maven not found. Skipping Java processing.")
        return

    print(f"\n✅ Using Maven: {mvn_path}")

    valid_poms = [f for f in java_files if "test" not in f.lower() and "examples" not in f.lower()]
    print(f"\n📦 Processing {len(valid_poms)} Java POM(s)")

    for idx, pom_file in enumerate(valid_poms, start=1):
        pom_dir = Path(pom_file).parent
        print(f"\n🚀 Processing Java POM #{idx}: {pom_file}")

        try:
            sbom_file = Path(repo_path) / f"java_sbom_{idx}.json"
            run_maven_sbom(pom_dir, output_file=sbom_file, mvn_bin=mvn_path)
            print(f"✅ SBOM generated → {sbom_file}")

            deps_txt = Path(repo_path) / f"java_deps_{idx}.txt"
            run_maven_dependency_tree(pom_dir, mvn_bin=mvn_path, output_file=deps_txt)

            deps_json = Path(repo_path) / f"java_deps_{idx}.json"
            parsed = parse_gradle_dependencies(str(deps_txt))
            save_dependencies_to_json(parsed, str(deps_json))

            comparison_file = Path(repo_path) / f"java_comparison_{idx}.txt"
            compare_sbom_and_tree(str(sbom_file), str(deps_json), str(comparison_file))
            print(f"✅ Comparison completed → {comparison_file}")

        except Exception as e:
            print(f"❌ Error processing {pom_file}: {e}")

# -------------------- Go Helper --------------------
def process_go(repo_path, go_files):
    if not go_files:
        print("⚠️ No Go modules found.")
        return

    print(f"\n📦 Detected {len(go_files)} Go module(s)")

    root_folder = Path.cwd()
    install_deptree()

    for idx, go_mod in enumerate(go_files, start=1):
        mod_path = Path(go_mod).parent
        prepare_dependencies(mod_path)

        print(f"\n🚀 Processing Go module #{idx}: {mod_path}")

        deps_file = generate_dependency_tree(mod_path, root_folder, output_name=f"go_deps_{idx}.json")
        sbom_file = generate_go_sbom(mod_path, root_folder, output_name=f"go_sbom_{idx}.json")
        comparison_file = root_folder / f"go_comparison_{idx}.txt"
        generate_comparison(deps_file, sbom_file, comparison_file)

        print(f"✅ Go comparison completed → {comparison_file}")

# -------------------- Main Flow --------------------
def main():
    print("\n🎯 SBOM Generation Tool (Package File Only)")

    os_name = detect_os()
    print(f"\n🖥️ Detected OS: {os_name}")

    # -------------------- Get package manager file --------------------
    package_file = get_package_file()
    print(f"\n📄 Using package file: {package_file}")

    repo_path = Path.cwd()  # Use current directory as "repo path"

    # -------------------- Detect language based on file --------------------
    lang_info = detect_languages(str(repo_path))
    if not lang_info.get("files"):
        print("⚠️ No dependency manager files detected.")
        return

    for lang, files in lang_info["files"].items():
        manager, dep_files = detect_dependency_manager(str(repo_path), lang)
        # If user uploaded a single package file, override dep_files
        dep_files = [package_file]

        if not dep_files:
            print(f"⚠️ Skipping {lang}: No dependency manager files found")
            continue

        print(f"\n📦 Processing {lang} with manager: {manager}")

        if lang.lower() == "python":
            for i, dep_file in enumerate(dep_files, start=1):
                process_python("python-env", repo_path, manager, dep_file, i)

        elif lang.lower() == "java":
            process_java(repo_path, dep_files)

        elif lang.lower() == "go":
            process_go(repo_path, dep_files)

    print("\n🎉 SBOM generation completed for all detected languages!")

if __name__ == "__main__":
    main()

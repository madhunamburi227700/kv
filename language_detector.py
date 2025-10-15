import os
from pathlib import Path
from collections import defaultdict

# -------------------- Constants --------------------
EXCLUDE_DIRS = {".venv", "venv", "env", "__pycache__", "node_modules", "dist",
                "target", "build", "site-packages"}

# Map extensions to languages
LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".java": "Java",
    ".go": "Go",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".rs": "Rust",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".scala": "Scala",
    ".sh": "Shell",
}

PYTHON_PRIORITY = ["uv", "poetry", "pipenv", "flit", "pyproject", "setuptools", "pip"]

# -------------------- Language Detection --------------------
def detect_languages(repo_path: str):
    language_stats = defaultdict(int)
    file_details = defaultdict(list)
    total_size = 0
    detected_package_managers = set()

    repo_path = Path(repo_path)
    if not repo_path.exists():
        return {"primary_language": "Unknown", "languages": {}, "files": {}}

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            _, ext = os.path.splitext(file)
            fpath = str(Path(root) / file)
            try:
                size = os.path.getsize(fpath)
            except OSError:
                size = 0

            # Detect code files
            if ext.lower() in LANGUAGE_EXTENSIONS:
                lang = LANGUAGE_EXTENSIONS[ext.lower()]
                language_stats[lang] += size
                total_size += size
                file_details[lang].append(fpath)

            # Detect package manager files
            lower_file = file.lower()
            if lower_file in {"requirements.txt", "pyproject.toml"}:
                detected_package_managers.add("Python")
                file_details["Python"].append(fpath)
            elif lower_file == "go.mod":
                detected_package_managers.add("Go")
                file_details["Go"].append(fpath)
                # Also check if go.sum exists
                go_sum = Path(root) / "go.sum"
                if go_sum.exists():
                    file_details["Go"].append(str(go_sum))
                else:
                    print(f"⚠️ Warning: {root} has go.mod but missing go.sum. Run 'go mod tidy' to generate it.")
            elif lower_file == "pom.xml":
                detected_package_managers.add("Java")
                file_details["Java"].append(fpath)

    # Determine primary language
    if language_stats:
        primary_language = max(language_stats, key=language_stats.get)
    elif detected_package_managers:
        primary_language = next(iter(detected_package_managers))
    else:
        primary_language = "Unknown"

    percentages = {
        lang: round((size / total_size) * 100, 2) if total_size > 0 else 0
        for lang, size in language_stats.items()
    }

    return {
        "primary_language": primary_language,
        "languages": percentages,
        "files": dict(file_details),
    }

# -------------------- Dependency Manager Detection --------------------
def detect_dependency_manager(repo_path: str, language: str):
    repo_path = Path(repo_path)
    lang = language.lower()
    found_files = defaultdict(list)

    # -------------------- Python --------------------
    if lang == "python":
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            rpath = Path(root)
            files_lower = [f.lower() for f in files]

            if "requirements.txt" in files_lower:
                found_files["pip"].append(str(rpath / "requirements.txt"))
            if "pyproject.toml" in files_lower:
                py_file = rpath / "pyproject.toml"
                manager = "pyproject"
                try:
                    import tomllib  # Python >=3.11
                except ImportError:
                    import tomli as tomllib  # Python <3.11

                try:
                    with open(py_file, "rb") as f:
                        data = tomllib.load(f)
                    tool_keys = data.get("tool", {})
                    if "poetry" in tool_keys:
                        manager = "poetry"
                    elif "uv" in tool_keys:
                        manager = "uv"
                    elif "flit" in tool_keys:
                        manager = "flit"
                except Exception:
                    manager = "pyproject"
                found_files[manager].append(str(py_file))

        for mgr in PYTHON_PRIORITY:
            if mgr in found_files:
                return mgr, sum(found_files.values(), [])
        return "Unknown", []

    # -------------------- Java --------------------
    elif lang == "java":
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            rpath = Path(root)
            if "pom.xml" in files:
                found_files["maven"].append(str(rpath / "pom.xml"))
            if "build.gradle" in files:
                found_files["gradle"].append(str(rpath / "build.gradle"))
            if "build.gradle.kts" in files:
                found_files["gradle"].append(str(rpath / "build.gradle.kts"))

        if "maven" in found_files:
            return "maven", found_files["maven"]
        if "gradle" in found_files:
            return "gradle", found_files["gradle"]
        return "Unknown", []

    # -------------------- Go --------------------
    elif lang == "go":
        go_files = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            rpath = Path(root)
            if (rpath / "go.mod").exists():
                go_files.append(str(rpath / "go.mod"))
                if (rpath / "go.sum").exists():
                    go_files.append(str(rpath / "go.sum"))
                else:
                    print(f"⚠️ Warning: {rpath} has go.mod but missing go.sum. Run 'go mod tidy' to generate it.")
        if go_files:
            return "go modules", go_files
        return "Unknown", []

    return "Unknown", []

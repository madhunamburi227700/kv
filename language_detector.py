import os
from pathlib import Path
from collections import defaultdict

# -------------------- TOML Loader --------------------
try:
    import tomllib  # Python >=3.11
except ImportError:
    import tomli as tomllib  # Python <3.11 fallback

# -------------------- Constants --------------------
LANGUAGE_EXTENSIONS = {
    ".py": "Python", ".java": "Java", ".go": "Go", ".js": "JavaScript",
    ".ts": "TypeScript", ".rb": "Ruby", ".php": "PHP", ".cpp": "C++",
    ".c": "C", ".cs": "C#", ".rs": "Rust", ".kt": "Kotlin", ".swift": "Swift",
    ".scala": "Scala", ".sh": "Shell",
}
EXCLUDE_DIRS = {".venv", "venv", "env", "__pycache__", "node_modules", "dist",
                "target", "build", "site-packages"}
PYTHON_PRIORITY = ["uv", "poetry", "pipenv", "flit", "pyproject", "setuptools", "pip"]

# ================================================================
# Language Detection
# ================================================================
def detect_languages(repo_path: str):
    language_stats = defaultdict(int)
    file_details = defaultdict(list)
    total_size = 0

    repo_path = Path(repo_path)
    if not repo_path.exists():
        return {"primary_language": "Unknown", "languages": {}, "files": {}}

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in LANGUAGE_EXTENSIONS:
                lang = LANGUAGE_EXTENSIONS[ext.lower()]
                fpath = str(Path(root) / file)
                try:
                    size = os.path.getsize(fpath)
                except OSError:
                    size = 0
                language_stats[lang] += size
                total_size += size
                file_details[lang].append(fpath)

    if not language_stats:
        primary_language = "Unknown"
    else:
        primary_language = max(language_stats, key=language_stats.get)

    percentages = {
        lang: round((size / total_size) * 100, 2) if total_size > 0 else 0
        for lang, size in language_stats.items()
    }

    return {
        "primary_language": primary_language,
        "languages": percentages,
        "files": dict(file_details),
    }

# ================================================================
# Dependency Manager Detection
# ================================================================
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
            if "setup.py" in files_lower:
                found_files["setuptools"].append(str(rpath / "setup.py"))

            if "pyproject.toml" in files_lower:
                py_file = rpath / "pyproject.toml"
                manager = "pyproject"
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

        if found_files:
            if "maven" in found_files:
                return "maven", found_files["maven"]
            if "gradle" in found_files:
                return "gradle", found_files["gradle"]
        return "Unknown", []

    # -------------------- Go --------------------
    elif lang == "go":
        go_mods = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            rpath = Path(root)
            if "go.mod" in files:
                go_mods.append(str(rpath / "go.mod"))
        if go_mods:
            return "go modules", go_mods
        return "Unknown", []

    # -------------------- Default --------------------
    return "Unknown", []

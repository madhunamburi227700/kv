import uuid
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import os
from fastapi import File, UploadFile, Form

from os_detect import detect_os

# -------------------- Import SBOM modules --------------------
from python_sbom.python_venv_manager import setup as setup_venv, remove_venv
from python_sbom.python_deps import install_dependencies
from python_sbom.python_dep_convert import convert_json
from python_sbom.python_generate_sbom import generate_sbom
from python_sbom.python_compare import compare as compare_python

from maven_sbom.maven_setup import get_mvn_path
from maven_sbom.maven_generate_sbom import run_maven_sbom, run_maven_dependency_tree
from maven_sbom.maven_generate_dependency_tree import parse_gradle_dependencies, save_dependencies_to_json
from maven_sbom.maven_comapre import compare_sbom_and_tree

from go_sbom.golang_sbom_generator import generate_sbom as generate_go_sbom

from language_detector import detect_dependency_manager
from package_file_handler import get_package_file_auto

app = FastAPI(title="SBOM Generator API", version="1.2.0")

# -------------------- In-memory store --------------------
sbom_store = {}

# -------------------- Request Schema --------------------
class SBOMRequest(BaseModel):
    source_input: str  # GitHub raw URL or local package file path
    id: str = None     # Optional custom ID

# -------------------- Python Helper --------------------
def process_python(env_name, output_folder, manager_name, dep_file, index):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    all_dep_file = output_folder / f"python_all-dep_{index}.txt"
    dets_file = output_folder / f"python_dets_{index}.json"
    normalized_file = output_folder / f"python_normalized_deps_{index}.json"
    sbom_file = output_folder / f"python_sbom_{index}.json"
    comparison_file = output_folder / f"python_comparison_{index}.txt"

    venv_path = setup_venv(env_name=env_name, project_path=output_folder)
    install_dependencies(env_name, output_folder, dep_file, all_dep_file, dets_file)

    if dets_file.exists():
        convert_json(dets_file, normalized_file)

    if all_dep_file.exists():
        generate_sbom(env_name, output_folder, all_dep_file, sbom_file)

    if normalized_file.exists() and sbom_file.exists():
        compare_python(sbom_file, normalized_file, comparison_file)

    remove_venv(venv_path)
    return {"sbom_file": str(sbom_file)}

# -------------------- Java Helper --------------------
def process_java(output_folder, java_files):
    mvn_path = get_mvn_path()
    if not mvn_path:
        raise HTTPException(status_code=500, detail="Maven not found on system")

    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    results = []
    for idx, pom_file in enumerate(java_files, start=1):
        pom_dir = Path(pom_file).parent
        sbom_file = output_folder / f"java_sbom_{idx}.json"
        deps_txt = output_folder / f"java_deps_{idx}.txt"
        deps_json = output_folder / f"java_deps_{idx}.json"
        comparison_file = output_folder / f"java_comparison_{idx}.txt"

        run_maven_sbom(pom_dir, output_file=sbom_file, mvn_bin=mvn_path)
        run_maven_dependency_tree(pom_dir, mvn_bin=mvn_path, output_file=deps_txt)
        parsed = parse_gradle_dependencies(str(deps_txt))
        save_dependencies_to_json(parsed, str(deps_json))
        compare_sbom_and_tree(str(sbom_file), str(deps_json), str(comparison_file))

        results.append({"sbom_file": str(sbom_file)})

    return results

# -------------------- Go Helper --------------------
def process_go(output_folder, go_files):
    if not go_files:
        raise HTTPException(status_code=400, detail="No Go modules found")

    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    results = []
    processed_dirs = set()
    for idx, go_file in enumerate(go_files, start=1):
        mod_dir = Path(go_file).parent
        if mod_dir in processed_dirs:
            continue
        processed_dirs.add(mod_dir)

        sbom_file = generate_go_sbom(mod_dir, output_folder, index=idx)
        results.append({"sbom_file": str(sbom_file)})

    return results

# -------------------- FastAPI Routes --------------------
@app.get("/")
def root():
    return {"message": "✅ SBOM Generator API is running."}

# -------------------- POST: Generate SBOM --------------------
@app.post("/generate_sbom")
def generate_sbom_api(request: SBOMRequest):
    source_input = request.source_input.strip()
    repo_path = Path.cwd()
    os_name = detect_os()

    # 1️ Generate SBOM ID first (use provided ID or create a new one)
    sbom_id = request.id if request.id else str(uuid.uuid4())
    sbom_folder = Path.cwd().joinpath(sbom_id)
    sbom_folder.mkdir(parents=True, exist_ok=False)  ## keep it false to avoid rewriting of same ID as folder.

    # 2️ Download or copy package file INTO sbom_folder
    package_file = get_package_file_auto(source_input,dest_folder=sbom_folder)
    if not package_file or not os.path.exists(package_file):
        raise HTTPException(status_code=400, detail=f"Package file not found: {package_file}")

    # 3️ Determine language based on file extension
    _, ext = os.path.splitext(package_file)
    ext = ext.lower()
    if ext in [".py", ".txt", ".toml"]:
        language = "Python"
    elif ext in [".mod", ".sum"]:
        language = "Go"
    elif ext == ".xml":
        language = "Java"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # 4️ Detect dependency manager inside the sbom_folder
    manager, dep_files = detect_dependency_manager(str(repo_path), language)
    dep_files = [package_file]

    # 5️ Process according to language
    if language.lower() == "python":
        result = [process_python("python-env", sbom_folder, manager, dep_files[0], 1)]
    elif language.lower() == "java":
        result = process_java(sbom_folder, dep_files)
    elif language.lower() == "go":
        result = process_go(sbom_folder, dep_files)

    # Read SBOM as proper JSON
    sbom_contents = []
    for item in result:
        sbom_file = item["sbom_file"]
        try:
            with open(sbom_file, "r", encoding="utf-8") as f:
                content = json.load(f)  # <--- parse JSON
            sbom_contents.append({"file": sbom_file, "content": content})
        except Exception as e:
            sbom_contents.append({"file": sbom_file, "error": str(e)})

    # 7️ Save metadata in memory
    sbom_store[sbom_id] = {
        "language": language,
        "os": os_name,
        "sbom_files": [item["sbom_file"] for item in result],
        "folder": str(sbom_folder)
    }
    # 8 Return response
    return {
        "id": sbom_id,
        "language": language,
        "os": os_name,
        "folder": str(sbom_folder),
        "sbom_files": sbom_contents,
        "message": "🎉 SBOM generation completed successfully"
    }

# -------------------- POST: Upload file and generate SBOM --------------------
@app.post("/upload_and_generate_sbom")
async def upload_and_generate_sbom(
    file: UploadFile = File(...),
    id: str = Form(None)
):
    os_name = detect_os()
    # 1️ Generate SBOM ID and folder
    sbom_id = id if id else str(uuid.uuid4())
    sbom_folder = Path.cwd().joinpath(sbom_id)
    sbom_folder.mkdir(parents=True, exist_ok=False)  # All files inside this folder

    # 2️ Save uploaded file directly in sbom_folder
    file_path = sbom_folder / file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 3️ Determine language
    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()
    if ext in [".py", ".txt", ".toml"]:
        language = "Python"
    elif ext in [".mod", ".sum"]:
        language = "Go"
    elif ext == ".xml":
        language = "Java"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # 4️ Process file based on language
    if language.lower() == "python":
        result = [process_python("python-env", sbom_folder, None, str(file_path), 1)]
    elif language.lower() == "java":
        result = process_java(sbom_folder, [str(file_path)])
    elif language.lower() == "go":
        result = process_go(sbom_folder, [str(file_path)])

    # 5️ Read SBOM JSONs
    sbom_contents = []
    for item in result:
        sbom_file = item["sbom_file"]
        try:
            with open(sbom_file, "r", encoding="utf-8") as f:
                content = json.load(f)
            sbom_contents.append({"file": sbom_file, "content": content})
        except Exception as e:
            sbom_contents.append({"file": sbom_file, "error": str(e)})

    # 6️ Save metadata in memory
    sbom_store[sbom_id] = {
        "language": language,
        "os": os_name,
        "sbom_files": [item["sbom_file"] for item in result],
        "folder": str(sbom_folder)
    }

    # 7️ Return response
    return {
        "id": sbom_id,
        "language": language,
        "os": os_name,
        "folder": str(sbom_folder),
        "sbom_files": sbom_contents,
        "message": "🎉 SBOM generated from uploaded file successfully"
    }


# -------------------- GET: Retrieve SBOM --------------------
@app.get("/generate_sbom/{sbom_id}")
def get_sbom(sbom_id: str):
    if sbom_id not in sbom_store:
        raise HTTPException(status_code=404, detail="SBOM ID not found")

    sbom_data = sbom_store[sbom_id]
    sbom_files = sbom_data.get("sbom_files", [])

    sbom_contents = []
    for sbom_file in sbom_files:
        try:
            with open(sbom_file, "r", encoding="utf-8") as f:
                content = json.load(f)  # <--- parse JSON
            sbom_contents.append({"file": sbom_file, "content": content})
        except Exception as e:
            sbom_contents.append({"file": sbom_file, "error": str(e)})

    return {
        "id": sbom_id,
        "language": sbom_data.get("language"),
        "os": sbom_data.get("os"),
        "folder": sbom_data.get("folder"),
        "sbom_files": sbom_contents,
        "message": "✅ SBOM files retrieved successfully"
    }

# -------------------- DELETE: Remove SBOM --------------------
@app.delete("/generate_sbom/{sbom_id}")
def delete_sbom(sbom_id: str):
    if sbom_id not in sbom_store:
        raise HTTPException(status_code=404, detail="SBOM ID not found")
    del sbom_store[sbom_id]
    return {"message": f"SBOM with ID {sbom_id} has been deleted"}
    
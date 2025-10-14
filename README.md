# Sbom-generator

- this tool helps in generating Software Bill of Materials (SBOM) for multi-module projects. right it gave supports for         java-maven,python,golang projects.
- it generates SBOM in cyclonedx format.
- it also generates dependency tree for maven projects and compare it with generated SBOM.
- it is dockerized application and can be run using docker.

# 1. Features of python

- This repository provides a **Python pipeline** to handle dependency management and SBOM generation efficiently.

## Features

- **Create isolated virtual environments** for your projects.
- **Install dependencies** from multiple Python dependency files (`pyproject.toml` or `requirements.txt`).
- **Generate a full dependency tree** (`dets.json`) and **normalized dependency file** (`normalized_deps.json`).
- **Produce a Software Bill of Materials (SBOM)** in **CycloneDX format** (`sbom.json`).


## Supported Python Package Managers

The pipeline supports the following **Python dependency managers**:

- pip : via requirements.txt
- Poetry/uv : via pyproject.toml (all extras supported)
- ⚠️ Only Python projects are supported. Other languages are ignored.

## Requirements

- Python 3.11+ recommended

- uv
 (used to create virtual environments and manage Python packages)

- Git (for cloning repositories)

## How to Use

- **Step 1:** Clone this repository and navigate into it:
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```
- **Step 2:** Run the main script
```bash
python main.py
```

- You will be prompted to enter a GitHub repository URL with branch:
```bash
Enter GitHub repo URL with branch (e.g. https://github.com/user/repo.git@branch):
```

- The script will automatically:
- Detect your OS.
- Clone the repo.
- Detect the primary language.
- Detect Python dependency manager(s) and files.
- Process each dependency file:

## Step 3: What happens for each dependency file

For each detected Python dependency file, the pipeline performs the following steps:

### 1. Create a Virtual Environment
- Default environment name: `sbom-env_x`
- Uses:  
```bash
uv venv <env_path>
```
### 2. Install Dependencies and Generate Dependency Tree

- Resolves all transitive dependencies using pipgrip.
- Generates the following files:
- all-dep_X.txt → Flattened list of dependencies
- dets_X.json → Detailed dependency tree

### 3. Normalize Dependency Tree

Converts dets_X.json to structured format:

-normalized_deps_X.json

### 4. Generate SBOM

Uses cyclonedx-bom for Python

- Generates sbom_X.json

### 5. Cleanup

- Removes the virtual environment after processing

- X in filenames represents the index of the dependency file to avoid overwriting files when multiple dependency files exist.

## Commands Used Internally for Python Projects

| Step                                 | Command                                                                               |
|--------------------------------------|---------------------------------------------------------------------------------------|
| Check Python version                 | `python --version`                                                                    |
| Create virtual environment           | `uv venv sbom-env`                                                                    |
| Install pipgrip                      | `uv pip install --upgrade pip pipgrip `                                               |
| Generate flattened dependency file   | `uv pip compile --all-extras pyproject.toml -o all-dep.txt`                           |
| Generate dependency tree             | `pipgrip --tree-json-exact -r all-dep.txt > dets.json`                                |
| Normalize dependencies               | `python dep_convert.py`                                                               |
| Install CycloneDX & generate SBOM    | `uv pip install cyclonedx-bom`<br>`cyclonedx-py requirements all-dep.txt -o sbom.json`|
| Remove virtual environment           | `python -c "import shutil; shutil.rmtree('<venv_path>')"`                             |


# 2. Features of golang

- This repository provides a **Go pipeline** to handle dependency management and SBOM generation efficiently.
- It gave multiple sbom's for one project if it has multiple modules.
- And also it gave multiple dependency tree's for one project if it has multiple modules.
- And also it compare each module's sbom with dependency tree and gave a comparison report.

## Go Project SBOM & Dependency Tree Auto-Generation

This project automates the generation of:
- **Dependency Tree** using [`deptree`](https://github.com/vc60er/deptree)
- **CycloneDX SBOM (Software Bill of Materials)** using [`cyclonedx-gomod`](https://github.com/CycloneDX/cyclonedx-gomod)
- **Comparison Report** between the dependency tree and SBOM

The flow is designed to:
1. Clone a given Go project repository.
2. Detect Go modules.
3. Prepare dependencies and run `go mod tidy`.
4. Generate the dependency tree in JSON format.
5. Generate CycloneDX SBOM for each module.
6. Compare results and produce a report.

### 1. Install Go
Make sure Go is installed and available in your `PATH`.

```bash
go version
```

### 2. Install Python (for orchestration scripts)
Ensure Python ≥3.8 is installed.

```bash
python --version
```

### 3. Install CycloneDX for Go
Install the CycloneDX Go module generator:
```bash
go install github.com/CycloneDX/cyclonedx-gomod/cmd/cyclonedx-gomod@latest
```
### 4. Install Deptree
Install the dependency tree generator:
```bash
go install github.com/vc60er/deptree@latest
```
- Both binaries (cyclonedx-gomod and deptree) must be in your GOPATH/bin or system PATH.

## 📝 Commands Used Internally

Here are the key shell commands executed by the scripts:

| Step                     | Command                                               |
|--------------------------|-------------------------------------------------------|
| Clone repository         | `git clone <repo_url>`                                |
| Checkout branch          | `git checkout <branch>`                               |
| Prepare dependencies     | `go mod tidy`                                         |
| Generate module graph    | `go mod graph`                                        |
| Generate dependency tree | `deptree -json < graph_output > deps.json`            |
| Generate CycloneDX SBOM  | `cyclonedx-gomod mod -json -output sbom.json .`       |


# 2. Features of java-maven


## Java-Maven Project SBOM & Dependency Tree Auto-Generation

This project automates **SBOM (Software Bill of Materials) generation** for Maven-based Java projects and compares it against the Maven dependency tree. It supports multi-module Maven projects, generates JSON SBOMs, dependency tree JSONs, and a comparison report highlighting missing dependencies or version mismatches.

---

## Features

- Automatically detects Maven projects (`pom.xml`) in a GitHub repository.
- Generates SBOM using **CycloneDX Maven plugin** in JSON format.
- Generates Maven **dependency tree** (`dependency:tree`) and converts it into JSON.
- Compares SBOM dependencies vs dependency tree:
  - Lists dependencies **present only in SBOM**.
  - Lists dependencies **present only in dependency tree**.
  - Lists **version mismatches**.
  - Lists **exact matches**.
- Skips test/example/problematic POMs automatically.

---

## Prerequisites

- Python 3.12+
- Maven installed and available in `PATH` (or `mvn` / `mvn.cmd` depending on OS)
- Git installed
- Internet connection to clone GitHub repositories

---

## Setup

1. Clone this repository:

```bash
git clone <this_repo_url>
cd <this_repo_folder>
```

2. Ensure required Python dependencies are installed (if any, e.g., for optional modules like os_detect).

3. Ensure Maven is installed and working:
```bash 
    mvn -v
```

### The script will:

- Detect the operating system.
- Clone the repository and checkout the specified branch.
- Detect programming languages and dependency managers.
- For Maven modules:

- Validate pom.xml files.

    Generate SBOM JSON via CycloneDX Maven plugin.
    Generate dependency tree JSON.
    Compare SBOM vs dependency tree and generate a comparison report.

### Example Commands

## 📝 Commands Used Internally

Here are the key shell commands executed by the scripts for Maven projects:

| Step                     | Command                                                                                              |
|--------------------------|------------------------------------------------------------------------------------------------------|
| Clone repository         | `git clone <repo_url>`                                                                               |
| Checkout branch          | `git checkout <branch>`                                                                              |
| Generate CycloneDX SBOM  | `mvn org.cyclonedx:cyclonedx-maven-plugin:2.9.1:makeAggregateBom -DoutputFormat=json -DoutputDirectory=<output_dir> -DoutputName=<sbom_file>` |
| Generate dependency tree | `mvn dependency:tree -DoutputFile=<deps_file>`                                                      |
| Parse dependency tree    | `python parse_gradle_dependencies.py <deps_file> <deps_json_file>` (internal Python parsing step)   |
| Compare SBOM vs tree     | `python maven_compare.py <sbom_file> <deps_json_file> <comparison_file>`                             |


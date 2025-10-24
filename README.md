# SBOM Generator cli based

A comprehensive tool for generating Software Bill of Materials (SBOM) for multi-language projects, supporting Python, Java (Maven), and Go. The tool generates SBOM in CycloneDX format and provides dependency analysis.

## 🌟 Key Features

- Multi-language support (Python, Java-Maven, Go)
- CycloneDX format SBOM generation
- Dependency tree generation and comparison
- Support for both local files and GitHub raw URLs
- Dockerized application for easy deployment

## 📝 Input Methods

You can provide dependency files in two ways:

1. **GitHub Raw URL**:
```bash
https://raw.githubusercontent.com/username/repo/branch/requirements.txt
https://raw.githubusercontent.com/username/repo/branch/pom.xml
https://raw.githubusercontent.com/username/repo/branch/go.mod
```

2. **Local File Path**:
```bash
C:\Projects\my-python-project\requirements.txt
C:\Projects\my-java-project\pom.xml
C:\Projects\my-go-project\go.mod
```

## 🔧 Language-Specific Features

### 1. Python Support
- **Input Files**: `requirements.txt`, `pyproject.toml`
- **Virtual Environment**: Automatic creation using `uv`
- **Output Files**:
  - `all-dep_X.txt` - Flattened dependencies
  - `dets_X.json` - Dependency tree
  - `normalized_deps_X.json` - Structured dependencies
  - `sbom_X.json` - CycloneDX SBOM

### 2. Java (Maven) Support
- **Input File**: `pom.xml`
- **Multi-module Support**: Yes
- **Output Files**:
  - `java_sbom_X.json` - CycloneDX SBOM
  - `java_deps_X.json` - Dependency tree
  - `java_comparison_X.txt` - Comparison report

### 3. Go Support
- **Input Files**: `go.mod`
- **Multi-module Support**: Yes
- **Output Files**:
  - `go_cdxgen_sbom_X.json` - cdxgen based sbom
  - `go_cdxgen_jq_sbom_1.json` - jq is used to update the sbom to human-readable format

## 🚀 Quick Start

### using the cli

```bash
python main.py
```

example to generate sbom from url

```bash
📂 Enter GitHub raw URL or local package file path: path or raw file link
```

### Using the API

1. **Generate SBOM from URL**:
```bash
curl -X POST "http://localhost:8000/generate_sbom" \
  -H "Content-Type: application/json" \
  -d '{
    "source_input": "https://raw.githubusercontent.com/user/repo/branch/requirements.txt",
    "id": "custom_id"
  }'
```

2. **Generate SBOM from Local File**:
```bash
curl -X POST "http://localhost:8000/generate_sbom" \
  -H "Content-Type: application/json" \
  -d '{
    "source_input": "C:\\Projects\\my-project\\requirements.txt",
    "id": "custom_id"
  }'
```

3. **Upload File Directly**:
```bash
curl -X POST "http://localhost:8000/upload_and_generate_sbom" \
  -F "file=@C:\\Projects\\my-project\\requirements.txt" \
  -F "id=custom_id"
```

## 📋 Prerequisites

### General Requirements
- Python 3.11+
- Docker (optional)
- Git (for GitHub URLs)

### Language-Specific Tools
- **Python**: `uv`, `pipgrip`, `cyclonedx-bom`
- **Java**: Maven
- **Go**: `cyclonedx-generator`, `jq`


## 📁 Output Structure

The tool creates a unique folder for each SBOM generation request:
```
<sbom_id>/
├── python_sbom_1.json    # Python SBOM
├── java_sbom_1.json     # Java SBOM
├── go_sbom_1.json       # Go SBOM
├── *_deps_*.json        # Dependency trees
└── *_comparison_*.txt   # Comparison reports
```

## 🔍 Error Handling

- Invalid URLs or paths return 400 Bad Request
- Unsupported file types are rejected
- Network issues are reported with appropriate error messages
- Missing dependencies trigger installation attempts

## 📚 API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/generate_sbom` | POST | Generate from URL/path |
| `/upload_and_generate_sbom` | POST | Generate from upload |
| `/generate_sbom/{sbom_id}` | GET | Retrieve SBOM |
| `/generate_sbom/{sbom_id}` | DELETE | Remove SBOM |

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
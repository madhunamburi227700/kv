# SBOM Generator — API Usage Guide

This repository provides a FastAPI-based service and CLI helpers to generate Software Bill of Materials (SBOM) for Python, Java (Maven), and Go projects. The API exposes endpoints to generate SBOMs from a package file (local or GitHub raw URL), upload a package file and generate an SBOM, retrieve a generated SBOM, and delete SBOM records.

---

## Key components used by the API

- FastAPI service implemented in `app.py` with endpoints:
  - [`app.generate_sbom_api`](app.py) — generate SBOM from a package file path or GitHub raw URL.
  - [`app.upload_and_generate_sbom`](app.py) — upload a package file and generate an SBOM.
  - [`app.get_sbom`](app.py) — retrieve generated SBOM(s) by ID.
  - [`app.delete_sbom`](app.py) — remove SBOM metadata from the in-memory store.
- Package retrieval: [`package_file_handler.get_package_file_auto`](package_file_handler.py) (handles download or local copy).
- Language / dependency detection: `language_detector.py`.
- Python SBOM helpers: `python_sbom/` (venv creation, pipgrip, cyclonedx).
- Maven helpers: `maven_sbom/` (Maven invocation, parsing dependency tree).
- Go helpers: `go_sbom/` (cdxgen usage).

See the complete API spec in [API_BASE.md](API_BASE.md).

---

## Endpoints

1. POST /generate_sbom
- Description: Provide a GitHub raw URL or local package file path. The server copies the file into a generated SBOM folder, detects the language from the file extension, and runs the appropriate pipeline.
- Request body (JSON):
  - source_input: string (GitHub raw URL or local file path)
  - id: optional string (custom SBOM id)
- Response: JSON with generated SBOM contents and metadata.

2. POST /upload_and_generate_sbom
- Description: Upload a dependency file directly (multipart form). The file is saved into a new SBOM folder and processed.
- Form fields:
  - file: uploaded file
  - id: optional SBOM id
- Response: JSON with generated SBOM contents and metadata.

3. GET /generate_sbom/{sbom_id}
- Description: Retrieve the generated SBOM JSON(s) and metadata stored in memory for the given SBOM id.

4. DELETE /generate_sbom/{sbom_id}
- Description: Delete the in-memory metadata for the SBOM id (does not delete disk artifacts).

---

## Supported package file extensions (map to language)
- Python: `.py`, `.txt`, `.toml` (commonly `requirements.txt`, `pyproject.toml`)
- Go: `.mod`, `.sum` (`go.mod`, `go.sum`)
- Java: `.xml` (`pom.xml`)

---


### SBOM Generator Endpoints

| Endpoint | Method | Description | Request Body/Params | Response |
|----------|--------|-------------|-------------------|-----------|
| `/generate_sbom` | POST | Generate SBOM from URL/path | `{"source_input": "string", "id": "optional"}` | SBOM JSON + metadata |
| `/upload_and_generate_sbom` | POST | Generate SBOM from uploaded file | `file: File, id: optional` | SBOM JSON + metadata |
| `/generate_sbom/{sbom_id}` | GET | Retrieve SBOM by ID | Path param: `sbom_id` | SBOM JSON + metadata |
| `/generate_sbom/{sbom_id}` | DELETE | Remove SBOM metadata | Path param: `sbom_id` | Success message |


## Example usage (curl)

Generate SBOM from a remote raw file and local path:
```bash
curl -X POST "http://localhost:8000/generate_sbom" `
>> -H "Content-Type: application/json" `
>> -d '{"source_input": "https://raw.githubusercontent.com/oraios/serena/refs/heads/main/pyproject.toml","id": "1"}'
```

Upload and generate SBOM:
```bash
curl -X POST "http://127.0.0.1:8000/upload_and_generate_sbom" `
>> -H "accept: application/json" `  
>> -H "Content-Type: multipart/form-data" `  
>> -F 'file=@C:\Users\Madhu2277\go-backend-clean-architecture\go.mod' `  
>> -F 'id=1'  
```

Get generated SBOM by ID:
```bash
curl -X GET "http://127.0.0.1:8000/generate_sbom/1"
```

SBOM entry removed fro
```bash
curl -X DELETE "http://127.0.0.1:8000/generate_sbom/1" 
```


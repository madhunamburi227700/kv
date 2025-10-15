from pathlib import Path

def is_golang_project(repo_path: Path) -> bool:
    """Check if folder contains go.mod and go.sum"""
    return (repo_path / "go.mod").exists() and (repo_path / "go.sum").exists()

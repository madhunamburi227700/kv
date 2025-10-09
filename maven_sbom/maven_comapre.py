import json
import re
from pathlib import Path

def normalize_name(name: str) -> str:
    """Normalize names for consistent comparison."""
    if not name:
        return ""
    name = name.lower().replace("_", ".").replace("-", ".")
    name = re.sub(r"\.+", ".", name)
    return name.strip(".")

def load_sbom(sbom_file: str):
    """Load SBOM JSON and return dict: (group,name) -> (version, line_number)."""
    with open(sbom_file, encoding="utf-8") as f:
        data = json.load(f)

    deps = {}

    def recurse(components):
        for comp in components:
            group = normalize_name(comp.get("group") or "")
            name = normalize_name(comp.get("name") or "")
            version = comp.get("version") or ""
            line_number = 0
            if group and name and version:
                deps[(group, name)] = (version, line_number)
            if "components" in comp and comp["components"]:
                recurse(comp["components"])

    if "components" in data:
        recurse(data["components"])

    return deps

def load_dependency_tree(tree_file: str):
    """Load dependency tree JSON and return dict: (group,name) -> (version, line_number)."""
    with open(tree_file, encoding="utf-8") as f:
        data = json.load(f)

    deps = {}

    def recurse(dep_list):
        for dep in dep_list:
            group = normalize_name(dep.get("group") or "")
            name = normalize_name(dep.get("name") or "")
            version = dep.get("version") or ""
            line_number = 0
            if group and name and version:
                deps[(group, name)] = (version, line_number)
            if "dependencies" in dep and dep["dependencies"]:
                recurse(dep["dependencies"])

    if "configurations" in data:
        for config in data["configurations"]:
            recurse(config.get("dependencies", []))

    return deps

def compare_dependencies(sbom_deps, tree_deps):
    sbom_only, tree_only, version_mismatch, exact_matches = [], [], [], []
    all_keys = set(sbom_deps.keys()).union(set(tree_deps.keys()))
    for key in all_keys:
        sbom_val = sbom_deps.get(key)
        tree_val = tree_deps.get(key)
        sbom_version, sbom_line = sbom_val if sbom_val else (None, None)
        tree_version, tree_line = tree_val if tree_val else (None, None)

        if sbom_version and not tree_version:
            sbom_only.append((key[0], key[1], sbom_version, sbom_line))
        elif tree_version and not sbom_version:
            tree_only.append((key[0], key[1], tree_version, tree_line))
        elif sbom_version != tree_version:
            version_mismatch.append((key[0], key[1], sbom_version, sbom_line, tree_version, tree_line))
        else:
            exact_matches.append((key[0], key[1], sbom_version, sbom_line, tree_line))

    return sbom_only, tree_only, version_mismatch, exact_matches

def save_comparison(sbom_only, tree_only, version_mismatch, exact_matches, output_file: str):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("==== Dependencies in SBOM but missing in dependency tree ====\n")
        if sbom_only:
            for group, name, version, line in sorted(sbom_only):
                f.write(f"{group}:{name} -> {version}\n")
        else:
            f.write("None\n")

        f.write("\n==== Dependencies in dependency tree but missing in SBOM ====\n")
        if tree_only:
            for group, name, version, line in sorted(tree_only):
                f.write(f"{group}:{name} -> {version}\n")
        else:
            f.write("None\n")

        f.write("\n==== Version mismatches ====\n")
        if version_mismatch:
            for group, name, sbom_v, sbom_line, tree_v, tree_line in sorted(version_mismatch):
                f.write(f"{group}:{name} -> SBOM: {sbom_v}, Tree: {tree_v}\n")
        else:
            f.write("None\n")

        f.write("\n==== Exact matches ====\n")
        if exact_matches:
            for group, name, version, sbom_line, tree_line in sorted(exact_matches):
                f.write(f"{group}:{name} -> {version}\n")
        else:
            f.write("None\n")

def compare_sbom_and_tree(sbom_file: str, tree_file: str, output_file: str):
    sbom_deps = load_sbom(sbom_file)
    tree_deps = load_dependency_tree(tree_file)
    sbom_only, tree_only, version_mismatch, exact_matches = compare_dependencies(sbom_deps, tree_deps)
    save_comparison(sbom_only, tree_only, version_mismatch, exact_matches, output_file)

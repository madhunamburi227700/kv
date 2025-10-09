import json
import re
import sys

# --- Regexes ---
DEP_LINE_RE = re.compile(r'^\s*[\|\s\\+]*[\\+]-\s+(.+)$')
DEP_PREFIX_RE = re.compile(r'^(\s*[\|\s\\+]*?)[\\+]-')


def parse_gradle_dependencies(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {"configurations": []}

    configurations = []
    current_config = None
    stack = []

    def create_dependency(notation_line):
        parts = notation_line.strip().split(':')
        dep = {}
        if len(parts) >= 5:
            dep["group"], dep["name"], dep["type"], dep["version"], dep["scope"] = [p.strip() for p in parts[:5]]
        elif len(parts) == 4:
            dep["group"], dep["name"], dep["type"], dep["version"] = [p.strip() for p in parts[:4]]
        elif len(parts) == 3:
            dep["group"], dep["name"], dep["version"] = [p.strip() for p in parts[:3]]
        else:
            return None
        dep["dependencies"] = []
        return dep

    def get_depth(line):
        m = DEP_PREFIX_RE.match(line)
        if not m:
            return 0
        prefix = m.group(1)
        cleaned = re.sub(r'[|+]', '', prefix)
        spaces = len(cleaned)
        return spaces // 2

    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped and not stripped.startswith(('+', '|', '\\')):
            top_dep = create_dependency(stripped)
            if not top_dep:
                top_dep = {"name": stripped, "dependencies": []}
            configurations.append(top_dep)
            current_config = top_dep
            stack.clear()
            continue

        m = DEP_LINE_RE.match(raw_line)
        if not m or current_config is None:
            continue

        notation = m.group(1).strip()
        dep = create_dependency(notation)
        if not dep:
            continue

        depth = get_depth(raw_line)
        while stack and stack[-1]["depth"] >= depth:
            stack.pop()

        if stack:
            parent = stack[-1]["node"]
            parent["dependencies"].append(dep)
        else:
            current_config["dependencies"].append(dep)

        stack.append({"depth": depth, "node": dep})

    return {"configurations": configurations}


def save_dependencies_to_json(parsed_data, output_file):
    try:
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2)
        print(f"✅ Dependencies JSON saved to {output_file}")
    except Exception as e:
        print(f"❌ Error writing JSON: {e}")

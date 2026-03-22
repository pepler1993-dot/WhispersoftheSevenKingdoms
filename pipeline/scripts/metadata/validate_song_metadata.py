#!/usr/bin/env python3
"""Validate song metadata JSON files against the project schema."""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "song.schema.json"
DEFAULT_TARGET = REPO_ROOT / "data" / "upload" / "metadata"


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_brief_object(value, field_name, errors):
    if value is None:
        return
    if not isinstance(value, dict):
        errors.append(f"Field {field_name} must be an object")
        return

    allowed = (
        ["style", "influences", "tempo", "energy", "avoid"]
        if field_name == "music_brief"
        else ["scene", "elements", "text", "style", "avoid"]
    )

    for key in value:
        if key not in allowed:
            errors.append(f"Unexpected field {field_name}.{key}")

    array_fields = {"influences", "avoid", "elements"}
    for key, val in value.items():
        if key in array_fields:
            if not isinstance(val, list):
                errors.append(f"Field {field_name}.{key} must be an array")
            else:
                for i, item in enumerate(val):
                    if not isinstance(item, str) or not item.strip():
                        errors.append(f"Field {field_name}.{key}[{i}] must be a non-empty string")
        elif not isinstance(val, str):
            errors.append(f"Field {field_name}.{key} must be a string")


def validate_song(data, schema):
    errors = []
    allowed_top = set(schema.get("properties", {}).keys())

    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"Missing required field: {field}")

    for key in data:
        if key not in allowed_top:
            errors.append(f"Unexpected top-level field: {key}")

    slug_pattern = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    if "slug" in data and not slug_pattern.match(data["slug"]):
        errors.append("Field slug must match ^[a-z0-9]+(?:-[a-z0-9]+)*$")

    if "title" in data and (not isinstance(data["title"], str) or not data["title"].strip()):
        errors.append("Field title must be a non-empty string")

    if "platform" in data:
        allowed_platforms = ["youtube", "spotify", "soundcloud"]
        if not isinstance(data["platform"], str) or data["platform"] not in allowed_platforms:
            errors.append(f"Field platform must be one of: {', '.join(allowed_platforms)}")

    if "theme" in data and (not isinstance(data["theme"], str) or not data["theme"].strip()):
        errors.append("Field theme must be a non-empty string")

    if "mood" in data:
        if not isinstance(data["mood"], list) or len(data["mood"]) == 0:
            errors.append("Field mood must be a non-empty array")
        else:
            for i, item in enumerate(data["mood"]):
                if not isinstance(item, str) or not item.strip():
                    errors.append(f"Field mood[{i}] must be a non-empty string")

    for field in ("notes", "duration_hint"):
        if field in data and not isinstance(data[field], str):
            errors.append(f"Field {field} must be a string")

    validate_brief_object(data.get("music_brief"), "music_brief", errors)
    validate_brief_object(data.get("thumbnail_brief"), "thumbnail_brief", errors)

    return errors


def list_json_files(target_path):
    p = Path(target_path)
    if p.is_file():
        return [p]
    return sorted(p.glob("*.json"))


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TARGET
    schema = load_json(SCHEMA_PATH)
    files = list_json_files(target)

    if not files:
        print("No JSON metadata files found.")
        sys.exit(1)

    failed = 0
    for file in files:
        try:
            data = load_json(file)
            errors = validate_song(data, schema)
            rel = file.relative_to(REPO_ROOT)
        except Exception as e:
            failed += 1
            try:
                rel = file.relative_to(REPO_ROOT)
            except ValueError:
                rel = file
            print(f"FAIL {rel}")
            print(f"  - Invalid JSON or unreadable file: {e}")
            continue

        if not errors:
            print(f"PASS {rel}")
        else:
            failed += 1
            print(f"FAIL {rel}")
            for error in errors:
                print(f"  - {error}")

    print("---")
    print(f"Checked files: {len(files)}")
    print(f"Failures: {failed}")
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()

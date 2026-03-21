#!/usr/bin/env python3
"""
Memory Briefing Generator – Whispers of the Seven Kingdoms

Erstellt eine kurze, tägliche/bei Bedarf-Briefing-Datei für Agents.
Holt Kerninfos aus PROJECT_STATUS.md und fragt offene PRs ab.

Usage:
    python generate_briefing.py
Output:
    BRIEFING.md im Repo-Root (überschreibt Vorversion)
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_STATUS_PATH = REPO_ROOT / "PROJECT_STATUS.md"
BRIEFING_PATH = REPO_ROOT / "BRIEFING.md"

GITHUB_API = "https://api.github.com/repos/pepler1993-dot/WhispersoftheSevenKingdoms"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # optional, erhöht Rate-Limit


def run_curl(url: str) -> dict:
    cmd = ["curl", "-s"]
    if GITHUB_TOKEN:
        cmd += ["-H", f"Authorization: token {GITHUB_TOKEN}"]
    cmd += [url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def get_open_prs() -> List[Dict]:
    data = run_curl(f"{GITHUB_API}/pulls?state=open&per_page=30")
    return data if isinstance(data, list) else []


def get_issue(issue_number: int) -> dict:
    data = run_curl(f"{GITHUB_API}/issues/{issue_number}")
    return data if isinstance(data, dict) else {}


def parse_project_status() -> Dict[str, str]:
    sections = {
        "goal": "",
        "team": "",
        "done": "",
        "in_progress": "",
        "blockers": "",
        "next_steps": ""
    }
    if not PROJECT_STATUS_PATH.exists():
        return sections

    content = PROJECT_STATUS_PATH.read_text(encoding="utf-8")
    # Einfache Section-Parser basierend auf Headern
    current = None
    lines = []
    for line in content.splitlines():
        if line.startswith("## "):
            header = line[3:].strip().lower()
            if current:
                sections[current] = "\n".join(lines).strip()
            current = None
            for key in sections:
                if key in header or header.startswith(key):
                    current = key
                    lines = []
                    break
            continue
        if current:
            lines.append(line)
    if current and lines:
        sections[current] = "\n".join(lines).strip()
    return sections


def extract_meilensteine(text: str) -> List[str]:
    # Nimm nur erledigte Items (✅)
    items = []
    for line in text.splitlines():
        if "✅" in line or "- [x]" in line.lower() or line.strip().startswith("✅"):
            items.append(line.strip())
    return items[:10]


def format_pr_list(prs: List[Dict]) -> List[str]:
    out = []
    for pr in prs:
        number = pr.get("number")
        title = pr.get("title", "No title")
        user = pr.get("user", {}).get("login", "unknown")
        out.append(f"• PR #{number}: {title} (by @{user})")
    return out


def main():
    # 1. Projektstatus lesen
    status = parse_project_status()

    # 2. Offene PRs holen
    open_prs = get_open_prs()
    pr_summary = format_pr_list(open_prs)

    # 3. Blocker aus PROJECT_STATUS extrahieren (Tabelle oder Liste)
    blockers = []
    if "Blocker" in status["blockers"]:
        blocker_lines = status["blockers"].splitlines()
        for line in blocker_lines:
            if line.strip().startswith("|") or "**" in line:
                continue
            if line.strip().startswith("-"):
                blockers.append(line.strip())

    # 4. Nächste Schritte
    next_steps = []
    for line in (status.get("next_steps") or "").splitlines():
        if line.strip().startswith("-") or line.strip().startswith("*"):
            next_steps.append(line.strip())

    # 5. Team
    team_lines = status.get("team", "").splitlines()
    team = [l for l in team_lines if l.strip() and not l.startswith("|") and "Ziel" not in l]

    briefing = f"""# BRIEFING – Whispers of the Seven Kingdoms
> Automatisch generiert am {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## 🎯 Ziel
Vollautomatisierte YouTube-Pipeline für GoT-themed Sleep Music.

## 👥 Team
{chr(10).join(team) if team else '- Keine Team-Info gefunden'}

## ✅ Erreichte Meilensteine
{chr(10).join(extract_meilensteine(status.get('done', ''))) or '- Keine vollständigen Meilensteine im Status gefunden'}

## 🔄 In Arbeit / Offen
{chr(10).join(next_steps) if next_steps else '- Keine spezifischen nächsten Schritte dokumentiert'}

## 🚧 Blocker
{chr(10).join(blockers[:5]) if blockers else '- Keine bekannten Blocker'}

## 📥 Offene PRs ({len(open_prs)})
{chr(10).join(pr_summary) if pr_summary else '- Keine offenen PRs'}

## 📂 Wichtige Pfade
- `publishing/musicgen/` – MusicGen-Pipeline
- `scripts/metadata/metadata_gen.py` – Metadaten
- `scripts/thumbnails/generate_thumbnail.py` – Thumbnails
- `scripts/video/render.py` – Video-Rendering
- `scripts/publish/youtube_upload.py` – YouTube Upload
- `pipeline.py` – End-to-End Orchestrierung

## 🔗 Nützlich
- Repo: https://github.com/pepler1993-dot/WhispersoftheSevenKingdoms
- PROJECT_STATUS.md ausführlich
- Sync-Service: {os.getenv('SYNC_BASE_URL', 'n/a')}

---
*Dieses Dokument wird automatisch generiert. Für Änderungen die Quelle (SCRIPT) anpassen.*
"""
    BRIEFING_PATH.write_text(briefing, encoding="utf-8")
    print(f"✅ Briefing geschrieben: {BRIEFING_PATH} ({len(briefing)} Zeichen)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

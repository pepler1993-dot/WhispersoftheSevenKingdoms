#!/usr/bin/env python3
"""Run metadata validation and write a preflight report."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
REPORTS_DIR = REPO_ROOT / "data" / "work" / "publish" / "reports"
VALIDATOR = REPO_ROOT / "pipeline" / "scripts" / "metadata" / "validate_song_metadata.py"


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "data/upload/metadata"
    target_path = (REPO_ROOT / target).resolve()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(target_path)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    timestamp = datetime.now(timezone.utc).isoformat()
    report = {
        "type": "metadata-preflight",
        "timestamp": timestamp,
        "target": str(Path(target_path).relative_to(REPO_ROOT)),
        "exitCode": result.returncode,
        "status": "pass" if result.returncode == 0 else "fail",
        "stdout": result.stdout.rstrip(),
        "stderr": result.stderr.rstrip(),
    }

    latest = REPORTS_DIR / "metadata-preflight.latest.json"
    stamped = REPORTS_DIR / f"metadata-preflight.{timestamp.replace(':', '-')}.json"

    for p in (latest, stamped):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            f.write("\n")

    print(f"Report written: {latest.relative_to(REPO_ROOT)}")
    print(f"Snapshot written: {stamped.relative_to(REPO_ROOT)}")
    if report["stdout"]:
        print(report["stdout"])
    if report["stderr"]:
        print(report["stderr"], file=sys.stderr)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()

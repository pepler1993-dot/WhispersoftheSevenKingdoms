#!/usr/bin/env python3
"""
Upload – Lädt generierte Tracks zu GitHub oder Nextcloud hoch.
"""

import base64
import os

import requests


def upload_to_github(file_path, track_name, config):
    """Upload einer Datei zu GitHub via Contents API."""
    gh_config = config["upload"]["github"]
    token = os.environ.get(gh_config["token_env"], "")

    if not token:
        print(f"❌ GitHub Token nicht gefunden. Setze {gh_config['token_env']} als Umgebungsvariable.")
        return False

    with open(file_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()

    ext = os.path.splitext(file_path)[1]
    upload_path = f"{gh_config['path']}/{track_name}{ext}"
    api_url = f"https://api.github.com/repos/{gh_config['repo']}/contents/{upload_path}"

    # Check if file already exists (need SHA for update)
    r = requests.get(api_url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    })

    payload = {
        "message": f"Add generated track: {track_name}",
        "content": content_b64,
        "branch": gh_config["branch"],
    }

    if r.status_code == 200:
        # File exists, need SHA for update
        payload["sha"] = r.json()["sha"]
        payload["message"] = f"Update generated track: {track_name}"

    r = requests.put(api_url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }, json=payload)

    if r.status_code in [200, 201]:
        print(f"✅ GitHub: {upload_path}")
        print(f"🔗 {r.json()['content']['html_url']}")
        return True
    else:
        print(f"❌ GitHub Fehler: {r.status_code} – {r.text[:200]}")
        return False


def upload_to_nextcloud(file_path, track_name, config):
    """Upload einer Datei zu Nextcloud via WebDAV."""
    nc_config = config["upload"]["nextcloud"]
    password = os.environ.get(nc_config["pass_env"], "")

    if not nc_config["url"] or not nc_config["user"]:
        print("❌ Nextcloud nicht konfiguriert (URL/User fehlt)")
        return False

    if not password:
        print(f"❌ Nextcloud Passwort nicht gefunden. Setze {nc_config['pass_env']} als Umgebungsvariable.")
        return False

    ext = os.path.splitext(file_path)[1]
    webdav_url = (
        f"{nc_config['url']}/remote.php/dav/files/"
        f"{nc_config['user']}{nc_config['path']}{track_name}{ext}"
    )

    with open(file_path, "rb") as f:
        r = requests.put(
            webdav_url,
            data=f,
            auth=(nc_config["user"], password),
            headers={"Content-Type": "audio/mpeg"},
        )

    if r.status_code in [200, 201, 204]:
        print(f"✅ Nextcloud: {nc_config['path']}{track_name}{ext}")
        return True
    else:
        print(f"❌ Nextcloud Fehler: {r.status_code} – {r.text[:200]}")
        return False


def upload_track(file_path, track_name, config):
    """Uploadet einen Track zum konfigurierten Ziel."""
    target = config["upload"]["target"]

    print(f"\n📤 Upload: {target}...")

    if target == "github":
        return upload_to_github(file_path, track_name, config)
    elif target == "nextcloud":
        return upload_to_nextcloud(file_path, track_name, config)
    elif target == "local":
        print(f"📁 Lokal gespeichert: {file_path}")
        return True
    else:
        print(f"❌ Unbekanntes Upload-Ziel: {target}")
        return False


if __name__ == "__main__":
    import argparse
    import yaml

    parser = argparse.ArgumentParser(description="Upload track to GitHub/Nextcloud")
    parser.add_argument("file", help="Dateipfad")
    parser.add_argument("--name", required=True, help="Track-Name")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--target", choices=["github", "nextcloud", "local"])

    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    if args.target:
        config["upload"]["target"] = args.target

    upload_track(args.file, args.name, config)

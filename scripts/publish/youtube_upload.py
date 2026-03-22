#!/usr/bin/env python3
"""
YouTube Upload – Whispers of the Seven Kingdoms

Uploadet Videos zu YouTube via Google API v3 mit OAuth2.

Setup (einmalig):
    1. Google Cloud Console: Projekt erstellen
    2. YouTube Data API v3 aktivieren
    3. OAuth2 Client ID erstellen (Desktop App)
    4. client_secret.json herunterladen
    5. GOOGLE_CLIENT_SECRET env var setzen (Pfad zur Datei)

Usage:
    python youtube_upload.py --video video.mp4 --metadata meta.json
    python youtube_upload.py --video video.mp4 --metadata meta.json --public
    python youtube_upload.py --setup  (OAuth2 Token holen)
"""

import argparse
import json
import os
import sys
import time

# Optional imports – nur wenn tatsächlich uploaden
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    HAS_GOOGLE_API = True
except ImportError:
    HAS_GOOGLE_API = False

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TOKEN_PATH = os.path.join(REPO_ROOT, ".youtube_token.json")

# Retry config
MAX_RETRIES = 3
RETRY_DELAY = 5


def check_dependencies():
    """Prüft ob Google API Libraries installiert sind."""
    if not HAS_GOOGLE_API:
        print("❌ Google API Libraries fehlen. Installiere mit:")
        print("   pip install google-api-python-client google-auth-oauthlib")
        sys.exit(1)


def get_credentials():
    """Holt oder refreshed OAuth2 Credentials."""
    creds = None

    # Existing token?
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # Refresh or new auth needed?
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Token wird refreshed...")
            creds.refresh(Request())
        else:
            # New auth flow
            client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "client_secret.json")
            if not os.path.exists(client_secret):
                print(f"❌ Client Secret nicht gefunden: {client_secret}")
                print("   Setze GOOGLE_CLIENT_SECRET env var oder lege client_secret.json ab.")
                sys.exit(1)

            print("🔐 OAuth2 Authorization Flow...")
            print("   Ein Browser-Fenster öffnet sich. Bitte einloggen und bestätigen.")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0)

        # Token speichern
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print(f"✅ Token gespeichert: {TOKEN_PATH}")

    return creds


def upload_video(youtube, video_path, metadata, privacy="private"):
    """Uploadet ein Video zu YouTube."""
    titles = metadata.get("titles", {})
    title = titles.get("primary", metadata.get("title", "Untitled"))
    description = metadata.get("description", "")
    tags = metadata.get("tags", [])
    category = metadata.get("category", "10")  # Music

    body = {
        "snippet": {
            "title": title[:100],  # YouTube max 100 chars
            "description": description[:5000],  # YouTube max 5000 chars
            "tags": tags[:500],  # YouTube limit
            "categoryId": category,
            "defaultLanguage": metadata.get("language", "en"),
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 10,  # 10MB chunks
    )

    print(f"📤 Uploade: {os.path.basename(video_path)}")
    print(f"🎵 Titel: {title}")
    print(f"🔒 Privacy: {privacy}")

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    retry = 0

    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   Upload: {progress}%")
        except Exception as e:
            retry += 1
            if retry > MAX_RETRIES:
                print(f"❌ Upload fehlgeschlagen nach {MAX_RETRIES} Versuchen: {e}")
                return None
            print(f"⚠️  Retry {retry}/{MAX_RETRIES} in {RETRY_DELAY}s: {e}")
            time.sleep(RETRY_DELAY)

    video_id = response["id"]
    print(f"✅ Upload erfolgreich!")
    print(f"🔗 https://youtube.com/watch?v={video_id}")

    return video_id


def add_to_playlist(youtube, video_id, playlist_name):
    """Fügt Video zu einer Playlist hinzu (sucht nach Name)."""
    # Playlists des Kanals abrufen
    playlists = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50,
    ).execute()

    playlist_id = None
    for pl in playlists.get("items", []):
        if pl["snippet"]["title"].lower() == playlist_name.lower():
            playlist_id = pl["id"]
            break

    if not playlist_id:
        print(f"⚠️  Playlist '{playlist_name}' nicht gefunden, überspringe.")
        return False

    youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id,
                },
            },
        },
    ).execute()

    print(f"📋 Zu Playlist hinzugefügt: {playlist_name}")
    return True


def setup_auth():
    """Interaktiver OAuth2 Setup."""
    check_dependencies()
    print("🔐 YouTube OAuth2 Setup\n")
    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    # Test: Kanal-Info abrufen
    channels = youtube.channels().list(part="snippet", mine=True).execute()
    if channels["items"]:
        channel = channels["items"][0]["snippet"]
        print(f"\n✅ Verbunden mit: {channel['title']}")
    else:
        print("\n⚠️  Kein YouTube-Kanal gefunden.")


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Upload – Whispers of the Seven Kingdoms"
    )
    parser.add_argument("--video", type=str, help="Pfad zur Video-Datei (MP4)")
    parser.add_argument("--metadata", type=str, help="Pfad zur Metadaten-JSON")
    parser.add_argument("--public", action="store_true",
                        help="Video als öffentlich hochladen (Standard: privat)")
    parser.add_argument("--playlist", action="store_true",
                        help="Video automatisch zu Playlists hinzufügen")
    parser.add_argument("--setup", action="store_true",
                        help="OAuth2 Setup durchführen")

    args = parser.parse_args()

    if args.setup:
        setup_auth()
        return

    if not args.video or not args.metadata:
        parser.print_help()
        print("\n💡 Erst --setup ausführen für OAuth2.")
        return

    check_dependencies()

    # Video prüfen
    if not os.path.exists(args.video):
        print(f"❌ Video nicht gefunden: {args.video}")
        sys.exit(1)

    # Metadaten laden
    if not os.path.exists(args.metadata):
        print(f"❌ Metadaten nicht gefunden: {args.metadata}")
        sys.exit(1)

    with open(args.metadata, encoding="utf-8") as f:
        metadata = json.load(f)

    # Auth
    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    # Upload
    privacy = "public" if args.public else metadata.get("privacy", "private")
    video_id = upload_video(youtube, args.video, metadata, privacy)

    if not video_id:
        sys.exit(1)

    # Playlist
    if args.playlist and "playlists" in metadata:
        for playlist_name in metadata["playlists"]:
            try:
                add_to_playlist(youtube, video_id, playlist_name)
            except Exception as e:
                print(f"⚠️  Playlist-Fehler: {e}")

    print(f"\n🎉 Fertig! Video: https://youtube.com/watch?v={video_id}")


if __name__ == "__main__":
    main()

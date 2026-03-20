import os
import time
from datetime import datetime

UPLOAD_SONGS = 'upload/songs'
UPLOAD_THUMBNAILS = 'upload/thumbnails'
UPLOAD_DONE = 'upload/done'

# Dummy-Uploadfunktion (YouTube/API integrieren!)
def upload_to_youtube(song_path, thumbnail_path, title, description):
    print(f"[UPLOAD] Song: {song_path}\nThumbnail: {thumbnail_path}\nTitle: {title}\nDescription: {description}\n---")
    # Hier sollte der echte Upload laufen
    return True

def auto_upload():
    os.makedirs(UPLOAD_SONGS, exist_ok=True)
    os.makedirs(UPLOAD_THUMBNAILS, exist_ok=True)
    os.makedirs(UPLOAD_DONE, exist_ok=True)
    
    for song in os.listdir(UPLOAD_SONGS):
        if not song.lower().endswith(('.mp3', '.wav', '.ogg')):
            continue
        song_path = os.path.join(UPLOAD_SONGS, song)
        # Thumbnail mit gleichem Namen (außer Endung) suchen
        base = os.path.splitext(song)[0]
        thumb = None
        for ext in ('.jpg', '.png', '.webp'):
            tp = os.path.join(UPLOAD_THUMBNAILS, base+ext)
            if os.path.exists(tp):
                thumb = tp
                break
        
        # Automatisch Titel & Beschreibung generieren
        date = datetime.now().strftime('%Y-%m-%d')
        title = f"{base.replace('_', ' ').title()} (GoT Sleep Song, {date})"
        description = f"Einschlaflied im Stil von Game of Thrones. Song: {base}. Automatisiert hochgeladen am {date}. #GoT #Sleep #Lullaby"
        
        # Upload durchführen
        success = upload_to_youtube(song_path, thumb, title, description)
        if success:
            # Dateien verschieben
            os.rename(song_path, os.path.join(UPLOAD_DONE, song))
            if thumb:
                os.rename(thumb, os.path.join(UPLOAD_DONE, os.path.basename(thumb)))
            print(f"Fertig: {base}")
        else:
            print(f"Fehler beim Upload: {base}")

if __name__ == "__main__":
    auto_upload()

# Audio Strategy

## Zweck
Diese Seite beschreibt den **aktuellen** Audio-Produktionspfad im Repo und die wichtigsten Prinzipien.

---

## Produktionsstand (verbindlich)

- **Einziger unterstützter Generierungspfad:** **Stable Audio Open** auf dem **lokalen GPU-Worker** (`stable-audio-local`).
- **Code:** `services/sync/app/audio_jobs.py` (Jobs), `services/sync/app/stable_audio_gen.py` (SSH/Daemon zum Worker).
- **Ausgabe:** fertige Tracks unter `data/upload/songs/<slug>.wav` (bzw. von der Pipeline akzeptierte Formate).
- **Kaggle, MusicGen-Colab und das frühere `musicgen/`-Verzeichnis** sind aus dem aktiven Code entfernt und gehören nicht mehr zur Betriebsrealität.

---

## Architekturprinzip

- **Dashboard** startet und überwacht Audio-Jobs.
- **Pipeline** (`pipeline/pipeline.py`) erwartet nur **vorhandenes Audio** am Slug — unabhängig davon, wie es erzeugt wurde.
- Kurze Clips plus **Looping / Crossfade / Post-Processing** in der Pipeline bleiben ein praktischer Hebel für lange Sleep-Tracks.

---

## Kurze Tracks + Looping

Statt in einem Schritt sehr lange Rohstücke zu erzeugen:

- kürzere Abschnitte generieren (Worker-Clip-Länge, typisch bis 30–47 s je nach Setup)
- in der Pipeline loopen, crossfaden, post-processen
- für lange YouTube-Versionen nutzen

Vorteile: weniger VRAM pro Schritt, schnellere Iteration, gut passend zum Sleep-Use-Case.

---

## GPU-Worker

- Modell: **Stable Audio Open** (siehe `stable_audio_gen.py`, `MODEL_NAME`).
- Daemon-Modus bevorzugt (Modell bleibt im VRAM); sonst Cold-Start-Pfad auf dem Worker.
- Konfiguration u. a. über Umgebungsvariablen: `GPU_WORKER_HOST`, `GPU_WORKER_USER`, `GPU_WORKER_SSH_KEY`, `GPU_WORKER_OUTPUT_DIR`, `GPU_WORKER_CODE_DIR` (Standard-Pfad zum Worker-Code auf der VM: `/opt/stable-audio-worker`).

---

## Historisch / Archiv

Evaluierung und Begründung aus der Übergangsphase (Kaggle, Colab, MusicGen, API-Anbieter):

- [`../AUDIO_GENERATION_ALTERNATIVES_EVALUATION.md`](../AUDIO_GENERATION_ALTERNATIVES_EVALUATION.md) — **archiviert**, Inhalt unverändert außer Kopf-Hinweis dort.

Frühere Feedback-Dateien zu Audio-Alternativen wurden aus dem Repo entfernt; die Evaluation-Datei reicht als Nachvollziehbarkeit.

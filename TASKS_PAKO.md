# Aufgaben für Pako

## Aktuelle Tasks

### #21 – Pipeline Prepare/Resume für Colab GPU-Worker (PRIORITÄT 1)
`pipeline.py` erweitern mit `--prepare` und `--resume` Flags.
- `--prepare`: Job-Datei erstellen, Prompt aus prompts.json, Status "pending"
- `--resume`: Prüft ob Audio da ist, dann Thumbnail→Video→Metadaten→Upload
- Status-Modell: NUR 3 Stufen (`pending`, `audio_ready`, `done`)
- Colab-Notebook anpassen: Job von Google Drive lesen, Audio zurückschreiben
- **KEIN Watcher-Service, KEIN colab_export.py, KEINE 8 Status-Stufen**
- Details: GitHub Issue #21

### #22 – Proxmox GPU-Passthrough Anleitung (PRIORITÄT 2)
Schritt-für-Schritt Doku für Kevin: `docs/GPU_SETUP_PROXMOX.md`
- BIOS, GRUB, VFIO, VM-Config, NVIDIA Treiber, CUDA, audiocraft
- Klickpfad-Stil, kein Theorie-Gelaber
- Details: GitHub Issue #22

## Erledigte Tasks
- ✅ #7 Video-Rendering (PR #18)
- ✅ #10 Pipeline-Orchestrierung (PR #20)

## Regeln
- Branch: `feature/pako-{task}`
- Sync-Service: Read → Claim → Work → Heartbeat → Release
- Smith reviewed und merged deine PRs
- **Halte es schlank** – lieber 50 Zeilen guter Code als 200 Zeilen Over-Engineering

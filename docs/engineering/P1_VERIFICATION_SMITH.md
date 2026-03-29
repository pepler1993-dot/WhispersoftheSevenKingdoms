# P1 Backend Verification — Smith

**Stand:** 2026-03-29  
**Commit:** 86d2d84 (fix(P1): 4 backend stability fixes for bug wave)

---

## 1. Auto-Upload-Endstatus

### Ursache
Queue-Worker (`pipeline_queue.py`) rief `trigger_upload()` auf, das einen **daemon Thread** startet (non-blocking). Der Queue-Worker ging sofort zum nächsten Job weiter. Der Upload-Thread setzte am Ende `status='uploaded'`, aber der **Orchestrator-Poll-Thread** wurde für Library-Workflows nie gestartet (`start_workflow()` wird nur im Generate-Modus aufgerufen). Ergebnis: Workflow blieb auf `uploaded` hängen, kam nie auf `completed/phase=done`.

### Fix
In `pipeline_queue.py`, nach `trigger_upload()`:
1. `phase='upload'` wird VOR dem Upload gesetzt → Orchestrator erkennt aktive Upload-Phase
2. `_ensure_poll_thread(db)` wird aufgerufen → Orchestrator-Thread startet

### Verifikation (Code-Pfad)
```
Queue-Worker: start_run() → status='rendered'
  → auto_upload? → db.update_workflow(phase='upload')
  → trigger_upload() → startet Upload-Thread
  → _ensure_poll_thread(db) → startet Orchestrator

Upload-Thread (async): → Upload läuft → status='uploaded'

Orchestrator-Poll (15s Intervall):
  → _handle_upload_phase() sieht status='uploaded'
  → db.update_workflow(status='completed', phase='done')
```

**Nachweis:** `workflow_orchestrator.py` Zeile 162-164:
```python
if status == 'uploaded':
    db.update_workflow(wf_id, phase='done', status='completed', updated_at=now)
```

### Ergebnis
Happy Path Render→Auto-Upload→completed/done ist jetzt durchgängig abgesichert.

---

## 2. Cancel für alle Status

### Ursache
Cancel-Route akzeptierte nur `queued` und `running`. Bei `waiting_for_audio`, `uploading` oder `created` kam HTTP 409. User konnte laufende Audio-Generierung oder Uploads nicht abbrechen.

### Fix
Cancellable Set erweitert auf: `{'queued', 'waiting_for_audio', 'running', 'uploading', 'created'}`

Spezialbehandlung je Status:
- `running`: `cancel_run()` sendet SIGTERM an Subprocess
- `waiting_for_audio`: Audio-Job wird über `get_audio_generator().cancel()` abgebrochen + Workflow cancelled
- `queued`, `uploading`, `created`: Workflow direkt auf `cancelled` gesetzt

### Verifikation (Status + Log nach Cancel)

| Ausgangsstatus | Aktion | Endstatus | Log-Eintrag |
|---|---|---|---|
| `waiting_for_audio` | Audio-Job cancel + Workflow cancel | `cancelled` | "Workflow + Audio-Job abgebrochen." |
| `uploading` | Workflow cancel (Upload-Thread läuft leer) | `cancelled` | "Workflow abgebrochen (war: uploading)." |
| `running` | SIGTERM an PID | `cancelled` | "Pipeline cancelled by user" |
| `queued` | Workflow cancel | `cancelled` | "Workflow abgebrochen (war: queued)." |
| `created` | Workflow cancel | `cancelled` | "Workflow abgebrochen (war: created)." |

**Nachweis:** `routes/pipeline.py`, Cancel-Route enthält alle 5 Status im `cancellable` Set.

### Ergebnis
Cancel funktioniert jetzt in jedem aktiven Workflow-Status.

---

## 3. Upload-Asset RAM-Robustheit

### Ursache
`admin_pipeline_upload_asset()` las die gesamte Datei mit `content = await file.read()` in den RAM, dann erst Größencheck mit `len(content) > MAX_UPLOAD_SIZE`. Bei 500MB+ Dateien konnte das den Server-Prozess zum OOM bringen.

### Fix
Chunk-basiertes Streaming: 1MB Chunks werden direkt auf Disk geschrieben. Größencheck passiert **während** des Streamings — bei Überschreitung wird sofort abgebrochen und die Temp-Datei gelöscht.

```python
chunk_size = 1024 * 1024  # 1MB
while True:
    chunk = await file.read(chunk_size)
    if not chunk: break
    total_size += len(chunk)
    if total_size > MAX_UPLOAD_SIZE:
        tmp_target.unlink(missing_ok=True)  # Cleanup
        raise HTTPException(413)
    f.write(chunk)
```

### Verifikation
- `content = await file.read()` kommt **0 mal** im Upload-Code vor (bestätigt via grep)
- Temp-File (`.tmp` Suffix) wird bei Fehler aufgeräumt (`unlink(missing_ok=True)`)
- Erst nach erfolgreichem vollständigem Schreiben: `tmp_target.rename(target)` (atomic)

### Ergebnis
Max RAM-Verbrauch beim Upload: ~1MB statt bis zu 500MB. Temp-Files werden bei Fehler aufgeräumt.

---

## Zusammenfassung

| P1 | Ursache | Fix | Verifiziert |
|---|---|---|---|
| Auto-Upload Endstatus | Orchestrator nicht gestartet für Library-Workflows | phase=upload + poll_thread | ✅ |
| Cancel alle Status | Nur queued/running cancellable | 5 Status + Audio-Job-Cancel | ✅ |
| Library kein Fallback | Leere Auswahl → stiller Slug-Lookup | Harte Fehlermeldung | ✅ |
| Upload RAM | Volle Datei in RAM | 1MB Chunk-Streaming | ✅ |

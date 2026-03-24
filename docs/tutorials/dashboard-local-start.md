# Tutorial – Dashboard lokal starten

## Ziel
In diesem Tutorial startest du das Dashboard lokal und prüfst, ob die wichtigsten UI-Bereiche erreichbar sind.

---

## Voraussetzungen

- Repo ist lokal vorhanden
- Python-Umgebung ist eingerichtet
- Dependencies aus `requirements.txt` sind installiert

Wenn das noch nicht passiert ist:
- zuerst [`../guides/QUICKSTART.md`](../guides/QUICKSTART.md)

---

## Schritt 1 – ins Repo gehen und Venv aktivieren

```bash
cd WhispersoftheSevenKingdoms
source .venv/bin/activate
```

---

## Schritt 2 – Dashboard starten

```bash
uvicorn services.sync.app.main:app --reload --host 0.0.0.0 --port 8000
```

Wenn alles sauber ist, läuft jetzt ein lokaler Entwicklungsserver.

---

## Schritt 3 – Browser öffnen

Öffne:
- `http://127.0.0.1:8000`

Je nach aktuellem Stand kannst du dort unter anderem sehen:
- Overview / Dashboard
- Pipeline / Create
- Audio Generator
- weitere Operations-/Systemseiten

---

## Schritt 4 – kurz Plausibilität prüfen

Ein sinnvoller Smoke-Test ist:
- lädt die Seite überhaupt?
- wirken Navigation und Layout plausibel?
- gibt es offensichtliche Template-/Importfehler?
- sind Statusbereiche sichtbar?

Du musst hier noch keinen kompletten Produktionslauf fahren. Es geht erst mal darum, dass die Control Plane lokal lebt.

---

## Häufige Probleme

### ImportError / Module not found
Dann fehlen Python-Abhängigkeiten oder du startest nicht aus dem Repo-Root.

### Port schon belegt
Dann einen anderen Port wählen, z. B. `--port 8001`.

### Template-/Static-Fehler
Dann prüfen, ob du wirklich aus dem Repository-Root startest und die Pfade stimmen.

---

## Nächste Schritte

Wenn das Dashboard läuft, sind die nächsten sinnvollen Tutorials:
- [`first-local-pipeline-run.md`](first-local-pipeline-run.md)
- später ein kompletter Flow von Eingabe bis Preview/Output

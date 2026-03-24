# Docs Audit – Diátaxis Migration

Stand: 2026-03-24
Status: working document

## Ziel
Diese Datei ordnet die vorhandene Dokumentation dem Diátaxis-Framework zu und markiert Altlasten, Dubletten und konkrete Migrationsschritte.

## Einordnung der aktuellen Dateien

| Pfad | Aktuelle Rolle | Zielkategorie | Status | Problem / Aktion |
|---|---|---|---|---|
| `README.md` | Repo-Einstieg | Einstieg + Querverweise | teilw. aktuell | weiter mit Docs verlinken |
| `PROJECT_STATUS.md` | Betriebswahrheit | outside docs / status source | aktuell | als Truth-Source behalten |
| `ROADMAP.md` | Planung | outside docs / planning source | aktuell | als Roadmap behalten |
| `docs/README.md` | Docs-Einstieg | docs landing page | brauchbar | weiter ausbauen |
| `docs/DIATAXIS_MIGRATION_PLAN.md` | Migrationsplan | explanation/meta | brauchbar | später mit Audit synchron halten |
| `docs/guides/QUICKSTART.md` | How-to | guide | veraltet | auf Monorepo/Pipeline aktualisieren |
| `docs/guides/PIPELINE.md` | How-to/Explanation gemischt | guide + explanation splitten | veraltet | neu schreiben |
| `docs/guides/AUTOMATION.md` | How-to/strategy | guide | prüfen | Pfade + Scope prüfen |
| `docs/guides/AGENT_SYNC.md` | How-to | guide | vermutlich okay | auf aktuelle Pfade prüfen |
| `docs/guides/BRANCHING.md` | Team-Guide | guide | vermutlich okay | Links prüfen |
| `docs/guides/CONTRIBUTING.md` | Team-Guide | guide | vermutlich okay | Links prüfen |
| `docs/technical/repo-structure.md` | Reference | reference | veraltet | an reale Struktur anpassen |
| `docs/technical/metadata.md` | Reference | reference | prüfen | Pfade/Schema prüfen |
| `docs/technical/preflight.md` | Reference | reference | prüfen | aktuelle Skripte prüfen |
| `docs/technical/upload-completeness.md` | Reference | reference | prüfen | aktuelle Pipeline prüfen |
| `docs/technical/validation.md` | Reference | reference | prüfen | aktuelle Skripte prüfen |
| `docs/templates/*` | Reference assets | reference | okay-ish | in docs/reference einhängen |
| `docs/publishing/*` | Reference/Explanation gemischt | mostly reference | prüfen | sauberer indexen |
| `docs/architecture/TECH_DECISIONS.md` | Rationale | explanation | okay | stärker verlinken |
| `docs/architecture/EXPANSION_PLAN_FINAL.md` | Rationale/vision | explanation | okay | stärker verlinken |
| `docs/AUDIO_GENERATION_ALTERNATIVES_EVALUATION.md` | Analyse | explanation | okay | später bündeln |
| `docs/AUDIO_GENERATION_ALTERNATIVES_FEEDBACK.md` | Review | explanation appendix | doppelt nah | mit Audio-Decision-Doc bündeln |
| `docs/AUDIO_GENERATION_ALTERNATIVES_SMITH_FEEDBACK.md` | Review | explanation appendix | doppelt nah | mit Audio-Decision-Doc bündeln |
| `docs/AUDIO_GENERATION_FEEDBACK_SMITH.md` | Review | explanation appendix | pot. Dublette | Inhalt prüfen/zusammenführen |

## Hauptprobleme

1. **Tutorials fehlen fast komplett**
   - Es gibt Guides, aber kaum Lernpfade von null bis Erfolg.

2. **Mehrere Docs referenzieren alte Pfade**
   - Beispiele: `scripts/`, `publishing/musicgen/`, `input/`, `output/` als Hauptstruktur.
   - Real ist inzwischen stark von `pipeline/`, `services/sync/`, `musicgen/`, `data/` geprägt.

3. **Guide vs. Explanation ist oft vermischt**
   - Besonders in `PIPELINE.md`.

4. **Audio-Entscheidungsdokumente sind redundant**
   - Mehrere Feedback-/Evaluationsdateien ohne klare Hierarchie.

## Zielstruktur

```text
docs/
  README.md
  DOCS_AUDIT.md
  tutorials/
  guides/
  reference/
  explanation/
```

Hinweis: Bestehende Unterordner wie `technical/`, `publishing/`, `templates/`, `architecture/` bleiben zunächst bestehen,
bis ihre Inhalte sauber migriert oder neu indexiert wurden.

## Priorisierte Arbeitspakete

### P0 – Jetzt
- [x] Audit-Datei anlegen
- [x] `docs/tutorials/` anlegen
- [x] `docs/reference/` anlegen
- [ ] `docs/README.md` auf echtes Navigationszentrum ausbauen
- [ ] Tutorial-Roadmap sichtbar machen

### P1 – Als Nächstes
- [ ] `docs/guides/QUICKSTART.md` auf aktuellen Stand bringen
- [ ] `docs/guides/PIPELINE.md` neu schreiben
- [ ] `docs/technical/repo-structure.md` korrigieren
- [ ] erstes Tutorial schreiben

### P2 – Danach
- [ ] Audio-Dokumente zusammenführen
- [ ] Explanation-Bereich klar indexieren
- [ ] Root-README stärker mit `docs/` verzahnen
- [ ] tote Links / alte Pfade bereinigen

## Was Jarvis parallel machen kann

Sinnvolle Nebenarbeiten für Jarvis, ohne Implementierungswissen zu erfinden:

1. **Dokumente klassifizieren**
   - jede Datei einer Diátaxis-Kategorie zuordnen
   - veraltete Links/Pfade sammeln

2. **Docs-Navigation verbessern**
   - `docs/README.md` pflegen
   - Bereichsindizes für explanation/reference vorbereiten

3. **Dublettenanalyse Audio-Dokus**
   - Unterschiede zwischen den Audio-Feedback-Dateien dokumentieren
   - Merge-Vorschlag schreiben, aber nicht raten

4. **Link- und Strukturhygiene**
   - Crosslinks ergänzen
   - Inkonsistenzen markieren

Nicht an Jarvis auslagern, solange technisch instabil:
- GPU-Worker-Setup-How-to
- lokale Audio-Provider-How-tos mit konkreten Befehlen
- alles, was reale Implementierungsdetails erfinden würde

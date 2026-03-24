# Documentation Index

Die Doku wird auf das **Diátaxis-Framework** umgebaut, damit man nicht erst Archäologie studieren muss, um etwas zu finden.

## Start hier

- **Projektstatus / operative Wahrheit**: [`../PROJECT_STATUS.md`](../PROJECT_STATUS.md)
- **Roadmap / nächste Prioritäten**: [`../ROADMAP.md`](../ROADMAP.md)
- **Repository-Überblick**: [`../README.md`](../README.md)
- **Changelog**: [`../CHANGELOG.md`](../CHANGELOG.md)
- **Doku-Audit / Migrationsstand**: [`DOCS_AUDIT.md`](DOCS_AUDIT.md)

---

## Diátaxis-Navigation

### Tutorials
Lernpfade von null bis zu einem funktionierenden Ergebnis.

- [`tutorials/README.md`](tutorials/README.md)
- _geplant_: Erstes Video lokal erzeugen
- _geplant_: Dashboard lokal starten und benutzen
- _geplant_: Vom Song zum Publish-Artefakt

### How-to Guides
Aufgabenorientierte Anleitungen für ein konkretes Ziel.

- [`guides/QUICKSTART.md`](guides/QUICKSTART.md) ⚠️ aktuell noch veraltet
- [`guides/PIPELINE.md`](guides/PIPELINE.md) ⚠️ aktuell noch veraltet / gemischt
- [`guides/AUTOMATION.md`](guides/AUTOMATION.md)
- [`guides/AGENT_SYNC.md`](guides/AGENT_SYNC.md)
- [`guides/BRANCHING.md`](guides/BRANCHING.md)
- [`guides/CONTRIBUTING.md`](guides/CONTRIBUTING.md)

### Agent Operations
Arbeitsregeln und Betriebswissen für Agenten, die im Projekt aktiv Änderungen machen.

- [`agents/README.md`](agents/README.md)
- [`agents/WORKING_IN_THIS_PROJECT.md`](agents/WORKING_IN_THIS_PROJECT.md)
- [`agents/GITHUB_AND_PAT.md`](agents/GITHUB_AND_PAT.md)
- [`agents/SYNC_SERVICE.md`](agents/SYNC_SERVICE.md)
- [`agents/PLAYBOOKS.md`](agents/PLAYBOOKS.md)

### Reference
Lookup-Material: technische Fakten, Formate, Konventionen, Templates.

- [`reference/README.md`](reference/README.md)
- [`reference/architecture-diagram.md`](reference/architecture-diagram.md)
- [`technical/repo-structure.md`](technical/repo-structure.md) ⚠️ veraltet
- [`technical/metadata.md`](technical/metadata.md)
- [`technical/validation.md`](technical/validation.md)
- [`technical/preflight.md`](technical/preflight.md)
- [`technical/upload-completeness.md`](technical/upload-completeness.md)
- [`templates/`](templates/)
- [`publishing/`](publishing/)

### Explanation
Warum Dinge so gebaut sind, welche Tradeoffs gelten, welche Strategie verfolgt wird.

- [`explanation/README.md`](explanation/README.md)
- [`explanation/architecture-overview.md`](explanation/architecture-overview.md)
- [`explanation/audio-strategy.md`](explanation/audio-strategy.md)
- [`architecture/TECH_DECISIONS.md`](architecture/TECH_DECISIONS.md)
- [`architecture/EXPANSION_PLAN_FINAL.md`](architecture/EXPANSION_PLAN_FINAL.md)
- [`AUDIO_GENERATION_ALTERNATIVES_EVALUATION.md`](AUDIO_GENERATION_ALTERNATIVES_EVALUATION.md)

---

## Aktuelle Probleme

Die größten Baustellen gerade:

1. **fehlende echte Tutorials**
2. **veraltete Pfade in QUICKSTART / PIPELINE / repo-structure**
3. **gemischte Doku-Typen**
4. **Audio-Dubletten im Explanation-Bereich**

---

## Nächste konkrete Schritte

1. `QUICKSTART.md` modernisieren
2. `PIPELINE.md` neu schreiben
3. erstes Tutorial anlegen
4. `repo-structure.md` auf reale Monorepo-Struktur ziehen
5. Audio-Entscheidungsdocs zusammenführen

---

## Arbeitsaufteilung

### Pako
- technische Guides mit echtem Implementierungsbezug
- Pipeline-, Dashboard- und Struktur-Doku
- Tutorials, die reale Workflows zeigen

### Jarvis
- Doku-Mapping
- Navigation / Crosslinks
- Dublettenanalyse
- Strukturhygiene und Linkpflege

### Smith
- Infra-, DB-, Deployment- und Backend-nahe Explanation/Reference

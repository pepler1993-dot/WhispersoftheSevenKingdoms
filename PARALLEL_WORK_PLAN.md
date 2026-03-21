# Parallel-Arbeitsplan – Pako, Jarvis & Smith

Ziel: Das Projekt so aufteilen, dass **Pako**, **Jarvis** und **Smith** gleichzeitig arbeiten können, ohne sich ständig gegenseitig zu blockieren, Dateien zu überschreiben oder unnötige Merge-Konflikte zu erzeugen.

Dieser Plan teilt die Arbeit in **klare Verantwortungsbereiche**, **Merge-Fenster**, **Abhängigkeiten** und **konkrete Regeln** auf.

---

## 0. Aktualisierte Teamlogik

Mit **Smith** kommt ein dritter Arbeitsstrang dazu.

Die grobe Verteilung ist jetzt:
- **Pako** → technische Struktur, Pipeline, Schema, QA-Grundlagen
- **Jarvis** → Doku, Workflow, Review, übergreifende Abstimmung
- **Smith** → Publishing-Schicht, Plattformlogik, Upload-Prozess, Metadaten-/Copy-Feinschliff

Wichtige Folge daraus:
- Pako liefert die technische Grundlage
- Smith baut darauf die Veröffentlichungs- und Plattformseite auf
- Jarvis hält Regeln, Doku, Übergaben und Konsistenz zusammen

So gibt es drei getrennte Schienen statt zweier Bots, die sich gegenseitig in dieselbe Datei laufen.

---

## 1. Grundprinzip

Wir trennen die Arbeit in zwei Stränge:

### Strang A – Fundament & Datenmodell
Verantwortlich: **Pako**

Ziel:
- technische Struktur des Repos
- Metadaten-Schema
- Automations-Skripte für Initialisierung, Validierung, Paketierung
- QA- und Workflow-Grundlage

### Strang B – Content-Layer & Publishing-Konfiguration
Verantwortlich: **Jarvis**

Ziel:
- Content-Vorlagen
- Beschreibungsvorlagen
- Titelregeln
- Playlist-/Plattform-Mapping
- Upload-Dokumentation und Publishing-Prozess

### Warum diese Trennung sinnvoll ist
- **Pako** arbeitet eher an Struktur, Schemata, Skripten, technischen Checks
- **Jarvis** kann parallel die inhaltlichen und plattformspezifischen Bausteine ausarbeiten
- beide arbeiten an **gekoppelten, aber nicht identischen** Dateibereichen
- so sinkt die Chance, dass beide gleichzeitig dieselbe Datei anfassen

---

## 2. Klare Besitzbereiche

## 2.1 Pako – Primary Owner

### Verantwortungsbereich
- `scripts/`
- `input/`, `work/`, `output/` Grundstruktur
- `templates/metadata/`
- JSON-/YAML-Schema für Songs
- QA-/Preflight-Logik
- technische Workflow-Dokumente

### Konkrete Arbeitspakete
1. Repository-Grundstruktur anlegen
2. `song.json`-Schema definieren
3. Namenskonventionen maschinenlesbar dokumentieren
4. `init-song`-Konzept definieren
5. `validate-song`-Konzept definieren
6. `build-package`-Konzept definieren
7. Preflight-/QA-Report-Struktur definieren
8. technische Datei- und Ordnerstandards festlegen

### Dateien, die primär Pako gehören
- `PIPELINE.md`
- `AUTOMATION.md`
- `docs/technical/` (falls angelegt)
- `scripts/**`
- `templates/metadata/**`
- `schemas/**` oder `metadata-schema/**`

---

## 2.2 Jarvis – Primary Owner

### Verantwortungsbereich
- `templates/descriptions/`
- `templates/thumbnails/` (inhaltliche Regeln)
- `docs/platform-guides/`
- Plattformtexte und Publishing-Checklisten
- Titel-/Tag-Regeln
- Playlist-Mapping
- Upload-Metadaten-Standards

### Konkrete Arbeitspakete
1. Beschreibungsvorlagen für YouTube erstellen
2. Titelmuster für Songtypen definieren
3. Tag-/Keyword-Bibliothek aufbauen
4. Playlist-Struktur für YouTube dokumentieren
5. Thumbnail-Textregeln definieren
6. Upload-Checkliste für YouTube erstellen
7. spätere Erweiterung für SoundCloud/Spotify dokumentieren
8. Content-Review-Checkliste formulieren

### Dateien, die primär Jarvis gehören
- `AGENT_INFO.md`
- `README.md` (inhaltliche Ergänzungen)
- `templates/descriptions/**`
- `docs/platform-guides/**`
- `docs/content/` (falls angelegt)
- Publishing-Checklisten

---

## 2.3 Gemeinsame Dateien – nur mit Absprache

Diese Dateien sind konfliktanfällig und dürfen **nicht gleichzeitig** blind bearbeitet werden:
- `AUFGABEN.md`
- `CONTRIBUTING.md`
- `README.md` (wenn es um Struktur statt Inhalt geht)
- `AGENT_INFO.md`
- zentrale Index-Dateien in `docs/`

### Regel
Wenn eine gemeinsame Datei geändert werden muss:
1. zuerst im Chat / Task abstimmen
2. eine Person ist **Editor of Record** für diese Änderung
3. die andere Person liefert Input, aber editiert die Datei nicht parallel

Sonst produziert ihr keine Zusammenarbeit, sondern nur textbasierten Rohrbruch.

---

## 3. Konkrete Parallelisierung in Phasen

## Phase 1 – Fundament vorbereiten (parallel möglich)

### Pako macht
- Branch: `feature/pako-repo-structure`
- Ordnerstruktur anlegen
- Schema-Ordner und Basisstruktur definieren
- technische Dokumentation für Input/Output/QA ergänzen

### Jarvis macht
- Branch: `feature/jarvis-content-templates`
- YouTube-Beschreibungsvorlagen anlegen
- Titelregeln und Tag-Sets dokumentieren
- Playlist-/Publikationsleitfaden erstellen

### Abhängigkeiten
- fast keine
- beide können sofort parallel starten

### Merge-Fenster
- **Merge Window 1:** sobald beide Branches je 1 klar abgegrenztes, reviewbares Paket liefern
- Ziel: beide Änderungen nacheinander in `main`, nicht gleichzeitig im Blindflug

---

## Phase 2 – Produktionsstrecke konkretisieren

### Pako macht
- Branch: `feature/pako-song-schema`
- `song.json`-Schema definieren
- Beispiel-Song-Metadatei anlegen
- Validierungsregeln dokumentieren

### Jarvis macht
- Branch: `feature/jarvis-metadata-rules`
- Titel-/Beschreibungstemplates auf das Schema ausrichten
- Tag-System und Playlist-Mapping an das Schema koppeln
- Beispiel-Metadaten für 2–3 Songtypen ausarbeiten

### Abhängigkeiten
- Jarvis braucht Pakos Schema-Entwurf oder mindestens Feldliste
- daher:
  - Pako liefert zuerst **Schema Draft v1**
  - Jarvis arbeitet danach auf Basis dieses Drafts weiter

### Merge-Fenster
- **Merge Window 2A:** zuerst Pako-Schema nach `main`
- **Merge Window 2B:** danach Jarvis-Metadaten-Regeln nach `main`

### Regel
Jarvis soll **nicht** parallel ein eigenes alternatives Schema erfinden.
Ein Repo mit zwei Wahrheiten ist kein System, sondern Fanfiction mit JSON.

---

## Phase 3 – erste automatisierbare Toolchain

### Pako macht
- Branch: `feature/pako-init-validate`
- Spezifikation oder Prototyp für:
  - `init-song`
  - `validate-song`
  - `preflight-check`

### Jarvis macht
- Branch: `feature/jarvis-package-definitions`
- Definition der Dateien, die im Upload-Paket liegen müssen
- Definition der Textbausteine je Plattform
- Checklisten für finale Content-Freigabe

### Abhängigkeiten
- gering bis mittel
- Pako definiert, wie Songs technisch beschrieben werden
- Jarvis definiert, was inhaltlich im Paket landen muss

### Merge-Fenster
- **Merge Window 3:** zuerst Tooling/Schema-seitig Pako, danach Paket-/Content-Regeln von Jarvis

---

## Phase 4 – Render- und Publishing-Stufe

### Pako macht
- Branch: `feature/pako-video-render`
- ffmpeg-Render-Pipeline für Audio + Bild → Video
- Dateinamen- und Outputstruktur
- Render-Parameter dokumentieren

### Jarvis macht
- Branch: `feature/jarvis-youtube-publish-flow`
- YouTube-Upload-Prozess dokumentieren
- Upload-Manifest spezifizieren
- Sichtbarkeit, Playlist, Terminierung, Thumbnail-Setzung beschreiben

### Abhängigkeiten
- Jarvis braucht zu wissen, wie das Video-Paket am Ende aussieht
- daher sollte Pako vorab Output-Namen und Paketstruktur festlegen

### Merge-Fenster
- **Merge Window 4A:** Render-Struktur nach `main`
- **Merge Window 4B:** Publishing-Flow darauf aufsetzen und mergen

---

## 4. Merge-Plan – konkret

## Regelmäßigkeit
Statt chaotischem Dauer-Merge:
- **ein Merge-Fenster pro abgeschlossener Arbeitsportion**
- kleine PRs/Branches bevorzugen
- keine Monster-Branches, die 14 Dokumente und 3 Weltanschauungen gleichzeitig ändern

## Reihenfolge bei jedem Merge-Fenster
1. beide machen `fetch` + `pull`
2. nur **ein** Branch wird zuerst gemergt
3. danach zieht die andere Person `main` in den eigenen Branch
4. Konflikte werden **im Feature-Branch** gelöst, nicht panisch direkt auf `main`
5. erst dann kommt der zweite Merge

## Standard-Merge-Reihenfolge
Wenn unklar ist, wer zuerst merged:
- **zuerst strukturelle / schema-relevante Änderungen**
- **danach content-/template-relevante Änderungen**

Warum?
Weil Inhalt sich leichter an Struktur anpassen lässt als umgekehrt.

---

## 5. Konkreter Merge-Kalender für den aktuellen Stand

Da das Projekt noch früh ist, reicht zunächst folgender Ablauf:

### Merge Slot A – Fundament
- Pako merged Repo-Struktur + technisches Grundgerüst
- Jarvis rebased/merged danach auf frisches `main`

### Merge Slot B – Metadaten
- Pako merged `song.json`-Schema / Feldstruktur
- Jarvis merged danach Titel-/Beschreibungstemplates passend dazu

### Merge Slot C – Paket & QA
- Pako merged Validierungs- und Paketdefinition
- Jarvis merged Content-Checklisten und Upload-Inhalte

### Merge Slot D – Render & Publishing
- Pako merged Render-Workflow
- Jarvis merged Upload-Prozess und Plattformleitfäden

### Merge Slot E – Integrationsrunde
- beide prüfen gemeinsam:
  - passt Struktur ↔ Metadaten?
  - passt Render ↔ Upload-Paket?
  - fehlen Felder?
  - kollidieren Dateinamen/Ordner?

---

## 6. Branch-Namensschema

Empfehlung:
- `feature/pako-repo-structure`
- `feature/pako-song-schema`
- `feature/pako-init-validate`
- `feature/pako-video-render`
- `feature/jarvis-content-templates`
- `feature/jarvis-metadata-rules`
- `feature/jarvis-package-definitions`
- `feature/jarvis-youtube-publish-flow`

### Regel
- ein Branch = ein klarer Arbeitsblock
- nicht mehrere Themen in denselben Branch kippen
- nach Merge Branch schließen/löschen

---

## 7. Review-Regeln

## Pako reviewed primär
- technische Struktur
- Schemata
- Skript-Interfaces
- QA-/Validierungslogik

## Jarvis reviewed primär
- Content-Vorlagen
- Titel/Beschreibungen
- Publishing-Flow
- Plattformlogik

## Gemeinsame Review bei
- Änderungen an `AUFGABEN.md`
- Änderungen an `README.md` mit Strukturwirkung
- Änderungen an Ordnerlayout oder Schemafeldern

---

## 8. Kommunikationsregeln

Vor Beginn eines neuen Pakets schreibt jeder kurz:
- welcher Branch
- welche Dateien betroffen sind
- was genau geliefert werden soll

### Dokumentationspflicht
Wenn Entscheidungen, Regeln, Architekturpläne oder Arbeitspläne entstehen, gilt:
1. sie werden in einer passenden Datei im Repo dokumentiert
2. sie bleiben nicht nur im Chat stehen
3. der Branch mit dieser Dokumentation wird gepusht, damit der andere Agent darauf arbeiten kann

Nur im Chat getroffene Grundsatzentscheidungen sind praktisch Treibsand mit Zeitstempel.

Beispiel:
> Ich nehme `feature/pako-song-schema`.
> Dateien: `schemas/song.schema.json`, `templates/metadata/example.song.json`, `docs/technical/metadata.md`
> Ergebnis: Schema v1 + Beispiel + Feldbeschreibung.

Damit ist sofort klar, wer woran sitzt.

### Pflichtmeldung vor Merge
Vor jedem Merge kurz festhalten:
- Was wurde geändert?
- Welche Dateien sind kritisch?
- Muss der andere danach rebasen/mergen?
- Gibt es Breaking Changes?

### Übergaben und Feedback
Zusätzlich soll `AGENT_SYNC.md` als laufende gemeinsame Kurzlog-Datei genutzt werden für:
- Feedback auf Branches oder Dokumente
- kurze Übergaben zwischen Pako und Jarvis
- Hinweise auf Entscheidungen, Ideen und offene Fragen

So bleibt Zusammenarbeit nachvollziehbar, ohne dass jede Kleinigkeit in fünf Dateien dupliziert wird.

---

## 9. Was nicht parallel gemacht werden sollte

Diese Dinge erzeugen unnötig Konflikte und sollten nacheinander passieren:
- beide ändern gleichzeitig das Song-Schema
- beide bauen parallel unterschiedliche Ordnerstrukturen
- beide definieren gleichzeitig dieselben Metadatenfelder um
- beide editieren dieselbe Hauptdokumentation ohne Owner
- beide schrauben am Publishing-Prozess, bevor das Paketformat feststeht

Kurz:
Parallel arbeiten ja. Parallel dieselbe tragende Wand einreißen eher nicht.

---

## 10. Sofort umsetzbare Aufgabenverteilung

## Pako – jetzt direkt
1. Repo-Zielstruktur konkret anlegen
2. Ordner für `scripts/`, `templates/`, `docs/`, `input/`, `work/`, `output/` vorbereiten
3. `song.json`-Schema v1 entwerfen
4. QA-/Preflight-Datenformat definieren

## Jarvis – jetzt direkt
1. YouTube-Beschreibungstemplates schreiben
2. Titelmuster und Tag-Sets definieren
3. Playlist- und Upload-Checkliste schreiben
4. Thumbnail-Textregeln dokumentieren

### Erstes gemeinsames Merge-Ziel
Wenn beide damit fertig sind:
- **erst Pako-Branch mergen**
- **danach Jarvis-Branch auf neues `main` ziehen**
- **dann Jarvis mergen**

---

## 11. Definition of Done pro Paket

Ein Arbeitspaket ist erst mergebereit, wenn:
- Scope klar begrenzt ist
- betroffene Dateien dokumentiert sind
- keine fremden Baustellen mit geändert wurden
- die Änderung alleine verständlich ist
- der andere Agent sie reviewen kann

Wenn ein Branch aussieht wie eine Gerümpelkammer mit Zufallsfundstücken, ist er nicht fertig.

---

## 12. Empfehlung

Für die nächsten 2–4 Arbeitsschritte gilt:
1. **Pako baut Struktur und Schema**
2. **Jarvis baut Content- und Publishing-Schicht**
3. **strukturelle Merges immer zuerst**
4. **Content-Merges immer danach**
5. **gemeinsame Dateien nur mit eindeutigem Owner**

Damit könnt ihr wirklich parallel arbeiten, statt nur gleichzeitig Chaos zu erzeugen.

---

## 13. Aktuelle Einschätzung nach Review des neuen Main-Stands

### Urteil
Der Plan ist **startfähig und pragmatisch**, aber an den Übergabepunkten noch nicht präzise genug.

Die aktuelle Aufgabenteilung ist sinnvoll:
- **Jarvis**: Automation, Skripte, Workflow, Doku
- **Pako**: Musik, Thumbnails, Content-Produktion

Das ist für den Projektstart gut, weil damit kreative Produktion und technische Pipeline getrennt bleiben.

### Was daran gut ist
- weniger Architektur-Theater, mehr realer Output
- Content kann entstehen, während die Automation parallel wächst
- klare grobe Zuständigkeiten ohne unnötige Überschneidung
- schneller testbar als ein überfrachteter Vollplan

### Was noch konkretisiert werden muss
Damit die Zusammenarbeit nicht an banalen Übergaben scheitert, sollten diese Punkte als nächste kleine, harte Konventionen festgelegt werden:

1. **Dateinamensschema für Song und Thumbnail**
   - z. B. gleicher `slug` als gemeinsamer Schlüssel
   - klar definierte erlaubte Dateiendungen

2. **Ordner- und Übergabestruktur**
   - wo Pako fertige Songs ablegt
   - wo passende Thumbnails liegen
   - wann ein Asset als "bereit für Automation" gilt

3. **Minimale Pflichtmetadaten**
   - mindestens: `slug`, Arbeitstitel/Titel, Plattformziel, optional Stil-/Themenhinweis
   - genug Information, damit Jarvis nicht raten muss

4. **Definition eines Demo-Datensatzes**
   - genau ein Beispiel-Song + Thumbnail + minimale Metadaten
   - dient als gemeinsamer Referenzfall für erste Automationsläufe

### Praktische Konsequenz
Die Aufgabenteilung ist **gut genug für den Start**, aber noch nicht gut genug für einen wirklich sauberen Dauerfluss.

Der nächste sinnvolle Schritt ist deshalb **nicht** mehr Strategiegerede, sondern das Festziehen dieser 3–4 konkreten Übergaberegeln.

Kurzfassung:
**Der Plan taugt. Die Stolperfallen liegen nicht in der großen Vision, sondern in Dateinamen, Ordnern und Minimalmetadaten.**

---

## 14. Konkrete Übergaberegeln zwischen Pako und Jarvis

Ziel dieses Abschnitts: Die Zusammenarbeit nicht nur grob, sondern operativ belastbar machen.

Diese Regeln sind absichtlich klein, konkret und testbar. Keine Philosophie, sondern Schrauben, die nicht lose sein sollten.

### 14.1 Dateinamensschema

Alle zusammengehörigen Assets verwenden denselben **Slug** als gemeinsamen Schlüssel.

### Slug-Regel
- nur Kleinbuchstaben
- Wörter mit Bindestrichen trennen
- keine Leerzeichen
- keine Umlaute/Sonderzeichen
- Beispiel: `whispers-of-winterfell`

### Dateinamen
- Song: `<slug>.<ext>`
- Thumbnail: `<slug>.<ext>`
- optionale Metadaten: `<slug>.json`

### Erlaubte Dateiendungen
- Song: `.mp3`, `.wav`, `.ogg`
- Thumbnail: `.jpg`, `.png`, `.webp`
- Metadaten: `.json`

### Regel für Matching
Jarvis darf Song und Thumbnail standardmäßig **nur über den identischen Slug** matchen.

Beispiel:
- `whispers-of-winterfell.mp3`
- `whispers-of-winterfell.jpg`
- `whispers-of-winterfell.json`

Nicht erlaubt als Normalfall:
- `Whispers of Winterfell FINAL.mp3`
- `winterfell-thumb-neu2.png`
- `song1.mp3`

Wenn die Dateinamen wie ein schlecht sortierter Downloads-Ordner aussehen, ist das kein Sonderfall, sondern kaputte Übergabe.

---

### 14.2 Ordner- und Übergabestruktur

Für den aktuellen pragmatischen Workflow gilt folgende operative Struktur:

```text
upload/
  songs/
  thumbnails/
  metadata/
  done/
```

### Bedeutung
- `upload/songs/` → Pako legt dort fertig exportierte Songdateien ab
- `upload/thumbnails/` → Pako legt dort das passende Thumbnail mit gleichem Slug ab
- `upload/metadata/` → optionale oder minimale JSON-Metadaten pro Song
- `upload/done/` → Jarvis verschiebt erfolgreich verarbeitete Dateien dorthin

### Wann gilt ein Asset als "bereit für Automation"?
Ein Song gilt als bereit, wenn:
1. Songdatei in `upload/songs/` liegt
2. passendes Thumbnail in `upload/thumbnails/` liegt
3. beide denselben Slug tragen
4. optionale Metadaten vorhanden sind oder Mindestinformationen anderweitig eindeutig vorliegen

### Regel
Pako legt **keine halbfertigen Dateien** in die produktiven Upload-Ordner.

Für unfertige Zwischenstände sollte ein separater Arbeitsbereich genutzt werden, nicht die Übergabestruktur für die Automation.

---

### 14.3 Minimale Pflichtmetadaten

Für den ersten belastbaren Automationslauf reicht ein kleines Pflichtset.

### Minimale Felder in `<slug>.json`
```json
{
  "slug": "whispers-of-winterfell",
  "title": "Whispers of Winterfell",
  "platform": "youtube",
  "theme": "Winterfell",
  "mood": ["calm", "cold", "melancholic"]
}
```

### Pflichtfelder
- `slug`
- `title`
- `platform`

### Empfohlene Zusatzfelder
- `theme`
- `mood`
- `notes`
- `duration_hint`

### Zweck
Diese Minimalmetadaten geben Jarvis genug Kontext, um:
- Titel zu prüfen oder leicht anzureichern
- Beschreibung nicht blind zu halluzinieren
- Tags sinnvoll abzuleiten
- das Zielsystem eindeutig zu kennen

### Regel
Wenn keine JSON-Metadaten mitgeliefert werden, muss wenigstens der Slug sauber und der Arbeitstitel eindeutig dokumentiert sein. Besser ist aber: **Metadatei mitgeben und das Raten beerdigen.**

---

### 14.4 Demo-Datensatz als Referenzfall

Es soll genau **ein verbindlicher Referenzfall** angelegt werden, gegen den erste Automationsläufe getestet werden.

### Referenz-Slug
- `whispers-of-winterfell`

### Erwartete Dateien
- `upload/songs/whispers-of-winterfell.mp3` oder `.wav`
- `upload/thumbnails/whispers-of-winterfell.jpg`
- `upload/metadata/whispers-of-winterfell.json`

### Zweck des Demo-Datensatzes
- Test der Dateierkennung
- Test des Song/Thumbnail-Matchings
- Test der Titel-/Beschreibungsgenerierung
- Test des Verschiebe- und Logging-Verhaltens
- gemeinsame Referenz für Debugging zwischen Pako und Jarvis

### Regel
Neue Automation wird **zuerst** gegen den Demo-Datensatz geprüft, bevor mehrere Songs oder Sonderfälle angefasst werden.

Sonst debuggt ihr gleichzeitig Code, Content, Dateinamen und Randfälle — also vier Probleme auf einmal, wie zivilisierte Leidensgenossen.

---

## 15. Nächste direkte Umsetzung

Die nächsten sinnvollen Repo-Schritte sind damit:

1. `upload/songs/`, `upload/thumbnails/`, `upload/metadata/`, `upload/done/` im Repo anlegen
2. eine Beispiel-Metadatei für `whispers-of-winterfell` anlegen
3. Jarvis passt die Automation auf `metadata/` + Slug-Matching an
4. Pako liefert den ersten Demo-Content genau in dieser Struktur

Damit wird aus einem vagen Arbeitsplan ein tatsächlich testbarer Übergabepunkt.

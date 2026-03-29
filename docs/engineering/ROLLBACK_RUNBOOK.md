# Rollback Runbook

**Owner:** Jarvis  
**Reviewer:** Smith  
**Stand:** 2026-03-29  
**Welle:** B09

---

## Zweck

Dieses Runbook definiert ein pragmatisches Standardvorgehen, wenn ein Release oder Hotfix zurückgenommen werden muss.

Ziel ist nicht Perfektion, sondern kontrollierte Schadensbegrenzung:
- Ausfall minimieren
- Zustand stabilisieren
- unkoordinierte Panik-Aktionen vermeiden

---

## Wann Rollback prüfen?

Rollback ist ernsthaft zu prüfen, wenn nach einem Release mindestens eines davon zutrifft:

- Hauptpfad ist kaputt
- Dashboard startet nicht mehr oder ist unbenutzbar
- Create-/Audio-/Upload-Flow ist blockiert
- kritischer Fehler betrifft produktiven Betrieb
- Hotfix verschlimmert die Lage
- Ursache ist unklar und schnelle Reparatur ist riskanter als Rücksprung

---

## Grundsatz

**Rollback vor hektischem Weiterpatchen**, wenn:
- der Fehler live ist
- kein sicherer Mini-Fix innerhalb kurzer Zeit möglich ist
- der letzte stabile Stand bekannt ist

Wenn die Lage unklar ist, ist ein sauberer Rücksprung oft billiger als drei schlechte Notfallfixes hintereinander.

---

## Voraussetzungen

Vor einem sinnvollen Rollback sollte möglichst bekannt sein:
- welcher Release / Tag gerade aktiv ist
- welcher letzte stabile Stand bekannt ist
- ob Datenmigrationen oder irreversible Änderungen enthalten waren
- ob nur Code oder auch Runtime-/Secrets-/Config betroffen sind

---

## Rollback-Arten

## 1. Soft Rollback
Problem wird durch Konfigurationsänderung, Feature-Deaktivierung oder Rücknahme eines kleinen Umschalters entschärft.

Geeignet wenn:
- kein kompletter Code-Rücksprung nötig ist
- Fehler klar isolierbar ist
- Risiko eines Voll-Rollbacks größer wäre

## 2. Code Rollback
Deploy auf einen früheren bekannten Commit oder Tag.

Geeignet wenn:
- aktueller Code klar fehlerhaft ist
- letzter stabiler Stand bekannt ist
- keine irreversiblen Migrationen dagegen sprechen

## 3. Teil-Rollback / Komponenten-Rollback
Nur ein Teilpfad wird zurückgenommen, z. B. Upload-Logik, UI-Teil oder Worker-bezogene Änderungen.

Geeignet wenn:
- Ursache klar eingegrenzt ist
- Systemgrenzen sauber genug sind
- Mischzustand beherrschbar bleibt

---

## Standard-Ablauf

## Schritt 1 – Incident kurz einordnen
Vor jeder Aktion kurz festhalten:
- Was ist kaputt?
- Seit wann?
- Welche Nutzer / Pfade sind betroffen?
- Ist es P0, P1 oder kleiner?
- Gibt es Datenrisiko oder nur Funktionsausfall?

## Schritt 2 – letzten stabilen Stand bestimmen
Bevor irgendetwas zurückgesetzt wird:
- letzten bekannten funktionierenden Tag/Commit identifizieren
- prüfen, ob seitdem Migrationen / irreversible Änderungen erfolgten
- prüfen, ob Secrets / Umgebungsvariablen / Runtime parallel geändert wurden

## Schritt 3 – Rollback-Entscheidung treffen
Entscheide explizit:
- Soft Rollback?
- kompletter Code-Rollback?
- Teil-Rollback?
- oder doch gezielter Hotfix?

## Schritt 4 – Änderung kontrolliert durchführen
Wichtig:
- keine parallelen Ad-hoc-Experimente auf Produktion
- nur ein verantwortlicher Operator führt den Rücksprung durch
- Änderungsschritt dokumentieren

## Schritt 5 – Verify
Nach Rollback mindestens prüfen:
- Dienst startet
- Hauptseiten laden
- Kernpfad funktioniert wieder
- keine offensichtlichen Folgefehler sichtbar

## Schritt 6 – Nacharbeit
Rollback beendet nur den Incident, nicht die Ursachenanalyse.
Danach:
- Ursache festhalten
- Follow-up-Issue anlegen
- Changelog / Incident-Notiz ergänzen
- Release-/Hotfix-Prozess ggf. verbessern

---

## Minimaler Verify-Check nach Rollback

- [ ] App erreichbar
- [ ] Login / Zugriff funktioniert
- [ ] betroffener Hauptpfad funktioniert wieder
- [ ] keine neuen Tracebacks / Crash-Symptome sichtbar
- [ ] Version / Stand nachvollziehbar

Bei Upload-Problemen zusätzlich:
- [ ] Upload-Auth / Token-Kontext plausibel
- [ ] Upload-Script startet wieder sauber

Bei Audio-/Pipeline-Problemen zusätzlich:
- [ ] Workflow startbar
- [ ] Worker-/Job-Status plausibel
- [ ] keine offensichtliche Queue-/Polling-Störung

---

## Was vor Rollback geprüft werden muss

### Datenmodell / Migration
Fragen:
- Gab es Schemaänderungen?
- Wurde Datenstruktur irreversibel geändert?
- Erwartet älterer Code eine frühere Struktur?

Wenn ja, ist ein einfacher Code-Rollback möglicherweise nicht ausreichend.

### Secrets / Config
Fragen:
- Wurden OAuth-Clients, Tokens oder ENV-Variablen geändert?
- Hängt der Fehler eher an Runtime-/Secret-Zustand als am Code?

Wenn ja, muss Konfiguration mitbetrachtet werden.

### Externe Abhängigkeiten
Fragen:
- Ist der Fehler intern oder durch YouTube / Google / GPU-Worker / Netzwerk verursacht?
- Würde Rollback überhaupt helfen?

Nicht jeder Incident ist ein Release-Problem.

---

## Rollback-Entscheidungsmatrix

| Situation | Empfohlene Reaktion |
|---|---|
| kleiner klarer Bug, Fix in Minuten sicher | Hotfix statt Rollback |
| Hauptpfad kaputt, Ursache unklar | Rollback bevorzugen |
| Runtime-/Secret-Problem ohne Codefehler | Konfigurationsfix statt Code-Rollback |
| Datenmigration irreversibel | kein Blind-Rollback, erst Analyse |
| UI kaputt, Backend stabil | Teil-Rollback oder gezielter Hotfix |
| Upload/Publish defekt nach Release | letzten stabilen Upload-Stand prüfen, ggf. Teil-Rollback |

---

## Verantwortlichkeit

Die release-verantwortliche Person koordiniert den Rollback.  
Laut aktuellem Projektstand ist das primär **Smith**, im Notfall **Jarvis**.

Wichtig ist:
- eine Person entscheidet
- Änderungen nicht parallel gegeneinander fahren
- Ergebnis sichtbar dokumentieren

---

## Dokumentationspflicht nach Rollback

Nach jedem echten Rollback sollte mindestens festgehalten werden:
- betroffener Release / Commit / Tag
- Grund für den Rollback
- Zielstand des Rücksprungs
- Ergebnis des Verify
- offenes Folgeproblem / neues Issue

---

## Nicht-Ziel

Dieses Runbook ersetzt keine host-spezifischen Shell-Befehle oder Deploy-Skripte.  
Es definiert den **operativen Denk- und Entscheidungsrahmen**, damit Rücksprünge kontrolliert und nachvollziehbar ablaufen.

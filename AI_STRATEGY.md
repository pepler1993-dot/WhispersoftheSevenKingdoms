# KI-Strategie – Whispers of the Seven Kingdoms

Ziel dieses Dokuments: festlegen, **wo KI im Projekt nötig, sinnvoll oder optional ist**, wenn die Songs **nicht manuell selbst erstellt** werden sollen.

---

## 1. Grundsatzentscheidung

### Status
Vorgeschlagen

### Entscheidung
Die Songs sollen **möglichst nicht manuell selbst komponiert/produziert** werden.

Daraus folgt:
- Für die **Song-Erzeugung** wird ein externer generativer Ansatz benötigt.
- Die Projektpipeline soll so gebaut werden, dass sie **KI-generierte Audio-Dateien** als Input verarbeiten kann.
- Die Kernpipeline darf **nicht von genau einem KI-Anbieter hart abhängig** sein.

### Konsequenz
Wir trennen sauber zwischen:
1. **Generierungsschicht** → KI-/Tool-abhängige Erstellung von Songs und optional Visuals
2. **Produktionsschicht** → strukturierte Verarbeitung, QA, Video-Render, Paketbau, Upload

So bleibt der Kern stabil, selbst wenn später das KI-Tool wechselt.

---

## 2. Wo KI konkret gebraucht wird

## 2.1 Song-Erzeugung
### KI-Bedarf
**Ja, praktisch notwendig**, wenn Songs nicht manuell erstellt werden.

### Aufgabe
- Musik / Soundscape / Einschlaf-Track generieren lassen
- ggf. unterschiedliche Längen / Varianten erzeugen
- Thema, Mood und Stil auf Westeros-/Fantasy-Schlafmusik ausrichten

### Anforderungen an die Generierung
- brauchbare Audioqualität
- reproduzierbarer Prompt-/Preset-Ansatz
- Export als brauchbare Audiodatei
- dokumentierbare Parameter pro Song

### Wichtige Regel
Das Repo sollte **nicht** von einem einzelnen Provider-Modell ausgehen, sondern ein neutrales Eingabeformat behalten:
- `generator`: Name des Tools/Anbieters
- `prompt`: verwendeter Prompt
- `style`: Stilparameter
- `duration_target`: Zieldauer
- `source_audio`: Pfad zur exportierten Datei

---

## 2.2 Visuals / Artwork
### KI-Bedarf
**Optional, aber sinnvoll**

Wenn pro Song neue Fantasy-/Ambient-Bilder gewünscht sind, ist KI hilfreich.
Wenn ein festes Template mit wiederverwendbaren Hintergründen reicht, ist KI nicht zwingend nötig.

### Empfehlung
- Start: Template-basierte Visuals
- später optional: KI-generierte Key-Art pro Song

---

## 2.3 Titel / Beschreibung / Tags
### KI-Bedarf
**Optional**

Diese Texte können auch regelbasiert über Templates gebaut werden.
KI ist eher ein Komfort- und Variationswerkzeug.

### Empfehlung
- Start mit Templates
- später optional KI für Varianten, aber nicht blind ohne Review

---

## 2.4 Upload / Publishing / QA
### KI-Bedarf
**Nein**

Diese Teile sollten klassisch und deterministisch bleiben.

---

## 3. Zielarchitektur

## Ebene A – KI-abhängige Generierung
Mögliche künftige Schritte:
- `generate-song`
- optional `generate-artwork`
- optional `suggest-copy`

## Ebene B – KI-unabhängige Kernpipeline
Soll immer funktionieren mit beliebigem Input-Audio:
- `validate-song`
- `render-video`
- `build-package`
- `preflight-check`
- `upload-youtube`

### Vorteil
Wenn ein Generator wechselt oder ausfällt, bricht nicht das ganze Projekt zusammen.

---

## 4. Technische Empfehlung

### Kurzfristig
- KI für **Song-Erzeugung** einplanen
- Kernpipeline trotzdem **tool-agnostisch** bauen
- generierte Songs wie normale Input-Dateien behandeln

### Mittelfristig
- Generator-Metadaten standardisieren
- Prompt-/Preset-Dokumentation je Song speichern
- Qualitätsprüfung zwischen Generator und Pipeline einziehen

### Langfristig
- mehrere Generatoren vergleichbar machen
- Provider austauschbar halten

---

## 5. Offene Punkte
- Welcher Musikgenerator wird zuerst getestet?
- Welche Audioqualität und Exportformate liefert er?
- Wie werden Prompt, Seed, Stilparameter und Version dokumentiert?
- Gibt es rechtliche / kommerzielle Einschränkungen bei der Nutzung?

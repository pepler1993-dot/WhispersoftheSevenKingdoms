# Task-Zusammenfassungen und Task-Detail im Dashboard

## Analyse

### Aktuelle Implementierung
1. **Taskliste** (`/admin/tasks`):
   - Zeigt `assignment_title` als lesbare Kurzbeschreibung
   - Status bleibt separat
   - Bearbeiter bleibt separat
   - Fallback auf "Issue von ... geöffnet" oder "arbeitet gerade daran" bei fehlender Beschreibung

2. **Task-Detailseite** (`/admin/tasks/{task_id}`):
   - Zeigt detaillierte Aufgabenbeschreibung aus `summary`
   - Fallback auf generische Beschreibungen wie "arbeitet gerade daran"

### Problem
- Fallback-Texte sind generisch und nicht hilfreich
- Keine Live-Filterung in der Taskliste
- Zusammenfassungen nutzen nicht den Issue-Titel als primäre Quelle

## Verbesserungsvorschläge

### 1. Taskliste
- Priorisiere Issue-Titel aus GitHub als `assignment_title`
- Zeige sinnvolle Fallbacks basierend auf letzten Events
- Implementiere Live-Filterung ohne extra Button

### 2. Task-Detailseite
- Zeige ausführliche Beschreibung aus Issue-Body
- Verdichte automatisch aus GitHub Events
- Biete sinnvolle Fallbacks bei fehlendem Issue-Text

### 3. Filter
- Status als Dropdown
- Agent/Bearbeiter als Dropdown
- Live-Filtering ohne extra Button

## Umsetzungsplan

### Schritte
1. Erweitere `_extract_issue_title` Funktion um Issue-Body zu extrahieren
2. Verbessere `_humanize_task_for_manager` für bessere Fallbacks
3. Aktualisiere Taskliste mit Live-Filterung
4. Verbessere Task-Detailseite mit ausführlicheren Beschreibungen
5. Implementiere Dropdown-Filter für Status und Agent
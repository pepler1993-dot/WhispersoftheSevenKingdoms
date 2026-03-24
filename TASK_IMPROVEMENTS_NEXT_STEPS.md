# Nächste Schritte für Task-Verbesserungen

## Offene Punkte

### 1. API-Endpunkt für Filterwerte
- Implementierung eines separaten API-Endpunkts zur Bereitstellung aller verfügbaren Filterwerte
- Dynamische Befüllung der Dropdown-Listen mit echten Daten

### 2. Verbesserte Fallback-Texte
- Überarbeitung der generischen Texte wie "arbeitet gerade daran"
- Nutzung von spezifischeren Informationen aus den Events

### 3. Serverseitiges Filtern für große Datenmengen
- Implementierung von serverseitigem Filtern für bessere Performance
- Pagination für sehr große Task-Listen

## Umsetzungsplan

### 1. API-Endpunkt für Filterwerte
- Erstellung eines neuen Endpunkts `/api/filters` in `main.py`
- Rückgabe aller verfügbaren Bearbeiter und Status
- Aktualisierung des JavaScript-Codes zur Nutzung dieses Endpunkts

### 2. Verbesserte Fallback-Texte
- Erweiterung der `_humanize_task_for_manager` Funktion
- Nutzung von spezifischeren Event-Informationen für bessere Beschreibungen
- Hinzufügung von Kontextinformationen aus den GitHub Events

### 3. Serverseitiges Filtern
- Erweiterung des bestehenden Filtermechanismus in `main.py`
- Implementierung von Pagination für große Datenmengen
- Verbesserung der Performance bei vielen Tasks

## Technische Umsetzung

### API-Endpunkt
```python
@app.get('/api/filters')
def get_filter_options():
    # Hole alle verfügbaren Bearbeiter und Status aus der Datenbank
    agents = db.get_unique_agents()
    phases = db.get_unique_phases()
    return {'agents': agents, 'phases': phases}
```

### Verbesserte Fallback-Texte
```python
def _humanize_task_for_manager(task: dict[str, Any], detail: dict[str, Any] | None = None) -> dict[str, Any]:
    # ... bestehende Implementierung ...
    
    # Verbesserte Fallbacks
    if summary == 'Noch keine verständliche Zusammenfassung vorhanden.':
        # Nutze spezifischere Informationen aus den Events
        if detail:
            github_events = detail.get('github_events') or []
            for event in github_events:
                if event.get('event_type') == 'issues' and event.get('action') == 'opened':
                    summary = f"Neues Issue: {event.get('payload_json', {}).get('issue', {}).get('title', 'Ohne Titel')}"
                    break
                elif event.get('event_type') == 'pull_request' and event.get('action') == 'opened':
                    summary = f"Neuer Pull Request von {event.get('sender', 'einem Contributor')}"
                    break
    
    return {
        # ... bestehende Rückgabe ...
    }
```

### Serverseitiges Filtern
- Erweiterung der bestehenden `list_tasks_for_admin` Funktion in `store.py`
- Hinzufügung von Pagination-Parametern
- Optimierung der Datenbankabfragen
# Config / Scope Modell

**Owner:** Smith  
**Stand:** 2026-03-29  
**Welle:** B04  
**Issue:** #140  
**Typ:** Architecture  
**Bereich:** Configuration

---

## Zweck

Dieses Dokument definiert, wie Konfiguration im System strukturiert, vererbt und
aufgelöst wird. Es ersetzt die heutige Situation, in der Defaults über
`house_templates.json`, UI-Formulare und verstreute Konstanten verteilt sind.

---

## Scope-Hierarchie

```
┌────────────────────────────────────────────────────┐
│  System                                             │
│  (globale Infrastruktur, alle Spaces)               │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Space                                        │   │
│  │  (projektspezifische Grundwerte)              │   │
│  │                                               │   │
│  │  ┌────────────────────────────────────────┐   │   │
│  │  │  Preset                                 │   │   │
│  │  │  (Haus-/Theme-Defaults)                 │   │   │
│  │  │                                         │   │   │
│  │  │  ┌──────────────────────────────────┐   │   │   │
│  │  │  │  Variant                          │   │   │   │
│  │  │  │  (Ort-/Varianten-Overrides)       │   │   │   │
│  │  │  │                                   │   │   │   │
│  │  │  │  ┌────────────────────────────┐   │   │   │   │
│  │  │  │  │  Workflow (Override)        │   │   │   │   │
│  │  │  │  │  (einmalige Anpassungen)   │   │   │   │   │
│  │  │  │  └────────────────────────────┘   │   │   │   │
│  │  │  └──────────────────────────────────┘   │   │   │
│  │  └────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

**Auflösungsrichtung:** Von innen nach außen. Der spezifischste Scope gewinnt.

---

## Settings pro Scope

### System-Scope
Infrastruktur und Provider-Konfiguration, die für alle Spaces gilt.

| Setting | Beispiel | Warum hier |
|---|---|---|
| `gpu_worker.host` | `192.168.178.152` | Hardware-Infrastruktur |
| `gpu_worker.ssh_key_path` | `/root/.ssh/gpu_worker` | Server-spezifisch |
| `gpu_worker.max_concurrent_jobs` | `2` | Hardware-Limit |
| `storage.backend` | `local` | Infrastruktur-Entscheidung |
| `storage.local.base_path` | `/data` | Server-spezifisch |
| `ffmpeg.binary_path` | `/usr/bin/ffmpeg` | System-Tool |
| `server.port` | `8000` | Infrastruktur |
| `feature_flags` | `{"shorts_enabled": true}` | Globale Feature-Steuerung |

### Space-Scope
Projektspezifische Grundwerte und externe Integrationen.

| Setting | Beispiel | Warum hier |
|---|---|---|
| `youtube.client_secret_path` | `./client_secret.json` | OAuth pro Projekt/Kanal |
| `youtube.default_privacy` | `unlisted` | Projekt-Policy |
| `youtube.default_category_id` | `10` (Music) | Projekt-Thema |
| `audio.default_sample_rate` | `44100` | Projekt-Standard |
| `audio.default_format` | `wav` | Projekt-Standard |
| `content.default_language` | `en` | Projekt-Sprache |

### Preset-Scope
Haus-/Theme-spezifische Defaults — entspricht heute `house_templates.json`.

| Setting | Beispiel | Warum hier |
|---|---|---|
| `audio.mood_profile` | `dark, ambient, ethereal` | Haus-Stimmung |
| `audio.default_duration_hours` | `3` | Haus-Standard |
| `audio.crossfade_seconds` | `10` | Audio-Engineering |
| `audio.post_process.eq_preset` | `ambient_warm` | Klangprofil |
| `thumbnail.style_brief` | `Dark fantasy, fire...` | Visueller Stil |
| `metadata.title_template` | `{house} - {variant} | {mood}` | Titelstruktur |
| `metadata.default_tags` | `["ambient", "fantasy"]` | SEO |

### Variant-Scope
Ort-/Varianten-spezifische Overrides — nur Abweichungen vom Preset.

| Setting | Beispiel | Warum hier |
|---|---|---|
| `audio.loop_duration_hours` | `1` (statt Preset-Default 3) | Varianten-spezifisch |
| `audio.variant_prompt_suffix` | `with ocean waves` | Ort-Klang |
| `background.image_ref` | `asset_bg_dragonstone_01` | Ort-Bild |
| `thumbnail.variant_overlay` | `Dragonstone` | Varianten-Text |

### Workflow-Scope (Override)
Einmalige Anpassungen für genau diesen Workflow-Lauf.

| Setting | Beispiel | Warum hier |
|---|---|---|
| `audio.duration_hours` | `5` (einmaliges Special) | Einmalig anders |
| `metadata.title` | `Custom Title Override` | Manuell gesetzt |
| `publish.privacy` | `private` (Test-Upload) | Einmalig anders |
| `audio.custom_prompt` | `Add thunderstorm...` | Kreativ-Override |

---

## Preset-Vererbung

### Wie es funktioniert

```
Preset "House Targaryen"
├── mood_profile: "dark, epic, fire"
├── default_duration_hours: 3
├── crossfade_seconds: 10
├── thumbnail_style: "dark fantasy, dragons"
│
├── Variant "Dragonstone"
│   ├── (erbt mood_profile, duration, crossfade, thumbnail_style)
│   ├── loop_duration_hours: 3  ← identisch, kein Override nötig
│   ├── background: dragonstone.jpg
│   └── variant_prompt_suffix: "with ocean waves and distant thunder"
│
├── Variant "Old Valyria"
│   ├── (erbt alles von Preset)
│   ├── loop_duration_hours: 1  ← Override: kürzer
│   ├── background: old_valyria.jpg
│   └── variant_prompt_suffix: "with volcanic rumble and ancient echoes"
│
└── Workflow #42 (Variant: Old Valyria)
    ├── (erbt alles von Old Valyria → Targaryen)
    └── duration_hours: 5  ← einmaliger Override
```

### Regeln

1. **Variant erbt alles vom Preset**, sofern nicht explizit überschrieben.
2. **Workflow erbt von Variant → Preset**, sofern nicht explizit überschrieben.
3. **Nur gesetzte Werte überschreiben.** `null` oder fehlend = erben.
4. **Kein Cross-Preset-Erben.** Eine Variant gehört zu genau einem Preset.

---

## Provider-Config-Scope

Provider-Konfiguration hat eigene Regeln, weil sie oft Infrastruktur betrifft.

| Provider | Config-Scope | Begründung |
|---|---|---|
| **GPU Worker** | System | Hardware, eine Instanz für alle |
| **YouTube OAuth** | Space | Ein Kanal pro Space/Projekt |
| **Storage Backend** | System | Infrastruktur-Entscheidung |
| **Storage Paths** | Space (Base) + Asset (Detail) | Projekt-Trennung |
| **ffmpeg** | System | Server-Tool |
| **Audio Post-Processing** | Preset (Default) + Workflow (Override) | Kreativ-Parameter |

### Beispiel: YouTube pro Space

```json
{
  "scope": "space",
  "space_id": "sp_whispers",
  "provider": "youtube",
  "config": {
    "client_secret_path": "./secrets/client_secret.json",
    "token_path": "./secrets/token.json",
    "default_privacy": "unlisted",
    "default_category_id": "10"
  }
}
```

---

## Feature Flags

Feature Flags leben als JSON im `settings`-Feld auf System- oder Space-Ebene.

### Struktur

```json
{
  "feature_flags": {
    "shorts_enabled": true,
    "new_audio_lab_ui": false,
    "parallel_audio_jobs": false,
    "auto_publish": false
  }
}
```

### Regeln

- **System-Flags** gelten global (z.B. `parallel_audio_jobs` = Infrastruktur).
- **Space-Flags** überschreiben System-Flags für diesen Space.
- Unbekannte Flags werden ignoriert (kein Fehler).
- Default für ungesetzte Flags: `false`.

### Abfrage im Code

```python
def is_feature_enabled(flag: str, space_id: str | None = None) -> bool:
    """Prüft Feature-Flag mit Scope-Auflösung."""
    if space_id:
        space_flags = get_space_settings(space_id).get("feature_flags", {})
        if flag in space_flags:
            return space_flags[flag]
    system_flags = get_system_settings().get("feature_flags", {})
    return system_flags.get(flag, False)
```

---

## Resolution-Algorithmus

### Pseudocode

```python
def resolve_config(key: str, workflow_id: str) -> Any:
    """
    Löst einen Config-Wert auf.
    Spezifischster Scope gewinnt.
    """
    workflow = get_workflow(workflow_id)

    # 1. Workflow-Override?
    value = workflow.config_overrides.get(key)
    if value is not None:
        return value

    # 2. Variant-Scope?
    if workflow.variant_id:
        variant = get_variant(workflow.variant_id)
        value = variant.override_configuration.get(key)
        if value is not None:
            return value

    # 3. Preset-Scope?
    preset = get_preset(workflow.preset_id)
    value = preset.default_configuration.get(key)
    if value is not None:
        return value

    # 4. Space-Scope?
    space = get_space(workflow.space_id)
    value = space.settings.get(key)
    if value is not None:
        return value

    # 5. System-Scope
    system = get_system_settings()
    value = system.get(key)
    if value is not None:
        return value

    # 6. Kein Wert gefunden
    return None  # oder Default aus Schema
```

### Auflösungskette (Zusammenfassung)

```
Workflow Override  →  Variant  →  Preset  →  Space  →  System  →  Default/None
  (spezifischst)                                        (allgemeinst)
```

### Wichtig

- `None` / fehlend = "nicht gesetzt" = weiter zum nächsten Scope.
- Explizit gesetzter Wert (auch `false`, `0`, `""`) = Override, nicht weitersuchen.
- Für Batch-Auflösung (alle Settings eines Workflows): Merge in umgekehrter Reihenfolge.

```python
def resolve_all_config(workflow_id: str) -> dict:
    """Merged Config aus allen Scopes."""
    workflow = get_workflow(workflow_id)
    merged = {}
    merged.update(get_system_settings())
    merged.update(get_space(workflow.space_id).settings)
    merged.update(get_preset(workflow.preset_id).default_configuration)
    if workflow.variant_id:
        merged.update(get_variant(workflow.variant_id).override_configuration)
    merged.update(workflow.config_overrides or {})
    return merged
```

---

## DB-Repräsentation (Vorschlag)

### Settings-Tabelle

```sql
CREATE TABLE settings (
    id          TEXT PRIMARY KEY,
    scope       TEXT NOT NULL,          -- 'system', 'space', 'preset', 'variant'
    scope_id    TEXT,                   -- NULL für system, sonst space_id/preset_id/variant_id
    key         TEXT NOT NULL,
    value_json  TEXT NOT NULL,          -- JSON-kodierter Wert
    updated_at  TEXT NOT NULL,
    updated_by  TEXT,
    UNIQUE(scope, scope_id, key)
);
```

Alternative: `settings_json`-Feld direkt auf den Entity-Tabellen (Space, Preset, Variant).
Für v1 ist das einfacher und ausreichend.

---

## Zusammenfassung

- **5 Scopes:** System → Space → Preset → Variant → Workflow
- **Spezifischster gewinnt:** Workflow-Override schlägt alles
- **Vererbung ist implizit:** Nicht-gesetzte Werte fallen zum nächsten Scope durch
- **Feature Flags:** Einfaches JSON, System + Space, Default = false
- **Provider-Config:** Lebt auf dem Scope, der fachlich passt (GPU = System, YouTube = Space)

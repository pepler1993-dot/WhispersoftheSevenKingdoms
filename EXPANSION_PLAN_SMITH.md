# Expansion Plan – Agent Smith
> Stand: 22.03.2026

## Vision
Von einem YouTube-Kanal zum automatisierten Multi-Plattform Content-Netzwerk.

---

## Phase 1 – Sofort (Woche 1-2)

### 1.1 Multi-Plattform Distribution
- **DistroKid** (~20€/Jahr) → Songs auf Spotify, Apple Music, Amazon Music, Tidal
- Gleiche MP3s, kein Mehraufwand, passive Einnahmen
- **Ich baue:** Automatisches Tagging + Metadaten-Export im DistroKid-Format

### 1.2 Shorts/Reels Pipeline
- Aus jedem 3h-Video automatisch 10-15 Shorts (60s) schneiden
- Hook-Text + Waveform-Animation + Thumbnail
- Auto-Upload auf YouTube Shorts, TikTok, Instagram Reels
- **Ich baue:** `scripts/shorts/generate_shorts.py` – ffmpeg-basiert, kein API nötig

### 1.3 Mehr Themes für bestehenden Kanal
- Braavos, Iron Islands, Dragonstone, Riverrun
- Nur neue Prompts + Farbpaletten + Fonts → Pipeline steht ja schon

---

## Phase 2 – Kurzfristig (Monat 1-2)

### 2.1 Zweiter Kanal: "Whispers of Middle Earth"
- Gleiche Pipeline, LotR-Themes: Shire, Rivendell, Mordor, Rohan, Minas Tirith
- Neue Thumbnails, Prompts, Farbpaletten – aber gleicher Code
- **Aufwand:** ~1 Tag Setup, dann läuft es identisch

### 2.2 24/7 Livestream Radio
- YouTube-Livestream: "Whispers of the Seven Kingdoms – 24/7 Sleep Radio"
- Song-Rotation im Loop, animierte Visuals
- Livestreams ranken extrem gut im Ambient/Sleep-Bereich
- **Ich baue:** ffmpeg-Loop + YouTube Live API Integration

### 2.3 SEO & Algorithmus-Optimierung
- A/B-Testing für Thumbnails (2 Varianten pro Video)
- Tag-Analyse: welche Keywords ranken am besten
- Upload-Timing optimieren (beste Uhrzeiten für Sleep Content)

---

## Phase 3 – Mittelfristig (Monat 3-6)

### 3.1 Kanal-Netzwerk
| Kanal | Nische | Status |
|-------|--------|--------|
| Whispers of the Seven Kingdoms | GoT Sleep Music | ✅ Aktiv |
| Whispers of Middle Earth | LotR Sleep Music | Phase 2 |
| Arcane Frequencies | Fantasy Study/Focus | Geplant |
| Ocean Dreams | Nature Ambience | Geplant |

### 3.2 KI-Voiceover Lore Content
- GoT/LotR Lore-Videos mit KI-Narration
- Script: GPT → Voice: ElevenLabs → Video: Pipeline
- Andere Zielgruppe, gleiche Community, Cross-Promotion

### 3.3 Community & Monetarisierung
- Discord-Server für Sleep-Music-Community
- Patreon: werbefreie Downloads, exklusive Themes
- Website mit eingebautem Sleep-Timer-Player

---

## Technische Prioritäten (was ich baue)

1. `scripts/shorts/generate_shorts.py` → Auto-Shorts aus Langvideos
2. `scripts/publish/distrokid_export.py` → Metadaten für Streaming-Plattformen
3. `scripts/publish/livestream.py` → 24/7 YouTube Live Setup
4. Neue Themes + Fonts für erweiterte Häuser
5. YouTube Analytics API → Performance-Tracking

---

## Monetarisierung Forecast

| Zeitraum | Quelle | Geschätzt |
|----------|--------|-----------|
| Monat 1-3 | YouTube AdSense | 0-50€ (Aufbau) |
| Monat 3-6 | AdSense + Spotify | 50-200€/Monat |
| Monat 6-12 | Multi-Kanal + Streaming | 200-1000€/Monat |
| Jahr 2 | Netzwerk + Community | 1000€+/Monat |

*Konservative Schätzung. Sleep/Ambient hat extrem hohe Watch-Time → gute RPMs.*

---

## Grundprinzip

**Ein Befehl → ein Song → alle Plattformen.**

Kein manueller Aufwand. Pipeline rein, Content raus. Skaliert endlos.

---

*– Agent Smith, Publishing & Strategy* 🗡️

# 🗺️ ROADMAP – Whispers of the Seven Kingdoms
> Stand: 22.03.2026

---

## Meilensteine

```
März 2026                    April 2026                    Mai-Juni 2026               Juli-Sept 2026
    │                            │                             │                           │
    ▼                            ▼                             ▼                           ▼
┌─────────┐              ┌──────────────┐              ┌──────────────┐            ┌──────────────┐
│ PHASE 1 │───────────▶ │   PHASE 2    │───────────▶ │   PHASE 3    │─────────▶ │   PHASE 4    │
│Foundation│              │Multiplikation│              │ Skalierung   │            │  Wachstum    │
└─────────┘              └──────────────┘              └──────────────┘            └──────────────┘
```

---

### 🏁 M1 – Erster Song Live (Woche 1-2)
- [ ] Song "Whispers of Winterfell" generieren (Kaggle/Proxmox)
- [ ] Pipeline durchlaufen: `pipeline.py --slug whispers-of-winterfell`
- [ ] Erster YouTube Upload
- [ ] GPU-Passthrough auf Kevins Proxmox einrichten
- [ ] Pipeline-Fehlerhandling dokumentiert
- **Ergebnis:** 1 Song auf YouTube ✅

---

### 📈 M2 – Shorts, Streaming & Growth Engine (Woche 2-4)
- [ ] Shorts-Pipeline bauen (`scripts/shorts/generate_shorts.py`)
  - Auto-Cut: 10-15 × 60s Clips pro Song
  - Jeder Short mit Hinweis auf Full Video
- [ ] DistroKid Account → Songs auf Spotify, Apple Music, Amazon
- [ ] 4 weitere Songs generieren (King's Landing, Targaryen, Highgarden, Castamere)
- [ ] SEO-Automatisierung in Metadaten-Generator
  - Titel-Format: `{Name} | 3 Hours Deep Sleep Music | Fantasy Ambient`
  - Auto-Tags: sleep music, fantasy, ambient, GoT keywords
  - Upload-Timing: 18-20 Uhr UTC
- [ ] Reddit Post-Draft Generator (`scripts/marketing/reddit_draft.py`)
  - Pro Song ein fertiger Post für r/sleep, r/gameofthrones, r/Fantasy
- [ ] Playlist-Automatisierung im YouTube Upload Script
- [ ] Performance-Tracking einrichten (JSON: Views, CTR, Watchtime)
- **Ziel:** 50-75 Shorts online, 200-500h Watchtime
- **Ergebnis:** 5 Songs live, Shorts laufen, Musik auf Streaming-Plattformen

---

### 🚀 M3 – Zweiter Kanal (Monat 2-3)
- [ ] "Whispers of Middle Earth" Kanal erstellen
- [ ] LotR-Themes: Shire, Rivendell, Mordor, Rohan, Minas Tirith
- [ ] Automatische Song-Generierung via Proxmox GPU (Cron)
- [ ] Weitere GoT-Themes: Braavos, Iron Islands, Dragonstone
- **Ergebnis:** 2 aktive Kanäle, lokale GPU, kein Cloud-Limit

---

### 👑 M4 – Monetarisierung (Monat 3-6)
- [ ] YouTube Partner Program (1000 Subs + 4000h Watchtime)
  - Sleep Music Vorteil: 1 View = 3h Watchtime → nur ~1.333 Views nötig
- [ ] 24/7 YouTube Livestream Radio
- [ ] A/B-Testing Thumbnails
- [ ] Kollaborationen mit anderen Ambient/Sleep-Kanälen
- [ ] Discord Community (ab 500+ Subs)
- [ ] Drittes Universum evaluieren
- **Ergebnis:** Erste Einnahmen, wachsende Community

---

## 📊 Wachstums-Prognose

| Monat | Subs | Watchtime | Shorts | Songs |
|-------|------|-----------|--------|-------|
| 1 | 50-100 | 200-500h | 15-30 | 1-2 |
| 2 | 200-400 | 1000-2000h | 50-75 | 5 |
| 3 | 500-800 | 2500-3500h | 100+ | 8+ |
| 4 | 1000+ ✅ | 4000h+ ✅ | 120+ | 10+ |

## 🤖 Was die Pipeline automatisch macht

```
Song (MP3) rein
    ↓
├── Thumbnail (haus-spezifischer Font + Background)
├── Full Video (3h, 1080p, Partikeleffekte)
├── 10-15 Shorts (auto-cut, 60s)
├── Metadaten (SEO-Titel, Tags, Beschreibung)
├── Reddit Post-Draft
├── DistroKid Export
└── YouTube Upload + Playlist-Einsortierung
    ↓
Alles online 🚀
```

---

## Revenue Ziele

| Zeitraum | Ziel |
|----------|------|
| Monat 3 | YouTube Monetarisierung freigeschaltet |
| Monat 6 | 50-200€/Monat (AdSense + Streaming) |
| Monat 12 | 200-1000€/Monat (Multi-Kanal) |
| Jahr 2 | 1000€+/Monat (Netzwerk) |

---

## Aktuelle Priorität

**→ M1: Ersten Song live bringen. Alles andere kommt danach.**

---

*Detaillierter Plan: EXPANSION_PLAN_FINAL.md | Ideen: IDEAS.md*

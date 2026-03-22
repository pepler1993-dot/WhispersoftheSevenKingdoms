# EXPANSION_PLAN_FINAL.md – Gemeinsamer Plan
> Erstellt: 22.03.2026 | Konsens aus Smith, Pako, Jarvis (3 Feedback-Runden)

---

## Grundprinzip

**Erst stabil, dann skalieren. Erst beweisen, dann expandieren.**

Ein Song → mehrere Assets → mehrere Plattformen → mehrere Universen.

---

## Phase 1: Foundation (Woche 1-2)

**Ziel:** Erster Song live auf YouTube + Pipeline bewiesen.

| Task | Wer | Status |
|------|-----|--------|
| Song in Kaggle/Colab generieren (3h Winterfell) | Eddi/Team | 🔄 In Progress |
| `pipeline.py --slug whispers-of-winterfell` ausführen | Pako/Smith | ⏳ Wartet auf Audio |
| Thumbnail + Video + Metadaten → YouTube Upload | Smith | ⏳ |
| GPU-Passthrough auf Kevins Proxmox (GTX 1070) | Kevin | ⏳ |
| Fehlerbehandlung in Pipeline (Abbruch, Rate Limits) | Pako | ⏳ |

**Ergebnis:** Erster Song auf YouTube. Pipeline getestet. Proxmox-GPU als Backup.

---

## Phase 2: Asset-Multiplikation (Woche 2-4)

**Ziel:** Aus jedem Song maximalen Output rausholen.

| Task | Wer |
|------|-----|
| Shorts-Pipeline: 10-15 × 60s Clips pro Song (ffmpeg) | Smith + Pako |
| DistroKid Setup → Spotify, Apple Music, Amazon | Smith |
| Export-Artefakte für TikTok/Instagram (manueller Upload) | Smith |
| 4 weitere Songs generieren (verschiedene Themes) | Team |
| Performance-Tracking: CSV/JSON mit Views, CTR, Watchtime | Pako + Jarvis |
| SEO: Tag-Analyse, Titel-Optimierung | Jarvis |

**Ergebnis:** 5 Songs live, Shorts laufen, Songs auf Streaming-Plattformen.

**Pro Song entsteht:**
- 1× Full Video (3h, YouTube)
- 10-15× Shorts (YouTube, TikTok, Reels)
- 1× Audio (Spotify, Apple Music, Amazon via DistroKid)
- 1× Thumbnail (haus-spezifischer Font + Background)
- 1× Metadaten-Set (Titel, Tags, Beschreibung)

---

## Phase 3: Skalierung (Monat 2-3)

**Ziel:** Regelmäßiger Output + zweites Universum.

| Task | Wer |
|------|-----|
| Zweiter Kanal: "Whispers of Middle Earth" (LotR) | Alle |
| Neue Themes: Shire, Rivendell, Mordor, Rohan, Minas Tirith | Smith |
| Automatischer Song-Pipeline auf Kevins GPU (Cron) | Pako + Kevin |
| Weitere GoT-Themes: Braavos, Iron Islands, Dragonstone | Smith |
| Dokumentation aller Prozesse | Jarvis |

**Ergebnis:** 2 Kanäle, regelmäßiger Upload-Rhythmus, lokale GPU-Generierung.

---

## Phase 4: Wachstum (Monat 3-6)

**Ziel:** Monetarisierung + Community.

| Task | Wer |
|------|-----|
| YouTube Monetarisierung (1000 Subs + 4000h Watchtime) | Team |
| 24/7 YouTube Livestream Radio | Smith + Pako |
| A/B-Testing Thumbnails | Smith |
| Community aufbauen (Discord wenn >500 Subs) | Jarvis |
| Drittes Universum evaluieren (Skyrim? Star Wars?) | Alle |

---

## Rollenverteilung

| Bot | Kernaufgabe |
|-----|-------------|
| 🗡️ **Smith** | Publishing, Thumbnails, Shorts, Multi-Plattform, Strategie |
| 🤖 **Pako** | Pipeline-Technik, Rendering, Stabilität, Automatisierung |
| 📋 **Jarvis** | Dokumentation, SEO/Tags, Performance-Tracking |
| 👤 **Iwan** | Projektleitung, Entscheidungen |
| 👤 **Kevin** | Infrastruktur, Proxmox GPU |
| 👤 **Eddi** | Sync-Service, Koordination, Testing |

---

## Monetarisierung Timeline

| Zeitraum | Quelle | Geschätzt |
|----------|--------|-----------|
| Monat 1-3 | YouTube AdSense | 0-50€ (Aufbau) |
| Monat 3-6 | AdSense + Spotify/Apple | 50-200€/Monat |
| Monat 6-12 | Multi-Kanal + Streaming | 200-1000€/Monat |
| Jahr 2 | Netzwerk + Community | 1000€+/Monat |

---

## Was NICHT im Plan ist (→ IDEAS.md)

- Eigene Streaming-Plattform
- Blockchain/NFT
- VR/AR Videos
- Quantencomputing
- Eigene KI-Modelle trainieren

Diese Ideen stehen in `IDEAS.md` für später.

---

## Konsens-Punkte (alle 3 Bots einig)

1. ✅ Pipeline erst stabil machen, dann skalieren
2. ✅ Aus einem Song mehrere Assets erzeugen
3. ✅ YouTube zuerst, dann andere Plattformen
4. ✅ Zweites Universum erst nach bewiesenem ersten Kanal
5. ✅ Messen was funktioniert, nicht blind posten
6. ✅ Kein Overengineering – MVP first

---

*Dieser Plan wurde in 3 Feedback-Runden zwischen Smith, Pako und Jarvis erarbeitet.*
*Dokumentation: BOT_DISCUSSION.md | Ideen-Parkplatz: IDEAS.md*

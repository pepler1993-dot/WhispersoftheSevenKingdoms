# Architecture Diagram

Dieses Diagramm zeigt die aktuelle Systemstruktur auf hoher Ebene.

Es ist bewusst simpel gehalten: verständlich > beeindruckend.

## High-Level Overview

```mermaid
flowchart TD
    U[User / Team] --> D[Dashboard / Control Plane\nservices/sync]
    D --> A[Audio: Stable Audio Local\nGPU-Worker via services/sync]
    A --> IN[data/upload/songs]
    D --> M[data/upload/metadata]
    D --> T[data/upload/thumbnails]

    IN --> P[pipeline/pipeline.py]
    M --> P
    T --> P

    P --> AU[pipeline/scripts/audio]
    P --> TH[pipeline/scripts/thumbnails]
    P --> ME[pipeline/scripts/metadata]
    P --> VI[pipeline/scripts/video]
    P --> QA[pipeline/scripts/qa]
    P --> YT[pipeline/scripts/publish]

    TH --> OUT[data/output/youtube/<slug>]
    ME --> OUT
    VI --> OUT
    QA --> REP[data/work/publish/reports]
    P --> JOB[data/work/jobs/<slug>/status.json]
    YT --> Y[YouTube]
```

## Interpretation

- `services/sync/` ist die **Control Plane**
- `pipeline/` ist der **Produktionspfad**
- `data/` ist die operative Datei- und Statusschicht
- Audio-Erzeugung: **stable-audio-local** (GPU-Worker); die Pipeline braucht nur gültige Dateien unter `data/upload/songs/`
- Upload ist bewusst nur ein späterer Schritt, nicht die einzige Wahrheit des Systems

## Wichtige Architekturidee

Die Pipeline ist **nicht** an die Erzeugung gekoppelt: wichtig ist, dass gültiges Audio + Metadaten + optional Thumbnail vorliegen. Im Dashboard ist die Erzeugung fest **Stable Audio Local**.

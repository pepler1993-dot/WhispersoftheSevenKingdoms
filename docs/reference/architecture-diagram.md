# Architecture Diagram

Dieses Diagramm zeigt die aktuelle Systemstruktur auf hoher Ebene.

Es ist bewusst simpel gehalten: verständlich > beeindruckend.

## High-Level Overview

```mermaid
flowchart TD
    U[User / Team] --> D[Dashboard / Control Plane\nservices/sync]
    D --> A[Audio Generator Paths\nKaggle / Colab / Local Worker]
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
- Audio-Generatoren sind austauschbare vorgelagerte Quellen
- Upload ist bewusst nur ein späterer Schritt, nicht die einzige Wahrheit des Systems

## Wichtige Architekturidee

Die Pipeline soll möglichst **nicht hart an einen einzelnen Audio-Provider gekoppelt** sein.
Wichtig ist am Ende, dass gültiges Audio + Metadaten + optional Thumbnail vorliegen.

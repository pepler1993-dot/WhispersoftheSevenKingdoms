# Library Management Plan

This document defines the first implementation plan for a dedicated dashboard area that manages the asset library used by the pipeline.

## Goal

Create a human-friendly **Library** section in the dashboard where operators can manage the assets required to start pipeline runs.

Primary asset groups for the MVP:
- Songs
- Thumbnails
- Metadata

## Why this is needed

The current dashboard lets users **select** library assets during pipeline creation, but there is no central place to **manage** those assets.

That creates avoidable friction:
- assets are selectable but not visible as a library
- uploads are mixed into pipeline start instead of proper asset management
- people cannot easily inspect what is available before starting a run

## MVP principles

- Keep the Library area focused on **pipeline input assets**
- Make it **human-readable** for operators and project managers
- Prefer a clean central library over scattered upload controls
- Do not overcomplicate the first release with bulk workflows or advanced media tooling

## MVP scope

### 1. New dashboard section
Add a dedicated navigation item:
- **Library**

### 2. Human-readable asset overview
For each asset group show:
- file name
- type
- file size
- last modified timestamp
- path / location hint when useful

### 3. Upload support
Allow uploads for:
- songs
- thumbnails
- metadata JSON

### 4. Clear organization
Separate the library into at least these sections:
- Songs
- Thumbnails
- Metadata

### 5. Pipeline relationship
The Create tab should continue to use these assets, but the Library page becomes the primary place to manage them.

## Explicitly out of scope for the first slice
- drag-and-drop multi-upload polish
- asset renaming in UI
- deletion / trash flow
- tagging / search / filtering beyond simple listing
- bulk asset operations
- shorts-specific library surfaces

## Implementation phases

## Phase 1 — foundation
- add Library nav item
- add Library page route and template
- list current assets from the known upload directories
- keep presentation readable and grouped by asset type

## Phase 2 — uploads
- add upload forms for songs, thumbnails, metadata
- save files into the correct library directories
- show success / error messages in UI

## Phase 3 — integration polish
- make Create page clearly reference the Library as the asset source of truth
- improve empty states and operator guidance
- optionally add lightweight preview details where useful

## Affected areas

### Dashboard / service
- `services/sync/app/main.py`
- `services/sync/templates/base.html`
- `services/sync/templates/library.html`

### Data / filesystem
- `data/upload/songs/`
- `data/upload/thumbnails/`
- `data/upload/metadata/`

## Acceptance criteria for initial MVP

- operators can open a dedicated Library page
- songs, thumbnails, and metadata are clearly listed
- uploads can be performed from the Library page
- the page is understandable without needing terminal access
- the Create pipeline still works with the same underlying asset folders

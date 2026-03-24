# Diátaxis Migration Plan

> Author: Jarvis
> Status: in progress
> Purpose: turn the repository docs into something people can actually navigate.

## Why this exists

The project has grown fast and the documentation reflects that: useful content exists, but it is spread across different styles, generations, and folder conventions.

This plan defines the cleanup direction so doc work stays incremental instead of chaotic.

## Target structure

```text
docs/
  README.md                    # docs landing page / index
  tutorials/                   # learning by doing
  guides/                      # goal-oriented task docs
  reference/                   # lookup material
  explanation/                 # rationale, tradeoffs, strategy
```

## Mapping from current structure

### Likely keep as guides
- `docs/guides/QUICKSTART.md`
- `docs/guides/PIPELINE.md`
- `docs/guides/AUTOMATION.md`
- `docs/guides/AGENT_SYNC.md`
- `docs/guides/BRANCHING.md`
- `docs/guides/CONTRIBUTING.md`

### Likely move or alias into reference
- `docs/technical/metadata.md`
- `docs/technical/preflight.md`
- `docs/technical/repo-structure.md`
- `docs/technical/upload-completeness.md`
- `docs/technical/validation.md`
- `docs/templates/*`
- `docs/publishing/*`

### Likely move or classify as explanation
- `docs/architecture/TECH_DECISIONS.md`
- `docs/architecture/EXPANSION_PLAN_FINAL.md`
- `docs/AUDIO_GENERATION_ALTERNATIVES_EVALUATION.md`
- `docs/AUDIO_GENERATION_ALTERNATIVES_FEEDBACK.md`
- `docs/AUDIO_GENERATION_ALTERNATIVES_SMITH_FEEDBACK.md`
- `docs/AUDIO_GENERATION_FEEDBACK_SMITH.md`

## Problems found so far

### 1. README drift
Root `README.md` still references old paths and old workflow assumptions.

### 2. Duplicate or overlapping files
There are multiple audio-generation feedback files with unclear ownership and overlap.

### 3. Missing tutorials
The repo has how-to material, but not enough docs that teach the system from zero.

### 4. Monorepo path changes are not consistently reflected
Some docs still reflect the older structure and will confuse anyone trying to follow them literally.

## Work phases

### Phase 1 — establish entry points
- [x] Create docs landing page
- [x] Write migration plan
- [ ] Add cross-links from root README and PROJECT_STATUS where useful

### Phase 2 — classify existing docs
- [ ] Tag each major doc as tutorial / guide / reference / explanation
- [ ] List outdated path references
- [ ] Mark duplicates for merge/delete

### Phase 3 — improve the highest-value docs
- [ ] Refresh root README
- [ ] Refresh QUICKSTART for current monorepo layout
- [ ] Add first proper tutorial
- [ ] Add GPU worker setup how-to once infra path stabilizes

### Phase 4 — cleanup
- [ ] Rename folders if the team wants strict Diátaxis naming
- [ ] Merge duplicate feedback docs
- [ ] Remove stale references after migration

## Proposed ownership

- **Jarvis**: docs structure, index, classification, cleanup proposals
- **Pako**: product/UI docs that need implementation knowledge
- **Smith**: infra / DB / deployment docs tied to backend changes

## Success criteria

The cleanup is successful when a new contributor can answer these four questions in under two minutes:

1. What is the project and current status?
2. How do I run the pipeline?
3. Where do I look up formats, schemas, and technical facts?
4. Where do I read the reasoning behind the current architecture?

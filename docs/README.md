# Documentation Index

This repository is moving toward a Diátaxis-style documentation structure so people can find the right kind of information quickly instead of digging through archaeology layers.

## Start here

- **Project status / current truth**: [`../PROJECT_STATUS.md`](../PROJECT_STATUS.md)
- **Roadmap / what comes next**: [`../ROADMAP.md`](../ROADMAP.md)
- **Repository overview**: [`../README.md`](../README.md)

## Diátaxis map

### Tutorials
Learning-oriented, step-by-step material for getting something working end to end.

- _Planned_: first-run tutorial for local setup
- _Planned_: first successful end-to-end song generation + publish walkthrough

### How-to guides
Goal-oriented instructions for a concrete task.

- [`guides/QUICKSTART.md`](guides/QUICKSTART.md)
- [`guides/PIPELINE.md`](guides/PIPELINE.md)
- [`guides/AUTOMATION.md`](guides/AUTOMATION.md)
- [`guides/AGENT_SYNC.md`](guides/AGENT_SYNC.md)
- [`guides/BRANCHING.md`](guides/BRANCHING.md)
- [`guides/CONTRIBUTING.md`](guides/CONTRIBUTING.md)

### Reference
Lookup material: structures, schemas, templates, technical facts.

- [`technical/repo-structure.md`](technical/repo-structure.md)
- [`technical/metadata.md`](technical/metadata.md)
- [`technical/validation.md`](technical/validation.md)
- [`technical/preflight.md`](technical/preflight.md)
- [`technical/upload-completeness.md`](technical/upload-completeness.md)
- [`templates/`](templates/)
- [`publishing/`](publishing/)

### Explanation
Why things are the way they are, tradeoffs, strategy, architecture.

- [`architecture/TECH_DECISIONS.md`](architecture/TECH_DECISIONS.md)
- [`architecture/EXPANSION_PLAN_FINAL.md`](architecture/EXPANSION_PLAN_FINAL.md)
- [`AUDIO_GENERATION_ALTERNATIVES_EVALUATION.md`](AUDIO_GENERATION_ALTERNATIVES_EVALUATION.md)
- [`AUDIO_GENERATION_ALTERNATIVES_FEEDBACK.md`](AUDIO_GENERATION_ALTERNATIVES_FEEDBACK.md)
- [`AUDIO_GENERATION_ALTERNATIVES_SMITH_FEEDBACK.md`](AUDIO_GENERATION_ALTERNATIVES_SMITH_FEEDBACK.md)
- [`AUDIO_GENERATION_FEEDBACK_SMITH.md`](AUDIO_GENERATION_FEEDBACK_SMITH.md)

## Current documentation problems

These are the main issues still being cleaned up:

1. **Outdated paths** – some docs still refer to pre-monorepo paths like `scripts/` or `publishing/musicgen/`.
2. **Mixed doc types** – tutorials, reference, and rationale are currently mixed together.
3. **Duplicate feedback docs** – there are overlapping audio-generation feedback files that should be merged or clearly differentiated.
4. **Missing true tutorials** – there are several guides, but almost no beginner-friendly learning docs yet.

## Next cleanup steps

- Create a proper `tutorials/` section
- Rewrite `README.md` to reflect current monorepo paths
- Merge or clarify duplicate audio-generation feedback documents
- Add a "local GPU worker setup" how-to once the VM path is stable

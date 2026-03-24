# Claim Expiry Investigation Plan

This document is the detailed execution plan for backlog item **"Claims expire unexpectedly"**.

Related issue:
- GitHub Issue **#67** — Ops: investigate why sync-service claims expire unexpectedly

## Goal

Determine why sync-service claims sometimes expire while agents still believe they are actively working, then define and implement the required fixes.

## Investigation questions

The work should answer these questions clearly:

1. What is the exact lifecycle of a claim in the current system?
2. Under what conditions does a claim become stale or expire?
3. Are claims expiring because of missing heartbeats, short leases, race conditions, task duplication, or incorrect workflow usage?
4. Is the problem mostly backend logic, agent behavior, or poor visibility in Operations?
5. What should be fixed in code vs. in workflow vs. in UI warnings?

## Execution phases

## Phase 1 — trace the current lifecycle
- inspect the sync-service claim, heartbeat, release, and complete endpoints
- inspect task state storage and lease timestamps
- map the state transitions for:
  - issue visible
  - claim
  - heartbeat
  - release
  - done
  - stale/expired
- write down the actual current behavior in plain language

### Output of phase 1
A short technical note describing how claim/lease state currently works.

## Phase 2 — identify failure modes
- inspect the relevant backend code paths for lease expiry and stale detection
- inspect Operations/task UI for how those states are presented
- identify realistic failure scenarios such as:
  - heartbeat not sent at all
  - heartbeat sent too late
  - lease duration shorter than real task behavior
  - task claimed multiple times across agents/sessions
  - completed work marked `released` instead of `done`
  - task visible delay between GitHub issue creation and sync ingestion

### Output of phase 2
A concrete list of failure modes with evidence from code and/or observed behavior.

## Phase 3 — validate against real examples
- compare the backend logic with cases the team has already seen in chat
- inspect task/ops data for examples of expired or stale claims
- verify whether multi-task drift and missing `done` transitions are contributing factors

### Output of phase 3
A short findings summary connecting real incidents to identified failure modes.

## Phase 4 — define fixes
Split fixes into categories:

### Backend fixes
Examples:
- lease duration adjustments
- heartbeat handling corrections
- stale detection improvements
- more robust task visibility timing

### Workflow fixes
Examples:
- `done` vs `released` rule enforcement
- no repo work before visible task + claim
- no parallel active tasks without explicit intent

### UI / Operations fixes
Examples:
- stale claim warnings
- multiple-active-task warnings
- visible protocol health card
- task history clarity improvements

### Output of phase 4
A proposed fix list grouped by backend / workflow / UI.

## Phase 5 — implementation plan
Once root causes are confirmed, split the implementation into follow-up issues or execution slices:
- backend reliability changes
- operations visibility improvements
- workflow/documentation guardrails

## Deliverables

This task should produce:
- a documented understanding of the current claim lifecycle
- a list of verified failure modes
- a grouped set of proposed fixes
- a recommended implementation order

## Success criteria

This investigation is complete when:
- the team can explain why claims expire today
- the main failure modes are evidence-based, not guesses
- the next implementation tasks are clearly defined
- the result is actionable for both code and workflow changes

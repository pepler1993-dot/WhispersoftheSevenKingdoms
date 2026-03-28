# UI/UX Agent Workflow

## Core rule
GitHub is the source of truth. Telegram is only the trigger channel.

## Roles
1. Reviewer diagnoses
2. Designer defines solution
3. Implementer applies solution
4. Reviewer verifies result

## One task = one GitHub issue
Each UI/UX task must live in one issue with:
- problem / goal
- route or page
- screenshots if needed
- latest decisions
- PR link
- current status

## Labels
- needs-review
- review-complete
- needs-design
- design-complete
- ready-for-implementation
- implemented
- needs-re-review
- done
- blocked
- needs-human-decision

## Sequence
### 1. Review
Reviewer reads the issue, opens the UI if needed, adds findings, then marks review-complete.

### 2. Design
Designer reads the review, writes the solution and acceptance criteria, then marks design-complete and ready-for-implementation.

### 3. Implementation
Implementer reads the proposal, creates/updates the branch and PR, documents changes, then marks implemented and needs-re-review.

### 4. Re-review
Reviewer checks the result against the original problem and acceptance criteria, then either approves or sends back.

## Handoff rules
- Do not skip roles.
- Do not duplicate work.
- Only one role should actively drive a task at a time.
- Always read the latest issue/PR context before acting.
- Important decisions must be written in GitHub, not only in Telegram.

## Decision boundaries
- Reviewer owns problem diagnosis.
- Designer owns UX/UI direction.
- Implementer owns technical execution.
- Reviewer owns final user-facing validation.

## Telegram usage
Use Telegram only to trigger the next role, for example:
- Reviewer: handle issue #42
- Designer: use review in issue #42 and write proposal
- Implementer: implement issue #42
- Reviewer: re-review issue #42

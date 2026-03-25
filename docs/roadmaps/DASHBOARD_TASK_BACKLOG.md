# Dashboard Task Backlog

This document captures the current dashboard, workflow, and operations backlog from the team discussion and turns it into concrete work items.

It is written as a practical backlog for implementation planning, not as a raw transcript.

## Priority A — critical / blocking

## 1. Claims expire unexpectedly
**Status:** In progress / partially implemented. Heartbeat + lease fields and related task-phase handling exist in the sync service, but the full investigation + dashboard visibility + acceptance criteria are not yet fully closed.

**Goal:** Sync-service claims should not expire unexpectedly while an agent is actively working.

### Tasks
- Trace the full lifecycle of a claim: issue → task visible → claim → heartbeat → completion.
- Identify whether claim expiry is caused by missing heartbeats, wrong lease duration, race conditions, or agents holding multiple active tasks.
- Add clearer visibility in the dashboard for stale claims, missing heartbeats, and multiple active task assignments.
- Enforce the semantic rule that completed work must end in `done`, not `released`.
- Add protocol-health warnings in Operations when claims are stale or workflow rules are being violated.

### Acceptance criteria
- A claimed task remains active while valid heartbeats continue.
- If a claim becomes stale, the reason is visible in Operations.
- Finished work no longer incorrectly lands in `released`.

## 2. Ticket system in the dashboard
**Goal:** Users should be able to enter bugs, features, and changes directly in the dashboard, with tasks flowing from there to GitHub and the sync service.

### Tasks
- Add a dedicated **Tickets** area to the dashboard.
- Support ticket types such as Bug, Feature, Improvement, Ops, and Documentation.
- Build a form with title, type, priority, and detailed description.
- Create GitHub issues from dashboard tickets.
- Ensure created issues appear as sync-service tasks.
- Add a dashboard list for open, in-progress, and completed tickets.
- Link dashboard ticket ↔ GitHub issue ↔ sync task.

### Acceptance criteria
- A user can create a ticket in the dashboard.
- The ticket creates a GitHub issue.
- That issue becomes a visible sync task.

## 3. Old Kaggle logic still visible in Audio Lab / Pipeline
**Goal:** Audio generation should consistently use the GPU-worker-based flow without confusing Kaggle leftovers.

### Tasks
- Audit Audio Lab for remaining Kaggle-specific labels, form fields, and provider messaging.
- Remove or replace outdated Kaggle-specific UI elements.
- Align prompt, preset, and generation settings with the GPU-worker model.
- Ensure the "generate song directly in pipeline" flow does not still use the old Kaggle path.
- Simplify the form so only relevant fields remain visible.

### Acceptance criteria
- Audio Lab no longer presents misleading Kaggle-first UI.
- Pipeline and Audio Lab use the same current generation model.

## 3a. Audio-to-pipeline workflow is still too fragmented
**Goal:** A user should be able to start production in one coherent flow instead of manually hopping between audio generation, pipeline start, and upload steps.

### Tasks
- Allow a pipeline configuration to optionally auto-upload to YouTube after successful completion.
- Add an explicit "generate audio and continue directly into pipeline" mode so users do not need to first trigger audio generation and then separately start the pipeline.
- Support a true overnight flow where audio, thumbnail, metadata, video, QA, and optional upload can run in one go without another manual click.
- Clarify in the UI whether a run is waiting for audio, actively generating audio, rendering video, awaiting manual review, or uploading.
- Review whether the current safety stance for automatic upload should stay opt-in per run, opt-in per preset, or both.

### Acceptance criteria
- A user can launch a single run that includes audio generation and pipeline execution.
- Auto-upload can be enabled intentionally without needing to press a second upload button after completion.
- The run state clearly communicates which phase the workflow is currently in.

## 3b. Audio job cancel is unreliable or missing
**Goal:** Users must be able to stop an audio generation job cleanly from the dashboard.

### Tasks
- Trace the cancel flow from UI action to worker/process termination.
- Verify cancel behavior for queued, pushing, running, and downloading audio-job states.
- Make sure cancel updates job status consistently in storage and UI.
- Show a clear error or unsupported-state message when a job cannot be cancelled yet.
- Add regression coverage so cancel does not silently fail again.

### Acceptance criteria
- A running or queued audio job can be cancelled from the dashboard.
- The resulting state is visible and consistent.
- Failed cancellation attempts surface a visible reason instead of doing nothing.

## 3c. Thumbnail source/provenance is unclear
**Goal:** Users should be able to tell where the thumbnail used by a pipeline run came from.

### Tasks
- Show whether a thumbnail was selected from Library, uploaded manually, or auto-generated from the briefing.
- Surface the exact source file/path or generation mode on the run detail page.
- Make it obvious which thumbnail will be used before a run starts.
- Review fallback logic so unexpected thumbnail selection can be diagnosed quickly.

### Acceptance criteria
- Before and after a run, the dashboard shows which thumbnail source was chosen.
- Unexpected thumbnail usage can be traced without reading backend code.

## 3d. Pipeline jobs should support queueing and sequential execution
**Goal:** Users should be able to line up multiple productions so the next one starts automatically when the previous one finishes.

### Tasks
- Add first-class queue support for pipeline jobs instead of only one-off manual starts.
- Define queue semantics for waiting, running, completed, failed, cancelled, and blocked jobs.
- Ensure only the allowed number of concurrent runs execute at once, with the default being sequential processing.
- Add queue visibility in the dashboard with order, status, and estimated next start.
- Define how queued jobs interact with audio generation, optional auto-upload, and retry behavior.

### Acceptance criteria
- A user can add multiple pipeline jobs to a queue.
- When one job finishes, the next job starts automatically according to queue policy.
- Queue order and current status are visible in the dashboard.

## Priority B — dashboard usability and content clarity

## 4. Documentation start page is too dense
**Goal:** The docs homepage should be easier to scan and less overwhelming.

### Tasks
- Reduce the amount of information shown at once.
- Break the content into clearer entry sections.
- Prioritize first actions such as getting started, Audio Lab, Pipeline, Library, and Troubleshooting.
- Improve spacing and card grouping on desktop and mobile.

### Acceptance criteria
- Users can quickly identify where to click next.
- The docs homepage feels structured rather than overloaded.

## 5. Dashboard documentation is not consistently written from the user perspective
**Goal:** The dashboard docs should explain how to use the system, not how to run it locally.

### Tasks
- Review all user-facing docs sections for developer-only or server-only language.
- Remove or move instructions about local setup and implementation details.
- Rewrite user-facing content as task-oriented usage documentation.
- Separate technical/developer docs from operator/user docs more clearly.

### Acceptance criteria
- User-facing docs no longer talk about irrelevant local workflow details.
- A dashboard user can follow the docs without needing developer context.

## 6. Task summaries are still not meaningful enough
**Goal:** Task summaries in Operations should say what the task is actually about.

### Tasks
- Replace generic task summary text such as “Jarvis works on this now” with meaningful issue-derived summaries.
- Use the GitHub issue title as the base task description when available.
- Show a more detailed task description on the task detail page.
- Define fallback behavior when no rich issue description exists.

### Acceptance criteria
- Task list entries describe the actual task.
- Task detail pages provide a more detailed assignment description.

## 7. Task filters need to be more usable
**Goal:** Filtering tasks should feel immediate and intuitive.

### Tasks
- Make **Status** a dropdown.
- Make **Agent / Assignee** a dropdown.
- Apply filters live without requiring an extra “Filter” click.
- Turn the current filter button into a “Reset filters” action.
- Keep the UI responsive and mobile-friendly.

### Acceptance criteria
- Filters apply immediately after selection/input.
- Resetting filters is obvious and simple.

## 8. Bottom navigation on mobile is unstable
**Goal:** The mobile bottom navigation should behave consistently.

### Tasks
- Test all main views with the bottom navigation.
- Fix broken active states or layout jumps.
- Audit scroll behavior, fixed positioning, stacking order, and overflow.
- Improve tap-target quality and label fit.

### Acceptance criteria
- Mobile bottom navigation behaves reliably across the dashboard.

## Priority C — library and content management

## 9. Metadata should be creatable directly in Library
**Goal:** Users should be able to create metadata in the dashboard instead of only uploading files.

### Tasks
- Add a metadata form in Library.
- Support fields such as title, description, tags, privacy, and playlist metadata.
- Save the generated metadata as JSON in the metadata library.
- Optionally support editing existing metadata later.

### Acceptance criteria
- A user can create a metadata file from the dashboard UI.

## 10. Songs in Library need direct usability improvements
**Goal:** Song management in Library should be more useful and connected to workflow.

### Tasks
- Add a direct link from Library to Audio Lab.
- Support MP3 and WAV upload clearly.
- Add in-dashboard playback so tracks can be previewed.
- Show meaningful file details and playback controls.

### Acceptance criteria
- Songs can be uploaded and played back directly from Library.
- The relation between Library and Audio Lab is obvious.

## 11. Thumbnails need a creation workflow, not just storage
**Goal:** The dashboard should eventually support thumbnail creation rather than only file management.

### Tasks
- Define an MVP thumbnail editor concept.
- Explore drag-and-drop composition of text, emblem, image, and overlay elements.
- Define how a created thumbnail is exported and saved to Library.
- Decide whether this should start as a constrained template editor before a fully free editor.

### Acceptance criteria
- A concrete plan/MVP exists for dashboard-based thumbnail creation.

## 12. Animated video/image assets need a management concept
**Goal:** The pipeline needs a structured way to handle assets used for animated video output.

### Tasks
- Define a new library asset class for visual and animation inputs.
- Decide how backgrounds, overlays, motion layers, still images for animated output, or image sequences should be stored.
- Define how these assets are selected and referenced in the pipeline.
- Clarify whether the first version needs simple animated still-image videos or a richer asset animation workflow.

### Acceptance criteria
- There is a clear asset model for visuals used by animated video generation.
- The first implementation target for animated visual support is explicitly defined.

## Priority D — monitoring and system visibility

## 13. GPU-worker / GPU-server usage should be visible in the dashboard
**Goal:** Operators should see GPU health and utilization directly.

### Tasks
- Surface GPU load, VRAM usage, and temperature.
- Add queue/job-related GPU worker state where relevant.
- Present the information in a human-readable form.

### Acceptance criteria
- The dashboard shows the practical state of the GPU worker.

## 14. Proxmox PVE temperature should be visible in the dashboard
**Goal:** The operations view should include host thermal data.

### Tasks
- Identify a reliable temperature source on the PVE host.
- Decide which sensors matter for dashboard visibility.
- Add readable temperature display and warning thresholds.

### Acceptance criteria
- Operators can see PVE temperature in the dashboard.

## 15. Version and server metrics belong in the System tab
**Goal:** Move technical status information out of the homepage and into a better place.

### Tasks
- Move version information into the System tab.
- Move server metrics from the homepage into the System tab.
- Redesign the System tab into the main technical status surface.

### Acceptance criteria
- The homepage is cleaner.
- Technical metrics are grouped under System.

## Priority E — performance, security, and admin workflow

## 16. Audio Lab loads too slowly
**Goal:** Audio Lab should open quickly, with slow checks happening in the background.

### Tasks
- Profile what blocks initial page load.
- Move slow health checks or remote status checks to background fetches.
- Render the page immediately and hydrate secondary status later.
- Add non-blocking loading states where necessary.

### Acceptance criteria
- Audio Lab becomes fast to open.
- Long-running checks no longer block page rendering.

## 17. Slug should be generated automatically from title
**Status:** In progress — Pako is currently working on this task.

**Goal:** Users should not have to manually manage slugs.

### Tasks
- Remove or hide manual slug entry where possible.
- Auto-generate slug as lowercase title with spaces replaced by `-` and unsafe characters removed.
- Centralize slug generation logic so all flows behave consistently.

### Acceptance criteria
- Slugs are generated automatically from titles.
- Users are no longer forced to manage slugs manually.

## 18. Admin login with persistent sessions/cookies
**Goal:** Protect the dashboard without forcing repeated login prompts.

### Tasks
- Add admin authentication.
- Use sessions or cookies so authorized users stay logged in.
- Protect all admin-facing views.
- Add logout and sensible session lifetime.

### Acceptance criteria
- The dashboard is access-controlled.
- Admins do not need to log in again on every use.

## Priority F — roles and process

## 19. Pako should become a dedicated UI/UX tester
**Goal:** When Pako is stable again, define a concrete role for UX testing.

### Tasks
- Formalize Pako’s role as UI/UX tester.
- Define a workflow for testing, screenshot collection, findings, and follow-up tasks.
- Tie UI/UX testing into the dashboard improvement cycle.

### Acceptance criteria
- Pako has a defined test role rather than an ad-hoc one.

## Recommended implementation order

### Immediate next priorities
1. Fix claim expiry behavior.
2. Improve task summaries and task detail descriptions.
3. Improve task filters and live filtering.
4. Remove old Kaggle assumptions from Audio Lab and Pipeline.
5. Improve Audio Lab load performance.

### Near-term workflow improvements
6. Add the dashboard ticket system.
7. Extend Library with metadata form and song preview.
8. Fix mobile bottom navigation.
9. Clean up user-facing documentation.

### Structured expansion work
10. Add GPU and PVE metrics.
11. Auto-generate slugs.
12. Redesign the System tab.
13. Add admin login.
14. Design thumbnail editor and animated visual asset handling.
.
2. Enforce `done` vs `released` semantics in workflow and UI.
3. Add protocol-health visibility in Operations.

### Slice 2 — task management usability
4. Improve task summaries.
5. Add detailed task descriptions on the task detail page.
6. Improve task filters with live filtering and reset behavior.

### Slice 3 — audio workflow cleanup
7. Remove old Kaggle assumptions from Audio Lab and Pipeline.
8. Improve Audio Lab load performance.
9. Make presets/prompts and GPU-worker flow consistent in the UI.

### Slice 4 — library productivity
10. Extend Library with metadata form.
11. Add song preview/playback and tighter Audio Lab linking.
12. Define the visual/animation asset model.

### Slice 5 — content tooling and docs
13. Clean up user-facing documentation.
14. Redesign the docs homepage for clarity.
15. Design thumbnail editor / template workflow.

### Slice 6 — monitoring and system structure
16. Add GPU worker metrics.
17. Add PVE temperature.
18. Move version and server metrics into the System tab.

### Slice 7 — user/admin quality of life
19. Auto-generate slugs from title.
20. Add admin login with persistent sessions.
21. Fix remaining mobile navigation polish issues.

### Slice 8 — future process / testing roles
22. Add the dashboard ticket system.
23. Formalize Pako as UI/UX tester with a repeatable workflow.

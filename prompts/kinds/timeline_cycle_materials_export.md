# Codex Task: export Timeline cycle materials

{{ common.send_verification_block }}

You are working in repository:

```text
{{ repo.name }}
```

Repository path:

```text
{{ repo.path }}
```

## Purpose

Create the next-cycle evidence package for the Timeline product family after the recent product-thread commit wave.

This is not a new feature sprint. Treat it as an evidence collection and export cycle.

## Operating Context

{{ common.timeline_operating_context }}

## Product Focus

{{ product_note }}

## Cycle Context

Recent product-thread outcomes to capture:

- `TimelineForWindowsCodex`: committed `9c366da Finalize Timeline export metadata`
- `TimelineForChatGPT`: committed `18cbe2d Preserve final timeline metadata and attachment evidence`
- `TimelineForAudio`: committed `fe654fb Document audio run layout and bind web locally`
- `TimelineForVideo`: committed `fd685be Stabilize local TimelineForVideo verification`
- `TimelineForPC`: committed `f7c5f6e Document TimelineForPC verification workflow`

Push was not performed for these commits.

## Direction

Use the product's existing README, CLI, scripts, and tests to produce the strongest local export material that can feed the next operations-planning thread.

Keep the work focused on:

- Codex thread history export
- raw session evidence preservation
- product-thread `CYCLE_RESULT` recovery
- send-log / observed session evidence where available
- a concise next-cycle summary that helps the parent thread decide what to do next

Do not make product implementation changes unless a very small repo-local fix is necessary to make the export command honestly run.

## Expected Output

Create or identify the export artifacts that should be attached to the operations thread next.

Prefer existing product output locations and naming conventions. Do not invent a new parallel export format if the product already has one.

If source ZIP creation is already supported by this product or an existing local script, use it. If it is not supported, do not build a new ad-hoc zipper in this cycle; instead, report exactly what is missing and what existing artifact should be attached now.

## Verification

Run the relevant lightweight checks for the export path.

At minimum, verify that:

- the export artifact exists
- it includes evidence for the product threads above, or clearly states what was unavailable
- generated summary/status/result files are internally consistent
- no raw session data was deleted, moved, renamed, or rewritten

## Boundaries

```text
commit: allowed only for a small repo-local fix required to make the export path truthful
push: not allowed
```

Do not change secrets, deploy, publish externally, rename repos/products, delete raw history, or perform a broad output contract migration.

## Human Decision Standard

Ask the human only if the remaining decision is outside local export work.

If you need a human decision, explain in plain language:

- what is blocked
- what you already checked
- what artifact can still be produced
- what the human's smallest action is

## Report

Return a concise final report with:

```md
Run ID: <echo the run id above>

## Current state
## Export artifacts
## What was captured
## What was not captured
## Verification
## Commits
## Pushed
## Human decision needed
## Next recommended action

## CYCLE_RESULT

repo:
cycle_goal:
commits:
pushed:
tests:
changed_files:
completed:
blocked:
human_decisions_needed:
ready_for_next_cycle:
next_recommended_action:
```

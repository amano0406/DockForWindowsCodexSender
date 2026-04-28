# Codex Task: commit verified Timeline changes

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

Review the current local changes in this product thread and commit them if they are coherent, verified, and within the product's current direction.

Do not stop only because the working tree is dirty. Dirty changes are expected after a fix-forward cycle.

## Operating Context

{{ common.timeline_operating_context }}

## Product Focus

{{ product_note }}

## Direction

Keep this as a commit-readiness pass, not a new feature sprint.

Use your judgment to confirm:

- the diff belongs to the current product work
- the tests or smoke checks are strong enough for a local commit
- any caveats are clearly stated
- no secrets, raw user data, public deployment, product rename, or export contract breakage is included

If a small follow-up fix is necessary to make the commit honest, make it and verify it.

## Commit / Push Rule

```text
commit: allowed when the current verified changes are coherent
push: not allowed
```

Use a concise commit message that describes the product outcome, not the investigation steps.

## Human Decision Standard

Do not ask the human to decide ordinary repo maintenance or test repair. Ask only when the remaining choice is outside local product work, such as public release, push, secret changes, broad contract migration, or deleting/moving raw user data.

If you need a human decision, explain it in plain language and include the smallest action needed.

## Report

Return a concise final report with:

```md
Run ID: <echo the run id above>

## Current state
## What was committed
## Verification
## Commit status
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

# Codex Task: TimelineForVideo fix-forward

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

Move `TimelineForVideo` forward from the current E2E blocker state.

Do not treat a blocked test as a final answer by itself. Treat it as a signal to understand what is stopping progress, fix what can be fixed in the repo, and leave the product in a more verifiable state.

## Operating Context

{{ common.timeline_operating_context }}

## Product Focus

{{ product_note }}

## Direction

Keep the task outcome-oriented rather than procedural.

Use your judgment to distinguish:

- a repo problem that can be fixed safely
- a local environment setup gap
- a Windows safety feature blocking execution
- a case where an equivalent or near-equivalent smoke check is enough
- a case where human approval is genuinely needed

The preferred outcome is that the E2E smoke passes.

If that is not the practical outcome in this cycle, produce the strongest safe alternative:

- a low-risk repo fix
- a clearer and lighter verification path
- equivalent smoke coverage
- commit-ready evidence with caveats stated plainly
- a human decision request that is easy for a non-engineer to answer

## Human Decision Standard

Only ask the human when the remaining decision is genuinely outside repo-level work.

When asking, do not say only "security policy blocked it." Explain in plain language:

- what is being stopped
- what likely stopped it
- what you already checked
- what alternatives exist
- what each alternative costs or risks
- what you recommend
- the smallest action the human needs to take

## Boundaries

Stay local-first. Do not change secrets, publish externally, deploy, rename the product, push, or break the existing output/export contract.

## Report

Return a concise final report with:

```md
Run ID: <echo the run id above>

## Current state
## What changed
## Verification
## E2E blocker finding
## Commit status
## Human decision needed
## Next recommended action
```

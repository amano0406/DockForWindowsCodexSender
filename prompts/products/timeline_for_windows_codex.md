# Product note: TimelineForWindowsCodex

This product should timeline Codex threads, work history, repo state, and ledgers.

Baseline input:

```text
data/input/codex/
```

Baseline output:

```text
data/output/runs/timeline-for-windows-codex/
```

Use this model:

```text
1 thread bundle = 1 InputItem
1 thread bundle = 1 Job
1 codex export snapshot = parent Job
```

Prioritize:

- raw session JSONL as the primary evidence
- `state_5.sqlite` as discovery/fallback metadata, not source of truth
- read-only source roots
- thread status extraction
- repo status extraction
- unresolved task extraction
- AGENTS.md / prompt / docs references
- fidelity report
- reproducibility
- all-thread export / selected-thread export / environment ledger consistency
- `status.json` / `result.json` / `manifest.json` / `fidelity_report.json` finalize consistency

This product may later help receive/analyze results sent by DockForWindowsCodexSender.

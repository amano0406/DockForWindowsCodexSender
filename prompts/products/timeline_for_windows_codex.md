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

- thread status extraction
- repo status extraction
- unresolved task extraction
- AGENTS.md / prompt / docs references
- fidelity report
- reproducibility

This product may later help receive/analyze results sent by DockForWindowsCodexSender.

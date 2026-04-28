# Product note: TimelineForVideo

Use this model:

```text
1 video file = 1 InputItem
1 video file = 1 Job
1 Job can have multiple Runs
```

Baseline input:

```text
data/input/video/
```

Baseline output:

```text
data/output/runs/timeline-for-video/
```

Prioritize:

- original video preservation
- transcript traceability
- screen-derived evidence traceability
- audio extraction manifest
- visual frame/OCR sidecar handling
- scene/event timing
- fidelity report
- reproducibility
- worker / web / export contract stability
- Docker, start script, and local smoke stability

Avoid large rewrites until TimelineForAudio v2 output contracts are clearer.

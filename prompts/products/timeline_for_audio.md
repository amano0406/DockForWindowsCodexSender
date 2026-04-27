# Product note: TimelineForAudio

Use this model:

```text
1 audio file = 1 InputItem
1 audio file = 1 Job
1 Job can have multiple Runs
```

Baseline input:

```text
data/input/audio/
```

Baseline output:

```text
data/output/runs/timeline-for-audio/
```

Prioritize:

- original audio preservation
- input snapshot
- manifest
- fidelity report
- readable text
- LLM pack
- reproducibility

Do not force Audio-specific IPA / diarization / reconstruction concepts into other products.

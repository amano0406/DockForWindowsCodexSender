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
- IPA as an important intermediate artifact when present
- clear boundaries between transcription, diarization, reconstruction, and export
- input snapshot
- manifest
- fidelity report
- readable text
- LLM pack
- reproducibility
- mock mode and local smoke stability

Do not force Audio-specific IPA / diarization / reconstruction concepts into other products.

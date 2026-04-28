# Product note: TimelineForChatGPT

Use this model:

```text
1 ChatGPT export zip or export directory = 1 parent Job
conversation-level processing = child Job or child artifact
attachments = inventory + sidecar + evidence reference
```

Baseline input:

```text
data/input/chatgpt/
```

Baseline output:

```text
data/output/runs/timeline-for-chatgpt/
```

Prioritize:

- conversation order
- message order
- original export preservation
- attachment inventory
- branch ambiguity disclosure
- missing attachment disclosure
- main pack / sidecar text pack / binary evidence inventory
- hash, size, mtime, relative path
- missing or unprocessed attachment disclosure

Keep responsibilities separate:

- TimelineForChatGPT transforms ChatGPT export data into Timeline artifacts.
- TimelineForWindowsCodex handles Codex session/work history.
- DockForChatGPT operates ChatGPT Web as a bridge.

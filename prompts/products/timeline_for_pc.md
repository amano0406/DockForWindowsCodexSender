# Product note: TimelineForPC

Treat this as a PC environment snapshot collector, not a normal file-input Timeline product.

Use this model:

```text
InputSource = local_pc / collector profile
Job         = PC snapshot request
Run         = one actual collection
Artifact    = PC environment report
```

Baseline output:

```text
data/output/runs/timeline-for-pc/
```

Security:

- do not collect secrets
- do not collect private keys
- avoid unnecessary absolute path exposure
- be careful with username, hostname, network information
- keep local-first
- keep mock mode working
- keep CLI-only; do not add Web UI
- keep snapshot / redaction / report / export contracts clear

Do not mix always-on screenshot/activity monitoring into this repository without explicit decision.

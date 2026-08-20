# SAST Analysis

## Tool

Semgrep

## Target

`src/`

## Recommended scan

```bash
semgrep scan --config auto src
```

## Save JSON output

```bash
mkdir -p sast/results
semgrep scan --config auto src --json > sast/results/semgrep.json
```

Do not commit `.venv/` or generated local database files.

# Runnable examples

`offline_manifest.json` is a safe plumbing example for the resumable batch
controller. It uses Inspect's mock model, so it requires no API key and produces no
behavior measurement.

Preview the exact commands without executing them:

```bash
python -m runner.batch examples/offline_manifest.json \
  --state logs/example_state.json --dry-run
```

To execute the two bounded smoke runs, omit `--dry-run`. The resulting state file is
local under `logs/` and ignored by Git. Do not export these mock outputs as benchmark
scores.

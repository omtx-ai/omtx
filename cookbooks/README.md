# Cookbooks

Cookbooks are high-value applied recipes. They assume the reader already knows
the basics and wants a focused way to accomplish a specific job.

Cookbooks may use the public `omtx` Python SDK, Om API, or `omtx` CLI, but
source code for those tools stays in `vibe-discovery`.

## Tracks

- Data access: build training-ready binder/non-binder datasets.
- Diligence: turn a question into a compact evidence briefing.
- Hub: run artifact-backed modeling workflows and retrieve outputs.
- CLI: inspect jobs and structures from a local command line.

## Planned Recipes

- `build-a-training-set.md`: load binders/non-binders and prepare a local
  training dataset.
- `diligence-briefing.md`: submit a diligence query and turn the job result into
  a short briefing.
- `hub-artifact-workflow.md`: upload a structure, launch a Hub job, and retrieve
  output artifacts.

## Rules

- Use synthetic or explicitly public data.
- Target `https://api.omtx.ai`.
- Keep secrets in environment variables only.
- Include idempotency keys for retryable POST examples.
- Strip notebook outputs before committing.

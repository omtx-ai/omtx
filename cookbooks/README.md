# Cookbooks

Cookbooks are applied recipes for completing specific OMTX tasks.

Cookbooks use the `omtx` Python SDK, Om API, or `omtx` CLI to complete practical
research and modeling tasks.

## Tracks

- Data access: build training-ready binder/non-binder datasets.
- Diligence: turn a question into a compact evidence briefing.
- Hub: run artifact-backed modeling workflows and retrieve outputs.
- CLI: inspect jobs and structures from a local command line.

## Recipes

- `build-a-training-set.md`: load binders/non-binders and prepare a local
  training dataset.
- `diligence-briefing.md`: submit a diligence query and turn the job result into
  a short briefing.
- `hub-artifact-workflow.md`: upload a structure, launch a Hub job, and retrieve
  output artifacts.

## Best Practices

- Use example inputs or data you have permission to access.
- Target `https://api.omtx.ai`.
- Keep secrets in environment variables only.
- Include idempotency keys for retryable POST examples.
- Keep generated outputs in your own working directory.

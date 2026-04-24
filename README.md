# omtx

Quick starts, tutorials, cookbooks, and runnable examples for using OMTX.

Use these guides to learn the Om API, work with the `omtx` Python SDK, run
data-access workflows, launch diligence jobs, and use Hub models and artifacts.

## Start Here

- [Quick Start](quick-start/README.md): first successful API, SDK, and CLI
  workflows.
- [Tutorials](tutorials/README.md): step-by-step walkthroughs for data access,
  diligence jobs, and Hub artifact jobs.
- [Cookbooks](cookbooks/README.md): applied recipes for common research and
  modeling tasks.
- [Examples](examples/python): runnable Python scripts.

## What You Can Do

- Query the Om API from curl, scripts, and notebooks.
- Install and use the `omtx` Python SDK.
- Load binder and non-binder datasets for accessible proteins.
- Submit diligence jobs and poll results.
- Upload artifacts, launch Hub jobs, and retrieve outputs.
- Use idempotency keys for safe retries.

## Prerequisites

- An OMTX API key.
- Python 3.9+ for SDK examples.
- `pip install omtx` for Python workflows.

Keep API keys in environment variables:

```bash
export OMTX_API_KEY="your-api-key"
```

## Choose A Path

- New to OMTX: start with [API Quickstart](quick-start/api.md) or
  [Python SDK Quickstart](quick-start/sdk.md).
- Loading datasets: follow
  [Data Access Python Workflows](tutorials/data-access-python-workflows.md), then
  use [Build A Training Set](cookbooks/build-a-training-set.md).
- Running diligence: follow [Diligence Jobs](tutorials/diligence-jobs.md), then
  use [Diligence Briefing](cookbooks/diligence-briefing.md).
- Running Hub jobs: follow
  [Hub Jobs And Artifacts](tutorials/hub-jobs-and-artifacts.md), then use
  [Hub Artifact Workflow](cookbooks/hub-artifact-workflow.md).

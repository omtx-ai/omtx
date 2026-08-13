# omtx

Quick starts, tutorials, cookbooks, and runnable examples for using OMTX.

Use these guides to learn the Om API, work with the `omtx` Python SDK, run
data-access workflows, launch diligence jobs, use Hub models and artifacts, and
run LULA scoring with hosted Om workflows or local open-weight models.

## Start Here

- [Quick Start](quick-start/README.md): first successful API, SDK, and CLI
  workflows.
- [Tutorials](tutorials/README.md): step-by-step walkthroughs for data access,
  diligence jobs, and Hub artifact jobs.
- [Cookbooks](cookbooks/README.md): applied recipes for common research and
  modeling tasks.
- [Examples](examples/python): runnable Python scripts.
- [Notebooks](examples/notebooks): Colab-friendly LULA workflow notebooks.

## What You Can Do

- Query the Om API from curl, scripts, and notebooks.
- Install and use the `omtx` Python SDK.
- Load binder and non-binder datasets for accessible proteins.
- Submit diligence jobs and poll results.
- Upload artifacts, launch Hub jobs, and retrieve outputs.
- Score protein sequences and SMILES with hosted LULA-1/LULA-2 or local
  open-weight LULA-1, LULA-1.1, and LULA-2.
- Fetch Om Accessible Space molecules by Wallet Credit tier, score them with
  your own tools or LULA, and create Wallet Credits-funded Molecule Fulfillment
  orders.
- Use idempotency keys for safe retries.

## Prerequisites

- An OMTX API key for API, hosted, and Hub workflows.
- Python 3.9+ for SDK examples.
- `pip install omtx` for Python workflows.
- `pip install "omtx[lula]>=2.0.20"` for local open-weight LULA scoring.

Keep API keys in environment variables:

```bash
export OMTX_API_KEY="your-api-key"
```

## Choose A Path

- New to OMTX: start with [API Quickstart](quick-start/api.md) or
  [Python SDK Quickstart](quick-start/sdk.md).
- LULA scoring: follow [LULA Quickstart](quick-start/lula.md), then use
  [LULA Score To Order](cookbooks/lula-score-to-order.md).
- Molecule selection without LULA: use
  [Molecule Accessible Space To Order](cookbooks/molecule-accessible-space-to-order.md).
- Colab users: open
  [LULA Om Accessible Space To Order](examples/notebooks/lula_om_space_to_order.ipynb)
  or [LULA Explicit SMILES](examples/notebooks/lula_explicit_smiles.ipynb).
- Loading datasets: follow
  [Data Access Python Workflows](tutorials/data-access-python-workflows.md), then
  use [Build A Training Set](cookbooks/build-a-training-set.md).
- Running diligence: follow [Diligence Jobs](tutorials/diligence-jobs.md), then
  use [Diligence Briefing](cookbooks/diligence-briefing.md).
- Running Hub jobs: follow
  [Hub Jobs And Artifacts](tutorials/hub-jobs-and-artifacts.md), then use
  [Hub Artifact Workflow](cookbooks/hub-artifact-workflow.md).

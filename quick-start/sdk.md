# Python SDK Quickstart

Use the `omtx` Python package to call the Om API from notebooks, scripts, and
training workflows.

## Install

```bash
pip install omtx
```

Set your API key before creating a client:

```bash
export OMTX_API_KEY="your-api-key"
```

The SDK targets `https://api.omtx.ai` by default.

## Basic Client

```python
from omtx import OmClient

with OmClient() as client:
    health = client.status()
    print("API version:", health.get("version"))

    catalog = client.datasets.catalog()
    print("Catalog keys:", sorted(catalog.keys()))
```

## Data Access

Use `protein_uuid` for data access. The API resolves the latest
accessible dataset snapshot server-side.

```python
from omtx import OmClient

with OmClient() as client:
    loaded = client.load_data(
        protein_uuid="0d64fb6a-8a66-50ad-82b6-fabee8bb1516",
        binders=1000,
        nonbinder_multiplier=5,
        sample_seed=42,
    )

    binders = loaded["binders"]
    nonbinders = loaded["nonbinders"]
    print(binders.shape, nonbinders.shape)
```

If you need separate pool control:

```python
binders = client.load_binders(
    protein_uuid="0d64fb6a-8a66-50ad-82b6-fabee8bb1516",
    n=1000,
    sample_seed=42,
)
nonbinders = client.load_nonbinders(
    protein_uuid="0d64fb6a-8a66-50ad-82b6-fabee8bb1516",
    n=5000,
    sample_seed=42,
)
```

Omit `n` or pass `n=None` to load the full pool.

## Diligence Job

```python
from omtx import OmClient

with OmClient() as client:
    job = client.diligence.search(
        query="BRAF inhibitor resistance mechanisms",
        idempotency_key="diligence-search-braf-demo-001",
    )

    result = client.jobs.wait(
        job["job_id"],
        poll_interval=5,
        timeout=1800,
    )
    print(result["status"])
```

For result-specific detail routes, `client.jobs.wait(...)` also supports a
`result_endpoint` template such as `/v2/jobs/deep-diligence/{job_id}`.

## Hub Job

For active Hub models, use `client.hub.submit(...)` or a typed helper when one
exists.

```python
from omtx import OmClient

with OmClient() as client:
    job = client.hub.submit(
        job_type="hub.boltz2",
        payload={
            "protein_sequence": "MSTNPKPQRKTKRNTNRRPQDVKFPGG",
            "ligand_smiles": "CCO",
        },
        idempotency_key="hub-boltz2-demo-001",
    )

    status = client.jobs.wait(job["job_id"], poll_interval=5, timeout=3600)
    print(status["status"])
```

For artifact-backed workflows, upload files first with `client.artifacts.*`.

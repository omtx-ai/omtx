# Python SDK Quickstart

Use the `omtx` Python package to call the Om API from notebooks, scripts, and
training workflows.

## Install

```bash
pip install omtx
```

For local open-weight LULA scoring:

```bash
pip install "omtx[lula]>=2.0.20"
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

## Local LULA-1

Local LULA-1 scoring uses public Hugging Face weights and does not require an
OMTX API key or Hugging Face login:

```bash
omtx lula download
omtx lula verify
```

Then score protein-sequence plus SMILES pairs with `omtx lula score` or
`from omtx.lula import load_model`.

See [Local LULA-1 Quickstart](lula.md) for the full workflow.

## LULA Score And Order

Hosted LULA can score explicit SMILES or orderable Om Accessible Space
molecules:

```python
from omtx import OmClient

with OmClient() as client:
    explicit = client.lula2.score(
        protein_sequence=protein_sequence,
        smiles=["CCO", "Cc1ccc(cc1)S(=O)(=O)N"],
        idempotency_key="explicit-smiles-demo-001",
    )

    orderable = client.lula2.score(
        protein_sequence=protein_sequence,
        source="om",
        tier=50,
        n=50000,
        top_k=10000,
        idempotency_key="om-space-demo-001",
    )
```

Use `smiles=[...]` to score molecules you already have. Use `source="om"` and a
tier to score orderable Om Accessible Space molecules. Only Om Accessible Space
score rows include `source_metadata` and can be ordered directly with Wallet
Credits.

See [LULA Score To Order](../cookbooks/lula-score-to-order.md) for the full
score-to-order workflow.

## Molecule Access Without LULA

Use Om Accessible Space directly when you want orderable molecules but want to
score, filter, or randomly select them yourself:

```python
from uuid import uuid4

from omtx import OmClient

with OmClient() as client:
    pool = client.molecules.accessible_space(
        tier=50,
        n=50000,
        seed=123,
        idempotency_key="om-space-slice-demo-001",
    )

    # smiles is a plain list[str], one SMILES per molecule.
    smiles = client.molecules.smiles(pool)

    # scores must be a same-length list[float], one score per SMILES.
    scores = score_with_your_model(smiles)

    # with_scores adds your scores back to the orderable Om rows.
    scored_rows = client.molecules.with_scores(pool, scores)

    selected = sorted(scored_rows, key=lambda row: row["score"], reverse=True)[:96]

    addresses = client.molecules.shipping_addresses()
    order = client.molecules.order(
        items=selected,
        shipping_address_id=addresses["default_shipping_address_id"],
        idempotency_key=f"molecule-order-{uuid4()}",
    )
```

`with_scores(...)` keeps the Om order metadata attached while adding your scores.
See
[Molecule Accessible Space To Order](../cookbooks/molecule-accessible-space-to-order.md)
for the full molecule-only workflow.

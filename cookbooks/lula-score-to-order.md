# LULA Score To Order

Use this recipe when you want to start from a protein sequence, score molecules
with LULA, and order selected hits through Om Molecule Fulfillment.

The same `omtx` SDK supports four common paths:

- hosted LULA scoring over explicit SMILES you already have
- hosted LULA-2 scoring over Om Accessible Space, then order selected rows
- local open-weight LULA scoring over an Om Accessible Space slice, then order
  selected rows
- local open-weight LULA scoring over explicit SMILES

## Prerequisites

- `pip install "omtx[lula]>=2.0.20"`
- `OMTX_API_KEY` set in your shell for hosted scoring, Om Accessible Space
  slices, Wallet Credits, and ordering
- a saved shipping address in your Om account
- enough Wallet Credits for the selected molecule tier

```bash
export OMTX_API_KEY="omtx_..."
```

## Runnable Examples

- [`examples/python/lula_hosted_score_smiles.py`](../examples/python/lula_hosted_score_smiles.py):
  hosted LULA-2 over an explicit SMILES list
- [`examples/python/lula_score_om_space_to_order.py`](../examples/python/lula_score_om_space_to_order.py):
  hosted LULA-2 over Om Accessible Space, with optional ordering
- [`examples/python/lula_explicit_smiles.py`](../examples/python/lula_explicit_smiles.py):
  local open-weight LULA over an explicit SMILES list
- [`examples/notebooks/lula_om_space_to_order.ipynb`](../examples/notebooks/lula_om_space_to_order.ipynb)
  and [`examples/notebooks/lula_explicit_smiles.ipynb`](../examples/notebooks/lula_explicit_smiles.ipynb):
  Colab-friendly versions

## Product Rule

```text
Use smiles=[...] to score molecules you already have.
Use source="om" and tier=50/100/150/... to score orderable Om Accessible Space molecules.
Only Om Accessible Space score rows include source_metadata and can be ordered directly with Wallet Credits.
```

## Hosted LULA Over Explicit SMILES

Use hosted async LULA when you want Om to run scoring infrastructure for a SMILES
list you already have.

```python
from pathlib import Path

import polars as pl
from omtx import OmClient

def score_column(frame: pl.DataFrame) -> str:
    for column in ("score", "lula2_score", "lula1_crossattention_v1_score"):
        if column in frame.columns:
            return column
    for column in frame.columns:
        if column.endswith("_score"):
            return column
    raise ValueError(f"No score column found. Columns: {frame.columns}")

protein_sequence = "YOUR_PROTEIN_SEQUENCE"
smiles = [
    "CCOc1ccc2nc(S(N)(=O)=O)sc2c1",
    "Cn1ccnc1CCNCc1cn(-c2ccc(F)c(Cl)c2)nn1",
    "CCO",
]

with OmClient() as client:
    job = client.lula2.score(
        protein_sequence=protein_sequence,
        smiles=smiles,
        threshold=1.0,
        top_k=len(smiles),
        idempotency_key="explicit-smiles-lula2-demo-001",
    )

    result_dir = Path("outputs/explicit-smiles-lula2")
    artifact_paths = []
    for job_id in job["job_ids"]:
        client.jobs.wait(job_id, poll_interval=5, timeout=3600)
        artifact_paths.extend(
            Path(path)
            for path in client.jobs.download_all_artifacts(
                job_id, output_dir=result_dir / job_id, overwrite=True
            )
        )

score_tables = [
    pl.read_parquet(path)
    for path in artifact_paths
    if path.suffix == ".parquet"
]
score_rows = pl.concat(score_tables)
score_rows = score_rows.sort(score_column(score_rows), descending=True)
```

These rows are score-only by default. They do not carry Om Accessible Space
`source_metadata`, so they cannot be passed directly to
`client.molecules.order(...)`.

## Hosted LULA-2 Over Om Accessible Space

Use hosted scoring when you want Om to run the score job and return ranked
artifacts.

```python
from pathlib import Path
from uuid import uuid4

import polars as pl
from omtx import OmClient

def score_column(frame: pl.DataFrame) -> str:
    for column in ("score", "lula2_score", "lula1_crossattention_v1_score"):
        if column in frame.columns:
            return column
    for column in frame.columns:
        if column.endswith("_score"):
            return column
    raise ValueError(f"No score column found. Columns: {frame.columns}")

protein_sequence = "YOUR_PROTEIN_SEQUENCE"

with OmClient() as client:
    job = client.lula2.score(
        protein_sequence=protein_sequence,
        source="om",
        tier=50,
        n=50_000,
        top_k=10_000,
        idempotency_key=f"lula2-om-space-{uuid4()}",
    )

    result_dir = Path("outputs/lula2-om-space")
    artifact_paths = []
    for job_id in job["job_ids"]:
        client.jobs.wait(job_id, poll_interval=5, timeout=3600)
        artifact_paths.extend(
            Path(path)
            for path in client.jobs.download_all_artifacts(
                job_id, output_dir=result_dir / job_id, overwrite=True
            )
        )

score_tables = [
    pl.read_parquet(path)
    for path in artifact_paths
    if path.suffix == ".parquet"
]
score_rows = pl.concat(score_tables)
score_rows = score_rows.sort(score_column(score_rows), descending=True)
selected_hits = score_rows.head(100).to_dicts()
```

Rows scored from Om Accessible Space include the `source_metadata` Om needs to
validate fixed Wallet Credit cost and route fulfillment internally.

## Order Selected Hits

```python
from uuid import uuid4

from omtx import OmClient

with OmClient() as client:
    addresses = client.molecules.shipping_addresses()
    shipping_address_id = addresses["default_shipping_address_id"]

    order = client.molecules.order(
        items=selected_hits,
        shipping_address_id=shipping_address_id,
        idempotency_key=f"molecule-order-{uuid4()}",
    )

print(order["order_number"])
```

Customers do not choose the upstream vendor for Om Accessible Space rows. Om
handles procurement routing after the Wallet Credits-funded order is placed.

## Local Open-Weight Scoring Over Om Accessible Space

Use this path when you want the protein sequence and model scores to stay local,
while still using Om to retrieve an orderable molecule slice.

```python
from omtx import OmClient
from omtx.lula import load_model

protein_sequence = "YOUR_PROTEIN_SEQUENCE"

with OmClient() as client:
    model = load_model("lula1.1")
    scores = model.score(
        protein_sequence=protein_sequence,
        source="om",
        tier=50,
        n=50_000,
        client=client,
    )

selected_hits = sorted(scores, key=lambda row: row["score"], reverse=True)[:100]
```

The Om slice request sends only `source`, `tier`, and `n`; the local scoring
path does not send your protein sequence or local scores to Om.

## Explicit SMILES

If you already have a SMILES list, score it directly with local open-weight
LULA. This does not require Om and does not send the protein sequence or SMILES
to Om.

```python
from omtx.lula import load_model

protein_sequence = "YOUR_PROTEIN_SEQUENCE"
smiles = ["CCO", "c1ccccc1", "CC(=O)Nc1nnc(s1)S(N)(=O)=O"]

model = load_model("lula1.1")
rows = model.score(protein_sequence=protein_sequence, smiles=smiles)
for row in sorted(rows, key=lambda item: item["rank"]):
    print(row["rank"], f"{row['score']:.6f}", row["smiles"])
```

For ordering, use Om Accessible Space. Arbitrary explicit SMILES score rows are
ranking outputs unless you separately establish orderability through a supported
Molecule Fulfillment path.

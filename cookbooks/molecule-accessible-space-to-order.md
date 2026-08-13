# Molecule Accessible Space To Order

Use this recipe when you want orderable Om molecules but do not want Om or LULA
to score them. You fetch a fixed Wallet Credit tier, score or filter the rows
with your own tools, then order selected rows through Om Molecule Fulfillment.

## Prerequisites

- `pip install "omtx>=2.0.23"`
- `OMTX_API_KEY` set in your shell
- a saved shipping address in your Om account
- enough Wallet Credits for the selected molecule tier

```bash
export OMTX_API_KEY="omtx_..."
```

## Product Rule

```text
Fetch Om Accessible Space rows with client.molecules.accessible_space(...).
Get plain SMILES with client.molecules.smiles(...).
Score, rank, filter, or randomly select SMILES however you want.
Attach scores with client.molecules.with_scores(...).
Order selected rows with client.molecules.order(...).
```

Customers do not choose upstream vendors. Om uses the returned
order metadata to revalidate the catalog row, settle Wallet Credits, and route
fulfillment internally after the order is placed.

## Fetch Orderable Molecules

```python
from omtx import OmClient

with OmClient() as client:
    pool = client.molecules.accessible_space(
        tier=50,
        n=50_000,
        seed=123,
        idempotency_key="target-a-om-space-slice-1",
    )

    # smiles is a plain list[str], one SMILES per molecule.
    smiles = client.molecules.smiles(pool)
```

`accessible_space(...)` returns unscored orderable molecules. `smiles(...)`
gives you the plain SMILES list to pass to your model.

## Score Or Select Locally

Replace this placeholder with your own model, assay-prioritization logic, or
manual selection.

```python
# scores must be a same-length list[float], one score per SMILES.
scores = score_with_your_model(smiles)

# with_scores adds your scores back to the orderable Om rows.
scored_rows = client.molecules.with_scores(pool, scores)

selected_hits = sorted(
    scored_rows,
    key=lambda row: row["score"],
    reverse=True,
)[:96]
```

`with_scores(...)` copies the original Om rows and adds your scores, so selected
rows remain orderable without you manually handling Om metadata.

## Fetch Many Random Batches

For larger random screens, repeat the same call with a different seed. Each
response is just one batch, so process it before requesting the next batch.

```python
from omtx import OmClient

with OmClient() as client:
    for seed in range(20_000):
        pool = client.molecules.accessible_space(
            tier=50,
            n=50_000,
            seed=seed,
            idempotency_key=f"om-50-random-{seed}",
        )

        # smiles is a plain list[str], one SMILES per molecule.
        smiles = client.molecules.smiles(pool)

        # scores must be a same-length list[float], one score per SMILES.
        scores = score_with_your_model(smiles)

        # with_scores adds your scores back to the orderable Om rows.
        scored_rows = client.molecules.with_scores(pool, scores)
        save_batch_scores(seed, scored_rows)
```

That loop requests `20_000 * 50_000 = 1_000_000_000` random molecule rows. The
SDK does not keep prior batches in memory.

If you want to persist each batch as Parquet, use Polars batch-by-batch and
store `source_metadata` as JSON so selected rows can be rehydrated before
ordering:

```python
import json
from pathlib import Path

import polars as pl
from omtx import OmClient

out_dir = Path("om-random-slices")
out_dir.mkdir(exist_ok=True)

with OmClient() as client:
    for seed in range(3):
        pool = client.molecules.accessible_space(
            tier=50,
            n=50_000,
            seed=seed,
            idempotency_key=f"om-50-random-{seed}",
        )

        # smiles is a plain list[str], one SMILES per molecule.
        smiles = client.molecules.smiles(pool)

        # scores must be a same-length list[float], one score per SMILES.
        scores = score_with_your_model(smiles)

        # with_scores adds your scores back to the orderable Om rows.
        scored_rows = client.molecules.with_scores(pool, scores)
        rows = [
            {
                **{key: value for key, value in row.items() if key != "source_metadata"},
                "wallet_credits": row["source_metadata"].get("customer_wallet_credits"),
                "source_metadata_json": json.dumps(row["source_metadata"]),
            }
            for row in scored_rows
        ]
        pl.DataFrame(rows).write_parquet(out_dir / f"seed={seed}.parquet")
```

For billion-row jobs, do not collect all rows in memory. Either write every
scored row as partitioned Parquet, or more commonly write only the top hits from
each 50K batch. Then select the global top hits from disk.

With Polars lazy scanning:

```python
import json

import polars as pl

top_hits = (
    pl.scan_parquet("om-random-slices/*.parquet")
    .top_k(96, by="score")
    .collect()
    .to_dicts()
)

selected_hits = [
    {
        **{key: value for key, value in row.items() if key != "source_metadata_json"},
        "source_metadata": json.loads(row["source_metadata_json"]),
    }
    for row in top_hits
]
```

With DuckDB SQL:

```python
import json

import duckdb

columns = [
    "smiles",
    "canonical_smiles",
    "score",
    "wallet_credits",
    "source_metadata_json",
]
rows = duckdb.sql(
    """
    SELECT smiles, canonical_smiles, score, wallet_credits, source_metadata_json
    FROM read_parquet('om-random-slices/*.parquet')
    ORDER BY score DESC
    LIMIT 96
    """
).fetchall()
top_hits = [dict(zip(columns, row)) for row in rows]
selected_hits = [
    {
        **{key: value for key, value in row.items() if key != "source_metadata_json"},
        "source_metadata": json.loads(row["source_metadata_json"]),
    }
    for row in top_hits
]
```

DuckDB is optional:

```bash
pip install duckdb
```

Use `with_scores(...)` before ordering scored rows. If you build new rows from
only SMILES and scores, Om cannot treat them as fixed-price Accessible Space
order items.

## Order Selected Rows

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

## Runnable Example

Use the dry-run example before placing an order:

```bash
python examples/python/molecule_accessible_space_to_order.py \
  --tier 50 \
  --n 100 \
  --select 10 \
  --seed 123
```

Fetch three random batches and write selected rows to one Parquet file per
batch:

```bash
python examples/python/molecule_accessible_space_to_order.py \
  --tier 50 \
  --n 100 \
  --select 10 \
  --seed 123 \
  --batches 3 \
  --out-dir om-random-slices
```

Add `--place-order` only when you are ready to spend Wallet Credits.

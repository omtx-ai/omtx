# Data Access Python Workflows

Use the Python SDK when you want binder and non-binder data in notebooks,
scripts, or training workflows.

## Contract

- Public data-access requests use `protein_uuid`.
- The Om API resolves the latest accessible dataset snapshot server-side.
- Customers do not select `vintage_number` for public shard access.
- Entitlement is enforced by the API. Missing access can return `402`.
- SDK sampling happens after shard URLs are retrieved.

## Recommended: Paired Training Load

```python
from omtx import OmClient

with OmClient() as client:
    loaded = client.load_data(
        protein_uuid="0d64fb6a-8a66-50ad-82b6-fabee8bb1516",
        binders=50000,
        nonbinder_multiplier=5,
        sample_seed=42,
    )

    binders = loaded["binders"]
    nonbinders = loaded["nonbinders"]
    print(binders.shape, nonbinders.shape)
```

`binders` is required. If `nonbinders` is omitted, the SDK uses
`binders * nonbinder_multiplier`.

## Explicit Per-Pool Loading

```python
from omtx import OmClient

with OmClient() as client:
    binders = client.load_binders(
        protein_uuid="0d64fb6a-8a66-50ad-82b6-fabee8bb1516",
        n=1000,
        sample_seed=42,
    )
    nonbinders = client.load_nonbinders(
        protein_uuid="0d64fb6a-8a66-50ad-82b6-fabee8bb1516",
        n=10000,
        sample_seed=42,
    )

    print(binders.shape, nonbinders.shape)
```

Omit `n` or pass `n=None` to load the full pool.

## Raw Shard URLs

Use raw URLs only when you need custom orchestration.

```python
from omtx import OmClient

with OmClient() as client:
    urls = client.binders.urls(
        protein_uuid="0d64fb6a-8a66-50ad-82b6-fabee8bb1516",
        idempotency_key="data-access-urls-demo-001",
    )

    print("Binder shards:", len(urls["binder_urls"]))
    print("Non-binder shards:", len(urls["non_binder_urls"]))
```

## Molecule Preview

`OmData.show(...)` renders molecule previews when notebook display and RDKit are
available.

```python
binders.show(top_n=24)
binders.show(top_n=24, sort_by="selectivity_score")
```

Defaults are strict: `smiles` and `binding_score`. Pass an exact existing
column name to `sort_by`.

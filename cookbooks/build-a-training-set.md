# Build A Training Set

Use this recipe when you want a local binder/non-binder dataset for exploratory
modeling or downstream training.

## Prerequisites

- `pip install omtx`
- `OMTX_API_KEY` set in your shell
- Access to the target `protein_uuid`

## Recipe

```python
from omtx import OmClient

protein_uuid = "0d64fb6a-8a66-50ad-82b6-fabee8bb1516"

with OmClient() as client:
    loaded = client.load_data(
        protein_uuid=protein_uuid,
        binders=50000,
        nonbinder_multiplier=5,
        sample_seed=42,
        include_metadata=True,
    )

binders = loaded["binders"]
nonbinders = loaded["nonbinders"]
metadata = loaded["metadata"]

print("Binder rows:", binders.shape)
print("Non-binder rows:", nonbinders.shape)
print("Dataset:", metadata["export"].get("dataset_id"))
```

## Notes

- Use `client.load_data(...)` for paired training pools.
- Use `client.load_binders(...)` and `client.load_nonbinders(...)` when pool
  sizes need to be controlled separately.
- Omit `n` or pass `n=None` to load a full pool.
- Data access is entitlement-gated; missing access can return `402`.

## Next Steps

- Inspect columns with `binders.columns`.
- Preview molecules with `binders.show(top_n=24)`.
- Save local derived files outside git-tracked paths.

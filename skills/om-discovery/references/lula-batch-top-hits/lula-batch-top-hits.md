# Merging top hits across a multi-job LULA-2 batch

A LULA-2 scoring request that exceeds one shard's molecule capacity does not
come back as a single job. The gateway fans it out into many independent
jobs that share one `metadata.batch_id`. Every per-job tool — `jobs_status`,
`jobs_get_top_scored_molecules`, `jobs_export_json` — is scoped to exactly
one job_id. None of them verify sibling completion or compute a batch-wide
winner; `jobs_get_top_scored_molecules`'s own description says so directly.

If you need "the top hit" (or a ranked export) for a batch like that, do not
call a ranking tool once per job_id inside this conversation. With dozens or
hundreds of shard jobs that is dozens or hundreds of tool round-trips, each
one dumping its full response into the conversation — this is the exact
failure mode that has crashed agent sessions doing this by hand.

## Why the merge is cheap even though the batch is large

Every completed shard job already writes a small, pre-ranked
`accessible_space/top_hits.parquet` — its own locally-ranked retained hits,
already sorted by score — alongside the much larger raw
`accessible_space/scored_shards/*.parquet` score table. Merging a batch's
top hits means downloading the small, already-sorted file from each shard
and doing one final sort. Nothing needs to be re-ranked from scratch.

## Run it as a script, not as tool calls in chat

Use [`examples/python/lula_batch_top_hits.py`](../../../examples/python/lula_batch_top_hits.py).
It requires `pip install omtx polars` and `OMTX_API_KEY` set to the batch
owner's own key (never a different account's key — the script, like every
job tool, can only see jobs the key's account owns).

```bash
export OMTX_API_KEY="your-api-key"
python examples/python/lula_batch_top_hits.py --batch-id <batch_id> --top-n 50
```

If the `batch_id` is not known, omit `--batch-id` and the script lists the
distinct batch IDs found in recent job history (with job count, status
breakdown, and a human-readable label) to pick from.

The script:

1. Pages `jobs.history()` to find every job_id sharing the target
   `batch_id` via each job's own `metadata`.
2. Reads the shared score column name from one shard's small
   `scored_shards_manifest.json`.
3. Downloads every completed shard's `top_hits.parquet` concurrently via
   `jobs.get_artifact_url()`.
4. Concatenates, re-sorts locally, and writes one merged top-N CSV.

Report back to the user only the printed summary (shards merged, candidate
rows, top score, output file path) — not the raw per-shard tool responses
that produced it.

## Known limitation — read before calling a merged top-N "the" global winner

Each shard's `top_hits.parquet` only contains that shard's retained
fraction, set at launch by `threshold` (default 0.3 = top 30% of that shard)
and capped by `top_k`. `lula2_score`'s own description warns that "a
retained-file merge may omit global winners." This merge is exact only if
every shard retained at least as many rows as the top-N you asked for. The
script reports each shard's retained row count and warns explicitly when any
shard retained fewer rows than the requested `--top-n` — read that warning
before presenting a merged result as a certified global ranking rather than
a best-effort one.

# Merging top hits across a multi-job LULA-2 batch

For a batch-wide top N, use the completed jobs' existing ranked results and
keep a running top N. Do not make rescoring, full-catalog identity reconciliation,
or chemical pool design prerequisites for a request for ranked hits.

`jobs_get_top_scored_molecules` ranks one `job_id`; it does not combine sibling
jobs. The batch workflow combines those per-job results programmatically.
For large batches, keep the rows outside the conversation and return a bounded
summary plus a ranked artifact. Use approved cloud compute for bulk data when
the workspace requires it; do not relay bulk results through the workstation.

## Recover the batch and check coverage

Reuse the original launch response or saved job manifest when available. A
fan-out batch has independent jobs with one batch identity. The published
`accessible_space/scored_shards_manifest.json` records `batch_id`, `job_index`,
`job_count`, and `total_molecules`; history metadata alone is not a reliable
membership source.

Before calling the result complete, account for every expected job index,
confirm success, and verify that the jobs are comparable slices of the same
protein/model run with consistent score semantics. Do not merge unrelated
targets, checkpoints, or runs merely because their outputs have a `score` column.
Report missing, failed, or unreadable jobs as incomplete coverage.

## Keep a running top N

1. Get each job's highest N valid rows, or all its valid rows if it has fewer
   than N. Prefer the already-published `accessible_space/top_hits.parquet`
   when its retention is sufficient. Om MCP supplies job metadata and signed
   artifact links; the same owner's SDK can retrieve those artifacts too.
2. Merge that candidate set with the running best set, sort by full-precision
   score descending and a consistent deterministic tie-break, and keep N rows.
3. Repeat for every job. Save the ranked result with source job and molecule
   identity, catalog/order metadata, and the completed-job denominator.

This is the same ranking as sorting the complete union: a row below rank N
in its own job already has N rows ahead of it and cannot enter the global top N.
The running set needs only N rows; no full score-matrix download is necessary
when the retained candidates are sufficient. Exclude missing/non-finite scores
and report their counts. Define whether N means rows or unique molecules;
deduplication must precede the relevant truncation when unique molecules are
requested, or deeper candidates may be needed.

`top_n` sets the per-job ranking size. `return_rows_limit` only caps the inline
preview; it does not change that ranking size or provide pagination. A small
preview or a score cutoff is not the complete candidate set for the merge.
Prefer published files for bulk results, rather than placing thousands of rows
from every job into the chat.

## Existing SDK helper

Use [`examples/python/lula_batch_top_hits.py`](../../../../examples/python/lula_batch_top_hits.py)
with `omtx`, `polars`, and `requests` installed. It uses the batch owner's own
`OMTX_API_KEY`; never substitute an administrator's or another account's key.
MCP access uses the existing OAuth connection and does not require replacing
it with an API key.

```bash
python examples/python/lula_batch_top_hits.py --batch-id <batch_id> --top-n 10000
```

Replace `<batch_id>` with the original launch response's batch ID. Omitting it
lists batches discovered from recent job history and their published manifests.
Use the SDK's configured endpoint for the batch's environment.

The current helper discovers jobs, reports completion/retention gaps, fetches
their retained top-hit files, concatenates and sorts them, and writes a top-N
CSV. That produces the same ranking as the rolling merge but retains all
candidate frames in memory; do not describe it as a bounded-memory implementation.
Report its summary and output path, not its raw per-job responses.

## When the retained files are insufficient

Retention is set by the scoring request's `threshold` and `top_k`. A sufficient
condition for an exact top N is that every job retained at least
`min(N, that job's valid scored-row count)` highest rows, with compatible
tie-breaking. A small final shard containing fewer than N total valid rows is
complete if all of them are present. Check actual retention and coverage before
claiming an exact global ranking; a helper warning is not a completion proof.

If retention is insufficient, retrieve deeper ranked results or the existing
full-score artifacts only for the affected jobs through the authorized path.
Do not silently certify the retained subset or launch new scoring.

For a constrained selection (supplier eligibility, previous-screen exclusions,
diversity, or AS-MS mass separation), a raw top N may not contain enough eligible
or compatible compounds. Apply row-level eligibility before truncating where
supported, or expand candidates until the requested selection has adequate
coverage. Pool admission and its validation are subsequent work; do not call a
top-hit export an exhaustive whole-catalog or validated pool analysis.

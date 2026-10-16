"""Merge pre-ranked top_hits.parquet files across every job in one LULA-2 batch.

A LULA-2 scoring request that exceeds one shard's molecule capacity fans out
into many independent jobs. No per-job tool (status, top-scored-molecules,
export) computes a batch-wide winner, so getting "the top hit" for a batch
means merging each shard's own ranked result yourself. Do this with a
script, not by calling a ranking tool once per job_id in an agent
conversation -- with dozens or hundreds of shards that floods the
conversation and can stall the session. See
skills/om-discovery/references/lula-batch-top-hits/lula-batch-top-hits.md
for the full explanation.

/v2/jobs/history's own `metadata` field does not carry a batch_id -- that is
only returned once, in the original launch response. Each shard job's own
accessible_space/scored_shards_manifest.json records its batch identity
directly instead (batch_id, job_index, job_count, total_molecules), so this
script reads batch membership from there.

Every completed shard job already writes a small, pre-ranked
accessible_space/top_hits.parquet (its own locally-ranked retained hits,
already sorted by score) alongside the much larger raw
accessible_space/scored_shards/*.parquet table. This script downloads only
the small, already-ranked file from each shard and does one final sort --
nothing is re-ranked from scratch.

Install first:
    pip install omtx polars requests

Set your own API key (this can only see jobs your own account owns):
    export OMTX_API_KEY="your-api-key"

Usage:
    # Don't know the batch_id? List recent batches:
    python lula_batch_top_hits.py

    # Merge a known batch's top hits:
    python lula_batch_top_hits.py --batch-id <batch_id> --top-n 50
"""

from __future__ import annotations

import argparse
import io
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import polars as pl
import requests

from omtx import OmClient

TOP_HITS_ARTIFACT = "accessible_space/top_hits.parquet"
MANIFEST_ARTIFACT = "accessible_space/scored_shards_manifest.json"
HISTORY_PAGE_LIMIT = 100
MAX_DOWNLOAD_CONCURRENCY = 8
# The job-level lifecycle status (NOT the manifest's own internal "status"
# field, which records something different and is commonly "completed").
JOB_STATUS_SUCCEEDED = "succeeded"


def fetch_history(client: OmClient, max_pages: int) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    cursor = None
    for _ in range(max_pages):
        page = client.jobs.history(limit=HISTORY_PAGE_LIMIT, cursor=cursor)
        items = page.get("items") or []
        jobs.extend(items)
        cursor = page.get("next_cursor")
        if not cursor or not items:
            break
    return jobs


def fetch_manifest(client: OmClient, job_id: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        info = client.jobs.get_artifact_url(job_id, MANIFEST_ARTIFACT)
        content = requests.get(info["download_url"], timeout=60).content
        return json.loads(content), None
    except Exception as exc:  # noqa: BLE001 - report, don't crash the whole scan
        return None, f"{job_id}: {exc}"


def group_by_batch(
    client: OmClient, jobs: list[dict[str, Any]]
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]], list[str]]:
    """Group lula2.score jobs by batch_id, read from each job's own manifest.

    /v2/jobs/history's `metadata` does not carry a batch_id (that is only
    returned once, in the original launch response), so this fetches each
    candidate job's small scored_shards_manifest.json and reads batch_id,
    job_count and total_molecules from its `batch` object instead.

    Returns (batches, batch_info_by_id, manifest_fetch_errors).
    """
    candidates = [j for j in jobs if j.get("job_type") == "lula2.score"]
    batches: dict[str, list[dict[str, Any]]] = defaultdict(list)
    batch_info: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_CONCURRENCY) as pool:
        futures = {
            pool.submit(fetch_manifest, client, j["job_id"]): j for j in candidates
        }
        for future in as_completed(futures):
            job = futures[future]
            manifest, error = future.result()
            if error:
                errors.append(error)
                continue
            batch = (manifest or {}).get("batch") or {}
            batch_id = batch.get("batch_id")
            if not batch_id:
                continue
            batches[batch_id].append(job)
            batch_info.setdefault(
                batch_id,
                {
                    "job_count": batch.get("job_count"),
                    "total_molecules": batch.get("total_molecules"),
                },
            )
    return batches, batch_info, errors


def print_batch_list(client: OmClient, history_pages: int) -> None:
    jobs = fetch_history(client, history_pages)
    batches, batch_info, errors = group_by_batch(client, jobs)
    if errors:
        print(f"{len(errors)} job(s) failed a manifest lookup while scanning:")
        for e in errors[:10]:
            print(f"    {e}")
        if len(errors) > 10:
            print(f"    ... and {len(errors) - 10} more")
    if not batches:
        print("No LULA-2 batches found in the scanned history window.")
        return
    print(f"Recent LULA-2 batches found in the last {history_pages} history page(s):\n")
    rows = []
    for batch_id, items in batches.items():
        job_names = sorted({j.get("job_name") or "" for j in items if j.get("job_name")})
        label = job_names[0].split(" [")[0] if job_names else ""
        statuses: dict[str, int] = defaultdict(int)
        for j in items:
            statuses[j.get("status") or "unknown"] += 1
        expected_job_count = batch_info.get(batch_id, {}).get("job_count")
        rows.append(
            {
                "batch_id": batch_id,
                "label": label,
                "job_count": len(items),
                "expected_job_count": expected_job_count,
                "statuses": dict(statuses),
                "most_recent": max((j.get("created_at") or "" for j in items), default=""),
            }
        )
    rows.sort(key=lambda r: r["most_recent"], reverse=True)
    for row in rows:
        coverage = (
            f"{row['job_count']}/{row['expected_job_count']}"
            if row["expected_job_count"]
            else str(row["job_count"])
        )
        print(
            f"  batch_id={row['batch_id']}  jobs_found={coverage}  "
            f"statuses={row['statuses']}  label={row['label']!r}  "
            f"most_recent={row['most_recent']}"
        )
    print("\nRe-run with --batch-id <one of the above>.")


def fetch_score_column(client: OmClient, job_id: str) -> str:
    manifest, error = fetch_manifest(client, job_id)
    if error or not manifest:
        raise RuntimeError(f"Could not fetch manifest for job {job_id}: {error}")
    score_column = manifest.get("score_column")
    if not score_column:
        raise RuntimeError(f"No score_column in manifest for job {job_id}")
    return str(score_column)


def fetch_top_hits(client: OmClient, job: dict[str, Any]) -> tuple[pl.DataFrame | None, str | None]:
    job_id = job["job_id"]
    try:
        info = client.jobs.get_artifact_url(job_id, TOP_HITS_ARTIFACT)
        content = requests.get(info["download_url"], timeout=60).content
        frame = pl.read_parquet(io.BytesIO(content))
        if "source_metadata" in frame.columns:
            # source_metadata is a nested struct; CSV cannot hold it directly.
            frame = frame.with_columns(
                pl.col("source_metadata").struct.json_encode().alias("source_metadata")
            )
        frame = frame.with_columns(pl.lit(job_id).alias("_source_job_id"))
        return frame, None
    except Exception as exc:  # noqa: BLE001 - report, don't crash the whole merge
        return None, f"{job_id}: {exc}"


def merge_batch(client: OmClient, batch_id: str, top_n: int, history_pages: int, out_dir: str) -> None:
    batches, batch_info, manifest_errors = group_by_batch(
        client, fetch_history(client, history_pages)
    )
    jobs = batches.get(batch_id, [])
    if not jobs:
        raise SystemExit(
            f"No jobs found for batch_id={batch_id} in the scanned history window. "
            "Try a larger --history-pages, or confirm the batch_id."
        )
    if manifest_errors:
        print(
            f"Note: {len(manifest_errors)} other job(s) in the scanned window failed "
            "a manifest lookup during batch discovery and could not be checked for "
            "membership in this batch -- if this batch looks incomplete, one of these "
            "may actually belong to it:"
        )
        for e in manifest_errors[:10]:
            print(f"    {e}")
        if len(manifest_errors) > 10:
            print(f"    ... and {len(manifest_errors) - 10} more")

    expected_job_count = batch_info.get(batch_id, {}).get("job_count")
    completed = [j for j in jobs if (j.get("status") or "").lower() == JOB_STATUS_SUCCEEDED]
    incomplete = [j for j in jobs if (j.get("status") or "").lower() != JOB_STATUS_SUCCEEDED]
    print(
        f"Batch {batch_id}: {len(jobs)} jobs found, {len(completed)} succeeded, "
        f"{len(incomplete)} not succeeded."
    )
    if expected_job_count and len(jobs) != expected_job_count:
        print(
            f"WARNING: this batch expects {expected_job_count} total jobs (per its own "
            f"manifest), but only {len(jobs)} were found in the scanned "
            f"--history-pages window. This merge covers an INCOMPLETE batch -- increase "
            f"--history-pages, or confirm no shard jobs were deleted/excluded."
        )
    if incomplete:
        print(
            "  Excluded from merge (not succeeded): "
            + ", ".join(f"{j['job_id']}={j.get('status')}" for j in incomplete)
        )
    if not completed:
        raise SystemExit("No succeeded jobs to merge.")

    score_column = fetch_score_column(client, completed[0]["job_id"])
    print(f"Score column (from scored_shards_manifest.json): {score_column}")

    frames: list[pl.DataFrame] = []
    shard_counts: dict[str, int] = {}
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_CONCURRENCY) as pool:
        futures = {pool.submit(fetch_top_hits, client, job): job for job in completed}
        for future in as_completed(futures):
            job = futures[future]
            frame, error = future.result()
            if frame is not None:
                frames.append(frame)
                shard_counts[job["job_id"]] = frame.height
            if error:
                errors.append(error)

    if errors:
        print(f"  {len(errors)} shard(s) failed to fetch top_hits.parquet:")
        for e in errors:
            print(f"    {e}")
    if not frames:
        raise SystemExit("No top_hits.parquet could be fetched for any completed job.")

    merged = pl.concat(frames, how="diagonal_relaxed")
    ranked = merged.sort(score_column, descending=True).head(top_n)

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    out_path = Path(out_dir) / f"{batch_id}-top{top_n}.csv"
    ranked.drop("_source_job_id").write_csv(out_path)

    min_shard_retained = min(shard_counts.values()) if shard_counts else 0
    print(
        f"\nMerged {len(frames)}/{len(completed)} shard top_hits files, "
        f"{merged.height} candidate rows total."
    )
    print(f"Wrote top {ranked.height} ranked rows to {out_path}")
    if ranked.height:
        print(
            f"Top score: {ranked[score_column][0]}  /  "
            f"rank-{ranked.height} score: {ranked[score_column][-1]}"
        )
    print(f"Smallest per-shard retained count: {min_shard_retained}")
    if min_shard_retained < top_n:
        print(
            f"\nWARNING: at least one shard retained fewer rows ({min_shard_retained}) "
            f"than the requested top_n ({top_n}). This merge is NOT guaranteed to be "
            f"the certified global top-{top_n} -- see the 'Known limitation' section "
            f"in lula-batch-top-hits.md."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-id", default=None)
    parser.add_argument("--top-n", type=int, default=50)
    parser.add_argument("--out", default="outputs/lula-batch-top-hits")
    parser.add_argument(
        "--history-pages",
        type=int,
        default=20,
        help="max jobs.history() pages to scan (100 jobs/page)",
    )
    args = parser.parse_args()

    with OmClient() as client:
        if not args.batch_id:
            print_batch_list(client, args.history_pages)
            return
        merge_batch(client, args.batch_id, args.top_n, args.history_pages, args.out)


if __name__ == "__main__":
    main()

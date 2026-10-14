"""Merge pre-ranked top_hits.parquet files across every job in one LULA-2 batch.

A LULA-2 scoring request that exceeds one shard's molecule capacity fans out
into many independent jobs that share one `metadata.batch_id`. No per-job
tool (status, top-scored-molecules, export) computes a batch-wide winner, so
getting "the top hit" for a batch means merging each shard's own ranked
result yourself. Do this with a script, not by calling a ranking tool once
per job_id in an agent conversation -- with dozens or hundreds of shards that
floods the conversation and can stall the session. See
skills/om-discovery/references/lula-batch-top-hits/lula-batch-top-hits.md
for the full explanation.

Every completed shard job already writes a small, pre-ranked
accessible_space/top_hits.parquet (its own locally-ranked retained hits,
already sorted by score) alongside the much larger raw
accessible_space/scored_shards/*.parquet table. This script downloads only
the small, already-ranked file from each shard and does one final sort --
nothing is re-ranked from scratch.

Install first:
    pip install omtx polars

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

from omtx import OmClient

TOP_HITS_ARTIFACT = "accessible_space/top_hits.parquet"
MANIFEST_ARTIFACT = "accessible_space/scored_shards_manifest.json"
HISTORY_PAGE_LIMIT = 100
MAX_DOWNLOAD_CONCURRENCY = 8


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


def group_by_batch(jobs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    batches: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for job in jobs:
        if job.get("job_type") != "lula2.score":
            continue
        metadata = job.get("metadata") or {}
        batch_id = metadata.get("batch_id")
        if batch_id:
            batches[batch_id].append(job)
    return batches


def print_batch_list(client: OmClient, history_pages: int) -> None:
    jobs = fetch_history(client, history_pages)
    batches = group_by_batch(jobs)
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
        rows.append(
            {
                "batch_id": batch_id,
                "label": label,
                "job_count": len(items),
                "statuses": dict(statuses),
                "most_recent": max((j.get("created_at") or "" for j in items), default=""),
            }
        )
    rows.sort(key=lambda r: r["most_recent"], reverse=True)
    for row in rows:
        print(
            f"  batch_id={row['batch_id']}  jobs={row['job_count']}  "
            f"statuses={row['statuses']}  label={row['label']!r}  "
            f"most_recent={row['most_recent']}"
        )
    print("\nRe-run with --batch-id <one of the above>.")


def fetch_score_column(client: OmClient, job_id: str) -> str:
    info = client.jobs.get_artifact_url(job_id, MANIFEST_ARTIFACT)
    import requests

    content = requests.get(info["download_url"], timeout=60).content
    manifest = json.loads(content)
    score_column = manifest.get("score_column")
    if not score_column:
        raise RuntimeError(f"No score_column in manifest for job {job_id}")
    return str(score_column)


def fetch_top_hits(client: OmClient, job: dict[str, Any]) -> tuple[pl.DataFrame | None, str | None]:
    import requests

    job_id = job["job_id"]
    try:
        info = client.jobs.get_artifact_url(job_id, TOP_HITS_ARTIFACT)
        content = requests.get(info["download_url"], timeout=60).content
        frame = pl.read_parquet(io.BytesIO(content))
        frame = frame.with_columns(pl.lit(job_id).alias("_source_job_id"))
        return frame, None
    except Exception as exc:  # noqa: BLE001 - report, don't crash the whole merge
        return None, f"{job_id}: {exc}"


def merge_batch(client: OmClient, batch_id: str, top_n: int, history_pages: int, out_dir: str) -> None:
    jobs = group_by_batch(fetch_history(client, history_pages)).get(batch_id, [])
    if not jobs:
        raise SystemExit(
            f"No jobs found for batch_id={batch_id} in the scanned history window. "
            "Try a larger --history-pages, or confirm the batch_id."
        )

    completed = [j for j in jobs if (j.get("status") or "").lower() == "completed"]
    incomplete = [j for j in jobs if (j.get("status") or "").lower() != "completed"]
    print(
        f"Batch {batch_id}: {len(jobs)} jobs total, {len(completed)} completed, "
        f"{len(incomplete)} not completed."
    )
    if incomplete:
        print(
            "  Excluded from merge (not completed): "
            + ", ".join(f"{j['job_id']}={j.get('status')}" for j in incomplete)
        )
    if not completed:
        raise SystemExit("No completed jobs to merge.")

    score_column = fetch_score_column(client, completed[0]["job_id"])
    print(f"Score column (from scored_shards_manifest.json): {score_column}")

    frames: list[pl.DataFrame] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_CONCURRENCY) as pool:
        futures = {pool.submit(fetch_top_hits, client, job): job for job in completed}
        for future in as_completed(futures):
            frame, error = future.result()
            if frame is not None:
                frames.append(frame)
            if error:
                errors.append(error)

    if errors:
        print(f"  {len(errors)} shard(s) failed to fetch top_hits.parquet:")
        for e in errors:
            print(f"    {e}")
    if not frames:
        raise SystemExit("No top_hits.parquet could be fetched for any completed job.")

    shard_counts = {f["_source_job_id"][0]: f.height for f in frames}
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

"""Score Om Accessible Space with hosted LULA-2, then optionally order hits.

This example launches real hosted scoring jobs and can consume Wallet Credits.
It does not place an order unless --place-order is passed.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from uuid import uuid4

import polars as pl
from omtx import OmClient, OMTXError


def score_column(frame: pl.DataFrame) -> str:
    for column in ("score", "lula2_score", "lula1_crossattention_v1_score"):
        if column in frame.columns:
            return column
    for column in frame.columns:
        if column.endswith("_score"):
            return column
    raise ValueError(f"No score column found. Columns: {frame.columns}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protein-sequence", required=True)
    parser.add_argument("--tier", type=int, default=50)
    parser.add_argument("--n", type=int, default=50_000)
    parser.add_argument("--top-k", type=int, default=10_000)
    parser.add_argument("--select", type=int, default=100)
    parser.add_argument("--output-dir", default="outputs/lula2-om-space")
    parser.add_argument("--place-order", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not os.getenv("OMTX_API_KEY"):
        print("Set OMTX_API_KEY before running this example.", file=sys.stderr)
        return 2

    try:
        with OmClient() as client:
            job = client.lula2.score(
                protein_sequence=args.protein_sequence,
                source="om",
                tier=args.tier,
                n=args.n,
                top_k=args.top_k,
                idempotency_key=f"lula2-om-space-{uuid4()}",
            )

            result_dir = Path(args.output_dir)
            artifact_paths: list[Path] = []
            for job_id in job["job_ids"]:
                client.jobs.wait(job_id, poll_interval=5, timeout=3600)
                artifact_paths.extend(
                    Path(path)
                    for path in client.jobs.download_all_artifacts(
                        job_id,
                        output_dir=result_dir / job_id,
                        overwrite=True,
                    )
                )

            score_tables = [
                pl.read_parquet(path)
                for path in artifact_paths
                if path.suffix == ".parquet"
            ]
            score_rows = pl.concat(score_tables)
            score_rows = score_rows.sort(score_column(score_rows), descending=True)
            selected_hits = score_rows.head(args.select).to_dicts()
            print(f"Selected {len(selected_hits)} hits")

            if not args.place_order:
                print("Dry run complete. Re-run with --place-order to create an order.")
                return 0

            addresses = client.molecules.shipping_addresses()
            order = client.molecules.order(
                items=selected_hits,
                shipping_address_id=addresses["default_shipping_address_id"],
                idempotency_key=f"molecule-order-{uuid4()}",
            )
    except OMTXError as exc:
        print(f"OMTX error: {exc}", file=sys.stderr)
        return 1

    print("Order number:", order["order_number"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Fetch Om Accessible Space molecules, score locally, then optionally order.

This example does not use LULA. It fetches unscored orderable molecules from a
fixed Om Wallet Credit tier, applies a placeholder local ranker, and keeps Om
order metadata on selected rows so they can be ordered.

The final order step is disabled unless --place-order is passed.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from uuid import uuid4

from omtx import OmClient, OMTXError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier", default="50")
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument("--select", type=int, default=10)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--batches", type=int, default=1)
    parser.add_argument("--out", default=None)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--place-order", action="store_true")
    return parser.parse_args()


def demo_score_smiles(
    smiles: list[str],
    *,
    seed: int,
) -> list[float]:
    """Replace this placeholder with your own model or ranking code."""

    rng = random.Random(seed)
    return [rng.random() for _ in smiles]


def write_selected_parquet(rows: list[dict[str, object]], path: Path) -> None:
    try:
        import polars as pl
    except ModuleNotFoundError as exc:
        raise OMTXError("Install polars to use --out-dir parquet output.") from exc

    flattened = []
    for row in rows:
        source_metadata = row.get("source_metadata") or {}
        flattened_row = {
            key: value
            for key, value in row.items()
            if key != "source_metadata"
        }
        flattened_row["wallet_credits"] = source_metadata.get(
            "customer_wallet_credits"
        )
        flattened_row["source_metadata_json"] = json.dumps(
            source_metadata,
            sort_keys=True,
        )
        flattened.append(flattened_row)

    path.parent.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(flattened).write_parquet(path)


def main() -> int:
    args = parse_args()
    try:
        if args.batches < 1:
            raise OMTXError("--batches must be at least 1")
        if args.n < 1:
            raise OMTXError("--n must be at least 1")
        if args.select < 1:
            raise OMTXError("--select must be at least 1")
        if args.place_order and args.batches != 1:
            raise OMTXError("--place-order is limited to --batches 1 in this example")

        selected_for_output = []
        selected_for_order = []
        out_dir = Path(args.out_dir) if args.out_dir else None

        with OmClient() as client:
            for batch_idx in range(args.batches):
                seed = args.seed + batch_idx
                pool = client.molecules.accessible_space(
                    tier=args.tier,
                    n=args.n,
                    seed=seed,
                    idempotency_key=(
                        f"om-space-slice-tier-{args.tier}-n-{args.n}-seed-{seed}"
                    ),
                )
                # smiles is a plain list[str], one SMILES per molecule.
                smiles = client.molecules.smiles(pool)

                # scores must be a same-length list[float], one score per SMILES.
                scores = demo_score_smiles(smiles, seed=seed)

                # with_scores adds your scores back to the orderable Om rows.
                scored = client.molecules.with_scores(pool, scores)
                selected = sorted(
                    scored,
                    key=lambda row: float(row["score"]),
                    reverse=True,
                )[: args.select]

                print(
                    f"Batch {batch_idx + 1}/{args.batches}: "
                    f"fetched {len(smiles)} molecules from {pool['source']['tier']}; "
                    f"selected {len(selected)}"
                )
                for row in selected[:10]:
                    metadata = row.get("source_metadata") or {}
                    print(
                        f"{float(row['score']):.6f}",
                        metadata.get("customer_wallet_credits"),
                        row["smiles"],
                    )

                if out_dir:
                    write_selected_parquet(
                        selected,
                        out_dir / f"batch_{batch_idx:06d}.parquet",
                    )
                if args.out:
                    selected_for_output.extend(selected)
                if args.place_order:
                    selected_for_order.extend(selected)

            if args.out:
                Path(args.out).write_text(
                    json.dumps(selected_for_output, indent=2) + "\n",
                    encoding="utf-8",
                )

            if not args.place_order:
                print("Dry run complete. Re-run with --place-order to create an order.")
                return 0

            addresses = client.molecules.shipping_addresses()
            shipping_address_id = addresses.get("default_shipping_address_id")
            if not shipping_address_id:
                raise OMTXError("No default shipping address found.")

            order = client.molecules.order(
                items=selected_for_order,
                shipping_address_id=shipping_address_id,
                idempotency_key=f"molecule-order-{uuid4()}",
            )
    except OMTXError as exc:
        print(f"OMTX error: {exc}", file=sys.stderr)
        return 1

    print("Order number:", order["order_number"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

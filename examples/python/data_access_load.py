"""Load binder and non-binder pools with the Python SDK."""

from __future__ import annotations

import argparse
import os
import sys

from omtx import OmClient, OMTXError

DEFAULT_PROTEIN_UUID = "0d64fb6a-8a66-50ad-82b6-fabee8bb1516"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protein-uuid", default=DEFAULT_PROTEIN_UUID)
    parser.add_argument("--binders", type=int, default=1000)
    parser.add_argument("--nonbinder-multiplier", type=float, default=5.0)
    parser.add_argument("--sample-seed", type=int, default=42)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not os.getenv("OMTX_API_KEY"):
        print("Set OMTX_API_KEY before running this example.", file=sys.stderr)
        return 2

    try:
        with OmClient() as client:
            loaded = client.load_data(
                protein_uuid=args.protein_uuid,
                binders=args.binders,
                nonbinder_multiplier=args.nonbinder_multiplier,
                sample_seed=args.sample_seed,
                include_metadata=True,
            )
    except OMTXError as exc:
        print(f"OMTX error: {exc}", file=sys.stderr)
        return 1

    binders = loaded["binders"]
    nonbinders = loaded["nonbinders"]
    metadata = loaded.get("metadata", {})
    export = metadata.get("export", {})
    print("Dataset:", export.get("dataset_id"))
    print("Vintage:", export.get("vintage") or export.get("vintage_id"))
    print("Binder rows:", binders.shape)
    print("Non-binder rows:", nonbinders.shape)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

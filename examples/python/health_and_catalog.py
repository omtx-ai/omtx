"""Minimal Om API health and catalog example using the Python SDK."""

from __future__ import annotations

import os
import sys

from omtx import OmClient, OMTXError


def main() -> int:
    if not os.getenv("OMTX_API_KEY"):
        print("Set OMTX_API_KEY before running this example.", file=sys.stderr)
        return 2

    try:
        with OmClient() as client:
            health = client.status()
            catalog = client.datasets.catalog()
    except OMTXError as exc:
        print(f"OMTX error: {exc}", file=sys.stderr)
        return 1

    print("Health:", health)
    print("Catalog keys:", sorted(catalog.keys()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

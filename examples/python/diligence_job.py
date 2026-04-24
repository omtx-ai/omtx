"""Submit and poll a diligence search job with the Python SDK."""

from __future__ import annotations

import argparse
import os
import sys
import time

from omtx import OmClient, OMTXError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--query",
        default="BRAF inhibitor resistance mechanisms",
        help="Search query to submit.",
    )
    parser.add_argument(
        "--idempotency-key",
        default=None,
        help="Retry-stable key for this logical job launch.",
    )
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--timeout", type=float, default=1800.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not os.getenv("OMTX_API_KEY"):
        print("Set OMTX_API_KEY before running this example.", file=sys.stderr)
        return 2

    idempotency_key = args.idempotency_key or f"diligence-search-demo-{int(time.time())}"
    if args.idempotency_key is None:
        print(
            "Generated a one-off idempotency key. Pass --idempotency-key to reuse one across retries.",
            file=sys.stderr,
        )

    try:
        with OmClient() as client:
            job = client.diligence.search(
                query=args.query,
                idempotency_key=idempotency_key,
            )
            print("Job ID:", job["job_id"])
            result = client.jobs.wait(
                job["job_id"],
                poll_interval=args.poll_interval,
                timeout=args.timeout,
            )
    except OMTXError as exc:
        print(f"OMTX error: {exc}", file=sys.stderr)
        return 1

    print("Final status:", result.get("status"))
    print("Result keys:", sorted(result.keys()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Score explicit SMILES with local open-weight LULA."""

from __future__ import annotations

import argparse
from pathlib import Path

from omtx.lula import load_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="lula1.1", choices=["lula1", "lula1.1", "lula2"])
    parser.add_argument("--protein-sequence", required=True)
    parser.add_argument(
        "--smiles",
        nargs="+",
        default=["CCO", "c1ccccc1", "CC(=O)Nc1nnc(s1)S(N)(=O)=O"],
    )
    parser.add_argument("--out", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model = load_model(args.model)
    rows = sorted(
        model.score(protein_sequence=args.protein_sequence, smiles=args.smiles),
        key=lambda row: row["rank"],
    )

    lines = ["rank,score,top_percentile_in_batch,smiles"]
    for row in rows:
        lines.append(
            f"{row['rank']},{row['score']:.8f},"
            f"{row['top_percentile_in_batch']},{row['smiles']}"
        )

    output = "\n".join(lines)
    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()

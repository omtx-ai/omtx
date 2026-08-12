"""Score explicit SMILES with hosted async LULA.

Install first:
    pip install omtx polars

Set:
    export OMTX_API_KEY="your-api-key"
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from omtx import OmClient


def score_column(frame: pl.DataFrame) -> str:
    for column in ("score", "lula2_score", "lula1_crossattention_v1_score"):
        if column in frame.columns:
            return column
    for column in frame.columns:
        if column.endswith("_score"):
            return column
    raise ValueError(f"No score column found. Columns: {frame.columns}")


PROTEIN_SEQUENCE = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQANN"
SMILES = [
    "CCOc1ccc2nc(S(N)(=O)=O)sc2c1",
    "Cn1ccnc1CCNCc1cn(-c2ccc(F)c(Cl)c2)nn1",
    "CCO",
]


def main() -> None:
    with OmClient() as client:
        launch = client.lula2.score(
            protein_sequence=PROTEIN_SEQUENCE,
            smiles=SMILES,
            threshold=1.0,
            top_k=len(SMILES),
            idempotency_key="explicit-smiles-lula2-example-001",
        )

        result_dir = Path("outputs/explicit-smiles-lula2")
        artifact_paths = []
        for job_id in launch["job_ids"]:
            client.jobs.wait(job_id, poll_interval=5, timeout=3600)
            artifact_paths.extend(
                Path(path)
                for path in client.jobs.download_all_artifacts(
                    job_id, output_dir=result_dir / job_id, overwrite=True
                )
            )

    tables = [
        pl.read_parquet(path)
        for path in artifact_paths
        if path.suffix == ".parquet"
    ]
    score_rows = pl.concat(tables)
    score_name = score_column(score_rows)
    rows = score_rows.sort(score_name, descending=True).to_dicts()
    for row in rows:
        print(round(float(row[score_name]), 4), row["smiles"])


if __name__ == "__main__":
    main()

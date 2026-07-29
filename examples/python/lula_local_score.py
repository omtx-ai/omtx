"""Run local open-weight LULA-1 scoring with the public omtx package.

Install first:
    pip install "omtx[lula]>=2.0.12"
    omtx lula download
    omtx lula verify
"""

from __future__ import annotations

from omtx.lula import load_model


CA2 = (
    "MSHHWGYGKHNGPEHWHKDFPIAKGERQSPVDIDTHTAKYDPSLKPLSVSYDQATSLRIL"
    "NNGHAFNVEFDDSQDKAVLKGGPLDGTYRLIQFHFHWGSLDGQGSEHTVDKKKYAAELHL"
    "VHWNTKYGDFGKAVQQPDGLAVLGIFLKVGSAKPGLQKVVDVLDSIKTKGKSADFTNFDP"
    "RGLLPESLDYWTYPGSLTTPPLLECVTWIVLKEPISVSSEQVLKFRKLNFNGEGEPEELM"
    "VDNWRPAQPLKNRQIKASFK"
)

MOLECULES = [
    "CC(=O)Nc1nnc(s1)S(N)(=O)=O",
    "Cc1ccc(cc1)S(=O)(=O)N",
    "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
    "CCN(CC)CCNC(=O)c1ccc(N)cc1",
    "c1ccc(cc1)C(=O)O",
    "CCO",
]


def main() -> None:
    model = load_model()
    rows = model.score(protein_sequence=CA2, smiles=MOLECULES)
    for row in sorted(rows, key=lambda item: item["rank"]):
        print(
            row["rank"],
            round(row["score"], 4),
            row["top_percentile_in_batch"],
            row["smiles"],
        )


if __name__ == "__main__":
    main()

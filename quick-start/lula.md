# Local LULA-1 Quickstart

Run open-weight LULA-1 locally with the public `omtx` package. LULA-1 scores a
protein amino-acid sequence against one or more ligand SMILES strings and
returns `score`, `rank`, and `top_percentile_in_batch`.

Model card and weights: <https://huggingface.co/omtx/lula-1>

## Install

```bash
pip install "omtx[lula]>=2.0.12"
```

No Hugging Face login is required for the public LULA-1 weights.

## Download And Verify

```bash
omtx lula download
omtx lula verify
```

The download command fetches the LULA-1 scoring head plus the required public
encoder assets. Verification checks the LULA-1 files against
`release_manifest.json`.

## Score With Python

Runnable script: [`examples/python/lula_local_score.py`](../examples/python/lula_local_score.py).

```python
from omtx.lula import load_model

CA2 = (
    "MSHHWGYGKHNGPEHWHKDFPIAKGERQSPVDIDTHTAKYDPSLKPLSVSYDQATSLRIL"
    "NNGHAFNVEFDDSQDKAVLKGGPLDGTYRLIQFHFHWGSLDGQGSEHTVDKKKYAAELHL"
    "VHWNTKYGDFGKAVQQPDGLAVLGIFLKVGSAKPGLQKVVDVLDSIKTKGKSADFTNFDP"
    "RGLLPESLDYWTYPGSLTTPPLLECVTWIVLKEPISVSSEQVLKFRKLNFNGEGEPEELM"
    "VDNWRPAQPLKNRQIKASFK"
)

mols = [
    "CC(=O)Nc1nnc(s1)S(N)(=O)=O",
    "Cc1ccc(cc1)S(=O)(=O)N",
    "CCO",
]

model = load_model()
for row in sorted(model.score(protein_sequence=CA2, smiles=mols), key=lambda r: r["rank"]):
    print(row["rank"], round(row["score"], 4), row["top_percentile_in_batch"], row["smiles"])
```

## Score With The CLI

```bash
omtx lula score \
  --protein protein.fasta \
  --smiles molecules.smi \
  --out scores.csv
```

`protein.fasta` may be a FASTA/text file or an inline amino-acid sequence.
`molecules.smi` may be a SMILES file or an inline SMILES string.

## Output Fields

Each score row contains:

- `score`: bounded 0-1 LULA-1 model score.
- `rank`: rank within the submitted batch.
- `top_percentile_in_batch`: percentile rank within the submitted batch.

Use `score` for ranking and enrichment. Use `rank` and
`top_percentile_in_batch` to inspect the submitted batch.

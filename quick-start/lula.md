# LULA Quickstart

Run open-weight LULA locally with the public `omtx` package. LULA scores a
protein amino-acid sequence against one or more ligand SMILES strings and
returns `score`, `rank`, and `top_percentile_in_batch`.

Model cards and weights:

- <https://huggingface.co/omtx/lula-1>
- <https://huggingface.co/omtx/lula-1.1>
- <https://huggingface.co/omtx/lula-2>

## Install

```bash
pip install "omtx[lula]>=2.0.20"
```

Hugging Face login is required for gated LULA weights.

## Download And Verify

```bash
hf auth login
omtx lula download --model lula1.1
omtx lula verify --model lula1.1
```

The download command fetches the LULA scoring head plus the required public
encoder assets. Verification checks the model files against
`release_manifest.json`.

Use `--model lula1`, `--model lula1.1`, or `--model lula2` to choose a release.

## Score With Python

Runnable script: [`examples/python/lula_local_score.py`](../examples/python/lula_local_score.py).
Notebook: [`examples/notebooks/lula_explicit_smiles.ipynb`](../examples/notebooks/lula_explicit_smiles.ipynb).

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

model = load_model("lula1.1")
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

## Your SMILES Or Om Accessible Space

Use `smiles=[...]` when you want to score molecules you already have:

```python
scores = model.score(
    protein_sequence=protein_sequence,
    smiles=["CCO", "Cc1ccc(cc1)S(=O)(=O)N"],
)
```

Use `source="om"` when you want Om to return orderable molecules from a fixed
Wallet Credit tier:

```python
from omtx import OmClient

with OmClient(api_key="your-api-key") as client:
    scores = model.score(
        protein_sequence=protein_sequence,
        source="om",
        tier=50,
        n=50000,
        client=client,
    )
```

`smiles=[...]` rows are score-only by default. `source="om"` rows include
`source_metadata`, so selected rows can be ordered through Om with Wallet
Credits.

## Order Molecules

For the full score-to-order workflow, including Om Accessible Space scoring,
explicit SMILES checks, shipping address lookup, and Wallet Credits-funded
orders, use [LULA Score To Order](../cookbooks/lula-score-to-order.md) and the
examples in [`examples/python`](../examples/python).

# CLI Quickstart

Use the `omtx` command for local open-weight LULA workflows.

## Setup

Install the public package with the LULA extra:

```bash
pip install "omtx[lula]>=2.0.20"
```

Hugging Face login is required for gated LULA weights.

For API, hosted scoring, Hub jobs, and artifact workflows, use the Python SDK
or direct API quickstarts.

## Command Families

| Command | Purpose |
| --- | --- |
| `omtx lula download` | Download LULA weights and required encoders. |
| `omtx lula verify` | Verify LULA model files against the release manifest. |
| `omtx lula score` | Score protein-sequence plus SMILES pairs locally. |

## Download And Verify

```bash
hf auth login
omtx lula download --model lula1.1
omtx lula verify --model lula1.1
```

Use `--model lula1`, `--model lula1.1`, or `--model lula2` to choose a release.

## Score Example

```bash
omtx lula score \
  --protein protein.fasta \
  --smiles molecules.smi \
  --out scores.csv
```

`protein.fasta` may be a FASTA/text file or an inline amino-acid sequence.
`molecules.smi` may be a SMILES file or an inline SMILES string.

See [LULA Quickstart](lula.md) for the Python API, expected fields, and Hugging
Face model links.

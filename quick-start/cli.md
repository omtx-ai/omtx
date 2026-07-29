# CLI Quickstart

Use the `omtx` command for local open-weight LULA-1 workflows.

## Setup

Install the public package with the LULA extra:

```bash
pip install "omtx[lula]>=2.0.12"
```

No OMTX API key or Hugging Face login is required for local LULA-1 scoring.

For API, hosted scoring, Hub jobs, and artifact workflows, use the Python SDK
or direct API quickstarts.

## Command Families

| Command | Purpose |
| --- | --- |
| `omtx lula download` | Download public LULA-1 weights and required encoders. |
| `omtx lula verify` | Verify LULA-1 model files against the release manifest. |
| `omtx lula score` | Score protein-sequence plus SMILES pairs locally. |

## Download And Verify

```bash
omtx lula download
omtx lula verify
```

## Score Example

```bash
omtx lula score \
  --protein protein.fasta \
  --smiles molecules.smi \
  --out scores.csv
```

`protein.fasta` may be a FASTA/text file or an inline amino-acid sequence.
`molecules.smi` may be a SMILES file or an inline SMILES string.

See [Local LULA-1 Quickstart](lula.md) for the Python API, expected fields, and
Hugging Face model link.

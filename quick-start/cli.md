# CLI Quickstart

The `omtx` command is owned by `vibe-discovery`. This repo documents public
usage patterns only; CLI source, tests, packaging, and runtime tooling stay in
`vibe-discovery`.

## Setup

The CLI consumes the public Python SDK and uses `OMTX_API_KEY` for authenticated
API workflows.

```bash
export OMTX_API_KEY="your-api-key"
```

Run a local check:

```bash
omtx doctor
```

## Command Families

| Command | Purpose |
| --- | --- |
| `omtx doctor` | Check local CLI prerequisites. |
| `omtx sdk surface` | Inspect the local SDK namespaces and operations. |
| `omtx sdk schema` | Inspect one SDK operation schema. |
| `omtx hub models` | List active Hub model specs from the local SDK. |
| `omtx hub schema` | Inspect one Hub model schema. |
| `omtx hub submit` | Submit a canonical `hub.<model>` job. |
| `omtx hub status` | Fetch a job status by job ID. |
| `omtx hub wait` | Poll a job until terminal state. |
| `omtx hub history` | List recent jobs. |
| `omtx artifacts upload` | Upload a local file as an Om artifact. |
| `omtx workflow ...` | Run higher-level structure workflows on top of SDK and local PyMOL. |
| `omtx pymol ...` | Manage a local PyMOL session. |

## Hub Submit Example

```bash
omtx hub submit \
  --job-type hub.boltz2 \
  --payload-json '{"protein_sequence":"MSTNPKPQRKTKRNTNRRPQDVKFPGG","ligand_smiles":"CCO"}' \
  --idempotency-key hub-boltz2-cli-demo-001 \
  --wait
```

## Artifact Upload Example

```bash
omtx artifacts upload --file target.pdb
```

Use `--signed-url` for the signed upload flow when appropriate:

```bash
omtx artifacts upload --file target.cif --signed-url
```

## PyMOL Session Flow

Session-bound PyMOL commands require a session created under the same
`OMTX_HOME`.

```bash
export OMTX_HOME=/tmp/omtx-cli-demo

omtx pymol open --replace-session
omtx pymol status
omtx pymol close
```

Direct runtime launches are diagnostics only; product validation should go
through `omtx ...`.

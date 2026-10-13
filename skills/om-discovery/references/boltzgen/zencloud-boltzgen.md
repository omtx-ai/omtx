# BoltzGen on ZenCloud

Rent compute to use the prepared BoltzGen image. Choose your own scientific inputs, design objective, safe model controls and reservation length. Start by reading the current contract:

```json
{"action":"describe","image":"boltzgen"}
```

## Three vetted starting examples

| Example | Full run template | Source/input manifest | Inputs |
| --- | --- | --- | --- |
| Barnase–barstar interface redesign | [Run](barnase-barstar.run.json) | [Inputs](barnase-barstar.inputs.json) | 2 files |
| PD-L1 Fab design | [Run](pdl1-fab.run.json) | [Inputs](pdl1-fab.inputs.json) | 30 files |
| TSA ligand-binding protein design | [Run](tsa-protein.run.json) | [Inputs](tsa-protein.inputs.json) | 1 file |

Each template generates two candidates and selects one final design (`--budget 1`). `--budget` is the final design selection count; compute is billed by the reservation term. These are example choices, not design-count caps.

Barnase–barstar redesign uses 1BRS chains A and D and redesigns chain D residues 33–46. The Fab example uses PD-L1 chain A from 7UXQ and fourteen alternative Fab scaffolds. The ligand-binding example uses CCD TSA; the upstream filename `chorismite.yaml` does not identify chorismate.

## Prepare inputs before reserving compute

Fetch the files listed in the selected manifest in your scientific workspace and check their frozen byte counts and SHA-256 hashes. The manifests link to public upstream sources; all repository sources are pinned to one revision. Register each file as an artifact owned by your authenticated Om account, then replace the quoted artifact placeholders in the run template with the returned artifact UUIDs.

Preserve every staged `files/` path and relative YAML reference. The redesign YAML needs its neighboring `1brs.cif`. The Fab YAML needs its target CIF and all fourteen scaffold YAML/CIF pairs: upload all thirty files. A workspace/chat attachment ID is not a registered artifact UUID.

The submitted file entries contain `artifact_id`, `path` and optional `media_type`. Bytes and hashes are server-resolved; the source manifest itself is not a run request.

## Review the compute term, then run

Use the live `describe` response to inspect applications, argument schema, input/output limits, current hourly Wallet Credits rate and reservation policy. Compute the complete term as `ceil(rate * minutes / 60)` and confirm that total and term before opening a new reservation. In Mendel, review the captured approval card. Additional sessions require their own reservation review.

The paid clock begins at readiness. The complete term is charged once at readiness and cannot be cancelled, extended or refunded afterward. Finish input registration before opening compute, and submit the prepared invocation promptly when ready.

Replace the template's quoted session placeholder with the accepted session ID. One invocation runs at a time on a reservation. Resolve an uncertain response using the original operation identity and accepted IDs.

## Retrieve and inspect the native results

Poll `zencloud get` with the accepted session and invocation IDs. For `completed`, retrieve the archive from `output_artifact.download_url`, check its bytes and SHA-256, and verify every file against `output_manifest.files`. Ask the same `get` for a fresh link while retention permits.

The native export includes candidate and selected-design CSVs, structures and `results_overview.pdf`. Inspect confidence, structural metrics and native liability annotations. Newly generated designs are computational predictions; successful execution does not establish experimental binding or a hit rate.

## Use your own target and settings

Edit the native YAML to choose the target, structure, scaffold set, design region or protein length, and ligand. Register edited files as new owned artifacts and update their staged references. Adjust supported design counts, budgets, protocols, steps, diffusion settings, filters and typed configuration overrides using the current contract.

The reservation length bounds execution. There is no separate fixed 60-minute BoltzGen cutoff. The frozen example checksums identify the starting examples and do not restrict custom inputs.

A read-only first prompt is:

> Show the three BoltzGen ZenCloud examples, their input manifests and complete run templates. Explain how to customize the scientific settings. Do not register files, reserve compute or run a design yet.

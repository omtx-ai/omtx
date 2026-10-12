# BindCraft2 scientific campaigns on ZenCloud

Read this for BindCraft2 discovery, positive controls, result interpretation,
or continuation. Follow Case 19 in `SKILL.md` for connection, live discovery,
reservation approval, readiness, retries, and downloads.

## Establish intent and availability

Call `zencloud(action="describe", image="bindcraft2")`. Use the returned
applications, complete `run_input_schema`, image `parameter_schema`, reservation
policy, and existing sessions. If the image is absent or inaccessible, report
that result and do not reserve another image as a substitute. A VM prototype,
upstream installation, or example request does not prove hosted availability.

Distinguish the user's scientific goal:

- **Functional test:** verify execution and faithful native results. A
  completed run with zero accepted designs can pass execution checks.
- **Known-pair positive control:** use a vetted interacting binder and antigen.
  Name the exact pair and what was tested. Scoring supplied coordinates is
  narrower than recovering a pose without supplying it; neither demonstrates
  successful de novo discovery in every binder format.
- **Discovery campaign:** generate new candidates, independently refold them,
  and inspect native acceptance. An accepted computational design still needs
  experimental binding validation.

Never call a shipped target example a positive control merely because the
target is familiar. Never report zero accepted designs as a successful binder.

## Prepare the experiment and bound its search

Review the antigen construct, chain selection, exposed epitope, residue
numbering, and relevant biological assembly. Use the chosen modality's shipped
scaffold when appropriate, or register the user's custom scaffold as another
declared input. Preserve a specifically requested binder format.

For scFv, BC2 models paired variable domains; the connecting linker needs
separate design for the final experimental construct.

One trajectory optimizes a binder backbone. ProteinMPNN can produce multiple
sequence candidates from that backbone; those are not independent trajectories.
The validation refolds and native filters determine which sequences are
accepted. Design-stage confidence alone is insufficient.

- `number_of_final_designs` is the desired accepted-sequence count, not a
  guarantee or a count of independent backbones.
- `max_trajectories` caps total attempts in the campaign. Stop at the requested
  accepted count or the attempt cap, whichever comes first.
- Size a batch using measurements relevant to that modality, target/scaffold
  size, settings, and runtime environment. Include refolding, upload/export
  handling, and headroom; qualify warm-cache or prototype-only timings.
- Keep each invocation small enough to finish and export before the returned
  reservation expiry. Native files written during unfinished work are not a
  guaranteed resumable customer checkpoint at expiry.

Do not promise a few hours per accepted binder from a per-trajectory timing.
One failed trajectory does not establish a discovery hit rate. Preserve the
native acceptance criteria for a baseline search; report any deliberately
changed scientific recipe or thresholds as a separate experiment.

## Complete illustrative run request

Verify this example against the selected release's live schema. It assumes
antigen chain A and the shipped scFv scaffold. Review chain/epitope choices for
the actual structure. The agent registers the antigen with
`artifacts_upload_bytes`, then replaces the artifact placeholder with the
returned user-owned UUID and the session placeholder with an accepted ready
session ID. Do not invent either ID or send server-only hashes and byte counts.

```json
{
  "action": "run",
  "session_id": "<READY_SESSION_ID>",
  "parameters": {
    "application": "design",
    "target_file": "files/antigen.cif",
    "chains": "A",
    "modality": "scFv",
    "core": "benchmark",
    "number_of_final_designs": 3,
    "max_trajectories": 2,
    "settings": ["campaign_seed=12345"]
  },
  "files": {
    "antigen": {
      "artifact_id": "<REGISTERED_ANTIGEN_ARTIFACT_UUID>",
      "path": "files/antigen.cif",
      "media_type": "chemical/x-mmcif"
    }
  }
}
```

Three accepted sequences and two trajectories are illustrative choices, not
platform limits. Check the selected native preset and record the resolved
settings. A custom scaffold or campaign JSON requires its own registered file
slot at the path referenced by the scientific inputs. For example, a campaign
staged at `files/campaign.json` can reference a sibling as `antigen.cif`;
`parameters.campaign_file` selects the staged `files/campaign.json` path.

Keep session, invocation, and retry identities in agent/client state. Users
should be able to ask for progress or continuation without copying recovery
keys. Poll `get` with the accepted IDs; report only progress fields actually
returned. Do not imply access to live native stage counters or operator GPU
telemetry when the public interface supplies only invocation state.

## Interpret results and continue

For a completed export, validate its manifest and inspect the native files:

- `3_Ranked/!_Ranked.csv` and companion structures: accepted designs.
- `2_Refolded/!_Refolded.csv`: sequence candidates, validation measurements,
  and failed filters, including rejections.
- `1_Trajectories/!_Trajectories.csv`: attempts and their termination points.
- `campaign_metadata.json` and returned campaign state: settings, provenance,
  and records needed to review or resume the experiment.

Report the accepted count explicitly, including zero. Inspect validation
measurements rather than substituting optimized trajectory scores. Native
confidence scores do not measure binding affinity. Select structurally and
sequence-diverse candidates for experimental testing; several ProteinMPNN
variants may share the same backbone.

Use advertised `score`, `rank`, or `filter` applications when useful. Ranking
or refiltering existing outputs does not create new predictions or experimental
evidence. If no designs pass, inspect failure patterns and the target/scaffold
setup before proposing a larger paid search or a documented recipe change.

To continue, restore the completed campaign's returned state and required
scientific files as declared inputs and use native resume support. Do not assume
another invocation or reservation inherits the previous filesystem. Increasing
`max_trajectories` from 2 to 4 permits four total attempts, not four additional
attempts. Keep the scientific recipe consistent for continuation; use a new
campaign for a different target, scaffold, or other incompatible setup.

A later paid term needs a new reservation and full quote/confirmation under
Case 19. Preserve completed outputs while their returned retention deadline
permits access. If the client's output-restoration path is unavailable or
unverified, name that gap rather than claiming seamless continuation or falling
back to arbitrary shell work. Apply only the continuation the user requested.

For scientific context, consult the selected native release's documentation:
[upstream design guide](https://github.com/PacesaLab/BindCraft2/blob/main/docs/source/design-guide.md)
and [modality documentation](https://github.com/PacesaLab/BindCraft2#design-modalities).
Current upstream documentation can differ from the installed release; the live
image contract and returned campaign metadata govern that run.

# Historical Hub Jobs And Artifacts

Hub is retired for new execution. Use
[ZenCloud scientific sessions](../skills/om-discovery/SKILL.md#case-19--zencloud-scientific-sessions)
for new structure, docking, and design work. Describe the selected image and
use its current parameters and registered file inputs; a Hub payload is not a
ZenCloud request. Confirm the full reservation price and term before starting.

Older clients may still list Hub launch methods. Do not use them to create work
or retry a historical job. The read-only `hub_models_catalog` provides migration
guidance; it is not a launch path.

## Inspect An Existing Job

Keep the original job ID. Through Om MCP, use `jobs_status` for its state and
useful inline results, `jobs_export_json` for its public export, and
`jobs_get_artifact_url` or `jobs_download_artifact` for authorized files.
`jobs_history` can help find an owned job.

For an SDK workflow, `client.jobs.status(job_id)` reads an existing job. Retrieve
an artifact using the exact public name from its result or a previously verified
download record; do not invent a path from the model name. See
[Historical Hub Artifact Retrieval](../cookbooks/hub-artifact-workflow.md).

A missing artifact listing alone does not prove that an authorized named
download is unavailable. Report which status, export and exact named download
paths were actually checked. If no public artifact name is known, preserve that
limitation instead of guessing. A preview is not proof of a full native output.

## Continue With ZenCloud

Use the existing scientific results as inputs when appropriate. Do not repeat
inference merely to repair a download or migrate a workflow. Inspect the live
ZenCloud catalog for an available replacement. Former Hub BindCraft work uses
the `bindcraft2` successor when available; other names still require a live
catalog check. Historical Hub results retain their own access contract; do not
apply a new ZenCloud session's retention deadline to them.

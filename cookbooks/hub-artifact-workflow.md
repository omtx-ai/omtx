# Hub Artifact Workflow

Use this recipe when a Hub job starts from an uploaded structure and returns
artifacts you want to inspect or download.

## Prerequisites

- `pip install omtx`
- `OMTX_API_KEY` set in your shell
- A local structure file such as `target.pdb`

## Recipe

```python
from omtx import OmClient

with OmClient() as client:
    artifact = client.artifacts.upload("target.pdb")

    job = client.hub.diffdock(
        protein_artifact_id=artifact["artifact_id"],
        ligand_smiles="CCO",
        idempotency_key="diffdock-artifact-demo-001",
    )

    status = client.jobs.wait(
        job["job_id"],
        poll_interval=5,
        timeout=3600,
    )

    print("Final status:", status["status"])
```

## Retrieve A Large Result

```python
url_info = client.jobs.get_artifact_url(
    job_id=job["job_id"],
    artifact_name="outputs/results.json",
)
print(url_info["download_url"])
```

## Notes

- Use `client.artifacts.upload_via_signed_url(...)` for larger uploads.
- Use `client.hub.submit(job_type="hub.<model>", payload={...})` for active
  models that do not have a typed helper in your installed SDK version.
- Signed result URLs are short-lived; request them when you are ready to fetch.

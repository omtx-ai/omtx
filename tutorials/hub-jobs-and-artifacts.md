# Hub Jobs And Artifacts

Hub workflows are asynchronous jobs. Some models accept sequence inputs, and
others require an uploaded structure artifact first.

## Active Public Models

The active Hub model set currently documented by the SDK is:

- `boltz2`
- `boltzgen`
- `rosettafold3`
- `chai1`
- `rfd3`
- `bindcraft`
- `alphafold`
- `proteinttt`
- `diffdock`
- `flowdock`
- `neuralplexer`
- `openfold3`

Use `client.hub.submit(job_type="hub.<model>", payload={...})` for full active
model coverage. Typed helpers exist for common models and remain thin wrappers
over the API routes.

## Sequence Job

```python
from omtx import OmClient

with OmClient() as client:
    job = client.hub.submit(
        job_type="hub.boltz2",
        payload={
            "protein_sequence": "MSTNPKPQRKTKRNTNRRPQDVKFPGG",
            "ligand_smiles": "CCO",
        },
        idempotency_key="hub-boltz2-demo-001",
    )

    status = client.jobs.wait(job["job_id"], poll_interval=5, timeout=3600)
    print(status["status"])
```

## Artifact Upload

For artifact-backed jobs, upload the file first.

```python
from omtx import OmClient

with OmClient() as client:
    artifact = client.artifacts.upload("target.pdb")
    print(artifact["artifact_id"])
```

For larger files, use the signed URL helper:

```python
artifact = client.artifacts.upload_via_signed_url("target.cif")
```

## Artifact-Backed Hub Job

```python
from omtx import OmClient

with OmClient() as client:
    artifact = client.artifacts.upload("target.pdb")

    job = client.hub.diffdock(
        protein_artifact_id=artifact["artifact_id"],
        ligand_smiles="CCO",
        idempotency_key="hub-diffdock-demo-001",
    )

    status = client.jobs.wait(job["job_id"], poll_interval=5, timeout=3600)
    print(status["status"])
```

## Result Artifact URLs

Use signed result URLs for large outputs instead of inlining artifact bytes.

```python
url_info = client.jobs.get_artifact_url(
    job_id=job["job_id"],
    artifact_name="outputs/results.json",
)
print(url_info["download_url"])
```

## CLI Option

You can also inspect active Hub models and submit jobs from the CLI:

```bash
omtx hub models
omtx hub schema --engine boltz2
omtx hub submit --job-type hub.boltz2 --payload-file payload.json --wait
```

# Historical Hub Artifact Retrieval

Use this recipe to retrieve an authorized result from an existing Hub job.
For new model execution, follow
[ZenCloud scientific sessions](../skills/om-discovery/SKILL.md#case-19--zencloud-scientific-sessions).
Hub submission and replacement attempts are retired.

## Prerequisites

- `pip install omtx` and `OMTX_API_KEY` in your environment.
- An owned historical job ID.
- An exact public artifact name from its result or a previously verified download.

## Retrieve The Existing Result

Set `OM_JOB_ID` and `OM_PUBLIC_ARTIFACT_NAME` to those known values first.
Do not substitute a guessed model-specific filename.

```python
import os

from omtx import OmClient

with OmClient() as client:
    job_id = os.environ["OM_JOB_ID"]
    status = client.jobs.status(job_id)
    print("Job status:", status["status"])

    url_info = client.jobs.get_artifact_url(
        job_id=job_id,
        artifact_name=os.environ["OM_PUBLIC_ARTIFACT_NAME"],
    )
    print(url_info["download_url"])
```

Signed URLs are short-lived. Request a fresh authorized link when needed, keep
it private, and inspect the actual file before reporting successful delivery.
A returned URL alone does not prove content integrity. Keep large artifacts in
your approved compute/storage environment.

An empty artifact list alone does not establish that a known named download is
unavailable. If the public filename is unknown or the reader fails, report the
exact limitation; do not submit a replacement Hub job. Distinguish a reviewed
preview from the full native scientific result.

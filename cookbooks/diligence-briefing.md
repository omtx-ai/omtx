# Diligence Briefing

Use this recipe when you want to turn a research question into a pollable
diligence job and inspect the final result.

## Prerequisites

- `pip install omtx`
- `OMTX_API_KEY` set in your shell

## Recipe

```python
from omtx import OmClient

question = "BRAF inhibitor resistance mechanisms"

with OmClient() as client:
    job = client.diligence.deep_diligence(
        query=question,
        preset="quick",
        idempotency_key="deep-diligence-braf-briefing-001",
    )

    result = client.jobs.wait(
        job["job_id"],
        result_endpoint="/v2/jobs/deep-diligence/{job_id}",
        poll_interval=5,
        timeout=1800,
    )

print(result.keys())
```

## Notes

- Reuse the same `idempotency_key` when retrying the same logical launch.
- Use `client.diligence.search(...)` for a narrower search job.
- Use `client.diligence.gather(...)` or `client.diligence.crawl(...)` for
  alternate diligence workflows.
- `client.jobs.wait(...)` raises on terminal failure states.

## Next Steps

- Store the returned `job_id` with your local analysis notes.
- Use result-specific keys from the returned payload to build your briefing.

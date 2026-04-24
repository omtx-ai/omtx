# Diligence Jobs

Diligence workflows are asynchronous job-backed API calls. Launch methods
return a job envelope with `job_id`; poll the job until it reaches a terminal
state.

## SDK Helpers

```python
client.diligence.search(query=...)
client.diligence.gather(query=..., preset="quick")
client.diligence.crawl(url=..., preset="quick")
client.diligence.deep_diligence(query=..., preset="quick")
client.diligence.synthesize_report(gene_key=...)
client.diligence.list_gene_keys()
```

`search` accepts `query` only. `gather`, `crawl`, and `deep_diligence` accept an
optional preset.

## Search Example

```python
from omtx import OmClient

with OmClient() as client:
    job = client.diligence.search(
        query="SOX2 inhibitor evidence",
        idempotency_key="diligence-search-sox2-demo-001",
    )

    result = client.jobs.wait(
        job["job_id"],
        poll_interval=5,
        timeout=1800,
    )
    print(result["status"])
```

## Deep Diligence Example

```python
from omtx import OmClient

with OmClient() as client:
    job = client.diligence.deep_diligence(
        query="BRAF inhibitor resistance mechanisms",
        preset="quick",
        idempotency_key="deep-diligence-braf-demo-001",
    )

    result = client.jobs.wait(
        job["job_id"],
        result_endpoint="/v2/jobs/deep-diligence/{job_id}",
        poll_interval=5,
        timeout=1800,
    )
    print(result.keys())
```

## Terminal States

The SDK treats `succeeded` as terminal success. Terminal failure states include
`failed`, `canceled`, `cancelled`, and `expired`.

## Retry Rule

Generated idempotency keys are convenient but not retry-stable. For safe
retries, pass and reuse your own `idempotency_key` for the same logical launch.

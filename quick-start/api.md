# API Quickstart

Use the Om API from scripts, notebooks, or service integrations with your API
key.
The production API base URL is:

```text
https://api.omtx.ai
```

## Set Your API Key

Keep keys in environment variables:

```bash
export OMTX_API_KEY="your-api-key"
```

## Health Check

Use `GET /v2/health` to confirm the API is reachable.

```bash
curl https://api.omtx.ai/v2/health
```

Most other routes require your API key:

```bash
curl https://api.omtx.ai/v2/datasets/catalog \
  -H "x-api-key: $OMTX_API_KEY"
```

## Idempotency

Use an `Idempotency-Key` header on JSON requests that create work, launch jobs,
or request signed access. Reuse the same key when retrying the same logical
operation.

```bash
curl -X POST https://api.omtx.ai/v2/data-access/shards \
  -H "x-api-key: $OMTX_API_KEY" \
  -H "Idempotency-Key: data-access-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"protein_uuid":"0d64fb6a-8a66-50ad-82b6-fabee8bb1516"}'
```

## Common Public Routes

| Route | Purpose |
| --- | --- |
| `GET /v2/health` | API smoke check. |
| `GET /v2/datasets/catalog` | Dataset catalog and accessible generated datasets. |
| `POST /v2/data-access/shards` | Signed binder/non-binder shard URLs for an entitled `protein_uuid`. |
| `POST /v2/diligence/search` | Start a diligence search job. |
| `POST /v2/diligence/gather` | Start a diligence gather job. |
| `POST /v2/diligence/crawl` | Start a diligence crawl job. |
| `POST /v2/diligence/deep-diligence` | Start a deep diligence job. |
| `POST /v2/hub/<model>/start` | Start an active Hub model job. |
| `GET /v2/jobs/{job_id}` | Read job status. |
| `GET /v2/jobs/history` | Page through recent jobs. |

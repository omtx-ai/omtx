# omtx

Open source home for OMTX quick starts, tutorials, cookbooks, and public
examples.

This repository is connected to git at
`https://github.com/omtx-ai/omtx.git`. At audit start it contained only this
README and the Apache 2.0 license, so its immediate job is to define a clean
public boundary before tutorials, cookbooks, or examples are rewritten from the
larger private repos.

## Purpose

Use this repo for material that can be public, useful, and maintained outside
the private product monorepos:

- quick starts for public OMTX API, SDK, and CLI workflows
- tutorials that teach one workflow at a time
- cookbooks for high-value applied use cases
- runnable examples for public OMTX workflows
- contribution guidance for docs and cookbook changes

Do not use this repo as a mirror of internal infrastructure, customer-facing
application code, private notebooks, local environment files, service account
keys, generated customer data, or operational runbooks that assume private
systems. Do not use this repo for SDK or CLI source; that remains in
`vibe-discovery`.

## Source Repos Reviewed

- `vibe-discovery`: canonical repo for the VIBE discovery CLI and Om Python SDK.
- `om-external`: private customer-facing product monorepo for frontend, backend,
  schemas, docs, payments, Hub, MCPs, and marketing/customer workflows.
- `om-internal`: private internal services, data pipelines, infra, notebooks,
  jobs, and internal engineering docs.

Internal planning and repo guidance lives under ignored `docs/**`.

## Public Content

- [Quick Start](quick-start/README.md): general setup and first successful API,
  SDK, and CLI workflows.
- [Tutorials](tutorials/README.md): teaching walkthroughs for data access,
  diligence jobs, and Hub artifact jobs.
- [Cookbooks](cookbooks/README.md): high-value applied recipes.
- [Examples](examples/python): runnable Python examples.

## Suggested Shape

```text
quick-start/
  README.md
  api.md
  sdk.md
  cli.md
tutorials/
  README.md
  data-access-python-workflows.md
  diligence-jobs.md
  hub-jobs-and-artifacts.md
cookbooks/
  README.md
  ...
examples/
  python/
  notebooks/
  data/
docs/
  ...
```

`docs/**` is ignored and reserved for local repo guidance, planning notes,
style rules, and private working checklists. Public-facing material belongs in
`quick-start/`, `tutorials/`, `cookbooks/`, and `examples/`.

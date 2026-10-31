---
name: om-discovery
description: >
  Full playbook for hosted Om MCP. Highlight the live omtx.ai products: LULA
  scoring, Discovery with AS-MS, Discovery Challenges, Diligence, Om
  Accessible Space, molecule ordering, and ZenCloud scientific sessions.
  Also covers Data Access, Wallet Credits, and quote-then-confirm rules.
  Adaptyv, A-Alpha Bio, and my genome are not ready; do not treat them as
  available. Use when connecting
  to https://agents.omtx.ai/mcp or the user mentions Om, OMTX, LULA, Discovery,
  Hub, Diligence, ZenCloud, BoltzGen on Om, BindCraft2 on Om, merging top hits
  across a multi-job LULA batch, or ordering molecules.
---

# Om Discovery

This skill is the customer playbook for hosted Om MCP. Lead with the live
omtx.ai products: **LULA**, **Discovery**, **Discovery Challenges**,
**Diligence**, **Om Accessible Space**, **ordering molecules**, and
**ZenCloud**. Do not invent prices, scores, binder labels, or order IDs.
Call Om tools and report
what they return.

## Not ready yet

These tools may appear in the MCP inventory. They are **not customer-available**.
Do not run them as a live product path:

- Adaptyv (`adaptyv_*`)
- A-Alpha Bio (`aalphabio_*`)
- my genome (`my_genome_*`)

If the user asks for any of those, say they are coming soon. Offer a live
omtx.ai path instead: LULA scoring, Discovery, Challenges, Diligence, ZenCloud, or
molecule orders.

## Connect

Hosted MCP URL:

```text
https://agents.omtx.ai/mcp
```

Auth is OAuth in the client. Om asks for **email only**. Do not paste an API key
into MCP config.

If the MCP is not attached: add that URL, complete browser login, restart if
tools are missing, then call `om_status`.

If a hosted call reports an authentication failure, complete email-only OAuth
again for that same connection, restart its MCP connection, and verify with
`om_status`. Keep the authorized account. Do not substitute an API key or
another account to bypass a failed customer OAuth check.

For a configured Codex MCP server, use its actual configured name:

```bash
codex mcp login --scopes email <configured-server-name>
```

Replace the placeholder before running the command.

Cursor: desktop only. Do not claim Cursor on the web or Cursor Agents.

## Money and safety

Keep these rules for every paid path:

- Quote first. Show the Wallet Credits total from the tool. Wait for an explicit
  confirm of **that total** before any order tool or ZenCloud reservation.
- Chat-only words such as "ok", "go", or "proceed" are not enough unless the
  user confirmed the quoted total (and shipping address when shipping).
- Physical molecule orders are separate from Discovery validation data.
- Do not invent LULA scores, prices, or binder/non-binder labels.
- A LULA score ranks molecules within one protein's run only. Never compare
  score values between proteins or runs, and never read one as a probability
  of binding. Report ranks, not score values.
- Do not call `wallet_topup` unless the user confirmed the **exact** amount and
  payment mode (saved card vs invoice).
- Prefer LULA-2 for hosted scoring unless the user asks for LULA-1.

## Core omtx.ai products — highlight these

| Product | What it is | Start with |
| --- | --- | --- |
| LULA | Score a protein against Om Accessible Space, or one SMILES across a protein panel | `lula2_score`, `lula2_proteome_score`, `lula2_residue_map` |
| Discovery | Same website program: LULA ranks space, Om runs AS-MS, data back in weeks | `discovery_checkout_quote`, `discovery_checkout_order`, `discovery_get` |
| Discovery Challenges | Submit om_50 molecules for wet-lab validation / payout challenges | `discovery_challenges_list`, `discovery_challenge_validate`, `discovery_challenge_submit` |
| Order molecules | Ship selected Om Accessible Space hits with Wallet Credits | `molecule_fulfillment_pricing`, `molecule_fulfillment_order` |
| ZenCloud | Structure, docking, design and other typed scientific workloads on a cataloged image | `zencloud_status` with `action=describe`; quote and confirm before `zencloud(action=start)` |
| Diligence | Target landscape with citations | `diligence_search`, then gather / deep only if needed |
| Accessible Space | Fetch or export Om molecules without scoring | `molecule_accessible_space`, `molecule_accessible_space_export` |
| Data Access | Account Generated Data binders / non-binders | `datasets_catalog`, `binders_get_ranked_molecules` |
| Wallet | Credits balance and funding | `credits_get`, `pricing_get`, `wallet_topup` only after exact amount |

Also live, supporting those products: fine-tune LULA, molecule search/quote, assay fulfillment, artifacts/jobs, vibe video, evidence lookups.

## Default order

After Hello World, unless the user names a later step:

1. Score a protein with LULA against Om Accessible Space.
2. Quote Discovery **or** quote molecule shipment. Wait for confirm.
3. Diligence if they want target context.
4. ZenCloud if they want structure, docking, or design on a hit (Cases 7 and 19).
5. Discovery Challenges if they want to submit om_50 molecules to a live challenge.
6. Data Access if they already have Generated Data.
7. ZenCloud if they want a scientific session: describe, quote, and confirm
   before reserving (Case 19).
8. If they ask for Adaptyv, A-Alpha Bio, or my genome, say those are not ready.

Protein sequences for scoring and Discovery: methionine-start amino acid
sequence. Follow the selected tool’s current sequence bounds.

---

## Case 0 — Hello World

**You say**

```text
Run om_status. If Om MCP is healthy, show my Wallet Credits
and list the highest-value things I can do next.
```

**Tools:** `om_status`, `credits_get`, `pricing_get`

**Do this:** Call those three. Then highlight the live omtx.ai next steps:
score a protein with LULA, quote Discovery, order molecules, Discovery
Challenges, Diligence, or describe available ZenCloud images. Do not
launch scoring, orders, or reservations yet. Do not offer Adaptyv, A-Alpha
Bio, or my genome.

---

## Case 1 — Score a protein against Om Accessible Space

Highest-value first look at a new target.

**You say**

```text
Score this protein with LULA-2 against Small Om Accessible Space,
n=1000, and return the top 25 hits. Wait until scoring finishes.
Also map hotspot residues for the top hit with lula2_residue_map.

[paste a methionine-start amino acid sequence]
```

**Tools:** `lula2_score`, `jobs_wait`, `jobs_get_top_scored_molecules`,
`lula2_residue_map`

**Do this**

1. Require a methionine-start sequence. If missing, ask for it.
2. `lula2_score` with `source=om`. Use the named Accessible Space tier.
   Default **Small** if they do not name a tier. Use LULA-1 (`lula1_score`)
   only if they ask for LULA-1.
3. Use the bounded wait loop in Case 14 with the accepted job ID, then
   `jobs_get_top_scored_molecules` after success.
4. `lula2_residue_map` on the top hit (protein sequence + that SMILES) if they
   asked, or after returning ranked hits.
5. Nothing is ordered yet.

**Reply shape:** Ranked hits from the job, reported as ranks rather than score
values — a score only orders molecules within this protein. Hotspot residues if
mapped. Offer quote-to-order or Discovery next.

---

## Case 2 — Score a proteome (one molecule, many proteins)

Inverse of Accessible Space scoring. Selectivity / off-target.

**You say**

```text
I have one SMILES and a FASTA of proteins.
Upload the FASTA, then score this SMILES across that protein panel with LULA-2.
Return the top proteins this molecule is predicted to bind.
```

**Tools:** `artifacts_upload_bytes`, `lula2_proteome_score` (or
`lula1_proteome_score` if they asked for LULA-1), `jobs_wait`

**Do this:** Upload the FASTA, call proteome score with that
`protein_artifact_id` and the SMILES, wait, return top protein hits.

---

## Case 3 — Fetch Om Accessible Space without LULA

Use when they want Om molecules to score with their own model, docking, or
internal ML.

**You say**

```text
Give me 96 om_50 molecules from Om Accessible Space. Do not score them yet.
```

**Tools:** `molecule_accessible_space` for a bounded slice.
`molecule_accessible_space_export` for the complete customer-safe Om 50
Parquet release (manifest + expiring links, no Wallet Credits charge).

**Do this:** Fetch rows or export. Do not order until they select rows and
confirm a fulfillment quote.

---

## Case 4 — Order selected molecules

Move hits onto the bench.

**You say**

```text
Take the top 10 LULA-2 hits from the last score.
Quote Molecule Fulfillment, then wait for my confirm before placing a
Wallet Credits order to ship those molecules.
```

**Tools:** `molecule_fulfillment_pricing`,
`molecule_fulfillment_shipping_addresses`, `molecule_fulfillment_order`,
`molecule_fulfillment_order_status`

**Do this**

1. Quote the selected rows. Show the Wallet Credits total from the tool.
2. Get a shipping address via `molecule_fulfillment_shipping_addresses`.
3. Call `molecule_fulfillment_order` only after they confirm the total **and**
   a shipping address.
4. Physical molecules are a separate order from Discovery AS-MS data.

---

## Case 5 — Fine-tune LULA and rescore

Customer assay labels back into ranking.

**You say**

```text
I have a labeled CSV of binders and non-binders as an Om artifact.
Fine-tune LULA-2 on it, then rescore the same protein against Small
Accessible Space with that derived model.
```

**Tools:** `lula2_finetune` (or `lula1_finetune` if asked),
`finetuned_derived_models_list`, `finetuned_derived_models_get`,
`lula2_score` with `derived_model_id`

**Do this:** Fine-tune on `csv_artifact_id`, wait until the derived checkpoint
is ready, rescore the same protein with `derived_model_id`. That rescore uses
their labels instead of base LULA weights.

---

## Case 6 — Submit a Discovery program

Use the checkout tools for a new review. They quote a defined molecule
selection and destination before the customer commits Wallet Credits.

**You say**

```text
Quote a Discovery program for this protein: 10 molecules, Small space,
AS-MS included. Show the selection, validation, and total Wallet Credits.
Do not place the order until I confirm.

[paste the protein sequence]
```

**Tools:** `discovery_checkout_quote`, `discovery_checkout_order`,
`discovery_get`, `credits_get`

**Do this**

1. Choose the requested selection and destination. Use
   `candidate_source="om_ranked"` with the protein, space and molecule count
   for Om-ranked candidates. For an explicit customer selection sent to AS-MS,
   use `candidate_source="customer_selected"` and the exact selected SMILES.
   Read the current schema for supported assay values and required inputs.
2. Quote the exact inputs. Show the returned selection, destination, material
   terms, price components and `total_credits`. Preserve `quote_fingerprint`;
   do not reuse remembered prices or substitute a different selection.
3. After the user confirms those terms and total, call
   `discovery_checkout_order` with the same inputs and fingerprint. Keep one
   stable `idempotency_key` for this logical order, including retries after a
   lost response. If the quote is stale or the inputs change, quote again and
   obtain confirmation of the revised terms before ordering.
4. Use `discovery_get` with the accepted order ID for status. A timeout is an
   unknown outcome; recover the original order before creating another.

`assay_type="none"` on an Om-ranked checkout selects physical delivery and
requires a confirmed shipping address at order time. Shipping an explicit list
of already-selected hits uses Molecule Fulfillment (Case 4). AS-MS validation
data and physical shipment are distinct destinations.

Use `discovery_launch_*` only when explicitly continuing a legacy launch;
they are not the starting point for a new checkout review.

---

## Case 7 — Structure, docking, or design with ZenCloud

Hub is retired for new work. Use ZenCloud for new model execution, including
when an older client still advertises Hub launch tools. Do not submit new
`hub_*` work or retry an old Hub job to create a replacement attempt.
`hub_models_catalog` is retained only for read-only migration guidance.

**You say**

```text
Describe the available ZenCloud images for this protein-ligand pair.
If Boltz-2 is available, inspect its input schema and quote a reservation.
Wait for my confirmation of the full Wallet Credits total and term before
reserving, then run the prediction and inspect the returned results.
```

**Tools:** `zencloud_status`, `zencloud`, and `artifacts_upload_bytes` when
the selected image requires files. Follow the complete workflow in Case 19.

**Do this:** Describe the catalog, then the selected image. Obtain its current
applications, parameters and file contract; do not reuse a Hub request body.
For former Hub BindCraft work, inspect the ZenCloud `bindcraft2` image and its
linked guidance. A former Hub model name does not prove a ZenCloud image is
available. If it is absent, report that limitation without falling back to Hub.

For an existing Hub job, retain its job ID and use the historical status,
export and authorized artifact readers in Case 14. Preserve the original
scientific results and their limitations; retirement does not require rerunning
them. Use exact known public artifact names. A missing artifact list alone does
not prove that an authorized named download is unavailable, and a preview does
not establish delivery of the full native result.

---

## Case 8 — Diligence / learn more about a target

**You say**

```text
Use Om MCP to search KRAS and summarize the therapeutic strategy,
current clinical context, and the highest-signal citations.
```

**Deep follow-up**

```text
Run deep diligence on KEAP1 resistance mechanisms and give me the
strongest evidence with citations.
```

**Tools:** `diligence_search`, then `diligence_gather` or
`diligence_deep_diligence` only if the first result warrants it.
Also `diligence_crawl`, `diligence_synthesize_report`,
`diligence_get_target_diligence_report`, `diligence_gene_keys_list`,
`rag_search`, `jobs_get_deep_diligence_result`,
`jobs_get_synthesize_report_result`.

**Do this:** Search first. Stay inside retrieved evidence. If a claim is not
in the sources, say so. Do not invent citations.

---

## Case 9 — Data Access / Generated Data

ML workflows, binder vs non-binder exports for a protein UUID they own.

**You say**

```text
Show me which Generated Data entries are available in Data Access
and which ones are most relevant to EGFR-family work.
```

```text
Give me molecular binders for this protein UUID and tell me what
downstream workflow you would run next.
```

```text
For this protein UUID, get molecular binders and non-binders and explain
how you would use them in a ranking or ML workflow.
```

**Tools:** `datasets_catalog`, `datasets_generated_protein_uuids`,
`binders_get_ranked_molecules`, `binders_get_shards`, `binders_urls`

**Do this:** These tools return signed export URLs or bounded ranked rows for
account-owned Generated Data, not a public dump of Om space. If the account
has no qualifying data, say that. Offer LULA scoring or Discovery as the path
to generate data.

---

## Case 10 — Discovery Challenges (Open Pipeline)

Submit eligible Om molecules for experimental validation. User keeps Result
Data. Payouts follow the live challenge terms.

**You say**

```text
List open Discovery Challenges. Validate these om_50 SMILES against the
STAT6 challenge, then quote/submit only after I confirm.
```

**Tools:** `discovery_challenges_list`, `discovery_challenge_get`,
`discovery_challenge_validate`, `discovery_challenge_submit`,
`discovery_challenge_submissions_list`, `discovery_challenge_result_get`

**Do this:** List/get the challenge. Validate SMILES first. Submit only after
they confirm the Wallet Credits cost and any required license flags. Report
live terms from the challenge tool, not remembered payout copy.

---

## Case 11 — Assay fulfillment

Om-run assays on selected molecules, quoted in Wallet Credits.

**You say**

```text
Quote assay fulfillment for these molecules and this assay. Do not order
until I confirm the Wallet Credits total.
```

**Tools:** `assay_fulfillment_quote`, `assay_fulfillment_order`,
`assay_fulfillment_order_status`, `assay_fulfillment_orders`

**Do this:** Quote, show the total from the tool, order only after confirm.

---

## Not ready — do not run these

If the user asks for Adaptyv, A-Alpha Bio, or my genome:

- Say that product is not ready yet / coming soon.
- Do not call `adaptyv_*`, `aalphabio_*`, or `my_genome_*`.
- Offer a live omtx.ai path: LULA, Discovery, Challenges, Diligence, ZenCloud, or
  molecule orders.

---

## Case 12 — Search or quote a molecule

**You say**

```text
Search Om for this SMILES or identifier and quote it if it is orderable.
Do not place an order until I confirm.
```

**Tools:** `molecule_search`, `molecule_quote`, then fulfillment tools from
Case 4 if they want to ship.

**Do this:** Search/quote. Fulfillment order only after they confirm the
Wallet Credits total and shipping address.

---

## Case 13 — Order Generated Data

**You say**

```text
Order Generated Data for this protein. Show the quote and wait for my
confirm before placing it.
```

**Tools:** `data_generation_order`, `credits_get`, then Data Access (Case 9)
after data exists.

**Do this:** Use the tool output for price and status. Order only after they
confirm the live total. This is not the same as Discovery Launch or shipping
physical molecules.

---

## Case 14 — Artifacts, jobs, and retries

**You say**

```text
Upload this file to Om artifacts and then use it as the input to the next
ZenCloud workflow, following the selected image’s file-input contract.
```

```text
Export this completed Om job as JSON and summarize the most important
fields for a scientist reviewing the run.
```

**Tools:** `artifacts_upload_bytes`, `artifacts_create_upload_url`,
`artifacts_finalize_upload`, `artifacts_get`, `jobs_history`,
`jobs_status`, `jobs_wait`, `jobs_export_json`, `jobs_get_artifact_url`,
`jobs_download_artifact`, `retry_job`

For every asynchronous job in this playbook, retain the accepted `job_id` and
call `jobs_wait(job_id=..., timeout_s=25)`. If it returns `wait_timeout` /
`wait_status="timed_out"`, the job is still running or its latest state is not
yet known: repeat the bounded wait with the **same** ID. A wait timeout does
not cancel a job and is not a reason to submit or retry the workload. Use
`jobs_status` if a client cannot complete a wait call; respect any returned
polling interval. Continue until the job reaches a terminal state or the
user's agreed observation deadline, then retrieve results only after success.
Report failed or cancelled work from its actual status. At an observation
deadline, report the latest state and retained ID so monitoring can resume.
Do not request one multi-minute or multi-hour MCP wait.

A large LULA-2 scoring request (enough molecules to exceed one shard's
capacity) does not come back as a single job. It fans out into many jobs
that share one batch identity (recorded on each job's own
`scored_shards_manifest.json`, not in `/v2/jobs/history`'s `metadata`), and
every per-job tool here
(`jobs_status`, `jobs_get_top_scored_molecules`, `jobs_export_json`) is
scoped to one job_id only — none of them compute a batch-wide winner. If the
user asks for "the top hit" or a ranked export of a batch like that, do
**not** call a ranking tool once per job_id in this conversation: with
dozens or hundreds of shards that floods the context and can stall the
session entirely. Instead read
[references/lula-batch-top-hits/lula-batch-top-hits.md](references/lula-batch-top-hits/lula-batch-top-hits.md)
and run the provided example script, which merges each shard's small,
already-ranked `top_hits.parquet` outside the conversation and reports back
only the final ranked result and its file path.

---

## Case 15 — Vibe / discovery video

**You say**

```text
Use Om MCP to submit a discovery video request for KRAS. Use this music
prompt: "high-energy 90s hip hop focus track for target discovery." Use a
visual prompt with molecular structures, target context, and Om's dark
discovery aesthetic. Set the title hint to "KRAS Discovery Session."
```

```text
List my Om MCP vibe video submissions and show me the newest request
status, title hint, and moderation state.
```

**Tools:** `vibe_video_submit`, `vibe_video_list`, `vibe_video_status`

**Do this:** Include music prompt, visual prompt, and title hint on submit.
This creates a reviewed media request, not a guaranteed instant video.

---

## Case 16 — Wallet Credits top-up

**You say**

```text
Check my Wallet Credits. If I need more, ask me before adding credits
by saved card or invoice.
```

**Tools:** `credits_get`, `pricing_get`, `wallet_topup`, `users_profile`

**Do this:** Show the live balance. Call `wallet_topup` only after they
confirm the exact amount and payment mode. Never guess an amount.

---

## Case 17 — Target evidence lookups

Use when Diligence is too heavy or they want a named public source. Prefer
`diligence_search` first for a landscape brief.

Then, as needed, public-source tools such as: `query_uniprot`,
`query_pubmed`, `query_chembl`, `query_pdb`, `query_clinicaltrials`,
`query_opentargets`, `query_ensembl`, `query_ncbi_gene`, `build_target_brief`,
`build_compound_evidence_brief`, `build_structure_brief`, and the matching
`get_*` detail tools.

Stay inside retrieved evidence. If it is not in the source payload, say so.

---

## Case 18 — End-to-end session

Typical customer loop in one chat:

1. Hello World.
2. Diligence on the target if they want context.
3. Score the protein (Case 1).
4. Optional residue map and a quoted ZenCloud prediction on the top hit
   (Cases 1, 7 and 19).
5. Quote Discovery **or** quote molecule shipment (Cases 6 or 4).
6. Wait for confirm. Then order.
7. Optional Data Access later if Generated Data exists (Case 9).

Keep outputs in context. Do not restart from scratch unless the user changes
the target.

---

## Case 19 — ZenCloud scientific sessions

**You say**

```text
Describe available ZenCloud images. If STORMM supports RDKit preparation,
quote the shortest permitted reservation to prepare ethanol (SMILES CCO).
Show the complete Wallet Credits price and fixed-term policy. Wait for my
confirmation before reserving, then run it and validate the returned files.
```

**Tools:** `zencloud_status` for `describe` and `get`; `zencloud` for `start`
and `run`.
Use `artifacts_upload_bytes` for required file inputs and `credits_get` for
the current balance. There is no separate quote, stop, or extend action.

Before quoting a BindCraft2 design, or handling its controls, memory failures,
results or continuation, read
[references/zencloud-bindcraft2.md](references/zencloud-bindcraft2.md).
It covers total target-plus-binder size, bounded OOM recovery and reviewed
cropping, and distinguishes functional tests from binder discovery. Observed
execution sizes are not guaranteed capacity limits or proof of accepted designs.

For BoltzGen on rented compute, read
[references/boltzgen/zencloud-boltzgen.md](references/boltzgen/zencloud-boltzgen.md).
It includes three vetted starting examples, complete run templates and input
manifests while preserving customer control over scientific settings.

**Do this**

1. **Describe first.** Read the active image's applications, parameter schema,
   file types and size limits, reservation bounds, hourly Wallet Credits rate,
   and artifact retention policy. Use only an advertised application and its
   typed inputs. Do not infer support from the image name or copy a remembered
   application list, price, or reservation limit.
   Use `zencloud_status(action="describe")` for catalog discovery, then
   `zencloud_status(action="describe", image=...)` for the selected image’s
   complete schemas and run guidance before preparing work. The catalog
   summary omits parameter schemas. An absent or inaccessible image is not
   an available paid path.
2. **Choose a session.** Reuse a known owned, ready session when the user wants
   to continue there. If the response lists open sessions, or the user wants
   several workloads, resolve whether to share a session sequentially or open
   additional sessions for parallel work. Each additional session needs its
   own full-term quote and confirmation. A missing session list does not prove
   no session exists.
3. **Quote before start.** For a new session, validate the chosen image and
   `reservation_minutes` against the live minimum, maximum, and increment.
   Calculate the full-term total as
   `ceil(wallet_credits_per_hour * reservation_minutes / 60)` using the live
   catalog rate. Show the image, term, exact total, available Wallet Credits,
   and fixed-term policy. Wait for confirmation of those values before
   `action=start`. If the catalog or quote changes, confirm the revised values.
4. **Wait for readiness.** Start with the approved image and term, recording
   the accepted `session_id`. Poll `action=get` with that ID until `ready` or
   a terminal state. The paid clock starts at readiness; use the returned
   `term_started_at` and `expires_at`. The complete term is charged once at
   readiness. After readiness it cannot be cancelled, extended, or refunded;
   workload failure or early completion does not reduce that charge. A failed
   provisioning attempt follows the returned status and Wallet outcome; do not
   invent a confirmed refund from an error alone.
5. **Run typed work sequentially.** Use `action=run` with the accepted session
   ID, schema-valid `parameters`, and any required `files` mapping. Upload file
   inputs as owned Om artifacts first; use their accepted artifact IDs, the
   contract's file paths, and allowed media types. Do not send shell commands
   or arbitrary executables. Record the accepted `invocation_id`, then poll
   `action=get` with both IDs through its terminal state. Only one invocation
   runs per session; `session_busy` is not a queue. Wait for the current work
   before submitting the next invocation on that session.
   Read `run_input_schema` for the full envelope and `parameter_schema` for
   image parameters. Each named file slot binds a registered artifact UUID to
   a `files/` path. A chat/workspace upload ID is not that UUID; bytes and
   SHA-256 are server-resolved. Examples must retain `action`, `session_id`,
   `parameters`, and `files`, with explicit placeholders for unknown IDs.
6. **Validate results.** For `completed`, retrieve the authorized output
   artifact while retention permits. Check archive bytes and SHA-256 against
   the response, then file sizes and hashes against the output manifest.
   Inspect the scientific results and report their limitations. `failed` and
   `cancelled_at_expiry` do not provide a successful output archive. At fixed
   expiry, active work is cancelled; completed exports follow the returned
   retention deadline. Get a fresh authorized download URL when an old link
   expires, while the artifact is still retained.

Keep stable `idempotency_key` values for the original start and run requests.
After a timeout or uncertain write, preserve the original key and accepted IDs;
recover the original operation through supported status or same-key replay.
Do not blindly start a replacement reservation or repeat a workload. If no
accepted ID is available and the client cannot recover the original operation,
report the uncertainty and seek support before another paid attempt.

**Reply shape:** The actual session and invocation states, quoted and confirmed
charge outcome, validated authorized results, retention deadline, and any
scientific limitations. Do not infer successful science from an accepted run.

---

## If a tool does not appear

- Restart the client after adding the server.
- Finish OAuth in the client. Om asks for email only. If openid/profile/phone
  appears, cancel instead of approving.
- Confirm the URL is exactly `https://agents.omtx.ai/mcp`.
- Use the same email on Om that they authorized in the browser.

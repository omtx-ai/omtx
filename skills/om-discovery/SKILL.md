---
name: om-discovery
description: >
  Full playbook for hosted Om MCP. Highlight the live omtx.ai products: LULA
  scoring, Discovery with AS-MS, Discovery Challenges, Hub, Diligence, Om
  Accessible Space, and molecule ordering. Also covers Data Access, Wallet
  Credits, and quote-then-confirm rules. Adaptyv, A-Alpha Bio, zencloud, and
  my genome are not ready; do not treat them as available. Use when connecting
  to https://agents.omtx.ai/mcp or the user mentions Om, OMTX, LULA, Discovery,
  Hub, Diligence, or ordering molecules.
---

# Om Discovery

This skill is the customer playbook for hosted Om MCP. Lead with the live
omtx.ai products: **LULA**, **Discovery**, **Discovery Challenges**, **Hub**,
**Diligence**, **Om Accessible Space**, and **ordering molecules**. Do not
invent prices, scores, binder labels, or order IDs. Call Om tools and report
what they return.

## Not ready yet

These tools may appear in the MCP inventory. They are **not customer-available**.
Do not run them as a live product path:

- Adaptyv (`adaptyv_*`)
- A-Alpha Bio (`aalphabio_*`)
- zencloud (`zencloud`)
- my genome (`my_genome_*`)

If the user asks for any of those, say they are coming soon. Offer a live
omtx.ai path instead: LULA scoring, Discovery, Challenges, Hub, Diligence, or
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

If the client cannot complete remote MCP OAuth, tell the user to use the Om API
with an API key instead.

Cursor: desktop only. Do not claim Cursor on the web or Cursor Agents.

## Money and safety

Keep these rules for every paid path:

- Quote first. Show the Wallet Credits total from the tool. Wait for an explicit
  confirm of **that total** before any order tool.
- Chat-only words such as "ok", "go", or "proceed" are not enough unless the
  user confirmed the quoted total (and shipping address when shipping).
- Physical molecule orders are separate from Discovery validation data.
- Do not invent LULA scores, prices, or binder/non-binder labels.
- Do not call `wallet_topup` unless the user confirmed the **exact** amount and
  payment mode (saved card vs invoice).
- Prefer LULA-2 for hosted scoring unless the user asks for LULA-1.

## Core omtx.ai products — highlight these

| Product | What it is | Start with |
| --- | --- | --- |
| LULA | Score a protein against Om Accessible Space, or one SMILES across a protein panel | `lula2_score`, `lula2_proteome_score`, `lula2_residue_map` |
| Discovery | Same website program: LULA ranks space, Om runs AS-MS, data back in weeks | `discovery_launch_quote`, `discovery_launch_order`, `discovery_launch_get` |
| Discovery Challenges | Submit om_50 molecules for wet-lab validation / payout challenges | `discovery_challenges_list`, `discovery_challenge_validate`, `discovery_challenge_submit` |
| Order molecules | Ship selected Om Accessible Space hits with Wallet Credits | `molecule_fulfillment_pricing`, `molecule_fulfillment_order` |
| Hub | Structure, docking, design (Boltz-2 and other live models) | `hub_models_catalog`, then `hub_boltz2` / `hub_submit` |
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
4. Hub if they want structure/docking/design on a hit.
5. Discovery Challenges if they want to submit om_50 molecules to a live challenge.
6. Data Access if they already have Generated Data.
7. If they ask for Adaptyv, A-Alpha Bio, zencloud, or my genome, say those are not ready.

Protein sequences for scoring and Discovery: methionine-start amino acid
sequence. Discovery Launch sequences are typically 300–1500 aa starting with M.

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
Challenges, Hub, or Diligence. Do not launch scoring or orders yet. Do not
offer Adaptyv, A-Alpha Bio, zencloud, or my genome.

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
3. `jobs_wait`, then `jobs_get_top_scored_molecules`.
4. `lula2_residue_map` on the top hit (protein sequence + that SMILES) if they
   asked, or after returning ranked hits.
5. Nothing is ordered yet.

**Reply shape:** Ranked hits from the job. Hotspot residues if mapped. Offer
quote-to-order or Discovery next.

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

Same product as the website: LULA ranks Om Accessible Space, Om runs AS-MS,
binder and non-binder data come back in weeks.

**You say**

```text
Quote a Discovery program for this protein: 10 molecules, Small space,
AS-MS included. Show Molecules / Validation / Total Wallet Credits.
Do not place the order until I confirm.

[paste a 300–1500 aa sequence starting with M]
```

**Tools:** `discovery_launch_quote`, `discovery_launch_order`,
`discovery_launch_get`, `credits_get`

**Do this**

1. Quote. Show Molecules, Validation, and Total **from the quote tool**.
   Do not reuse stale example numbers.
2. `discovery_launch_order` only after they confirm the total.
3. `discovery_launch_get` for status after it is placed.

---

## Case 7 — Launch Hub jobs

Structure, docking, or design in the same session.

**You say**

```text
Show active Hub models. Then launch Boltz-2 on this protein-ligand pair
and wait until the job finishes. Return artifacts when ready.
```

**Tools:** `hub_models_catalog`, `hub_tool_schema` if inputs are unclear,
then the named model (`hub_boltz2`, `hub_boltzgen`, `hub_chai1`,
`hub_openfold3`, `hub_diffdock`, `hub_alphafold`, `hub_bindcraft`,
`hub_flowdock`, `hub_nesso1`, `hub_neuralplexer`, `hub_rfd3`,
`hub_rosettafold3`) or `hub_submit`. Then `jobs_wait`,
`jobs_get_artifact_url` / `jobs_download_artifact`.

**Do this:** Catalog first. Launch only the model they chose. Wait. Return
artifact URLs. Upload Hub inputs with `artifacts_upload_bytes` when needed.

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

If the user asks for Adaptyv, A-Alpha Bio, zencloud, or my genome:

- Say that product is not ready yet / coming soon.
- Do not call `adaptyv_*`, `aalphabio_*`, `zencloud`, or `my_genome_*`.
- Offer a live omtx.ai path: LULA, Discovery, Challenges, Hub, Diligence, or
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
Hub workflow.
```

```text
Export this completed Om job as JSON and summarize the most important
fields for a scientist reviewing the run.
```

**Tools:** `artifacts_upload_bytes`, `artifacts_create_upload_url`,
`artifacts_finalize_upload`, `artifacts_get`, `jobs_history`,
`jobs_status`, `jobs_wait`, `jobs_export_json`, `jobs_get_artifact_url`,
`jobs_download_artifact`, `retry_job`

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
4. Optional residue map and Hub Boltz-2 on the top hit (Cases 1 and 7).
5. Quote Discovery **or** quote molecule shipment (Cases 6 or 4).
6. Wait for confirm. Then order.
7. Optional Data Access later if Generated Data exists (Case 9).

Keep outputs in context. Do not restart from scratch unless the user changes
the target.

---

## If a tool does not appear

- Restart the client after adding the server.
- Finish OAuth in the client. Om asks for email only. If openid/profile/phone
  appears, cancel instead of approving.
- Confirm the URL is exactly `https://agents.omtx.ai/mcp`.
- Use the same email on Om that they authorized in the browser.

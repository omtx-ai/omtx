---
name: om-discovery
description: Use hosted Om MCP for LULA scoring, Discovery quotes, molecule fulfillment quotes, Hub jobs, and target diligence. Use when the user mentions Om, OMTX, LULA, binders, Om Accessible Space, Discovery, AS-MS, Hub, Boltz, or connecting an MCP client to https://agents.omtx.ai/mcp.
---

# Om Discovery

Connect the hosted Om MCP, then run Om workflows with Om tools. Do not invent prices, job results, or orders.

## Connect

Hosted MCP URL:

```text
https://agents.omtx.ai/mcp
```

Auth is OAuth in the client. Om asks for email only. Do not paste an API key into MCP config.

If the MCP is not attached, add that URL, complete browser login, restart the client if tools are missing, then call `om_status`.

If the client cannot complete remote MCP OAuth, tell the user to use the Om API with an API key instead.

## First checks

1. Call `om_status`.
2. If healthy, call `credits_get` and `pricing_get`.
3. Do not launch scoring, Discovery, Hub, or orders until those succeed.

## Workflow order

After Hello World, use this order unless the user asks for a specific later step:

1. Score a protein against Om Accessible Space.
2. Score a proteome only if the user has one SMILES and many proteins.
3. Quote molecule fulfillment or Discovery. Wait for an explicit confirm before any paid order.
4. Fine-tune and rescore only if the user has labeled data as an Om artifact.
5. Launch Hub jobs only after `hub_models_catalog` and an explicit model choice.
6. Use Diligence for target landscape questions.

## Score a protein

Required: a methionine-start amino acid sequence.

Call `lula2_score` with `source=om` and the requested Accessible Space tier. Default to Small if the user does not name a tier. Wait with `jobs_wait`. Return top hits with `jobs_get_top_scored_molecules`. Map hotspot residues for the top hit with `lula2_residue_map` only if asked or after returning the ranked hits.

Nothing is ordered yet.

## Quote, then wait

For Discovery: call `discovery_launch_quote`. Show Molecules, Validation, and Total Wallet Credits. Do not call `discovery_launch_order` until the user confirms the total.

For physical molecules: quote with `molecule_fulfillment_pricing`. Do not call `molecule_fulfillment_order` until the user confirms the Wallet Credits total and a shipping address.

Physical molecules are a separate order from Discovery validation data.

## Do not

- Do not top up the wallet or charge a card from this skill.
- Do not place Discovery or fulfillment orders from chat-only words such as "ok" unless the user confirmed the quoted Wallet Credits total.
- Do not invent LULA scores, prices, or binder labels.
- Do not claim Cursor on the web or Cursor Agents are supported. Cursor desktop is the documented Cursor path.

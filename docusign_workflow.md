# DocuSign Offer Workflow (standing process)

Approach chosen 6/17/2026: **template + email-subject** (start simple).

## Account / template
- Account: Charles Pleasant (`52c8cb04-d8d3-47aa-b1db-51a9f64eab61`)
- Template: **Paragon Wholesale** (`50d2b607-2071-4e81-aaf8-7c37adb0dc9e`), 4 pages
- Roles: **Buyer** = Charles (preset, charlesp@paragongovsolutions.net) · **Seller** = filled per deal

## ⚠️ ONE-TIME PREREQUISITE (only Charles can do, in DocuSign web UI)
The Seller role has **no signature field**, so as-is the seller/agent CANNOT sign.
API tools cannot add it. Fix once:
1. DocuSign → Templates → Paragon Wholesale → Edit → Next (fields screen)
2. Switch active recipient to **Seller**
3. Drag a **Signature** + **Date Signed** field onto page 4
4. Save
Until this is done, only the Buyer can sign.

## Per-deal send (what Claude needs from Charles)
- Seller/agent **name** + **email** (property address + price come from the campaign)

## Send mechanics
- Tool: `createEnvelope` with `templateId` + `templateRoles` (Buyer preset, Seller = name/email), `status: "sent"`
- Put deal terms in the **email subject**, format:
  `Cash Offer to Purchase: {address} — ${price}`
- Optional emailBlurb: 1-line cover ("Paragon cash offer, as-is, quick close. Terms in document.")

## Tracking
- `getEnvelope` / `listRecipients` to check sent → delivered → completed
- `sendReminder` to nudge a stalled signer
- Log envelopeId on the HubSpot deal; move stage to contractsent

## Safety rule
Always confirm recipient email + price with Charles before sending (it emails a real agent).

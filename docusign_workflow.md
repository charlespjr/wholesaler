# DocuSign Offer Workflow (standing process)

## 🛑 HARD RULES (learned 6/17/2026 — Jason Gale / 5001 Beaucaire declined)
1. **NEVER auto-send a DocuSign envelope.** Claude prepares it; CHARLES approves
   and sends every single one. No exceptions.
2. **The listing AGENT is NOT a signer.** Only the SELLER signs (and Charles as buyer).
   The agent just receives the offer to review/present. Never put the agent in a
   signer role.
3. **The offer document must be COMPLETE** — all terms filled IN THE DOCUMENT
   (price, property, buyer, earnest, closing, contingencies, as-is, assignment).
   Terms in the email subject only = incomplete = rejected. The blank
   "template + email-subject" approach FAILED and is abandoned.
4. Agents often want to **meet virtually** before the seller entertains an offer.

## Corrected approach
- Claude generates a COMPLETE, filled offer document (LOI or PSA) per deal.
- Charles reviews it, then sends it himself (or Claude sends ONLY on explicit
  per-deal "send it" approval), addressed to the agent to present to the seller.
- Signature routing: Buyer = Charles; Seller = the actual seller (not the agent).
  For first contact, a buyer-signed LOI the agent can present is often cleaner.

## OLD (abandoned) approach
~~template + email-subject~~ — proved incomplete; agent declined.

## Account / template
- Account: Charles Pleasant (`52c8cb04-d8d3-47aa-b1db-51a9f64eab61`)
- Template: **Paragon Wholesale** (`50d2b607-2071-4e81-aaf8-7c37adb0dc9e`), 4 pages
- Roles: **Buyer** = Charles (preset, charlesp@paragongovsolutions.net) · **Seller** = filled per deal

## Seller signature fix (SOLVED via API — no UI edit needed)
Plain `templateRoles` sends drop the Seller's signature field (seller shows 0 tabs).
FIX: send via **composite templates** — layer an inline template over the server
template and inject the Seller's signHere + dateSigned tabs. This both surfaces the
template's own seller fields AND guarantees a signature field. Confirmed working 6/17.

## Per-deal send (what Claude needs from Charles)
- Seller/agent **name** + **email** (property address + price come from the campaign)

## Send mechanics (USE COMPOSITE TEMPLATES)
- Tool: `createEnvelope` with `compositeTemplates`:
  - `serverTemplates: [{sequence:"1", templateId: <Paragon Wholesale>}]`
  - `inlineTemplates: [{sequence:"2", recipients:{signers:[
      {roleName:"Seller", recipientId:"2", email, name,
       tabs:{signHereTabs:[{documentId:"1",pageNumber:"4",xPosition:"330",yPosition:"208"}],
             dateSignedTabs:[{documentId:"1",pageNumber:"4",xPosition:"330",yPosition:"260"}]}},
      {roleName:"Buyer", recipientId:"1", email:"charlesp@paragongovsolutions.net", name:"Charles Pleasant"}
    ]}}]`
  - `status: "sent"`
- Put deal terms in the **email subject**, format:
  `Cash Offer to Purchase: {address} — ${price}`
- Optional emailBlurb: 1-line cover ("Paragon cash offer, as-is, quick close. Terms in document.")

## Tracking
- `getEnvelope` / `listRecipients` to check sent → delivered → completed
- `sendReminder` to nudge a stalled signer
- Log envelopeId on the HubSpot deal; move stage to contractsent

## Safety rule
Always confirm recipient email + price with Charles before sending (it emails a real agent).

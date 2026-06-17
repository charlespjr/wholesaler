# Campaign File Conventions (standing rules)

Apply these to EVERY campaign CSV built from a lead sheet, automatically.

## Column headers (locked)
- Contact-name column → **`Name`**  (NOT "Contact")
- Phone column → **`Phone Number`**  (NOT "Phone")

## Always include
- `InitialText` column — ready-to-send opening message per lead
- `FollowUpText` column — follow-up message per lead
- Offer math: `AskingPrice`, `OpeningOffer`

## Standard message templates
- Initial: "Hi {Name}, is {Address} in {City} still available? I'm a cash investor,
  buy as-is, quick close. Would the seller consider around ${OpeningOffer} cash
  on the {property|lot}, subject to walkthrough and final due diligence?"
- Follow-up: "Following up on {Address}. Still active? Any feedback from the seller
  on my ${OpeningOffer} cash offer? Can review details and close fast."

## Messaging rule — "no agent fees" (FIXED 6/17/2026)
- DO NOT say "no agent fees" / "no agent on your end" on **LISTED (MLS) properties.**
  Agents read it as trying to cut their commission (broker Irene Huang reacted this way
  on 6436 S Vernon). On listed deals the SELLER already pays commission per the listing —
  the agent keeps it, and we want them paid (they often double-end and push our offer).
- "No agent fees" phrasing is ONLY for true **off-market / FSBO / direct-to-owner** leads.
- Listed-property soft inquiry should say: "cash, as-is, quick close, seller nets a clean
  sale" — NOT "no agent fees."

## Routing tags (in Notes/description)
- Distressed/foreclosure/gut-rehab/land ≤60% value → **MaxDispo-fit** (builders/developers)
- Turnkey/remodeled/tenant-occupied rentals → **BUY-HOLD (landlord buyer, not MaxDispo)**

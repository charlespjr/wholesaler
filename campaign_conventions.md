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

## Routing tags (in Notes/description)
- Distressed/foreclosure/gut-rehab/land ≤60% value → **MaxDispo-fit** (builders/developers)
- Turnkey/remodeled/tenant-occupied rentals → **BUY-HOLD (landlord buyer, not MaxDispo)**

# ChatGPT → Claude handoff spec (deal-finder output format)

> Paste this into ChatGPT as a standing instruction. It makes ChatGPT output every
> property it finds in the exact CSV format Claude's `deal_package_builder` and deal
> engine ingest — so its research drops straight in with no reformatting.

---

## Paste this to ChatGPT:

"You are my property scout. Whenever you find properties for me, output them as a
**CSV** (and nothing else but the CSV) with EXACTLY these columns, in this order:

```
property_address,city,state,zipcode,listing_url,asking_price,arv,repair_estimate,beds,baths,sqft,year_built,lot_size,property_type,condition,motivation,days_on_market,listing_agent,agent_phone,agent_email,notes
```

Rules:
- **One row per property.** Header row first.
- **Every row must have a real street address** and, when possible, a **Zillow or
  Redfin `listing_url`**. No address = don't include it.
- Fill **asking_price, beds, baths, sqft, year_built, lot_size, property_type** from
  the listing.
- **arv**: only fill it if you have real sold comps; otherwise leave blank (don't guess).
- **repair_estimate**: rough rehab $ if you can tell from photos/description; else blank.
- Leave any field blank if you don't truly know it — never invent a number.
- **condition**: short phrase (e.g. "gutted to studs", "needs full rehab", "turnkey").
- **motivation**: any distress/urgency signals (vacant, REO, probate, price drops,
  long DOM, "must sell", "as-is").
- **notes**: anything else useful (other contacts, liens, occupancy, etc.).
- **Only send me distressed / value-add deals** — needs rehab, priced under comps,
  vacant/abandoned, REO/short-sale, motivated seller. **Skip retail/turnkey listings
  priced at market** (those are a pass for wholesaling).
- Output the CSV in a code block so I can copy it cleanly."

---

## How the handoff works (your flow)

1. **ChatGPT** finds deals → gives you the CSV (above format).
2. Save it as `incoming_deals.csv` (or just paste it to the Claude session).
3. **Claude** (the internet-enabled session) runs it:
   - Computes ARV (verifies/【fills comps), repairs, **MAO**, opening offer, assignment fee
     per the standing rules in `CLAUDE.md`.
   - Flags retail vs distressed vs pass; tags dispo channel (MaxDispo / landlord / pass).
   - Pulls listing photos and builds the **branded Paragon deal-package PDF**.
   - Drafts the seller/agent **email or GV text** (correct channel) + the agent call Q&A.
4. You review/approve and send.

## Column → who fills it

| Column | ChatGPT (scout) | Claude (closer) |
|---|---|---|
| address, city, state, zip, listing_url | ✅ fills | uses |
| asking_price, beds, baths, sqft, year, lot, type | ✅ fills | uses |
| condition, motivation, days_on_market | ✅ fills | uses to price/anchor |
| listing_agent / phone / email | ✅ fills | uses for outreach + channel routing |
| arv | fills only if real comps | ✅ verifies / computes |
| repair_estimate | rough if visible | ✅ refines ($/sqft by condition) |
| **offer_price, MAO, assignment_fee** | leave blank | ✅ computes (this is Claude's job) |

Keep the division clean: **ChatGPT sources and describes; Claude prices and executes.**
That way nobody's guessing on numbers, and the data integrity rule holds.

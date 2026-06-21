# Paragon Wholesaling — working rules for Claude

## Offer pricing (STANDING RULE — apply to every offer, always)
This is a **wholesaling business**. Every offer must leave assignment spread + room to negotiate up. Never anchor at the max.

- **MAO is the CEILING, not the offer.** 70% MAO (= 70% × ARV − repairs − assignment fee) is the walk-away max — the most we'd ever pay. We never open there.
- **Default opening offer ≈ 15% below MAO**, rounded to a clean number, and lower when the deal warrants it.
  - Example: MAO $51,500 → open ~**$43,000**; ceiling $51,500.
- **Anchor even lower** when any of these are true (low anchor costs nothing on marginal deals): full/heavy rehab, "unknown" or seller-never-occupied disclosure, seller "firm" but priced above MAO, long days-on-market, or strong distress/motivation signals.
- **Always justify the number** with condition / disclosure / rehab scope ("seller has no condition knowledge, full rehab, all risk on buyer, all cash, fast close").
- **If it can't close at or under MAO, pass.** Don't chase firm sellers priced above MAO.

## No address, no deal (HARD RULE)
- **A lead with no specific property address is not a deal — skip it.** Never draft an offer, a "your listing" feeler, or a generic buyer-intro for a contact that has no address. (Learned 6/20/26: built 3 addressless "active cash buyer" intros for Deborah/Johnnie/Maria — Charles: "if no address, then i dont do business.")
- If a lead is missing the address, drop it from the campaign — do not substitute a generic outreach to keep it in.

## No retail listings (HARD RULE)
- **Do not make offers on retail/turnkey/at-market listings — those are an automatic PASS.** Only draft an offer when the property is distressed AND there is real wholesale spread. (Learned 6/20/26: Juliana/River Hills and Woodshaw — both turnkey, agent-listed at market — declined as "significantly below market"; chasing them wasted engagement. Charles: "stop offering on retail.")
- **Retail = pass.** Signals: turnkey/updated condition, priced at/near comps, listed by an agent at market, seller wants market value, no motivation. Don't manufacture a wholesale number for these.
- **Distressed = work it.** Signals: needs full/heavy rehab, sold as-is, priced well below market comps, REO / short sale, vacant/abandoned, motivated or firm-low seller, value-add (list well under area median).
- If condition/pricing is unclear, find out before drafting — don't default to sending an offer.

## No walkthroughs (HARD RULE)
- **We do NOT do in-person walkthroughs/tours — never promise or request to "walk it," "tour it," or "get someone through it" as our step.** We buy sight-unseen. (Learned 6/21/26: Charles — "you know fucking well u cant do no walkthrough.")
- Verify condition via **current interior photos/video + seller disclosures**, and rely on the **10-day inspection/feasibility contingency** (order a local inspector/contractor during that window if needed) to confirm or terminate.
- If a seller **requires** a walk before they'll consider an offer (e.g. 201 Sandhurst), that needs a local third party (buyer's agent/inspector) — flag it to Charles; don't commit Paragon to physically walking it.

## Lead channel routing (HARD RULE)
- **Has an email → email** the formal offer/inquiry to that address.
- **Phone number only (no email) → add to the GV (Google Voice) campaign** with a unique SMS opener. **Always output campaign files as CSV** (`GV_Campaign_NoEmail_*.csv`), columns: #, Contact, Phone, Property, Brokerage, SMS Script. Never just hand back a "call script." The opener intros Paragon + the property, asks for a cash/as-is look + quick close, and asks **where to email written terms** — the offer number follows once they engage (so we don't quote blind). (Learned 6/21/26: Charles — "when it's only a number, you need to do gv campaign"; "csv format always.")

## Data integrity (HARD RULE)
- **Pull every number — ARV, repairs, list price, rent, comps — straight from the deal's own docs / buyer package / dealsheet. NEVER estimate or back-into a figure that already exists in the files.** (Learned 6/20/26: estimated 7512 Saint Lawrence value at ~$140K when the buyer package clearly stated ARV $180K. Do not repeat.)
- If a needed number genuinely isn't in any provided file, say so explicitly and label it an assumption — don't silently substitute a guess.
- Evaluate every deal off **ARV**, not list/as-is price (MaxDispo and the 70% rule both work off ARV).

## Deal evaluation format (run on EVERY deal, upfront — no back-and-forth)
For each deal, lead with a tight numbers block, then profit, then dispo fit, then verdict:

1. **Numbers:** Ask | ARV | Repairs | **Builder max** (0.70×ARV − repairs = what an end cash buyer/builder pays) | **My MAO ceiling** (builder max − assignment fee) | **My opening** (~15% below MAO, lower if heavy rehab / unknown disclosure / firm-overpriced / long DOM).
2. **My profit (assignment fee)** = builder price − my contract price. Show it at the opening price AND at the ceiling. Target fee ~$8–15k.
3. **MaxDispo fit** (their buyers = builders; need deep discount, contract ≤ ~60% of ARV, gut/teardown/distressed product). Test: builder all-in (my contract + repairs) should be ≤ ~70% of ARV (≥~30% builder margin). Tag the channel:
   - **MaxDispo (builders)** ← deep-discount distressed, contract ≤60% ARV.
   - **Buy-hold / landlord buyers** ← turnkey / tenant-occupied / cap-rate deals.
   - **Pass** ← can't be contracted at/under MY MAO.
4. **Verdict + recommended opening offer.** If it can't be contracted at/under my MAO, it's a pass — say so plainly.

(See `maxdispo_buybox.md`. MaxDispo rejects anything only lightly under list — "30k under list is still retail.")

## Buyer / terms defaults
- Buyer: **Paragon Government Solutions LLC, and/or assigns** (assignment rights always — except REO/bank deals that prohibit it).
- $1,000 earnest money to title within 3 business days of acceptance.
- As-is, where-is; 10-day inspection/feasibility; close 21 days or seller's timeline; no financing/appraisal contingency.
- Proof of funds via doubleclose.com (prep a POF spec; see POF_spec_*.docx).

## Branding
- All outbound offer docs use the Paragon logo header + footer via `tools/paragon_brand.py`.
- Contact on docs: 11166 Fairfax Blvd, Suite 500, Fairfax, VA 22030 · (888) 495-6935 · charlesp@paragongovsolutions.net · UEI FSCZBK8CBV82 · CAGE 9WX69.

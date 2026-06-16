# Lead Scaling Plan — Acquisition (More Leads + More Deals)

Goal: maximize **lead volume** (top of funnel) and **conversion** (replies → signed
contracts). Dispo is handled by MaxDispo, so this plan is acquisition-only.

---

## TRACK 1 — ON-MARKET (Zillow Detail Scraper) — *do now*

This is the channel every current lead came from. We just need bigger pulls.

### Scrape settings (apply to every metro)
- Listing type: **For Sale (FSBO + agent)**
- Price ceiling: **≤ $325,000** (wholesale range; skip luxury)
- Prioritize distress filters: **Price Reduced**, **Days on Zillow 30+**, **"as-is" / "investor" / "TLC" / "handyman" / "cash only"** in description
- Pull `attributionInfo` (agent name + phone) — required for GV texting

### Target metros (expand beyond the 6 already worked)
Tier 1 — cheap distressed inventory, high investor activity (best wholesale yield):
| Metro | Why |
|---|---|
| **Detroit, MI** (more zips) | already top producer; pull remaining 48xxx zips |
| **Cleveland, OH** (more zips) | strong; expand 441xx |
| **Memphis, TN** 38108/38111/38114/38115/38127 | huge wholesale market, untapped |
| **Birmingham, AL** 35206/35208/35211/35224 | cheap, untapped |
| **Indianapolis, IN** 46201/46218/46222/46226 | untapped |
| **Kansas City, MO** 64127/64128/64130/64132 | untapped |
| **St. Louis, MO** 63111/63115/63116/63118/63120 | untapped |
| **Jacksonville, FL** (more zips) | top producer; expand 322xx |
| **Houston, TX** (more zips) | top producer; expand 770xx |
| **Chicago, IL** (south/west) | expand 606xx |

Tier 2 — keep feeding existing winners: Columbia SC, Dallas TX, Baltimore MD,
Atlanta GA, Baton Rouge LA, Fayetteville NC, Albuquerque NM, Phoenix AZ.

### Workflow
1. You run the Zillow Detail Scraper per metro (settings above), export CSV.
2. Send me the CSV(s).
3. I dedup (internal + vs HubSpot), run MAO math, build:
   - `offer_campaign_<metro>.csv` (ranked by motivation)
   - `gv_campaign_<metro>.json` (throttled texts, $0 offers auto-excluded)
   - HubSpot deals import.

### Also ready: auction.com scraper (`tools/run_auction_scraper.py`)
Blocked from this cloud env (egress). Run locally:
`APIFY_TOKEN=xxx python3 tools/run_auction_scraper.py` → send me `auction_raw.json`.

---

## TRACK 2 — OFF-MARKET (direct-to-seller) — *bigger, less competition*

No agents, no retail pricing, where the real margin lives.

### Pull list from a data source (PropStream / BatchLeads / DealMachine)
Stack these filters (this is the motivated-seller recipe):
- **Absentee / out-of-state owner**
- **High equity** (≥ 50%, ideally free-and-clear)
- **Distress overlays** (any): pre-foreclosure / NOD, tax-delinquent, code
  violations, vacant, tired landlord (owned 7+ yrs), inherited/probate, 55+ owner
- Target the same Tier-1 metros above for consistency
- Pull **500–1,000 records/metro** → skip trace → ~600 with phone

### Workflow
1. You export the filtered list (CSV with owner name, mailing address, property
   address, phone if skip-traced).
2. Send me the CSV.
3. I dedup vs HubSpot, build a **cold-text GV campaign** (throttled 120–180s, DNC
   honored) + a **direct-mail merge** for the no-phone records.
4. Replies flow back to me for margin check → offer.

### Compliance (locked rules)
- Honor every "stop/remove/unsubscribe" → immediate close + DNC (already a rule).
- No "foreclosure rescue" framing (IL Mortgage Rescue Fraud Act, etc.).

---

## CONVERSION BOOSTERS (more deals from the same leads)

1. **Motivation scoring** — auto-rank every new lead/reply by signals (price drop
   size, DOM, "tired landlord," vacancy, equity %). Work hottest first, pass dead
   ones faster. *I can bake this into the campaign builder.*
2. **Rehab-from-photos** — when agents send listing photos, AI rough-estimates
   repairs → tighter MAO → more credible offers → more acceptances.
3. **Follow-up tracker** — timed nudges so live threads don't go cold
   (e.g., current: 5511 Cruz Rd, 8723 S Eggleston, 7512 S Saint Lawrence counter).

---

## Immediate next actions
- [ ] You: run Zillow Detail Scraper on 3–4 Tier-1 metros (settings above), send CSVs
- [ ] You: pull one off-market list (PropStream/BatchLeads) for one Tier-1 metro
- [ ] Me: build campaigns from whatever you send; add motivation scoring to the builder

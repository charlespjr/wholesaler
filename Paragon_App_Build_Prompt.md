# BUILD PROMPT — "Paragon Deal Engine" wholesaling app

> Paste this entire document to Claude (or Claude Code) as the spec. It defines the
> business, the exact deal math, the hard rules, the templates, and the app to build.
> The goal: I enter ONE address (or bulk-upload a CSV of addresses/skip-trace leads),
> and the app works each deal end-to-end — pulls the numbers, decides retail vs.
> distressed vs. pass, computes a disciplined offer, and generates the seller email,
> the SMS/Google-Voice script, and a branded PDF offer, then routes each lead to the
> right channel. Below is everything it needs to know.

---

## 0) ROLE & MISSION

You are building **Paragon Deal Engine**, the in-house software for **Paragon
Government Solutions LLC**, a **real-estate wholesaling** company. Wholesaling =
I get a property under contract with the seller at a deep discount, then assign that
contract to an end cash buyer (a builder/landlord) for an assignment fee. I never
intend to close/own; the spread between my contract price and the buyer's price is my
profit.

The app must take a property (or a list) and **do the analyst + copywriter + dispatcher
work automatically**, applying the rules in this document exactly. Treat every rule
marked **HARD RULE** as non-negotiable business logic, not a suggestion.

---

## 1) THE CORE DEAL MATH (implement exactly)

Everything is evaluated off **ARV (After Repair Value)** — never off list price or
as-is price.

```
builder_max  = 0.70 * ARV - repairs        # what an end cash buyer/builder will pay
MAO (ceiling)= builder_max - assignment_fee  # max I will EVER pay the seller
opening_offer= round_clean(MAO * 0.85)       # default open ~15% BELOW MAO (never anchor at max)
assignment_fee target = $8,000–$15,000 (default $10,000)
```

- **MAO is the CEILING, not the offer.** Never open at MAO. Default opening ≈ **15%
  below MAO**, rounded to a clean number.
- **Anchor even lower** (open ~20–30% below MAO) when ANY of these are true: full/heavy
  rehab, "unknown"/seller-never-occupied disclosure, seller "firm" but priced above MAO,
  long days-on-market, strong distress/motivation signals.
- **Always attach a justification string** to the number (condition / disclosure / rehab
  scope / "all cash, fast close, all risk on buyer").
- **If the deal cannot be contracted at or under MAO → PASS.** Do not chase firm sellers
  priced above MAO.

### Repairs estimate
- Default light/cosmetic rehab ≈ **$37–$40 / sqft** (as-is).
- Heavier scope by condition: dated/needs-work ≈ **$45–$55/sqft**; full gut/teardown ≈
  **$60–$80/sqft**. Pick from condition signals (see §3).
- If interior condition is unknown, assume a **heavier** number (low anchor costs nothing).

### Owner-direct mail/offer letter number (for skip-trace owner campaigns)
When mailing/texting an owner directly (no list price, value = AVM estimate):
```
owner_offer = round_to_1000( max( 0.70*AVM - 37*sqft , 0.10*AVM ) )
```
Quote the number only when both AVM>0 and sqft>0; otherwise say "cash offer to follow
once I confirm condition."

### MaxDispo / dispo fit test
End buyers come in two types — tag every deal to ONE channel **before** dispo:
1. **MaxDispo (builders)** ← deep-discount distressed. Requires **contract ≤ ~60% of
   ARV**, and builder all-in (`my_contract + repairs`) **≤ ~70% of ARV** (≥~30% builder
   margin). Product: gut/teardown/vacant/fire/REO/tax-delinquent/code-violation.
   *(MaxDispo's own words: "30k under list is still retail." Lightly-under-list ≠ a fit.)*
2. **Buy-hold / landlord buyers** ← turnkey / tenant-occupied / cap-rate deals. Price on
   income (cap rate / DSCR), not on the gut formula. (e.g. remodeled, tenant in place.)
3. **Pass** ← can't be contracted at/under MY MAO.

---

## 2) THE HARD RULES (enforce as code; never override)

1. **NO ADDRESS, NO DEAL.** A lead with no specific property address is not a deal —
   skip it. Never draft an offer, "your listing" feeler, or generic intro for a contact
   with no address. Drop addressless leads from campaigns (don't substitute generic
   outreach). Also drop placeholder addresses (street number `0`, blank city/zip).

2. **NO RETAIL LISTINGS.** Retail/turnkey/at-market listings = automatic PASS. Only make
   an offer when the property is **distressed AND there is real wholesale spread**.
   - *Retail signals (PASS):* turnkey/updated, priced at/near comps (list within ~5% of
     value), listed by an agent at market, seller wants market value, no motivation.
   - *Distressed signals (WORK IT):* needs full/heavy rehab, sold as-is, priced well below
     comps, REO/short-sale, vacant/abandoned, motivated or firm-low seller, value-add
     (listed well under area median). Long DOM = added motivation.
   - If condition/pricing is unclear, **enrich first** — don't default to sending an offer.

3. **NO WALKTHROUGHS.** We buy **sight-unseen**. Never promise/request to "walk it,"
   "tour it," or "get someone through it" as our step. Verify condition via **current
   interior photos/video + seller disclosures**, and rely on the **10-day
   inspection/feasibility contingency** (order a local inspector/contractor in that
   window if needed). If a seller *requires* a walk, flag it for a human — route to a
   local third party (buyer's agent/inspector); never commit Paragon to physically walking.

4. **LEAD-CHANNEL ROUTING.**
   - Lead **has an email → email** the formal offer/inquiry to that address.
   - **Phone number only (no email) → Google-Voice (GV) SMS campaign** with a unique
     opener. **Always output GV campaigns as CSV** (`GV_Campaign_*.csv`) with columns:
     `#, Contact, Phone (non-DNC), Property / Properties, Owner_Type, Property_Count,
     SMS Script (unique)`. Never output just a "call script."
   - The SMS opener intros Paragon + the property, asks for a cash/as-is look + quick
     close, and asks **where to email written terms** — the number follows once they
     engage (don't quote blind over SMS).

5. **DATA INTEGRITY.** Pull every number — ARV, repairs, list, rent, comps — from real
   data/the deal's own docs. **Never estimate or back-into a figure that already exists.**
   If a needed number genuinely isn't available, say so explicitly and label it an
   assumption — don't silently substitute a guess. Evaluate off **ARV**, always.

6. **VOICE / TONE (every seller/agent message).** Write like a **real person**, not an AI.
   Contractions, short sentences, a little informal — a busy investor firing off a reply,
   not a form letter. **Avoid AI tells:** no em-dash-heavy structured paragraphs, no
   "I want to be straight with you about why," no bulleted reasoning in a person-to-person
   message, no stiff sign-offs. Sign casually ("Charles" / "Thanks, Charles"). Formal PA
   documents stay formal; texts and seller emails stay human.

---

## 3) PER-DEAL PIPELINE (what the app does to each address)

**Input:** one address, OR a bulk CSV (either a plain address list, or a REsimpli/skip-
trace export — see §6 for that schema).

For each property, run these stages:

**Stage A — Normalize & guard.** Parse/standardize the address. Apply HARD RULE 1
(no-address/placeholder → drop with reason). Dedup by `(normalized_address, zip)` against
the existing database and within the batch.

**Stage B — Enrich.** Gather, from data providers and/or web research (cite sources):
- ARV (comps-based; conservative — haircut aggressive AVMs), beds/baths/sqft, year built,
  lot size, property type (SFH/townhouse/condo/land/multi).
- List price + days-on-market + listing agent (if listed).
- Condition signals → rehab $/sqft bucket (photos, "as-is," "needs work," "investor
  special," REO, vacancy, code violations).
- Owner & contact (skip-trace): name, entity type (LLC/Trust/Bank = company), emails,
  phones with **DNC flags**, mailing address, absentee/vacant flags.
- For rentals: in-place rent, market rent, taxes, insurance, mgmt → cap rate / DSCR.
- Land: price off $/acre comps, not home median.

**Stage C — Classify.** Retail vs Distressed vs Land vs Rental (buy-hold). Apply HARD
RULE 2 (retail → PASS). **LLC/Bank/Trust-owned → exclude from owner-direct outreach by
default** (I don't cold-contact entities; flag separately).

**Stage D — Price.** Compute `ARV, repairs, builder_max, MAO, opening_offer,
assignment_fee at open AND at ceiling`, with justification. Run the MaxDispo/dispo fit
test and tag the channel.

**Stage E — Verdict.** Emit the standard deal block (below). If PASS, say so plainly with
the reason; generate no offer.

**Stage F — Generate outputs** (only for non-PASS):
- **Seller/agent email draft** (human voice) — or **SMS script** if phone-only — per the
  routing rule.
- **Branded PDF offer** (Paragon header/footer) when a formal offer is requested or the
  channel is email.
- **Buyer/dispo blast** tagged to MaxDispo or landlord channel.
- Add to the right campaign CSV; record status in the pipeline.

### Standard deal-evaluation output block (render for EVERY deal, upfront)
```
ADDRESS — City, ST ZIP        [Distressed | Retail | Rental | Land]
Numbers:  Ask $___ | ARV $___ | Repairs $___ ($/sqft, scope)
          Builder max (0.70*ARV - repairs) $___
          My MAO ceiling (builder max - fee) $___
          My opening (~15% below MAO) $___   [justification]
Profit:   assignment fee @ opening $___ | @ ceiling $___   (target $8–15k)
Dispo:    [MaxDispo builders ≤60% ARV | Buy-hold/landlord | Pass]   (show the fit math)
VERDICT:  <recommended opening offer, or PASS + reason>
```

---

## 4) MESSAGE & DOCUMENT TEMPLATES (match this voice exactly)

### 4a) Seller email — single property, distressed (human voice)
```
Subject: Regarding {address}, {city} - a private cash offer (no pressure)

Hello,

I'm Charles Pleasant with Paragon Government Solutions - a real company, run by real
people - writing to you directly and honestly about your property at {full_address}.

Given its estimated value of about ${ARV} and the updates it likely needs, my as-is cash
offer is ${opening} - all cash, no repairs, no commissions, no closing costs, and I close
on your timeline (as little as two weeks). If it's in better shape than I've assumed, the
number goes up.

The straight truth: a traditional agent sale might net more if you can wait and make
repairs. My offer is for certainty and speed - especially if you've fallen behind or a
deadline is near. No pressure, no obligation.

With respect,
Charles Pleasant
Paragon Government Solutions LLC
(888) 495-6935 | charlesp@paragongovsolutions.net
11166 Fairfax Blvd, Suite 500, Fairfax, VA 22030
Reply REMOVE to opt out of future letters about your property.
```
(Multi-property owner: subject `Cash offers on your {n} properties ({city})`; list each
address with "cash offer to follow once I confirm condition"; no per-property number.)

### 4b) Google-Voice SMS opener (phone-only lead) — 1–2 segments, asks where to email
```
Hi, this is Charles Pleasant with Paragon Government Solutions, a cash buyer. I'm
interested in your property at {address}, {city} {state}. I'd make a fair, all-cash,
as-is offer - no fees, no commissions, close on your timeline. Where can I email you
written terms? Reply STOP to opt out.
```

### 4c) Agent reply when their listing is RETAIL (honest pass, keep the relationship)
Human, short: acknowledge, say at the list price it doesn't pencil for cash, don't
lowball, leave the door open if it gets distressed or the seller turns flexible.

### Reply-quality bar
- Human voice (HARD RULE 6). Tailor to what they actually said.
- Never exceed MAO. If a seller counters above MAO, the app recommends PASS.
- SMS segment awareness: ≤160 chars = 1 segment, ≤306 = 2, ≤459 = 3. Keep openers ≤2.

---

## 5) BUYER / OFFER / BRANDING DEFAULTS (bake into every offer & PDF)

- **Buyer:** `Paragon Government Solutions LLC, and/or assigns` (assignment rights always —
  EXCEPT REO/bank deals that prohibit assignment; then drop "and/or assigns").
- **Earnest money:** $1,000 to title within **3 business days** of acceptance.
- **Terms:** as-is/where-is; **10-day inspection/feasibility**; close in **21 days** or the
  seller's timeline; **no financing/appraisal contingency**.
- **Proof of funds:** via doubleclose.com (generate a POF spec when needed).
- **Branding (header/footer on every outbound doc):** Paragon logo +
  `11166 Fairfax Blvd, Suite 500, Fairfax, VA 22030 · (888) 495-6935 ·
  charlesp@paragongovsolutions.net · www.paragongovsolutions.net · UEI FSCZBK8CBV82 ·
  CAGE 9WX69`.
- **Compliance:** CAN-SPAM physical address on every bulk email; honor TCPA/DNC (never
  text a DNC-flagged number); A2P 10DLC registration for SMS sending.

---

## 6) BULK UPLOAD — SKIP-TRACE CSV SCHEMA (REsimpli-style) the app must ingest

Columns the importer should read (extra columns ignored):
```
Property_Street_Address, Property_Street_Address_2, Property_City, Property_State,
Property_Zip_Code, Property_Estimated_Value (AVM), Property_Approx_Sq_Ft, Property_Bed,
Property_Bath, Property_Year_Built, Property_House_Type, Owner_Type, ownershipType
(individual|company|trust), Full_Name, First_Name, Last_Name, Mailing_Formated_Address,
Email_1..Email_6, Phone_1..Phone_10 with matching Phone_N_DNC ("[\"DNC\"]" = do not text)
and Phone_N_type/status, Vacant, Absentee.
```
Importer logic:
- Skip rows failing HARD RULE 1 (placeholder/no address).
- Collect non-blank, valid emails (Email_1..6); collect 10-digit phones with DNC flag.
- `company`/`trust` → entity → **exclude from owner-direct outreach** (flag, don't contact).
- Route: any email → **email campaign** (one row per owner, group an owner's multiple
  properties); else any **non-DNC** phone → **GV SMS campaign**; else no reachable channel
  → drop.
- Dedup by `(address, zip)`; suppress any email/phone on the Do-Not-Contact list; only
  generate **net-new** (never already-contacted) outreach.
- Output: `Paragon_Owner_Mailmerge_{DATE}.csv` (`#, Email, Subject, Body, Property_Count`)
  and `GV_Campaign_{DATE}.csv` (columns in HARD RULE 4). Maintain a master
  `owner_leads_consolidated` store for dedup across runs.

---

## 7) SENDING & CAMPAIGN MECHANICS

- **Email:** integrate Gmail API (or an ESP). Send **from the verified alias
  `charlesp@paragongovsolutions.net`** (not the raw Google account). Throttle (~25/run,
  1–4s apart), one-to-one, resumable with per-row Status/SentAt, suppression-aware,
  CAN-SPAM postal address appended. (Today this is a Google-Apps-Script batch sender; the
  app should productize it with a real queue + provider.)
- **SMS / Google Voice:** unique opener per lead, DNC-scrubbed, STOP handling, A2P 10DLC.
- **Inbound handling:** parse seller/agent replies, map them back to the property,
  re-run the deal math, and draft the next human-voice response — never exceeding MAO,
  recommending PASS when they counter above it.
- **Pipeline/CRM:** board with stages (New → Enriched → Offer Sent → Negotiating →
  Under Contract → Assigned/Dispo → Closed/Dead), per-deal numbers, message history, and
  the dispo channel tag.

---

## 8) APP SHAPE (suggested, not prescriptive)

- **Frontend:** web app. Two primary inputs — a single "Work this address" box, and a
  "Bulk upload" drop for CSVs. A results table/board with the deal block per property,
  generated drafts (editable), and one-click "approve & send."
- **Backend:** API service (Python/FastAPI or Node). Modules: `enrich` (data providers +
  LLM research w/ citations), `price` (the §1 math), `classify` (§2/§3), `generate`
  (templates §4, PDF via reportlab/Puppeteer with Paragon branding), `route` (§4 channel
  rules), `campaigns` (dedup/suppression/DNC/batch send §6–7), `inbox` (reply parsing).
- **AI:** use the latest Claude model (e.g. `claude-opus-4-8`) for comp research,
  condition reads from photos/disclosures, classification, and all human-voice copy.
  Encode §1–§5 as the system prompt for those calls so output obeys the rules.
- **Data:** Postgres for leads/deals/campaigns/suppression + object storage for PDFs.
- **Integrations:** skip-trace + comps/AVM provider, Gmail API, SMS/A2P (e.g. Twilio),
  e-sign (DocuSign) for PAs, doubleclose.com POF.

---

## 9) ACCEPTANCE CRITERIA (the app is "done" when…)

1. I paste **one address** → it returns the full deal block (§3), a correct
   retail/distressed/pass verdict, a disciplined opening offer at/under MAO, and a ready
   seller email **or** SMS (correct channel) in human voice, plus a branded PDF offer.
2. I **bulk-upload** a skip-trace CSV → it returns net-new, deduped, suppression- and
   DNC-clean **email** and **GV** campaign CSVs in the exact column formats, entities
   excluded, owners grouped.
3. It **never** drafts on a no-address lead, **never** offers on retail, **never** quotes
   above MAO, **never** texts a DNC number, **never** promises a walkthrough, and **never**
   invents a number that already exists in the data.
4. Every seller/agent message reads like a real person wrote it.
5. Inbound replies get mapped to the property and answered with a disciplined,
   human-voice next step.

> Build it so a non-technical operator (me) just enters addresses and approves what it
> produces. The engine does the analyst, copywriter, and dispatcher work — by these rules.

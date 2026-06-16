# Automation & Systems — Implementation

Covers the 8 items requested, mapped to your actual stack (HubSpot CRM + Google
Voice texting + MaxDispo dispo + this repo's campaign engine).

---

## 1) Zapier automation for new-lead notifications  *(needs your Zapier acct)*
**Goal:** the instant a lead comes in, you get pinged + it lands in HubSpot.

**Build it (10 min):**
1. Zapier → Create Zap → Trigger: **Webhooks by Zapier → Catch Hook**. Copy the
   hook URL → paste into `lead_intake_form.html` (`WEBHOOK_URL`).
2. Action 1: **HubSpot → Create/Update Contact** (map firstname, lastname, phone,
   email).
3. Action 2: **HubSpot → Create Deal** (dealname = property_address, stage =
   Appointment Scheduled, pipeline = Sales).
4. Action 3: **SMS by Zapier** (or **Email**) to your cell:
   *"NEW LEAD: {{firstname}} — {{property_address}} — {{phone}} — {{motivation}}"*.
**Result:** website/intake leads auto-create deals and text you immediately.

Bonus Zap: Trigger **HubSpot → New Deal** → SMS alert (covers leads I create via API too).

## 2) Best CRM for a solo investor
You already use **HubSpot** — keep it. It's free-tier-capable, has the API/MCP we
use to auto-log every deal, and Zapier-connects to everything. REI-specific
alternatives (REsimpli, Podio+GoHighLevel) add built-in skip trace + dialer + SMS,
but they're paid and you'd lose the automation we've already built on HubSpot.
**Verdict: stay on HubSpot; bolt on Google Voice (texting) + Zapier (glue).**

## 3) Seller lead intake form that syncs with CRM  *(BUILT)*
`lead_intake_form.html` — branded cash-offer landing form. Captures name, phone,
email, address, **motivation, condition, timeline**. Host it anywhere (Netlify/
Carrd/your site) and paste your HubSpot Form URL or Zapier hook into `WEBHOOK_URL`.
Submissions → HubSpot deal + (via Zap) instant text to you.

## 4) Top AI tools for automating a wholesaling business
- **HubSpot** — CRM/system of record (you have it).
- **Google Voice / Smarter Contact / Launch Control** — bulk SMS to sellers/agents.
- **PropStream / BatchLeads / DealMachine** — off-market lists + skip trace + comps.
- **Apify** — scraping (Zillow Detail, auction.com) → your lead feed.
- **Zapier / Make** — connect everything, no code.
- **MaxDispo** — your dispo (already in use).
- **This repo + Claude** — dedup, MAO math, campaign + GV build, reply triage,
  offer letters/contracts, follow-up tracking.

## 5) Auto follow-up reminders  *(BUILT + RUNNING)*
`tools/followup_tracker.py` + in-session HubSpot pull. Cadence: offer-out (contract
sent) chased every **2 days**, awaiting-seller every **3**, negotiating every **4**;
2x past due = STALE. Ask me **"run my follow-ups"** any time and I'll pull the live
list. For hands-off reminders, mirror these as **HubSpot Workflows** (Deal stage =
X AND days-since-activity > N → create Task + email you).

## 6) Hottest ZIP codes for flipping/wholesaling (your active metros)
Highest-yield distressed ZIPs from your worked markets (cheap basis, high investor
demand, older stock):
- **Detroit, MI:** 48205, 48224, 48227, 48228, 48234, 48235, 48238
- **Cleveland, OH:** 44105, 44108, 44109, 44110, 44112, 44128
- **Jacksonville, FL:** 32206, 32208, 32209, 32210, 32254, 32208
- **Houston, TX:** 77016, 77026, 77028, 77033, 77051, 77078, 77093
- **Dallas, TX:** 75210, 75215, 75216, 75217, 75227, 75241  (Cruz/Berwick zone)
- **Baltimore, MD:** 21215, 21216, 21217, 21223, 21229
- **Chicago, IL (S/W):** 60619, 60620, 60621, 60624, 60628, 60636, 60644
- **Columbia, SC:** 29203, 29204, 29210, 29223
- **Birmingham AL 35208/35211 · Memphis TN 38108/38114/38127 · Indy 46218/46226 ·
  KC MO 64127/64128 · St. Louis 63113/63115/63120** (untapped — high volume)

## 7) Top states to virtually wholesale in 2025-26
Best for virtual (low friction, high distressed volume, investor-friendly law):
**TX, FL, GA, OH, MI, AL, TN, IN, MO, SC, NC.** Favor: no transfer-tax surprises,
strong rental demand for buy-hold end buyers, lots of pre-1970 stock, and large
absentee-owner pools. You're already in most of these — deepen before adding more.
Be cautious wholesaling in **IL, NJ, OK, SC** where assignment/disclosure rules are
tighter (use assignable contracts + disclose your wholesaler role).

## 8) Find absentee-owned properties with >40% equity  *(needs PropStream/BatchLeads)*
Direct-to-owner, no agents. Pull this filter stack per target ZIP:
- **Owner-occupied = No** (absentee / out-of-state mailing address)
- **Equity ≥ 40%** (ideally ≥ 50% or free-and-clear)
- Overlay any distress: tax-delinquent, pre-foreclosure/NOD, vacant, code
  violation, owned 7+ years, 55+ owner, inherited/probate
- Pull 500-1,000/ZIP → skip trace → ~600 with phone → send me the CSV → I dedup vs
  HubSpot + build the cold-text GV campaign + direct-mail merge.
**This is your biggest untapped well** (the "desperate owner" channel).

---

### What's live now vs. needs your action
| Item | Status |
|---|---|
| 3 Intake form | ✅ built — host it + paste webhook |
| 5 Follow-up tracker | ✅ built + running (ask "run my follow-ups") |
| 6 Hottest ZIPs / 7 Top states | ✅ delivered above |
| 1 Zapier alerts | ⏳ you build the Zap (recipe above) |
| 8 Absentee/equity list | ⏳ you pull from PropStream → I build campaign |
| 2 CRM / 4 AI tools | ✅ answered (stay on HubSpot) |

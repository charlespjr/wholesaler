# SESSION HANDOFF — read this first, then continue the work

> Charles is moving off an old no-internet session. Everything is committed in the
> bundle. This file is the current state + what to do. Read `CLAUDE.md` for the rules
> and the **Autopilot SOP** (it auto-runs the whole workflow). This file is the snapshot.

## 0) First-run setup (do once)
1. **Import the work** (if not already): `git clone paragon_zealous_FULL.bundle` or
   `git fetch <bundle> 'refs/heads/*:refs/remotes/recovered/*'` then check out
   `claude/zealous-tesla-trflw3`.
2. **Push to the REAL GitHub so it's never trapped again** (this env has internet):
   `git push -u origin claude/zealous-tesla-trflw3`. Confirm it shows on github.com.
3. **Verify internet + photo path:** curl any URL (expect 200). Zillow 403s cloud IPs —
   **use Nimble** to pull listing pages/photos. Install deps:
   `pip install -r deal_package_builder/requirements.txt && playwright install chromium`.
4. **Read `CLAUDE.md`** — the Autopilot SOP + all hard rules. Obey them without being asked.

## 1) Standing connections / how outreach actually goes out
- **Email:** Gmail MCP can only **create drafts** (no send). Charles taps Send. Make
  **standalone** drafts (not in-thread replies) for new offers. From-address must be the
  **charlesp@paragongovsolutions.net** alias, not pleasantc@.
- **Bulk email campaigns:** the Apps Script sender `Paragon_BulkSend.gs` (already in
  Charles's Google account) — import the campaign CSV to a Sheet, run `sendBatch`. It
  uses the charlesp@ alias + the `Suppression` tab.
- **Google Voice texts:** inbound arrive in Gmail from `…@txt.voice.google.com`. Reply by
  creating a Gmail draft TO that same address. Phone-only leads → GV campaign CSV.
- **Photos:** never trust a plain fetch for Zillow (403 on cloud IPs) — use Nimble.
- **Approvals:** never send anything externally without Charles's okay. Draft, then ask.

## 2) In-flight work — DO NOT drop these
- **Stephanie (Baton Rouge REO deal flow)** — `incoming_deals_stephanie.csv` has 5:
  2138 Minnesota, 272 W Harrison, 280 Harrison, 180 Harrison, 6040 W Perimeter.
  - Pull BR comps now (Nimble) for rough ARVs; **don't quote** until she sends list price +
    condition.
  - **All REO → close in Paragon's name, double-close, drop "and/or assigns."**
  - Harrison trio: confirm $89,900 is per-door vs bulk, and that they're separate parcels,
    before assuming spread (could be retail).
  - 6040 W Perimeter: deal hinges on the repair number (no sewer/water = utility/septic
    cost) — get the specific cause + confirm vacant + bank's floor.
- **Mary Twitty / AVS Realty** (803-303-0390, info@avsrealtyllc.com):
  - 3961 Live Oak → **under contract, dead.** 336 Byron → retail at $235k list, **pass.**
  - A "send me your distressed/as-is inventory" email to info@avsrealtyllc.com is staged in
    Gmail drafts — confirm it sent; she's a live agent source, keep her fed.
- **5001 Beaucaire St, New Orleans 70129** (Jason Gale, Redfin, 504-356-1663): gut-rehab,
  ARV ~$210k, repairs ~$105k, **open $28k, ceiling $32k.** Package built (photos + VA
  script). NOTE: this deal was **declined 6/17** — re-approach low-key, test new motivation.
- **NEW4 owner campaigns** ready to send: `Paragon_Owner_Mailmerge_NEW4_20260622.csv`
  (151 individual email owners) + `GV_Campaign_Owners_NEW4_20260622.csv` (3 phone-only).
  Load email CSV into the Apps Script Sheet and run; GV via Google Voice.
- **Avia / 205 Parliament Dr, Columbia SC** (TRT, 803-622-1417): ~$95k offer staged in GV
  drafts; if seller counters much above ~$105k it's a pass.
- **Suppression list** (`Suppression_DoNotContact.csv`): jmail6909@, benness313@,
  803soldjustintime@ — never contact.

## 3) The repeating cadence (this is the business)
- **ChatGPT scout sends an `incoming_deals` CSV** → run **Autopilot Trigger A** on each
  (comps→ARV, repairs, MAO/offer, dispo tag, REO check, photos+branded package w/ VA
  script, channel-routed outreach draft) → present for approval.
- **A seller/agent replies** (Gmail or GV) → **Trigger B**: map to property, re-underwrite,
  draft human-voice reply (never above MAO; pass if retail or over MAO).
- **A skip-trace owner list arrives** → **Trigger C**: dedup, suppress, drop LLCs, route
  email vs GV, output campaigns, update `owner_leads_consolidated.json`.

## 4) Key files
- `CLAUDE.md` — rules + Autopilot SOP (read first).
- `deal_package_builder/` — photo→branded PDF tool (VA call script auto-included). Run:
  `python build_deal_packages.py --input incoming_deals.csv --output output`.
- `ChatGPT_to_Claude_handoff_spec.md` — the CSV format ChatGPT outputs.
- `Agent_Call_QA_Playbook.md` — agent Q&A (also auto-embedded in packages).
- `Paragon_BulkSend.gs` — bulk email sender.
- `owner_leads_consolidated.json` — master owner dedup set.

**Bottom line:** read CLAUDE.md, push to real GitHub, then just run the autopilot on what
comes in. Charles approves sends. He should not have to narrate steps again.

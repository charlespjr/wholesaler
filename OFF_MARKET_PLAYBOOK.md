# Off-Market Lead Engine — Owner-Direct (SC)

On-market MLS scraping gives you lowball-offer *targets*. **Off-market, owner-direct is where the real wholesale margin lives** — you reach motivated owners *before* they list, with no agent and no retail pricing. This is the channel that produces the `[OFF-MKT]` deals already in your HubSpot.

## 1. Pick a data source (one is enough to start)
- **PropStream** (recommended) — best filters, comps, and skip trace built in. ~$100/mo.
- **DealMachine** — strong for driving-for-dollars + list building + skip trace.
- **BatchLeads / BatchSkipTracing** — list + skip trace + texting in one.
- **Free/cheap:** county records directly (tax-delinquent rolls, register of deeds, code-enforcement, probate court) + a standalone skip-trace (REISkip, IDI/TLO).

## 2. The lists to pull (highest-converting first)
Pull these for your SC markets (Columbia, Greenville, Charleston, etc.). **Stacking filters = hotter leads.**

| Priority | List / filter | Why it converts |
|---|---|---|
| 1 | **Pre-foreclosure / lis pendens / auction** | Time pressure, must sell |
| 2 | **Tax delinquent** (1+ yrs behind) | Financial distress |
| 3 | **Code violations / condemned** | Owner can't/won't fix |
| 4 | **Probate / inherited / deceased owner** | Heirs want cash, not a project |
| 5 | **Absentee + tired landlord** (owner addr ≠ property; long hold; eviction/section-8) | Done being a landlord |
| 6 | **High equity (50%+) + long tenure (10+ yrs)** | Can sell at a discount and still profit |
| 7 | **Vacant** (USPS vacancy flag) | No one living there = motivated |
| 8 | **Out-of-state owners** | Distance = willingness to offload |

**Best single stack to start:** *Absentee owner + High equity (50%+) + Tenure 10+ yrs* — big, motivated, and able to discount. Layer in vacant/tax-delinquent for the hottest sub-list.

## 3. Skip trace
Run the list through skip tracing (PropStream/Batch/REISkip) to get **owner phone + email** (you're contacting the *owner*, not an agent). Expect 60–80% hit rate.

## 4. Outreach (multi-touch, multi-channel)
Owners are cold — it takes **5–8 touches**. Rotate channels:
- **Text** (via your Google Voice / CoWork flow) — highest response, lowest cost.
- **Cold call / voicemail drop** (RVM).
- **Direct mail** (yellow letter / postcard) — best for skip-trace-fails and high-equity older owners.

⚠️ **Compliance:** cold texting/calling is governed by **TCPA + state law + DNC**. Scrub against the **National DNC registry**, get consent where required, honor STOP immediately, and prefer **direct mail or RVM** for numbers you can't text safely. When in doubt, mail first.

## 5. Owner-direct scripts (cold seller — different from agent outreach)
**Text 1 (intro):**
> "Hi [Owner first name], my name's Charles with Paragon — I buy houses in [City]. Would you consider a cash offer on [Property address]? No agents, no repairs, you pick the closing date. Worth a quick chat?"

**Text 2 (follow-up, 2–3 days later):**
> "Hi [Owner], following up on [Address]. I can pay cash and close on your timeline, as-is — even if it needs work or has tenants. Any interest in a no-obligation number?"

**Voicemail / RVM:**
> "Hi [Owner], this is Charles with Paragon Government Solutions. I'm a local cash buyer interested in [Address] — no agents, no repairs, you choose the date. Call or text me back at [number]. Thanks!"

**Direct mail (postcard):**
> "We buy houses in [City] for cash — any condition, any situation. Need to sell [Address]? Call/text Charles at [number] for a no-obligation cash offer. Close on your timeline."

## 6. Plug into the system you already have
1. **Import** the skip-traced owner list into the app + HubSpot (same CSV import we built — owner = contact, property = deal).
2. **Text** via Google Voice / CoWork using the scripts above.
3. **Responses → offers** (MAO calc) → **contract** (the assignable PSA generator) → **DocuSign**.
4. **Dispo** via assignment / double-close / MaxDispo.

## Weekly rhythm (target ~100+ working leads)
- Pull ~500–1,000 owner records (stacked filters) → skip trace → ~600 with contacts.
- Text in throttled batches (Google Voice 2–3 min apart), mail the rest.
- ~3–5% respond → ~20–40 conversations → a handful of real deals.

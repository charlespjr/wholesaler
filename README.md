# Flipster Lite — Wholesale Deal Machine

A single-file (`index.html`) web CRM for real estate wholesaling. Open
`index.html` in any browser — no build step, no server, no dependencies
beyond the Tailwind + Font Awesome CDNs.

## Features

- **Leads Dashboard** — searchable table of 32 sample listings across major US
  cities, showing Listing Price vs. calculated Wholesale Offer (MAO).
- **Deal modal** — per-lead List Price / Wholesale Offer / ARV breakdown,
  agent contact, click-to-call, and an auto-generated, randomized SMS (with a
  "Shuffle" button) drawn from 12 templates.
- **Lead Finder** — generates Google "dork" search strings
  (`site:zillow.com "<keyword>" "<location>"`) for any zip/city.
- **MAO Calculator** — `(ARV × 0.70) − Repairs − Wholesale Fee`, with a full
  line-item breakdown.
- **Bulk CSV export** — every column plus a ready-to-send personalized SMS per
  row. Exported via Blob (safe for commas, quotes, and `#`).

## Wholesale math

```
Wholesale Offer (MAO) = (Estimated ARV × 0.70) − Estimated Repairs − Wholesale Fee
```

Offers are clamped at $0 so a thin deal never shows a negative number.

## About the data

The 32 rows are **real Zillow listings** found via web search in **June 2026**
(real street address, list price where available, motivation, and a real
listing link). They are a starting point, not a maintained feed — treat them
accordingly:

- **Listings change.** Prices, status (active/pending/sold), and availability
  move fast. Always open the Zillow link to confirm the live state before
  acting. A few addresses sit in an adjacent zip to the target city because the
  exact zip had no distressed inventory at search time.
- **8 listings had no price** in the search snippet — these show "See listing"
  and have no calculated offer until you fill in the real price.
- **28 rows link straight to the exact listing** (`/homedetails/..._zpid/`).
  The other 4 (Houston, Tampa, Jacksonville, Augusta) use an address-search
  fallback because the exact listing URL didn't surface — the address is real,
  so the search lands on or beside the property.
- **Agent name/phone are intentionally blank.** Zillow returns HTTP 403 to
  automated requests and gates agent contact behind JavaScript, so it cannot be
  scraped. Click the Zillow link and Zillow shows the listing agent and a
  contact button. Paste a verified phone into the lead's `contact_phone` field
  if you want click-to-call inside the app.

Before any outreach: confirm the listing is live, get the agent's real contact
from the listing, and make sure you comply with TCPA / carrier rules —
randomized templates personalize a message, they do not make unsolicited bulk
texting compliant. Scraping Zillow directly violates its Terms of Service; the
Lead Finder hands you search links to review manually rather than scraping.

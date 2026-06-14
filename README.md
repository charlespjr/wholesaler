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

## ⚠️ Important — the sample data is NOT verified

The 32 rows are **demonstration data**. Every phone number uses the
`555‑01xx` reserved/non-dialable range and the agent names are placeholders.
**Do not text or call these.** Before any real outreach you must:

1. Pull genuine active listings (the Lead Finder generates the searches).
2. Verify the listing agent's name and number from the actual listing.
3. Confirm you have a lawful basis to contact them and comply with TCPA /
   carrier rules — randomized templates personalize a message, they do not make
   unsolicited bulk texting compliant.

Scraping Zillow directly violates their Terms of Service; the Lead Finder
intentionally hands you search links to review manually rather than scraping.

# Wholesale Deal Package Builder

Extracts **publicly accessible** property photos from Zillow / Redfin listing
pages and assembles a clean, investor-style **wholesale deal-package PDF** per
property — cover, property summary, deal analysis (with MAO math), photo grid,
and a disclaimer. Built for emailing to cash buyers.

> **Access & ethics:** this tool only reads images the public listing page
> already serves. It does **not** log in, solve CAPTCHAs, defeat bot protection,
> or access anything behind a paywall/login. If a page blocks an anonymous
> browser, the PDF is still produced from your property data with a clear
> *"Listing photos could not be retrieved."* note. Photos remain the property of
> their respective owners/listing sources — verify reuse rights before
> redistributing.

---

## Features

- **Robust extraction** (no single brittle selector): renders the page with
  headless Chromium, then runs several independent passes —
  source-specific JSON/state parsing for **Zillow** and **Redfin**, plus generic
  `<img>`/`srcset`, **JSON-LD**, and **Open Graph** fallbacks — and unions the
  results.
- **Highest-resolution** public image variant chosen per photo.
- **De-duplication** via URL normalization **and** perceptual (average-hash)
  image hashing.
- **Filtering**: drops logos, maps, headshots, icons, floor-plans, and
  thumbnails narrower than 600px.
- **Room classification** + priority ordering (front, rear, kitchen, living,
  beds, baths, basement, repair areas, yard, extras) — up to 15 photos.
- **Professional PDF** (US Letter, ReportLab): cover, summary, deal-analysis
  table, 4-up photo grid with captions, **VA agent call script + agent Q&A**
  (auto-built from the deal's numbers — talking points, the "are you
  wholesaling?" answer, objection handling, hard stops), per-page header
  (address) + footer (page numbers), disclaimer page.
- **Batch-safe**: one failing listing never stops the run; a
  `processing_report.csv` records what happened to each property.
- **Degrades gracefully**: works (PDF only) even if Playwright/httpx/pandas are
  not installed.

## Deal math

```
MAO (Maximum Allowable Offer) = (ARV × 0.70) − Repairs − Assignment Fee
Investor purchase price       = Offer + Assignment Fee
Investor profit / spread      = ARV − Repairs − Investor purchase price
```

Missing inputs are shown as **"Not provided"** — the tool never invents numbers.

---

## Setup

Requires **Python 3.11+**.

```bash
cd deal_package_builder
python -m venv .venv && source .venv/bin/activate     # optional but recommended
pip install -r requirements.txt
playwright install chromium                           # one-time browser download
```

## Usage

**Batch (CSV or Excel):**
```bash
python build_deal_packages.py --input properties.csv --output output --max-photos 15
```

**Single listing:**
```bash
python build_deal_packages.py \
  --url "https://www.zillow.com/homedetails/.../84467910_zpid/" \
  --address "5001 Beaucaire St, New Orleans, LA 70129" \
  --output output
```

**Options**

| flag | default | description |
|------|---------|-------------|
| `--input` | – | CSV/Excel file, one property per row |
| `--url` | – | a single Zillow/Redfin listing URL |
| `--address` | "" | address used with `--url` |
| `--output` | `output` | output directory |
| `--max-photos` | `15` | max photos per property |
| `--min-width` | `600` | skip images narrower than this |
| `--no-headless` | off | show the browser window (debugging) |
| `--no-brand` | off | disable Paragon letterhead branding |
| `--logo` | (Paragon) | path to a logo PNG (overrides the default) |
| `--verbose` / `-v` | off | verbose logging |

### Branding

By default every package is produced on **Paragon letterhead** — the logo
(`assets/paragon_logo.png`) on the cover and a footer block (company name,
`11166 Fairfax Blvd, Suite 500, Fairfax, VA 22030`, phone/email, UEI/CAGE) on
every page. Use `--no-brand` for a plain package, or `--logo /path/to/logo.png`
to use a different mark. The contact lines live in `PARAGON_BRAND` in
`build_deal_packages.py`.

## Input columns

Any subset of these (extra columns are ignored; headers are case/space
insensitive):

```
property_address, city, state, zipcode, listing_url, asking_price, offer_price,
arv, repair_estimate, assignment_fee, beds, baths, sqft, year_built, lot_size,
property_type, notes
```

See `properties.sample.csv`.

## Output layout

```
output/
├── deal_packages/
│   └── 5001_Beaucaire_St_New_Orleans_LA_Deal_Package.pdf
├── photos/
│   └── 5001_Beaucaire_St/
│       ├── 01_front_exterior.jpg
│       ├── 02_kitchen.jpg
│       └── ...
└── processing_report.csv
```

`processing_report.csv` columns: `property_address, listing_url, source,
photos_found, photos_downloaded, pdf_created, error_message`.

---

## Project structure

| file | responsibility |
|------|----------------|
| `build_deal_packages.py` | CLI, input parsing, per-property orchestration, report |
| `extractors.py` | Playwright render + Zillow/Redfin/JSON-LD/OG photo extraction |
| `images.py` | download, validate, perceptual dedup, classify, save |
| `pdfgen.py` | ReportLab deal-package PDF |
| `models.py` | `Property` model, money parsing, deal math |

## Notes & limitations

- Listing sites change their markup and actively rate-limit/bot-block. The
  multi-strategy extractor is resilient, but **no scraper is guaranteed** —
  always sanity-check `processing_report.csv`. When a page blocks an anonymous
  browser, you'll get a photo-less PDF (by design).
- Run from inside the `deal_package_builder/` directory (modules import as
  siblings).
- Optional deps degrade gracefully: without `httpx` it uses `urllib`; without
  `pandas` it reads CSV with the stdlib and `.xlsx` via `openpyxl`.

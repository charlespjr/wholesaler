#!/usr/bin/env python3
"""
Auction.com property scraper runner (Apify: parseforge/auction-com-property-scraper).

Scrapes foreclosure + private-seller listings across target metros, then writes
a ranked worksheet with wholesale offer math.

Usage:
    APIFY_TOKEN=apify_xxx python3 tools/run_auction_scraper.py

Token is read from the APIFY_TOKEN env var (never hard-coded). Get one at
https://console.apify.com/account/integrations and rotate it after the run.
"""
import os
import sys
import csv
import re

CITIES = ["Dallas", "Houston", "Columbia SC", "Cleveland", "Baton Rouge", "Chicago"]
SALE_TYPES = ["foreclosures", "private-seller"]
MAX_ITEMS = 50
MIN_BEDS = 2

ACTOR = "parseforge/auction-com-property-scraper"


def money(n):
    try:
        return int(round(float(n)))
    except Exception:
        return None


def calc_offer(arv, repairs=0):
    """MAO = ARV*70% - repairs - $10k fee; opening ~12% under MAO, rounded $500."""
    if not arv:
        return None, None
    mao = arv * 0.70 - repairs - 10000
    if mao <= 0:
        return None, None
    opening = mao * 0.88
    opening = int(round(opening / 500.0) * 500)
    mao = int(round(mao / 500.0) * 500)
    return opening, mao


def main():
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("ERROR: set APIFY_TOKEN env var (https://console.apify.com/account/integrations)")

    try:
        from apify_client import ApifyClient
    except ImportError:
        sys.exit("ERROR: pip install apify-client")

    client = ApifyClient(token)
    all_rows = []

    for city in CITIES:
        print(f"Scraping {city} ...", flush=True)
        run_input = {
            "search_term": city,
            "maxItems": MAX_ITEMS,
            "sale_types": SALE_TYPES,
            "min_beds": MIN_BEDS,
        }
        try:
            run = client.actor(ACTOR).call(run_input=run_input)
            items = client.dataset(run["defaultDatasetId"]).list_items().items
        except Exception as e:
            print(f"  ! {city} failed: {e}", flush=True)
            continue
        print(f"  got {len(items)} items", flush=True)
        for it in items:
            all_rows.append((city, it))

    if not all_rows:
        sys.exit("No results returned. Check token / actor inputs.")

    # Dump raw for inspection
    import json
    with open("auction_raw.json", "w") as f:
        json.dump([{"city": c, **i} for c, i in all_rows], f, indent=2)
    print(f"Wrote auction_raw.json ({len(all_rows)} rows)")

    # Build worksheet — field names are best-effort; adjust after seeing raw keys
    out = "auction_campaign.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(["City", "SaleType", "Address", "Beds", "Baths", "SqFt",
                    "YearBuilt", "EstValue", "OpeningBid", "OpeningOffer",
                    "MAO", "Occupied", "URL"])
        for city, it in all_rows:
            addr = it.get("address") or it.get("propertyAddress") or ""
            est = money(it.get("estimatedValue") or it.get("estMarketValue")
                        or it.get("avm"))
            opening, mao = calc_offer(est)
            w.writerow([
                city,
                it.get("saleType") or it.get("sale_type") or "",
                addr,
                it.get("beds") or it.get("bedrooms") or "",
                it.get("baths") or it.get("bathrooms") or "",
                it.get("sqft") or it.get("squareFootage") or "",
                it.get("yearBuilt") or "",
                est or "",
                it.get("openingBid") or it.get("opening_bid") or "",
                opening or "",
                mao or "",
                it.get("occupancyStatus") or it.get("occupied") or "",
                it.get("url") or it.get("detailUrl") or "",
            ])
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

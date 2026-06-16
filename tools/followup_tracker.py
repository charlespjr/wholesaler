#!/usr/bin/env python3
"""
Follow-up tracker — flags active HubSpot deals that have gone cold.

Two ways to use it:
  1) In-session: Claude queries HubSpot (search_crm_objects) for deals in active
     stages sorted by last-modified, then runs this scoring to produce the
     follow-up list. (No setup needed — just ask "run my follow-ups".)
  2) Standalone: export active deals from HubSpot to a CSV with columns
     dealname, dealstage, hs_lastmodifieddate, amount — then:
        python3 tools/followup_tracker.py deals.csv

Cadence rules (days since last activity before a nudge is due):
    contractsent / decisionmakerboughtin : 2 days  (offer is out — chase hard)
    presentationscheduled                : 3 days  (awaiting agent/seller)
    qualifiedtobuy                        : 4 days  (negotiating)
Anything past 2x its threshold = STALE (escalate or close).
"""
import sys, csv, datetime

CADENCE = {
    "contractsent": 2,
    "decisionmakerboughtin": 2,
    "presentationscheduled": 3,
    "qualifiedtobuy": 4,
}
TODAY = datetime.date.today()

def days_since(iso):
    try:
        d = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
        return (TODAY - d).days
    except Exception:
        return None

def classify(stage, age):
    thr = CADENCE.get(stage, 4)
    if age is None: return ""
    if age >= thr * 2: return "STALE — escalate/close"
    if age >= thr:     return "DUE — follow up now"
    return ""

def run(rows):
    out = []
    for r in rows:
        age = days_since(r.get("hs_lastmodifieddate", ""))
        status = classify(r.get("dealstage", ""), age)
        if status:
            out.append((age, status, r.get("dealname", ""), r.get("dealstage", ""),
                        r.get("amount", "")))
    out.sort(key=lambda x: -(x[0] or 0))
    print(f"{'AGE':>4}  {'STATUS':<22} {'STAGE':<22} DEAL")
    for age, status, name, stage, amt in out:
        print(f"{age:>4}d {status:<22} {stage:<22} {name}")
    print(f"\n{len(out)} deals need attention.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            run(list(csv.DictReader(f)))
    else:
        print("Usage: python3 tools/followup_tracker.py <hubspot_active_deals.csv>")
        print("Or ask Claude to 'run my follow-ups' to pull live from HubSpot.")

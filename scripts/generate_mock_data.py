"""
Generate MOCK campaign exports for a fictional client: "Brightside Fitness" (a fitness app).

The data is deliberately messy, the way real platform exports are:
  - each platform uses different column names and date formats
  - money comes as text with "$" and commas
  - there are blanks, a duplicate row, a "Total" row, and inconsistent campaign names
  - a few REAL problems are planted for the anomaly detector to find

Run:  python scripts/generate_mock_data.py
Output: data/raw/google_ads.csv, data/raw/meta_ads.csv, data/raw/app_installs.csv

All data is invented. Seeded, so it produces the same files every time.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

OUT = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

START = date(2026, 9, 7)   # a Monday
DAYS = 28                  # four full weeks -> week-over-week comparisons work

# campaign -> (base daily spend USD, CTR, click->install rate, revenue per install USD)
GOOGLE = {
    "BS_Search_Brand": (120, 0.060, 0.18, 2.10),
    "BS_UAC_Install":  (300, 0.012, 0.35, 1.40),
}
META = {
    "BS - Prospecting - Video": (250, 0.009, 0.30, 1.20),
    "BS - Retargeting":         (90,  0.020, 0.22, 2.60),
}

# ---- Planted problems (the "answer key" for your anomaly detector) ----
TRACKING_OUTAGE = (date(2026, 9, 29), "BS_UAC_Install")          # spend, but 0 installs
SPEND_SPIKE     = (date(2026, 10, 1), "BS - Prospecting - Video")  # ~3.5x normal spend
MISSING_DAY     = (date(2026, 9, 21), "BS - Retargeting")          # row missing from Meta export


def jitter(x, pct=0.15):
    return x * random.uniform(1 - pct, 1 + pct)


def simulate(base_spend, ctr, cvr, rev_per_install, day_index, multiplier=1.0):
    # gentle upward trend so week-over-week change is visible
    trend = 1 + 0.01 * day_index
    spend = jitter(base_spend * trend) * multiplier
    cpm = jitter(8.0)                      # cost per 1000 impressions
    impressions = int(spend / cpm * 1000)
    clicks = int(impressions * jitter(ctr))
    installs = int(clicks * jitter(cvr))
    revenue = installs * jitter(rev_per_install, 0.3)
    return round(spend, 2), impressions, clicks, installs, round(revenue, 2)


installs_rows = []  # collected from both channels, written to the attribution file

# ---------------- Google Ads export ----------------
g_rows = []
for i in range(DAYS):
    d = START + timedelta(days=i)
    for camp, params in GOOGLE.items():
        spend, imp, clk, inst, rev = simulate(*params, i)
        if (d, camp) == TRACKING_OUTAGE:
            inst, rev = 0, 0.0
        g_rows.append({
            "Day": d.isoformat(),                       # 2026-09-07
            "Campaign": camp,
            "Cost": f"${spend:,.2f}",                   # "$1,234.56" -> text, not a number
            "Impr.": imp,
            "Clicks": clk,
            "Conversions": round(inst * jitter(0.9, 0.1), 1),  # platform's own (unreliable) count
        })
        # attribution tool uses different naming + casing
        installs_rows.append((d, "googleadwords_int", camp.lower() + random.choice(["", " "]), inst, rev))

g_rows.append(g_rows[10].copy())  # duplicate row (export glitch)
total_cost = sum(float(r["Cost"].strip("$").replace(",", "")) for r in g_rows)
g_rows.append({"Day": "Total", "Campaign": "", "Cost": f"${total_cost:,.2f}",
               "Impr.": "", "Clicks": "", "Conversions": ""})  # summary row Google adds

with open(OUT / "google_ads.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(g_rows[0].keys()))
    w.writeheader()
    w.writerows(g_rows)

# ---------------- Meta Ads export ----------------
m_rows = []
for i in range(DAYS):
    d = START + timedelta(days=i)
    for camp, params in META.items():
        mult = 3.5 if (d, camp) == SPEND_SPIKE else 1.0
        spend, imp, clk, inst, rev = simulate(*params, i, multiplier=mult)
        installs_rows.append((d, "Facebook Ads", camp, inst, rev))
        if (d, camp) == MISSING_DAY:
            continue
        m_rows.append({
            "Reporting starts": d.strftime("%d/%m/%Y"),   # 07/09/2026 (day first!)
            "Reporting ends": d.strftime("%d/%m/%Y"),
            "Campaign name": camp,
            "Amount spent (USD)": spend,
            "Impressions": imp,
            "Link clicks": "" if random.random() < 0.06 else clk,  # occasional blanks
            "Results": inst,
        })

with open(OUT / "meta_ads.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(m_rows[0].keys()))
    w.writeheader()
    w.writerows(m_rows)

# ---------------- App install attribution export ----------------
# Source of truth for installs + revenue (ad platforms over/under-count).
random.shuffle(installs_rows)  # exports don't come sorted
with open(OUT / "app_installs.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "media_source", "campaign", "installs", "revenue_usd"])
    for d, src, camp, inst, rev in installs_rows:
        w.writerow([
            d.strftime("%d %b %Y"),                       # 07 Sep 2026
            src,
            camp,
            inst,
            "" if random.random() < 0.04 else rev,        # occasional missing revenue
        ])

print(f"Wrote mock data to {OUT}")
print(f"  google_ads.csv   {len(g_rows)} rows")
print(f"  meta_ads.csv     {len(m_rows)} rows")
print(f"  app_installs.csv {len(installs_rows)} rows")
"""Day 2 tests: each cleaning rule does what it claims."""
import pandas as pd
import pytest

from campaign_report.clean import (
    campaign_key, clean_app_installs, clean_google_ads, clean_meta_ads,
    merge_sources, parse_money,
)
from campaign_report.load import load_all


# --- helpers, tested with tiny hand-made inputs ---

def test_parse_money_strips_symbols():
    result = parse_money(pd.Series(["$1,234.56", "$0.50", ""]))
    assert result[0] == 1234.56
    assert result[1] == 0.50
    assert pd.isna(result[2])


def test_campaign_key_matches_across_platforms():
    names = pd.Series(["BS_Search_Brand", "bs_search_brand ", "BS - Prospecting - Video"])
    assert list(campaign_key(names)) == ["bs_search_brand", "bs_search_brand", "bs_prospecting_video"]


# --- full cleaning on the mock files ---

@pytest.fixture(scope="module")
def cleaned():
    raw = load_all()
    log = []
    google = clean_google_ads(raw["google_ads"], log)
    meta = clean_meta_ads(raw["meta_ads"], log)
    installs = clean_app_installs(raw["app_installs"], log)
    merged = merge_sources(google, meta, installs, log)
    return {"google": google, "meta": meta, "merged": merged, "log": log}


def test_google_total_and_duplicate_removed(cleaned):
    assert len(cleaned["google"]) == 56          # 58 raw - 1 Total - 1 duplicate
    assert not cleaned["google"].duplicated().any()


def test_meta_dates_are_day_first(cleaned):
    assert cleaned["meta"]["date"].min() == pd.Timestamp("2026-09-07")   # not 9 July


def test_merged_has_expected_columns(cleaned):
    assert list(cleaned["merged"].columns) == [
        "date", "channel", "campaign", "campaign_key",
        "spend", "impressions", "clicks", "installs", "revenue",
    ]


def test_every_campaign_has_a_display_name(cleaned):
    assert cleaned["merged"]["campaign"].notna().all()


def test_missing_meta_day_is_kept_visible(cleaned):
    # 21 Sep Retargeting is missing from Meta's export but present in installs:
    # it must survive the merge (with no spend) so the anomaly check can flag it.
    m = cleaned["merged"]
    row = m[(m["date"] == pd.Timestamp("2026-09-21")) & (m["campaign_key"] == "bs_retargeting")]
    assert len(row) == 1
    assert pd.isna(row["spend"].iloc[0])


def test_every_fix_is_logged(cleaned):
    assert len(cleaned["log"]) == 5
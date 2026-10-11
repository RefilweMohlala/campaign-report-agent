"""Day 1 tests: the raw files exist and look the way we expect."""
import pytest

from campaign_report.load import load_all

EXPECTED_COLUMNS = {
    "google_ads": ["Day", "Campaign", "Cost", "Impr.", "Clicks", "Conversions"],
    "meta_ads": ["Reporting starts", "Reporting ends", "Campaign name",
                 "Amount spent (USD)", "Impressions", "Link clicks", "Results"],
    "app_installs": ["date", "media_source", "campaign", "installs", "revenue_usd"],
}


@pytest.fixture(scope="module")
def raw():
    return load_all()


def test_all_sources_load(raw):
    assert set(raw) == set(EXPECTED_COLUMNS)


@pytest.mark.parametrize("source", EXPECTED_COLUMNS)
def test_columns_match_expected(raw, source):
    assert list(raw[source].columns) == EXPECTED_COLUMNS[source]


@pytest.mark.parametrize("source", EXPECTED_COLUMNS)
def test_files_are_not_empty(raw, source):
    assert len(raw[source]) > 0


def test_google_has_total_row_to_clean(raw):
    # Documents a known quirk: cleaning must remove this row.
    assert (raw["google_ads"]["Day"] == "Total").sum() == 1
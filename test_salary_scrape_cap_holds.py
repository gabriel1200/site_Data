import importlib.util
import os
from pathlib import Path

import pandas as pd
import pytest


source = os.environ.get("SALARY_SCRAPE_PATH", str(Path(__file__).with_name("salary_scrape.py")))
spec = importlib.util.spec_from_file_location("salary_scrape_under_test", source)
scraper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper)


def table(cell, header="2026-27", label="Player"):
    return (
        f"<table><thead><tr><th>{label}</th><th>{header}</th></tr></thead>"
        f"<tbody><tr><td>Example</td>{cell}</tr></tbody></table>"
    )


def amount(cell, section):
    frame = pd.DataFrame({"Player": ["Example"], "2026-27": ["raw"]})
    return scraper._parse_table_html_for_salaries(
        frame, table(cell), ["2026-27"], section=section
    ).loc[0, "2026-27"]


def test_active_free_agent_placeholder_remains_zero():
    cell = '<td data-sort="4"><span class="pill-ufa">UFA</span> / $21.9M</td>'
    assert amount(cell, "active") == 0


def test_hold_uses_display_when_sort_value_is_status_code():
    cell = '<td data-sort="4"><span class="pill-ufa">UFA</span> / $21.9M</td>'
    assert amount(cell, "holds") == 21_900_000


def test_hold_prefers_exact_sort_value():
    cell = '<td data-sort="2449421"><span class="pill-rfa">RFA</span> / $2.4M</td>'
    assert amount(cell, "holds") == 2_449_421


def test_summary_keeps_label_and_parses_amount():
    html = table('<td data-sort="31383379">$31.4M</td>', label="CAP")
    frame = pd.DataFrame({"CAP": ["Cap Holds"], "2026-27": ["$31.4M"]})
    parsed = scraper._parse_table_html_for_salaries(
        frame, html, ["2026-27"], section="summary"
    )
    assert parsed.loc[0, "CAP"] == "Cap Holds"
    assert parsed.loc[0, "2026-27"] == 31_383_379


def test_summary_parses_negative_display_fallback():
    assert amount('<td>-$65,091,891</td>', "summary") == -65_091_891


def test_cap_hold_processor_preserves_non_season_columns():
    html = (
        '<table><thead><tr><th>Player</th><th>Pos</th><th>Age</th>'
        '<th>2026-27</th></tr></thead><tbody><tr>'
        '<td>Example</td><td>SG</td><td>30</td>'
        '<td data-sort="4">UFA / $21.9M</td></tr></tbody></table>'
    )
    frame = pd.DataFrame({"Player": ["Example"], "Pos": ["SG"], "Age": [30], "2026-27": ["UFA / $21.9M"]})
    parsed = scraper.process_cap_holds((frame, html), "ATL", id_map={"Example": "123"})
    assert parsed.loc[0, "Pos"] == "SG"
    assert parsed.loc[0, "Age"] == 30
    assert parsed.loc[0, "2026-27"] == 21_900_000


def test_summary_processor_preserves_cap_labels():
    html = table('<td data-sort="31383379">$31.4M</td>', label="CAP")
    frame = pd.DataFrame({"CAP": ["Cap Holds"], "2026-27": ["$31.4M"]})
    parsed = scraper.process_summary((frame, html), "ATL")
    assert parsed.loc[0, "CAP"] == "Cap Holds"
    assert parsed.loc[0, "2026-27"] == 31_383_379


def test_export_guard_rejects_partial_or_unpriced_refresh():
    salary = pd.DataFrame({"Team": ["ATL"], "2026-27": [193_511_432]})
    holds = pd.DataFrame({"Team": ["ATL"], "2026-27": [21_900_000]})
    summary = pd.DataFrame({"Team": ["ATL"], "CAP": ["Cap Holds"], "2026-27": [31_383_379]})
    scraper.validate_required_scrape(salary, holds, summary, ["ATL"])
    with pytest.raises(RuntimeError, match="missing teams"):
        scraper.validate_required_scrape(salary, holds, summary, ["ATL", "BOS"])
    with pytest.raises(RuntimeError, match="No priced cap holds"):
        scraper.validate_required_scrape(salary, holds.assign(**{"2026-27": 0}), summary, ["ATL"])

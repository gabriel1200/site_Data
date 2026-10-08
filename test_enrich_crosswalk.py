"""Regression test: WAIVED rows (placeholder spotrac_id 0) must not all inherit one player's nba_id.

    ../web_app/venv/bin/python -m pytest test_enrich_crosswalk.py -q
"""
import contextlib
import io
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import salary_scrape as S  # noqa: E402


def _enrich(frames, tmp_path):
    crosswalk = pd.DataFrame({
        "spotrac_id": ["10", "0", "0"], "spotrac_name": ["Real Star", "Damian Lillard WAIVED", "DeMar DeRozan WAIVED"],
        "nba_id": [111, 203081, 201942], "bref_id": ["realst01", "lillada01", "derozde01"],
    })
    path = tmp_path / "x.csv"
    crosswalk.to_csv(path, index=False)
    with contextlib.redirect_stdout(io.StringIO()):
        return S.enrich_with_crosswalk(frames, crosswalk_path=str(path))


def test_waived_rows_get_their_own_id_by_name_and_unknown_ones_stay_null(tmp_path):
    salaries = pd.DataFrame({
        "Player": ["Damian Lillard WAIVED", "Real Star", "Klay Thompson WAIVED", "DeMar DeRozan WAIVED"],
        "spotrac_id": [0, 10, 0, 0], "Team": ["MIL", "AAA", "DAL", "SAC"],
    })
    out = _enrich({"nba_salaries.csv": salaries}, tmp_path)["nba_salaries.csv"].set_index("Player")
    assert out.loc["Damian Lillard WAIVED", "nba_id"] == 203081
    assert out.loc["DeMar DeRozan WAIVED", "nba_id"] == 201942          # not Lillard's
    assert pd.isna(out.loc["Klay Thompson WAIVED", "nba_id"])           # not in the crosswalk: unknown, never a wrong id
    assert out.loc["Real Star", "nba_id"] == 111                        # normal id join untouched
    assert out.index.tolist() == ["Damian Lillard WAIVED", "Real Star", "Klay Thompson WAIVED", "DeMar DeRozan WAIVED"]  # row order kept


def test_blank_spotrac_id_rows_in_other_frames_are_matched_by_name_too(tmp_path):
    dead = pd.DataFrame({"Player": ["DeMar DeRozan WAIVED"], "spotrac_id": [float("nan")], "Team": ["SAC"]})
    out = _enrich({"nba_dead_money.csv": dead}, tmp_path)["nba_dead_money.csv"]
    assert out.nba_id.iloc[0] == 201942


# ---- accumulating crosswalk (cross.py) ---------------------------------------------------------

import cross  # noqa: E402


def _index(rows):
    return pd.DataFrame(rows, columns=["player", "bref_id", "nba_id", "year"])


def test_update_crosswalk_keeps_old_mappings_when_a_player_leaves_the_scrape(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _index([("Star One", "star01", 1, 2026), ("Cole Anthony", "anthoco01", 1630175, 2026), ("Klay Thompson", "thompkl01", 202691, 2026)]).to_csv("index_master.csv", index=False)
    first = pd.DataFrame({"Player": ["Star One", "Cole Anthony WAIVED"], "spotrac_id": [10, 0], "Team": ["AAA", "MEM"]})
    with contextlib.redirect_stdout(io.StringIO()):
        cross.update_crosswalk(first, "index_master.csv", "sal_crosswalk.csv", out_dir="figures")
        # next scrape: Cole Anthony's WAIVED row is gone and a different WAIVED player appears
        second = pd.DataFrame({"Player": ["Star One", "Klay Thompson WAIVED"], "spotrac_id": [10, 0], "Team": ["AAA", "DAL"]})
        merged = cross.update_crosswalk(second, "index_master.csv", "sal_crosswalk.csv", out_dir="figures")
    names = set(merged.spotrac_name)
    assert {"Star One", "Cole Anthony WAIVED", "Klay Thompson WAIVED"} <= names   # nothing dropped, new player added
    assert merged.set_index("spotrac_name").loc["Klay Thompson WAIVED", "nba_id"] == 202691


def test_new_row_replaces_the_old_one_for_the_same_real_spotrac_id():
    old = pd.DataFrame({"spotrac_id": ["10", "0"], "spotrac_name": ["Star One", "A WAIVED"], "nba_id": [1, 5]})
    new = pd.DataFrame({"spotrac_id": ["10"], "spotrac_name": ["Star One Jr."], "nba_id": [2]})
    merged = cross.merge_crosswalk(old, new)
    assert merged.spotrac_id.tolist().count("10") == 1 and merged.set_index("spotrac_id").loc["10", "nba_id"] == 2
    assert "A WAIVED" in set(merged.spotrac_name)                                   # unrelated placeholder row survives
    pd.testing.assert_frame_equal(cross.merge_crosswalk(merged, new).reset_index(drop=True), merged.reset_index(drop=True))  # idempotent


# ---- payroll_history_scrape ---------------------------------------------------------------------

import datetime as dt  # noqa: E402
import payroll_history_scrape as payroll  # noqa: E402


def _table(heading, rows, with_pos=True):
    body = "".join(
        f'<tr><td><a href="/nba/player/_/id/{pid}/x">{name}</a></td><td>PG</td><td>25</td><td>{kind}</td><td>{cap}</td><td>5%</td><td>{base}</td></tr>'
        for pid, name, kind, cap, base in rows)
    return (f"<h3>{heading}</h3><table><thead><tr><th>Player (n)</th><th>Pos</th><th>Age</th><th>Type</th><th>Cap Hit</th>"
            f"<th>Cap Hit Pct  League Cap</th><th>Base Salary</th></tr></thead><tbody>{body}</tbody></table>")


def test_payroll_page_is_split_by_section_and_cap_hit_ignores_the_percent_column():
    html = (_table("2019-20 Active Roster Cap", [(1, "Jeff Teague", "", "$19,000,000", "$19,000,000"), (2, "Trae Young", "RK-1ST", "$6,273,000", "$6,273,000")])
            + _table("2019-20 Dead Money Cap", [(3, "Chandler Parsons", "", "$25,102,511", "-")])
            + _table("2019-20 Cap Hold Cap", [(4, "Dewayne Dedmon", "", "$1,500,000", "-")]))
    frame = payroll.parse_payroll_page(html, "ATL", 2019)
    assert frame.groupby("section").cap_hit.sum().to_dict() == {"active": 25_273_000.0, "dead_money": 25_102_511.0, "cap_hold": 1_500_000.0}
    assert set(frame.season_end) == {2020} and frame.spotrac_id.tolist() == ["1", "2", "3", "4"]
    assert frame.loc[frame.player == "Chandler Parsons", "base_salary"].isna().all()   # "-" is missing, not zero


def test_a_page_without_a_full_active_roster_is_not_valid_and_season_arithmetic_is_right():
    thin = payroll.parse_payroll_page(_table("2019-20 Active Roster Cap", [(1, "A", "", "$1", "$1")]), "ATL", 2019)
    assert not payroll.page_is_valid(thin)
    full = payroll.parse_payroll_page(_table("2019-20 Active Roster Cap", [(i, f"P{i}", "", "$1,000,000", "$1,000,000") for i in range(12)]), "ATL", 2019)
    assert payroll.page_is_valid(full)
    assert payroll.last_complete_spot_year(dt.date(2026, 10, 8)) == 2025   # 2025-26 is the latest finished season
    assert payroll.last_complete_spot_year(dt.date(2026, 6, 1)) == 2024    # 2025-26 still in progress in early June


class _Response:
    def __init__(self, status, text=""):
        self.status_code, self.text = status, text


class _Session:
    def __init__(self, *statuses_and_pages):
        self.queue, self.calls = list(statuses_and_pages), 0

    def get(self, url, **kwargs):
        self.calls += 1
        return self.queue.pop(0)


def _full_page():
    rows = [(i, f"P{i}", "", "$1,000,000", "$1,000,000") for i in range(12)]
    return _table("2019-20 Active Roster Cap", rows) + "x" * payroll.MIN_PAGE_BYTES


def test_a_block_is_waited_out_and_retried_but_a_404_is_not(monkeypatch):
    waits = []
    monkeypatch.setattr(payroll.time, "sleep", lambda seconds: waits.append(seconds))
    session = _Session(_Response(403, "x"), _Response(403, "x"), _Response(200, _full_page()))
    frame, status = payroll.fetch_team_year("ATL", 2019, session)
    assert status == "ok" and session.calls == 3 and waits == list(payroll.BLOCK_WAITS[:2])   # 20s then 45s
    gone = _Session(_Response(404, ""))
    frame, status = payroll.fetch_team_year("LAC", 2013, gone)
    assert status.startswith("failed: HTTP 404") and gone.calls == 1                            # no pointless retries
    always = _Session(*[_Response(403, "x")] * 10)
    frame, status = payroll.fetch_team_year("ATL", 2019, always)
    assert status.startswith("failed: HTTP 403") and always.calls == len(payroll.BLOCK_WAITS) + 1   # gives up after the last wait


def test_pacing_slows_down_after_a_block_and_recovers():
    pacing = payroll.Pacing()
    assert pacing.delay() < payroll.SLOW_AFTER_BLOCK                  # normal pace
    pacing.blocked()
    slow = [pacing.delay() for _ in range(payroll.SLOW_PAGES)]
    assert all(d >= payroll.SLOW_AFTER_BLOCK for d in slow)
    assert pacing.delay() < payroll.SLOW_AFTER_BLOCK                  # back to normal afterwards
    assert payroll.SLUGS["LAC"] == "la-clippers"


def test_a_run_limited_to_some_teams_keeps_every_other_cached_team_year(tmp_path, monkeypatch):
    monkeypatch.setattr(payroll, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(payroll, "HERE", str(tmp_path))
    monkeypatch.setattr(payroll.time, "sleep", lambda s: None)
    (tmp_path / "cache").mkdir()
    def frame(team, year):
        return pd.DataFrame([{**{c: None for c in payroll.COLUMNS}, "season_end": year + 1, "spot_year": year, "team": team,
                              "section": "active", "spotrac_id": "1", "player": "P", "cap_hit": 1.0}])
    for team in ("ATL", "BOS"):
        frame(team, 2019).to_csv(tmp_path / "cache" / f"{team}_2019.csv", index=False)
    monkeypatch.setattr(payroll, "fetch_team_year", lambda team, year, session, pacing: (frame(team, year), "ok"))
    history, pages = payroll.run(2019, 2019, force=True, teams=["ATL"])        # only ATL requested
    assert set(history.team) == {"ATL", "BOS"}                                  # BOS stays in the output
    row = pages[(pages.team == "CHI") & (pages.spot_year == 2019)].iloc[0]
    assert row.status.startswith("missing")                                     # and the manifest says what is not loaded


def test_exempt_list_players_are_kept_as_pay_not_dropped_as_unknown():
    html = (_table("2019-20 Active Roster Cap", [(1, "A", "", "$1", "$1")])
            + _table("2019-20 Exempt List Cap", [(2, "Bradley Beal", "FA", "$27,093,019", "$27,093,019")]))
    frame = payroll.parse_payroll_page(html, "WAS", 2019)
    assert frame.set_index("player").loc["Bradley Beal", "section"] == "exempt"

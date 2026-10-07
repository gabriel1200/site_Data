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

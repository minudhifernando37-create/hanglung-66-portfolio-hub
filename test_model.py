"""Sanity tests for the calculation layer. Run with:  python -m pytest -q   (or  python test_model.py)"""

import numpy as np

import data as D
import model as M


def test_store_allocation_sums_exactly():
    for shares in D.MIX_PRESETS.values():
        for total in (200, 247, 250, 300):
            assert M.allocate_stores(shares, total).sum() == total
    assert M.allocate_stores([0, 0, 0], 10).sum() == 10  # all-zero weights fall back to equal


def test_vectorised_frontier_matches_scalar_model():
    cats = M.categories_frame()
    rng = np.random.default_rng(66)
    shares = rng.dirichlet(np.ones(len(cats)) * 1.6, size=5)
    cloud = M.frontier(cats, 250, 0.92, n=5, seed=66)
    for i, s in enumerate(shares):
        r = M.simulate_mix(cats, M.allocate_stores(s, 250), 0.92)
        assert abs(r["gri_rmb_m"] - cloud.loc[i, "gri_rmb_m"]) < 1e-6
        assert abs(r["traffic_m"] - cloud.loc[i, "traffic_m"]) < 1e-6


def test_rent_is_higher_of_base_or_turnover():
    cats = M.categories_frame()
    r = M.simulate_mix(cats, M.allocate_stores(D.MIX_PRESETS["Luxury-led"], 250), 0.92)
    t = r["table"]
    assert (t["rent_psm_year"] >= t["base_rent"] * 12 - 1e-9).all()


def test_ramp_reaches_stabilised_gri():
    ramp = M.ramp_up(600, 0.91, 0.98, 12)
    assert abs(ramp["gri_rmb_m"].iloc[-1] * 12 - 600) < 1e-6
    assert ramp["gri_rmb_m"].is_monotonic_increasing


def test_coverage_timeline_matches_public_chronology():
    tl = M.coverage_timeline()
    assert tl["covered"].iloc[-1] == 11
    assert str(tl["switch_date"].iloc[0].date()) == "2021-12-01"   # Spring City 66
    assert str(tl["switch_date"].iloc[-1].date()) == "2026-10-01"  # Riverside 66


def test_no_grid_power_after_full_coverage():
    e = M.monthly_energy()
    assert e.loc[e["month"] >= "2026-10-01", "grid_mwh"].sum() == 0


def test_implied_emission_factor():
    assert abs(D.IMPLIED_GRID_EF - 227_513 / 440_655) < 1e-12


def test_city_scores_bounded_and_ranked():
    s = M.score_cities(M.cities_frame(), {"lci": 4, "whitespace": 3, "hnwi": 2, "growth_idx": 2, "connect": 1})
    assert s["score"].between(0, 100).all()
    assert s["score"].is_monotonic_decreasing


def test_leaderboard_and_levels():
    logs = M.seed_logs()
    board = M.leaderboard(logs)
    assert len(board) == len(D.TENANTS)
    assert abs(board["points"].sum() - logs["points"].sum()) < 1e-6
    assert M.level_for(0)[0] == "Foundational"
    assert M.level_for(D.LEVELS[1][0])[0] == "Advanced"
    assert M.level_for(10_000) == ("Changemaker Elite", None, 1.0)


def test_new_log_moves_points_and_badges():
    logs = M.seed_logs()
    tenant = D.TENANTS[0][0]
    row = M.make_log("2026-10-20", tenant, "Shipping pallets recycled", 120)
    assert row["points"] == 600
    import pandas as pd
    logs2 = pd.concat([logs, pd.DataFrame([row])], ignore_index=True)
    assert "Circularity Pioneer" in M.badges_for(logs2[logs2["tenant"] == tenant])


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
    print(f"{len(tests)} tests passed")

"""
Calculation layer for the hub. Pure pandas/numpy - no Streamlit - so every number the
app shows can be tested on its own (see test_model.py).
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

import data as D

# ======================================================================================
# Module 1A - Retail mix planner
# ======================================================================================

def categories_frame() -> pd.DataFrame:
    """Editable assumptions table for the retail categories."""
    return pd.DataFrame(
        D.RETAIL_CATEGORIES,
        columns=["category", "gla_sqm", "base_rent", "sales_density", "turnover_pct", "draw_k"],
    )


def allocate_stores(shares, total: int) -> np.ndarray:
    """Turn category shares into whole store counts that sum exactly to `total`
    (largest-remainder rounding)."""
    shares = np.asarray(shares, dtype=float)
    if shares.sum() <= 0:
        shares = np.ones_like(shares)
    shares = shares / shares.sum()
    raw = shares * total
    counts = np.floor(raw).astype(int)
    remainder = total - counts.sum()
    order = np.argsort(-(raw - counts))
    counts[order[:remainder]] += 1
    return counts


def simulate_mix(cats: pd.DataFrame, counts, leasing_rate: float = 0.92) -> dict:
    """Estimate foot traffic and gross rental income (GRI) for a tenant mix.

    Mechanics (all illustrative, explained in the app's assumptions panel):
      * Rent per store = GLA x max(base rent, turnover % x sales density)
        - the usual "higher of base or turnover rent" lease structure.
      * Anchor halo: luxury anchors lift sales density of the other luxury-adjacent
        categories (jewellery, lifestyle, beauty) by up to +25%.
      * Traffic per category has diminishing returns (count ** 0.85): the 60th
        café adds less traffic than the 6th.
      * Dwell synergy: F&B + experiential GLA share near 35-45% maximises dwell
        time, which multiplies traffic (peak +15%) and lifts F&B sales.
      * Only leased stores generate rent and traffic (x leasing rate).
    """
    c = cats.copy().reset_index(drop=True)
    c["stores"] = np.asarray(counts, dtype=float)
    c["gla_total"] = c["stores"] * c["gla_sqm"]
    total_gla = c["gla_total"].sum()
    total_stores = c["stores"].sum()

    def share_of_gla(*names):
        if total_gla == 0:
            return 0.0
        return c.loc[c["category"].isin(names), "gla_total"].sum() / total_gla

    anchor_share_stores = (
        c.loc[c["category"] == "Luxury Anchor", "stores"].sum() / total_stores if total_stores else 0.0
    )
    halo = 1 + min(0.25, 2.0 * anchor_share_stores)

    leisure_share = share_of_gla("High-End F&B", "Experiential & Culture")
    # Bell-shaped synergy centred on 40% leisure GLA share
    dwell = 1 + 0.15 * np.exp(-((leisure_share - 0.40) ** 2) / (2 * 0.10 ** 2))

    sales = c["sales_density"].astype(float).copy()
    halo_cats = c["category"].isin(["Jewellery & Watches", "Premium Lifestyle", "Beauty & Wellness"])
    sales[halo_cats] *= halo
    sales[c["category"] == "High-End F&B"] *= dwell

    rent_psm_year = np.maximum(c["base_rent"] * 12, c["turnover_pct"] * sales)
    c["rent_psm_year"] = rent_psm_year
    c["gri_rmb_m"] = c["gla_total"] * rent_psm_year * leasing_rate / 1e6
    c["traffic_m"] = (c["stores"] ** 0.85) * c["draw_k"] * leasing_rate * dwell / 1e3

    gri = c["gri_rmb_m"].sum()
    traffic = c["traffic_m"].sum()
    return {
        "table": c,
        "gri_rmb_m": gri,
        "traffic_m": traffic,
        "total_gla": total_gla,
        "gri_per_sqm": (gri * 1e6 / (total_gla * leasing_rate)) if total_gla else 0.0,
        "fnb_share_stores": (
            c.loc[c["category"] == "High-End F&B", "stores"].sum() / total_stores if total_stores else 0.0
        ),
        "leisure_share_gla": leisure_share,
        "halo": halo,
        "dwell": dwell,
    }


def frontier(cats: pd.DataFrame, total_stores: int, leasing_rate: float, n: int = 1500, seed: int = 66):
    """Sample random tenant mixes to show the traffic vs. rent trade-off space."""
    rng = np.random.default_rng(seed)
    k = len(cats)
    shares = rng.dirichlet(np.ones(k) * 1.6, size=n)
    # vectorised largest-remainder rounding
    raw = shares * total_stores
    counts = np.floor(raw)
    rem = (total_stores - counts.sum(axis=1)).astype(int)
    order = np.argsort(-(raw - counts), axis=1)
    for i in range(n):
        counts[i, order[i, :rem[i]]] += 1

    names = cats["category"].to_numpy()
    gla = cats["gla_sqm"].to_numpy(float)
    base = cats["base_rent"].to_numpy(float)
    sales0 = cats["sales_density"].to_numpy(float)
    turn = cats["turnover_pct"].to_numpy(float)
    draw = cats["draw_k"].to_numpy(float)

    gla_tot = counts * gla
    total_gla = gla_tot.sum(axis=1)
    anchor = (names == "Luxury Anchor")
    halo = 1 + np.minimum(0.25, 2.0 * counts[:, anchor].sum(axis=1) / total_stores)
    leisure_mask = np.isin(names, ["High-End F&B", "Experiential & Culture"])
    leisure = np.where(total_gla > 0, gla_tot[:, leisure_mask].sum(axis=1) / np.maximum(total_gla, 1), 0)
    dwell = 1 + 0.15 * np.exp(-((leisure - 0.40) ** 2) / (2 * 0.10 ** 2))

    sales = np.tile(sales0, (n, 1))
    halo_mask = np.isin(names, ["Jewellery & Watches", "Premium Lifestyle", "Beauty & Wellness"])
    sales[:, halo_mask] *= halo[:, None]
    fnb = names == "High-End F&B"
    sales[:, fnb] *= dwell[:, None]
    rent = np.maximum(base * 12, turn * sales)
    gri = (gla_tot * rent).sum(axis=1) * leasing_rate / 1e6
    traffic = ((counts ** 0.85) * draw).sum(axis=1) * leasing_rate * dwell / 1e3
    return pd.DataFrame({"traffic_m": traffic, "gri_rmb_m": gri, "total_gla": total_gla})


def ramp_up(annual_gri: float, open_leasing: float, stable_leasing: float,
            months_to_stabilise: int, start_trading_share: float = 0.70,
            horizon: int = 24, open_date: date = D.PUBLIC_FACTS["westlake_open_date"]) -> pd.DataFrame:
    """Monthly GRI ramp after opening. Tenants open in phases (trading share rises to
    100%) while leasing climbs from the opening rate to the stabilised rate.

    `annual_gri` is the stabilised annual GRI at `stable_leasing`."""
    months = np.arange(horizon + 1)
    progress = np.clip(months / max(months_to_stabilise, 1), 0, 1)
    # smooth S-curve
    s = 3 * progress ** 2 - 2 * progress ** 3
    leasing = open_leasing + (stable_leasing - open_leasing) * s
    trading = start_trading_share + (1 - start_trading_share) * s
    monthly = annual_gri / 12 * (leasing / stable_leasing) * trading
    dates = pd.date_range(pd.Timestamp(open_date).to_period("M").to_timestamp(), periods=horizon + 1, freq="MS")
    return pd.DataFrame({
        "month": dates,
        "leasing_rate": leasing,
        "trading_share": trading,
        "gri_rmb_m": monthly,
        "cumulative_gri_rmb_m": monthly.cumsum(),
    })


# ======================================================================================
# Module 1B - Expansion matrix
# ======================================================================================

CITY_COLS = ["city", "lat", "lon", "tier", "has_66", "lci", "supply", "hnwi", "growth", "connect"]


def cities_frame() -> pd.DataFrame:
    return pd.DataFrame(D.CITIES, columns=CITY_COLS)


def market_feed(months: int = 18, seed: int = 66, end: date | None = None) -> pd.DataFrame:
    """Mock monthly 'live' indicator feed: each city's indices random-walk around their
    base level (mean-reverting), so the dashboard has something to track over time."""
    rng = np.random.default_rng(seed)
    base = cities_frame()
    end = end or date.today()
    dates = pd.date_range(end=pd.Timestamp(end).to_period("M").to_timestamp(), periods=months, freq="MS")
    out = []
    for _, row in base.iterrows():
        lci, supply, growth = float(row.lci), float(row.supply), float(row.growth)
        # walk backwards from today's base value so the latest month equals the base
        lci_s, sup_s, gr_s = [lci], [supply], [growth]
        for _ in range(months - 1):
            lci_s.append(np.clip(lci_s[-1] - rng.normal(0.35, 1.2), 20, 100))
            sup_s.append(np.clip(sup_s[-1] - rng.normal(0.25, 0.8), 10, 100))
            gr_s.append(gr_s[-1] - rng.normal(0.0, 0.35))
        for d, a, b, g in zip(dates, lci_s[::-1], sup_s[::-1], gr_s[::-1]):
            out.append((row.city, d, a, b, g))
    return pd.DataFrame(out, columns=["city", "month", "lci", "supply", "growth"])


def score_cities(df: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """Weighted attractiveness score (0-100).

    Supply is inverted: a saturated premium mixed-use market scores LOW ("whitespace").
    Growth (% YoY) is rescaled 0-100 across the city set.
    """
    d = df.copy()
    g = d["growth"]
    d["growth_idx"] = 100 * (g - g.min()) / (g.max() - g.min()) if g.max() > g.min() else 50.0
    d["whitespace"] = 100 - d["supply"]
    parts = {
        "lci": d["lci"],
        "whitespace": d["whitespace"],
        "hnwi": d["hnwi"],
        "growth_idx": d["growth_idx"],
        "connect": d["connect"],
    }
    total_w = sum(weights.values()) or 1.0
    d["score"] = sum(parts[k] * w for k, w in weights.items()) / total_w
    d["rank"] = d["score"].rank(ascending=False, method="min").astype(int)
    return d.sort_values("score", ascending=False).reset_index(drop=True)


def quadrant(lci: float, whitespace: float, lci_cut: float = 70, ws_cut: float = 45) -> str:
    if lci >= lci_cut and whitespace >= ws_cut:
        return "Ripe for a 66"
    if lci >= lci_cut:
        return "Strong demand, crowded"
    if whitespace >= ws_cut:
        return "Open field, demand building"
    return "Watch list"


# ======================================================================================
# Module 2A - Renewable transition tracker
# ======================================================================================

def properties_frame() -> pd.DataFrame:
    rows = []
    for name, city, prov, (y, m), note in D.PROPERTIES:
        mwh, wind, (oy, om) = D.PROPERTY_ENERGY[name]
        rows.append({
            "property": name, "city": city, "province": prov,
            "switch_date": pd.Timestamp(y, m, 1), "milestone": note,
            "annual_mwh": mwh, "wind_share": wind, "open_date": pd.Timestamp(oy, om, 1),
        })
    return pd.DataFrame(rows)


def coverage_timeline() -> pd.DataFrame:
    """Cumulative number of properties on 100% renewable electricity (public chronology)."""
    p = properties_frame().groupby("switch_date")["property"].apply(list).reset_index()
    p["added"] = p["property"].apply(len)
    p["covered"] = p["added"].cumsum()
    p["names"] = p["property"].apply(", ".join)
    return p[["switch_date", "added", "covered", "names"]]


def monthly_energy(start="2021-01-01", end="2026-12-01", seed: int = 66) -> pd.DataFrame:
    """Illustrative monthly electricity by property and source (grid / wind / solar).

    A property is 100% grid before its switch month and 100% renewable after it.
    Consumption has a summer-cooling peak, and a new property ramps up after opening.
    """
    rng = np.random.default_rng(seed)
    props = properties_frame()
    months = pd.date_range(start, end, freq="MS")
    season = 1 + 0.18 * np.cos((months.month - 7.5) / 12 * 2 * np.pi)  # peak Jul/Aug
    rows = []
    for _, p in props.iterrows():
        base = p.annual_mwh / 12
        noise = rng.normal(1, 0.025, len(months))
        for i, m in enumerate(months):
            if m < p.open_date:
                continue
            age_m = (m.year - p.open_date.year) * 12 + (m.month - p.open_date.month)
            ramp = min(1.0, 0.45 + 0.55 * age_m / 12) if age_m < 12 else 1.0
            mwh = base * season[i] * noise[i] * ramp
            if m >= p.switch_date:
                wind, solar, grid = mwh * p.wind_share, mwh * (1 - p.wind_share), 0.0
            else:
                wind, solar, grid = 0.0, 0.0, mwh
            rows.append((p.property, m, grid, wind, solar))
    df = pd.DataFrame(rows, columns=["property", "month", "grid_mwh", "wind_mwh", "solar_mwh"])
    df["total_mwh"] = df[["grid_mwh", "wind_mwh", "solar_mwh"]].sum(axis=1)
    return df


def green_premium(annual_mwh: float, premium_rmb_per_mwh: float, efficiency_cut: float,
                  tariff_rmb_per_mwh: float) -> dict:
    """What tenant energy efficiency is worth once supply is already 100% renewable."""
    saved_mwh = annual_mwh * efficiency_cut
    premium_cost = annual_mwh * premium_rmb_per_mwh / 1e6
    saved_rmb_m = saved_mwh * (tariff_rmb_per_mwh + premium_rmb_per_mwh) / 1e6
    location_t = saved_mwh * D.IMPLIED_GRID_EF
    return {
        "saved_mwh": saved_mwh,
        "premium_cost_rmb_m": premium_cost,
        "saved_rmb_m": saved_rmb_m,
        "location_based_t": location_t,
    }


# ======================================================================================
# Module 2B / 2C - Changemakers portal & leaderboard
# ======================================================================================

LOG_COLS = ["date", "tenant", "property", "activity", "pillar", "quantity", "unit",
            "points", "kg_co2e", "note"]


def make_log(day, tenant: str, activity: str, quantity: float, note: str = "") -> dict:
    pillar, unit, pts, kg = D.ACTIVITIES[activity]
    prop = next(t[2] for t in D.TENANTS if t[0] == tenant)
    return {
        "date": pd.Timestamp(day), "tenant": tenant, "property": prop, "activity": activity,
        "pillar": pillar, "quantity": float(quantity), "unit": unit,
        "points": round(quantity * pts, 1), "kg_co2e": round(quantity * kg, 1), "note": note,
    }


def seed_logs(today: date | None = None, seed: int = 66) -> pd.DataFrame:
    """Mock season of activity for the fictional tenants (last 90 days)."""
    rng = np.random.default_rng(seed)
    today = today or date.today()
    typical = {  # sensible quantity ranges per activity
        "Lighting schedule optimisation": (150, 900),
        "LED / display lighting retrofit": (400, 2_500),
        "HVAC set-point optimisation": (300, 1_800),
        "Shipping pallets recycled": (4, 30),
        "Packaging take-back": (20, 160),
        "Food waste diverted": (25, 140),
        "Staff sustainability training": (4, 25),
        "Community volunteering": (2, 12),
    }
    acts = list(D.ACTIVITIES)
    rows = []
    for name, _cat, _prop, bias in D.TENANTS:
        n = int(rng.integers(6, 19))
        weights = np.array([3.0 if D.ACTIVITIES[a][0] == bias else 1.0 for a in acts])
        # F&B tenants are the ones with food waste; offices have no pallets
        for i, a in enumerate(acts):
            if a == "Food waste diverted" and _cat != "F&B":
                weights[i] = 0.0
            if a == "Shipping pallets recycled" and _cat == "Office":
                weights[i] = 0.0
        weights /= weights.sum()
        for _ in range(n):
            a = acts[rng.choice(len(acts), p=weights)]
            lo, hi = typical[a]
            q = float(rng.integers(lo, hi + 1))
            day = today - timedelta(days=int(rng.integers(1, 91)))
            rows.append(make_log(day, name, a, q))
    return pd.DataFrame(rows, columns=LOG_COLS).sort_values("date").reset_index(drop=True)


def level_for(points: float) -> tuple[str, str | None, float]:
    """Return (current level, next level, progress 0-1 towards next)."""
    current, nxt, lo, hi = D.LEVELS[0][1], None, 0, None
    for i, (threshold, name) in enumerate(D.LEVELS):
        if points >= threshold:
            current, lo = name, threshold
            if i + 1 < len(D.LEVELS):
                nxt, hi = D.LEVELS[i + 1][1], D.LEVELS[i + 1][0]
            else:
                nxt, hi = None, None
    progress = 1.0 if hi is None else (points - lo) / (hi - lo)
    return current, nxt, float(np.clip(progress, 0, 1))


def badges_for(logs: pd.DataFrame) -> list[str]:
    """Badges earned by a single tenant's logs."""
    if logs.empty:
        return []
    q = logs.groupby("activity")["quantity"].sum()
    get = lambda a: float(q.get(a, 0.0))
    lighting = get("Lighting schedule optimisation") + get("LED / display lighting retrofit")
    energy = lighting + get("HVAC set-point optimisation")
    earned = ["First Step"]
    if lighting >= 1_000:
        earned.append("Lightwise Champion")
    if energy >= 5_000:
        earned.append("Energy Saver")
    if get("Shipping pallets recycled") >= 100 or get("Packaging take-back") >= 500:
        earned.append("Circularity Pioneer")
    if get("Food waste diverted") >= 300:
        earned.append("Zero-Waste Kitchen")
    if get("Community volunteering") >= 20:
        earned.append("Community Builder")
    if logs["pillar"].nunique() == len(D.PILLARS):
        earned.append("All-Rounder")
    return earned


def leaderboard(logs: pd.DataFrame) -> pd.DataFrame:
    """One row per tenant: points by pillar, total, carbon, level, badges, rank."""
    tenants = pd.DataFrame(D.TENANTS, columns=["tenant", "category", "property", "_bias"]).drop(columns="_bias")
    if logs.empty:
        pts = pd.DataFrame(columns=D.PILLARS)
    else:
        pts = logs.pivot_table(index="tenant", columns="pillar", values="points", aggfunc="sum", fill_value=0)
    for p in D.PILLARS:
        if p not in pts.columns:
            pts[p] = 0.0
    pts = pts[D.PILLARS]
    board = tenants.merge(pts, left_on="tenant", right_index=True, how="left").fillna({p: 0.0 for p in D.PILLARS})
    board["points"] = board[D.PILLARS].sum(axis=1)
    carbon = logs.groupby("tenant")["kg_co2e"].sum() / 1000 if not logs.empty else pd.Series(dtype=float)
    board["t_co2e"] = board["tenant"].map(carbon).fillna(0.0)
    actions = logs.groupby("tenant").size() if not logs.empty else pd.Series(dtype=int)
    board["actions"] = board["tenant"].map(actions).fillna(0).astype(int)
    board["level"] = board["points"].apply(lambda p: level_for(p)[0])
    board["badges"] = board["tenant"].apply(lambda t: len(badges_for(logs[logs["tenant"] == t])) if not logs.empty else 0)
    board = board.sort_values(["points", "actions"], ascending=False).reset_index(drop=True)
    board["rank"] = np.arange(1, len(board) + 1)
    return board

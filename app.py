"""
Hang Lung "66 Portfolio" Growth & Decarbonization Hub
Independent concept prototype - Streamlit + pandas + plotly.

Run locally:   streamlit run app.py
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import data as D
import model as M

st.set_page_config(
    page_title="66 Portfolio Hub",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------------------
# Design tokens (validated categorical palette, light surface)
# --------------------------------------------------------------------------------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
NEUTRAL_FILL = "#d6d4cc"
S1, S2, S3, S4, S5, S6 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"
CATEGORY_COLORS = dict(zip([c[0] for c in D.RETAIL_CATEGORIES], [S1, S2, S3, S4, S5, S6]))
PILLAR_COLORS = {"Energy": S1, "Waste & Circularity": S2, "Community": S3}
FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"

st.markdown(
    """
    <style>
      .block-container {padding-top: 2rem; max-width: 1280px;}
      .tag {display:inline-block; font-size:0.72rem; font-weight:600; letter-spacing:.02em;
            padding:2px 8px; border-radius:999px; margin-right:6px; vertical-align:middle;}
      .tag-public {background:#e6f0fb; color:#184f95;}
      .tag-mock   {background:#f3efe4; color:#6b5a1e;}
      .eyebrow {font-size:0.78rem; letter-spacing:.08em; text-transform:uppercase; color:#52514e;
                font-weight:600; margin-bottom:-0.4rem;}
      .badge {display:inline-block; padding:4px 10px; border-radius:8px; margin:0 6px 6px 0;
              font-size:0.82rem; border:1px solid rgba(11,11,11,.10);}
      .badge-on  {background:#e8f5ee; color:#0b4d2c;}
      .badge-off {background:#f4f3f0; color:#898781;}
      div[data-testid="stMetricValue"] {font-size: 1.6rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def tag(kind: str) -> str:
    return (
        '<span class="tag tag-public">Public data</span>' if kind == "public"
        else '<span class="tag tag-mock">Mock / illustrative</span>'
    )


def header(eyebrow: str, title: str, intent: str, tags=("mock",)):
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(" ".join(tag(t) for t in tags) + f" &nbsp; {intent}", unsafe_allow_html=True)
    st.write("")


def style(fig: go.Figure, title: str | None = None, height: int = 380, legend: bool = True) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0, xanchor="left", font=dict(size=15, color=INK)) if title else None,
        height=height,
        font=dict(family=FONT, size=12, color=INK_2),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        margin=dict(l=8, r=8, t=48 if title else 16, b=8),
        hoverlabel=dict(bgcolor="white", bordercolor=AXIS, font=dict(family=FONT, size=12, color=INK)),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, title=None),
        barcornerradius=4,
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=AXIS, zeroline=False, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, linecolor=AXIS, zeroline=False, tickfont=dict(color=MUTED))
    return fig


def show(fig: go.Figure):
    st.plotly_chart(fig, config={"displayModeBar": False})


def rmb_m(x: float) -> str:
    return f"RMB {x:,.0f}m"


# --------------------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------------------
PAGES = [
    "Overview",
    "1A · Westlake 66 Retail Mix Planner",
    "1B · Mainland Expansion Matrix",
    "2A · Renewable Transition Tracker",
    "2B · Changemakers Tenant Portal",
    "2C · Green Changemaker Leaderboard",
]

if "page" not in st.session_state:
    st.session_state.page = PAGES[0]
if "logs" not in st.session_state:
    st.session_state.logs = M.seed_logs()
if "feed_seed" not in st.session_state:
    st.session_state.feed_seed = 66


@st.cache_data(show_spinner=False)
def cached_frontier(cats: pd.DataFrame, total: int, leasing: float) -> pd.DataFrame:
    return M.frontier(cats, total, leasing)


def goto(page: str):
    st.session_state.page = page


# --------------------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ◆ 66 Portfolio Hub")
    st.caption("Growth & Decarbonization")
    st.radio("Navigate", PAGES, key="page", label_visibility="collapsed")
    st.divider()
    st.caption(
        "Independent concept prototype by Minudhi Fernando. Not affiliated with or endorsed by "
        "Hang Lung Properties. Figures tagged *Public data* come from Hang Lung's published "
        "releases; everything tagged *Mock / illustrative* is an assumption for demonstration."
    )


# ======================================================================================
# Overview
# ======================================================================================
def page_overview():
    header(
        "Concept prototype",
        "66 Portfolio Growth & Decarbonization Hub",
        "An asset-management and sustainability portal built around Hang Lung's two live priorities: "
        "launching premium mixed-use destinations, and running them on clean energy with tenants.",
        tags=("public",),
    )

    f = D.PUBLIC_FACTS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Westlake 66 retail leasing at opening", ">90%", help="~250 stores, opened 28 Apr 2026")
    c2.metric("Mainland properties on 100% renewable power", f"{f['mainland_properties']} / 11",
              help="Riverside 66 completed coverage on 1 Oct 2026")
    c3.metric("Renewable electricity procured, 2026E", f"{f['re_mwh_2026e']:,} MWh")
    c4.metric("GHG emissions avoided, 2026E", f"{f['ghg_avoided_t_2026e']:,} t")

    st.write("")
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown("#### Module 1 · Premium mixed-use launch & optimisation")
            st.markdown(
                "Built on the Westlake 66 launch and the *Pulse of the City* positioning: how a tenant mix "
                "drives footfall and rental income, how a new mall ramps to stabilisation, and which "
                "Mainland city is ripe for the next 66."
            )
            b1, b2 = st.columns(2)
            b1.button("Retail Mix Planner →", on_click=goto, args=(PAGES[1],), use_container_width=True)
            b2.button("Expansion Matrix →", on_click=goto, args=(PAGES[2],), use_container_width=True)
    with right:
        with st.container(border=True):
            st.markdown("#### Module 2 · Renewable portfolio & Changemakers")
            st.markdown(
                "The 100% renewable target for the Mainland portfolio was **delivered on 1 Oct 2026**. "
                "So the tracker looks back at the five-year transition and forward to the next lever: "
                "tenant energy efficiency, driven through a gamified Changemakers portal."
            )
            b1, b2, b3 = st.columns(3)
            b1.button("Renewables →", on_click=goto, args=(PAGES[3],), use_container_width=True)
            b2.button("Tenant portal →", on_click=goto, args=(PAGES[4],), use_container_width=True)
            b3.button("Leaderboard →", on_click=goto, args=(PAGES[5],), use_container_width=True)

    st.write("")
    with st.expander("How the data works"):
        st.markdown(
            f"""
- {tag('public')} Headline facts (Westlake 66 opening, leasing rate, store count, the renewable
  chronology for all 11 Mainland properties, MWh procured, emissions avoided) come from Hang Lung's
  press releases and investor materials listed below.
- {tag('mock')} Tenant economics, city indices, per-property energy splits, tenant names and
  activity logs are illustrative assumptions. Each page shows which is which, and the
  assumptions are editable where it matters.
- The implied grid emission factor used for carbon estimates is derived from the two public
  2026E figures: {f['ghg_avoided_t_2026e']:,} t ÷ {f['re_mwh_2026e']:,} MWh =
  **{D.IMPLIED_GRID_EF:.3f} tCO₂e/MWh**.
            """,
            unsafe_allow_html=True,
        )
        st.markdown("**Sources**")
        for title, url in D.SOURCES:
            st.markdown(f"- [{title}]({url})")


# ======================================================================================
# 1A - Retail mix planner
# ======================================================================================
CAT_NAMES = [c[0] for c in D.RETAIL_CATEGORIES]


def apply_preset():
    shares = D.MIX_PRESETS[st.session_state.preset]
    for name, s in zip(CAT_NAMES, shares):
        st.session_state[f"mix_{name}"] = int(round(s * 100))


def page_retail():
    header(
        "Module 1A",
        "Westlake 66 Retail Mix Planner",
        "Simulate how the ~250-store tenant mix shifts footfall and gross rental income (GRI), "
        "and how the mall ramps to stabilisation after its 28 Apr 2026 opening.",
        tags=("public", "mock"),
    )

    if "preset" not in st.session_state:
        st.session_state.preset = list(D.MIX_PRESETS)[0]
        apply_preset()

    cats = M.categories_frame()

    ctrl, out = st.columns([1, 2.2], gap="large")
    with ctrl:
        st.selectbox("Start from a scenario", list(D.MIX_PRESETS), key="preset", on_change=apply_preset)
        total = st.slider("Number of stores", 200, 300, D.PUBLIC_FACTS["westlake_store_count"], 5)
        leasing = st.slider("Leasing rate", 0.80, 1.00, 0.92, 0.01, format="%.2f",
                            help="Westlake 66 opened with a >90% retail leasing rate")
        gla_cap = st.number_input("Retail GLA available (sqm)", 60_000, 200_000, D.DEFAULT_RETAIL_GLA, 5_000,
                                  help="Illustrative assumption")
        st.markdown("**Tenant mix** · relative weight by store count")
        weights = [st.slider(n, 0, 40, key=f"mix_{n}") for n in CAT_NAMES]

    with st.expander("Edit category economics (illustrative assumptions)"):
        cats = st.data_editor(
            cats,
            hide_index=True,
            disabled=["category"],
            column_config={
                "category": "Category",
                "gla_sqm": st.column_config.NumberColumn("Avg GLA / store (sqm)", min_value=20, step=10),
                "base_rent": st.column_config.NumberColumn("Base rent (RMB/sqm/month)", min_value=0, step=10),
                "sales_density": st.column_config.NumberColumn("Sales density (RMB/sqm/yr)", min_value=0, step=1000),
                "turnover_pct": st.column_config.NumberColumn("Turnover rent %", min_value=0.0, max_value=0.3,
                                                              step=0.005, format="%.3f"),
                "draw_k": st.column_config.NumberColumn("Visits pulled / store / yr ('000)", min_value=0, step=10),
            },
        )
        st.markdown(
            "- **Rent** per store = GLA × the higher of base rent or turnover % × sales.\n"
            "- **Anchor halo:** luxury anchors lift sales of jewellery, lifestyle and beauty by up to +25%.\n"
            "- **Diminishing returns:** traffic per category scales with stores^0.85.\n"
            "- **Dwell synergy:** F&B + experiential space near 40% of GLA maximises dwell time (up to +15% "
            "traffic, and higher F&B sales).\n"
            "- Only leased stores generate rent and traffic."
        )

    counts = M.allocate_stores(weights, total)
    r = M.simulate_mix(cats, counts, leasing)
    tbl = r["table"]
    over_cap = r["total_gla"] > gla_cap

    with out:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Est. annual footfall", f"{r['traffic_m']:.1f}m visits")
        k2.metric("Est. gross rental income", rmb_m(r["gri_rmb_m"]))
        k3.metric("GRI per leased sqm", f"RMB {r['gri_per_sqm']:,.0f}")
        k4.metric("GLA used", f"{r['total_gla']:,.0f} sqm",
                  delta=f"{r['total_gla'] - gla_cap:+,.0f} vs available", delta_color="inverse")
        if over_cap:
            st.warning("This mix needs more GLA than is available - trim large-format categories "
                       "(anchors, experiential) or reduce the store count.", icon="⚠️")

        # Share of stores vs share of rent
        store_share = tbl["stores"] / tbl["stores"].sum()
        rent_share = tbl["gri_rmb_m"] / tbl["gri_rmb_m"].sum()
        fig = go.Figure()
        fig.add_bar(y=tbl["category"], x=store_share, name="Share of stores", orientation="h",
                    marker=dict(color=S1, line=dict(color=SURFACE, width=2)),
                    customdata=np.c_[tbl["stores"]],
                    hovertemplate="%{y}<br>%{x:.0%} of stores (%{customdata[0]:.0f})<extra></extra>")
        fig.add_bar(y=tbl["category"], x=rent_share, name="Share of rental income", orientation="h",
                    marker=dict(color=S2, line=dict(color=SURFACE, width=2)),
                    customdata=np.c_[tbl["gri_rmb_m"]],
                    hovertemplate="%{y}<br>%{x:.0%} of GRI (RMB %{customdata[0]:,.0f}m)<extra></extra>")
        fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.08)
        fig.update_xaxes(tickformat=".0%")
        fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
        show(style(fig, "Who fills the mall vs. who pays the rent", height=360))

        anchor = tbl.loc[tbl["category"] == "Luxury Anchor"]
        if not anchor.empty and tbl["stores"].sum():
            a_st = float(anchor["stores"].iloc[0] / tbl["stores"].sum())
            a_gri = float(anchor["gri_rmb_m"].iloc[0] / tbl["gri_rmb_m"].sum())
            st.caption(
                f"Luxury anchors are {a_st:.0%} of stores but {a_gri:.0%} of rental income; "
                f"their halo lifts neighbouring categories' sales by {r['halo'] - 1:.0%}. "
                f"F&B + experiential take {r['leisure_share_gla']:.0%} of GLA (dwell multiplier ×{r['dwell']:.2f})."
            )

    st.divider()
    f_col, r_col = st.columns(2, gap="large")

    with f_col:
        st.markdown("#### Traffic vs. rent trade-off")
        st.caption("1,500 random tenant mixes at the current store count and leasing rate, "
                   "keeping only those that fit the available GLA.")
        cloud = cached_frontier(cats, total, leasing)
        cloud = cloud[cloud["total_gla"] <= gla_cap]
        fig = go.Figure()
        fig.add_scatter(x=cloud["traffic_m"], y=cloud["gri_rmb_m"], mode="markers", name="Random mixes",
                        marker=dict(size=6, color=NEUTRAL_FILL, line=dict(width=0)),
                        hovertemplate="%{x:.1f}m visits · RMB %{y:,.0f}m<extra>random mix</extra>")
        for name, shares in D.MIX_PRESETS.items():
            pr = M.simulate_mix(cats, M.allocate_stores(shares, total), leasing)
            fig.add_scatter(x=[pr["traffic_m"]], y=[pr["gri_rmb_m"]], mode="markers+text",
                            text=[name.split(" (")[0]], textposition="top center",
                            textfont=dict(color=INK_2, size=11), showlegend=False,
                            marker=dict(size=10, color=SURFACE, line=dict(color=INK_2, width=2)),
                            hovertemplate=f"{name}<br>%{{x:.1f}}m visits · RMB %{{y:,.0f}}m<extra></extra>")
        fig.add_scatter(x=[r["traffic_m"]], y=[r["gri_rmb_m"]], mode="markers+text", name="Your mix",
                        text=["Your mix"], textposition="bottom center", textfont=dict(color=INK, size=12),
                        marker=dict(size=14, color=S1, line=dict(color=SURFACE, width=2)),
                        hovertemplate="Your mix<br>%{x:.1f}m visits · RMB %{y:,.0f}m<extra></extra>")
        fig.update_xaxes(title="Annual footfall (m visits)")
        fig.update_yaxes(title="Gross rental income (RMB m)")
        show(style(fig, height=420, legend=False))
        if not cloud.empty:
            better = ((cloud["traffic_m"] > r["traffic_m"]) & (cloud["gri_rmb_m"] > r["gri_rmb_m"])).mean()
            st.caption(f"{better:.0%} of feasible random mixes beat yours on **both** footfall and rent. "
                       "Points on the upper-right edge are the efficient mixes.")

    with r_col:
        st.markdown("#### Opening ramp-up")
        st.caption("Tenants open in phases after a soft opening; occupancy and sales build over "
                   "roughly 12 months (per Hang Lung's interim results).")
        a, b = st.columns(2)
        open_lr = a.slider("Leasing at opening", 0.85, 0.99, 0.91, 0.01, format="%.2f")
        months = b.slider("Months to stabilise", 6, 24, 12)
        trading0 = st.slider("Share of leased stores trading on day one", 0.4, 1.0, 0.7, 0.05, format="%.2f")
        stable_gri = M.simulate_mix(cats, counts, max(leasing, open_lr))["gri_rmb_m"]
        ramp = M.ramp_up(stable_gri, open_lr, max(leasing, open_lr), months, trading0)

        fig = go.Figure()
        fig.add_scatter(x=ramp["month"], y=ramp["gri_rmb_m"], mode="lines", name="Monthly GRI",
                        line=dict(color=S1, width=2),
                        hovertemplate="%{x|%b %Y}<br>RMB %{y:,.1f}m<extra></extra>")
        fig.update_yaxes(title="Monthly GRI (RMB m)", rangemode="tozero")
        fig.update_layout(hovermode="x unified")
        show(style(fig, height=260, legend=False))

        fig = go.Figure()
        fig.add_scatter(x=ramp["month"], y=ramp["leasing_rate"], mode="lines", name="Leasing rate",
                        line=dict(color=S1, width=2))
        fig.add_scatter(x=ramp["month"], y=ramp["trading_share"], mode="lines", name="Leased stores trading",
                        line=dict(color=S2, width=2))
        fig.update_yaxes(tickformat=".0%", range=[0.3, 1.02])
        fig.update_layout(hovermode="x unified")
        show(style(fig, height=230))
        year1 = ramp.loc[ramp.index < 12, "gri_rmb_m"].sum()
        st.caption(f"Year-one GRI {rmb_m(year1)} vs. {rmb_m(stable_gri)} at stabilisation "
                   f"({year1 / stable_gri:.0%}).")

    with st.expander("Store count and economics by category"):
        view = tbl[["category", "stores", "gla_total", "rent_psm_year", "gri_rmb_m", "traffic_m"]].rename(columns={
            "category": "Category", "stores": "Stores", "gla_total": "GLA (sqm)",
            "rent_psm_year": "Rent (RMB/sqm/yr)", "gri_rmb_m": "GRI (RMB m)", "traffic_m": "Footfall (m)"})
        st.dataframe(view.style.format({"Stores": "{:.0f}", "GLA (sqm)": "{:,.0f}", "Rent (RMB/sqm/yr)": "{:,.0f}",
                                         "GRI (RMB m)": "{:,.1f}", "Footfall (m)": "{:.2f}"}), hide_index=True)


# ======================================================================================
# 1B - Expansion matrix
# ======================================================================================
def page_expansion():
    header(
        "Module 1B",
        "Mainland Market Expansion Matrix",
        "Score tier-1 and tier-2 cities on demand and premium-supply whitespace to find the "
        "next city ripe for a 66. Indicator feed is simulated.",
        tags=("mock",),
    )

    feed = M.market_feed(seed=st.session_state.feed_seed)
    latest_month = feed["month"].max()

    top = st.columns([1, 1, 1, 1, 1, 1.2])
    w_lci = top[0].slider("Luxury consumption", 0, 10, 4)
    w_ws = top[1].slider("Supply whitespace", 0, 10, 3)
    w_hn = top[2].slider("HNW density", 0, 10, 2)
    w_gr = top[3].slider("Retail growth", 0, 10, 2)
    w_cn = top[4].slider("Connectivity", 0, 10, 1)
    with top[5]:
        include_existing = st.toggle("Include existing 66 cities", value=False)
        if st.button("↻ Refresh market feed", use_container_width=True):
            st.session_state.feed_seed += 1
            st.rerun()
    weights = {"lci": w_lci, "whitespace": w_ws, "hnwi": w_hn, "growth_idx": w_gr, "connect": w_cn}

    base = M.cities_frame().drop(columns=["lci", "supply", "growth"])
    now = feed[feed["month"] == latest_month].drop(columns="month")
    cities = base.merge(now, on="city")
    scored = M.score_cities(cities, weights)
    scored["quadrant"] = [M.quadrant(l, w) for l, w in zip(scored["lci"], scored["whitespace"])]
    scored["status"] = np.where(scored["has_66"], "Existing 66 city", "Candidate")
    pool = scored if include_existing else scored[~scored["has_66"]]
    pool = pool.reset_index(drop=True)

    if pool.empty or sum(weights.values()) == 0:
        st.info("Give at least one indicator a weight above zero.")
        return

    best = pool.iloc[0]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Top-ranked city", best["city"], help=best["quadrant"])
    k2.metric("Attractiveness score", f"{best['score']:.0f} / 100")
    k3.metric("Luxury Consumption Index", f"{best['lci']:.0f}")
    k4.metric("Feed as of", latest_month.strftime("%b %Y"))

    m_col, q_col = st.columns([1.15, 1], gap="large")
    with m_col:
        fig = go.Figure()
        for status, color in [("Existing 66 city", MUTED), ("Candidate", S1)]:
            d = scored[scored["status"] == status]
            size = np.full(len(d), 9.0) if status == "Existing 66 city" else np.clip(d["score"] / 3.2, 6, 30)
            fig.add_scattergeo(
                lat=d["lat"], lon=d["lon"], text=d["city"], name=status, mode="markers+text",
                textposition="top center", textfont=dict(size=10, color=INK_2),
                marker=dict(size=size, color=color, opacity=0.85,
                            line=dict(color=SURFACE, width=2)),
                customdata=list(zip(d["score"], d["lci"], d["whitespace"], d["tier"])),
                hovertemplate="<b>%{text}</b> · %{customdata[3]}<br>Score %{customdata[0]:.0f}"
                              "<br>Luxury index %{customdata[1]:.0f} · Whitespace %{customdata[2]:.0f}<extra></extra>",
            )
        fig.update_geos(
            projection_type="mercator", lataxis_range=[19, 45], lonaxis_range=[99, 127],
            showland=True, landcolor="#f0efec", showocean=True, oceancolor=SURFACE,
            showcountries=True, countrycolor=AXIS, showcoastlines=True, coastlinecolor=AXIS,
            showlakes=False, bgcolor=SURFACE,
        )
        show(style(fig, "Candidate bubble size = attractiveness score", height=520))

    with q_col:
        lci_cut, ws_cut = 70, 45
        fig = go.Figure()
        for status, color in [("Existing 66 city", MUTED), ("Candidate", S1)]:
            d = pool[pool["status"] == status]
            if d.empty:
                continue
            fig.add_scatter(
                x=d["lci"], y=d["whitespace"], text=d["city"], name=status, mode="markers+text",
                textposition="top center", textfont=dict(size=10, color=INK_2),
                marker=dict(size=10, color=color, line=dict(color=SURFACE, width=2)),
                hovertemplate="<b>%{text}</b><br>Luxury index %{x:.0f}<br>Whitespace %{y:.0f}<extra></extra>",
            )
        fig.add_vline(x=lci_cut, line=dict(color=AXIS, dash="dot", width=1))
        fig.add_hline(y=ws_cut, line=dict(color=AXIS, dash="dot", width=1))
        for x, y, label in [(99, 99, "Ripe for a 66"), (99, 2, "Strong demand, crowded"),
                            (41, 99, "Open field"), (41, 2, "Watch list")]:
            fig.add_annotation(x=x, y=y, text=label, showarrow=False, font=dict(size=11, color=MUTED),
                               xanchor="right" if x > 50 else "left", yanchor="top" if y > 50 else "bottom")
        fig.update_xaxes(title="Luxury Consumption Index (demand)", range=[40, 100])
        fig.update_yaxes(title="Premium supply whitespace (100 − supply)", range=[0, 100])
        show(style(fig, "Demand vs. whitespace", height=520))

    st.markdown("#### Ranking")
    table = pool[["rank", "city", "tier", "status", "score", "lci", "whitespace", "hnwi", "growth", "connect", "quadrant"]]
    st.dataframe(
        table,
        hide_index=True,
        column_config={
            "rank": st.column_config.NumberColumn("#", width="small"),
            "city": "City", "tier": "Tier (indicative)", "status": "Status",
            "score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.0f"),
            "lci": st.column_config.NumberColumn("Luxury index", format="%.0f"),
            "whitespace": st.column_config.NumberColumn("Whitespace", format="%.0f"),
            "hnwi": st.column_config.NumberColumn("HNW density", format="%.0f"),
            "growth": st.column_config.NumberColumn("Retail growth", format="%.1f%%"),
            "connect": st.column_config.NumberColumn("Connectivity", format="%.0f"),
            "quadrant": "Quadrant",
        },
    )

    st.markdown("#### Indicator trend")
    choices = st.multiselect("Compare up to three cities", scored["city"].tolist(),
                             default=pool["city"].head(3).tolist(), max_selections=3)
    metric = st.radio("Indicator", ["Luxury Consumption Index", "Premium Mixed-Use Supply", "Retail growth (% YoY)"],
                      horizontal=True)
    col = {"Luxury Consumption Index": "lci", "Premium Mixed-Use Supply": "supply",
           "Retail growth (% YoY)": "growth"}[metric]
    fig = go.Figure()
    for city, color in zip(choices, [S1, S2, S3]):
        d = feed[feed["city"] == city]
        fig.add_scatter(x=d["month"], y=d[col], mode="lines", name=city, line=dict(color=color, width=2),
                        hovertemplate=f"{city}<br>%{{x|%b %Y}}: %{{y:.1f}}<extra></extra>")
        last = d.iloc[-1]
        fig.add_annotation(x=last["month"], y=last[col], text=city, showarrow=False, xanchor="left",
                           xshift=6, font=dict(size=11, color=INK_2))
    fig.update_layout(hovermode="x unified")
    show(style(fig, height=320))


# ======================================================================================
# 2A - Renewable transition tracker
# ======================================================================================
def page_renewables():
    header(
        "Module 2A",
        "Renewable Energy Transition Tracker",
        "All 11 Mainland operating properties reached 100% renewable electricity on 1 Oct 2026. "
        "This view tracks how the portfolio got there, and what the next lever is.",
        tags=("public", "mock"),
    )
    f = D.PUBLIC_FACTS
    props = M.properties_frame()
    timeline = M.coverage_timeline()
    energy = M.monthly_energy()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Properties on 100% renewable", "11 / 11", help="Spring City 66 first (Dec 2021), Riverside 66 last (Oct 2026)")
    k2.metric("Mainland GFA covered", f"{f['mainland_gfa_sqm'] / 1e6:.2f}m sqm")
    k3.metric("Renewable electricity, 2026E", f"{f['re_mwh_2026e']:,} MWh")
    k4.metric("GHG avoided, 2026E", f"{f['ghg_avoided_t_2026e']:,} t")

    t_col, a_col = st.columns(2, gap="large")
    with t_col:
        st.markdown(f"#### Five-year transition &nbsp; {tag('public')}", unsafe_allow_html=True)
        steps = pd.concat([timeline, pd.DataFrame([{
            "switch_date": pd.Timestamp("2026-12-01"), "added": 0, "covered": 11, "names": ""}])])
        fig = go.Figure()
        fig.add_scatter(x=steps["switch_date"], y=steps["covered"], mode="lines", line_shape="hv",
                        line=dict(color=S1, width=2), hoverinfo="skip", showlegend=False)
        fig.add_scatter(x=timeline["switch_date"], y=timeline["covered"], mode="markers",
                        marker=dict(size=9, color=S1, line=dict(color=SURFACE, width=2)),
                        customdata=list(zip(timeline["names"], timeline["added"])),
                        hovertemplate="%{x|%b %Y}: %{y} of 11<br>+%{customdata[1]}: %{customdata[0]}<extra></extra>",
                        showlegend=False)
        for _, row in timeline.iterrows():
            short = row["names"] if len(row["names"]) < 28 else f"+{row['added']} properties"
            fig.add_annotation(x=row["switch_date"], y=row["covered"], text=short, showarrow=False,
                               xanchor="right", yanchor="bottom", xshift=-4, yshift=4,
                               font=dict(size=10, color=INK_2))
        fig.update_yaxes(title="Properties covered", range=[0, 12.5], dtick=2)
        fig.update_xaxes(range=["2021-01-01", "2027-02-01"])
        show(style(fig, height=380, legend=False))

    with a_col:
        st.markdown(f"#### Portfolio electricity by source &nbsp; {tag('mock')}", unsafe_allow_html=True)
        port = energy.groupby("month")[["grid_mwh", "wind_mwh", "solar_mwh"]].sum().reset_index()
        fig = go.Figure()
        for col, name, color in [("grid_mwh", "Grid (non-renewable)", NEUTRAL_FILL),
                                 ("wind_mwh", "Wind", S1), ("solar_mwh", "Solar", S2)]:
            fig.add_scatter(x=port["month"], y=port[col] / 1000, name=name, stackgroup="one", mode="lines",
                            line=dict(width=0.5, color=SURFACE), fillcolor=color,
                            hovertemplate=f"{name}: %{{y:,.1f}} GWh<extra></extra>")
        fig.update_yaxes(title="GWh per month")
        fig.update_layout(hovermode="x unified")
        show(style(fig, height=380))

    st.markdown("#### Property detail")
    table = props[["property", "city", "province", "switch_date", "milestone", "annual_mwh", "wind_share"]].copy()
    table["wind_share"] = table["wind_share"] * 100
    table["solar_share"] = 100 - table["wind_share"]
    table = table.sort_values("switch_date")
    st.dataframe(
        table,
        hide_index=True,
        column_config={
            "property": "Property", "city": "City", "province": "Province",
            "switch_date": st.column_config.DateColumn("100% renewable since", format="MMM YYYY"),
            "milestone": "Milestone",
            "annual_mwh": st.column_config.NumberColumn("Annual MWh (illustr.)", format="%d"),
            "wind_share": st.column_config.ProgressColumn("Wind share (illustr.)", min_value=0, max_value=100, format="%.0f%%"),
            "solar_share": st.column_config.ProgressColumn("Solar share (illustr.)", min_value=0, max_value=100, format="%.0f%%"),
        },
    )
    st.caption("Switch dates and milestones are public; per-property consumption and wind/solar splits are illustrative.")

    pick = st.selectbox("Drill into a property", props["property"].tolist(), index=9)
    d = energy[energy["property"] == pick]
    fig = go.Figure()
    for col, name, color in [("grid_mwh", "Grid", NEUTRAL_FILL), ("wind_mwh", "Wind", S1), ("solar_mwh", "Solar", S2)]:
        fig.add_bar(x=d["month"], y=d[col], name=name, marker=dict(color=color, line=dict(color=SURFACE, width=1)),
                    hovertemplate=f"{name}: %{{y:,.0f}} MWh<extra></extra>")
    fig.update_layout(barmode="stack", bargap=0.15, hovermode="x unified")
    fig.update_yaxes(title="MWh per month")
    show(style(fig, f"{pick} · monthly electricity by source", height=300))

    st.divider()
    st.markdown(f"#### The next lever: tenant efficiency &nbsp; {tag('mock')}", unsafe_allow_html=True)
    st.markdown(
        "With supply 100% renewable, every MWh the portfolio *doesn't* use still matters: green power "
        "carries a premium, the supply is finite, and Hang Lung's whole-building procurement covers "
        "tenant consumption too. Cutting demand is where Changemakers comes in."
    )
    c1, c2, c3, c4 = st.columns(4)
    annual = c1.number_input("Portfolio demand (MWh/yr)", 200_000, 800_000, f["re_mwh_2026e"], 5_000)
    tariff = c2.number_input("Base tariff (RMB/MWh)", 300, 1_200, 700, 10)
    premium = c3.number_input("Green premium (RMB/MWh)", 0, 200, 30, 5)
    cut = c4.slider("Efficiency gain from tenants", 0.0, 0.20, 0.08, 0.01, format="%.2f")
    g = M.green_premium(annual, premium, cut, tariff)
    r1, r2, r3 = st.columns(3)
    r1.metric("Electricity avoided", f"{g['saved_mwh']:,.0f} MWh/yr")
    r2.metric("Annual cost saved (tariff + premium)", f"RMB {g['saved_rmb_m']:,.1f}m")
    r3.metric("Location-based CO₂e avoided", f"{g['location_based_t']:,.0f} t/yr",
              help=f"At the implied grid factor of {D.IMPLIED_GRID_EF:.3f} tCO₂e/MWh. Market-based Scope 2 is "
                   "already ~zero for renewable-covered load.")


# ======================================================================================
# 2B - Changemakers portal
# ======================================================================================
ACT_NAMES = list(D.ACTIVITIES)


def page_portal():
    header(
        "Module 2B",
        "Changemakers Tenant Portal",
        "Tenants log sustainability actions, earn points and badges, and climb from Foundational "
        "to Advanced level. Tenants and logs here are fictional.",
        tags=("mock",),
    )
    if st.session_state.get("flash"):
        st.toast(st.session_state.pop("flash"), icon="🌿")
    logs = st.session_state.logs
    tenant_names = [t[0] for t in D.TENANTS]
    tenant = st.selectbox("Signed in as", tenant_names)
    info = next(t for t in D.TENANTS if t[0] == tenant)
    mine = logs[logs["tenant"] == tenant]
    board = M.leaderboard(logs)
    me = board[board["tenant"] == tenant].iloc[0]
    level, nxt, prog = M.level_for(me["points"])

    st.caption(f"{info[1]} · {info[2]}")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Season points", f"{me['points']:,.0f}")
    k2.metric("Leaderboard rank", f"#{me['rank']} of {len(board)}")
    k3.metric("Actions logged", f"{me['actions']}")
    k4.metric("CO₂e avoided (location-based)", f"{me['t_co2e']:.2f} t")
    if nxt:
        nxt_threshold = next(t for t, n in D.LEVELS if n == nxt)
        st.progress(prog, text=f"**{level}** · {nxt_threshold - me['points']:,.0f} points to {nxt}")
    else:
        st.progress(1.0, text=f"**{level}** · top level reached")

    earned = set(M.badges_for(mine))
    st.markdown(
        "".join(
            f'<span class="badge {"badge-on" if b in earned else "badge-off"}" title="{desc}">'
            f'{"✓ " if b in earned else "○ "}{b}</span>'
            for b, desc in D.BADGES
        ),
        unsafe_allow_html=True,
    )

    st.write("")
    form_col, side = st.columns([1.2, 1], gap="large")
    with form_col:
        with st.form("log_action", clear_on_submit=True):
            st.markdown("#### Log an action")
            day = st.date_input("Date", value=date.today(), max_value=date.today())
            act = st.selectbox("Action", ACT_NAMES,
                               format_func=lambda a: f"{a}  ·  {D.ACTIVITIES[a][0]} ({D.ACTIVITIES[a][1]})")
            qty = st.number_input("Quantity (in the unit shown for the action)", min_value=0.0, value=100.0, step=10.0)
            note = st.text_input("Note (optional)", placeholder="e.g. Display lighting off 22:00-10:00 on non-trading hours")
            submitted = st.form_submit_button("Submit action", type="primary")
        if submitted:
            if qty <= 0:
                st.error("Enter a quantity above zero.")
            else:
                row = M.make_log(day, tenant, act, qty, note)
                st.session_state.logs = pd.concat([logs, pd.DataFrame([row])], ignore_index=True)
                new_badges = set(M.badges_for(st.session_state.logs[st.session_state.logs["tenant"] == tenant])) - earned
                msg = f"+{row['points']:,.0f} points logged for {act.lower()}."
                if new_badges:
                    msg += " New badge: " + ", ".join(sorted(new_badges)) + "!"
                st.session_state.flash = msg
                st.rerun()

    with side:
        st.markdown("#### Points by pillar")
        pts = mine.groupby("pillar")["points"].sum().reindex(D.PILLARS, fill_value=0)
        fig = go.Figure(go.Bar(x=pts.values, y=pts.index, orientation="h",
                               marker=dict(color=[PILLAR_COLORS[p] for p in pts.index]),
                               hovertemplate="%{y}: %{x:,.0f} pts<extra></extra>",
                               text=[f"{v:,.0f}" for v in pts.values], textposition="outside",
                               textfont=dict(color=INK_2)))
        fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
        fig.update_xaxes(range=[0, max(pts.max() * 1.25, 10)])
        show(style(fig, height=200, legend=False))
        with st.container(border=True):
            st.markdown("**A note on carbon accounting**")
            st.caption(
                "Every Mainland property now runs on 100% renewable electricity, so electricity savings no "
                "longer reduce *market-based* Scope 2 emissions. The portal therefore rewards energy actions "
                "on kWh saved, and reports carbon on a *location-based* basis (grid-average factor "
                f"{D.IMPLIED_GRID_EF:.3f} tCO₂e/MWh), which is what the saving would avoid on a typical grid."
            )

    st.markdown("#### Activity history")
    hist = st.session_state.logs[st.session_state.logs["tenant"] == tenant].sort_values("date", ascending=False)
    st.dataframe(
        hist[["date", "activity", "pillar", "quantity", "unit", "points", "kg_co2e", "note"]],
        hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("Date", format="D MMM YYYY"),
            "activity": "Action", "pillar": "Pillar",
            "quantity": st.column_config.NumberColumn("Qty", format="%.0f"), "unit": "Unit",
            "points": st.column_config.NumberColumn("Points", format="%.0f"),
            "kg_co2e": st.column_config.NumberColumn("kg CO₂e", format="%.0f"), "note": "Note",
        },
        height=300,
    )
    st.download_button("Download my log (CSV)", hist.to_csv(index=False).encode("utf-8"),
                       file_name=f"changemakers_{tenant.lower().replace(' ', '_')}.csv", mime="text/csv")


# ======================================================================================
# 2C - Leaderboard
# ======================================================================================
def page_leaderboard():
    header(
        "Module 2C",
        "Green Changemaker Leaderboard",
        "Tenants compete across the season for the title of Hang Lung Green Changemaker, "
        "unlocking marketing features and priority access to event space.",
        tags=("mock",),
    )
    logs = st.session_state.logs
    f1, f2, f3 = st.columns([1.4, 1, 1])
    props = f1.multiselect("Property", sorted({t[2] for t in D.TENANTS}), placeholder="All properties")
    cat = f2.selectbox("Tenant type", ["All"] + sorted({t[1] for t in D.TENANTS}))
    window = f3.selectbox("Season window", ["Last 90 days", "Last 30 days"])
    if window == "Last 30 days":
        logs = logs[logs["date"] >= pd.Timestamp(date.today()) - pd.Timedelta(days=30)]

    board = M.leaderboard(logs)
    if props:
        board = board[board["property"].isin(props)]
    if cat != "All":
        board = board[board["category"] == cat]
    board = board.reset_index(drop=True)
    board["rank"] = np.arange(1, len(board) + 1)

    if board.empty:
        st.info("No tenants match these filters.")
        return

    podium = st.columns(3)
    medals = ["🥇 Green Changemaker", "🥈 Runner-up", "🥉 Third"]
    for i, col in enumerate(podium):
        if i < len(board):
            row = board.iloc[i]
            with col:
                with st.container(border=True):
                    st.caption(medals[i])
                    st.markdown(f"### {row['tenant']}")
                    st.caption(f"{row['category']} · {row['property']}")
                    st.metric("Points", f"{row['points']:,.0f}", help=f"{row['actions']} actions · {row['badges']} badges")

    chart_col, table_col = st.columns([1.3, 1], gap="large")
    with chart_col:
        b = board.iloc[::-1]
        fig = go.Figure()
        for p in D.PILLARS:
            fig.add_bar(y=b["tenant"], x=b[p], name=p, orientation="h",
                        marker=dict(color=PILLAR_COLORS[p], line=dict(color=SURFACE, width=2)),
                        hovertemplate=f"%{{y}}<br>{p}: %{{x:,.0f}} pts<extra></extra>")
        fig.update_layout(barmode="stack", bargap=0.25)
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
        fig.update_xaxes(title="Season points")
        show(style(fig, "Points by pillar", height=max(300, 34 * len(board) + 90)))
    with table_col:
        st.dataframe(
            board[["rank", "tenant", "property", "points", "level", "badges", "t_co2e"]],
            hide_index=True,
            column_config={
                "rank": st.column_config.NumberColumn("#", width="small"),
                "tenant": "Tenant", "property": "Property",
                "points": st.column_config.ProgressColumn("Points", min_value=0,
                                                          max_value=float(max(board["points"].max(), 1)), format="%.0f"),
                "level": "Level", "badges": st.column_config.NumberColumn("Badges", format="%d"),
                "t_co2e": st.column_config.NumberColumn("t CO₂e", format="%.1f"),
            },
            height=max(300, 36 * len(board) + 40),
        )

    st.markdown("#### What winning unlocks")
    st.dataframe(pd.DataFrame(D.REWARDS, columns=["Who qualifies", "Reward"]), hide_index=True)
    st.caption("Levels: " + ", ".join(f"{n} ({t:,}+)" for t, n in D.LEVELS) + ". Points per unit: "
               + "; ".join(f"{a} {v[2]:g}/{v[1].split()[0]}" for a, v in D.ACTIVITIES.items()) + ".")


# --------------------------------------------------------------------------------------
ROUTES = dict(zip(PAGES, [page_overview, page_retail, page_expansion, page_renewables, page_portal, page_leaderboard]))
ROUTES[st.session_state.page]()

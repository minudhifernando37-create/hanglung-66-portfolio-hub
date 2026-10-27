# 66 Portfolio Growth & Decarbonization Hub

An independent concept prototype built in Python (Streamlit, pandas, plotly) around two of
Hang Lung Properties' current priorities: launching premium "66" mixed-use destinations, and
running the Mainland portfolio on renewable energy together with tenants.

> Not affiliated with or endorsed by Hang Lung Properties. Figures tagged **Public data** come
> from Hang Lung's published releases (sources on the Overview page). Everything tagged
> **Mock / illustrative** is an assumption written for this prototype.

## What's inside

| Page | What it does |
|---|---|
| **Overview** | Headline public facts, how the data works, sources |
| **1A · Westlake 66 Retail Mix Planner** | Allocate ~250 stores across six tenant categories; see footfall, gross rental income, GLA use, a 1,500-mix traffic-vs-rent trade-off cloud, and a 24-month opening ramp-up. Category economics are editable. |
| **1B · Mainland Expansion Matrix** | Weighted scoring of 24 tier-1/tier-2 cities on luxury demand, premium-supply whitespace, HNW density, retail growth and connectivity; map, demand-vs-whitespace quadrant, ranking, simulated monthly indicator feed. |
| **2A · Renewable Transition Tracker** | The public five-year chronology to 11/11 properties on 100% renewable electricity (completed 1 Oct 2026), portfolio electricity by source, property drill-down, and a calculator for the next lever: tenant efficiency. |
| **2B · Changemakers Tenant Portal** | A tenant logs actions (energy, waste & circularity, community), earns points, badges and levels; history export to CSV. |
| **2C · Green Changemaker Leaderboard** | Season leaderboard with filters, podium, points by pillar, and the rewards each rank unlocks. |

## Run it on your laptop (about 2 minutes)

You need Python 3.10–3.12.

```bash
cd hanglung_hub
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

It opens at http://localhost:8501.

Optional checks of the calculation layer: `python test_model.py`

## Put it online (free, gives you a link for your application)

1. Create a GitHub repository and upload this folder's contents (including the hidden
   `.streamlit` folder).
2. Go to https://share.streamlit.io, sign in with GitHub, click **Create app**.
3. Pick the repository, set **Main file path** to `app.py`, and under *Advanced settings*
   choose Python 3.12.
4. Deploy. You get a public `*.streamlit.app` URL to put on your CV or in your cover letter.

## Project structure

```
app.py            UI: pages, charts, widgets
model.py          all calculations (pure pandas/numpy, no Streamlit)
data.py           public facts + clearly labelled mock assumptions
test_model.py     sanity tests for model.py
requirements.txt  pinned dependencies
.streamlit/       theme
```

## Notes on the modelling

- **Rent** per store is GLA × the higher of base rent or turnover rent, the usual structure
  for premium retail leases. Luxury anchors lift neighbouring categories' sales (halo);
  F&B and experiential space near 40% of GLA maximises dwell time; traffic has diminishing
  returns per category.
- **Carbon:** because every Mainland property now runs on 100% renewable electricity, saving
  electricity no longer reduces *market-based* Scope 2 emissions. The portal rewards energy
  actions on kWh saved and reports carbon on a *location-based* basis, using the factor implied
  by Hang Lung's own figures (227,513 t ÷ 440,655 MWh ≈ 0.516 tCO₂e/MWh).
- Tenant logs live in the browser session for this demo. A production version would write
  them to a database and verify them against meter data.

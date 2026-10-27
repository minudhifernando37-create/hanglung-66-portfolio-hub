"""
Reference data for the 66 Portfolio Growth & Decarbonization Hub.

Two kinds of data live here, and the app labels them differently:

  PUBLIC  - taken from Hang Lung press releases / investor materials (sources listed
            in SOURCES). Shown with a "Public data" tag.
  MOCK    - illustrative assumptions written for this prototype. Shown with a
            "Mock / illustrative" tag. Replace with internal data in a real build.
"""

from datetime import date

# --------------------------------------------------------------------------------------
# PUBLIC facts
# --------------------------------------------------------------------------------------
PUBLIC_FACTS = {
    "westlake_open_date": date(2026, 4, 28),
    "westlake_gfa_sqm": 390_200,
    "westlake_store_count": 250,          # "~250 stores"
    "westlake_leasing_rate_floor": 0.90,  # ">90% retail leasing rate" at opening
    "mainland_properties": 11,
    "mainland_cities": 9,
    "mainland_gfa_sqm": 2_650_000,
    "re_full_coverage_date": date(2026, 10, 1),
    "re_mwh_2026e": 440_655,
    "ghg_avoided_t_2026e": 227_513,
    "re_all_ops_target_year": 2050,
    "changemakers_launch": date(2023, 12, 1),
    "lightwise_participation": 0.93,      # Lightwise tenant participation, Mainland
}

# Implied grid emission factor from the two public 2026E figures (tCO2e per MWh)
IMPLIED_GRID_EF = PUBLIC_FACTS["ghg_avoided_t_2026e"] / PUBLIC_FACTS["re_mwh_2026e"]

# Hang Lung's 11 Mainland operating properties and the month each one switched to
# 100% renewable electricity (public chronology, Sept 2026 press release).
PROPERTIES = [
    # name,              city,       province,   switch (y, m), first-in-province note
    ("Spring City 66",   "Kunming",  "Yunnan",   (2021, 12), "First commercial complex in Yunnan"),
    ("Parc 66",          "Jinan",    "Shandong", (2023, 1),  "First commercial property in Shandong"),
    ("Plaza 66",         "Shanghai", "Shanghai", (2024, 4),  ""),
    ("Grand Gateway 66", "Shanghai", "Shanghai", (2024, 4),  ""),
    ("Center 66",        "Wuxi",     "Jiangsu",  (2024, 4),  ""),
    ("Forum 66",         "Shenyang", "Liaoning", (2025, 5),  "First in Liaoning (with Palace 66, Olympia 66)"),
    ("Palace 66",        "Shenyang", "Liaoning", (2025, 5),  "First in Liaoning (with Forum 66, Olympia 66)"),
    ("Olympia 66",       "Dalian",   "Liaoning", (2025, 5),  "First in Liaoning (with Forum 66, Palace 66)"),
    ("Heartland 66",     "Wuhan",    "Hubei",    (2026, 1),  "First commercial complex in Hubei"),
    ("Westlake 66",      "Hangzhou", "Zhejiang", (2026, 5),  ""),
    ("Riverside 66",     "Tianjin",  "Tianjin",  (2026, 10), "Completes 11/11 coverage"),
]

SOURCES = [
    ("Hang Lung opens Westlake 66 (IR news, 28 Apr 2026)",
     "https://www.hanglung.com/en-us/investor/ir-news/2026/20260428"),
    ("Hang Lung's Mainland portfolio to be 100% powered by renewable energy (24 Sep 2026)",
     "https://www.malaymail.com/news/money/mediaoutreach/2026/09/24/hang-lungs-mainland-portfolio-to-be-100-powered-by-renewable-energy/489911"),
    ("HLP FY26 interim results analyst presentation",
     "https://www.hanglung.com/getmedia/fe42184a-d16e-47ea-ba26-c4ccd6c9d2aa/HLP-FY26-interim-results-analyst-presentation.pdf"),
    ("Changemakers Program drives collaboration with tenants (23 Jul 2024)",
     "https://www.hanglung.com/en-us/media/press-releases/2024/20240722"),
    ("Changemakers Program gains traction (29 Apr 2025)",
     "https://www.hanglung.com/en-us/media/press-releases/2025/20250429"),
]

# --------------------------------------------------------------------------------------
# MOCK - Module 1A: retail mix planner assumptions (illustrative, not Hang Lung data)
# --------------------------------------------------------------------------------------
# gla_sqm        average gross leasable area per store
# base_rent      RMB per sqm per month (fixed minimum rent)
# sales_density  RMB tenant sales per sqm per year
# turnover_pct   turnover rent as % of tenant sales (tenant pays the higher of the two)
# draw_k         annual visits a single store of this type pulls in (thousands)
RETAIL_CATEGORIES = [
    # name,                    gla,  base,  sales,   turn,  draw_k
    ("Luxury Anchor",          700,  650,   160_000, 0.07,  450),
    ("Jewellery & Watches",    180,  1_100, 220_000, 0.06,  120),
    ("Premium Lifestyle",      250,  550,   60_000,  0.12,  150),
    ("Beauty & Wellness",      120,  700,   70_000,  0.12,  140),
    ("High-End F&B",           300,  350,   45_000,  0.10,  260),
    ("Experiential & Culture", 800,  150,   12_000,  0.08,  380),
]

# Share of store COUNT by category, per preset scenario (each sums to 1.0)
MIX_PRESETS = {
    "Pulse of the City (balanced)": [0.08, 0.10, 0.30, 0.14, 0.28, 0.10],
    "Luxury-led":                   [0.16, 0.18, 0.26, 0.14, 0.20, 0.06],
    "Experience-led":               [0.05, 0.06, 0.27, 0.12, 0.32, 0.18],
}

DEFAULT_RETAIL_GLA = 110_000  # sqm available for retail (illustrative assumption)

# --------------------------------------------------------------------------------------
# MOCK - Module 1B: city indicators (0-100 indices are illustrative, not real statistics)
# --------------------------------------------------------------------------------------
# lci     Luxury Consumption Index (demand)
# supply  Premium Mixed-Use Supply index (higher = more saturated / more competition)
# hnwi    High-net-worth household density index
# growth  Retail sales growth, % YoY
# connect Tourism & air connectivity index
CITIES = [
    # city,        lat,    lon,    tier,          has_66, lci, supply, hnwi, growth, connect
    ("Shanghai",   31.23, 121.47, "Tier 1",       True,  98, 88, 97, 3.1, 98),
    ("Hangzhou",   30.27, 120.16, "New Tier 1",   True,  84, 62, 82, 5.2, 80),
    ("Wuxi",       31.49, 120.31, "Tier 2",       True,  66, 48, 70, 4.0, 52),
    ("Shenyang",   41.80, 123.43, "Tier 2",       True,  58, 55, 52, 2.6, 55),
    ("Dalian",     38.91, 121.61, "Tier 2",       True,  55, 46, 54, 2.9, 58),
    ("Jinan",      36.65, 117.12, "Tier 2",       True,  57, 44, 55, 4.1, 50),
    ("Tianjin",    39.13, 117.20, "New Tier 1",   True,  63, 60, 64, 2.4, 66),
    ("Kunming",    25.04, 102.71, "Tier 2",       True,  54, 42, 48, 4.6, 62),
    ("Wuhan",      30.59, 114.31, "New Tier 1",   True,  71, 58, 66, 5.0, 70),
    ("Beijing",    39.90, 116.41, "Tier 1",       False, 96, 90, 98, 2.8, 97),
    ("Shenzhen",   22.54, 114.06, "Tier 1",       False, 90, 78, 93, 4.4, 88),
    ("Guangzhou",  23.13, 113.26, "Tier 1",       False, 85, 80, 84, 3.0, 90),
    ("Chengdu",    30.57, 104.07, "New Tier 1",   False, 88, 64, 78, 6.1, 86),
    ("Chongqing",  29.56, 106.55, "New Tier 1",   False, 76, 57, 63, 5.6, 74),
    ("Nanjing",    32.06, 118.80, "New Tier 1",   False, 79, 58, 77, 4.8, 72),
    ("Suzhou",     31.30, 120.58, "New Tier 1",   False, 74, 50, 83, 4.7, 60),
    ("Xi'an",      34.34, 108.94, "New Tier 1",   False, 72, 49, 60, 5.4, 78),
    ("Changsha",   28.23, 112.94, "New Tier 1",   False, 70, 45, 61, 6.0, 64),
    ("Qingdao",    36.07, 120.38, "New Tier 1",   False, 65, 47, 66, 4.3, 68),
    ("Xiamen",     24.48, 118.09, "Tier 2",       False, 69, 41, 72, 4.9, 71),
    ("Ningbo",     29.87, 121.54, "New Tier 1",   False, 64, 39, 74, 4.5, 56),
    ("Hefei",      31.82, 117.23, "New Tier 1",   False, 60, 36, 58, 6.4, 54),
    ("Zhengzhou",  34.75, 113.62, "New Tier 1",   False, 61, 43, 52, 5.1, 63),
    ("Fuzhou",     26.07, 119.30, "Tier 2",       False, 58, 34, 62, 4.6, 55),
]

# --------------------------------------------------------------------------------------
# MOCK - Module 2A: property energy profile (illustrative split of the public portfolio)
# --------------------------------------------------------------------------------------
# Annual stabilised electricity use (MWh) and wind share of renewable supply.
# Annual figures are scaled so the 2026 portfolio total lands near the public 440,655 MWh.
PROPERTY_ENERGY = {
    # name:              (annual_mwh, wind_share, open (y, m))
    "Spring City 66":    (34_000, 0.45, (2019, 8)),
    "Parc 66":           (36_000, 0.62, (2011, 8)),
    "Plaza 66":          (52_000, 0.58, (2001, 1)),
    "Grand Gateway 66":  (56_000, 0.55, (1999, 1)),
    "Center 66":         (44_000, 0.50, (2013, 9)),
    "Forum 66":          (40_000, 0.72, (2012, 1)),
    "Palace 66":         (31_000, 0.70, (2010, 5)),
    "Olympia 66":        (37_000, 0.68, (2015, 9)),
    "Heartland 66":      (38_000, 0.52, (2021, 9)),
    "Westlake 66":       (46_000, 0.48, (2025, 10)),
    "Riverside 66":      (41_000, 0.66, (2014, 9)),
}

# --------------------------------------------------------------------------------------
# MOCK - Module 2B/2C: Changemakers portal
# --------------------------------------------------------------------------------------
# Programme pillars mirror the public Changemakers aims: energy, waste/circularity,
# community wellbeing. Points and carbon factors are illustrative.
# kg_co2e_per_unit for electricity uses a LOCATION-based factor (see IMPLIED_GRID_EF):
# under market-based accounting, saving electricity in a 100%-renewable building no
# longer cuts Scope 2 - the app surfaces this nuance on the portal page.
ACTIVITIES = {
    # activity:                          (pillar,                unit,          pts/unit, kgCO2e/unit)
    "Lighting schedule optimisation":    ("Energy",              "kWh saved",   0.10, IMPLIED_GRID_EF),
    "LED / display lighting retrofit":   ("Energy",              "kWh saved",   0.10, IMPLIED_GRID_EF),
    "HVAC set-point optimisation":       ("Energy",              "kWh saved",   0.10, IMPLIED_GRID_EF),
    "Shipping pallets recycled":         ("Waste & Circularity", "pallets",     5.00, 15.0),
    "Packaging take-back":               ("Waste & Circularity", "kg",          0.50, 1.5),
    "Food waste diverted":               ("Waste & Circularity", "kg",          0.40, 0.6),
    "Staff sustainability training":     ("Community",           "participants", 2.00, 0.0),
    "Community volunteering":            ("Community",           "hours",       3.00, 0.0),
}

PILLARS = ["Energy", "Waste & Circularity", "Community"]

# Fictional tenants - deliberately not real brands.
TENANTS = [
    # tenant,                  category,              property,          activity bias (pillar)
    ("Maison Aurelle",         "Luxury Fashion",      "Westlake 66",      "Energy"),
    ("Orbis Horology",         "Jewellery & Watches", "Plaza 66",         "Energy"),
    ("Jadeleaf Tea House",     "F&B",                 "Westlake 66",      "Waste & Circularity"),
    ("Northline Outdoor",      "Premium Lifestyle",   "Grand Gateway 66", "Waste & Circularity"),
    ("Lumen Beauty Lab",       "Beauty & Wellness",   "Center 66",        "Waste & Circularity"),
    ("Harbourstone Capital",   "Office",              "Plaza 66",         "Community"),
    ("Saffron & Salt",         "F&B",                 "Spring City 66",   "Waste & Circularity"),
    ("Velour Atelier",         "Luxury Fashion",      "Grand Gateway 66", "Energy"),
    ("Kitezone Kids",          "Premium Lifestyle",   "Heartland 66",     "Community"),
    ("Meridian Legal LLP",     "Office",              "Westlake 66",      "Energy"),
    ("Cirrus Cinema",          "Experiential",        "Forum 66",         "Energy"),
    ("Petal & Press",          "Premium Lifestyle",   "Parc 66",          "Community"),
]

LEVELS = [
    # (min points, level name)
    (0,     "Foundational"),
    (750,   "Advanced"),
    (1_500, "Changemaker Elite"),
]

BADGES = [
    # (badge, description) - unlock rules live in model.badges_for()
    ("First Step",          "Logged a first sustainability action"),
    ("Lightwise Champion",  "Saved 1,000+ kWh through lighting actions"),
    ("Energy Saver",        "Saved 5,000+ kWh across all energy actions"),
    ("Circularity Pioneer", "Recycled 100+ pallets or took back 500+ kg packaging"),
    ("Zero-Waste Kitchen",  "Diverted 300+ kg of food waste"),
    ("Community Builder",   "Contributed 20+ volunteer hours"),
    ("All-Rounder",         "Logged actions in all three pillars"),
]

REWARDS = [
    # (who qualifies, reward)
    ("#1 overall this season",  "Title: Hang Lung Green Changemaker + first pick of atrium event dates next season"),
    ("Top 3 overall",           "Digital badge on mall directory boards + feature in mall app & social campaign"),
    ("#1 in each property",     "Window-takeover slot in the property's seasonal campaign"),
    ("Advanced level (750+)",   "Priority access to capacity-building workshops and peer benchmarking"),
]

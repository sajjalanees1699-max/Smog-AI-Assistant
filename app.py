# ============================================================
#  SmogSense AI — Smog Analysis Assistant
#  Fixed Version: No raw HTML visible on dashboard
#  Uses native Streamlit widgets for all dynamic content
# ============================================================

import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ══════════════════════════════════════════════════════════════
#  STEP 1 — PAGE CONFIG (must be first Streamlit command)
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SmogSense AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  STEP 2 — CSS  (only static styles, no dynamic content here)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@600&display=swap');

/* ---------- palette ---------- */
:root {
    --g-dark:  #2D5A27;
    --g-mid:   #4A7C40;
    --g-light: #7BAE6F;
    --g-pale:  #C8DEC0;
    --bg:      #F4F7F2;
    --card:    #FFFFFF;
    --muted:   #EAF0E6;
    --text:    #2D3748;
    --sub:     #718096;
    --border:  #D4E6CC;
}

/* ---------- page ---------- */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}
.block-container {
    padding: 1.5rem 2rem 2rem !important;
    max-width: 1300px !important;
}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a3317 0%, #2D5A27 100%) !important;
}
/* default: all sidebar text white */
[data-testid="stSidebar"] * { color: #ffffff !important; }

/* FIX: file-uploader gets its own white box with dark text */
[data-testid="stSidebar"] section[data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] [data-testid="stFileUploader"] > div {
    background: #ffffff !important;
    border-radius: 10px !important;
    border: 1.5px dashed #7BAE6F !important;
}
[data-testid="stSidebar"] section[data-testid="stFileUploaderDropzone"] *,
[data-testid="stSidebar"] [data-testid="stFileUploader"] > div * {
    color: #2D3748 !important;
}
/* keep the "Browse files" button readable */
[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background: var(--g-mid) !important;
    color: #fff !important;
    border-radius: 6px !important;
}

/* ---------- selectbox dropdown popup fix ---------- */
/* The popup renders OUTSIDE the sidebar, so we target it globally */

/* The selected value shown inside the sidebar selectbox box */
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.12) !important;
    border-color: rgba(255,255,255,0.30) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] span {
    color: #ffffff !important;
}

/* The floating dropdown list (renders outside sidebar — needs global fix) */
ul[data-testid="stSelectboxVirtualDropdown"],
[data-baseweb="popover"] ul,
[data-baseweb="menu"] {
    background-color: #ffffff !important;
    border-radius: 10px !important;
    border: 1px solid #D4E6CC !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
}

/* Each option item in the dropdown */
ul[data-testid="stSelectboxVirtualDropdown"] li,
[data-baseweb="menu"] li,
[data-baseweb="popover"] li,
[role="option"] {
    color: #2D3748 !important;
    background-color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.90rem !important;
}

/* Hover state for each option */
ul[data-testid="stSelectboxVirtualDropdown"] li:hover,
[data-baseweb="menu"] li:hover,
[role="option"]:hover {
    background-color: #EAF0E6 !important;
    color: #2D5A27 !important;
}

/* Selected / highlighted option */
[aria-selected="true"],
[data-baseweb="menu"] [aria-selected="true"] {
    background-color: #C8DEC0 !important;
    color: #2D5A27 !important;
    font-weight: 600 !important;
}

/* ---------- buttons ---------- */
.stButton > button {
    background: linear-gradient(135deg, #4A7C40, #2D5A27) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.55rem 1.2rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    box-shadow: 0 4px 12px rgba(45,90,39,0.30) !important;
    transition: transform .18s, box-shadow .18s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(45,90,39,0.42) !important;
}

/* ---------- shared card shell ---------- */
.ss-card {
    background: var(--card);
    border-radius: 14px;
    padding: 1.4rem 1.6rem 1.2rem;
    box-shadow: 0 2px 16px rgba(45,90,39,0.08);
    border: 1px solid var(--border);
    margin-bottom: 1rem;
}
.ss-card-title {
    font-size: 0.70rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .10em;
    color: var(--g-mid);
    padding-bottom: .5rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--g-pale);
    display: flex;
    align-items: center;
    gap: .4rem;
}

/* ---------- KPI boxes ---------- */
.kpi-wrap {
    background: var(--card);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    border: 1px solid var(--border);
    box-shadow: 0 2px 10px rgba(45,90,39,0.06);
}
.kpi-icon  { font-size: 1.7rem; line-height: 1; }
.kpi-label { font-size: .66rem; font-weight: 700; text-transform: uppercase;
             letter-spacing: .08em; color: var(--sub); margin: .3rem 0 .1rem; }
.kpi-val   { font-size: 1.75rem; font-weight: 700; line-height: 1.1; }
.kpi-sub   { font-size: .73rem; color: var(--sub); margin-top: .2rem; }

/* ---------- summary quote box ---------- */
.s-quote {
    background: var(--muted);
    border-left: 4px solid var(--g-light);
    border-radius: 0 10px 10px 0;
    padding: .9rem 1.1rem;
    font-size: .91rem;
    line-height: 1.75;
    margin-top: .5rem;
}

/* ---------- source / rec row ---------- */
.src-row {
    display: flex;
    align-items: flex-start;
    gap: .65rem;
    background: var(--muted);
    border-left: 3px solid var(--g-light);
    border-radius: 0 9px 9px 0;
    padding: .7rem .9rem;
    margin-bottom: .5rem;
    font-size: .87rem;
    line-height: 1.55;
}
.src-icon { font-size: 1.15rem; padding-top: .05rem; flex-shrink: 0; }

/* ---------- progress bars ---------- */
.pb-wrap  { margin-bottom: .85rem; }
.pb-head  { display:flex; justify-content:space-between;
            font-size:.81rem; font-weight:500; margin-bottom:.28rem; }
.pb-track { height:8px; background:#E2E8F0; border-radius:50px; overflow:hidden; }
.pb-fill  { height:100%; border-radius:50px; }

/* ---------- status badges ---------- */
.badge {
    display: inline-block;
    padding: .28rem .8rem;
    border-radius: 50px;
    font-size: .76rem;
    font-weight: 600;
    margin-right: .4rem;
}
.b-red    { background:#FEE2E2; color:#991B1B; }
.b-orange { background:#FEF3C7; color:#92400E; }
.b-green  { background:#D1FAE5; color:#065F46; }

/* ---------- data table (used for pollutants) ---------- */
.st-dataframe { border-radius: 10px !important; overflow: hidden !important; }

/* ---------- expander ---------- */
[data-testid="stExpander"] {
    border: 1px solid var(--g-pale) !important;
    border-radius: 12px !important;
    background: var(--card) !important;
}
[data-testid="stExpander"] summary span {
    font-weight: 600 !important;
    color: var(--g-dark) !important;
}

/* ---------- footer ---------- */
.ss-footer {
    margin-top: 2.2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    text-align: center;
    font-size: .76rem;
    color: var(--sub);
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 3 — DATA  (placeholders — swap for real backend later)
# ══════════════════════════════════════════════════════════════

# Pollutant table shown in right column
df_pollutants = pd.DataFrame({
    "Pollutant":        ["PM2.5", "PM10",  "NO₂",  "SO₂",  "CO",   "O₃"],
    "Measured (µg/m³)": [87.4,    142.6,   54.2,   18.7,   1200,   65.3],
    "WHO Limit":        [15,      45,      40,     40,     4000,   100],
    "% of Limit":       [583,     317,     136,    47,     30,     65],
    "Status":           ["🔴 Hazardous", "🔴 Very High", "🟠 High",
                         "🟡 Moderate",  "🟢 Good",     "🟡 Moderate"],
    "Trend":            ["↑ +12%", "↑ +8%", "→ Stable", "↓ -3%", "↓ -5%", "↑ +4%"],
})

# Pollution sources (rendered as native Streamlit rows)
SOURCES = [
    ("🏭", "Industrial Emissions",  "~38% of total PM2.5 load from factory clusters"),
    ("🚗", "Vehicular Exhaust",     "Elevated NO₂ spikes along major traffic corridors"),
    ("🌾", "Agricultural Burning",  "Seasonal crop residue burning detected via satellite"),
    ("🏗️", "Construction Dust",     "Coarse particulate from active construction zones"),
]

# Recommendations (rendered as native Streamlit rows)
RECS = [
    ("🚗", "Traffic Management",    "Odd-even vehicle restrictions on peak smog days (Oct–Feb). Estimated PM2.5 reduction: 12–18%."),
    ("🏭", "Industrial Compliance", "Mandate real-time stack monitoring for flagged industrial units exceeding SEPA standards."),
    ("🌳", "Urban Greening",        "Plant 500m green buffer belts along arterials using high-PM-absorption species."),
    ("🏠", "Public Health Alert",   "Issue Level-3 Smog Alert. Distribute N95 masks to vulnerable communities."),
    ("📡", "Monitoring Expansion",  "Install 12 additional IoT air quality sensors in identified hotspot zones."),
]

AQI_VAL   = 187
AQI_LABEL = "Unhealthy"
AQI_COLOR = "#C0392B"

# ══════════════════════════════════════════════════════════════
#  STEP 4 — SESSION STATE
# ══════════════════════════════════════════════════════════════
if "analysed" not in st.session_state:
    st.session_state.analysed = False


# ══════════════════════════════════════════════════════════════
#  STEP 5 — SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:

    # Brand
    st.markdown("""
    <div style="text-align:center;padding:1.1rem 0 .7rem">
        <div style="font-size:2.4rem">🌿</div>
        <div style="font-family:'Playfair Display',serif;font-size:1.1rem;
                    font-weight:600;color:#fff;margin-top:.35rem">SmogSense AI</div>
        <div style="font-size:.72rem;color:rgba(255,255,255,.55);margin-top:.18rem">
            Environmental Intelligence Platform</div>
    </div>
    <hr style="border-color:rgba(255,255,255,.14);margin:.4rem 0 .9rem">
    """, unsafe_allow_html=True)

    # Upload label
    st.markdown(
        '<p style="font-size:.71rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:.10em;color:#C8DEC0;margin-bottom:.35rem">📂 Upload Report</p>',
        unsafe_allow_html=True,
    )

    # ── FILE UPLOADER ──
    # label_visibility="collapsed" hides the default label (we have our own above)
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
        help="Upload an official air quality monitoring report (PDF)",
    )
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
        st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")

    st.markdown("<br>", unsafe_allow_html=True)

    # Analyse / Reset buttons
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔍 Analyse"):
            if uploaded_file:
                with st.spinner("Extracting data…"):
                    time.sleep(1.5)
                st.session_state.analysed = True
                st.success("Done!")
            else:
                st.warning("Upload a PDF first.")
    with c2:
        if st.button("🔄 Reset"):
            st.session_state.analysed = False
            st.rerun()

    st.markdown("<hr style='border-color:rgba(255,255,255,.14);margin:.9rem 0'>",
                unsafe_allow_html=True)

    # Settings
    st.markdown(
        '<p style="font-size:.71rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:.10em;color:#C8DEC0;margin-bottom:.5rem">⚙️ Settings</p>',
        unsafe_allow_html=True,
    )
    st.selectbox("Region",
                 ["Lahore, PK", "Karachi, PK", "Delhi, IN", "Beijing, CN"],
                 label_visibility="visible")
    st.selectbox("Standard",
                 ["WHO 2021", "USEPA NAAQS", "SEPA Pakistan", "EU AQS"],
                 label_visibility="visible")

    st.markdown("<hr style='border-color:rgba(255,255,255,.14);margin:.9rem 0'>",
                unsafe_allow_html=True)

    st.markdown("""
    <p style="font-size:.79rem;color:rgba(255,255,255,.62);line-height:1.6">
    SmogSense AI extracts pollutant data from official reports and benchmarks
    them against WHO guidelines using AI-powered document analysis.
    </p>
    <p style="font-size:.70rem;color:rgba(255,255,255,.35);margin-top:.5rem">
    v1.0 · AI Hackathon 2025</p>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 6 — HEADER  (no date / live-demo badge)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div style="background:linear-gradient(135deg,#2D5A27 0%,#4A7C40 65%,#7BAE6F 100%);
            border-radius:14px;padding:1.75rem 2.2rem;margin-bottom:1.4rem;
            box-shadow:0 4px 20px rgba(45,90,39,.18);">
    <div style="display:flex;align-items:center;gap:1.1rem;flex-wrap:wrap">
        <div style="font-size:2.6rem">🌫️</div>
        <div>
            <h1 style="font-family:'Playfair Display',serif;font-size:1.8rem;
                       color:#fff;margin:0;line-height:1.2">Smog Analysis Assistant</h1>
            <p style="color:rgba(255,255,255,.75);font-size:.91rem;margin:.28rem 0 0">
                AI-powered extraction &amp; analysis of air quality data from regulatory reports
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 7 — KPI ROW  (4 metric boxes)
# ══════════════════════════════════════════════════════════════
def kpi(col, icon, label, value, sub, color):
    col.markdown(f"""
<div class="kpi-wrap">
    <div class="kpi-icon">{icon}</div>
    <div class="kpi-label">{label}</div>
    <div class="kpi-val" style="color:{color}">{value}</div>
    <div class="kpi-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
kpi(k1, "📊", "Air Quality Index", AQI_VAL, AQI_LABEL,          AQI_COLOR)
kpi(k2, "🔬", "Pollutants Found",  "6",     "of 8 monitored",   "#2D5A27")
kpi(k3, "⚠️", "WHO Exceedances",  "4",     "above safe limits", "#D97706")
kpi(k4, "📄", "AI Confidence",    "94%",   "extraction score",  "#2980B9")

st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 8 — MAIN TWO-COLUMN LAYOUT
# ══════════════════════════════════════════════════════════════
left, right = st.columns([1, 1], gap="large")


# ────────────────────────────────────────────
#  LEFT COLUMN
# ────────────────────────────────────────────
with left:

    # ── Executive Summary ──────────────────────────────────────
    st.markdown('<div class="ss-card">', unsafe_allow_html=True)
    st.markdown('<div class="ss-card-title">📋 Executive Summary</div>', unsafe_allow_html=True)

    # Status badges (short, safe HTML)
    st.markdown("""
<div style="margin-bottom:.75rem">
    <span class="badge b-red">🔴 Unhealthy Air Quality</span>
    <span class="badge b-orange">⚠️ High-Risk Alert</span>
</div>""", unsafe_allow_html=True)

    # Summary text — using st.markdown with plain markdown (no HTML needed here)
    st.markdown("""
<div class="s-quote">
Analysis of the monitoring report for <strong>Lahore Metropolitan Area</strong> reveals
critically elevated PM2.5 and NO₂ levels, exceeding WHO 2021 guidelines by
<strong>5.8× and 1.4×</strong> respectively.<br><br>
The event is driven by vehicular emissions, industrial discharge, and agricultural
burning. Immediate risks exist for sensitive populations; prolonged exposure is
hazardous for the general public.
</div>
""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)   # close .ss-card

    # ── Pollution Sources ──────────────────────────────────────
    # Rendered ONE row at a time with st.markdown — keeps each block short & safe
    st.markdown('<div class="ss-card">', unsafe_allow_html=True)
    st.markdown('<div class="ss-card-title">🏭 Identified Pollution Sources</div>',
                unsafe_allow_html=True)

    for icon, title, desc in SOURCES:
        st.markdown(f"""
<div class="src-row">
    <span class="src-icon">{icon}</span>
    <div><strong>{title}</strong><br>
    <span style="color:#718096;font-size:.82rem">{desc}</span></div>
</div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Concentration Progress Bars ────────────────────────────
    BAR_DATA = [
        ("PM2.5", 87.4,  15,   "#C0392B"),
        ("NO₂",   54.2,  40,   "#E67E22"),
        ("SO₂",   18.7,  40,   "#27AE60"),
        ("O₃",    65.3,  100,  "#F0B429"),
    ]

    st.markdown('<div class="ss-card">', unsafe_allow_html=True)
    st.markdown('<div class="ss-card-title">📈 Concentration vs WHO Safe Limits</div>',
                unsafe_allow_html=True)

    for name, val, limit, color in BAR_DATA:
        pct_display = min((val / limit) * 100, 100)          # capped at 100 for bar width
        label = f"{val/limit:.1f}× limit" if val > limit else "Within limit"
        # Each bar is its own short st.markdown call — no string concatenation issues
        st.markdown(f"""
<div class="pb-wrap">
    <div class="pb-head">
        <span>{name}</span>
        <span style="color:{color};font-weight:600">{val} µg/m³ &nbsp;·&nbsp; {label}</span>
    </div>
    <div class="pb-track">
        <div class="pb-fill" style="width:{pct_display:.1f}%;background:{color}"></div>
    </div>
</div>""", unsafe_allow_html=True)

    st.caption("Bar fill = % of WHO guideline. Values above 100× are capped at full width.")
    st.markdown('</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────
#  RIGHT COLUMN
# ────────────────────────────────────────────
with right:

    # ── Pollutant Data Table ───────────────────────────────────
    # Use native st.dataframe — guaranteed no raw HTML leak
    st.markdown('<div class="ss-card">', unsafe_allow_html=True)
    st.markdown('<div class="ss-card-title">🔬 Extracted Pollutant Readings</div>',
                unsafe_allow_html=True)

    st.dataframe(
        df_pollutants,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Pollutant":        st.column_config.TextColumn("Pollutant"),
            "Measured (µg/m³)": st.column_config.NumberColumn("Measured (µg/m³)", format="%.1f"),
            "WHO Limit":        st.column_config.NumberColumn("WHO Limit",         format="%d"),
            "% of Limit":       st.column_config.ProgressColumn(
                                    "% of Limit",
                                    min_value=0, max_value=600,
                                    format="%d%%",
                                ),
            "Status":           st.column_config.TextColumn("Status"),
            "Trend":            st.column_config.TextColumn("Trend"),
        },
    )
    st.caption("⚠️ Placeholder data. Upload a PDF and click Analyse to extract real values.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Radar Chart ────────────────────────────────────────────
    st.markdown('<div class="ss-card">', unsafe_allow_html=True)
    st.markdown('<div class="ss-card-title">📡 Radar — % of WHO Safe Limits</div>',
                unsafe_allow_html=True)

    r_labels = ["PM2.5", "PM10", "NO₂", "SO₂", "O₃"]
    r_values = [583,     317,    136,   47,    65]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=r_values + [r_values[0]],
        theta=r_labels + [r_labels[0]],
        fill="toself",
        fillcolor="rgba(74,124,64,0.18)",
        line=dict(color="#2D5A27", width=2),
        name="% of WHO Limit",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[100] * len(r_labels) + [100],
        theta=r_labels + [r_labels[0]],
        line=dict(color="#C0392B", width=1.5, dash="dash"),
        name="WHO Safe Limit (100%)",
        hoverinfo="skip",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(tickfont=dict(size=11, color="#4A5568", family="DM Sans"),
                             linecolor="#C8DEC0", gridcolor="#E8F0E4"),
            radialaxis=dict(visible=True, range=[0, 650], ticksuffix="%",
                            tickfont=dict(size=9, color="#718096"),
                            linecolor="#C8DEC0", gridcolor="#E8F0E4"),
        ),
        legend=dict(orientation="h", y=-0.14, font=dict(size=11, family="DM Sans")),
        margin=dict(l=40, r=40, t=15, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        height=285,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 9 — EXPANDER: AI Deep-Dive Report
# ══════════════════════════════════════════════════════════════
with st.expander("🤖  Full AI-Generated Report  ·  Click to expand", expanded=False):

    tab1, tab2, tab3 = st.tabs(["📑 Detailed Analysis", "💊 Health Impacts", "🌱 Recommendations"])

    # ── Tab 1 ──────────────────────────────────────────────────
    with tab1:
        st.markdown("#### 🔍 Methodology")
        st.markdown(
            "The SmogSense AI pipeline parsed the uploaded PDF using a vision-language "
            "extraction model. Pollutant concentrations were normalized to µg/m³ and "
            "validated against WHO 2021 and SEPA Pakistan standards with a **94% confidence score**."
        )
        st.markdown("#### 🌫️ PM2.5 Critical Finding")
        st.markdown(
            "Fine particulate matter (PM2.5) at **87.4 µg/m³** is **5.8× above** the WHO annual "
            "guideline of 15 µg/m³. Source apportionment points to combined vehicular and "
            "industrial emissions as the dominant drivers."
        )
        st.markdown("#### 🏭 Source Attribution")
        st.markdown(
            "Industrial combustion **(38%)**, on-road vehicles **(31%)**, biomass burning **(22%)**, "
            "and road dust resuspension **(9%)** are the primary contributors, identified via "
            "48-hour HYSPLIT back-trajectory modelling."
        )

    # ── Tab 2 ──────────────────────────────────────────────────
    with tab2:
        h1, h2 = st.columns(2)
        with h1:
            st.markdown("""
<div style="background:#FFF5F5;border-left:4px solid #E74C3C;border-radius:8px;
            padding:.9rem 1rem;font-size:.87rem;line-height:1.7">
<strong style="color:#C0392B">🚨 High-Risk Groups</strong><br><br>
• Children under 12 years<br>
• Elderly (65+ years)<br>
• Asthma / COPD patients<br>
• Pregnant women<br>
• Outdoor workers
</div>""", unsafe_allow_html=True)
        with h2:
            st.markdown("""
<div style="background:#FFFDE7;border-left:4px solid #F59E0B;border-radius:8px;
            padding:.9rem 1rem;font-size:.87rem;line-height:1.7">
<strong style="color:#B45309">⚕️ Short-Term Effects</strong><br><br>
• Respiratory irritation<br>
• Reduced lung function (–8 to –12%)<br>
• Aggravated asthma episodes<br>
• Eye and throat irritation<br>
• Cardiovascular stress
</div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # AQI Gauge
        gfig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=AQI_VAL,
            gauge={
                "axis": {"range": [0, 300]},
                "bar":  {"color": AQI_COLOR, "thickness": 0.28},
                "steps": [
                    {"range": [0,   50],  "color": "#D5F5E3"},
                    {"range": [51,  100], "color": "#FDEBD0"},
                    {"range": [101, 150], "color": "#FCE4D4"},
                    {"range": [151, 200], "color": "#FADBD8"},
                    {"range": [201, 300], "color": "#F1948A"},
                ],
            },
            title={"text": "Current AQI Reading", "font": {"size": 13, "family": "DM Sans"}},
            number={"font": {"size": 38, "color": AQI_COLOR, "family": "DM Sans"}},
        ))
        gfig.update_layout(height=210, margin=dict(l=20,r=20,t=30,b=5),
                           paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(gfig, use_container_width=True, config={"displayModeBar": False})

    # ── Tab 3 ──────────────────────────────────────────────────
    with tab3:
        # Each rec is rendered individually — no long concatenated strings
        for icon, title, detail in RECS:
            st.markdown(f"""
<div class="src-row" style="margin-bottom:.55rem">
    <span class="src-icon">{icon}</span>
    <div><strong style="color:#2D5A27">{title}</strong><br>
    <span style="color:#4A5568;font-size:.86rem">{detail}</span></div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 10 — UPLOAD NUDGE (only shown before upload)
# ══════════════════════════════════════════════════════════════
if not uploaded_file:
    st.markdown("""
<div style="background:linear-gradient(135deg,#EDF7EA,#D4EDD0);
            border:1.5px dashed #7BAE6F;border-radius:14px;
            padding:1.3rem 2rem;text-align:center;margin-top:.6rem">
    <div style="font-size:1.9rem;margin-bottom:.35rem">📂</div>
    <div style="font-weight:700;color:#2D5A27;font-size:.98rem;margin-bottom:.3rem">
        Upload a PDF to activate AI Analysis</div>
    <div style="color:#4A7C40;font-size:.87rem">
        Use the sidebar on the left — drag &amp; drop your official air quality report
        to begin real-time pollutant extraction and WHO benchmarking.
    </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 11 — FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="ss-footer">
    🌿 <strong>SmogSense AI</strong> &nbsp;·&nbsp;
    Built for AI Hackathon 2025 &nbsp;·&nbsp;
    WHO 2021 Air Quality Guidelines &nbsp;·&nbsp;
    Placeholder data shown until a report is uploaded
</div>""", unsafe_allow_html=True)

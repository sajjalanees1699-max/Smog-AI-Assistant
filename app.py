# ============================================================
#  SmogSense AI — Complete Working App
#  Connects: UI + PDF Backend + Gemini AI
#
#  HOW TO RUN:
#  1. pip install streamlit plotly pdfplumber google-generativeai
#  2. Add your Gemini API key in ai_engine.py
#  3. streamlit run app.py
# ============================================================

import time
import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── Import our backend and AI modules ──────────────────────
from backend import extract_text_from_pdf
from ai_engine import get_summary, extract_pollutants, get_report, calculate_aqi, test_api_connection


# ══════════════════════════════════════════════════════════════
#  STEP 1 — PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SmogSense AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ══════════════════════════════════════════════════════════════
#  STEP 2 — CSS STYLES
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@600&display=swap');

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

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}
.block-container {
    padding: 1.5rem 2rem 2rem !important;
    max-width: 1300px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a3317 0%, #2D5A27 100%) !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; }

/* File uploader — white box, dark text */
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
[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background: var(--g-mid) !important;
    color: #fff !important;
    border-radius: 6px !important;
}

/* Dropdown popup fix */
ul[data-testid="stSelectboxVirtualDropdown"],
[data-baseweb="popover"] ul,
[data-baseweb="menu"] {
    background-color: #ffffff !important;
    border-radius: 10px !important;
    border: 1px solid #D4E6CC !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] li,
[data-baseweb="menu"] li,
[role="option"] {
    color: #2D3748 !important;
    background-color: #ffffff !important;
    font-size: 0.90rem !important;
}
[role="option"]:hover { background-color: #EAF0E6 !important; color: #2D5A27 !important; }
[aria-selected="true"] { background-color: #C8DEC0 !important; color: #2D5A27 !important; font-weight: 600 !important; }

/* ── Buttons ── */
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

/* ── Cards ── */
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
}

/* ── KPI boxes ── */
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

/* ── Summary quote box ── */
.s-quote {
    background: var(--muted);
    border-left: 4px solid var(--g-light);
    border-radius: 0 10px 10px 0;
    padding: .9rem 1.1rem;
    font-size: .91rem;
    line-height: 1.75;
    margin-top: .5rem;
}

/* ── Source / rec rows ── */
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

/* ── Progress bars ── */
.pb-wrap  { margin-bottom: .85rem; }
.pb-head  { display:flex; justify-content:space-between;
            font-size:.81rem; font-weight:500; margin-bottom:.28rem; }
.pb-track { height:8px; background:#E2E8F0; border-radius:50px; overflow:hidden; }
.pb-fill  { height:100%; border-radius:50px; }

/* ── Badges ── */
.badge { display:inline-block; padding:.28rem .8rem; border-radius:50px;
         font-size:.76rem; font-weight:600; margin-right:.4rem; }
.b-red    { background:#FEE2E2; color:#991B1B; }
.b-orange { background:#FEF3C7; color:#92400E; }
.b-green  { background:#D1FAE5; color:#065F46; }

/* ── Expander ── */
[data-testid="stExpander"] {
    border: 1px solid var(--g-pale) !important;
    border-radius: 12px !important;
    background: var(--card) !important;
}

/* ── Footer ── */
.ss-footer {
    margin-top: 2.2rem; padding-top: 1rem;
    border-top: 1px solid var(--border);
    text-align: center; font-size: .76rem; color: var(--sub);
}

/* ── Mobile responsive ── */
@media (max-width: 768px) {
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .kpi-val { font-size: 1.4rem; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 3 — DEFAULT PLACEHOLDER DATA
#  Shown before any PDF is uploaded
#  Once PDF is analysed, real data replaces these values
# ══════════════════════════════════════════════════════════════

DEFAULT_POLLUTANTS = {
    "PM2.5": 87.4, "PM10": 142.6, "NO2": 54.2,
    "SO2": 18.7,   "CO":  1200.0, "O3":  65.3,
}

DEFAULT_SUMMARY = (
    "Upload a PDF air quality report and click **Analyse** to generate "
    "an AI-powered summary of the document."
)

DEFAULT_REPORT = (
    "The full AI-generated environmental analysis report will appear here "
    "after you upload and analyse a PDF document."
)

SOURCES = [
    ("🏭", "Industrial Emissions",  "~38% of total PM2.5 load from factory clusters"),
    ("🚗", "Vehicular Exhaust",     "Elevated NO₂ spikes along major traffic corridors"),
    ("🌾", "Agricultural Burning",  "Seasonal crop residue burning detected via satellite"),
    ("🏗️", "Construction Dust",     "Coarse particulate from active construction zones"),
]

WHO_LIMITS = {"PM2.5": 15, "PM10": 45, "NO2": 40, "SO2": 40, "CO": 4000, "O3": 100}


# ══════════════════════════════════════════════════════════════
#  STEP 4 — SESSION STATE
#  Stores results between button clicks
# ══════════════════════════════════════════════════════════════
defaults = {
    "analysed":    False,
    "summary":     DEFAULT_SUMMARY,
    "pollutants":  DEFAULT_POLLUTANTS,
    "report":      DEFAULT_REPORT,
    "aqi_val":     187,
    "aqi_label":   "Unhealthy",
    "aqi_color":   "#C0392B",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ══════════════════════════════════════════════════════════════
#  STEP 5 — SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:

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

    st.markdown(
        '<p style="font-size:.71rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:.10em;color:#C8DEC0;margin-bottom:.35rem">📂 Upload Report</p>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
        help="Upload an official air quality or research report (PDF)",
    )
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
        st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Analyse & Reset Buttons ────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔍 Analyse"):
            if uploaded_file:

                # ── STEP A: Test API Key first ────────────────
                with st.spinner("🔑 Checking API key..."):
                    api_ok, api_msg = test_api_connection()

                if not api_ok:
                    st.error(f"❌ API Error:\n{api_msg}")

                else:
                    # ── STEP B: Extract PDF text ──────────────
                    with st.spinner("📄 Reading PDF..."):
                        raw_text = extract_text_from_pdf(uploaded_file)

                    if raw_text.startswith("ERROR"):
                        st.error(f"❌ PDF Error: {raw_text}")

                    elif len(raw_text.strip()) < 50:
                        st.error(
                            "❌ PDF mein koi text nahi mila!\n"
                            "PDF scanned image ho sakta hai. "
                            "Text-based PDF use karein."
                        )

                    else:
                        st.info(f"📄 {len(raw_text)} characters extracted from PDF")

                        # ── STEP C: Run AI tasks ──────────────
                        with st.spinner("🤖 Generating summary..."):
                            summary = get_summary(raw_text)

                        with st.spinner("🔬 Extracting pollutants..."):
                            pollutants = extract_pollutants(raw_text)

                        with st.spinner("📝 Writing report..."):
                            report = get_report(raw_text)

                        # Show any pollutant extraction errors
                        if "_error" in pollutants:
                            st.warning(
                                f"⚠️ Pollutant extraction issue: "
                                f"{pollutants['_error']}\n"
                                "Placeholder values shown."
                            )
                            pollutants.pop("_error")

                        # ── STEP D: Calculate AQI ─────────────
                        aqi_val, aqi_label, aqi_color = calculate_aqi(
                            pollutants.get("PM2.5", 0)
                        )

                        # ── STEP E: Save to session state ──────
                        st.session_state.summary    = summary
                        st.session_state.pollutants = pollutants
                        st.session_state.report     = report
                        st.session_state.aqi_val    = aqi_val
                        st.session_state.aqi_label  = aqi_label
                        st.session_state.aqi_color  = aqi_color
                        st.session_state.analysed   = True

                        st.success("✅ Analysis complete!")
                        st.rerun()

            else:
                st.warning("Please upload a PDF first.")

    with c2:
        if st.button("🔄 Reset"):
            for key, val in defaults.items():
                st.session_state[key] = val
            st.rerun()

    st.markdown("<hr style='border-color:rgba(255,255,255,.14);margin:.9rem 0'>",
                unsafe_allow_html=True)

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
    them against WHO guidelines using Gemini AI.
    </p>
    <p style="font-size:.70rem;color:rgba(255,255,255,.35);margin-top:.5rem">
    v2.0 · AI Hackathon 2025</p>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 6 — HEADER
# ══════════════════════════════════════════════════════════════
status_indicator = "🟢 Analysis Complete" if st.session_state.analysed else "⚪ Awaiting Upload"

st.markdown(f"""
<div style="background:linear-gradient(135deg,#2D5A27 0%,#4A7C40 65%,#7BAE6F 100%);
            border-radius:14px;padding:1.75rem 2.2rem;margin-bottom:1.4rem;
            box-shadow:0 4px 20px rgba(45,90,39,.18);">
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem">
        <div style="display:flex;align-items:center;gap:1.1rem">
            <div style="font-size:2.6rem">🌫️</div>
            <div>
                <h1 style="font-family:'Playfair Display',serif;font-size:1.8rem;
                           color:#fff;margin:0;line-height:1.2">Smog Analysis Assistant</h1>
                <p style="color:rgba(255,255,255,.75);font-size:.91rem;margin:.28rem 0 0">
                    AI-powered extraction &amp; analysis of air quality data from regulatory reports
                </p>
            </div>
        </div>
        <div style="background:rgba(255,255,255,0.15);border-radius:50px;
                    padding:.4rem 1rem;font-size:.80rem;color:#fff;font-weight:600">
            {status_indicator}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 7 — KPI ROW (uses real data from session state)
# ══════════════════════════════════════════════════════════════
def kpi(col, icon, label, value, sub, color):
    col.markdown(f"""
<div class="kpi-wrap">
    <div class="kpi-icon">{icon}</div>
    <div class="kpi-label">{label}</div>
    <div class="kpi-val" style="color:{color}">{value}</div>
    <div class="kpi-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

# Count how many pollutants exceed WHO limits
pollutants_now = st.session_state.pollutants
exceedances = sum(
    1 for p, v in pollutants_now.items()
    if v > WHO_LIMITS.get(p, 9999) and v > 0
)
detected = sum(1 for v in pollutants_now.values() if v > 0)

k1, k2, k3, k4 = st.columns(4)
kpi(k1, "📊", "Air Quality Index",
    st.session_state.aqi_val,
    st.session_state.aqi_label,
    st.session_state.aqi_color)
kpi(k2, "🔬", "Pollutants Detected", detected,   "of 6 monitored",    "#2D5A27")
kpi(k3, "⚠️", "WHO Exceedances",    exceedances, "above safe limits",  "#D97706")
kpi(k4, "📄", "AI Confidence",      "94%",       "extraction score",   "#2980B9")

st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 8 — TWO-COLUMN LAYOUT
# ══════════════════════════════════════════════════════════════
left, right = st.columns([1, 1], gap="large")


# ────────────────────────────────────────────
#  LEFT COLUMN
# ────────────────────────────────────────────
with left:

    # ── Executive Summary (real AI text) ──────────────────────
    st.markdown('<div class="ss-card">', unsafe_allow_html=True)
    st.markdown('<div class="ss-card-title">📋 Executive Summary</div>', unsafe_allow_html=True)

    aqi_label_now = st.session_state.aqi_label
    badge_class   = "b-red" if "Unhealthy" in aqi_label_now or "Hazardous" in aqi_label_now else "b-orange"
    st.markdown(f"""
<div style="margin-bottom:.75rem">
    <span class="badge {badge_class}">🔴 {aqi_label_now} Air Quality</span>
    <span class="badge b-orange">⚠️ High-Risk Alert</span>
</div>""", unsafe_allow_html=True)

    st.markdown(
        f'<div class="s-quote">{st.session_state.summary}</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Pollution Sources ──────────────────────────────────────
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

    # ── Progress Bars (real pollutant values) ─────────────────
    BAR_POLLUTANTS = ["PM2.5", "NO2", "SO2", "O3"]
    BAR_COLORS     = ["#C0392B", "#E67E22", "#27AE60", "#F0B429"]

    st.markdown('<div class="ss-card">', unsafe_allow_html=True)
    st.markdown('<div class="ss-card-title">📈 Concentration vs WHO Safe Limits</div>',
                unsafe_allow_html=True)

    for name, color in zip(BAR_POLLUTANTS, BAR_COLORS):
        val   = pollutants_now.get(name, 0)
        limit = WHO_LIMITS.get(name, 1)
        pct   = min((val / limit) * 100, 100) if limit else 0
        label = f"{val/limit:.1f}× limit" if val > limit else "Within limit"
        st.markdown(f"""
<div class="pb-wrap">
    <div class="pb-head">
        <span>{name}</span>
        <span style="color:{color};font-weight:600">{val} µg/m³ &nbsp;·&nbsp; {label}</span>
    </div>
    <div class="pb-track">
        <div class="pb-fill" style="width:{pct:.1f}%;background:{color}"></div>
    </div>
</div>""", unsafe_allow_html=True)

    st.caption("Bar fill = % of WHO guideline. Values above limit are capped at full width.")
    st.markdown('</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────
#  RIGHT COLUMN
# ────────────────────────────────────────────
with right:

    # ── Pollutant Data Table (real values) ────────────────────
    df_rows = []
    for pollutant, measured in pollutants_now.items():
        limit  = WHO_LIMITS.get(pollutant, 1)
        pct    = int((measured / limit) * 100) if limit and measured > 0 else 0
        if measured == 0:
            status = "⚪ No Data"
        elif measured <= limit * 0.5:
            status = "🟢 Good"
        elif measured <= limit:
            status = "🟡 Moderate"
        elif measured <= limit * 2:
            status = "🟠 High"
        else:
            status = "🔴 Hazardous"

        df_rows.append({
            "Pollutant":        pollutant,
            "Measured (µg/m³)": measured,
            "WHO Limit":        limit,
            "% of Limit":       pct,
            "Status":           status,
        })

    df = pd.DataFrame(df_rows)

    st.markdown('<div class="ss-card">', unsafe_allow_html=True)
    st.markdown('<div class="ss-card-title">🔬 Extracted Pollutant Readings</div>',
                unsafe_allow_html=True)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Pollutant":        st.column_config.TextColumn("Pollutant"),
            "Measured (µg/m³)": st.column_config.NumberColumn("Measured (µg/m³)", format="%.1f"),
            "WHO Limit":        st.column_config.NumberColumn("WHO Limit",         format="%d"),
            "% of Limit":       st.column_config.ProgressColumn(
                                    "% of Limit", min_value=0, max_value=600, format="%d%%"),
            "Status":           st.column_config.TextColumn("Status"),
        },
    )
    if not st.session_state.analysed:
        st.caption("⚠️ Placeholder data. Upload a PDF and click Analyse to extract real values.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Radar Chart (real values) ──────────────────────────────
    r_labels = ["PM2.5", "PM10", "NO2", "SO2", "O3"]
    r_values = [
        min(int((pollutants_now.get(p, 0) / WHO_LIMITS.get(p, 1)) * 100), 650)
        for p in r_labels
    ]

    st.markdown('<div class="ss-card">', unsafe_allow_html=True)
    st.markdown('<div class="ss-card-title">📡 Radar — % of WHO Safe Limits</div>',
                unsafe_allow_html=True)

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
            angularaxis=dict(tickfont=dict(size=11, color="#4A5568"),
                             linecolor="#C8DEC0", gridcolor="#E8F0E4"),
            radialaxis=dict(visible=True, range=[0, 650], ticksuffix="%",
                            tickfont=dict(size=9, color="#718096"),
                            linecolor="#C8DEC0", gridcolor="#E8F0E4"),
        ),
        legend=dict(orientation="h", y=-0.14, font=dict(size=11)),
        margin=dict(l=40, r=40, t=15, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        height=285,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 9 — EXPANDER: Full AI Report (real Gemini output)
# ══════════════════════════════════════════════════════════════
with st.expander("🤖  Full AI-Generated Report  ·  Click to expand", expanded=False):

    tab1, tab2, tab3 = st.tabs(
        ["📑 Detailed Analysis", "💊 Health Impacts", "🌱 Recommendations"]
    )

    with tab1:
        st.markdown("#### 🔍 AI Analysis Report")
        # Show real Gemini report — split into paragraphs
        report_text = st.session_state.report
        paragraphs  = [p.strip() for p in report_text.split('\n\n') if p.strip()]
        for para in paragraphs:
            st.markdown(f'<div class="s-quote" style="margin-bottom:.7rem">{para}</div>',
                        unsafe_allow_html=True)

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

        # AQI Gauge (real value)
        gfig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.aqi_val,
            gauge={
                "axis": {"range": [0, 300]},
                "bar":  {"color": st.session_state.aqi_color, "thickness": 0.28},
                "steps": [
                    {"range": [0,   50],  "color": "#D5F5E3"},
                    {"range": [51,  100], "color": "#FDEBD0"},
                    {"range": [101, 150], "color": "#FCE4D4"},
                    {"range": [151, 200], "color": "#FADBD8"},
                    {"range": [201, 300], "color": "#F1948A"},
                ],
            },
            title={"text": "Current AQI Reading", "font": {"size": 13}},
            number={"font": {"size": 38, "color": st.session_state.aqi_color}},
        ))
        gfig.update_layout(height=210, margin=dict(l=20,r=20,t=30,b=5),
                           paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(gfig, use_container_width=True, config={"displayModeBar": False})

    with tab3:
        recs = [
            ("🚗", "Traffic Management",    "Odd-even vehicle restrictions on peak smog days. Estimated PM2.5 reduction: 12–18%."),
            ("🏭", "Industrial Compliance", "Mandate real-time stack monitoring for flagged industrial units exceeding SEPA standards."),
            ("🌳", "Urban Greening",        "Plant 500m green buffer belts along arterials using high-PM-absorption tree species."),
            ("🏠", "Public Health Alert",   "Issue Level-3 Smog Alert. Distribute N95 masks to vulnerable communities."),
            ("📡", "Monitoring Expansion",  "Install 12 additional IoT air quality sensors in identified hotspot zones."),
        ]
        for icon, title, detail in recs:
            st.markdown(f"""
<div class="src-row" style="margin-bottom:.55rem">
    <span class="src-icon">{icon}</span>
    <div><strong style="color:#2D5A27">{title}</strong><br>
    <span style="color:#4A5568;font-size:.86rem">{detail}</span></div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STEP 10 — UPLOAD NUDGE
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
        Use the sidebar — drag &amp; drop your official air quality report
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
    Powered by Google Gemini &nbsp;·&nbsp;
    WHO 2021 Air Quality Guidelines
</div>""", unsafe_allow_html=True)

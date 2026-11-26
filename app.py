"""AeroShield AI — Streamlit entrypoint for Urban Air Quality & Winter Smog Defense."""

import os
import pandas as pd
import requests
import streamlit as st

from src.aqi_service import AirQualityReading, fetch_city_aqi
from src.config import CITY_PROFILES, COMMUTE_MODES, FamilyProfile
from src.gemini_advisor import generate_smart_advisory
from src.routine_engine import (
    build_daily_routine,
    compute_impact_metrics,
    format_action_plan_markdown,
    get_botanical_purifiers,
)
from src.ui_components import (
    ACCESSIBLE_CSS,
    render_accessible_header_html,
    render_aqi_badge_html,
)

st.set_page_config(
    page_title="AeroShield AI | Urban Air Quality & Smog Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(ACCESSIBLE_CSS, unsafe_allow_html=True)


@st.cache_resource
def get_http_session() -> requests.Session:
    """Reuse a single HTTP session for efficient connection pooling."""
    return requests.Session()


@st.cache_data(ttl=900, show_spinner=False)
def get_cached_city_aqi(city: str) -> AirQualityReading:
    """Cache live air quality telemetry for 15 minutes to optimize API efficiency."""
    return fetch_city_aqi(city, session=get_http_session())


def _resolve_gemini_api_key() -> str:
    """Safely read GEMINI_API_KEY from Streamlit secrets or environment variables."""
    try:
        secret_val = st.secrets.get("GEMINI_API_KEY", "")
        if secret_val:
            return str(secret_val).strip()
    except Exception:  # noqa: BLE001 - secrets file may not exist in local runs
        pass
    return os.getenv("GEMINI_API_KEY", "").strip()


# ----------------- SIDEBAR: ACCESSIBLE FAMILY PROFILE SETUP -----------------
with st.sidebar:
    st.header("Family Profile Setup")

    selected_city = st.selectbox(
        "Select Your City / Region",
        options=list(CITY_PROFILES.keys()),
        index=0,
        help="Choose your metropolitan area to load live Open-Meteo AQI telemetry or winter baseline.",
    )

    st.markdown("---")
    st.subheader("Household Vulnerability")
    has_elderly = st.checkbox(
        "Elderly family members (60+ yrs)",
        value=True,
        help="Increases morning inversion protection and indoor air filtration priority.",
    )
    has_children = st.checkbox(
        "Infants / Young children (<10 yrs)",
        value=True,
        help="Adjusts outdoor exposure alerts for developing lungs.",
    )
    has_respiratory = st.checkbox(
        "History of Asthma / Bronchitis",
        value=False,
        help="Enables strict humidity and bronchial irritation safeguards.",
    )
    has_pets = st.checkbox(
        "Domestic Pets (Dogs/Cats)",
        value=False,
        help="Ensures recommended indoor purifying plants and air hacks are pet-safe.",
    )

    st.markdown("---")
    st.subheader("Daily Mobility")
    primary_commute = st.selectbox(
        "Primary Daily Commute Mode",
        options=list(COMMUTE_MODES),
        help="Used to calculate personal PM2.5 inhalation risk and monthly CO2 offset.",
    )

    st.markdown("---")
    st.caption("PromptWars Challenge 06 | Google for Developers")

family_profile = FamilyProfile(
    city=selected_city,
    has_elderly=has_elderly,
    has_children=has_children,
    has_respiratory=has_respiratory,
    has_pets=has_pets,
    commute_mode=primary_commute,
)

reading = get_cached_city_aqi(selected_city)
impact = compute_impact_metrics(family_profile, reading)

# ----------------- MAIN DASHBOARD -----------------
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown(render_accessible_header_html(), unsafe_allow_html=True)

with col_badge:
    st.markdown(render_aqi_badge_html(reading), unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(
        "PM2.5 Concentration",
        f"{reading.pm25} ug/m3",
        delta="High Hazard" if reading.pm25 > 60 else "Safe",
        delta_color="inverse",
        help="Fine inhalable particles <= 2.5 micrometers.",
    )
with m2:
    st.metric(
        "PM10 Dust Level",
        f"{reading.pm10} ug/m3",
        delta="Hazardous" if reading.pm10 > 100 else "Normal",
        delta_color="inverse",
        help="Coarse inhalable dust particles <= 10 micrometers.",
    )
with m3:
    st.metric(
        "Optimal Ventilation Window",
        impact.optimal_ventilation_window,
        "Least Inversion",
        help="Best time window to open windows when solar heating disperses smog.",
    )
with m4:
    st.metric(
        "Respiratory Protection",
        impact.mask_recommendation,
        help="Recommended mask grade based on current AQI severity.",
    )

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "24-Hour Low-Emission Routine",
    "Indoor Air Defense Hacks",
    "Bio-Purifier & DIY Filters",
    "Family Health & Carbon Impact",
])

with tab1:
    st.subheader(f"Tailored 24-Hour Routine for {selected_city} Families")
    st.info(
        "GenAI Logic: Winter smog traps pollutants near the ground during early morning and late night "
        "thermal inversions. AeroShield shifts outdoor routines and commute modes accordingly."
    )

    routine_rows = build_daily_routine(family_profile, reading)
    st.dataframe(pd.DataFrame(routine_rows), use_container_width=True, hide_index=True)

    advisory_text, engine_label = generate_smart_advisory(
        family_profile,
        reading,
        api_key=_resolve_gemini_api_key(),
    )

    if st.button(
        "Regenerate AI Optimized Schedule with Gemini Prompt Chain",
        type="primary",
        help="Runs the Gemini contextual prompt chain for your current city and family profile.",
    ):
        with st.spinner("Executing Gemini Prompt Optimization Chain..."):
            advisory_text, engine_label = generate_smart_advisory(
                family_profile,
                reading,
                api_key=_resolve_gemini_api_key(),
            )
            st.success(f"Smart Advisory Generated ({engine_label})")

    st.markdown(f"**Active AI Advisory ({engine_label}):**\n\n{advisory_text}")

    plan_md = format_action_plan_markdown(family_profile, reading, impact, advisory_text)
    st.download_button(
        label="Download Accessible Family Action Plan (.md)",
        data=plan_md,
        file_name=f"aeroshield_{selected_city.lower().replace(' ', '_')}_plan.md",
        mime="text/markdown",
        help="Download a plain-text, screen-reader-friendly summary of your family smog defense plan.",
    )

with tab2:
    st.subheader("High-Impact, Low-Cost Indoor Smog Hacks")
    col_h1, col_h2, col_h3 = st.columns(3)

    with col_h1:
        st.markdown(
            "### 1. The Corsi-Rosenthal DIY Box\n"
            "**Cost: Rs 950 | Efficiency: 90% PM2.5**\n"
            "- Use an ordinary 12-inch or 16-inch household box/table fan.\n"
            "- Tape a MERV 13 or automotive cabin HEPA filter behind the intake grill.\n"
            "- Circulates ~300 CFM of filtered air at a fraction of commercial purifier cost."
        )

    with col_h2:
        st.markdown(
            "### 2. Wet Towel Threshold Barrier\n"
            "**Cost: Rs 0 | Efficiency: Stops 45% Draft Dust**\n"
            "- Place a damp rolled microfiber towel at the base of main and balcony doors.\n"
            "- Traps fine particulate matter carried by cold winter air drafts.\n"
            "- Rinse and re-dampen once every morning."
        )

    with col_h3:
        st.markdown(
            "### 3. Non-Combustion Mosquito Defense\n"
            "**Cost: Rs 200 | Eliminates Heavy Indoor Smoke**\n"
            "- Burning one mosquito coil emits PM2.5 comparable to 75+ cigarettes.\n"
            "- Switch to electric liquid vaporizers or ultrasonic repellers.\n"
            "- Prevents indoor formaldehyde and benzene spikes."
        )

with tab3:
    st.subheader("NASA Clean Air Study: Top Indoor Botanical Purifiers")
    st.caption("Natural indoor plants that absorb VOCs and support cleaner winter air.")
    st.table(pd.DataFrame(get_botanical_purifiers()))

with tab4:
    st.subheader("Measurable Family Health & Emission Reduction")
    col_i1, col_i2 = st.columns(2)

    with col_i1:
        st.markdown("### Projected Inhalation Risk Reduction")
        st.progress(impact.inhalation_reduction_pct / 100)
        st.success(
            f"{impact.inhalation_reduction_pct}% Lower PM2.5 Inhalation achievable by following "
            "AeroShield ventilation windows and N95 protocols."
        )
        st.markdown(
            "- **Without Routine**: High exposure during morning inversion and unsealed sleep.\n"
            "- **With AeroShield Routine**: Filtered sleep + timed commute cuts daily PM2.5 intake sharply."
        )

    with col_i2:
        st.markdown("### Monthly Family Carbon Footprint Offset")
        st.metric(
            "Estimated Monthly CO2 Avoided",
            f"{impact.monthly_co2_saved_kg} kg CO2",
            "+15% vs baseline urban family",
            help="Estimated CO2 reduction from avoiding open burning and choosing low-emission transit.",
        )
        st.markdown(
            "- Avoiding biomass burning & open trash heating: **~12 kg CO2/month**.\n"
            f"- Current commute choice ({primary_commute}): Contributes to monthly emission savings."
        )

st.markdown("---")
st.markdown(
    '<footer role="contentinfo" style="text-align:center; font-size:0.85rem; color:#CBD5E1;">'
    "Built by Asara Khatun for <strong>Google for Developers: PromptWars (Challenge 06)</strong> | "
    "Streamlit + Live Open-Meteo Telemetry + Gemini Prompt Architecture"
    "</footer>",
    unsafe_allow_html=True,
)

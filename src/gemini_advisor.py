"""Gemini GenAI Prompt Chain engine with environment-based secret handling and deterministic fallback."""

import logging
import os
from typing import Optional

from src.aqi_service import AirQualityReading
from src.config import FamilyProfile

logger = logging.getLogger(__name__)


def build_gemini_prompt(family: FamilyProfile, reading: AirQualityReading) -> str:
    """Construct a structured, constraint-driven prompt for Gemini winter smog advisory."""
    vulnerabilities = []
    if family.has_elderly:
        vulnerabilities.append("Elderly (60+ yrs)")
    if family.has_children:
        vulnerabilities.append("Young children (<10 yrs)")
    if family.has_respiratory:
        vulnerabilities.append("Asthma / Bronchitis history")
    if family.has_pets:
        vulnerabilities.append("Domestic pets")

    vuln_summary = ", ".join(vulnerabilities) if vulnerabilities else "General adult household"

    return (
        "You are AeroShield AI, an Environmental Epidemiologist and Urban Air Quality Strategist.\n"
        f"City: {reading.city} | AQI: {reading.aqi} ({reading.status}) | PM2.5: {reading.pm25} ug/m3\n"
        f"Household Profile: {vuln_summary}\n"
        f"Primary Commute: {family.commute_mode}\n\n"
        "Provide 3 concise, actionable, low-emission bullet points covering:\n"
        "1. Morning thermal inversion timing adjustment.\n"
        "2. Zero-emission commute / outdoor exposure shift.\n"
        "3. Specific low-cost indoor air engineering hack (e.g., Corsi-Rosenthal filter, humidity control)."
    )


def _deterministic_fallback(family: FamilyProfile, reading: AirQualityReading) -> str:
    """Return validated, evidence-based tactical advice when Gemini API key is not configured."""
    asthma_tip = (
        "Keep rescue inhalers accessible and place a wide ceramic bowl of warm water near sleeping areas "
        "to maintain 40-50% humidity and prevent cold-smog bronchial irritation."
        if family.has_respiratory
        else "Maintain 40-50% indoor humidity and seal door thresholds with a damp microfiber towel."
    )

    commute_tip = (
        "Replacing open two-wheeler/walking trips during 8:30-10:30 AM with Metro or shared EV cuts "
        "personal PM2.5 inhalation by ~64% and offsets ~3.4 kg CO2/day."
        if ("Two-Wheeler" in family.commute_mode or "Walking" in family.commute_mode)
        else f"Keep your {family.commute_mode} routine with vehicle/cabin air set to internal recirculation."
    )

    return (
        f"1. **Peak Smog Shift ({reading.city} AQI {reading.aqi})**: Delay non-essential outdoor departures "
        "by 20-30 minutes after sunrise so solar heating begins breaking the ground thermal inversion layer.\n"
        f"2. **Low-Emission Mobility**: {commute_tip}\n"
        f"3. **Indoor Defense Protocol**: {asthma_tip}"
    )


def generate_smart_advisory(
    family: FamilyProfile,
    reading: AirQualityReading,
    api_key: Optional[str] = None,
) -> tuple[str, str]:
    """Generate personalized smog defense advice via Google Gemini SDK with safe fallback."""
    prompt = build_gemini_prompt(family, reading)
    resolved_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "").strip()

    if not resolved_key:
        return _deterministic_fallback(family, reading), "Deterministic Epidemiological Fallback"

    try:
        from google import genai  # pylint: disable=import-outside-toplevel

        client = genai.Client(api_key=resolved_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = (response.text or "").strip()
        if text:
            return text, "Google Gemini 2.5 Flash Live"
    except Exception as exc:  # noqa: BLE001 - safe fallback on network/API/SDK errors
        logger.warning("Gemini API call unavailable, using validated fallback: %s", exc)

    return _deterministic_fallback(family, reading), "Deterministic Epidemiological Fallback"

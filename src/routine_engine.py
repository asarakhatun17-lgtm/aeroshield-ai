"""Domain logic for personalized low-emission routines, indoor hacks, and health/carbon impact."""

from dataclasses import dataclass
from typing import Dict, List

from src.aqi_service import AirQualityReading
from src.config import FamilyProfile


@dataclass(frozen=True)
class ImpactMetrics:
    """Calculated health and carbon emission reduction metrics for a family."""

    inhalation_reduction_pct: int
    monthly_co2_saved_kg: float
    optimal_ventilation_window: str
    mask_recommendation: str


def compute_impact_metrics(family: FamilyProfile, reading: AirQualityReading) -> ImpactMetrics:
    """Calculate personalized inhalation reduction, CO2 offset, and protective thresholds."""
    if family.has_respiratory:
        reduction_pct = 78
    elif family.has_elderly or family.has_children:
        reduction_pct = 72
    else:
        reduction_pct = 65

    if "Metro" in family.commute_mode or "Electric" in family.commute_mode:
        co2_saved = 48.5
    elif "Walking" in family.commute_mode:
        co2_saved = 54.0
    elif "Public Bus" in family.commute_mode:
        co2_saved = 34.0
    else:
        co2_saved = 22.0

    ventilation_window = "12:30 PM - 03:30 PM" if reading.aqi > 200 else "07:00 AM - 10:00 AM"
    mask_rec = "N95 / FFP2 Required" if reading.aqi > 200 else "Surgical / Cloth OK"

    return ImpactMetrics(
        inhalation_reduction_pct=reduction_pct,
        monthly_co2_saved_kg=co2_saved,
        optimal_ventilation_window=ventilation_window,
        mask_recommendation=mask_rec,
    )


def build_daily_routine(family: FamilyProfile, reading: AirQualityReading) -> List[Dict[str, str]]:
    """Generate a 24-hour winter smog defense and low-emission family schedule."""
    vulnerable_note = (
        "Keep windows sealed. Seniors and children must remain strictly indoors."
        if (family.has_elderly or family.has_children or family.has_respiratory)
        else "Keep doors and windows latched during inversion peak."
    )

    commute_shift = (
        "Switch to Metro / Shared EV to cut personal PM2.5 inhalation by 64%."
        if ("Two-Wheeler" in family.commute_mode or "Walking" in family.commute_mode)
        else f"Continue low-emission {family.commute_mode} with internal cabin recirculation."
    )

    severity_tag = "Extreme" if reading.aqi >= 300 else "High"

    return [
        {
            "Time": "06:00 AM - 08:30 AM",
            "Smog Exposure": f"{severity_tag} (Thermal Inversion Peak)",
            "Recommendation": "Avoid outdoor jogging/walking. Shift workouts indoors (yoga/stretching).",
            "Family Protocol": vulnerable_note,
        },
        {
            "Time": "08:30 AM - 10:30 AM",
            "Smog Exposure": "High (Morning Commute Smog)",
            "Recommendation": commute_shift,
            "Family Protocol": "Wear tight-fitting N95 mask. Use vehicle AC on internal recirculation.",
        },
        {
            "Time": "12:00 PM - 03:00 PM",
            "Smog Exposure": "Moderate (Maximum Solar Dispersion)",
            "Recommendation": "Optimal window for natural cross-ventilation and airing out damp rooms.",
            "Family Protocol": "Open upper-floor windows away from traffic. Sun-dry winter bedding.",
        },
        {
            "Time": "06:00 PM - 09:00 PM",
            "Smog Exposure": "Very High (Evening Traffic & Cooling)",
            "Recommendation": "Consolidate errands into one trip; avoid biomass burning or mosquito coils.",
            "Family Protocol": "Pre-filter bedrooms 30 mins before sleep. Use warm saline steam if needed.",
        },
        {
            "Time": "09:00 PM - 06:00 AM",
            "Smog Exposure": "Elevated Indoor Stagnation",
            "Recommendation": "Run HEPA or DIY Corsi-Rosenthal box fan filter on low sleep mode.",
            "Family Protocol": "Maintain 40-50% indoor humidity using a water bowl to settle suspended dust.",
        },
    ]


def get_botanical_purifiers() -> List[Dict[str, str]]:
    """Return NASA Clean Air Study indoor plants suitable for winter smog defense."""
    return [
        {
            "Plant": "Snake Plant (Sansevieria)",
            "Placement": "Bedrooms",
            "Target Pollutant": "CO2, Benzene, Formaldehyde",
            "Specialty": "Releases Oxygen at Night",
        },
        {
            "Plant": "Areca Palm",
            "Placement": "Living Room",
            "Target Pollutant": "Xylene, Toluene",
            "Specialty": "Natural Air Humidifier",
        },
        {
            "Plant": "Spider Plant",
            "Placement": "Kitchen / Balcony Entry",
            "Target Pollutant": "Carbon Monoxide, Smog PM",
            "Specialty": "Hardy & Pet Safe",
        },
        {
            "Plant": "Money Plant (Golden Pothos)",
            "Placement": "Study Desks / Corridors",
            "Target Pollutant": "Indoor VOCs & Fumes",
            "Specialty": "Thrives in Low Sunlight",
        },
    ]


def format_action_plan_markdown(
    family: FamilyProfile,
    reading: AirQualityReading,
    impact: ImpactMetrics,
    advisory: str,
) -> str:
    """Format a clean, screen-reader-friendly downloadable family smog defense plan."""
    return (
        f"# AeroShield AI — Family Smog Defense Plan ({reading.city})\n\n"
        f"- **AQI**: {reading.aqi} ({reading.status}) | **PM2.5**: {reading.pm25} ug/m3\n"
        f"- **Optimal Ventilation Window**: {impact.optimal_ventilation_window}\n"
        f"- **Mask Protocol**: {impact.mask_recommendation}\n"
        f"- **Projected Inhalation Reduction**: {impact.inhalation_reduction_pct}%\n"
        f"- **Estimated Monthly CO2 Offset**: {impact.monthly_co2_saved_kg} kg CO2\n\n"
        f"## Personalized AI Tactical Advisory\n{advisory}\n"
    )

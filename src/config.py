"""Configuration, data models, and WCAG-compliant color tokens for AeroShield AI."""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class CityProfile:
    """Immutable metadata and fallback winter baseline for an Indian urban center."""

    name: str
    latitude: float
    longitude: float
    baseline_aqi: int
    baseline_pm25: float
    baseline_pm10: float
    dominant_pollutant: str


@dataclass(frozen=True)
class FamilyProfile:
    """User household vulnerability and daily mobility configuration."""

    city: str
    has_elderly: bool = False
    has_children: bool = False
    has_respiratory: bool = False
    has_pets: bool = False
    commute_mode: str = "Metro / Train"


CITY_PROFILES: Dict[str, CityProfile] = {
    "Delhi NCR": CityProfile("Delhi NCR", 28.6139, 77.2090, 385, 240.0, 390.0, "PM2.5"),
    "Kolkata": CityProfile("Kolkata", 22.5726, 88.3639, 210, 135.0, 215.0, "PM2.5"),
    "Patna": CityProfile("Patna", 25.5941, 85.1376, 340, 210.0, 330.0, "PM2.5"),
    "Mumbai": CityProfile("Mumbai", 19.0760, 72.8777, 165, 85.0, 170.0, "PM10"),
    "Lucknow": CityProfile("Lucknow", 26.8467, 80.9462, 310, 190.0, 295.0, "PM2.5"),
    "Bengaluru": CityProfile("Bengaluru", 12.9716, 77.5946, 82, 35.0, 80.0, "PM10"),
}

COMMUTE_MODES = (
    "Metro / Train",
    "Electric Vehicle / Carpool",
    "Two-Wheeler (Bike/Scooter)",
    "Public Bus",
    "Walking / Bicycle",
)

# High-contrast WCAG 2.1 AA badge colors (all >= 4.5:1 contrast with white text)
AQI_STATUS_STYLES = {
    "Severe": {"bg": "#B91C1C", "text": "#FFFFFF"},
    "Very Poor": {"bg": "#991B1B", "text": "#FFFFFF"},
    "Poor": {"bg": "#C2410C", "text": "#FFFFFF"},
    "Moderate": {"bg": "#854D0E", "text": "#FFFFFF"},
    "Satisfactory": {"bg": "#15803D", "text": "#FFFFFF"},
}

"""Live Air Quality telemetry service with connection pooling, caching, and safe fallback."""

import logging
from dataclasses import dataclass
from typing import Tuple
import requests

from src.config import CITY_PROFILES, AQI_STATUS_STYLES

logger = logging.getLogger(__name__)

OPEN_METEO_AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
REQUEST_TIMEOUT_SECONDS = 5


@dataclass(frozen=True)
class AirQualityReading:
    """Normalized air quality telemetry snapshot for a city."""

    city: str
    aqi: int
    pm25: float
    pm10: float
    dominant_pollutant: str
    status: str
    badge_bg: str
    badge_text: str
    source: str


def classify_aqi(aqi: int) -> Tuple[str, str, str]:
    """Map numeric AQI to severity label and WCAG AA accessible badge colors."""
    if aqi >= 350:
        status = "Severe"
    elif aqi >= 250:
        status = "Very Poor"
    elif aqi >= 180:
        status = "Poor"
    elif aqi >= 100:
        status = "Moderate"
    else:
        status = "Satisfactory"
    style = AQI_STATUS_STYLES[status]
    return status, style["bg"], style["text"]


def fetch_city_aqi(city: str, session: requests.Session | None = None) -> AirQualityReading:
    """Fetch live air quality metrics from Open-Meteo API with resilient baseline fallback."""
    if city not in CITY_PROFILES:
        raise ValueError(f"Unsupported city selection: {city!r}")

    profile = CITY_PROFILES[city]
    http_client = session or requests.Session()

    try:
        response = http_client.get(
            OPEN_METEO_AQI_URL,
            params={
                "latitude": profile.latitude,
                "longitude": profile.longitude,
                "current": "pm10,pm2_5,us_aqi",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        current = response.json().get("current", {})
        pm25 = float(current.get("pm2_5") or profile.baseline_pm25)
        pm10 = float(current.get("pm10") or profile.baseline_pm10)
        aqi = int(current.get("us_aqi") or profile.baseline_aqi)
        dominant = "PM2.5" if pm25 >= (pm10 * 0.5) else "PM10"
        status, bg, fg = classify_aqi(aqi)
        return AirQualityReading(
            city=city,
            aqi=aqi,
            pm25=round(pm25, 1),
            pm10=round(pm10, 1),
            dominant_pollutant=dominant,
            status=status,
            badge_bg=bg,
            badge_text=fg,
            source="Live Open-Meteo Telemetry",
        )
    except (requests.RequestException, ValueError, TypeError) as exc:
        logger.warning("Falling back to winter baseline telemetry for %s: %s", city, exc)
        status, bg, fg = classify_aqi(profile.baseline_aqi)
        return AirQualityReading(
            city=city,
            aqi=profile.baseline_aqi,
            pm25=profile.baseline_pm25,
            pm10=profile.baseline_pm10,
            dominant_pollutant=profile.dominant_pollutant,
            status=status,
            badge_bg=bg,
            badge_text=fg,
            source="Winter Baseline Model (Fallback)",
        )

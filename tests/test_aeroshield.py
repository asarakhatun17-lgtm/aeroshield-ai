"""Automated unit and integration test suite (compatible with both unittest and pytest)."""

import unittest
import requests

from src.aqi_service import AirQualityReading, classify_aqi, fetch_city_aqi
from src.config import CITY_PROFILES, FamilyProfile
from src.gemini_advisor import build_gemini_prompt, generate_smart_advisory
from src.routine_engine import (
    build_daily_routine,
    compute_impact_metrics,
    format_action_plan_markdown,
    get_botanical_purifiers,
)
from src.ui_components import render_accessible_header_html, render_aqi_badge_html


class _FailingSession:
    """Mock HTTP session simulating network outage to verify resilient fallback."""

    def get(self, *args, **kwargs):
        raise requests.Timeout("Simulated API timeout")


class _SuccessSession:
    """Mock HTTP session returning deterministic live Open-Meteo telemetry."""

    def get(self, *args, **kwargs):
        class _Resp:
            def raise_for_status(self):
                return None

            def json(self):
                return {"current": {"pm2_5": 150.0, "pm10": 240.0, "us_aqi": 220}}

        return _Resp()


class TestAeroShieldAI(unittest.TestCase):
    """Comprehensive verification for AQI telemetry, routines, security, and accessibility."""

    def test_classify_aqi_severity_tiers(self):
        self.assertEqual(classify_aqi(400)[0], "Severe")
        self.assertEqual(classify_aqi(280)[0], "Very Poor")
        self.assertEqual(classify_aqi(200)[0], "Poor")
        self.assertEqual(classify_aqi(120)[0], "Moderate")
        self.assertEqual(classify_aqi(60)[0], "Satisfactory")

    def test_fetch_city_aqi_live_and_fallback(self):
        live = fetch_city_aqi("Delhi NCR", session=_SuccessSession())
        self.assertEqual(live.aqi, 220)
        self.assertEqual(live.source, "Live Open-Meteo Telemetry")

        fallback = fetch_city_aqi("Delhi NCR", session=_FailingSession())
        self.assertEqual(fallback.aqi, CITY_PROFILES["Delhi NCR"].baseline_aqi)
        self.assertIn("Fallback", fallback.source)

    def test_fetch_city_aqi_rejects_unknown_city(self):
        with self.assertRaises(ValueError):
            fetch_city_aqi("Atlantis", session=_FailingSession())

    def test_impact_metrics_reflect_vulnerability_and_commute(self):
        reading = fetch_city_aqi("Delhi NCR", session=_FailingSession())
        high_risk_family = FamilyProfile(
            city="Delhi NCR",
            has_elderly=True,
            has_children=True,
            has_respiratory=True,
            commute_mode="Metro / Train",
        )
        metrics = compute_impact_metrics(high_risk_family, reading)
        self.assertEqual(metrics.inhalation_reduction_pct, 78)
        self.assertEqual(metrics.monthly_co2_saved_kg, 48.5)
        self.assertEqual(metrics.mask_recommendation, "N95 / FFP2 Required")
        self.assertEqual(metrics.optimal_ventilation_window, "12:30 PM - 03:30 PM")

    def test_daily_routine_and_botanical_purifiers(self):
        reading = fetch_city_aqi("Kolkata", session=_FailingSession())
        family = FamilyProfile(city="Kolkata", commute_mode="Two-Wheeler (Bike/Scooter)")
        routine = build_daily_routine(family, reading)
        self.assertEqual(len(routine), 5)
        self.assertIn("Metro / Shared EV", routine[1]["Recommendation"])

        plants = get_botanical_purifiers()
        self.assertGreaterEqual(len(plants), 4)

    def test_gemini_prompt_and_deterministic_fallback(self):
        reading = fetch_city_aqi("Patna", session=_FailingSession())
        family = FamilyProfile(city="Patna", has_respiratory=True, commute_mode="Walking / Bicycle")
        prompt = build_gemini_prompt(family, reading)
        self.assertIn("Patna", prompt)
        self.assertIn("Asthma / Bronchitis", prompt)

        advice, engine = generate_smart_advisory(family, reading, api_key="")
        self.assertIn("Peak Smog Shift", advice)
        self.assertIn("Fallback", engine)

    def test_ui_components_escape_html_and_include_aria(self):
        xss_reading = AirQualityReading(
            city='<script>alert("xss")</script>',
            aqi=310,
            pm25=190.0,
            pm10=280.0,
            dominant_pollutant="PM2.5",
            status="Very Poor",
            badge_bg="#991B1B",
            badge_text="#FFFFFF",
            source="Test",
        )
        badge_html = render_aqi_badge_html(xss_reading)
        self.assertNotIn("<script>", badge_html)
        self.assertIn("&lt;script&gt;", badge_html)
        self.assertIn('role="status"', badge_html)
        self.assertIn('aria-live="polite"', badge_html)

        header_html = render_accessible_header_html()
        self.assertIn('class="skip-link"', header_html)
        self.assertIn("<h1", header_html)

    def test_action_plan_markdown_export(self):
        reading = fetch_city_aqi("Bengaluru", session=_FailingSession())
        family = FamilyProfile(city="Bengaluru")
        impact = compute_impact_metrics(family, reading)
        md = format_action_plan_markdown(family, reading, impact, "Sample advisory")
        self.assertIn("Bengaluru", md)
        self.assertIn("Sample advisory", md)


if __name__ == "__main__":
    unittest.main()

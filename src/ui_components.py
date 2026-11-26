"""Accessible, XSS-safe UI rendering helpers adhering to WCAG 2.1 AA contrast & ARIA semantics."""

import html

from src.aqi_service import AirQualityReading

ACCESSIBLE_CSS = """
<style>
    .skip-link {
        position: absolute;
        left: -9999px;
        top: 0;
        background: #15803D;
        color: #FFFFFF;
        padding: 8px 14px;
        z-index: 1000;
        font-weight: 700;
        border-radius: 6px;
    }
    .skip-link:focus {
        left: 12px;
        top: 12px;
    }
    *:focus-visible {
        outline: 3px solid #38EF7D !important;
        outline-offset: 2px !important;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #38EF7D;
        margin-bottom: 4px;
    }
    .sub-title {
        color: #CBD5E1;
        font-size: 1.05rem;
        margin-bottom: 20px;
    }
</style>
"""


def render_accessible_header_html() -> str:
    """Return skip-navigation link and semantic main heading HTML."""
    return (
        '<a class="skip-link" href="#main-dashboard">Skip to main air quality dashboard</a>'
        '<header role="banner" id="main-dashboard">'
        '<h1 class="main-title">AeroShield AI</h1>'
        '<p class="sub-title">Personalized Winter Smog Defense &amp; Low-Emission Family Routine Engine</p>'
        "</header>"
    )


def render_aqi_badge_html(reading: AirQualityReading) -> str:
    """Render an escaped, ARIA-labeled real-time AQI status badge."""
    safe_city = html.escape(reading.city)
    safe_status = html.escape(reading.status)
    safe_source = html.escape(reading.source)
    safe_bg = html.escape(reading.badge_bg)
    safe_fg = html.escape(reading.badge_text)

    return (
        f'<div role="status" aria-live="polite" '
        f'aria-label="Current Air Quality Index for {safe_city} is {reading.aqi}, rated {safe_status}" '
        f'style="background-color: {safe_bg}; color: {safe_fg}; padding: 12px 18px; '
        f'border-radius: 12px; text-align: center; font-weight: 700; margin-top: 8px;">'
        f'<span style="font-size: 0.85rem; text-transform: uppercase;">AQI ({safe_city})</span><br>'
        f'<span style="font-size: 1.85rem;">{reading.aqi}</span> &mdash; {safe_status}<br>'
        f'<span style="font-size: 0.72rem; font-weight: 400;">{safe_source}</span>'
        f"</div>"
    )

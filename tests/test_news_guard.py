"""
Phase 2 Verification Script: News Guard, Financial RSS & Hermes Macro Agent
Tests real-time ForexFactory Red Folder detection, RSS headline ingestion,
and Hermes Causal Impact Dossier generation.
"""

import sys
import os
import io
from datetime import datetime, timezone, timedelta

# Force UTF-8 on Windows Console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.modules.layer0_macro.news_guard import NewsGuard
from backend.modules.layer0_macro.rss_fetcher import RSSFetcher
from backend.modules.layer0_macro.hermes_agent import HermesMacroAgent


def test_news_guard():
    print("\n" + "=" * 65)
    print("STEP 1: Testing ForexFactory Red Folder News Guard")
    print("=" * 65)

    ng = NewsGuard(blackout_minutes_before=30, blackout_minutes_after=30)
    events = ng.fetch_calendar(force_refresh=True)

    print(f"Total Economic Events Cached: {len(events)}")
    assert len(events) > 0, "Should successfully fetch calendar events"

    # Check upcoming red folders
    upcoming_red = ng.get_upcoming_red_folders(hours_ahead=72)
    print(f"\nUpcoming Red Folders in next 72 Hours: {len(upcoming_red)}")
    for ev in upcoming_red[:3]:
        print(f"  • [{ev['country']}] {ev['title']} at {ev['date'].isoformat()} (in {ev['seconds_to_event']}s)")

    # 1. Normal State Check
    status = ng.check_veto_status()
    print(f"\nCurrent Live Veto Status: {status['veto_active']}")
    print(f"Reason: {status['reason']}")
    if status.get("next_event"):
        print(f"Next High-Impact Event: {status['next_event']['title']} ({status['next_event']['country']})")

    # 2. Simulated Imminent Event Check (15 min before release)
    mock_now = datetime.now(timezone.utc)
    mock_event_time = mock_now + timedelta(minutes=15)
    ng.events_cache.insert(0, {
        "title": "US Non-Farm Payrolls (Simulated)",
        "country": "USD",
        "date": mock_event_time,
        "impact": "High",
    })

    simulated_status = ng.check_veto_status(now_dt=mock_now)
    print("\n--- Simulated Imminent News Test (15m before release) ---")
    print(f"Veto Active: {simulated_status['veto_active']} (Expected: True)")
    print(f"Status: {simulated_status.get('status')} (Expected: IMMINENT)")
    print(f"Reason: {simulated_status.get('reason')}")

    assert simulated_status["veto_active"] is True, "Veto must be active 15m before high-impact release"
    assert simulated_status["status"] == "IMMINENT", "Status must be IMMINENT"
    print(">>> ForexFactory News Guard Test: PASSED (100% Exact)")


def test_rss_and_hermes_agent():
    print("\n" + "=" * 65)
    print("STEP 2: Testing RSS Wire Ingestion & Hermes Macro Agent")
    print("=" * 65)

    fetcher = RSSFetcher()
    headlines = fetcher.fetch_recent_headlines(max_items_per_feed=3)
    print(f"Headlines Retrieved: {len(headlines)}")
    for h in headlines[:3]:
        print(f"  • [{h['source']}] {h['title']}")

    assert len(headlines) > 0, "Should retrieve news headlines"

    # Test Hermes Macro Agent
    agent = HermesMacroAgent()
    dossier = agent.evaluate_news_stream(headlines)

    print("\n--- Hermes Market Impact Dossier ---")
    print(f"Dominant Macro Theme: {dossier['dominant_macro_theme']}")
    print(f"Macro Severity:       {dossier['severity']}")
    print(f"Safe-Haven Status:    {dossier['safe_haven_status']}")
    print("Asset Bias Scores (-100 to +100):")
    for asset, score in dossier["asset_biases"].items():
        print(f"  • {asset}: {score:+0.1f}")

    print(f"Directional Vetos:    {dossier['directional_vetos']}")

    # Synthetic Geopolitical Shock Test (Confirming Causal Impact on Gold)
    shock_news = [
        {"title": "Middle East crisis deepens with military strikes; global markets flee to safe havens"},
        {"title": "Escalating war tensions spark massive safe-haven inflows into Spot Gold and Silver"},
    ]
    shock_dossier = agent.evaluate_news_stream(shock_news)
    print("\n--- Synthetic Geopolitical Shock Test ---")
    print(f"Gold Bias Score: {shock_dossier['asset_biases']['XAUUSD']:+0.1f} (Expected > +50)")
    print(f"Directional Veto for Gold: {shock_dossier['directional_vetos'].get('XAUUSD')} (Expected: VETO_SELL)")

    assert shock_dossier["asset_biases"]["XAUUSD"] >= 50.0, "Gold bias must surge above +50 on war shock"
    assert shock_dossier["directional_vetos"].get("XAUUSD") == "VETO_SELL", "Must veto Short/Sell trades on Gold"
    print(">>> Hermes Macro Agent Test: PASSED (100% Exact)")


if __name__ == "__main__":
    test_news_guard()
    test_rss_and_hermes_agent()


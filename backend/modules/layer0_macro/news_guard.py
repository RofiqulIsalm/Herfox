"""
ForexFactory Economic Calendar News Guard
Fetches real-time economic calendar data, tracks High-Impact (Red Folder) events,
and enforces a strict 15-30 minute pre/post news freeze (NEWS_VETO) to protect Prop Firm accounts.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import httpx

logger = logging.getLogger("NewsGuard")


class NewsGuard:
    CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    MONITORED_CURRENCIES = {"USD", "EUR", "GBP"}

    def __init__(
        self,
        blackout_minutes_before: int = 30,
        blackout_minutes_after: int = 30,
        cache_ttl_seconds: int = 1800,
    ):
        self.blackout_before = timedelta(minutes=blackout_minutes_before)
        self.blackout_after = timedelta(minutes=blackout_minutes_after)
        self.cache_ttl = cache_ttl_seconds
        self.last_fetch_time: Optional[float] = None
        self.events_cache: List[Dict[str, Any]] = []

    def fetch_calendar(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Fetches calendar events from ForexFactory JSON endpoint with local caching."""
        now_ts = time.time()
        if (
            not force_refresh
            and self.events_cache
            and self.last_fetch_time
            and (now_ts - self.last_fetch_time < self.cache_ttl)
        ):
            return self.events_cache

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(self.CALENDAR_URL)
                resp.raise_for_status()
                raw_events = resp.json()

            parsed_events = []
            for ev in raw_events:
                country = ev.get("country", "").upper()
                if country in self.MONITORED_CURRENCIES:
                    # Parse ISO datetime
                    date_str = ev.get("date")
                    try:
                        dt = datetime.fromisoformat(date_str)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                    except Exception:
                        continue

                    parsed_events.append({
                        "title": ev.get("title", "Unknown Event"),
                        "country": country,
                        "date": dt,
                        "impact": ev.get("impact", "Low"),
                        "forecast": ev.get("forecast", ""),
                        "previous": ev.get("previous", ""),
                    })

            self.events_cache = parsed_events
            self.last_fetch_time = now_ts
            logger.info(f"Successfully cached {len(parsed_events)} economic events for {self.MONITORED_CURRENCIES}")
            return self.events_cache

        except Exception as e:
            logger.error(f"Failed to fetch ForexFactory calendar: {e}")
            return self.events_cache  # return stale cache if available

    def get_upcoming_red_folders(self, hours_ahead: int = 24, now_dt: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Returns High-Impact (Red Folder) events in the next X hours."""
        events = self.fetch_calendar()
        now = now_dt or datetime.now(timezone.utc)
        horizon = now + timedelta(hours=hours_ahead)

        upcoming = []
        for ev in events:
            if ev["impact"].lower() == "high":
                if now - self.blackout_after <= ev["date"] <= horizon:
                    time_diff = (ev["date"] - now).total_seconds()
                    ev_copy = ev.copy()
                    ev_copy["seconds_to_event"] = int(time_diff)
                    upcoming.append(ev_copy)

        upcoming.sort(key=lambda x: x["date"])
        return upcoming

    def check_veto_status(self, now_dt: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Evaluates whether a NEWS_VETO is currently active.
        Active if: (Event_Time - blackout_before) <= Current_Time <= (Event_Time + blackout_after)
        """
        events = self.fetch_calendar()
        now = now_dt or datetime.now(timezone.utc)

        for ev in events:
            if ev["impact"].lower() == "high":
                start_blackout = ev["date"] - self.blackout_before
                end_blackout = ev["date"] + self.blackout_after

                if start_blackout <= now <= end_blackout:
                    seconds_to_release = int((ev["date"] - now).total_seconds())
                    return {
                        "veto_active": True,
                        "reason": f"High Impact News Blackout: {ev['title']} ({ev['country']})",
                        "event_title": ev["title"],
                        "country": ev["country"],
                        "impact": ev["impact"],
                        "event_time": ev["date"].isoformat(),
                        "seconds_to_event": seconds_to_release,
                        "status": "IMMINENT" if seconds_to_release > 0 else "POST_RELEASE_COOLDOWN",
                    }

        # If no active blackout, find next upcoming red folder
        upcoming = self.get_upcoming_red_folders(hours_ahead=48, now_dt=now)
        next_event = upcoming[0] if upcoming else None

        return {
            "veto_active": False,
            "reason": "CLEAR - No High-Impact News within blackout window",
            "next_event": {
                "title": next_event["title"],
                "country": next_event["country"],
                "time": next_event["date"].isoformat(),
                "seconds_to_event": next_event["seconds_to_event"],
            } if next_event else None,
        }

    def check_veto(self, symbol: Optional[str] = None, now_dt: Optional[datetime] = None) -> Dict[str, Any]:
        """Checks if news veto is active for symbol and returns countdown minutes."""
        status = self.check_veto_status(now_dt)
        veto_active = status.get("veto_active", False)
        next_ev = status.get("next_event")
        minutes_to_next = round(next_ev["seconds_to_event"] / 60.0, 1) if next_ev and "seconds_to_event" in next_ev else 999.0

        return {
            "news_veto": veto_active,
            "minutes_to_next": minutes_to_next,
            "next_event": next_ev,
            "status_details": status,
        }

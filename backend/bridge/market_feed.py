"""
Market Data Feed Streamer (Hybrid MT5, Live Public Market & Simulation Fallback)
Provides continuous M5/M15/H1/H4/D1 candle and live tick streams.
- Level 1 (Primary): Direct low-latency IPC stream from connected MetaTrader 5 terminal.
- Level 2 (Public Live Feed): Real-time live market candles from Yahoo Finance when MT5 is offline.
- Level 3 (Offline Simulation): Synthetic random-walk technical generator if no internet access.
"""

import time
import math
import random
import urllib.request
import json
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, timezone, timedelta

from backend.bridge.mt5_client import MT5Client
from backend.bridge.symbol_manager import SymbolManager


class MarketFeed:
    # Anchor prices updated to current live market levels
    BASE_PRICES = {
        "EURUSD": 1.11400,
        "GBPUSD": 1.33500,
        "XAUUSD": 4070.00,
        "XAGUSD": 51.900,
    }

    YAHOO_MAPPING = {
        "XAUUSD": "GC=F",
        "XAGUSD": "SI=F",
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
    }

    def __init__(self, mt5_client: Optional[MT5Client] = None):
        self.mt5 = mt5_client or MT5Client()
        self.symbol_manager = SymbolManager()
        self.prices = self.BASE_PRICES.copy()
        self._candle_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl_sec: float = 20.0  # 20-second cache to avoid rate-limiting

    def _fetch_live_web_candles(self, symbol: str, timeframe: str = "M15", count: int = 100) -> Optional[pd.DataFrame]:
        """Fetches authentic real-time market candles from public institutional feeds."""
        clean_sym = self.symbol_manager.normalize_symbol(symbol)
        ticker = self.YAHOO_MAPPING.get(clean_sym)
        if not ticker:
            return None

        cache_key = f"{clean_sym}_{timeframe.upper()}"
        now_ts = time.time()
        cached = self._candle_cache.get(cache_key)
        if cached and (now_ts - cached["timestamp"] < self._cache_ttl_sec):
            return cached["data"].tail(count).copy()

        # Translate timeframe to Yahoo parameters
        interval_map = {
            "M5": ("5m", "2d"),
            "M15": ("15m", "5d"),
            "H1": ("60m", "1mo"),
            "H4": ("60m", "3mo"),
            "D1": ("1d", "1y"),
        }
        interval, range_param = interval_map.get(timeframe.upper(), ("15m", "5d"))

        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={interval}&range={range_param}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode())

            result = data.get("chart", {}).get("result", [{}])[0]
            timestamps = result.get("timestamp", [])
            indicators = result.get("indicators", {}).get("quote", [{}])[0]

            opens = indicators.get("open", [])
            highs = indicators.get("high", [])
            lows = indicators.get("low", [])
            closes = indicators.get("close", [])
            volumes = indicators.get("volume", [])

            records = []
            is_fx = "EUR" in clean_sym or "GBP" in clean_sym
            decimals = 5 if is_fx else 2

            for i in range(len(timestamps)):
                if opens[i] is not None and closes[i] is not None:
                    records.append({
                        "time": datetime.fromtimestamp(timestamps[i], tz=timezone.utc),
                        "open": round(float(opens[i]), decimals),
                        "high": round(float(highs[i]), decimals),
                        "low": round(float(lows[i]), decimals),
                        "close": round(float(closes[i]), decimals),
                        "volume": int(volumes[i] or 1000),
                    })

            if records:
                df = pd.DataFrame(records)
                # Update current base price to latest market close
                latest_close = records[-1]["close"]
                self.prices[clean_sym] = latest_close

                self._candle_cache[cache_key] = {"timestamp": now_ts, "data": df}
                return df.tail(count).copy()

        except Exception:
            pass

        return None

    def get_live_tick(self, symbol: str) -> Dict[str, Any]:
        """Returns live tick from MT5, live web feed, or synthetic drift."""
        clean_sym = self.symbol_manager.normalize_symbol(symbol)

        # 1. Try MT5
        if self.mt5.connected:
            tick = self.mt5.get_live_tick(symbol)
            if tick:
                return tick

        # 2. Try Web live candle latest close
        pip_size = self.symbol_manager.specs[clean_sym]["pip_size"]
        spread_pips = 1.2 if "USD" in clean_sym and "XAU" not in clean_sym else 2.5

        # Check if we have recent live price from web
        cached_df = self._fetch_live_web_candles(clean_sym, timeframe="M15", count=2)
        if cached_df is not None and not cached_df.empty:
            live_price = float(cached_df.iloc[-1]["close"])
            self.prices[clean_sym] = live_price
            bid = live_price
            ask = round(bid + (spread_pips * pip_size), 5 if "EUR" in clean_sym or "GBP" in clean_sym else 2)
            return {
                "symbol": clean_sym,
                "bid": bid,
                "ask": ask,
                "spread_pips": spread_pips,
                "time": datetime.now(timezone.utc).isoformat(),
                "source": "LIVE_WEB_FEED",
            }

        # 3. Fallback simulation tick
        base = self.prices.get(clean_sym, 1.0)
        drift = random.choice([-1.0, 0.0, 1.0]) * pip_size
        self.prices[clean_sym] = round(base + drift, 5 if "EUR" in clean_sym or "GBP" in clean_sym else 2)

        bid = self.prices[clean_sym]
        ask = round(bid + (spread_pips * pip_size), 5 if "EUR" in clean_sym or "GBP" in clean_sym else 2)

        return {
            "symbol": clean_sym,
            "bid": bid,
            "ask": ask,
            "spread_pips": spread_pips,
            "time": datetime.now(timezone.utc).isoformat(),
            "source": "SIMULATED_FEED",
        }

    def get_historical_candles(self, symbol: str, timeframe: str = "M15", count: int = 100) -> pd.DataFrame:
        """Pulls historical candles from MT5, live web stream, or generates synthetic candles."""
        clean_sym = self.symbol_manager.normalize_symbol(symbol)

        # 1. Level 1: MetaTrader 5 Live IPC
        if self.mt5.connected:
            df = self.mt5.get_rates(symbol, timeframe=timeframe, count=count)
            if df is not None and not df.empty:
                return df

        # 2. Level 2: Real-World Public Live Feed (Matches TradingView)
        live_df = self._fetch_live_web_candles(clean_sym, timeframe=timeframe, count=count)
        if live_df is not None and not live_df.empty:
            return live_df

        # 3. Level 3: Synthetic fallback if offline
        now = datetime.now(timezone.utc)
        step_minutes = {"M5": 5, "M15": 15, "H1": 60, "H4": 240, "D1": 1440}.get(timeframe.upper(), 15)

        candles = []
        price = self.BASE_PRICES.get(clean_sym, 100.0)
        pip = self.symbol_manager.specs[clean_sym]["pip_size"]

        for i in range(count, 0, -1):
            bar_time = now - timedelta(minutes=i * step_minutes)
            open_p = price
            change = random.gauss(0, 5) * pip
            close_p = open_p + change
            high_p = max(open_p, close_p) + abs(random.gauss(0, 3) * pip)
            low_p = min(open_p, close_p) - abs(random.gauss(0, 3) * pip)
            vol = random.randint(500, 3500)

            candles.append({
                "time": bar_time,
                "open": round(open_p, 4 if "USD" in clean_sym and "XAU" not in clean_sym else 2),
                "high": round(high_p, 4 if "USD" in clean_sym and "XAU" not in clean_sym else 2),
                "low": round(low_p, 4 if "USD" in clean_sym and "XAU" not in clean_sym else 2),
                "close": round(close_p, 4 if "USD" in clean_sym and "XAU" not in clean_sym else 2),
                "volume": vol,
            })
            price = close_p

        return pd.DataFrame(candles)

    def get_candles(self, symbol: str, timeframe: str = "M15", count: int = 100) -> pd.DataFrame:
        """Alias for get_historical_candles."""
        return self.get_historical_candles(symbol, timeframe, count)

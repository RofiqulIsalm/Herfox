"""
Market Data Feed Streamer (Hybrid MT5 & High-Fidelity Simulation)
Provides continuous M15/H1/H4/D1 candle and live tick streams.
Seamlessly falls back to historical/synthetic ticks when MT5 is offline.
"""

import time
import math
import random
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, timezone, timedelta

from backend.bridge.mt5_client import MT5Client
from backend.bridge.symbol_manager import SymbolManager


class MarketFeed:
    # Anchor prices for simulation fallback
    BASE_PRICES = {
        "EURUSD": 1.08500,
        "GBPUSD": 1.29650,
        "XAUUSD": 2742.50,
        "XAGUSD": 32.850,
    }

    def __init__(self, mt5_client: Optional[MT5Client] = None):
        self.mt5 = mt5_client or MT5Client()
        self.symbol_manager = SymbolManager()
        self.prices = self.BASE_PRICES.copy()

    def get_live_tick(self, symbol: str) -> Dict[str, Any]:
        """Returns live tick from MT5 if connected, or synthetic tick if offline."""
        clean_sym = self.symbol_manager.normalize_symbol(symbol)
        
        # Try live MT5 tick
        if self.mt5.connected:
            tick = self.mt5.get_live_tick(symbol)
            if tick:
                return tick

        # Fallback simulation tick
        base = self.prices.get(clean_sym, 1.0)
        pip_size = self.symbol_manager.specs[clean_sym]["pip_size"]
        spread_pips = 1.2 if "USD" in clean_sym and "XAU" not in clean_sym else 2.5
        
        # Random walk drift (-2 to +2 pips)
        drift = random.choice([-1.5, -0.5, 0.0, 0.5, 1.5]) * pip_size
        self.prices[clean_sym] = round(base + drift, 5 if "EUR" in clean_sym or "GBP" in clean_sym else 2)
        
        bid = self.prices[clean_sym]
        ask = round(bid + (spread_pips * pip_size), 5 if "EUR" in clean_sym or "GBP" in clean_sym else 2)

        return {
            "symbol": clean_sym,
            "bid": bid,
            "ask": ask,
            "spread_pips": spread_pips,
            "time": datetime.now(timezone.utc).isoformat(),
            "source": "SIMULATED_FEED" if not self.mt5.connected else "LIVE_MT5",
        }

    def get_historical_candles(self, symbol: str, timeframe: str = "M15", count: int = 100) -> pd.DataFrame:
        """Pulls historical candles from MT5 or generates realistic technical candles."""
        clean_sym = self.symbol_manager.normalize_symbol(symbol)

        if self.mt5.connected:
            df = self.mt5.get_rates(symbol, timeframe=timeframe, count=count)
            if df is not None and not df.empty:
                return df

        # Generate realistic synthetic OHLCV dataframe
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


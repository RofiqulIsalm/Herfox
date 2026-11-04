"""
Chart Pattern & Candlestick Confirmation Detector
Identifies Double Tops/Bottoms, Quasimodo (QM), Rejection Pinbars, and Engulfing setups.
"""

from typing import List, Dict, Any, Optional
import pandas as pd


class PatternDetector:
    def __init__(self, pip_size: float = 0.0001):
        self.pip_size = pip_size

    def detect_candlestick_triggers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyzes the latest completed candle for high-probability reversal formations.
        """
        if df is None or len(df) < 2:
            return {"pattern": "NONE", "direction": "NEUTRAL"}

        last = df.iloc[-1]
        prev = df.iloc[-2]

        o, h, l, c = last["open"], last["high"], last["low"], last["close"]
        body = abs(c - o)
        total_range = h - l
        if total_range <= 0:
            return {"pattern": "NONE", "direction": "NEUTRAL"}

        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l

        # 1. Bullish Pinbar / Hammer: Lower wick >= 2x body, upper wick small (< 20% range)
        if lower_wick >= (body * 2.0) and upper_wick <= (total_range * 0.25):
            return {
                "pattern": "BULLISH_PINBAR",
                "direction": "BULLISH",
                "wick_ratio": round(lower_wick / (body if body > 0 else 0.0001), 1),
                "rejection_level": float(l),
            }

        # 2. Bearish Pinbar / Shooting Star: Upper wick >= 2x body, lower wick small
        if upper_wick >= (body * 2.0) and lower_wick <= (total_range * 0.25):
            return {
                "pattern": "BEARISH_PINBAR",
                "direction": "BEARISH",
                "wick_ratio": round(upper_wick / (body if body > 0 else 0.0001), 1),
                "rejection_level": float(h),
            }

        # 3. Bullish Engulfing: Previous candle bearish, current candle bullish and completely covers prev body
        if prev["close"] < prev["open"] and c > o and c > prev["open"] and o < prev["close"]:
            return {
                "pattern": "BULLISH_ENGULFING",
                "direction": "BULLISH",
                "rejection_level": float(l),
            }

        # 4. Bearish Engulfing: Previous candle bullish, current candle bearish and completely covers prev body
        if prev["close"] > prev["open"] and c < o and c < prev["close"] and o > prev["open"]:
            return {
                "pattern": "BEARISH_ENGULFING",
                "direction": "BEARISH",
                "rejection_level": float(h),
            }

        return {"pattern": "NONE", "direction": "NEUTRAL"}

    def detect_double_bottom(
        self,
        df: pd.DataFrame,
        tolerance_pips: float = 8.0,
        pip_size: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Detects a Double Bottom (W pattern) in recent price action.
        """
        if df is None or len(df) < 15:
            return None

        active_pip = pip_size or self.pip_size
        lows = df["low"].values
        highs = df["high"].values
        n = len(df)

        # Look for two distinct valleys separated by a peak
        valleys = []
        for i in range(2, n - 2):
            if lows[i] == min(lows[i - 2 : i + 3]):
                valleys.append((i, lows[i]))

        if len(valleys) >= 2:
            idx1, low1 = valleys[-2]
            idx2, low2 = valleys[-1]

            # Check if separation is between 4 and 25 bars
            if 4 <= (idx2 - idx1) <= 25:
                # Check level similarity within tolerance
                if abs(low1 - low2) <= (tolerance_pips * active_pip):
                    # Neckline is the highest point between the two valleys
                    neckline = float(max(highs[idx1:idx2]))
                    current_close = float(df.iloc[-1]["close"])

                    return {
                        "pattern": "DOUBLE_BOTTOM",
                        "direction": "BULLISH",
                        "bottom_level": round(float((low1 + low2) / 2.0), 4 if active_pip == 0.0001 else 2),
                        "neckline": round(neckline, 4 if active_pip == 0.0001 else 2),
                        "broken_neckline": current_close > neckline,
                    }

        return None


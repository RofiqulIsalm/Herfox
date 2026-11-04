"""
Asian Range Liquidity & Judas Swing Sweep Detector
Tracks Asian Session (00:00 - 08:00 GMT) High/Low boundaries
and detects false breakout sweeps (Judas Swings) during London and New York opens.
"""

from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime, time, timezone


class AsianRangeDetector:
    def __init__(self, sweep_buffer_pips: float = 3.0, pip_size: float = 0.0001):
        self.sweep_buffer_pips = sweep_buffer_pips
        self.pip_size = pip_size

    def calculate_asian_range(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extracts the most recent Asian Session (00:00 to 08:00 GMT) High and Low.
        df['time'] must be datetime objects.
        """
        if df is None or len(df) == 0:
            return {}

        df_copy = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df_copy["time"]):
            df_copy["time"] = pd.to_datetime(df_copy["time"])

        # Filter for candles strictly in 00:00 to 08:00 GMT
        asian_candles = df_copy[
            (df_copy["time"].dt.hour >= 0) & (df_copy["time"].dt.hour < 8)
        ]

        if asian_candles.empty:
            # Fallback to recent 24-candle min/max if no GMT matching
            asian_high = float(df["high"].tail(32).max())
            asian_low = float(df["low"].tail(32).min())
            return {
                "asian_high": asian_high,
                "asian_low": asian_low,
                "range_pips": round((asian_high - asian_low) / self.pip_size, 1),
                "is_fallback": True,
            }

        # Take the most recent Asian session block
        latest_date = asian_candles["time"].dt.date.max()
        session_block = asian_candles[asian_candles["time"].dt.date == latest_date]

        asian_high = float(session_block["high"].max())
        asian_low = float(session_block["low"].min())

        return {
            "session_date": str(latest_date),
            "asian_high": asian_high,
            "asian_low": asian_low,
            "range_pips": round((asian_high - asian_low) / self.pip_size, 1),
            "is_fallback": False,
        }

    def detect_liquidity_sweep(
        self,
        df: pd.DataFrame,
        asian_range: Dict[str, Any],
        pip_size: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Detects if price has swept Asian High or Asian Low followed by an immediate reversal.
        """
        if df is None or len(df) == 0 or not asian_range:
            return {"sweep_detected": False, "type": "NONE"}

        active_pip = pip_size or self.pip_size
        asian_high = asian_range.get("asian_high", 0.0)
        asian_low = asian_range.get("asian_low", 0.0)

        # Inspect the last 5 execution candles
        recent = df.tail(5)

        for idx, candle in recent.iterrows():
            low = candle["low"]
            high = candle["high"]
            close = candle["close"]

            # Bullish Judas Sweep: Low penetrates below Asian Low, but candle closes back ABOVE Asian Low
            if low < (asian_low - (self.sweep_buffer_pips * active_pip)) and close > asian_low:
                return {
                    "sweep_detected": True,
                    "type": "BULLISH_ASIAN_SWEEP",
                    "level_swept": asian_low,
                    "sweep_depth_pips": round((asian_low - low) / active_pip, 1),
                    "candle_time": str(candle["time"]),
                    "actionable_signal": "BUY_CONFIRMATION",
                }

            # Bearish Judas Sweep: High penetrates above Asian High, but candle closes back BELOW Asian High
            if high > (asian_high + (self.sweep_buffer_pips * active_pip)) and close < asian_high:
                return {
                    "sweep_detected": True,
                    "type": "BEARISH_ASIAN_SWEEP",
                    "level_swept": asian_high,
                    "sweep_depth_pips": round((high - asian_high) / active_pip, 1),
                    "candle_time": str(candle["time"]),
                    "actionable_signal": "SELL_CONFIRMATION",
                }

        return {"sweep_detected": False, "type": "NONE"}

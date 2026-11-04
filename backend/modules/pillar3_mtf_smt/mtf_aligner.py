"""
Multi-Timeframe (MTF) Trend & Structure Aligner
Analyzes Daily and H4 charts to establish macro market bias (Higher Timeframe Trend)
and prevent counter-trend Lower Timeframe (M15) execution.
"""

from typing import Dict, Any, Optional
import pandas as pd


class MTFAligner:
    def __init__(self, fast_ema: int = 50, slow_ema: int = 200):
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema

    def calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        """Computes exponential moving average."""
        return series.ewm(span=period, adjust=False).mean()

    def analyze_timeframe_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Determines the directional trend of an OHLCV dataframe (H4 or Daily).
        Uses EMA 50 vs EMA 200 + recent price position.
        """
        if df is None or len(df) < 15:
            return {"bias": "NEUTRAL", "reason": "Insufficient candles"}

        closes = df["close"]
        current_close = float(closes.iloc[-1])

        # Calculate EMAs
        ema_fast = self.calculate_ema(closes, min(self.fast_ema, len(df) // 2)).iloc[-1]
        ema_slow = self.calculate_ema(closes, min(self.slow_ema, len(df) - 1)).iloc[-1]

        # Structural higher highs / lower lows check on last 10 candles
        recent_highs = df["high"].tail(10)
        recent_lows = df["low"].tail(10)

        is_bullish_structure = recent_highs.iloc[-1] >= recent_highs.iloc[0] and recent_lows.iloc[-1] >= recent_lows.iloc[0]
        is_bearish_structure = recent_highs.iloc[-1] <= recent_highs.iloc[0] and recent_lows.iloc[-1] <= recent_lows.iloc[0]

        if current_close > ema_fast > ema_slow and is_bullish_structure:
            bias = "BULLISH"
        elif current_close < ema_fast < ema_slow and is_bearish_structure:
            bias = "BEARISH"
        elif current_close > ema_fast:
            bias = "MODERATELY_BULLISH"
        elif current_close < ema_fast:
            bias = "MODERATELY_BEARISH"
        else:
            bias = "NEUTRAL"

        return {
            "bias": bias,
            "current_close": current_close,
            "ema_fast": float(ema_fast),
            "ema_slow": float(ema_slow),
            "structure": "BULLISH_HH_HL" if is_bullish_structure else ("BEARISH_LH_LL" if is_bearish_structure else "RANGING"),
        }

    def evaluate_mtf_alignment(
        self,
        h4_df: Optional[pd.DataFrame] = None,
        daily_df: Optional[pd.DataFrame] = None,
    ) -> Dict[str, Any]:
        """
        Synthesizes H4 and Daily trends into an overarching macro directive for M15.
        """
        h4_res = self.analyze_timeframe_trend(h4_df) if h4_df is not None else {"bias": "NEUTRAL"}
        daily_res = self.analyze_timeframe_trend(daily_df) if daily_df is not None else {"bias": "NEUTRAL"}

        h4_bias = h4_res["bias"]
        daily_bias = daily_res["bias"]

        # Combined consensus
        if "BULLISH" in h4_bias and "BULLISH" in daily_bias:
            macro_trend = "STRONG_BULLISH"
            veto_direction = "VETO_SELL"
        elif "BEARISH" in h4_bias and "BEARISH" in daily_bias:
            macro_trend = "STRONG_BEARISH"
            veto_direction = "VETO_BUY"
        elif "BULLISH" in h4_bias:
            macro_trend = "BULLISH"
            veto_direction = "NONE"
        elif "BEARISH" in h4_bias:
            macro_trend = "BEARISH"
            veto_direction = "NONE"
        else:
            macro_trend = "NEUTRAL"
            veto_direction = "NONE"

        return {
            "macro_trend": macro_trend,
            "h4_bias": h4_bias,
            "daily_bias": daily_bias,
            "veto_direction": veto_direction,
        }


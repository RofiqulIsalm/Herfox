"""
Institutional Order Block (OB) Detector
Identifies the final opposing candle before impulsive market displacement (BOS)
and tracks mitigation status.
"""

from typing import List, Dict, Any, Optional
import pandas as pd


class OrderBlockDetector:
    def __init__(self, displacement_multiplier: float = 1.8, pip_size: float = 0.0001):
        self.displacement_multiplier = displacement_multiplier
        self.pip_size = pip_size

    def detect_order_blocks(self, df: pd.DataFrame, pip_size: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Scans OHLCV DataFrame for institutional Order Blocks.
        df must contain columns: ['time', 'open', 'high', 'low', 'close', 'volume']
        """
        if df is None or len(df) < 2:
            return []

        active_pip_size = pip_size or self.pip_size
        obs: List[Dict[str, Any]] = []
        n = len(df)

        # Calculate average candle body size for displacement reference
        bodies = (df["close"] - df["open"]).abs()
        avg_body = bodies.rolling(window=14, min_periods=3).mean()

        for i in range(0, n - 1):
            prev_candle = df.iloc[i]
            prev_open = prev_candle["open"]
            prev_close = prev_candle["close"]
            prev_high = prev_candle["high"]
            prev_low = prev_candle["low"]
            prev_time = prev_candle["time"]

            raw_ref = avg_body.iloc[i] if not pd.isna(avg_body.iloc[i]) else (prev_high - prev_low)
            ref_body = raw_ref if raw_ref > 0 else (active_pip_size * 5)
            threshold = ref_body * self.displacement_multiplier

            # Subsequent displacement check (next 1-2 candles)
            next_candle_1 = df.iloc[i + 1]
            disp_body_1 = next_candle_1["close"] - next_candle_1["open"]

            # 1. Bullish Order Block: Bearish candle (close < open) followed by strong bullish displacement
            if prev_close < prev_open and disp_body_1 > threshold:
                # Mitigation check: has future price dropped below prev_low?
                mitigated = False
                tested = False
                for j in range(i + 2, n):
                    future_low = df.iloc[j]["low"]
                    if future_low < prev_low:
                        mitigated = True  # Breached / invalidated
                        break
                    elif future_low <= prev_high:
                        tested = True

                obs.append({
                    "type": "BULLISH_OB",
                    "top": float(prev_high),
                    "bottom": float(prev_low),
                    "entry_level": float(prev_high),
                    "sl_level": float(prev_low),
                    "size_pips": round((prev_high - prev_low) / active_pip_size, 1),
                    "time": str(prev_time),
                    "candle_index": i,
                    "tested": tested,
                    "mitigated": mitigated,
                })

            # 2. Bearish Order Block: Bullish candle (close > open) followed by strong bearish displacement
            elif prev_close > prev_open and (-disp_body_1) > threshold:
                mitigated = False
                tested = False
                for j in range(i + 2, n):
                    future_high = df.iloc[j]["high"]
                    if future_high > prev_high:
                        mitigated = True
                        break
                    elif future_high >= prev_low:
                        tested = True

                obs.append({
                    "type": "BEARISH_OB",
                    "top": float(prev_high),
                    "bottom": float(prev_low),
                    "entry_level": float(prev_low),
                    "sl_level": float(prev_high),
                    "size_pips": round((prev_high - prev_low) / active_pip_size, 1),
                    "time": str(prev_time),
                    "candle_index": i,
                    "tested": tested,
                    "mitigated": mitigated,
                })

        return obs

    def get_unmitigated_obs(self, df: pd.DataFrame, pip_size: Optional[float] = None) -> List[Dict[str, Any]]:
        """Filters for active unmitigated Order Blocks."""
        all_obs = self.detect_order_blocks(df, pip_size)
        return [ob for ob in all_obs if not ob["mitigated"]]

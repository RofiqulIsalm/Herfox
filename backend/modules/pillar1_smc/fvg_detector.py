"""
Fair Value Gap (FVG) Detector
Detects institutional 3-candle price imbalances and tracks mitigation status.
"""

from typing import List, Dict, Any, Optional
import pandas as pd


class FVGDetector:
    def __init__(self, min_gap_pips: float = 2.0, pip_size: float = 0.0001):
        self.min_gap_pips = min_gap_pips
        self.pip_size = pip_size

    def detect_fvgs(self, df: pd.DataFrame, pip_size: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Scans OHLCV DataFrame for unmitigated Bullish and Bearish Fair Value Gaps.
        df must contain columns: ['time', 'open', 'high', 'low', 'close', 'volume']
        """
        if df is None or len(df) < 4:
            return []

        active_pip_size = pip_size or self.pip_size
        fvgs: List[Dict[str, Any]] = []
        n = len(df)

        for i in range(2, n):
            c1_high = df.iloc[i - 2]["high"]
            c1_low = df.iloc[i - 2]["low"]
            c3_high = df.iloc[i]["high"]
            c3_low = df.iloc[i]["low"]
            c2_time = df.iloc[i - 1]["time"]

            # 1. Bullish FVG: Gap between Candle 1 High and Candle 3 Low
            if c3_low > c1_high:
                gap_size = c3_low - c1_high
                gap_pips = gap_size / active_pip_size
                if gap_pips >= self.min_gap_pips:
                    # Check subsequent mitigation
                    mitigated = False
                    for j in range(i + 1, n):
                        if df.iloc[j]["low"] <= c1_high:
                            mitigated = True
                            break

                    fvgs.append({
                        "type": "BULLISH_FVG",
                        "top": float(c3_low),
                        "bottom": float(c1_high),
                        "size_pips": round(gap_pips, 1),
                        "time": str(c2_time),
                        "candle_index": i - 1,
                        "mitigated": mitigated,
                    })

            # 2. Bearish FVG: Gap between Candle 1 Low and Candle 3 High
            elif c3_high < c1_low:
                gap_size = c1_low - c3_high
                gap_pips = gap_size / active_pip_size
                if gap_pips >= self.min_gap_pips:
                    # Check subsequent mitigation
                    mitigated = False
                    for j in range(i + 1, n):
                        if df.iloc[j]["high"] >= c1_low:
                            mitigated = True
                            break

                    fvgs.append({
                        "type": "BEARISH_FVG",
                        "top": float(c1_low),
                        "bottom": float(c3_high),
                        "size_pips": round(gap_pips, 1),
                        "time": str(c2_time),
                        "candle_index": i - 1,
                        "mitigated": mitigated,
                    })

        return fvgs

    def get_unmitigated_fvgs(self, df: pd.DataFrame, pip_size: Optional[float] = None) -> List[Dict[str, Any]]:
        """Filters for active unmitigated Fair Value Gaps."""
        all_fvgs = self.detect_fvgs(df, pip_size)
        return [f for f in all_fvgs if not f["mitigated"]]


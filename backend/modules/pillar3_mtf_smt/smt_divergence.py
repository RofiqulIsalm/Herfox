"""
SMT Divergence (Smart Money Tool - Intermarket Correlation) Engine
Compares swing pivots between correlated twins:
1. EURUSD vs GBPUSD
2. XAUUSD (Gold) vs XAGUSD (Silver)
Detects institutional non-confirmation (liquidity traps & major reversal signals).
"""

from typing import Dict, Any, Optional, Tuple
import pandas as pd


class SMTDivergenceEngine:
    CORRELATED_PAIRS = {
        "EURUSD": "GBPUSD",
        "GBPUSD": "EURUSD",
        "XAUUSD": "XAGUSD",
        "XAGUSD": "XAUUSD",
    }

    def __init__(self, lookback_bars: int = 20):
        self.lookback = lookback_bars

    @staticmethod
    def _find_recent_swing_points(df: pd.DataFrame, window: int = 1) -> Tuple[list, list]:
        """Finds swing highs and swing lows across the window."""
        highs = df["high"].values
        lows = df["low"].values
        n = len(df)
        if n < 3:
            return [(i, float(highs[i])) for i in range(n)], [(i, float(lows[i])) for i in range(n)]

        swing_h = []
        swing_l = []

        # Check start boundary
        if highs[0] >= highs[1]:
            swing_h.append((0, float(highs[0])))
        if lows[0] <= lows[1]:
            swing_l.append((0, float(lows[0])))

        for i in range(1, n - 1):
            if highs[i] >= highs[i - 1] and highs[i] >= highs[i + 1]:
                swing_h.append((i, float(highs[i])))
            if lows[i] <= lows[i - 1] and lows[i] <= lows[i + 1]:
                swing_l.append((i, float(lows[i])))

        # Check end boundary
        if highs[n - 1] >= highs[n - 2]:
            swing_h.append((n - 1, float(highs[n - 1])))
        if lows[n - 1] <= lows[n - 2]:
            swing_l.append((n - 1, float(lows[n - 1])))

        return swing_h, swing_l

    def detect_smt(
        self,
        asset_a_name: str,
        df_a: pd.DataFrame,
        asset_b_name: str,
        df_b: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Compares the recent price swings between Asset A and Asset B to spot SMT Divergence.
        """
        if df_a is None or df_b is None or len(df_a) < 3 or len(df_b) < 3:
            return {"smt_detected": False, "type": "NONE"}

        h_a, l_a = self._find_recent_swing_points(df_a.tail(self.lookback))
        h_b, l_b = self._find_recent_swing_points(df_b.tail(self.lookback))

        # 1. Bullish SMT Divergence (One makes Lower Low, twin makes Higher Low)
        if len(l_a) >= 2 and len(l_b) >= 2:
            low1_a, low2_a = l_a[-2][1], l_a[-1][1]
            low1_b, low2_b = l_b[-2][1], l_b[-1][1]

            # Case 1: A made Lower Low, B made Higher Low
            if low2_a < low1_a and low2_b >= low1_b:
                return {
                    "smt_detected": True,
                    "type": "BULLISH_SMT",
                    "leader": asset_b_name,
                    "laggard": asset_a_name,
                    "description": f"{asset_a_name} created a Lower Low, but {asset_b_name} refused and made a Higher Low (Smart Money Accumulation).",
                    "confluence_bonus": 15,
                }
            # Case 2: A made Higher Low, B made Lower Low
            elif low2_a >= low1_a and low2_b < low1_b:
                return {
                    "smt_detected": True,
                    "type": "BULLISH_SMT",
                    "leader": asset_a_name,
                    "laggard": asset_b_name,
                    "description": f"{asset_b_name} created a Lower Low, but {asset_a_name} refused and made a Higher Low (Smart Money Accumulation).",
                    "confluence_bonus": 15,
                }

        # 2. Bearish SMT Divergence (One makes Higher High, twin makes Lower High)
        if len(h_a) >= 2 and len(h_b) >= 2:
            high1_a, high2_a = h_a[-2][1], h_a[-1][1]
            high1_b, high2_b = h_b[-2][1], h_b[-1][1]

            # Case 1: A made Higher High, B made Lower High
            if high2_a > high1_a and high2_b <= high1_b:
                return {
                    "smt_detected": True,
                    "type": "BEARISH_SMT",
                    "leader": asset_b_name,
                    "laggard": asset_a_name,
                    "description": f"{asset_a_name} created a Higher High, but {asset_b_name} failed to confirm (Smart Money Distribution / Bull Trap).",
                    "confluence_bonus": 15,
                }
            # Case 2: A made Lower High, B made Higher High
            elif high2_a <= high1_a and high2_b > high1_b:
                return {
                    "smt_detected": True,
                    "type": "BEARISH_SMT",
                    "leader": asset_a_name,
                    "laggard": asset_b_name,
                    "description": f"{asset_b_name} created a Higher High, but {asset_a_name} failed to confirm (Smart Money Distribution / Bull Trap).",
                    "confluence_bonus": 15,
                }

        return {"smt_detected": False, "type": "NONE"}

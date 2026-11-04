"""
Support & Resistance Level Clustering
Detects major horizontal S/R key levels using swing pivot clustering and touch counts.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd


class SupportResistanceCluster:
    def __init__(self, tolerance_pips: float = 8.0, pip_size: float = 0.0001):
        self.tolerance_pips = tolerance_pips
        self.pip_size = pip_size

    def find_pivots(self, df: pd.DataFrame, window: int = 5) -> Tuple[list, list]:
        """Finds swing highs and swing lows using rolling peak detection."""
        highs = df["high"].values
        lows = df["low"].values
        n = len(df)

        swing_highs = []
        swing_lows = []

        for i in range(window, n - window):
            # Check swing high
            if highs[i] == max(highs[i - window : i + window + 1]):
                swing_highs.append(highs[i])
            # Check swing low
            if lows[i] == min(lows[i - window : i + window + 1]):
                swing_lows.append(lows[i])

        return swing_highs, swing_lows

    def cluster_levels(
        self,
        df: pd.DataFrame,
        window: int = 5,
        min_touches: int = 2,
        pip_size: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Clusters swing pivots into distinct Support and Resistance zones.
        """
        if df is None or len(df) < window * 2:
            return []

        active_pip = pip_size or self.pip_size
        highs = df["high"].values
        lows = df["low"].values
        n = len(df)
        pivots = []

        for i in range(window, n - window):
            if highs[i] == max(highs[i - window : i + window + 1]):
                pivots.append(highs[i])
            if lows[i] == min(lows[i - window : i + window + 1]):
                pivots.append(lows[i])

        if not pivots:
            return []

        tolerance = self.tolerance_pips * active_pip
        pivots = sorted(pivots)
        clusters: List[List[float]] = []

        current_cluster = [pivots[0]]
        for p in pivots[1:]:
            if p - current_cluster[-1] <= tolerance:
                current_cluster.append(p)
            else:
                clusters.append(current_cluster)
                current_cluster = [p]
        clusters.append(current_cluster)

        current_price = float(df.iloc[-1]["close"])
        results = []

        for c in clusters:
            if len(c) >= min_touches:
                avg_level = float(np.mean(c))
                level_type = "RESISTANCE" if avg_level > current_price else "SUPPORT"
                results.append({
                    "price_level": round(avg_level, 4 if active_pip == 0.0001 else 2),
                    "type": level_type,
                    "touch_count": len(c),
                    "distance_pips": round(abs(avg_level - current_price) / active_pip, 1),
                })

        # Sort by proximity to current price
        results.sort(key=lambda x: x["distance_pips"])
        return results

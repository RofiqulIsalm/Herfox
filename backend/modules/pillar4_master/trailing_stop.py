"""
Adaptive Trailing Stop Engine
Manages Tranche 3 (Runner) dynamically using M15 ATR volatility bands
and institutional swing market structure points.
Strict Rule: Trailing stops ratchet strictly forward in profit and never loosen.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from backend.modules.pillar4_master.order_manager import TradePackage


class AdaptiveTrailingStop:
    def __init__(self, atr_multiplier: float = 1.5):
        self.atr_multiplier = atr_multiplier
        self.peak_favorable_prices: Dict[str, float] = {}

    def update_trailing_stop(
        self,
        package: TradePackage,
        current_price: float,
        atr_value: Optional[float] = None,
        recent_swing_level: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluates current price and adjusts Stop Loss forward if new favorable level reached.
        Operates only on ACTIVE Tranche 3 (Runner).
        """
        t3 = package.tranches.get("T3")
        if not t3 or t3.status != "ACTIVE":
            return None

        is_buy = package.direction == "BUY"
        pkg_id = package.package_id

        # Update peak favorable price
        if pkg_id not in self.peak_favorable_prices:
            self.peak_favorable_prices[pkg_id] = current_price
        else:
            if is_buy and current_price > self.peak_favorable_prices[pkg_id]:
                self.peak_favorable_prices[pkg_id] = current_price
            elif (not is_buy) and current_price < self.peak_favorable_prices[pkg_id]:
                self.peak_favorable_prices[pkg_id] = current_price

        peak_price = self.peak_favorable_prices[pkg_id]
        current_sl = package.active_sl
        candidate_sl = current_sl

        # 1. ATR-based candidate stop
        if atr_value and atr_value > 0:
            trail_distance = atr_value * self.atr_multiplier
            if is_buy:
                atr_sl = peak_price - trail_distance
                candidate_sl = max(candidate_sl, atr_sl)
            else:
                atr_sl = peak_price + trail_distance
                candidate_sl = min(candidate_sl, atr_sl) if candidate_sl != 0 else atr_sl

        # 2. Structural Swing candidate stop (recent higher low or lower high)
        if recent_swing_level and recent_swing_level > 0:
            if is_buy and recent_swing_level > candidate_sl:
                candidate_sl = recent_swing_level
            elif (not is_buy) and (candidate_sl == 0 or recent_swing_level < candidate_sl):
                candidate_sl = recent_swing_level

        # Ratchet check: Stop must move in direction of profit
        stop_improved = False
        if is_buy and candidate_sl > current_sl:
            stop_improved = True
        elif (not is_buy) and (current_sl == 0 or candidate_sl < current_sl):
            stop_improved = True

        if stop_improved:
            old_sl = current_sl
            package.active_sl = round(candidate_sl, 5)
            t3.sl_price = round(candidate_sl, 5)
            now_str = datetime.now(timezone.utc).isoformat()
            package.events_log.append(f"Trailing stop ratcheted: {old_sl} -> {package.active_sl}")

            return {
                "event": "TRAILING_STOP_UPDATED",
                "package_id": pkg_id,
                "old_sl": old_sl,
                "new_sl": package.active_sl,
                "peak_price": peak_price,
                "timestamp": now_str,
            }

        return None


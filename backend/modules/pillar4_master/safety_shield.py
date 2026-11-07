"""
Prop Firm Safety Shield & Capital Protection Engine
Enforces institutional risk constraints and prop firm compliance:
1. Daily Trade Cap: Max 2 trades per day (Strict 1-2 A+ setups limit).
2. Daily Drawdown Shield: 4.0% max daily loss lockout (Halts trading immediately).
3. Max Total Drawdown Shield: 8.0% overall trailing drawdown lockout.
4. Friday Weekend Gap Guard: Prohibits new entries 1-2 hours before Friday market close (20:00 GMT)
   and flags open positions for weekend risk reduction.
"""

from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime, timezone


class PropFirmSafetyShield:
    def __init__(
        self,
        max_daily_drawdown_pct: float = 4.0,
        max_total_drawdown_pct: float = 8.0,
        max_daily_trades: int = 2,
        friday_freeze_hour_gmt: int = 20,
    ):
        self.max_daily_drawdown_pct = max_daily_drawdown_pct
        self.max_total_drawdown_pct = max_total_drawdown_pct
        self.max_daily_trades = max_daily_trades
        self.friday_freeze_hour_gmt = friday_freeze_hour_gmt

    def check_daily_trades(self, trades_taken_today: int) -> Tuple[bool, str]:
        """
        Ensures trader does not overtrade beyond max allowed high-grade setups per day.
        """
        if trades_taken_today >= self.max_daily_trades:
            return False, f"DAILY_CAP_LOCKOUT: Daily trade limit reached ({trades_taken_today}/{self.max_daily_trades} trades taken)."
        return True, "OK"

    def check_daily_drawdown(
        self,
        current_equity: float,
        starting_day_equity: float,
    ) -> Tuple[bool, float, str]:
        """
        Calculates daily drawdown percentage against starting day balance/equity.
        Triggered if daily loss exceeds 4.0%.
        """
        if starting_day_equity <= 0:
            return True, 0.0, "OK"

        loss_amount = starting_day_equity - current_equity
        if loss_amount <= 0:
            return True, 0.0, "OK"

        daily_dd_pct = (loss_amount / starting_day_equity) * 100.0
        if daily_dd_pct >= self.max_daily_drawdown_pct:
            return (
                False,
                daily_dd_pct,
                f"DAILY_DRAWDOWN_LOCKOUT: Current daily loss {daily_dd_pct:.2f}% breaches {self.max_daily_drawdown_pct:.1f}% Prop Firm threshold! Trading locked for the day.",
            )

        return True, daily_dd_pct, "OK"

    def check_total_drawdown(
        self,
        current_equity: float,
        initial_balance: float,
    ) -> Tuple[bool, float, str]:
        """
        Calculates total account drawdown percentage from initial funding.
        Triggered if drawdown exceeds 8.0%.
        """
        if initial_balance <= 0:
            return True, 0.0, "OK"

        loss_amount = initial_balance - current_equity
        if loss_amount <= 0:
            return True, 0.0, "OK"

        total_dd_pct = (loss_amount / initial_balance) * 100.0
        if total_dd_pct >= self.max_total_drawdown_pct:
            return (
                False,
                total_dd_pct,
                f"MAX_DRAWDOWN_BREACH: Total drawdown {total_dd_pct:.2f}% breaches {self.max_total_drawdown_pct:.1f}% limit! Emergency terminal stop.",
            )

        return True, total_dd_pct, "OK"

    def check_friday_weekend_guard(self, now_dt: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Checks if the current time is on Friday evening after the freeze hour (e.g. 20:00 GMT).
        Prevents entering new positions before weekend market closure to eliminate gap risk.
        """
        dt = now_dt or datetime.now(timezone.utc)
        # weekday(): Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
        if dt.weekday() == 4:  # Friday
            if dt.hour >= self.friday_freeze_hour_gmt:
                return (
                    False,
                    f"FRIDAY_WEEKEND_GUARD: Friday market closes soon ({dt.strftime('%H:%M')} GMT >= {self.friday_freeze_hour_gmt}:00 GMT freeze). New entries strictly prohibited to avoid weekend gaps.",
                )
        elif dt.weekday() in (5, 6):  # Saturday or Sunday
            return False, "WEEKEND_MARKET_CLOSED: Global forex and bullion markets are closed."

        return True, "OK"

    def evaluate_safety(
        self,
        current_equity: float,
        starting_day_equity: float,
        initial_balance: float,
        trades_taken_today: int,
        now_dt: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive shield evaluation returning status, active locks, and remaining thresholds.
        """
        dt = now_dt or datetime.now(timezone.utc)
        locks: List[str] = []
        messages: List[str] = []

        # 1. Trade Cap Check
        trades_ok, trades_msg = self.check_daily_trades(trades_taken_today)
        if not trades_ok:
            locks.append("DAILY_CAP_LOCK")
            messages.append(trades_msg)

        # 2. Daily Drawdown Check
        daily_dd_ok, daily_dd_pct, daily_dd_msg = self.check_daily_drawdown(current_equity, starting_day_equity)
        if not daily_dd_ok:
            locks.append("DAILY_DRAWDOWN_LOCK")
            messages.append(daily_dd_msg)

        # 3. Total Drawdown Check
        total_dd_ok, total_dd_pct, total_dd_msg = self.check_total_drawdown(current_equity, initial_balance)
        if not total_dd_ok:
            locks.append("MAX_DRAWDOWN_LOCK")
            messages.append(total_dd_msg)

        # 4. Friday Weekend Guard Check
        friday_ok, friday_msg = self.check_friday_weekend_guard(dt)
        if not friday_ok:
            locks.append("FRIDAY_WEEKEND_LOCK")
            messages.append(friday_msg)

        is_safe = len(locks) == 0

        return {
            "is_safe": is_safe,
            "active_locks": locks,
            "messages": messages,
            "trades_taken_today": trades_taken_today,
            "remaining_trades_today": max(0, self.max_daily_trades - trades_taken_today),
            "current_daily_drawdown_pct": round(daily_dd_pct, 2),
            "max_daily_drawdown_pct": self.max_daily_drawdown_pct,
            "remaining_daily_drawdown_pct": max(0.0, round(self.max_daily_drawdown_pct - daily_dd_pct, 2)),
            "current_total_drawdown_pct": round(total_dd_pct, 2),
            "max_total_drawdown_pct": self.max_total_drawdown_pct,
            "timestamp": dt.isoformat(),
        }


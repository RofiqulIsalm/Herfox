"""
Pillar 4 Order Manager & 3-Tranche Scaling Execution Engine
Manages multi-tranche position lifecycle:
- Tranche 1: TP1 (1.0R / 1.5R) - Locks immediate gain
- Tranche 2: TP2 (2.5R) - Captures extended swing
- Tranche 3: Runner (Open Target) - Trails with adaptive ATR/Swing stop
- Automated Break-Even: Upon TP1 hit, SL for Tranches 2 & 3 is moved to Entry + 1 pip spread buffer.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import uuid

from backend.bridge.symbol_manager import SymbolManager


@dataclass
class TrancheOrder:
    order_id: str
    tranche_name: str  # "TRANCHE_1_TP1", "TRANCHE_2_TP2", "TRANCHE_3_RUNNER"
    symbol: str
    direction: str     # "BUY" or "SELL"
    lots: float
    entry_price: float
    sl_price: float
    tp_price: Optional[float]
    status: str        # "ACTIVE", "CLOSED_TP", "CLOSED_SL", "CLOSED_TRAIL", "CLOSED_BE"
    open_time: str
    close_time: Optional[str] = None
    close_price: Optional[float] = None
    realized_pnl_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TradePackage:
    package_id: str
    symbol: str
    direction: str
    entry_price: float
    initial_sl: float
    r_distance_pips: float
    tp1_price: float
    tp2_price: float
    pip_size: float
    tranches: Dict[str, TrancheOrder]
    break_even_active: bool = False
    active_sl: float = 0.0
    status: str = "ACTIVE"  # "ACTIVE", "PARTIAL", "CLOSED"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    events_log: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "package_id": self.package_id,
            "symbol": self.symbol,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "initial_sl": self.initial_sl,
            "active_sl": self.active_sl,
            "r_distance_pips": self.r_distance_pips,
            "tp1_price": self.tp1_price,
            "tp2_price": self.tp2_price,
            "break_even_active": self.break_even_active,
            "status": self.status,
            "created_at": self.created_at,
            "tranches": {k: v.to_dict() for k, v in self.tranches.items()},
            "events_log": self.events_log,
        }


class OrderManager:
    def __init__(self, symbol_manager: Optional[SymbolManager] = None):
        self.symbol_manager = symbol_manager or SymbolManager()

    def create_trade_package(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        sl_price: float,
        account_balance: float = 10000.0,
        risk_percent: float = 1.0,
        tp1_rr: float = 1.0,
        tp2_rr: float = 2.5,
    ) -> TradePackage:
        """
        Creates an institutional 3-Tranche Trade Package with exact lot allocations and target levels.
        """
        clean_sym = self.symbol_manager.normalize_symbol(symbol)
        spec = self.symbol_manager.specs.get(clean_sym, self.symbol_manager.DEFAULT_SPECS["EURUSD"])
        pip_size = spec["pip_size"]

        # Calculate exact lot sizing and 3-tranche split
        lot_calc = self.symbol_manager.calculate_lot_size(
            symbol=clean_sym,
            account_balance=account_balance,
            risk_percent=risk_percent,
            entry_price=entry_price,
            sl_price=sl_price,
        )

        tranches_lots = lot_calc["tranches"]
        r_distance = abs(entry_price - sl_price)
        r_pips = r_distance / pip_size

        # Compute Take Profit Targets based on R-Multiples
        if direction.upper() == "BUY":
            tp1_price = round(entry_price + (r_distance * tp1_rr), spec["digits"])
            tp2_price = round(entry_price + (r_distance * tp2_rr), spec["digits"])
        else:
            tp1_price = round(entry_price - (r_distance * tp1_rr), spec["digits"])
            tp2_price = round(entry_price - (r_distance * tp2_rr), spec["digits"])

        package_id = f"PKG-{clean_sym}-{uuid.uuid4().hex[:8].upper()}"
        now_str = datetime.now(timezone.utc).isoformat()

        # Build 3 individual sub-orders
        t1 = TrancheOrder(
            order_id=f"{package_id}-T1",
            tranche_name="TRANCHE_1_TP1",
            symbol=clean_sym,
            direction=direction.upper(),
            lots=tranches_lots["tranche_1_tp1"],
            entry_price=entry_price,
            sl_price=sl_price,
            tp_price=tp1_price,
            status="ACTIVE",
            open_time=now_str,
        )

        t2 = TrancheOrder(
            order_id=f"{package_id}-T2",
            tranche_name="TRANCHE_2_TP2",
            symbol=clean_sym,
            direction=direction.upper(),
            lots=tranches_lots["tranche_2_tp2"],
            entry_price=entry_price,
            sl_price=sl_price,
            tp_price=tp2_price,
            status="ACTIVE",
            open_time=now_str,
        )

        t3 = TrancheOrder(
            order_id=f"{package_id}-T3",
            tranche_name="TRANCHE_3_RUNNER",
            symbol=clean_sym,
            direction=direction.upper(),
            lots=tranches_lots["tranche_3_runner"],
            entry_price=entry_price,
            sl_price=sl_price,
            tp_price=None,  # Open runner
            status="ACTIVE",
            open_time=now_str,
        )

        package = TradePackage(
            package_id=package_id,
            symbol=clean_sym,
            direction=direction.upper(),
            entry_price=entry_price,
            initial_sl=sl_price,
            active_sl=sl_price,
            r_distance_pips=round(r_pips, 1),
            tp1_price=tp1_price,
            tp2_price=tp2_price,
            pip_size=pip_size,
            tranches={"T1": t1, "T2": t2, "T3": t3},
            break_even_active=False,
            status="ACTIVE",
            events_log=[f"Order package initialized: 3 Tranches totaling {lot_calc['total_lot']} lots."],
        )

        return package

    def evaluate_price_tick(
        self,
        package: TradePackage,
        current_price: float,
        be_buffer_pips: float = 1.0,
    ) -> List[Dict[str, Any]]:
        """
        Evaluates a new price tick against the package's tranches.
        Applies automated Break-Even logic upon TP1 hit and executes SL/TP closures.
        Returns triggered events.
        """
        events: List[Dict[str, Any]] = []
        is_buy = package.direction == "BUY"
        pip_size = package.pip_size
        now_str = datetime.now(timezone.utc).isoformat()
        spec = self.symbol_manager.specs.get(package.symbol, self.symbol_manager.DEFAULT_SPECS["EURUSD"])
        pip_val = spec["pip_value_per_lot"]

        # Check Stop Loss first for active tranches
        sl_breached = (current_price <= package.active_sl) if is_buy else (current_price >= package.active_sl)
        if sl_breached:
            for tid, tranche in package.tranches.items():
                if tranche.status == "ACTIVE":
                    tranche.status = "CLOSED_BE" if package.break_even_active else "CLOSED_SL"
                    tranche.close_time = now_str
                    tranche.close_price = current_price
                    diff_pips = (current_price - tranche.entry_price) / pip_size if is_buy else (tranche.entry_price - current_price) / pip_size
                    tranche.realized_pnl_usd = round(diff_pips * pip_val * tranche.lots, 2)
                    events.append({
                        "event": "TRANCHE_SL_CLOSED",
                        "tranche": tid,
                        "status": tranche.status,
                        "close_price": current_price,
                        "pnl_usd": tranche.realized_pnl_usd,
                    })

            package.status = "CLOSED"
            package.events_log.append(f"Position closed at SL / BE level: {current_price}")
            return events

        # Check Tranche 1 (TP1)
        t1 = package.tranches.get("T1")
        if t1 and t1.status == "ACTIVE":
            tp1_hit = (current_price >= package.tp1_price) if is_buy else (current_price <= package.tp1_price)
            if tp1_hit:
                t1.status = "CLOSED_TP"
                t1.close_time = now_str
                t1.close_price = package.tp1_price
                diff_pips = (package.tp1_price - t1.entry_price) / pip_size if is_buy else (t1.entry_price - package.tp1_price) / pip_size
                t1.realized_pnl_usd = round(diff_pips * pip_val * t1.lots, 2)

                events.append({
                    "event": "TP1_HIT",
                    "tranche": "T1",
                    "close_price": package.tp1_price,
                    "pnl_usd": t1.realized_pnl_usd,
                })
                package.events_log.append(f"TP1 reached at {package.tp1_price}. Tranche 1 locked +${t1.realized_pnl_usd}.")

                # TRIGGER AUTOMATED BREAK-EVEN FOR TRANCHES 2 & 3
                buffer_dist = be_buffer_pips * pip_size
                be_price = round(package.entry_price + buffer_dist if is_buy else package.entry_price - buffer_dist, spec["digits"])
                package.active_sl = be_price
                package.break_even_active = True

                for tid in ["T2", "T3"]:
                    if package.tranches[tid].status == "ACTIVE":
                        package.tranches[tid].sl_price = be_price

                events.append({
                    "event": "BREAK_EVEN_ACTIVATED",
                    "new_sl": be_price,
                    "buffer_pips": be_buffer_pips,
                    "description": f"Risk eliminated! SL moved to {be_price} (Entry + {be_buffer_pips} pip spread buffer).",
                })
                package.events_log.append(f"Auto Break-Even moved SL to {be_price}.")

        # Check Tranche 2 (TP2)
        t2 = package.tranches.get("T2")
        if t2 and t2.status == "ACTIVE":
            tp2_hit = (current_price >= package.tp2_price) if is_buy else (current_price <= package.tp2_price)
            if tp2_hit:
                t2.status = "CLOSED_TP"
                t2.close_time = now_str
                t2.close_price = package.tp2_price
                diff_pips = (package.tp2_price - t2.entry_price) / pip_size if is_buy else (t2.entry_price - package.tp2_price) / pip_size
                t2.realized_pnl_usd = round(diff_pips * pip_val * t2.lots, 2)

                events.append({
                    "event": "TP2_HIT",
                    "tranche": "T2",
                    "close_price": package.tp2_price,
                    "pnl_usd": t2.realized_pnl_usd,
                })
                package.events_log.append(f"TP2 reached at {package.tp2_price}. Tranche 2 locked +${t2.realized_pnl_usd}.")

        # Check overall package status
        active_count = sum(1 for t in package.tranches.values() if t.status == "ACTIVE")
        if active_count == 0:
            package.status = "CLOSED"
        elif active_count < 3:
            package.status = "PARTIAL"

        return events


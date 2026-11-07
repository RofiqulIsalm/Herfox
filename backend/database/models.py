"""
Database models and dataclasses for terminal.db (SQLite).
Represents trade orders, signal telemetry vectors, and RSI evolution cycles.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import json


@dataclass
class TradeOrderModel:
    ticket_id: str
    package_id: str
    symbol: str
    direction: str
    tranche_number: int  # 1 (TP1), 2 (TP2), 3 (Runner)
    lot_size: float
    entry_price: float
    sl_price: float
    tp_price: Optional[float]
    open_time: str
    close_price: Optional[float] = None
    pnl_dollars: Optional[float] = None
    pnl_pips: Optional[float] = None
    close_time: Optional[str] = None
    exit_reason: Optional[str] = None  # TP1, TP2, BE, TRAIL, SL, MANUAL

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConfluenceTelemetryModel:
    signal_id: str
    timestamp: str
    symbol: str
    timeframe: str
    macro_score: float
    smc_score: float
    pattern_score: float
    mtf_bias: str
    smt_divergence: int  # 1 for True, 0 for False
    confluence_total: float
    trade_grade: str  # GRADE_A_PLUS, GRADE_A, GRADE_B_OR_LOWER
    outcome: str = "PENDING"  # PENDING, PROFIT, LOSS, BREAK_EVEN, VETOED
    reasons_json: str = "[]"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def reasons_list(self) -> list:
        try:
            return json.loads(self.reasons_json)
        except Exception:
            return []


@dataclass
class RSIEvolutionModel:
    cycle_id: str
    timestamp: str
    symbol: str
    previous_win_rate: float
    new_win_rate: float
    max_drawdown: float
    mutation_details: str
    promoted: int = 0  # 1 for Promoted to Champion, 0 for Discarded

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


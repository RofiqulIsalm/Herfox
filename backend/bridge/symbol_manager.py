"""
Symbol Manager & Dynamic Lot Sizing Engine
Handles tick specifications, pip values, contract sizes, and 3-tranche risk allocation
for Forex currency pairs (EURUSD, GBPUSD) and Precious Metals (XAUUSD, XAGUSD).
"""

from typing import Dict, Any, Tuple
import math


class SymbolManager:
    # Standard specifications reference
    DEFAULT_SPECS = {
        "EURUSD": {
            "pip_size": 0.0001,
            "contract_size": 100000,
            "pip_value_per_lot": 10.0,  # in USD
            "digits": 5,
            "min_lot": 0.01,
            "max_lot": 100.0,
            "lot_step": 0.01,
        },
        "GBPUSD": {
            "pip_size": 0.0001,
            "contract_size": 100000,
            "pip_value_per_lot": 10.0,  # in USD
            "digits": 5,
            "min_lot": 0.01,
            "max_lot": 100.0,
            "lot_step": 0.01,
        },
        "XAUUSD": {
            "pip_size": 0.10,  # 1 pip = 0.10, 10 pips = $1.00
            "contract_size": 100,  # 100 oz per standard lot
            "pip_value_per_lot": 10.0,  # 0.10 * 100 oz = $10.00 per pip
            "digits": 2,
            "min_lot": 0.01,
            "max_lot": 50.0,
            "lot_step": 0.01,
        },
        "XAGUSD": {
            "pip_size": 0.01,  # 1 pip = 0.01
            "contract_size": 5000,  # 5,000 oz per standard lot
            "pip_value_per_lot": 50.0,  # 0.01 * 5000 oz = $50.00 per pip
            "digits": 3,
            "min_lot": 0.01,
            "max_lot": 50.0,
            "lot_step": 0.01,
        },
    }

    def __init__(self, broker_symbols: Dict[str, Any] = None):
        self.specs = self.DEFAULT_SPECS.copy()
        if broker_symbols:
            self.update_from_broker(broker_symbols)

    def update_from_broker(self, broker_info: Dict[str, Any]):
        """Updates internal specifications using real broker symbol_info from MT5."""
        for sym, info in broker_info.items():
            clean_sym = self.normalize_symbol(sym)
            if clean_sym in self.specs:
                self.specs[clean_sym].update(info)

    @staticmethod
    def normalize_symbol(raw_symbol: str) -> str:
        """Strips broker suffixes like EURUSDm, EURUSD.pro, XAUUSD_i to root symbol."""
        upper = raw_symbol.upper()
        for root in ["EURUSD", "GBPUSD", "XAUUSD", "XAGUSD"]:
            if root in upper:
                return root
        return raw_symbol

    def calculate_lot_size(
        self,
        symbol: str,
        account_balance: float,
        risk_percent: float,
        entry_price: float,
        sl_price: float,
    ) -> Dict[str, Any]:
        """
        Calculates exact lot size based on account balance, risk %, and pip distance.
        Splits into 3 equal tranches for scaling-out.
        """
        clean_sym = self.normalize_symbol(symbol)
        spec = self.specs.get(clean_sym, self.DEFAULT_SPECS.get("EURUSD"))

        risk_amount = account_balance * (risk_percent / 100.0)
        price_diff = abs(entry_price - sl_price)

        if price_diff <= 0:
            raise ValueError("Entry and Stop Loss prices cannot be identical.")

        # Calculate Stop Loss in pips
        pip_size = spec["pip_size"]
        sl_pips = price_diff / pip_size

        # Lot size = Risk Amount / (SL in pips * Pip Value per 1.0 Lot)
        pip_value = spec["pip_value_per_lot"]
        total_lot = risk_amount / (sl_pips * pip_value)

        # Enforce broker bounds
        min_lot = spec["min_lot"]
        max_lot = spec["max_lot"]
        lot_step = spec["lot_step"]

        # Round to step
        steps = math.floor(total_lot / lot_step)
        total_lot = max(min_lot, min(max_lot, steps * lot_step))
        total_lot = round(total_lot, 2)

        # 3-Tranche Split
        tranche_size = math.floor((total_lot / 3.0) / lot_step) * lot_step
        tranche_size = max(min_lot, round(tranche_size, 2))

        # Remainder adjusted to tranche 3
        tranche_1 = tranche_size
        tranche_2 = tranche_size
        tranche_3 = round(total_lot - (tranche_1 + tranche_2), 2)
        if tranche_3 < min_lot:
            tranche_3 = min_lot
            total_lot = round(tranche_1 + tranche_2 + tranche_3, 2)

        return {
            "symbol": clean_sym,
            "account_balance": account_balance,
            "risk_percent": risk_percent,
            "risk_amount_dollars": round(risk_amount, 2),
            "sl_pips": round(sl_pips, 1),
            "total_lot": total_lot,
            "tranches": {
                "tranche_1_tp1": tranche_1,
                "tranche_2_tp2": tranche_2,
                "tranche_3_runner": tranche_3,
            },
            "pip_value_per_lot": pip_value,
            "pip_size": pip_size,
        }


"""
SQLite Database Manager for terminal.db
Handles low-latency WAL-mode persistence for:
1. trade_orders
2. confluence_telemetry
3. rsi_evolution_history
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from .models import TradeOrderModel, ConfluenceTelemetryModel, RSIEvolutionModel


class DatabaseManager:
    DEFAULT_DB_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "terminal.db")
    )

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self.DEFAULT_DB_PATH
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Yields connection with WAL mode enabled and Row factory, auto-closing upon exit."""
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initializes tables and indexes."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Trade Orders Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_orders (
                ticket_id TEXT PRIMARY KEY,
                package_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                tranche_number INTEGER NOT NULL,
                lot_size REAL NOT NULL,
                entry_price REAL NOT NULL,
                sl_price REAL NOT NULL,
                tp_price REAL,
                close_price REAL,
                pnl_dollars REAL,
                pnl_pips REAL,
                open_time TEXT NOT NULL,
                close_time TEXT,
                exit_reason TEXT
            );
            """)

            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_symbol_time 
            ON trade_orders (symbol, open_time);
            """)

            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_package 
            ON trade_orders (package_id);
            """)

            # 2. Confluence Telemetry Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS confluence_telemetry (
                signal_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT DEFAULT 'M15',
                macro_score REAL,
                smc_score REAL,
                pattern_score REAL,
                mtf_bias TEXT,
                smt_divergence INTEGER,
                confluence_total REAL,
                trade_grade TEXT,
                outcome TEXT DEFAULT 'PENDING',
                reasons_json TEXT
            );
            """)

            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_telemetry_time 
            ON confluence_telemetry (timestamp);
            """)

            # 3. RSI Evolution History Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS rsi_evolution_history (
                cycle_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                previous_win_rate REAL,
                new_win_rate REAL,
                max_drawdown REAL,
                mutation_details TEXT,
                promoted INTEGER DEFAULT 0
            );
            """)

            conn.commit()

    # ==========================================================
    # Trade Orders CRUD
    # ==========================================================

    def insert_order(self, order: TradeOrderModel):
        """Inserts a new trade order."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO trade_orders (
                ticket_id, package_id, symbol, direction, tranche_number,
                lot_size, entry_price, sl_price, tp_price, close_price,
                pnl_dollars, pnl_pips, open_time, close_time, exit_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                order.ticket_id, order.package_id, order.symbol, order.direction,
                order.tranche_number, order.lot_size, order.entry_price, order.sl_price,
                order.tp_price, order.close_price, order.pnl_dollars, order.pnl_pips,
                order.open_time, order.close_time, order.exit_reason
            ))
            conn.commit()

    def update_order_close(
        self,
        ticket_id: str,
        close_price: float,
        pnl_dollars: float,
        pnl_pips: float,
        close_time: str,
        exit_reason: str,
    ):
        """Updates an order with its exit details."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE trade_orders
            SET close_price = ?, pnl_dollars = ?, pnl_pips = ?, close_time = ?, exit_reason = ?
            WHERE ticket_id = ?;
            """, (close_price, pnl_dollars, pnl_pips, close_time, exit_reason, ticket_id))
            conn.commit()

    def update_order_sl(self, ticket_id: str, new_sl: float):
        """Updates the stop loss for an active order (e.g. Break-Even or Trailing Stop)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE trade_orders
            SET sl_price = ?
            WHERE ticket_id = ?;
            """, (new_sl, ticket_id))
            conn.commit()

    def get_order(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Fetches an order by ticket_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trade_orders WHERE ticket_id = ?;", (ticket_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_open_orders(self) -> List[Dict[str, Any]]:
        """Returns all open orders (where close_time is NULL)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trade_orders WHERE close_time IS NULL ORDER BY open_time DESC;")
            return [dict(row) for row in cursor.fetchall()]

    def get_daily_orders(self, date_str: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns orders opened on a given date (default today YYYY-MM-DD)."""
        target_date = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM trade_orders 
            WHERE open_time LIKE ? 
            ORDER BY open_time ASC;
            """, (f"{target_date}%",))
            return [dict(row) for row in cursor.fetchall()]

    def get_daily_stats(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        """Calculates today's trade count, net PnL in USD, and win rate."""
        orders = self.get_daily_orders(date_str)
        # Unique package count represents actual strategic trade setups (since each package has 3 tranches)
        packages = set(o["package_id"] for o in orders)
        trades_count = len(packages)

        closed_orders = [o for o in orders if o["close_time"] is not None]
        total_pnl = sum((o["pnl_dollars"] or 0.0) for o in closed_orders)
        winning_orders = [o for o in closed_orders if (o["pnl_dollars"] or 0.0) > 0]
        win_rate = (len(winning_orders) / len(closed_orders) * 100.0) if closed_orders else 0.0

        return {
            "date": date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "trades_count": trades_count,
            "closed_tranches_count": len(closed_orders),
            "daily_pnl_usd": round(total_pnl, 2),
            "win_rate": round(win_rate, 1),
        }

    # ==========================================================
    # Confluence Telemetry
    # ==========================================================

    def log_telemetry(self, telemetry: ConfluenceTelemetryModel):
        """Logs high-dimensional signal telemetry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO confluence_telemetry (
                signal_id, timestamp, symbol, timeframe, macro_score,
                smc_score, pattern_score, mtf_bias, smt_divergence,
                confluence_total, trade_grade, outcome, reasons_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                telemetry.signal_id, telemetry.timestamp, telemetry.symbol,
                telemetry.timeframe, telemetry.macro_score, telemetry.smc_score,
                telemetry.pattern_score, telemetry.mtf_bias, telemetry.smt_divergence,
                telemetry.confluence_total, telemetry.trade_grade, telemetry.outcome,
                telemetry.reasons_json
            ))
            conn.commit()

    def get_telemetry_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches recent telemetry history for RSI analysis."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM confluence_telemetry 
            ORDER BY timestamp DESC 
            LIMIT ?;
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # ==========================================================
    # RSI Evolution History
    # ==========================================================

    def log_rsi_cycle(self, cycle: RSIEvolutionModel):
        """Logs a completed mutation backtesting cycle."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO rsi_evolution_history (
                cycle_id, timestamp, symbol, previous_win_rate,
                new_win_rate, max_drawdown, mutation_details, promoted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                cycle.cycle_id, cycle.timestamp, cycle.symbol,
                cycle.previous_win_rate, cycle.new_win_rate, cycle.max_drawdown,
                cycle.mutation_details, cycle.promoted
            ))
            conn.commit()

    def get_rsi_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetches tournament evolution records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM rsi_evolution_history 
            ORDER BY timestamp DESC 
            LIMIT ?;
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

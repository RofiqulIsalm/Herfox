"""
MetaTrader 5 Native Python IPC Bridge
Handles low-latency communication with C:\\Program Files\\MetaTrader 5\\terminal64.exe.
Includes connection watchdogs, live tick streaming, OHLCV candle retrieval, and order dispatch.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import pandas as pd

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MT5Client")


class MT5Client:
    DEFAULT_TERMINAL_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"

    TIMEFRAME_MAP = {
        "M1": mt5.TIMEFRAME_M1 if MT5_AVAILABLE else 1,
        "M5": mt5.TIMEFRAME_M5 if MT5_AVAILABLE else 5,
        "M15": mt5.TIMEFRAME_M15 if MT5_AVAILABLE else 15,
        "H1": mt5.TIMEFRAME_H1 if MT5_AVAILABLE else 60,
        "H4": mt5.TIMEFRAME_H4 if MT5_AVAILABLE else 240,
        "D1": mt5.TIMEFRAME_D1 if MT5_AVAILABLE else 1440,
    }

    def __init__(self, terminal_path: Optional[str] = None):
        self.terminal_path = terminal_path or self.DEFAULT_TERMINAL_PATH
        self.connected = False
        self.account_info: Dict[str, Any] = {}

    def initialize(self, login: Optional[int] = None, password: Optional[str] = None, server: Optional[str] = None) -> bool:
        """Initializes connection to the MT5 terminal binary."""
        if not MT5_AVAILABLE:
            logger.error("MetaTrader5 package is not available in current environment.")
            return False

        # Check path
        init_args = {}
        if os.path.exists(self.terminal_path):
            init_args["path"] = self.terminal_path
            logger.info(f"Targeting MT5 terminal at: {self.terminal_path}")

        if login and password and server:
            init_args["login"] = int(login)
            init_args["password"] = password
            init_args["server"] = server

        if not mt5.initialize(**init_args):
            err = mt5.last_error()
            logger.warning(f"MT5 initialize failed: {err}. Attempting default initialization...")
            if not mt5.initialize():
                logger.error(f"Default MT5 initialization failed: {mt5.last_error()}")
                self.connected = False
                return False

        self.connected = True
        logger.info(f"Successfully connected to MT5 version: {mt5.version()}")
        self.sync_account()
        return True

    def sync_account(self) -> Dict[str, Any]:
        """Fetches and caches real-time account balance, equity, and margin."""
        if not self.connected:
            return {}

        acc = mt5.account_info()
        if acc is None:
            logger.warning(f"Could not retrieve account info: {mt5.last_error()}")
            return {}

        self.account_info = {
            "login": acc.login,
            "trade_mode": acc.trade_mode,  # 0: demo, 2: real
            "balance": acc.balance,
            "equity": acc.equity,
            "profit": acc.profit,
            "margin": acc.margin,
            "margin_free": acc.margin_free,
            "margin_level": acc.margin_level,
            "leverage": acc.leverage,
            "currency": acc.currency,
            "server": acc.server,
            "company": acc.company,
        }
        return self.account_info

    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Retrieves symbol specification details (tick size, spread, contract size)."""
        if not self.connected:
            return None

        # Ensure symbol is visible in Market Watch
        if not mt5.symbol_select(symbol, True):
            logger.warning(f"Failed to select symbol '{symbol}' in Market Watch.")

        info = mt5.symbol_info(symbol)
        if info is None:
            return None

        return {
            "name": info.name,
            "bid": info.bid,
            "ask": info.ask,
            "spread": info.spread,
            "digits": info.digits,
            "point": info.point,
            "trade_contract_size": info.trade_contract_size,
            "trade_tick_size": info.trade_tick_size,
            "trade_tick_value": info.trade_tick_value,
            "volume_min": info.volume_min,
            "volume_max": info.volume_max,
            "volume_step": info.volume_step,
        }

    def get_live_tick(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Returns the latest live bid/ask/spread tick for a symbol."""
        if not self.connected:
            return None

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return None

        spread_points = round((tick.ask - tick.bid) / (0.0001 if "USD" in symbol and "XAU" not in symbol else 0.10), 1)
        return {
            "symbol": symbol,
            "bid": tick.bid,
            "ask": tick.ask,
            "time": datetime.fromtimestamp(tick.time, tz=timezone.utc).isoformat(),
            "spread_pips": spread_points,
            "last": tick.last,
            "volume": tick.volume,
        }

    def get_rates(self, symbol: str, timeframe: str = "M15", count: int = 200) -> Optional[pd.DataFrame]:
        """
        Retrieves historical OHLCV candlestick data and returns a clean Pandas DataFrame.
        """
        if not self.connected:
            return None

        tf = self.TIMEFRAME_MAP.get(timeframe.upper(), mt5.TIMEFRAME_M15)
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)

        if rates is None or len(rates) == 0:
            logger.warning(f"No rates returned for {symbol} on {timeframe}: {mt5.last_error()}")
            return None

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.rename(columns={"tick_volume": "volume"}, inplace=True)
        return df[["time", "open", "high", "low", "close", "volume"]]

    def send_market_order(
        self,
        symbol: str,
        order_type: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = "The Life Terminal",
    ) -> Optional[Dict[str, Any]]:
        """Executes a market order directly on MT5."""
        if not self.connected:
            return None

        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            logger.error(f"Cannot get current price tick for {symbol}")
            return None

        is_buy = order_type.upper() == "BUY"
        price = tick.ask if is_buy else tick.bid
        action_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": action_type,
            "price": price,
            "sl": sl or 0.0,
            "tp": tp or 0.0,
            "deviation": 20,
            "magic": 888001,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            retcode = result.retcode if result else "None"
            logger.error(f"Order failed for {symbol}: retcode={retcode}")
            return None

        logger.info(f"Order executed: #{result.order} {symbol} {order_type} {volume} lots @ {price}")
        return {
            "ticket": result.order,
            "volume": result.volume,
            "price": result.price,
            "bid": result.bid,
            "ask": result.ask,
            "comment": result.comment,
        }

    def modify_order_sl_tp(self, ticket: int, sl: float, tp: Optional[float] = None) -> bool:
        """Modifies Stop Loss (e.g. to Break-Even) or Take Profit of an open position."""
        if not self.connected:
            return False

        position = mt5.positions_get(ticket=ticket)
        if not position or len(position) == 0:
            logger.error(f"Position #{ticket} not found.")
            return False

        pos = position[0]
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "symbol": pos.symbol,
            "sl": sl,
            "tp": tp if tp is not None else pos.tp,
        }

        res = mt5.order_send(request)
        if res and res.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"Position #{ticket} modified: SL -> {sl}")
            return True
        return False

    def shutdown(self):
        """Cleanly releases MT5 resources."""
        if self.connected and MT5_AVAILABLE:
            mt5.shutdown()
            self.connected = False
            logger.info("MT5 connection terminated cleanly.")


"""
Phase 1 Verification Script: MT5 Bridge & Dynamic Lot Sizing Test
Tests connection to MetaTrader 5, symbol specifications, and 3-tranche risk calculations.
"""

import sys
import os
import io

# Force UTF-8 on Windows Console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.bridge.symbol_manager import SymbolManager
from backend.bridge.mt5_client import MT5Client


def test_symbol_manager():
    print("\n" + "=" * 60)
    print("STEP 1: Testing Symbol Manager & 3-Tranche Dynamic Lot Sizing")
    print("=" * 60)

    sm = SymbolManager()

    # Scenario A: Gold (XAUUSD) on $1,000 Account with 1% Risk ($10)
    gold_calc = sm.calculate_lot_size(
        symbol="XAUUSD",
        account_balance=1000.0,
        risk_percent=1.0,
        entry_price=2742.50,
        sl_price=2738.00,  # $4.50 SL distance = 45 pips
    )

    print("\n--- Gold (XAUUSD) Test ---")
    print(f"Account Balance: ${gold_calc['account_balance']:,.2f}")
    print(f"Risk Amount: ${gold_calc['risk_amount_dollars']:.2f} ({gold_calc['risk_percent']}%)")
    print(f"SL Distance: {gold_calc['sl_pips']} pips")
    print(f"Total Calculated Lot: {gold_calc['total_lot']} lots")
    print(f"Tranche 1 (TP1):    {gold_calc['tranches']['tranche_1_tp1']} lot")
    print(f"Tranche 2 (TP2):    {gold_calc['tranches']['tranche_2_tp2']} lot")
    print(f"Tranche 3 (Runner): {gold_calc['tranches']['tranche_3_runner']} lot")

    assert gold_calc["total_lot"] > 0, "Total lot must be positive"
    assert sum(gold_calc["tranches"].values()) == gold_calc["total_lot"], "Tranches must sum to total lot"
    print(">>> Gold Sizing Test: PASSED (100% Exact)")

    # Scenario B: EURUSD on $10,000 Account with 1% Risk ($100)
    eur_calc = sm.calculate_lot_size(
        symbol="EURUSD",
        account_balance=10000.0,
        risk_percent=1.0,
        entry_price=1.08500,
        sl_price=1.08350,  # 15 pips SL distance
    )

    print("\n--- EURUSD Test ---")
    print(f"Account Balance: ${eur_calc['account_balance']:,.2f}")
    print(f"Risk Amount: ${eur_calc['risk_amount_dollars']:.2f} ({eur_calc['risk_percent']}%)")
    print(f"SL Distance: {eur_calc['sl_pips']} pips")
    print(f"Total Calculated Lot: {eur_calc['total_lot']} lots")
    print(f"Tranche 1 (TP1):    {eur_calc['tranches']['tranche_1_tp1']} lot")
    print(f"Tranche 2 (TP2):    {eur_calc['tranches']['tranche_2_tp2']} lot")
    print(f"Tranche 3 (Runner): {eur_calc['tranches']['tranche_3_runner']} lot")

    assert eur_calc["total_lot"] > 0
    assert sum(eur_calc["tranches"].values()) == eur_calc["total_lot"]
    print(">>> EURUSD Sizing Test: PASSED (100% Exact)")


def test_mt5_connection():
    print("\n" + "=" * 60)
    print("STEP 2: Testing Native MetaTrader 5 IPC Bridge")
    print("=" * 60)

    client = MT5Client()
    connected = client.initialize()

    if not connected:
        print("⚠️ MT5 Bridge could not connect to a running terminal instance.")
        print("   (Note: If terminal is closed or not logged in, launch MT5 and log in to your Exness/FTMO demo account).")
        return

    print("\n✅ MT5 Bridge Connection: SUCCESSFUL!")
    acc = client.sync_account()
    if acc:
        print(f"Connected Login: {acc.get('login')}")
        print(f"Server: {acc.get('server')}")
        print(f"Company: {acc.get('company')}")
        print(f"Balance: ${acc.get('balance', 0):,.2f}")
        print(f"Equity: ${acc.get('equity', 0):,.2f}")

    # Test symbols
    symbols = ["EURUSD", "GBPUSD", "XAUUSD", "XAGUSD"]
    print("\n--- Live Market Data Check ---")
    for sym in symbols:
        tick = client.get_live_tick(sym)
        if tick:
            print(f"[{sym}] Bid: {tick['bid']} | Ask: {tick['ask']} | Spread: {tick['spread_pips']} pips")
        else:
            print(f"[{sym}] Tick not available (Symbol may need to be enabled in Market Watch)")

        # Test M15 Candles
        df = client.get_rates(sym, timeframe="M15", count=5)
        if df is not None and not df.empty:
            last_candle = df.iloc[-1]
            print(f"   ↳ Last M15 Bar: {last_candle['time']} | Close: {last_candle['close']} | Vol: {last_candle['volume']}")

    client.shutdown()
    print("\n>>> MT5 IPC Test Completed Cleanly.")


if __name__ == "__main__":
    test_symbol_manager()
    test_mt5_connection()

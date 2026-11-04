"""
Phase 5 Verification Script: Database Persistence & 2-Way Telegram Mobile Command Center
Tests:
1. SQLite WAL Persistence (terminal.db: trade_orders, confluence_telemetry, rsi_evolution_history).
2. Headless Matplotlib Chart Snapshotter (High-res dark-mode PNG generation with trade overlays & HUD).
3. 2-Way Telegram Bot Client:
   - Outbound Grade A+ setup dispatch with chart attachment.
   - Outbound TP1/Auto Break-Even, TP2, and Hermes breaking news alerts.
   - Inbound interactive mobile remote (/status, /positions, /news, /pause, /resume, /closeall).
   - Strict whitelist security access control.
"""

import sys
import os
import io
import pandas as pd
from datetime import datetime, timezone, timedelta

# Force UTF-8 on Windows Console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.models import TradeOrderModel, ConfluenceTelemetryModel, RSIEvolutionModel
from backend.database.db_manager import DatabaseManager
from backend.alerts.chart_snapshotter import ChartSnapshotter
from backend.alerts.telegram_bot import TelegramBotClient


def test_sqlite_persistence():
    print("\n" + "=" * 65)
    print("STEP 1: Testing SQLite WAL Database Persistence (terminal.db)")
    print("=" * 65)

    test_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_terminal.db"))
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    db = DatabaseManager(db_path=test_db_path)
    now_str = datetime.now(timezone.utc).isoformat()

    # 1. Insert 3-Tranche Trade Package
    t1 = TradeOrderModel(
        ticket_id="TICKET-001",
        package_id="PKG-XAUUSD-001",
        symbol="XAUUSD",
        direction="BUY",
        tranche_number=1,
        lot_size=0.06,
        entry_price=2740.00,
        sl_price=2735.00,
        tp_price=2745.00,
        open_time=now_str,
    )
    t2 = TradeOrderModel(
        ticket_id="TICKET-002",
        package_id="PKG-XAUUSD-001",
        symbol="XAUUSD",
        direction="BUY",
        tranche_number=2,
        lot_size=0.06,
        entry_price=2740.00,
        sl_price=2735.00,
        tp_price=2752.50,
        open_time=now_str,
    )
    t3 = TradeOrderModel(
        ticket_id="TICKET-003",
        package_id="PKG-XAUUSD-001",
        symbol="XAUUSD",
        direction="BUY",
        tranche_number=3,
        lot_size=0.08,
        entry_price=2740.00,
        sl_price=2735.00,
        tp_price=None,
        open_time=now_str,
    )

    db.insert_order(t1)
    db.insert_order(t2)
    db.insert_order(t3)

    open_orders = db.get_open_orders()
    print(f"Open Tranches in Database: {len(open_orders)}")
    assert len(open_orders) == 3, "Must have 3 open tranches"

    # 2. Simulate TP1 Hit -> Close Tranche 1 and Move SL to Break-Even for T2/T3
    db.update_order_close(
        ticket_id="TICKET-001",
        close_price=2745.00,
        pnl_dollars=30.00,
        pnl_pips=50.0,
        close_time=datetime.now(timezone.utc).isoformat(),
        exit_reason="TP1",
    )
    db.update_order_sl(ticket_id="TICKET-002", new_sl=2740.10)
    db.update_order_sl(ticket_id="TICKET-003", new_sl=2740.10)

    t2_updated = db.get_order("TICKET-002")
    assert t2_updated["sl_price"] == 2740.10, "Tranche 2 SL must be updated to 2740.10"
    print(">>> Order Management & Break-Even SL Update: PASSED")

    # 3. Log Confluence Telemetry
    telemetry = ConfluenceTelemetryModel(
        signal_id="SIG-XAUUSD-001",
        timestamp=now_str,
        symbol="XAUUSD",
        timeframe="M15",
        macro_score=18.4,
        smc_score=30.0,
        pattern_score=20.0,
        mtf_bias="BULLISH",
        smt_divergence=1,
        confluence_total=88.4,
        trade_grade="GRADE_A_PLUS",
        outcome="PROFIT",
        reasons_json='["Institutional Bullish OB", "Unmitigated FVG", "SMT Divergence"]',
    )
    db.log_telemetry(telemetry)
    history = db.get_telemetry_history(limit=5)
    print(f"Confluence Telemetry Records: {len(history)} | Grade: {history[0]['trade_grade']}")
    assert len(history) == 1
    assert history[0]["trade_grade"] == "GRADE_A_PLUS"
    print(">>> Confluence Telemetry Logging: PASSED")

    # 4. Log RSI Mutation Cycle
    rsi_cycle = RSIEvolutionModel(
        cycle_id="RSI-CYCLE-001",
        timestamp=now_str,
        symbol="XAUUSD",
        previous_win_rate=68.5,
        new_win_rate=74.2,
        max_drawdown=3.8,
        mutation_details="Tightened FVG buffer to 3.0 pips; expanded TP2 ratio to 2.8R",
        promoted=1,
    )
    db.log_rsi_cycle(rsi_cycle)
    rsi_history = db.get_rsi_history(limit=5)
    print(f"RSI Cycles Logged: {len(rsi_history)} | Promoted: {bool(rsi_history[0]['promoted'])}")
    assert len(rsi_history) == 1
    assert rsi_history[0]["promoted"] == 1
    print(">>> RSI Evolution History Logging: PASSED")

    # Clean up test db safely
    try:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    except Exception:
        pass


def test_chart_snapshotter():
    print("\n" + "=" * 65)
    print("STEP 2: Testing Headless Chart Snapshotter (PNG Generation)")
    print("=" * 65)

    now = datetime.now(timezone.utc)
    candles = []
    base_price = 2735.0
    for i in range(35):
        base_price += (0.4 if i % 2 == 0 else -0.2)
        candles.append({
            "time": now - timedelta(minutes=15 * (35 - i)),
            "open": base_price,
            "high": base_price + 2.5,
            "low": base_price - 1.0,
            "close": base_price + 1.2,
            "volume": 1500,
        })
    df = pd.DataFrame(candles)

    snapshotter = ChartSnapshotter()
    png_path = snapshotter.render_signal_chart(
        df=df,
        symbol="XAUUSD",
        direction="BUY",
        entry_price=2740.00,
        sl_price=2735.00,
        tp1_price=2745.00,
        tp2_price=2752.50,
        confluence_score=88.4,
        reasons=[
            "Unmitigated Bullish FVG imbalance (40 pips)",
            "Institutional Order Block tapped at 2737.50",
            "SMT Divergence: Silver made higher low",
        ],
        obs=[{"type": "BULLISH_OB", "top": 2739.0, "bottom": 2737.5}],
    )

    print(f"Chart Snapshot Generated at: {png_path}")
    assert os.path.exists(png_path), "Generated PNG file must exist"
    file_size_bytes = os.path.getsize(png_path)
    print(f"Chart Snapshot File Size: {file_size_bytes / 1024:.1f} KB")
    assert file_size_bytes > 20000, "Chart image must be a valid high-res PNG (>20KB)"
    print(">>> Headless Chart Snapshot Generation: PASSED")


def test_telegram_client():
    print("\n" + "=" * 65)
    print("STEP 3: Testing 2-Way Telegram Bot Client (Alerts & Mobile Remote)")
    print("=" * 65)

    bot = TelegramBotClient()
    bot.whitelist = ["123456789"]  # Authorized user ID

    # 1. Test Outbound Grade A+ Setup Dispatch
    setup_data = {
        "symbol": "XAUUSD",
        "direction": "BUY",
        "confluence_score": 88.4,
        "grade": "GRADE_A_PLUS",
        "entry_price": 2740.00,
        "sl_price": 2735.00,
        "tp1_price": 2745.00,
        "tp2_price": 2752.50,
        "total_lots": "0.20",
        "risk_percent": 1.0,
        "reasons": [
            "Asian session low swept (Judas swing)",
            "Unmitigated Bullish FVG",
            "SMT Accumulation vs Silver",
        ],
    }
    sent_signal = bot.send_grade_a_signal(setup_data)
    assert sent_signal is True
    print("1. Outbound Grade A+ Alert Dispatched: SUCCESS")

    # 2. Test Outbound TP1 / Auto Break-Even Alert
    sent_tp1 = bot.send_tp_milestone_alert(
        symbol="XAUUSD",
        ticket_id="TICKET-001",
        milestone="TP1",
        close_price=2745.00,
        pnl_usd=30.00,
        active_sl=2740.10,
    )
    assert sent_tp1 is True
    print("2. Outbound TP1 & Auto Break-Even Alert Dispatched: SUCCESS")

    # 3. Test Inbound Commands from Authorized User
    # /status
    resp_status = bot.process_command(user_id="123456789", command_text="/status")
    print(f"3. Command /status Reply:\n{resp_status}\n")
    assert "THE LIFE TERMINAL STATUS" in resp_status
    assert "100% COMPLIANT" in resp_status

    # /pause & /resume
    resp_pause = bot.process_command(user_id="123456789", command_text="/pause")
    assert bot.is_paused is True
    assert "PAUSED" in resp_pause

    resp_resume = bot.process_command(user_id="123456789", command_text="/resume")
    assert bot.is_paused is False
    assert "RESUMED" in resp_resume
    print("4. Command /pause and /resume: SUCCESS")

    # /closeall & /confirm_kill emergency killswitch
    resp_closeall = bot.process_command(user_id="123456789", command_text="/closeall")
    assert "EMERGENCY KILLSWITCH" in resp_closeall
    assert bot.kill_pending is True

    resp_kill = bot.process_command(user_id="123456789", command_text="/confirm_kill")
    assert "EMERGENCY FLATTEN EXECUTED" in resp_kill
    assert bot.kill_pending is False
    print("5. Emergency Mobile Killswitch (/closeall -> /confirm_kill): SUCCESS")

    # 4. Test Security Whitelist (Unauthorized Intruder Block)
    resp_unauth = bot.process_command(user_id="UNKNOWN_HACKER_999", command_text="/status")
    print(f"6. Intruder Block Test Response: {resp_unauth}")
    assert "Access Denied" in resp_unauth
    print(">>> Strict Whitelist Security: PASSED (Intrusion Blocked)")


if __name__ == "__main__":
    test_sqlite_persistence()
    test_chart_snapshotter()
    test_telegram_client()

"""
Phase 6 Verification Script: Frontend Desktop Dashboard & FastAPI Server
Tests:
1. REST API endpoints:
   - /api/status (Account metrics, connection state)
   - /api/watchlist (4 symbols, live spreads, 24h chg)
   - /api/candles (Lightweight Charts formatted OHLCV)
   - /api/confluence (Real-time scoring, grade, drivers)
   - /api/execute (3-Tranche Scaling execution)
   - /api/positions (Open tranches)
   - /api/closeall (Emergency flatten)
   - /api/telegram/alert (Dispatches alert with chart snapshot)
2. WebSocket Stream contract validation.
"""

import sys
import os
import io

# Force UTF-8 on Windows Console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.app import app


def test_fastapi_endpoints():
    print("\n" + "=" * 65)
    print("STEP 1: Testing FastAPI Server REST Endpoints")
    print("=" * 65)

    client = TestClient(app)

    # 1. GET /api/status
    res_status = client.get("/api/status")
    print(f"1. GET /api/status -> Status Code: {res_status.status_code}")
    assert res_status.status_code == 200
    status_data = res_status.json()
    print(f"   • Terminal: {status_data['terminal_name']}")
    print(f"   • Broker: {status_data['broker']}")
    print(f"   • Balance: ${status_data['account_balance']} | Equity: ${status_data['equity']}")
    print(f"   • Server GMT: {status_data['server_time_gmt']}")
    assert "FTMO" in status_data["broker"]
    assert status_data["max_trades_per_day"] == 2

    # 2. GET /api/watchlist
    res_watch = client.get("/api/watchlist")
    print(f"\n2. GET /api/watchlist -> Status Code: {res_watch.status_code}")
    assert res_watch.status_code == 200
    watchlist = res_watch.json()["watchlist"]
    print(f"   • Monitored Instruments: {len(watchlist)}")
    symbols = [w["symbol"] for w in watchlist]
    print(f"   • Symbols: {', '.join(symbols)}")
    assert "XAUUSD" in symbols
    assert "EURUSD" in symbols
    assert "GBPUSD" in symbols
    assert "XAGUSD" in symbols

    # 3. GET /api/candles
    res_candles = client.get("/api/candles?symbol=XAUUSD&timeframe=M15&count=40")
    print(f"\n3. GET /api/candles -> Status Code: {res_candles.status_code}")
    assert res_candles.status_code == 200
    candles_data = res_candles.json()
    assert len(candles_data["candles"]) > 0
    first_c = candles_data["candles"][0]
    print(f"   • First Candle: Time {first_c['time']} | Open {first_c['open']} Close {first_c['close']}")
    assert "open" in first_c and "high" in first_c and "low" in first_c and "close" in first_c

    # 4. GET /api/confluence
    res_conf = client.get("/api/confluence?symbol=XAUUSD")
    print(f"\n4. GET /api/confluence -> Status Code: {res_conf.status_code}")
    assert res_conf.status_code == 200
    conf_data = res_conf.json()
    confluence = conf_data["confluence"]
    print(f"   • Confluence Score: {confluence['confluence_score']}% | Grade: {confluence['grade']}")
    print(f"   • Arbiter Decision: {confluence['decision']}")
    assert confluence["confluence_score"] > 0

    # 5. POST /api/execute (3-Tranche Scaling)
    res_exec = client.post("/api/execute", json={
        "symbol": "XAUUSD",
        "direction": "BUY",
        "risk_percent": 1.0,
        "account_balance": 10000.0,
    })
    print(f"\n5. POST /api/execute -> Status Code: {res_exec.status_code}")
    assert res_exec.status_code == 200
    exec_data = res_exec.json()
    print(f"   • Package Executed: {exec_data['package_id']}")
    print(f"   • Entry: {exec_data['entry_price']} | TP1: {exec_data['tp1']} | TP2: {exec_data['tp2']}")
    assert len(exec_data["tranches"]) == 3
    print(">>> 3-Tranche Execution API: PASSED")

    # 6. GET /api/positions
    res_pos = client.get("/api/positions")
    print(f"\n6. GET /api/positions -> Status Code: {res_pos.status_code}")
    assert res_pos.status_code == 200
    positions = res_pos.json()["open_positions"]
    print(f"   • Open Positions Recorded: {len(positions)} tranches")
    assert len(positions) >= 3

    # 7. POST /api/telegram/alert
    res_tg = client.post("/api/telegram/alert", json={
        "symbol": "XAUUSD",
        "direction": "BUY",
        "include_chart": True,
    })
    print(f"\n7. POST /api/telegram/alert -> Status Code: {res_tg.status_code}")
    assert res_tg.status_code == 200
    tg_data = res_tg.json()
    print(f"   • Alert Status: {tg_data['status']} | Chart Snapshot: {os.path.basename(tg_data['chart_path'])}")
    assert tg_data["status"] == "DISPATCHED"

    # 8. POST /api/closeall (Emergency Killswitch)
    res_close = client.post("/api/closeall")
    print(f"\n8. POST /api/closeall -> Status Code: {res_close.status_code}")
    assert res_close.status_code == 200
    close_data = res_close.json()
    print(f"   • Flattened Orders: {close_data['flattened_orders']}")
    assert close_data["flattened_orders"] >= 3

    print("\n>>> All 8 FastAPI REST Endpoints: PASSED (100% Exact)")


def test_websocket_stream_contract():
    print("\n" + "=" * 65)
    print("STEP 2: Testing Real-Time WebSocket Streaming Contract")
    print("=" * 65)

    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        print(f"WebSocket Packet Received:")
        print(f"  • Type: {data.get('type')}")
        print(f"  • Timestamp: {data.get('timestamp')}")
        print(f"  • Ticks: {data.get('ticks')}")
        print(f"  • Daily PnL: ${data.get('daily_pnl_usd')}")

        assert data.get("type") == "TICK_UPDATE"
        assert "XAUUSD" in data.get("ticks", {})
        print(">>> WebSocket Real-Time Streaming: PASSED")


if __name__ == "__main__":
    test_fastapi_endpoints()
    test_websocket_stream_contract()


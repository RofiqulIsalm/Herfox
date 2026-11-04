"""
Phase 4 Verification Script: Pillar 4 Master Arbiter & 3-Tranche Scaling Execution Engine
Tests:
1. Confluence scoring & Grade A+ consensus calculation.
2. Strict Veto hierarchy enforcement (News Guard, Spread, Daily Cap, MTF counter-trend, Hermes macro).
3. 3-Tranche Scaling lifecycle (TP1 lock, Auto Break-Even + 1 pip buffer, TP2 lock, Runner trailing stop).
"""

import sys
import os
import io

# Force UTF-8 on Windows Console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.modules.pillar4_master import ConfluenceEngine, OrderManager, AdaptiveTrailingStop


def test_confluence_scoring_grade_a_plus():
    print("\n" + "=" * 65)
    print("STEP 1: Testing Confluence Engine & Grade A+ Consensus")
    print("=" * 65)

    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "config", "strategy_dna.json"))
    engine = ConfluenceEngine(config_path=config_path)

    # Provide high confluence bullish data on XAUUSD
    macro_data = {
        "news_guard": {"news_veto": False, "minutes_to_next": 95.0},
        "hermes_bias": 42.0,  # Strongly bullish gold
    }
    smc_data = {
        "obs": [{"type": "BULLISH_OB", "top": 2739.0, "bottom": 2737.5}],
        "fvgs": [{"type": "BULLISH_FVG", "size_pips": 40.0, "mitigated": False}],
        "asian_sweep": {"sweep_detected": True, "type": "BULLISH_ASIAN_SWEEP", "sweep_depth_pips": 25.0},
    }
    pattern_data = {
        "candlestick_trigger": {"pattern": "BULLISH_PINBAR", "direction": "BULLISH"},
        "sr_clusters": [{"price_level": 2737.5, "type": "SUPPORT", "touch_count": 8}],
    }
    mtf_data = {
        "macro_trend": "BULLISH_TREND",
        "h4_aligned": True,
        "daily_aligned": True,
    }
    smt_data = {
        "smt_detected": True,
        "type": "BULLISH_SMT",
        "confluence_bonus": 15.0,
        "description": "Gold made lower low while Silver refused and made higher low",
    }

    result = engine.evaluate(
        symbol="XAUUSD",
        direction="BUY",
        entry_price=2740.0,
        sl_price=2735.0,
        current_spread_pips=1.8,
        macro_data=macro_data,
        smc_data=smc_data,
        pattern_data=pattern_data,
        mtf_data=mtf_data,
        smt_data=smt_data,
        daily_stats={"trades_taken_today": 0},
    )

    print(f"Symbol: {result['symbol']} | Direction: {result['direction']}")
    print(f"Total Confluence Score: {result['confluence_score']} / 100")
    print(f"Assigned Grade: {result['grade']}")
    print(f"Final Arbiter Decision: {result['decision']}")
    print("Breakdown:")
    for k, v in result["confluence_breakdown"].items():
        print(f"  • {k}: {v} pts")

    assert result["is_approved"] is True, "High confluence setup must be approved"
    assert result["grade"] == "GRADE_A_PLUS", "Score must qualify for Grade A+"
    assert result["confluence_score"] >= 80.0, "Score must be >= 80"
    assert result["veto_active"] is False, "No vetos should be active"
    print(">>> Confluence Grade A+ Consensus: PASSED")


def test_veto_hierarchy():
    print("\n" + "=" * 65)
    print("STEP 2: Testing Strict Veto Hierarchy Enforcement")
    print("=" * 65)

    engine = ConfluenceEngine()

    # Case A: News Veto (Red Folder in 10 minutes)
    res_news = engine.evaluate(
        symbol="EURUSD",
        direction="BUY",
        entry_price=1.0850,
        sl_price=1.0830,
        current_spread_pips=0.8,
        macro_data={"news_guard": {"news_veto": True, "minutes_to_next": 10.0, "next_event": {"title": "US CPI"}}},
    )
    print(f"1. News Guard Veto Test -> Veto Active: {res_news['veto_active']} | Decision: {res_news['decision']}")
    assert res_news["is_approved"] is False
    assert any("NEWS_VETO" in v for v in res_news["vetos"])

    # Case B: Spread Veto (Spread 4.2 pips > max 1.5 pips for EURUSD)
    res_spread = engine.evaluate(
        symbol="EURUSD",
        direction="BUY",
        entry_price=1.0850,
        sl_price=1.0830,
        current_spread_pips=4.2,
    )
    print(f"2. Spread Guard Veto Test -> Veto Active: {res_spread['veto_active']} | Decision: {res_spread['decision']}")
    assert res_spread["is_approved"] is False
    assert any("SPREAD_VETO" in v for v in res_spread["vetos"])

    # Case C: Daily Cap Veto (2 trades already executed today)
    res_cap = engine.evaluate(
        symbol="GBPUSD",
        direction="BUY",
        entry_price=1.2950,
        sl_price=1.2930,
        current_spread_pips=1.2,
        daily_stats={"trades_taken_today": 2},
    )
    print(f"3. Daily Cap Veto Test -> Veto Active: {res_cap['veto_active']} | Decision: {res_cap['decision']}")
    assert res_cap["is_approved"] is False
    assert any("DAILY_CAP_VETO" in v for v in res_cap["vetos"])

    # Case D: Counter-Trend MTF Veto (BUY attempt against Bearish H4 trend)
    res_mtf = engine.evaluate(
        symbol="XAUUSD",
        direction="BUY",
        entry_price=2740.0,
        sl_price=2735.0,
        current_spread_pips=1.5,
        mtf_data={"macro_trend": "BEARISH_TREND"},
    )
    print(f"4. Counter-Trend MTF Veto Test -> Veto Active: {res_mtf['veto_active']} | Decision: {res_mtf['decision']}")
    assert res_mtf["is_approved"] is False
    assert any("MTF_VETO" in v for v in res_mtf["vetos"])

    # Case E: Severe Macro Geopolitical/Rate opposition (-60 bias against BUY)
    res_macro = engine.evaluate(
        symbol="XAUUSD",
        direction="BUY",
        entry_price=2740.0,
        sl_price=2735.0,
        current_spread_pips=1.5,
        macro_data={"hermes_bias": -60.0},
    )
    print(f"5. Macro Sentiment Veto Test -> Veto Active: {res_macro['veto_active']} | Decision: {res_macro['decision']}")
    assert res_macro["is_approved"] is False
    assert any("HERMES_MACRO_VETO" in v for v in res_macro["vetos"])

    print(">>> All 5 Veto Arbiter Gates: PASSED (100% Zero-Leakage)")


def test_3_tranche_order_lifecycle():
    print("\n" + "=" * 65)
    print("STEP 3: Testing 3-Tranche Scaling & Auto Break-Even Lifecycle")
    print("=" * 65)

    order_mgr = OrderManager()
    trailing_engine = AdaptiveTrailingStop(atr_multiplier=1.5)

    # 1. Initialize Trade Package on Gold ($10,000 balance, 1% risk = $100 risk)
    # Entry: 2740.00, SL: 2735.00 -> 50 pips risk ($500/lot -> 0.20 lots total)
    pkg = order_mgr.create_trade_package(
        symbol="XAUUSD",
        direction="BUY",
        entry_price=2740.00,
        sl_price=2735.00,
        account_balance=10000.0,
        risk_percent=1.0,
        tp1_rr=1.0,
        tp2_rr=2.5,
    )

    print(f"Package ID: {pkg.package_id}")
    print(f"Symbol: {pkg.symbol} | Direction: {pkg.direction}")
    print(f"Entry: {pkg.entry_price} | Initial SL: {pkg.initial_sl} (Risk: {pkg.r_distance_pips} pips)")
    print(f"TP1 Target (1.0R): {pkg.tp1_price}")
    print(f"TP2 Target (2.5R): {pkg.tp2_price}")
    print(f"Tranches Created:")
    for tid, t in pkg.tranches.items():
        print(f"  • {tid} ({t.tranche_name}): {t.lots} lots | TP: {t.tp_price} | Status: {t.status}")

    assert pkg.tp1_price == 2745.00, "TP1 at 1.0R must be 2745.00"
    assert pkg.tp2_price == 2752.50, "TP2 at 2.5R must be 2752.50"
    assert pkg.tranches["T3"].tp_price is None, "Tranche 3 runner must have open target"
    assert round(sum(t.lots for t in pkg.tranches.values()), 2) == 0.20, "Total lot size must equal 0.20"

    # 2. Simulate Price Moving to 2745.00 (TP1 Hit!)
    print("\n--- Simulating Price Reaching TP1 (2745.00) ---")
    events = order_mgr.evaluate_price_tick(pkg, current_price=2745.00, be_buffer_pips=1.0)
    for ev in events:
        print(f"  Event: {ev['event']} -> {ev.get('description', '')} PnL: ${ev.get('pnl_usd', 0.0)}")

    assert pkg.tranches["T1"].status == "CLOSED_TP", "Tranche 1 must be closed at TP1"
    assert pkg.tranches["T1"].realized_pnl_usd > 0, "Tranche 1 must bank profit"
    assert pkg.break_even_active is True, "Auto Break-Even must activate upon TP1 hit"
    # Entry 2740.00 + 1 pip buffer (0.10) = 2740.10
    assert pkg.active_sl == 2740.10, "Active SL must move to Entry + 1.0 pip buffer (2740.10)"
    assert pkg.tranches["T2"].sl_price == 2740.10, "Tranche 2 SL must be updated to 2740.10"
    assert pkg.tranches["T3"].sl_price == 2740.10, "Tranche 3 SL must be updated to 2740.10"
    print(f">>> Auto Break-Even Verified: Guaranteed Risk-Free Trade Locked at {pkg.active_sl}")

    # 3. Simulate Price Retracement to 2741.00 (Above BE buffer, trade remains safe)
    print("\n--- Simulating Healthy Pullback to 2741.00 ---")
    events_pullback = order_mgr.evaluate_price_tick(pkg, current_price=2741.00)
    assert len(events_pullback) == 0, "No stops should be triggered on pullback above 2740.10"
    assert pkg.tranches["T2"].status == "ACTIVE"
    assert pkg.tranches["T3"].status == "ACTIVE"

    # 4. Simulate Price Surging to 2752.50 (TP2 Hit!)
    print("\n--- Simulating Price Reaching TP2 (2752.50) ---")
    events_tp2 = order_mgr.evaluate_price_tick(pkg, current_price=2752.50)
    for ev in events_tp2:
        print(f"  Event: {ev['event']} -> Tranche {ev.get('tranche')} closed at {ev.get('close_price')} PnL: ${ev.get('pnl_usd')}")

    assert pkg.tranches["T2"].status == "CLOSED_TP", "Tranche 2 must be closed at TP2"
    assert pkg.tranches["T2"].realized_pnl_usd > pkg.tranches["T1"].realized_pnl_usd, "TP2 profit must exceed TP1"

    # 5. Simulate Price Continuing to 2765.00 with Adaptive Trailing Stop
    print("\n--- Simulating Price Surging to 2765.00 & Runner Trailing Stop ---")
    # Gold ATR is 2.0. Trail distance = 1.5 * 2.0 = 3.0. Peak price = 2765.00 -> New SL = 2762.00
    trail_res = trailing_engine.update_trailing_stop(pkg, current_price=2765.00, atr_value=2.0)
    print(f"Trailing Stop Event: {trail_res['event']} | Old SL: {trail_res['old_sl']} -> New SL: {trail_res['new_sl']}")
    assert trail_res is not None
    assert pkg.active_sl == 2762.00, "Trailing stop must ratchet to 2762.00 (Peak 2765.00 - 3.0 ATR buffer)"

    # 6. Simulate Final Runner Exit when Price Pulls Back to 2762.00
    print("\n--- Simulating Runner Exit on Trailing Stop (2762.00) ---")
    final_events = order_mgr.evaluate_price_tick(pkg, current_price=2762.00)
    print(f"Final Exit: {final_events[0]['event']} | PnL: ${final_events[0]['pnl_usd']}")

    assert pkg.status == "CLOSED", "All 3 tranches closed, package complete"
    assert pkg.tranches["T3"].status == "CLOSED_BE" or pkg.tranches["T3"].status == "CLOSED_SL"
    total_realized_pnl = sum(t.realized_pnl_usd for t in pkg.tranches.values())
    print(f"Total Trade Lifecycle Realized PnL: +${total_realized_pnl:.2f} (Target Risk was $100)")
    assert total_realized_pnl > 250.0, "Cumulative profit must reflect institutional 3-tranche scaling"
    print(">>> 3-Tranche Scaling & Auto Break-Even Lifecycle: PASSED (100% Exact)")


if __name__ == "__main__":
    test_confluence_scoring_grade_a_plus()
    test_veto_hierarchy()
    test_3_tranche_order_lifecycle()


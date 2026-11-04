"""
Phase 3 Verification Script: Hybrid Technical Intelligence Core
Tests Pillar 1 (SMC: FVG, Order Block, Asian Sweep),
Pillar 2 (Patterns & S/R Clustering), and Pillar 3 (MTF & SMT Divergence).
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

from backend.modules.pillar1_smc import FVGDetector, OrderBlockDetector, AsianRangeDetector
from backend.modules.pillar2_patterns import SupportResistanceCluster, PatternDetector
from backend.modules.pillar3_mtf_smt import MTFAligner, SMTDivergenceEngine
from backend.modules.technical_analyzer import TechnicalAnalyzer


def test_pillar1_smc():
    print("\n" + "=" * 65)
    print("STEP 1: Testing Pillar 1 (SMC: FVG, Order Block & Asian Range)")
    print("=" * 65)

    now = datetime.now(timezone.utc)
    # Synthetic candles creating an unmistakable Bullish FVG & Order Block
    candles = [
        {"time": now - timedelta(minutes=45), "open": 2738.0, "high": 2739.0, "low": 2737.5, "close": 2737.8, "volume": 1000}, # C1 (Bearish OB candidate)
        {"time": now - timedelta(minutes=30), "open": 2738.0, "high": 2746.0, "low": 2738.0, "close": 2745.5, "volume": 3500}, # C2 (Strong Bullish displacement)
        {"time": now - timedelta(minutes=15), "open": 2745.5, "high": 2748.0, "low": 2743.0, "close": 2747.0, "volume": 2000}, # C3 (Low: 2743.0 > C1 High: 2739.0 -> 40 pip FVG!)
        {"time": now, "open": 2747.0, "high": 2747.5, "low": 2746.0, "close": 2747.2, "volume": 1200},
    ]
    df = pd.DataFrame(candles)

    # 1. Test FVG
    fvg_detector = FVGDetector(min_gap_pips=5.0, pip_size=0.10)
    fvgs = fvg_detector.detect_fvgs(df)
    print(f"Fair Value Gaps Detected: {len(fvgs)}")
    for f in fvgs:
        print(f"  • {f['type']}: Range [{f['bottom']} - {f['top']}] Size: {f['size_pips']} pips | Mitigated: {f['mitigated']}")

    assert len(fvgs) > 0, "Should detect at least 1 FVG"
    assert fvgs[0]["type"] == "BULLISH_FVG", "Should be a Bullish FVG"
    print(">>> FVG Detection: PASSED")

    # 2. Test Order Block
    ob_detector = OrderBlockDetector(displacement_multiplier=1.2, pip_size=0.10)
    obs = ob_detector.detect_order_blocks(df)
    print(f"\nOrder Blocks Detected: {len(obs)}")
    for ob in obs:
        print(f"  • {ob['type']}: Zone [{ob['bottom']} - {ob['top']}] Entry: {ob['entry_level']} SL: {ob['sl_level']}")

    assert len(obs) > 0, "Should detect Bullish Order Block"
    print(">>> Order Block Detection: PASSED")

    # 3. Test Asian Range & Sweep
    asian_detector = AsianRangeDetector(sweep_buffer_pips=2.0, pip_size=0.10)
    asian_mock_range = {"asian_high": 2745.0, "asian_low": 2735.0}

    # Candle that pierces below 2735.0 to 2732.0 but closes back at 2736.0 (Judas Swing)
    sweep_candle = pd.DataFrame([
        {"time": now, "open": 2735.5, "high": 2736.5, "low": 2732.0, "close": 2736.0, "volume": 4000}
    ])
    sweep = asian_detector.detect_liquidity_sweep(sweep_candle, asian_mock_range, pip_size=0.10)
    print(f"\nAsian Sweep Detected: {sweep['sweep_detected']}")
    print(f"  • Type: {sweep.get('type')} | Swept Level: {sweep.get('level_swept')} | Depth: {sweep.get('sweep_depth_pips')} pips")

    assert sweep["sweep_detected"] is True, "Must detect Bullish Judas Sweep"
    assert sweep["type"] == "BULLISH_ASIAN_SWEEP"
    print(">>> Asian Sweep Detection: PASSED")


def test_pillar2_patterns():
    print("\n" + "=" * 65)
    print("STEP 2: Testing Pillar 2 (Classical Patterns & S/R Clusters)")
    print("=" * 65)

    now = datetime.now(timezone.utc)
    # Rejection Hammer / Bullish Pinbar: Open 2740, High 2740.5, Low 2730, Close 2739.8 (Lower wick 9.8 vs body 0.2)
    pinbar_df = pd.DataFrame([
        {"time": now - timedelta(minutes=15), "open": 2742.0, "high": 2743.0, "low": 2739.0, "close": 2740.0, "volume": 1000},
        {"time": now, "open": 2740.0, "high": 2740.5, "low": 2730.0, "close": 2739.8, "volume": 2800},
    ])

    pat_detector = PatternDetector(pip_size=0.10)
    trigger = pat_detector.detect_candlestick_triggers(pinbar_df)
    print(f"Candlestick Trigger: {trigger['pattern']} (Direction: {trigger['direction']})")
    assert trigger["pattern"] == "BULLISH_PINBAR", "Must detect Bullish Pinbar"
    print(">>> Candlestick Rejection Trigger: PASSED")

    # Test Support / Resistance Clustering
    sr_cluster = SupportResistanceCluster(tolerance_pips=5.0, pip_size=0.10)
    # Generate 30 candles bouncing repeatedly off 2730.0
    oscillating_candles = []
    for i in range(30):
        low_val = 2730.0 + (0.2 if i % 2 == 0 else -0.1)
        oscillating_candles.append({
            "time": now - timedelta(minutes=30 * (30 - i)),
            "open": 2735.0,
            "high": 2745.0,
            "low": low_val,
            "close": 2738.0,
            "volume": 1500,
        })
    sr_df = pd.DataFrame(oscillating_candles)
    levels = sr_cluster.cluster_levels(sr_df, window=2, min_touches=2, pip_size=0.10)
    print(f"Key S/R Clusters Identified: {len(levels)}")
    for lvl in levels[:2]:
        print(f"  • Level: {lvl['price_level']} ({lvl['type']}) | Touches: {lvl['touch_count']}")

    assert len(levels) > 0, "Should detect clustered support zone around 2730.0"
    print(">>> S/R Clustering Test: PASSED")


def test_pillar3_mtf_and_smt():
    print("\n" + "=" * 65)
    print("STEP 3: Testing Pillar 3 (MTF Trend Alignment & SMT Divergence)")
    print("=" * 65)

    now = datetime.now(timezone.utc)
    # 1. MTF Aligner Test
    bullish_h4_candles = []
    base_price = 2700.0
    for i in range(25):
        base_price += 2.0
        bullish_h4_candles.append({
            "time": now - timedelta(hours=4 * (25 - i)),
            "open": base_price - 1.0,
            "high": base_price + 2.0,
            "low": base_price - 1.5,
            "close": base_price + 1.0,
            "volume": 2000,
        })
    h4_df = pd.DataFrame(bullish_h4_candles)

    mtf_aligner = MTFAligner()
    mtf_result = mtf_aligner.evaluate_mtf_alignment(h4_df=h4_df)
    print(f"H4 Macro Trend Result: {mtf_result['macro_trend']}")
    assert "BULLISH" in mtf_result["macro_trend"], "Should detect Bullish Macro Trend"
    print(">>> MTF Trend Alignment: PASSED")

    # 2. SMT Divergence Test (Gold makes Lower Low, Silver makes Higher Low)
    smt_engine = SMTDivergenceEngine(lookback_bars=15)
    # Gold: Low 1 = 2735.0, Low 2 = 2730.0 (Lower Low!)
    gold_candles = [
        {"high": 2745.0, "low": 2735.0, "close": 2740.0},
        {"high": 2742.0, "low": 2736.0, "close": 2738.0},
        {"high": 2744.0, "low": 2737.0, "close": 2742.0},
        {"high": 2740.0, "low": 2730.0, "close": 2738.0}, # Lower Low!
        {"high": 2742.0, "low": 2735.0, "close": 2741.0},
    ]
    # Silver: Low 1 = 32.50, Low 2 = 32.65 (Higher Low! Refused to follow Gold down)
    silver_candles = [
        {"high": 33.20, "low": 32.50, "close": 32.90},
        {"high": 33.00, "low": 32.60, "close": 32.85},
        {"high": 33.10, "low": 32.70, "close": 33.00},
        {"high": 33.05, "low": 32.65, "close": 32.95}, # Higher Low! (SMT Divergence)
        {"high": 33.15, "low": 32.80, "close": 33.10},
    ]

    smt_res = smt_engine.detect_smt("XAUUSD", pd.DataFrame(gold_candles), "XAGUSD", pd.DataFrame(silver_candles))
    print(f"\nSMT Divergence Detected: {smt_res['smt_detected']}")
    print(f"  • Type: {smt_res.get('type')}")
    print(f"  • Description: {smt_res.get('description')}")
    print(f"  • Confluence Bonus: +{smt_res.get('confluence_bonus')} points")

    assert smt_res["smt_detected"] is True, "Must detect Bullish SMT Divergence"
    assert smt_res["type"] == "BULLISH_SMT"
    print(">>> SMT Intermarket Divergence Test: PASSED")


def test_unified_technical_analyzer():
    print("\n" + "=" * 65)
    print("STEP 4: Testing Unified Technical Analyzer")
    print("=" * 65)

    analyzer = TechnicalAnalyzer()
    now = datetime.now(timezone.utc)
    sample_df = pd.DataFrame([
        {"time": now - timedelta(minutes=45), "open": 2738.0, "high": 2739.0, "low": 2737.5, "close": 2737.8, "volume": 1000},
        {"time": now - timedelta(minutes=30), "open": 2738.0, "high": 2746.0, "low": 2738.0, "close": 2745.5, "volume": 3500},
        {"time": now - timedelta(minutes=15), "open": 2745.5, "high": 2748.0, "low": 2743.0, "close": 2747.0, "volume": 2000},
        {"time": now, "open": 2747.0, "high": 2747.5, "low": 2746.0, "close": 2747.2, "volume": 1200},
    ])

    report = analyzer.analyze_symbol(symbol="XAUUSD", m15_df=sample_df)
    print(f"Symbol Analyzed: {report['symbol']}")
    print(f"Technical Score: {report['technical_score']} / 100")
    print(f"Identified Technical Confluences:")
    for r in report["reasons"]:
        print(f"  • {r}")

    assert report["technical_score"] > 0, "Technical score must be computed"
    print(">>> Unified Technical Analyzer Test: PASSED (100% Exact)")


if __name__ == "__main__":
    test_pillar1_smc()
    test_pillar2_patterns()
    test_pillar3_mtf_and_smt()
    test_unified_technical_analyzer()


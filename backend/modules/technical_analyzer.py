"""
Unified Technical Analysis Hub
Integrates Pillar 1 (SMC), Pillar 2 (Patterns & S/R), and Pillar 3 (MTF & SMT Divergence)
into a single cohesive quantitative analysis engine.
"""

from typing import Dict, Any, Optional
import pandas as pd

from backend.modules.pillar1_smc import FVGDetector, OrderBlockDetector, AsianRangeDetector
from backend.modules.pillar2_patterns import SupportResistanceCluster, PatternDetector
from backend.modules.pillar3_mtf_smt import MTFAligner, SMTDivergenceEngine
from backend.bridge.symbol_manager import SymbolManager


class TechnicalAnalyzer:
    def __init__(self):
        self.symbol_manager = SymbolManager()
        self.fvg_detector = FVGDetector()
        self.ob_detector = OrderBlockDetector()
        self.asian_detector = AsianRangeDetector()
        self.sr_cluster = SupportResistanceCluster()
        self.pattern_detector = PatternDetector()
        self.mtf_aligner = MTFAligner()
        self.smt_engine = SMTDivergenceEngine()

    def analyze_symbol(
        self,
        symbol: str,
        m15_df: pd.DataFrame,
        h4_df: Optional[pd.DataFrame] = None,
        daily_df: Optional[pd.DataFrame] = None,
        correlated_df: Optional[pd.DataFrame] = None,
    ) -> Dict[str, Any]:
        """
        Executes complete multi-pillar scan on a target symbol.
        """
        clean_sym = self.symbol_manager.normalize_symbol(symbol)
        pip_size = self.symbol_manager.specs.get(clean_sym, {}).get("pip_size", 0.0001)

        # --- PILLAR 1: SMC / ICT ---
        unmitigated_fvgs = self.fvg_detector.get_unmitigated_fvgs(m15_df, pip_size=pip_size)
        unmitigated_obs = self.ob_detector.get_unmitigated_obs(m15_df, pip_size=pip_size)
        asian_range = self.asian_detector.calculate_asian_range(m15_df)
        asian_sweep = self.asian_detector.detect_liquidity_sweep(m15_df, asian_range, pip_size=pip_size)

        # --- PILLAR 2: CLASSICAL PATTERNS & S/R ---
        sr_levels = self.sr_cluster.cluster_levels(m15_df, pip_size=pip_size)
        candle_trigger = self.pattern_detector.detect_candlestick_triggers(m15_df)
        double_bottom = self.pattern_detector.detect_double_bottom(m15_df, pip_size=pip_size)

        # --- PILLAR 3: MTF & SMT DIVERGENCE ---
        mtf_status = self.mtf_aligner.evaluate_mtf_alignment(h4_df, daily_df)

        correlated_sym = self.smt_engine.CORRELATED_PAIRS.get(clean_sym, "")
        smt_status = {"smt_detected": False, "type": "NONE"}
        if correlated_df is not None and not correlated_df.empty:
            smt_status = self.smt_engine.detect_smt(clean_sym, m15_df, correlated_sym, correlated_df)

        # Compute Technical Layer Points (0-100)
        points = 0
        reasons = []

        # SMC Points (max 40)
        if unmitigated_fvgs:
            points += 15
            reasons.append(f"Unmitigated {unmitigated_fvgs[-1]['type']} ({unmitigated_fvgs[-1]['size_pips']} pips)")
        if unmitigated_obs:
            points += 15
            reasons.append(f"Institutional {unmitigated_obs[-1]['type']}")
        if asian_sweep.get("sweep_detected"):
            points += 10
            reasons.append(f"Asian Liquidity Grab ({asian_sweep['type']})")

        # Pattern & S/R Points (max 30)
        if candle_trigger.get("pattern") != "NONE":
            points += 15
            reasons.append(f"Candlestick Trigger: {candle_trigger['pattern']}")
        if double_bottom:
            points += 15
            reasons.append("Structural Double Bottom Pattern")
        elif sr_levels and sr_levels[0]["distance_pips"] < 12.0:
            points += 10
            reasons.append(f"Proximity to Key {sr_levels[0]['type']} Zone")

        # MTF & SMT Points (max 30)
        if mtf_status.get("macro_trend") in ["STRONG_BULLISH", "STRONG_BEARISH"]:
            points += 15
            reasons.append(f"Strong MTF Trend: {mtf_status['macro_trend']}")
        elif mtf_status.get("macro_trend") in ["BULLISH", "BEARISH"]:
            points += 10

        if smt_status.get("smt_detected"):
            points += smt_status.get("confluence_bonus", 15)
            reasons.append(f"SMT Divergence: {smt_status['type']}")

        return {
            "symbol": clean_sym,
            "technical_score": min(100, points),
            "reasons": reasons,
            "pillar1_smc": {
                "active_fvgs": unmitigated_fvgs[:3],
                "active_obs": unmitigated_obs[:3],
                "asian_range": asian_range,
                "asian_sweep": asian_sweep,
            },
            "pillar2_patterns": {
                "key_sr_levels": sr_levels[:3],
                "candlestick_trigger": candle_trigger,
                "double_bottom": double_bottom,
            },
            "pillar3_mtf_smt": {
                "mtf_alignment": mtf_status,
                "smt_divergence": smt_status,
            },
        }


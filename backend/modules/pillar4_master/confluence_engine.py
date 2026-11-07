"""
Pillar 4 Confluence Arbiter Engine
Integrates Layer 0 Macro, Pillar 1 SMC, Pillar 2 Classical Patterns, and Pillar 3 MTF/SMT.
Calculates 0-100% Confluence Score, assigns Grades (A+, A), and enforces strict Veto hierarchy.
"""

from typing import Dict, Any, List, Optional
import json
import os


class ConfluenceEngine:
    DEFAULT_CONFIG = {
        "macro_news_weight": 20.0,
        "smc_liquidity_weight": 30.0,
        "classical_pattern_weight": 20.0,
        "mtf_alignment_weight": 15.0,
        "smt_divergence_weight": 15.0,
        "grade_a_plus_threshold": 80.0,
        "grade_a_threshold": 65.0,
        "max_trades_per_day": 2,
        "max_spread_pips": {
            "EURUSD": 1.5,
            "GBPUSD": 2.0,
            "XAUUSD": 3.0,
            "XAGUSD": 4.0,
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)

    def load_config(self, config_path: str):
        """Loads configuration from strategy_dna.json."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            weights = data.get("confluence_weights", {})
            self.config["macro_news_weight"] = weights.get("macro_news_weight", 0.20) * 100.0
            self.config["smc_liquidity_weight"] = weights.get("smc_liquidity_weight", 0.30) * 100.0
            self.config["classical_pattern_weight"] = weights.get("classical_pattern_weight", 0.20) * 100.0
            self.config["mtf_alignment_weight"] = weights.get("mtf_alignment_weight", 0.15) * 100.0
            self.config["smt_divergence_weight"] = weights.get("smt_divergence_weight", 0.15) * 100.0
            self.config["grade_a_plus_threshold"] = weights.get("grade_a_plus_threshold", 80.0)
            self.config["grade_a_threshold"] = weights.get("grade_a_threshold", 65.0)

            risk = data.get("risk_management", {})
            self.config["max_trades_per_day"] = risk.get("max_trades_per_day", 2)

            instruments = data.get("instruments", {})
            for sym, info in instruments.items():
                if "max_spread_pips" in info:
                    self.config["max_spread_pips"][sym] = info["max_spread_pips"]
        except Exception as e:
            print(f"[ConfluenceEngine] Warning: Could not parse config {config_path}: {e}")

    def evaluate(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        sl_price: float,
        current_spread_pips: float,
        macro_data: Optional[Dict[str, Any]] = None,
        smc_data: Optional[Dict[str, Any]] = None,
        pattern_data: Optional[Dict[str, Any]] = None,
        mtf_data: Optional[Dict[str, Any]] = None,
        smt_data: Optional[Dict[str, Any]] = None,
        daily_stats: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Runs comprehensive Master Arbiter evaluation across all pillars and vetos.
        Returns detailed scoring breakdown, active vetos, grade, and final action recommendation.
        """
        direction = direction.upper()
        symbol = symbol.upper()
        macro_data = macro_data or {}
        smc_data = smc_data or {}
        pattern_data = pattern_data or {}
        mtf_data = mtf_data or {}
        smt_data = smt_data or {}
        daily_stats = daily_stats or {}

        reasons: List[str] = []
        vetos: List[str] = []

        # ==========================================================
        # 1. VETO CHECKS (Strict Hierarchy)
        # ==========================================================

        # Check 1: News Guard VETO (High-Impact Red Folder Blackout)
        news_guard = macro_data.get("news_guard", {})
        if news_guard.get("news_veto", False):
            minutes = news_guard.get("minutes_to_next", 0)
            event_name = news_guard.get("next_event", {}).get("title", "High-Impact Event")
            vetos.append(f"NEWS_VETO: Red folder '{event_name}' within {abs(round(minutes, 1))} minutes.")

        # Check 2: Spread Guard VETO
        max_spread = self.config["max_spread_pips"].get(symbol, 3.0)
        if current_spread_pips > max_spread:
            vetos.append(
                f"SPREAD_VETO: Current spread ({current_spread_pips} pips) exceeds maximum threshold ({max_spread} pips)."
            )

        # Check 3: Daily Cap Guard VETO
        trades_today = daily_stats.get("trades_taken_today", 0)
        max_daily_trades = self.config.get("max_trades_per_day", 2)
        if trades_today >= max_daily_trades:
            vetos.append(
                f"DAILY_CAP_VETO: Daily execution limit of {max_daily_trades} trades has been reached ({trades_today} taken)."
            )

        # Check 3b: Prop Firm Daily Drawdown VETO
        daily_dd_pct = daily_stats.get("daily_drawdown_pct", 0.0)
        max_daily_dd = self.config.get("max_daily_drawdown_pct", 4.0)
        if daily_dd_pct >= max_daily_dd:
            vetos.append(
                f"DRAWDOWN_VETO: Daily drawdown ({daily_dd_pct:.2f}%) has breached Prop Firm limit ({max_daily_dd:.1f}%)."
            )

        # Check 3c: Friday Weekend Gap Guard VETO
        trade_dt = daily_stats.get("current_dt")
        if trade_dt and hasattr(trade_dt, "weekday"):
            if trade_dt.weekday() == 4 and trade_dt.hour >= 20:
                vetos.append(
                    f"FRIDAY_WEEKEND_VETO: Market approaches weekend close ({trade_dt.strftime('%H:%M')} GMT). Entries frozen."
                )

        # Check 4: MTF Counter-Trend VETO
        macro_trend = mtf_data.get("macro_trend", "NEUTRAL").upper()
        if direction == "BUY" and "BEARISH" in macro_trend:
            vetos.append("MTF_VETO: Cannot execute BUY against strong Bearish H4/Daily trend.")
        elif direction == "SELL" and "BULLISH" in macro_trend:
            vetos.append("MTF_VETO: Cannot execute SELL against strong Bullish H4/Daily trend.")

        # Check 5: Hermes Macro Bias Severe Opposition VETO
        hermes_bias = macro_data.get("hermes_bias", 0.0)
        if isinstance(hermes_bias, dict):
            hermes_bias = hermes_bias.get("bias_score", 0.0)
        if direction == "BUY" and hermes_bias <= -50.0:
            vetos.append(f"HERMES_MACRO_VETO: Severe negative macro sentiment ({hermes_bias}) opposes BUY.")
        elif direction == "SELL" and hermes_bias >= 50.0:
            vetos.append(f"HERMES_MACRO_VETO: Severe positive macro sentiment ({hermes_bias}) opposes SELL.")

        # ==========================================================
        # 2. CONFLUENCE SCORING (0 to 100)
        # ==========================================================

        # Pillar 1: SMC / Liquidity (Max 30 pts)
        smc_score = 0.0
        obs = smc_data.get("obs", [])
        fvgs = smc_data.get("fvgs", [])
        asian_sweep = smc_data.get("asian_sweep", {})

        # Active Order Block matching direction
        matching_obs = [ob for ob in obs if (direction == "BUY" and ob.get("type") == "BULLISH_OB") or
                                            (direction == "SELL" and ob.get("type") == "BEARISH_OB")]
        if matching_obs:
            smc_score += 15.0
            reasons.append(f"Institutional {matching_obs[0]['type']} tapped at zone [{matching_obs[0]['bottom']:.2f} - {matching_obs[0]['top']:.2f}]")

        # Unmitigated FVG matching direction
        matching_fvgs = [f for f in fvgs if not f.get("mitigated", False) and
                         ((direction == "BUY" and f.get("type") == "BULLISH_FVG") or
                          (direction == "SELL" and f.get("type") == "BEARISH_FVG"))]
        if matching_fvgs:
            smc_score += 10.0
            reasons.append(f"Unmitigated {matching_fvgs[0]['type']} ({matching_fvgs[0].get('size_pips', 0)} pips) imbalance")

        # Asian Session Liquidity Sweep (Judas Swing)
        if asian_sweep.get("sweep_detected", False):
            sweep_type = asian_sweep.get("type", "")
            if (direction == "BUY" and "BULLISH" in sweep_type) or (direction == "SELL" and "BEARISH" in sweep_type):
                smc_score += 15.0
                reasons.append(f"Asian Liquidity Judas Swing Sweep confirmed ({asian_sweep.get('sweep_depth_pips')} pips depth)")

        smc_score = min(self.config["smc_liquidity_weight"], smc_score)

        # Pillar 2: Classical Patterns & Horizontal S/R (Max 20 pts)
        pattern_score = 0.0
        candlestick = pattern_data.get("candlestick_trigger", {})
        c_dir = candlestick.get("direction", "").upper()
        if (direction == "BUY" and c_dir in ("BULLISH", "BUY")) or (direction == "SELL" and c_dir in ("BEARISH", "SELL")):
            pattern_score += 12.0
            reasons.append(f"Trigger Candlestick Confirmation: {candlestick.get('pattern')}")

        sr_clusters = pattern_data.get("sr_clusters", [])
        if sr_clusters:
            pattern_score += 8.0
            reasons.append(f"Confluent Horizontal Key Level support/resistance cluster ({len(sr_clusters)} touches)")

        pattern_score = min(self.config["classical_pattern_weight"], pattern_score)

        # Pillar 3: MTF EMA & Structure (Max 15 pts)
        mtf_score = 0.0
        if (direction == "BUY" and "BULLISH" in macro_trend) or (direction == "SELL" and "BEARISH" in macro_trend):
            mtf_score += 10.0
            reasons.append(f"Aligned with H4/Daily Macro EMA Trend ({macro_trend})")
            if mtf_data.get("daily_aligned", False):
                mtf_score += 5.0
                reasons.append("Multi-Timeframe Daily & H4 Confluence locked")

        mtf_score = min(self.config["mtf_alignment_weight"], mtf_score)

        # Pillar 3: SMT Intermarket Divergence (Max 15 pts)
        smt_score = 0.0
        if smt_data.get("smt_detected", False):
            smt_type = smt_data.get("type", "")
            if (direction == "BUY" and "BULLISH" in smt_type) or (direction == "SELL" and "BEARISH" in smt_type):
                smt_score = float(smt_data.get("confluence_bonus", 15.0))
                reasons.append(f"SMT Intermarket Divergence non-confirmation: {smt_data.get('description', '')}")

        smt_score = min(self.config["smt_divergence_weight"], smt_score)

        # Layer 0: Macro News & Hermes AI Sentiment (Max 20 pts)
        macro_score = 0.0
        if (direction == "BUY" and hermes_bias > 15.0) or (direction == "SELL" and hermes_bias < -15.0):
            # Proportional points up to 20 pts
            abs_bias = min(100.0, abs(hermes_bias))
            macro_score = round((abs_bias / 100.0) * self.config["macro_news_weight"], 1)
            reasons.append(f"Hermes AI Macro Bias corroborates {direction} (+{hermes_bias:.1f} sentiment)")
        elif abs(hermes_bias) <= 15.0:
            macro_score = round(self.config["macro_news_weight"] * 0.5, 1)  # Neutral environment neutral pass (10 pts)
            reasons.append("Hermes AI Macro Environment is calm/neutral")

        macro_score = min(self.config["macro_news_weight"], macro_score)

        # Total Confluence Score
        total_score = round(smc_score + pattern_score + mtf_score + smt_score + macro_score, 1)
        total_score = min(100.0, max(0.0, total_score))

        # ==========================================================
        # 3. GRADING & DECISION ARBITRATION
        # ==========================================================
        if total_score >= self.config["grade_a_plus_threshold"]:
            grade = "GRADE_A_PLUS"
        elif total_score >= self.config["grade_a_threshold"]:
            grade = "GRADE_A"
        else:
            grade = "GRADE_B_OR_LOWER"

        is_vetoed = len(vetos) > 0
        is_approved = (not is_vetoed) and (grade in ["GRADE_A_PLUS", "GRADE_A"])

        if is_vetoed:
            decision = "BLOCKED_BY_VETO"
        elif is_approved:
            decision = "APPROVED_FOR_EXECUTION"
        else:
            decision = "SUB_THRESHOLD_STAND_DOWN"

        return {
            "symbol": symbol,
            "direction": direction,
            "entry_price": entry_price,
            "sl_price": sl_price,
            "confluence_score": total_score,
            "grade": grade,
            "decision": decision,
            "is_approved": is_approved,
            "veto_active": is_vetoed,
            "vetos": vetos,
            "confluence_breakdown": {
                "smc_liquidity": smc_score,
                "classical_patterns": pattern_score,
                "mtf_alignment": mtf_score,
                "smt_divergence": smt_score,
                "macro_hermes": macro_score,
            },
            "reasons": reasons,
        }


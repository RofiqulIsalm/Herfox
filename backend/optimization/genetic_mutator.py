"""
Genetic Strategy Mutator
Applies bounded Bayesian parameter mutations to Strategy DNA:
- FVG sensitivity & mitigation threshold
- Order Block displacement multiplier
- Asian Range Judas Swing buffer
- Stop Loss ATR multiplier
- Take Profit R:R ratios
- Confluence weight matrices
Mathematically bounded to prevent absurd parameters while exploring alpha space.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
import random
import json
import os
import uuid


@dataclass
class StrategyVariant:
    variant_id: str
    generation: int
    asset: str
    params: Dict[str, Any]
    mutation_notes: str
    parent_id: Optional[str] = "CHAMPION-BASELINE"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GeneticMutator:
    # Parameter Bounds for Safe Exploration
    BOUNDS = {
        "atr_sl_multiplier": (1.1, 2.2),
        "tp1_rr_ratio": (0.8, 1.8),
        "tp2_rr_ratio": (2.0, 3.5),
        "asian_sweep_buffer_pips": (1.5, 6.0),
        "fvg_min_gap_pips": (3.0, 15.0),
        "ob_displacement_multiplier": (1.2, 2.5),
        "grade_a_plus_threshold": (78.0, 92.0),
        "confluence_weights": {
            "macro_news_weight": (0.10, 0.30),
            "smc_liquidity_weight": (0.20, 0.40),
            "classical_pattern_weight": (0.15, 0.30),
            "mtf_alignment_weight": (0.10, 0.25),
            "smt_divergence_weight": (0.10, 0.25),
        },
    }

    def __init__(self, baseline_config_path: Optional[str] = None):
        self.baseline_path = baseline_config_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "config", "strategy_dna.json")
        )
        self.baseline_dna = self._load_baseline()

    def _load_baseline(self) -> Dict[str, Any]:
        """Loads champion baseline DNA configuration."""
        if os.path.exists(self.baseline_path):
            try:
                with open(self.baseline_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[GeneticMutator] Warning loading baseline: {e}")

        # Sensible fallback baseline
        return {
            "active_champion_id": "DNA-DEFAULT-M15-V1",
            "risk_management": {
                "atr_sl_multiplier": 1.4,
                "tp1_rr_ratio": 1.0,
                "tp2_rr_ratio": 2.5,
            },
            "confluence_weights": {
                "macro_news_weight": 0.20,
                "smc_liquidity_weight": 0.30,
                "classical_pattern_weight": 0.20,
                "mtf_alignment_weight": 0.15,
                "smt_divergence_weight": 0.15,
                "grade_a_plus_threshold": 80.0,
            },
        }

    def mutate_variant(
        self,
        parent: Optional[StrategyVariant] = None,
        asset: str = "XAUUSD",
        generation: int = 1,
        variant_index: Optional[int] = None,
        mutation_rate: float = 0.25,
    ) -> StrategyVariant:
        """
        Creates a new candidate strategy mutation by perturbing 1-3 parameters
        with bounded Gaussian noise around the parent parameters.
        """
        if parent:
            base_params = json.loads(json.dumps(parent.params))
            parent_id = parent.variant_id
        else:
            risk = self.baseline_dna.get("risk_management", {})
            weights = self.baseline_dna.get("confluence_weights", {})
            base_params = {
                "atr_sl_multiplier": risk.get("atr_sl_multiplier", 1.4),
                "tp1_rr_ratio": risk.get("tp1_rr_ratio", 1.0),
                "tp2_rr_ratio": risk.get("tp2_rr_ratio", 2.5),
                "asian_sweep_buffer_pips": 2.5,
                "fvg_min_gap_pips": 5.0,
                "ob_displacement_multiplier": 1.6,
                "grade_a_plus_threshold": weights.get("grade_a_plus_threshold", 80.0),
                "macro_news_weight": weights.get("macro_news_weight", 0.20),
                "smc_liquidity_weight": weights.get("smc_liquidity_weight", 0.30),
                "classical_pattern_weight": weights.get("classical_pattern_weight", 0.20),
                "mtf_alignment_weight": weights.get("mtf_alignment_weight", 0.15),
                "smt_divergence_weight": weights.get("smt_divergence_weight", 0.15),
            }
            parent_id = self.baseline_dna.get("active_champion_id", "CHAMPION-BASELINE")

        notes = []

        # Perturb scalar parameters
        for key in ["atr_sl_multiplier", "tp1_rr_ratio", "tp2_rr_ratio", "asian_sweep_buffer_pips", "fvg_min_gap_pips", "ob_displacement_multiplier", "grade_a_plus_threshold"]:
            if random.random() < mutation_rate:
                low, high = self.BOUNDS[key]
                val = base_params.get(key, (low + high) / 2)
                # Apply Gaussian shift
                delta = random.gauss(0, (high - low) * 0.08)
                new_val = round(max(low, min(high, val + delta)), 2)
                if new_val != val:
                    notes.append(f"{key}: {val} -> {new_val}")
                    base_params[key] = new_val

        # Perturb confluence weights (normalize sum to 1.0)
        if random.random() < mutation_rate:
            w_keys = ["macro_news_weight", "smc_liquidity_weight", "classical_pattern_weight", "mtf_alignment_weight", "smt_divergence_weight"]
            perturbed_weights = {}
            for k in w_keys:
                low, high = self.BOUNDS["confluence_weights"][k]
                val = base_params.get(k, 0.20)
                delta = random.gauss(0, 0.03)
                perturbed_weights[k] = max(low, min(high, val + delta))

            # Normalize weights
            total_w = sum(perturbed_weights.values())
            for k in w_keys:
                base_params[k] = round(perturbed_weights[k] / total_w, 3)
            notes.append("Rebalanced confluence weights")

        variant_num_str = f"{variant_index:02d}" if variant_index is not None else uuid.uuid4().hex[:4].upper()
        variant_id = f"DNA-{asset.upper()}-M15-G{generation}-V{variant_num_str}"
        mutation_summary = ", ".join(notes) if notes else "Micro-tuned parameter weights"

        return StrategyVariant(
            variant_id=variant_id,
            generation=generation,
            asset=asset.upper(),
            params=base_params,
            mutation_notes=mutation_summary,
            parent_id=parent_id,
        )

    def generate_population(
        self,
        count: int = 15,
        asset: str = "XAUUSD",
        generation: int = 1,
        seed_variant: Optional[StrategyVariant] = None,
    ) -> List[StrategyVariant]:
        """Generates a diverse population of candidate strategy variants."""
        variants = []
        for i in range(count):
            v = self.mutate_variant(
                parent=seed_variant,
                asset=asset,
                generation=generation,
                variant_index=i + 1,
            )
            variants.append(v)
        return variants

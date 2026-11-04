"""
Hermes AI Macro Research & Causal Impact Engine
Analyzes breaking market-moving news and central bank updates.
Computes Causal Impact Dossiers and Asset Bias Scores (-100 to +100)
for EURUSD, GBPUSD, XAUUSD (Gold), and XAGUSD (Silver).
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger("HermesMacroAgent")


class HermesMacroAgent:
    # Causal Keyword Weights for specific asset drivers
    SAFE_HAVEN_BULLISH = [
        "war", "conflict", "escalation", "tensions", "crisis", "missile", 
        "attack", "sanctions", "nuclear", "retaliation", "hostage", "threat"
    ]
    
    USD_HAWKISH_DRIVERS = [
        "rate hike", "hawkish", "sticky inflation", "cautious on rate cuts", 
        "higher for longer", "resilient jobs", "dollar surges", "yields climb"
    ]
    
    USD_DOVISH_DRIVERS = [
        "rate cut", "dovish", "cooling inflation", "economic slowdown", 
        "policy easing", "yields tumble", "dollar weakens", "disinflation"
    ]

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def analyze_headline(self, title: str) -> Dict[str, Any]:
        """Performs lexical and causal domain analysis on a single headline."""
        text_lower = title.lower()
        vader_scores = self.vader.polarity_scores(title)
        compound = vader_scores["compound"]  # -1.0 to +1.0

        # Causal impact flags
        is_safe_haven = any(k in text_lower for k in self.SAFE_HAVEN_BULLISH)
        is_usd_hawkish = any(k in text_lower for k in self.USD_HAWKISH_DRIVERS)
        is_usd_dovish = any(k in text_lower for k in self.USD_DOVISH_DRIVERS)

        # Asset specific multipliers
        gold_impact = 0.0
        eur_impact = 0.0
        gbp_impact = 0.0

        if is_safe_haven:
            gold_impact += 65.0  # Safe-haven demand boosts Gold & Silver
        if is_usd_hawkish:
            gold_impact -= 25.0
            eur_impact -= 45.0
            gbp_impact -= 40.0
        elif is_usd_dovish:
            gold_impact += 35.0
            eur_impact += 45.0
            gbp_impact += 40.0

        # Incorporate baseline sentiment compound
        sentiment_delta = compound * 20.0
        gold_impact += sentiment_delta
        eur_impact += sentiment_delta * 0.5
        gbp_impact += sentiment_delta * 0.5

        return {
            "title": title,
            "compound_sentiment": compound,
            "is_safe_haven": is_safe_haven,
            "is_usd_hawkish": is_usd_hawkish,
            "is_usd_dovish": is_usd_dovish,
            "gold_impact": max(-100.0, min(100.0, gold_impact)),
            "eur_impact": max(-100.0, min(100.0, eur_impact)),
            "gbp_impact": max(-100.0, min(100.0, gbp_impact)),
        }

    def evaluate_news_stream(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesizes a full stream of headlines into a structured Market Impact Dossier.
        Returns aggregate Asset Bias Scores (-100 to +100) and directional vetos.
        """
        if not news_items:
            return self._default_dossier()

        analyzed_items = [self.analyze_headline(item.get("title", "")) for item in news_items]

        # Calculate weighted averages
        avg_gold = sum(item["gold_impact"] for item in analyzed_items) / len(analyzed_items)
        avg_eur = sum(item["eur_impact"] for item in analyzed_items) / len(analyzed_items)
        avg_gbp = sum(item["gbp_impact"] for item in analyzed_items) / len(analyzed_items)
        # Silver correlates strongly with Gold (0.85 beta)
        avg_silver = avg_gold * 0.85

        safe_haven_active = any(item["is_safe_haven"] for item in analyzed_items)
        dominant_severity = "HIGH" if safe_haven_active or abs(avg_gold) > 40 else "MEDIUM"

        # Directional vetos (e.g. Do NOT short Gold when safe haven is surging)
        directional_vetos = {}
        if avg_gold >= 50.0:
            directional_vetos["XAUUSD"] = "VETO_SELL"  # Prohibit shorting into strong macro safe-haven
            directional_vetos["XAGUSD"] = "VETO_SELL"
        elif avg_gold <= -50.0:
            directional_vetos["XAUUSD"] = "VETO_BUY"

        if avg_eur <= -45.0:
            directional_vetos["EURUSD"] = "VETO_BUY"
        elif avg_eur >= 45.0:
            directional_vetos["EURUSD"] = "VETO_SELL"

        summary_theme = (
            "Geopolitical escalation driving safe-haven demand into Precious Metals."
            if safe_haven_active
            else "Central bank policy expectations and inflation metrics guiding currency flows."
        )

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dominant_macro_theme": summary_theme,
            "severity": dominant_severity,
            "safe_haven_status": "SURGING" if safe_haven_active else "NEUTRAL",
            "asset_biases": {
                "XAUUSD": round(avg_gold, 1),
                "XAGUSD": round(avg_silver, 1),
                "EURUSD": round(avg_eur, 1),
                "GBPUSD": round(avg_gbp, 1),
            },
            "directional_vetos": directional_vetos,
            "headlines_analyzed": len(news_items),
        }

    def _default_dossier(self) -> Dict[str, Any]:
        """Neutral fallback dossier when no headlines are available."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dominant_macro_theme": "Market environment neutral; no major macro shock detected.",
            "severity": "LOW",
            "safe_haven_status": "NEUTRAL",
            "asset_biases": {
                "XAUUSD": 0.0,
                "XAGUSD": 0.0,
                "EURUSD": 0.0,
                "GBPUSD": 0.0,
            },
            "directional_vetos": {},
            "headlines_analyzed": 0,
        }


"""
Layer 0 Macro Module Package Initialization
"""
from .news_guard import NewsGuard
from .rss_fetcher import RSSFetcher
from .hermes_agent import HermesMacroAgent

# Alias for convenience
HermesAgent = HermesMacroAgent

__all__ = ["NewsGuard", "RSSFetcher", "HermesMacroAgent", "HermesAgent"]

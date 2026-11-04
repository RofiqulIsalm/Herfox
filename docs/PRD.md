# Product Requirements Document (PRD) - The Life Forex Confluence Terminal

> **Status:** Discovery & Planning Phase  
> **Last Updated:** 2026-11-02  
> **Document Purpose:** Single source of truth for features, trading engine architecture, data feeds, and technical specifications before development starts.

---

## 1. Executive Summary & Vision
- **Project Name:** The Life Forex Confluence Terminal *(Tentative)*
- **Vision:** An all-in-one professional Forex charting, backtesting, and automated market analysis terminal designed to eliminate the need for expensive TradingView subscriptions.
- **Primary Objective:** Empower traders with an 80% automated analysis workflow using a multi-layer Confluence Decision Engine combining Market Structure, Pattern Probability, and Multi-Timeframe Alignment.

---

## 2. Problem Statement & Opportunity
- **Problems with Existing Solutions (TradingView Paid):**
  - High recurring monthly/yearly subscription costs.
  - Artificial restrictions on free tiers (limited to 2-3 indicators per chart, restricted bar replay/backtesting range, limited alerts).
  - Lack of unified, cross-indicator algorithmic decision-making (users must manually reconcile multiple conflicting indicators).
- **The Opportunity:**
  - Build a custom, local-first terminal utilizing open-source TradingView Lightweight Charts.
  - Integrate unlimited custom indicators and multi-timeframe analytics with zero subscription cost.
  - Implement a 4-Pillar Confluence Engine to generate data-backed setups with calculated entry, stop loss, and take profit.

---

## 3. Target Audience, Assets & Prop Firm Safety
- **Primary Persona:** Active Forex & Prop Firm trader (managing Exness, FTMO, and FundingPips accounts). Requires discipline enforcement (max 1-2 trades/day on M15), zero manual lot calculation errors, and instant Telegram execution alerts.
- **Target Asset Universe:**
  1. `EURUSD` (Forex major - 4-decimal standard pip)
  2. `GBPUSD` (Forex major - high volatility intraday)
  3. `XAUUSD` (Spot Gold - $0.10 / 10-point pip, commodity safe-haven dynamics)
  4. `XAGUSD` (Spot Silver - $0.01 pip, 5,000 oz contract size)

---

## 4. System Architecture & Multi-Layer Intelligence Engine

> **Detailed Intelligence Specification:** For the complete multi-agent handshake, veto hierarchy, and market regime classifier, refer to:  
> [docs/INDICATOR_COMMUNICATION_AND_INTELLIGENCE.md](file:///c:/Users/OS/Desktop/The%20Life/docs/INDICATOR_COMMUNICATION_AND_INTELLIGENCE.md)  
> **Recursive Self-Improvement (RSI):** For the continuous self-learning, post-mortem error analysis, walk-forward testing, and champion-challenger architecture, refer to:  
> [docs/RECURSIVE_SELF_IMPROVEMENT_SPEC.md](file:///c:/Users/OS/Desktop/The%20Life/docs/RECURSIVE_SELF_IMPROVEMENT_SPEC.md)  
> **Empirical Feasibility & 100% Live Proof Report:** For the real-time live API tests, binary checks, and math validation, refer to:  
> [docs/EMPIRICAL_PROOF_AND_FEASIBILITY_REPORT.md](file:///c:/Users/OS/Desktop/The%20Life/docs/EMPIRICAL_PROOF_AND_FEASIBILITY_REPORT.md)  
> **Engineering System Design (SDD):** For the low-latency IPC, WebSocket event bus, and SQLite schema, refer to:  
> [docs/SYSTEM_DESIGN.md](file:///c:/Users/OS/Desktop/The%20Life/docs/SYSTEM_DESIGN.md)  
> **UI/UX & Wireframe Specification:** For the button-by-button layout, color palette, and screen zones, refer to:  
> [docs/UI_UX_DESIGN_SPECIFICATION.md](file:///c:/Users/OS/Desktop/The%20Life/docs/UI_UX_DESIGN_SPECIFICATION.md)  
> **Master Execution Roadmap (Phases 1-8):** For the sequential phased development and verification protocol, refer to:  
> [docs/EXECUTION_PHASES_AND_ROADMAP.md](file:///c:/Users/OS/Desktop/The%20Life/docs/EXECUTION_PHASES_AND_ROADMAP.md)  
> **Telegram Intelligence & 2-Way Remote Spec:** For the mobile alerts, chart snapshots, Hermes flash briefings, and interactive phone commands, refer to:  
> [docs/TELEGRAM_INTELLIGENCE_AND_DISPATCH_SPEC.md](file:///c:/Users/OS/Desktop/The%20Life/docs/TELEGRAM_INTELLIGENCE_AND_DISPATCH_SPEC.md)

```
       [ MetaTrader 5 (MT5) Terminal - Exness / FTMO / FundingPips ]
                                    │
               (Python MetaTrader5 API: Live Ticks, Bars, Balance)
                                    │
 ┌──────────────────────────────────┴──────────────────────────────────┐
 │                                                                     │
 ▼                                                                     ▼
[ Layer 0: Global AI Macro & News Guard ]               [ Layer 1: Technical Hybrid Engine ]
- Live RSS / Geopolitics (Middle East, US-Iran)         ┌───────────────────────┼───────────────────────┐
- Tech / Macro Catalyst (DeepSeek/NVDA, Rate cuts)      ▼                       ▼                       ▼
- Economic Calendar (ForexFactory Red Folders)     [ Pillar 1 ]            [ Pillar 2 ]            [ Pillar 3 ]
- Automatic 15-30m NO-TRADE News Freeze            SMC / ICT Engine        Classical Price Action  Multi-Timeframe (MTF)
- Asset Sentiment Score (-100 to +100)             (OB, FVG, Liquidity     (Support/Resistance,    (Daily / H4 / H1
                                                    Sweeps, BOS/CHoCH)      Patterns, Trendlines)   Trend Bias for M15)
 │                                                      │                       │                       │
 └──────────────────────────────────┬───────────────────┴───────────────────────┴───────────────────────┘
                                    ▼
                              [ Pillar 4 ]
                      Master Confluence Decision Engine
               (Scores 0-100%, Filters for A+ Setups Only)
                                    │
                                    ├───> [ Prop Firm Safety Shield ]
                                    │     - Max 1-2 trades/day hard cap
                                    │     - Auto Lot Size by Account Balance %
                                    │     - Daily Drawdown Circuit Breaker
                                    │
                                    ├───> [ Telegram Alert Dispatcher ]
                                    │     - Instant formatted setup
                                    │     - Pair, Direction, Entry, SL, TP1, TP2, TP3, Lot
                                    │
                                    ├───> [ 3-Tranche Scale-Out Execution ]
                                    │     - Tranche 1: Closed at TP1 (Locks base profit)
                                    │     - Tranche 2: Closed at TP2 (Extended profit)
                                    │     - Tranche 3: Runner with Auto Break-Even (BE) -> TP3/TP4
                                    │
                                    ▼
                 [ Windows VPS Terminal Dashboard ]
        (FastAPI Engine + TradingView Lightweight Charts + Desktop Shell)
```

### Detailed Breakdown of the Modules:

#### Layer 0: Hermes AI Macro Research & Geopolitical Sentinel
- **Targeted Market-Moving Intelligence:** Continuously monitors financial wirefeeds, central bank communications, and specialized forex blogs (FXStreet, Reuters Finance, DailyFX, FinancialJuice). Strictly filters for events that have direct or indirect structural impact on currency liquidity, inflation, interest rates, or safe-haven flows.
- **Autonomous Hermes Research Agent (Nous Hermes 3):**
  - Synthesizes complex articles and geopolitical tensions (e.g. US-Iran relations, Middle East escalations, OPEC decisions, tech sector shocks like DeepSeek vs. chipmakers).
  - Performs **Causal Impact Analysis**: Determines *how* and *why* a specific event alters supply/demand for `EURUSD`, `GBPUSD`, `XAUUSD` (Gold), and `XAGUSD` (Silver).
  - Outputs a structured **Market Impact Dossier**: Directional Bias (-100 to +100), Impact Severity (Low/Medium/High/Extreme), and Key Market Drivers.
- **Economic Calendar News Guard (ForexFactory):** Auto-fetches high-impact (Red Folder) releases (CPI, NFP, FOMC, Rate decisions). Freezes trading 15-30 minutes before and after the release to ensure 100% compliance with FTMO/FundingPips news rules.

#### Layer 1: Technical Confluence Pillars (The Hybrid Model)
1. **Pillar 1: Smart Money Concepts (SMC / ICT)**
   - Identifies institutional Order Blocks (OB), Fair Value Gaps (FVG), Break of Structure (BOS), and Liquidity Sweeps on M15.
   - **Asian Range Liquidity & Judas Swing Detector:** Calculates Asian Session High/Low (00:00-08:00 GMT) and flags London/NY false-breakout sweeps.
2. **Pillar 2: Classical Price Action & Chart Patterns**
   - Detects key Support/Resistance horizontal zones, dynamic trendlines, and high-probability patterns (Double Tops/Bottoms, Quasimodo / QM, Head & Shoulders, Flags).
   - Validates candlestick confirmation (Pinbars, Engulfing).
3. **Pillar 3: Multi-Timeframe Alignment & SMT Divergence (MTF & Intermarket)**
   - Pulls Daily, 4H, and 1H candles to map macro market structure and directional bias.
   - **SMT Divergence Engine (Intermarket Correlation):**
     - Correlates `EURUSD` vs `GBPUSD` vs `DXY`.
     - Correlates `XAUUSD` (Gold) vs `XAGUSD` (Silver).
     - Identifies institutional liquidity traps when one asset breaks a high/low but the correlated twin fails to confirm.
   - Strictly vetoes any M15 trade opposing the Higher Timeframe trend.

#### Pillar 4: Master Decision & Execution Guardian
- Requires simultaneous confluence: Macro Sentiment (Layer 0) + SMC (Pillar 1) + Price Action (Pillar 2) + MTF/SMT (Pillar 3).
- **Execution Safeguards:**
  - **Dynamic Spread & Slippage Guard:** Live spread verification via MT5 `symbol_info`. Cancels execution if spread exceeds max threshold (e.g., > 2.5 pips on Gold, > 1.2 pips on EURUSD).
  - **Weekend & Dead-Hours Shield:** Warns/closes open day trades 1 hour before Friday market close (protects Prop Firm accounts against weekend gaps). Disallows trades during dead hours.
- **Dynamic 3-Tranche Trade Management & Adaptive Trailing:**
  - Upon signal trigger, enters 3 equal sub-positions (e.g. 3x 0.01 lot for $1,000 balance):
    - **Position 1 (TP1):** Targets 1:1 or 1:1.5 R:R. Once hit, locks in early gain.
    - **Position 2 (TP2):** Targets 1:2.5 R:R.
    - **Position 3 (Runner):** Stop Loss instantly updated to **Break-Even (BE + 1 pip spread buffer)**.
    - **Adaptive Trailing Engine:** Once TP2 is achieved, trailing stop shifts behind recent M15 swing structures/ATR, locking 50-70% of peak profits until TP3/TP4.
- **Visual Telegram Journal:**
  - Captures and sends an instant high-resolution PNG chart screenshot with marked Entry, SL, TP, and confluence reasoning to Telegram on every signal, TP hit, and trade closure.

---

## 5. Technical Specifications & Environment
- **Operating Environment:** Windows 10/11 / Windows Server VPS (runs 24/5 headless or GUI mode).
- **Core Backend:** Python 3.10+ with `MetaTrader5` library.
- **Frontend / Visual Interface:** Modern HTML5/React with **TradingView Lightweight Charts** displayed inside a lightweight desktop window (PyWebView / Chromium Shell).
- **Alert System:** Telegram Bot API (webhook/polling with rich formatted markdown and charts).
- **Database / Cache:** SQLite / Local JSON for logging trade history, performance statistics, and user settings.

---

## 6. User Interface & Layout Architecture (Dashboard Wireframe)

```
┌────────────────────────────────────────────────────────────────────────┐
│  THE LIFE FOREX CONFLUENCE TERMINAL  ● MT5: Connected (FTMO)  [21:45]   │
├──────────────────────────────────────┬─────────────────────────────────┤
│  CHART VIEW (TradingView Engine)     │  LIVE CONFLUENCE RADAR          │
│  Pair: [ XAUUSD (Gold) ▼ ] [ M15 ▼ ] │  -----------------------------  │
│                                      │  Overall Confluence: 88% [A+]   │
│  [=================================] │                                 │
│  [  Candlestick Chart with         ] │  1. Macro News Bias: +75 (Bull) │
│  [  Order Blocks & FVG highlighted ] │     - ME tensions safe-haven    │
│  [  Dynamic S/R & Trendline        ] │  2. SMC / ICT: Bullish FVG+OB   │
│  [                                 ] │  3. Classical: Double Bottom    │
│  [  Entry: 2742.50                 ] │  4. MTF Bias (H4/D1): Bullish   │
│  [  SL:    2738.00                 ] │  -----------------------------  │
│  [  TP1:   2747.00 | TP2: 2753.50  ] │  NEWS GUARD: [ ACTIVE - CLEAR ] │
│  [  TP3:   2762.00 (Runner / BE)   ] │  Next Red Folder: NFP in 4h 15m │
├──────────────────────────────────────┴─────────────────────────────────┤
│  ACCOUNT & EXECUTION CONTROL                                           │
│  Balance: $1,000 | Risk: 1% ($10) | Lot Size: 3x 0.01                  │
│  Today's Trades: [ 1 / 2 ] | Daily PnL: +$18.50 | Drawdown: 0.0%       │
│  [ ONE-CLICK EXECUTE ] [ SEND TELEGRAM ALERT ] [ AUTO-EXECUTE: ON ]    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Step-by-Step Development Roadmap
- **Phase 1: MT5 Bridge & Core Engine**
  - Connect Python to MT5 terminal (Exness / FTMO / FundingPips).
  - Live tick/bar data streamer for `EURUSD`, `GBPUSD`, `XAUUSD`, `XAGUSD`.
  - Dynamic lot sizing engine respecting broker contract specifications.
- **Phase 2: Layer 0 - Macro News & Economic Calendar News Guard**
  - Scraper for ForexFactory / Economic Calendar (auto-freezing trades during Red Folders).
  - RSS & Geopolitical news analyzer providing live sentiment bias scores.
- **Phase 3: The Technical Confluence Engine (Pillars 1, 2 & 3)**
  - Algorithmic detectors for SMC (Order Blocks, FVGs, Sweeps, BOS).
  - Algorithmic detectors for Classical Price Action (Support/Resistance, Patterns).
  - Multi-Timeframe (MTF) trend aligner.
- **Phase 4: Pillar 4 Confluence Synthesizer & 3-Tranche Manager**
  - Score generator (0-100%).
  - Multi-tranche trade management: TP1 lock, TP2 lock, TP3 runner with automated Break-Even (BE).
- **Phase 5: Telegram Dispatcher & Interactive Desktop UI**
  - Telegram bot setup sending real-time charts and signal alerts.
  - Modern desktop interface with TradingView Lightweight Charts running on Windows/VPS.
- **Phase 6: Backtesting Engine & Rigorous Verification**
  - Bar-replay simulator to test historical performance and edge.




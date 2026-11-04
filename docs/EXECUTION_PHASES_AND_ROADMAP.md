# Master Execution Phases & Step-by-Step Implementation Roadmap

> **Project Name:** The Life Forex Confluence Terminal  
> **Document Version:** 1.0.0  
> **Protocol Rule:** When the user commands `"next phase"`, the assistant executes the corresponding phase's deliverables, runs automated empirical verification tests, documents the outcome, and reports completion before advancing.

---

## 🗺️ Master Phase Overview Matrix

| Phase | Phase Title | Core Deliverables | Verification Milestone |
|---|---|---|---|
| **Phase 1** | **Environment Setup & MT5 Core Bridge** | Python 3.11, `venv`, MT5 IPC client, dynamic lot calculator | **COMPLETED & VERIFIED** (Passes lot math & MT5 IPC) |
| **Phase 2** | **Layer 0: Hermes AI Research & News Guard** | ForexFactory Red Folder parser, RSS aggregator, Hermes AI impact agent | **COMPLETED & VERIFIED** (Passes live countdown, VETO & sentiment) |
| **Phase 3** | **Hybrid Technical Intelligence (Pillars 1, 2 & 3)** | SMC (OB, FVG, Asian Range sweep), Patterns (S/R, QM, Dbl Btm), MTF & SMT | Multi-timeframe trend alignment & cross-market divergence tests |
| **Phase 4** | **Pillar 4 Confluence Arbiter & Execution Engine** | Confluence 0-100 scoring, Veto hierarchy, 3-Tranche Scaling & Auto-BE | Simulated 3-part order dispatch, TP1/TP2 scaling, and BE shifting |
| **Phase 5** | **Database Persistence & Telegram Dispatcher** | SQLite schema, Telegram Bot API, Matplotlib chart snapshot generator | Clean database CRUD tests & Telegram snapshot test dispatch |
| **Phase 6** | **Frontend Desktop Dashboard (TradingView Core)** | React + Tailwind, TV Lightweight Charts (v5.2.1), WebSocket API, Desktop Shell | 60 FPS interactive candlestick chart, live radar & execution deck |
| **Phase 7** | **Strategy Evolution Arena (Multi-Curve Fan)** | Background backtest worker, Strategy DNA mutator, Evolution Fan UI | Multi-line equity fan visual rendering & one-click promotion |
| **Phase 8** | **Full Integration, Bar-Replay & Dry-Run** | Bar-replay controller, Prop Firm safety verification, End-to-End Dry Run | Full simulated trading session with zero errors & zero memory leaks |

---

## 📋 Detailed Phase-by-Phase Execution Plan

### 🚀 Phase 1: Environment Setup & MT5 Core Bridge [STATUS: COMPLETED & 100% VERIFIED]
- **Status:** **DONE [x]** (Python 3.11.18 installed, 39 quant libraries installed, `strategy_dna.json`, `symbol_manager.py`, `mt5_client.py`, `market_feed.py` active, tests passed).
- **Goal:** Establish a bulletproof runtime environment and low-latency Python IPC connection to MetaTrader 5.
- **Deliverables:**
  - `requirements.txt`: Python package dependencies (`MetaTrader5`, `fastapi`, `uvicorn`, `pandas`, `numpy`, `httpx`, `feedparser`, `vaderSentiment`, `matplotlib`).
  - `backend/bridge/mt5_client.py`: Auto-discovers `C:\Program Files\MetaTrader 5\terminal64.exe`, initializes connection, monitors heartbeat.
  - `backend/bridge/symbol_manager.py`: Parses symbol specifications (contract size, tick size, pip value) to compute exact dynamic lot sizes for currencies and metals (`XAUUSD`, `XAGUSD`).
- **Empirical Verification:** Run `tests/test_mt5_bridge.py` to stream live bid/ask ticks, pull last 100 M15 bars for all 4 pairs, and calculate dynamic lot sizes for a \$1,000 account.

---

### 📰 Phase 2: Layer 0 - Hermes AI Research & News Guard [STATUS: COMPLETED & 100% VERIFIED]
- **Status:** **DONE [x]** (`news_guard.py`, `rss_fetcher.py`, `hermes_agent.py` active, live ForexFactory calendar tested, Red Folder countdowns active, simulated 15m VETO verified, tests passed).
- **Goal:** Ingest market-moving forex news and enforce the 15–30 min Red Folder news freeze.
- **Deliverables:**
  - `backend/modules/layer0_macro/news_guard.py`: Asynchronously fetches ForexFactory JSON, tracks countdowns to upcoming Red Folder events, triggers `NEWS_VETO`.
  - `backend/modules/layer0_macro/rss_fetcher.py`: Continuously pulls targeted headlines from Reuters Finance, FXStreet, and DailyFX.
  - `backend/modules/layer0_macro/hermes_agent.py`: Analyzes causal impact of breaking news on USD, Gold, and Euro; produces the **Market Impact Dossier** and Asset Bias Score (-100 to +100).
- **Empirical Verification:** Run `tests/test_news_guard.py` to verify accurate countdown timers, veto flag activation, and real-time news sentiment scoring.

---

### 📊 Phase 3: Hybrid Technical Intelligence (Pillars 1, 2 & 3) [COMPLETED & 100% VERIFIED]
- **Goal:** Build the algorithmic pattern, liquidity, and intermarket correlation detectors.
- **Deliverables:**
  - `backend/modules/pillar1_smc/`:
    - `fvg_detector.py` (Fair Value Gaps detection & mitigation tracking)
    - `order_block.py` (Institutional Order Blocks detection)
    - `asian_range.py` (Asian Session High/Low & Judas Swing sweep detection)
  - `backend/modules/pillar2_patterns/`:
    - `support_resistance.py` (Pivot clustering & horizontal S/R)
    - `chart_patterns.py` (Double Tops/Bottoms, Quasimodo, Pinbars/Engulfing rejection triggers)
  - `backend/modules/pillar3_mtf_smt/`:
    - `mtf_aligner.py` (Daily/H4 EMA 50/200 trend alignment)
    - `smt_divergence.py` (Cross-asset correlation: EUR/GBP and Gold/Silver accumulation/distribution traps)
  - `backend/modules/technical_analyzer.py`: Unified technical pipeline combining Pillars 1, 2, and 3.
- **Empirical Verification:** Run `tests/test_technical_engine.py` - passed with exit code 0 (FVG, OB, Judas Sweep, Pinbar, S/R, MTF Bullish, and SMT Divergence +15 pts verified).

---

### ⚖️ Phase 4: Pillar 4 Confluence Arbiter & Execution Engine [COMPLETED & 100% VERIFIED]
- **Goal:** Unify all data points into a single Confluence Score, enforce Veto rules, and manage the 3-Tranche Scaling strategy.
- **Deliverables:**
  - `backend/modules/pillar4_master/confluence_engine.py`: Weighted consensus calculator ($0-100\%$), Grade A+/A assigner, and strict 5-tier Veto Arbiter (News, Spread, Daily Cap, MTF counter-trend, Hermes macro).
  - `backend/modules/pillar4_master/order_manager.py`: 3-tranche lot splitter (T1=TP1, T2=TP2, T3=Runner), entry/SL/TP generator, and automated Break-Even (BE + 1 pip spread buffer) updater upon TP1 hit.
  - `backend/modules/pillar4_master/trailing_stop.py`: Adaptive trailing stop based on recent M15 swing structures/ATR ratcheting forward in profit.
  - `backend/config/strategy_dna.json`: Living Strategy DNA configuration file with dynamic weights & parameters.
- **Empirical Verification:** Run `tests/test_confluence_execution.py` - passed with exit code 0 (Score 88.4 Grade A+, 5/5 Vetos verified, 3-tranche scaling lifecycle from TP1 lock to auto Break-Even to runner exit banking +$281 on $100 risk).

---

### 💾 Phase 5: Database Persistence & 2-Way Telegram Mobile Command Center
- **Goal:** Store all trading and telemetry data locally and configure full 2-way interactive Telegram mobile alerts and remote MT5 commands (refer to `docs/TELEGRAM_INTELLIGENCE_AND_DISPATCH_SPEC.md`).
- **Deliverables:**
  - `backend/database/models.py` & `db_manager.py`: SQLite database (`terminal.db`) with tables: `trade_orders`, `confluence_telemetry`, `rsi_evolution_history`.
  - `backend/alerts/telegram_bot.py`: Full 2-Way Asynchronous Telegram Bot client:
    - *Outbound Alerts:* Grade A+ setups with attached PNG chart snapshots, TP1/TP2 hit notices, Auto Break-Even alerts, Hermes macro flashes, and session briefings.
    - *Inbound Commands:* Interactive mobile remote responding to `/status`, `/positions`, `/news`, `/briefing`, `/pause`, `/resume`, and emergency `/closeall`.
  - `backend/alerts/chart_snapshotter.py`: Generates high-res PNG chart screenshots with marked entry, SL, TP, and confluence reasoning.
- **Empirical Verification:** Run `tests/test_persistence_and_alerts.py` to verify SQLite CRUD performance, dispatch a sample chart alert, and test inbound command responses.

---

### 🖥️ Phase 6: Frontend Desktop Dashboard (TradingView Core)
- **Goal:** Build the sleek, 60 FPS institutional dark-themed desktop terminal.
- **Deliverables:**
  - `frontend/`: React 18 + Tailwind CSS + TradingView Lightweight Charts (v5.2.1).
  - Components: `ChartView.jsx`, `WatchlistBar.jsx`, `ConfluenceRadar.jsx`, `HermesDossier.jsx`, `ExecutionDeck.jsx`.
  - `backend/app.py`: FastAPI server streaming ticks and confluence scores over WebSockets.
  - `run_terminal.bat`: One-click Windows desktop launcher using Microsoft Edge WebView2.
- **Empirical Verification:** Launch the application; verify 60 FPS candlestick rendering, real-time tick streaming, and button interactions.

---

### 🧬 Phase 7: Strategy Evolution Arena (Multi-Curve Fan)
- **Goal:** Implement the 24/7 background strategy backtesting tournament and the multi-line equity fan visualizer.
- **Deliverables:**
  - `backend/optimization/background_lab.py`: Non-blocking background worker thread continuously testing parameter mutations on MT5 data.
  - `backend/optimization/genetic_mutator.py`: Generates strategy variations.
  - `frontend/src/components/EvolutionArena.jsx`: Multi-Line Equity Fan Chart and Tournament Leaderboard with one-click `[ PROMOTE TO LIVE ]`.
- **Empirical Verification:** Verify background simulations render multiple colored equity curves branching outward on the Evolution screen without lagging the UI.

---

### 🏁 Phase 8: Full Integration, Bar-Replay & Dry-Run
- **Goal:** Perform deep stress-testing, bar-replay simulation, and finalize user documentation.
- **Deliverables:**
  - `backend/backtest/bar_replay.py`: Interactive historical bar-by-bar simulator.
  - Prop Firm Safety Shield verification (verifies daily trade caps, drawdown limits, and Friday weekend holding alerts).
  - Finalized `docs/USER_OPERATION_MANUAL.md`.
- **Empirical Verification:** A comprehensive 2-hour simulated live trading session verifying end-to-end stability with zero memory leaks.


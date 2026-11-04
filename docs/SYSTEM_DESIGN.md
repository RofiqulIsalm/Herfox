# System Design Document (SDD) - The Life Forex Confluence Terminal

> **Document Version:** 1.0.0  
> **System Architecture:** Local-First, Event-Driven Multi-Tier Micro-Modular Architecture  
> **Target OS:** Windows 10/11 & Windows Server (VPS)  
> **Inter-Process Communication:** Windows Named Pipes / Local IPC & High-Speed WebSockets

---

## 1. System Architecture Overview

The system is engineered as an institutional-grade, low-latency, event-driven trading workstation. It decouples high-speed data ingestion and quantitative computation from the user interface to ensure zero-lag execution.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER (UI/UX)                             │
│       React 18 + Tailwind CSS + TradingView Lightweight Charts (v5.2.1)         │
│          Hosted in Native Windows Desktop Shell (Microsoft Edge WebView2)       │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ High-Speed WebSockets (JSON / Events)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION & API GATEWAY                              │
│             FastAPI Asynchronous Web Framework (Localhost:8765)                 │
├────────────────────────────────────────┬────────────────────────────────────────┤
│ REST Endpoints:                        │ WebSocket Channels:                    │
│ - `/api/v1/orders/execute`             │ - `/ws/market-stream` (Realtime ticks) │
│ - `/api/v1/settings/risk`              │ - `/ws/confluence-radar` (Live scores) │
│ - `/api/v1/hermes/briefing`            │ - `/ws/news-guard` (Countdown/Vetos)   │
└────────────────────────────────────────┼────────────────────────────────────────┘
                                         │ Internal Event Bus (Asyncio Pub/Sub)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      QUANTITATIVE & AI INTELLIGENCE CORE                        │
├─────────────────────────┬───────────────────────────┬───────────────────────────┤
│ Layer 0: Macro Sentinel │ Layer 1: Technical Scout  │ Pillar 4: Master Arbiter  │
│ - Hermes Research Agent │ - Pillar 1: SMC / ICT     │ - Confluence Synthesizer  │
│ - ForexFactory NewsGuard│ - Pillar 2: S/R & Patterns│ - Veto Power Arbiter      │
│ - RSS Wire Aggregator   │ - Pillar 3: MTF & SMT     │ - 3-Tranche Risk Allocator│
└─────────────────────────┴─────────────┬─────────────┴───────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         EXECUTION & PERSISTENCE LAYER                           │
├───────────────────────────────────────┬─────────────────────────────────────────┤
│ MT5 Python Bridge (IPC)               │ SQLite Local Database (`terminal.db`)   │
│ - Sub-5ms tick listener               │ - Table: `trade_history`                │
│ - Native order dispatcher             │ - Table: `telemetry_logs`               │
│ - Real-time equity/margin syncer      │ - Table: `rsi_evolution_history`        │
└───────────────────────────────────────┴─────────────────────────────────────────┘
```

---

## 2. Core Subsystems & Interfaces

### 2.1 Broker IPC Gateway (`backend/bridge/`)
- **`mt5_client.py`:** Inter-Process Communication (IPC) bridge to `terminal64.exe` via MetaQuotes official 64-bit C-extension.
- **Connection Lifecycle:**
  - Auto-discovers local MT5 path (`C:\Program Files\MetaTrader 5\terminal64.exe`).
  - Implements a heartbeat watchdog (checks connection every 1000ms; auto-reconnects on disconnection).
- **Symbol Manager (`symbol_manager.py`):**
  - Queries broker `symbol_info` for exact tick size, contract size, and spread.
  - Normalizes price calculations across standard 4-decimal currencies (`EURUSD`, `GBPUSD`) and precious metals (`XAUUSD` = \$0.10 pip, `XAGUSD` = \$0.01 pip).

### 2.2 Layer 0: Hermes AI Macro Research & News Guard
- **ForexFactory News Guard (`backend/modules/layer0_macro/news_guard.py`):**
  - Fetches `https://nfs.faireconomy.media/ff_calendar_thisweek.json` hourly.
  - Caches events in memory; continuously computes seconds until next Red Folder event.
  - If `0 < RemainingTime <= 1800s (30m)`: Issues a `NEWS_VETO` packet on the Event Bus.
- **Hermes Macro Analyst (`backend/modules/layer0_macro/hermes_agent.py`):**
  - Ingests targeted feeds from Reuters Financial, FXStreet, DailyFX, and Central Bank statements.
  - Runs local Nous-Hermes 3 inference via Ollama / GGUF.
  - Outputs a structured payload:
    ```json
    {
      "asset": "XAUUSD",
      "bias_score": 75,
      "severity": "HIGH",
      "rationale": "Escalating geopolitical risk in the Middle East driving safe-haven gold accumulation.",
      "timestamp": "2026-11-03T16:15:00Z"
    }
    ```

### 2.3 Layer 1: Technical Analysis Engines
- **Pillar 1: SMC / ICT Engine (`backend/modules/pillar1_smc/`):**
  - Identifies Fair Value Gaps (3-candle price imbalance).
  - Identifies Bullish/Bearish Order Blocks (last opposing candle before strong displacement).
  - Asian Range Tracker: Stores Asian High/Low (00:00 - 08:00 GMT); detects sweeps during London/NY open.
- **Pillar 2: Classical Price Action (`backend/modules/pillar2_patterns/`):**
  - S/R Clusters: Uses Kernel Density Estimation (KDE) on swing highs/lows.
  - Patterns: Algorithmic detection of Double Tops/Bottoms, Quasimodo (QM), and Pinbar/Engulfing candles.
- **Pillar 3: MTF & SMT Divergence (`backend/modules/pillar3_mtf_smt/`):**
  - Multi-Timeframe Matrix: Maps Daily and H4 trend bias via 50/200 EMA + Market Structure.
  - SMT Engine: Compares normalized highs/lows between `EURUSD` vs `GBPUSD` and `XAUUSD` vs `XAGUSD`.

### 2.4 Pillar 4: Master Confluence Decision & Execution Engine
- Evaluates aggregate score:
  $$\text{Score} = (0.20 \times \text{Macro}) + (0.30 \times \text{SMC}) + (0.20 \times \text{Patterns}) + (0.15 \times \text{MTF}) + (0.15 \times \text{SMT})$$
- Enforces strict **Veto Hierarchy** (News Veto > Spread Veto > HTF Trend Mismatch Veto > Daily Drawdown Veto).
- Upon trigger ($\ge 85\%$), executes **3-Tranche Scaling Algorithm**:
  - Tranche 1: Exit at TP1 (Locks early profit).
  - Tranche 2: Exit at TP2 (Extended target).
  - Tranche 3: Move SL to Break-Even (BE + 1 pip spread buffer); trail behind recent M15 swing lows/highs for TP3/TP4.

### 2.5 Telegram Dispatcher & Visual Snapshot Engine
- Generates high-resolution PNG chart with marked entry, SL, TP, and confluence reasoning via `matplotlib`.
- Dispatches formatted alert to Telegram channel via asynchronous Telegram Bot HTTP API.

### 2.6 Recursive Self-Improvement (RSI) Engine
- Telemetry Logger: Logs every signal vector into `confluence_telemetry`.
- Post-Mortem Analyzer: Evaluates losing trades on weekend; runs Bayesian parameter tuning.
- Walk-Forward Sandbox: Simulates candidate mutation on unseen 30% MT5 historical data; executes 1,000-run Monte Carlo simulation.
- Champion-Challenger: Promotes Challenger only if expectancy improves $>10\%$ without increasing drawdown.

---

## 3. Database Schema (SQLite: `terminal.db`)

```sql
-- Historical Trade Records
CREATE TABLE trade_orders (
    ticket_id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL, -- BUY / SELL
    tranche_number INTEGER NOT NULL, -- 1, 2, or 3
    lot_size REAL NOT NULL,
    entry_price REAL NOT NULL,
    sl_price REAL NOT NULL,
    tp_price REAL NOT NULL,
    close_price REAL,
    pnl_dollars REAL,
    pnl_pips REAL,
    open_time DATETIME NOT NULL,
    close_time DATETIME,
    exit_reason TEXT -- TP1, TP2, TP3, BE, SL, MANUAL
);

-- High-Dimensional Signal Telemetry for RSI
CREATE TABLE confluence_telemetry (
    signal_id TEXT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT DEFAULT 'M15',
    macro_score REAL,
    smc_score REAL,
    pattern_score REAL,
    mtf_bias TEXT,
    smt_divergence INTEGER, -- 1 for True, 0 for False
    confluence_total REAL,
    trade_grade TEXT, -- A+, A, B
    outcome TEXT -- PROFIT, LOSS, BREAK_EVEN, VETOED
);

-- Champion-Challenger Evolution Audit
CREATE TABLE rsi_evolution_history (
    cycle_id TEXT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    symbol TEXT NOT NULL,
    previous_win_rate REAL,
    new_win_rate REAL,
    max_drawdown REAL,
    mutation_details TEXT,
    promoted INTEGER -- 1 for Promoted to Champion, 0 for Discarded
);
```

---

## 4. Low-Latency Data Flow Sequence

```
MT5 Terminal (Tick) ──> mt5_client.py ──> Market Data Buffer ──> Event Bus
                                                                    │
      ┌─────────────────────────────────────────────────────────────┤
      ▼                                                             ▼
Layer 0 News Check                                            Technical Analysis
(ForexFactory / Hermes)                                        (SMC, Patterns, MTF, SMT)
      │                                                             │
      └──────────────────────────────┬──────────────────────────────┘
                                     ▼
                          Pillar 4 Confluence Arbiter
                                     │
                   [ Does Confluence Score >= 85%? ]
                                     │
                    ├─── NO  ──> Discard & Log to SQLite
                    └─── YES ──> Check Veto Rules (News, Spread, Trend, Drawdown)
                                     │
                                     ├─── VETO ACTIVE ──> Halt with Warning
                                     └─── ALL CLEAR   ──> 1. Calculate Exact Lots (3 Tranches)
                                                          2. Dispatch Orders to MT5 API
                                                          3. Send Chart Snapshot to Telegram
                                                          4. Stream Trade to Desktop UI via WS
```


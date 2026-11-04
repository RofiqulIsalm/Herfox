# 🦅 The Life - Forex Confluence Terminal

> **Institutional-Grade Quantitative Trading System & Recursive Self-Improvement Arena**  
> *Engineered to eliminate retail reliance on expensive charting tools and deliver high-confluence M15 execution on EURUSD, GBPUSD, XAUUSD (Gold), and XAGUSD (Silver).*

---

## 🌟 System Architecture & Core Pillars

### 1. Layer 0: Macro Intelligence & Red Folder News Guard
- **ForexFactory News Guard:** Real-time JSON calendar feed scraper enforcing strict 15–30 minute pre/post release execution freezes (`NEWS_VETO`) around high-impact events (NFP, CPI, FOMC, Rate decisions).
- **Hermes AI Macro Agent:** Financial headline parser and sentiment analyzer computing dynamic Asset Bias Scores (-100 to +100) and directional macro vetoes.

### 2. Pillar 1: Smart Money Concepts (SMC / ICT)
- **Fair Value Gaps (FVG):** Imbalance detection and mitigation tracking.
- **Institutional Order Blocks (OB):** High-volume displacement base detection and zone testing.
- **Asian Session Liquidity & Judas Swing:** Automated 00:00–08:00 GMT high/low boundary tracking with false breakout sweep triggers.

### 3. Pillar 2: Classical Price Action
- **Horizontal S/R Clusters:** Multi-touch historical pivot clustering.
- **Rejection Triggers:** High-probability Pinbars, Engulfing bars, and Double Bottom/Top structures.

### 4. Pillar 3: Multi-Timeframe & SMT Divergence
- **MTF Trend Alignment:** Daily & H4 EMA 50/200 trend alignment.
- **SMT Divergence Engine:** Intermarket non-confirmation between correlated pairs (`EURUSD` vs `GBPUSD` and `XAUUSD` vs `XAGUSD`) uncovering smart money accumulation and distribution traps.

### 5. Pillar 4: Master Confluence Arbiter & Execution Engine
- **Consensus Scoring:** Weighted 0–100% scoring system requiring $\ge 80\%$ for `GRADE_A_PLUS` qualification.
- **5-Tier Veto Hierarchy:** Immediate zero-leakage vetoes for News Blackouts, Spread Spikes, Daily Cap (max 2 trades/day), MTF Counter-Trend, and Macro Sentiment opposition.
- **3-Tranche Scaling Execution:**
  - **Tranche 1 (TP1):** Quick profit lock at 1.0R / 1.5R.
  - **Automated Break-Even:** Instantly shifts Stop Loss of Tranches 2 & 3 to **Entry + 1.0 pip spread buffer** upon TP1 hit.
  - **Tranche 2 (TP2):** Extended target at 2.5R.
  - **Tranche 3 (Runner):** Adaptive ATR/Swing trailing stop ratcheting forward in profit.

### 6. Pillar 5: Persistence & 2-Way Mobile Command Center (In Progress)
- **Local SQLite Persistence:** `terminal.db` stores trade orders, confluence telemetry, and strategy evolution history.
- **2-Way Telegram Remote:** High-resolution chart snapshot alerts and interactive commands (`/status`, `/positions`, `/news`, `/briefing`, `/pause`, `/resume`, `/closeall`).

### 7. Pillar 6 & 7: UI Desktop & Evolution Arena (Upcoming)
- **React 18 + TradingView Lightweight Charts (v5.2.1):** 60 FPS deep OLED black desktop interface.
- **Recursive Self-Improvement Arena:** 24/7 background parameter mutation tournament rendering a real-time Multi-Line Equity Fan Chart with one-click live promotion.

---

## 📂 Repository Structure

```
├── backend/
│   ├── bridge/               # MT5 IPC Client, Market Feed Streamer, Symbol Manager
│   ├── config/               # strategy_dna.json (living strategy configuration)
│   ├── database/             # SQLite DB models & manager (Phase 5)
│   ├── modules/
│   │   ├── layer0_macro/     # ForexFactory News Guard, RSS Fetcher, Hermes AI
│   │   ├── pillar1_smc/      # FVG, Order Blocks, Asian Range Judas Sweeps
│   │   ├── pillar2_patterns/ # S/R Clusters, Pinbar & Pattern Detectors
│   │   ├── pillar3_mtf_smt/  # MTF Aligner & SMT Intermarket Divergence
│   │   ├── pillar4_master/   # Confluence Engine, Order Manager, Trailing Stop
│   │   └── technical_analyzer.py
│   └── alerts/               # Telegram Bot & Chart Snapshotter (Phase 5)
├── docs/                     # Full PRD, System Design, Roadmap, and Discovery Logs
├── tests/                    # 100% Empirical Verification Test Suite
├── requirements.txt          # Python dependencies
└── README.md
```

---

## 🛠️ Installation & Verification

1. **Python Environment:**
   ```bash
   uv venv --python 3.11 .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Verification Test Suites:**
   ```bash
   # Phase 1: MT5 Bridge & Symbol Manager
   .\.venv\Scripts\python.exe tests/test_mt5_bridge.py

   # Phase 2: Layer 0 Macro & News Guard
   .\.venv\Scripts\python.exe tests/test_news_guard.py

   # Phase 3: Hybrid Technical Intelligence (Pillars 1, 2 & 3)
   .\.venv\Scripts\python.exe tests/test_technical_engine.py

   # Phase 4: Master Confluence Arbiter & 3-Tranche Scaling
   .\.venv\Scripts\python.exe tests/test_confluence_execution.py
   ```

---

## 📜 License
Proprietary Quantitative Trading Infrastructure - Built for local-first desktop deployment.

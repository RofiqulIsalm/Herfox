# Tech Stack, Dependencies & Resource Sourcing Plan

> **Document Version:** 1.0.0  
> **Target OS:** Windows 10/11 & Windows Server (VPS)  
> **Cost Assessment:** 100% Free / Open Source (Zero paid third-party subscriptions)

---

## 1. System Components & Sourcing Matrix

| Component | Technology / Library | Source / Origin | Cost | Role & Purpose |
|---|---|---|---|---|
| **Core Runtime (Backend)** | Python 3.11 / 3.12 | `winget install Python.Python.3.11` | Free | Core execution engine, MT5 IPC bridge, quantitative analysis. |
| **Broker Bridge & FX Data** | `MetaTrader5` (Python package) | PyPI (`pip install MetaTrader5`) | Free | Direct link to local `terminal64.exe` (Exness, FTMO, FundingPips). Live ticks, M15/H1/H4 bars, balance, orders. |
| **Data Science & Quant Math** | `pandas`, `numpy`, `scipy` | PyPI (`pip install pandas numpy scipy`) | Free | High-speed vectorized OHLCV processing, Swing High/Low detection, ATR, volume profile. |
| **Interactive Chart Engine** | **TradingView Lightweight Charts** (v4.x) | Official TradingView Open Source (npm / standalone bundle) | Free (Apache 2.0) | 60 FPS interactive candlestick chart, infinite indicators, drawing layers, zero subscription fees. |
| **Frontend UI & Dashboard** | React + Vite + Tailwind CSS (Dark Mode) | npm (`vite`, `tailwindcss`, `lucide-react`) | Free (MIT) | Modern, sleek institutional dark-themed terminal UI. |
| **Desktop Window Shell** | `pywebview` / Windows WebView2 | PyPI (`pip install pywebview`) | Free | Wraps the UI into a native Windows Desktop App (`.exe` ready) using built-in Windows WebView2. |
| **High-Impact News Guard** | ForexFactory JSON/XML Feed | `nfs.faireconomy.media/ff_calendar_thisweek.json` | Free | Auto-detects upcoming Red Folder events (CPI, NFP, FOMC) with live countdown timers. |
| **Global Macro & News Stream** | `feedparser` + Financial RSS | Reuters, FXStreet, Bloomberg, Google News RSS | Free | Ingests real-time geopolitical updates (Middle East, Central Banks, Tech shocks). |
| **NLP Sentiment Analyzer** | `vaderSentiment` / HuggingFace `FinBERT` | PyPI (`pip install vaderSentiment`) | Free | Converts raw news headlines into an Asset Bias Score (-100 to +100). |
| **Hermes AI Research Agent** | **Nous Hermes 3** (Llama-3.1 8B / 3B) | Ollama (Local offline) / HuggingFace | Free / Open-Source | Autonomous deep research on market-moving forex news, financial blogs, and causal impact modeling. |
| **Telegram Alert Dispatcher** | Telegram Bot API (`httpx`) | Telegram @BotFather | Free | Instant formatted trade alerts with Pair, Entry, SL, TP1-3, and auto-lot calculation. |
| **Visual Chart Screenshotter** | Headless Canvas Snapshot / `mplfinance` | PyPI (`pip install matplotlib mplfinance`) | Free | Captures high-res PNG chart snapshots of setups and sends them directly to Telegram. |
| **Local Database & Storage** | SQLite (`sqlite3`) | Built-in Python Standard Library | Free | Persistent storage for trade history, daily PnL, journal records, and user settings. |

---

## 2. Where & How Each Dependency Is Obtained

### A. Backend & Broker Infrastructure
1. **Python 3.11 Installation:**
   - Command: `winget install Python.Python.3.11 --silent`
   - Configures local python interpreter and pip on Windows.
2. **MetaTrader 5 Bridge:**
   - Already present on user's machine at `C:\Program Files\MetaTrader 5\terminal64.exe`.
   - The Python library connects via local Named Pipes/IPC with ultra-low latency (<5ms).

### B. Charting & Frontend Infrastructure
1. **TradingView Lightweight Charts:**
   - Downloaded from the official TradingView open-source repository.
   - Embeds directly into our frontend without any external internet dependency or API keys.
2. **Node.js Environment:**
   - Already verified installed on user's system (`v24.19.0`).
   - We will use Vite to compile the UI assets into a standalone static bundle.

### C. News Feeds & Economic Data Sources
1. **ForexFactory Calendar:**
   - Fetched via an asynchronous HTTP GET request every 1 hour (and cached locally).
   - Filters events for currencies: `USD`, `EUR`, `GBP`.
2. **Geopolitical RSS Feeds:**
   - Polled every 5–10 minutes from top financial wire RSS endpoints (Reuters Business, FXStreet Breaking, Yahoo Finance).

### D. Alerts & Communication
1. **Telegram Bot Setup:**
   - Uses Telegram's standard Bot API (`https://api.telegram.org/bot<TOKEN>/sendMessage`).
   - Requires only a free Bot Token from `@BotFather` and the user's `chat_id`.

---

## 3. Directory & Codebase Architecture

```
c:\Users\OS\Desktop\The Life\
│
├── docs/                             # Complete Documentation & PRD
│   ├── PRD.md                        # Product Requirements Document
│   ├── DISCOVERY_LOG.md              # Interview and decision history
│   └── TECH_STACK_AND_RESOURCES.md   # Dependency & Sourcing Plan
│
├── backend/                          # Python Core Engine
│   ├── app.py                        # FastAPI / WebSocket server & main runner
│   ├── bridge/                       # MT5 Connection & Live Data Streaming
│   │   ├── mt5_client.py             # MT5 IPC client (ticks, bars, balance)
│   │   └── symbol_manager.py         # Pip & lot size engine (EURUSD, XAUUSD, XAGUSD)
│   ├── modules/                      # The Multi-Layer Confluence Engine
│   │   ├── layer0_macro/             # News Guard (ForexFactory) & Geopolitical RSS Sentiment
│   │   ├── pillar1_smc/              # Order Blocks, FVGs, Liquidity Sweeps, Asian Range
│   │   ├── pillar2_patterns/         # Classical S/R, Chart Patterns, Candlestick Formations
│   │   ├── pillar3_mtf_smt/          # Multi-Timeframe Bias & SMT Divergence Engine
│   │   └── pillar4_master/           # Confluence Synthesizer, 3-Tranche Scaling & BE Manager
│   ├── alerts/                       # Telegram Bot & Chart Snapshot Dispatcher
│   └── database/                     # SQLite models for trades, journal & daily PnL
│
├── frontend/                         # Modern Desktop / Web UI
│   ├── index.html                    # Root HTML
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChartView.jsx         # TradingView Lightweight Charts component
│   │   │   ├── ConfluenceRadar.jsx   # Live Confluence Score & Pillar Status
│   │   │   ├── NewsGuardBar.jsx      # Red Folder countdown & Macro Sentiment bias
│   │   │   └── ExecutionPanel.jsx    # Balance, lot calculator, 3-tranche order buttons
│   │   └── App.jsx                   # Main layout
│   └── vite.config.js                # Vite build configuration
│
├── run_terminal.bat                  # One-click desktop launcher for Windows / VPS
└── requirements.txt                  # Python dependencies list
```

---

## 4. Execution Readiness Checklist
- [x] MetaTrader 5 installed on Windows (`C:\Program Files\MetaTrader 5`)
- [x] Node.js runtime verified (`v24.19.0`)
- [x] Full PRD and Architecture finalized
- [ ] Install Python 3.11 via winget
- [ ] Initialize Python Virtual Environment (`venv`) & install dependencies
- [ ] Build & Test MT5 Bridge connectivity with live demo/live account


# 📖 The Life Forex Confluence Terminal — User Operation Manual
> **Institutional Quantitative Trading Desktop Terminal & Strategy Evolution Arena**  
> *Target Assets: EURUSD, GBPUSD, XAUUSD (Gold), XAGUSD (Silver)*  
> *Version: 1.0.0 (Production Master)*

---

## 📑 Table of Contents / সূচিপত্র
1. [Overview & Architectural Philosophy](#1-overview--architectural-philosophy)
2. [Pillars & Engine Breakdown](#2-pillars--engine-breakdown)
3. [System Requirements & Installation](#3-system-requirements--installation)
4. [One-Click Desktop Launch (`run_terminal.bat`)](#4-one-click-desktop-launch-run_terminalbat)
5. [Frontend Terminal Interface Guide](#5-frontend-terminal-interface-guide)
6. [Strategy Evolution Arena Guide (Multi-Line Fan)](#6-strategy-evolution-arena-guide-multi-line-fan)
7. [Prop Firm Safety Shield & Risk Management](#7-prop-firm-safety-shield--risk-management)
8. [2-Way Telegram Mobile Command Center](#8-2-way-telegram-mobile-command-center)
9. [Interactive Bar-Replay Simulator](#9-interactive-bar-replay-simulator)
10. [REST API & WebSocket Contract](#10-rest-api--websocket-contract)
11. [বাংলা ব্যবহার নির্দেশিকা (Bengali User Guide)](#11-বাংলা-ব্যবহার-নির্দেশিকা-bengali-user-guide)

---

## 1. Overview & Architectural Philosophy
**The Life Terminal** is an institutional-grade, local-first quantitative trading system built specifically to eliminate expensive third-party subscriptions (such as TradingView premium or commercial SaaS black-box indicators). 

### Core Tenets:
- **Zero Ongoing Cloud/Subscription Cost:** Runs 100% locally on your Windows PC.
- **Selective Quality Over Quantity:** Focuses exclusively on M15 execution filtered through H4/Daily trend alignment, executing strictly 1–2 Grade A+ setups per day.
- **Mathematical Multi-Pillar Consensus:** Orders are only approved when technical, liquidity, intermarket, and macroeconomic conditions align ($Score \ge 80\%$, $0\text{ Vetos}$).
- **Guaranteed Capital Preservation:** Enforces a rigid 3-Tranche Scaling model with automated Break-Even shifting ($Entry + 1\text{ pip}$ spread buffer) and a 4-tier Prop Firm Safety Shield.

---

## 2. Pillars & Engine Breakdown

| Layer / Pillar | System Component | Technical Mechanics |
|---|---|---|
| **Layer 0** | **Hermes Macro AI & News Guard** | Scrapes ForexFactory JSON for Red Folder news (30m pre/post-news freeze), ingests financial RSS feeds, and outputs a directional bias score ($-100$ to $+100$). |
| **Pillar 1** | **Smart Money Concepts (SMC)** | Identifies institutional Order Blocks (OB), unmitigated Fair Value Gaps (FVG), and Asian Session ($00:00–08:00\text{ GMT}$) Judas Swing liquidity sweeps. |
| **Pillar 2** | **Classical Price Action** | Detects high-volume horizontal S/R pivot clusters, Quasimodo / Double Tops & Bottoms, and Rejection Pinbar / Engulfing trigger bars. |
| **Pillar 3** | **MTF & SMT Divergence** | Confirms M15 setups with Daily & H4 50/200 EMA trends; cross-references EUR/GBP and Gold/Silver non-confirmations to detect institutional accumulation/distribution traps ($+15\text{ pts}$). |
| **Pillar 4** | **Master Arbiter & Scaling Engine** | Generates weighted 0–100% Confluence Score; enforces 5 strict veto gates; splits position into 3 tranches: TP1 ($1.0R$), TP2 ($2.5R$), TP3 (Open Runner with Adaptive Trailing Stop). Automatically ratchets SL to Break-Even $+1\text{ pip}$ upon TP1 hit. |
| **Pillar 5** | **Local Database & Telegram Bot** | High-performance SQLite database (`terminal.db` with WAL mode); sends high-resolution dark-theme PNG chart snapshots; provides 2-way interactive mobile controls (`/status`, `/positions`, `/news`, `/briefing`, `/pause`, `/resume`, `/closeall`). |
| **Pillar 6** | **Desktop Dashboard Shell** | React 18 + Tailwind CSS + TradingView Lightweight Charts v5.2.1 + FastAPI WebSocket server; launches as a borderless native Windows desktop application via Microsoft Edge WebView2. |
| **Pillar 7** | **Strategy Evolution Arena** | Continuous background tournament genetic backtester simulating variant DNA mutations; renders a real-time Multi-Line Equity Fan Chart branching trade-by-trade from \$1,000; provides one-click live hot-swap promotion. |
| **Pillar 8** | **Safety Shield & Bar-Replay** | Prop Firm Safety Shield enforcing daily trade cap (2 trades), daily drawdown limit (4%), max drawdown limit (8%), and Friday weekend gap freeze ($20:00\text{ GMT}$); includes interactive historical bar-by-bar simulator. |

---

## 3. System Requirements & Installation

### Requirements:
- **Operating System:** Windows 10 or Windows 11 (64-bit).
- **Python:** Python 3.11.x (included in `.venv`).
- **Browser/Runtime:** Microsoft Edge (standard on Windows 10/11) for WebView2 desktop app mode.
- **Broker Terminal:** MetaTrader 5 (MT5) with demo or live account (Exness, FTMO, or IC Markets).

### Directory Structure:
```
The Life/
├── backend/
│   ├── alerts/               # Telegram bot & Matplotlib PNG chart generator
│   ├── backtest/             # Interactive Bar-Replay engine
│   ├── bridge/               # MT5 IPC client, Symbol Manager, Market Feed
│   ├── config/               # strategy_dna.json & telegram_config.json
│   ├── database/             # SQLite models & WAL db_manager
│   ├── modules/
│   │   ├── layer0_macro/     # News Guard, RSS fetcher, Hermes Macro Agent
│   │   ├── pillar1_smc/      # FVG, Order Blocks, Asian Range sweep
│   │   ├── pillar2_patterns/ # S/R clusters, Candlestick pinbars/engulfing
│   │   ├── pillar3_mtf_smt/  # EMA 50/200 aligner & SMT divergence
│   │   └── pillar4_master/   # Confluence Arbiter, Order Manager, Safety Shield
│   ├── optimization/         # Genetic mutator & Background Lab tournament
│   └── app.py                # FastAPI REST & WebSocket streaming server
├── frontend/
│   ├── dist/                 # Precompiled production build (Ready to run)
│   ├── src/                  # React 18, Tailwind CSS, TradingView Lightweight Charts
│   └── vite.config.js
├── docs/                     # Roadmap, architecture, discovery & operation manual
├── tests/                    # 8 Automated unit & integration verification test suites
├── run_terminal.bat          # One-click Windows desktop launcher
└── terminal.db               # Local SQLite database (created automatically)
```

---

## 4. One-Click Desktop Launch (`run_terminal.bat`)

To start the entire terminal, simply **double-click** `run_terminal.bat` in the project root:
```cmd
run_terminal.bat
```

### What Happens Automatically:
1. Activates Python 3.11 virtual environment (`.\.venv\Scripts\activate.bat`).
2. Starts the FastAPI server and real-time WebSocket ticker on `http://127.0.0.1:8000`.
3. Opens Microsoft Edge in **Native App Mode** (`--app=http://localhost:8000 --window-size=1600,950`), removing all browser tabs, URL bars, and bookmark bars to give you a true borderless desktop terminal feel.
4. When you close the batch window or press any key, the background Python server gracefully shuts down.

---

## 5. Frontend Terminal Interface Guide

The terminal features two primary workspaces accessible via the top navigation bar:
1. `[ 📈 TERMINAL ]` — Live operational command deck.
2. `[ 🧬 EVOLUTION ARENA ]` — Genetic backtesting and strategy optimization lab.

### Top Header Bar:
- **Status Indicator:** Shows live WebSocket pulse (Green = Streaming, Red = Offline).
- **Time Sync:** Displays precise GMT server clock for session alignment (London 08:00–16:30 GMT, NY 13:00–21:00 GMT).
- **Account Summary:** Displays Balance, Equity, Today's Net PnL (\$), and Today's Trade Count ($n / 2\text{ max}$).
- **Killswitch Button:** Red `[ CLOSE ALL POSITIONS ]` emergency button with safety confirmation modal.

### Watchlist & Quick Switch Bar:
- Displays 4 key instruments: **XAUUSD**, **EURUSD**, **GBPUSD**, **XAGUSD**.
- Shows real-time bid/ask prices, live broker spread in pips, and current session bias. Click any card to switch the main chart instantly.

### Main Chart View (TradingView Lightweight Charts v5.2.1):
- Institutional dark aesthetic (`#0B0E14` background, `#00F0FF` cyan bullish candles, `#FF3B30` red bearish candles).
- Dynamic overlays:
  - Cyan dashed lines for Take Profit targets (TP1 & TP2).
  - Red dashed lines for Stop Loss and Break-Even levels.
  - SMC Fair Value Gap (FVG) and Order Block (OB) shaded boxes.
  - Interactive crosshairs with price and time tooltips.

### Confluence Radar HUD (Right Side):
- Circular 0–100% Confluence Gauge showing current setup score.
- Grade Badge:
  - `GRADE A+` ($\ge 80\%$): Full consensus, eligible for immediate automated execution.
  - `GRADE A` ($65–79\%$): Strong setup, standby for secondary confirmation.
  - `GRADE B OR LOWER` ($< 65\%$): Stand down, capital protection active.
- Pillar Breakdown Bars: Shows exact points contributed by SMC, Classical S/R, MTF Trend, SMT Divergence, and Hermes Macro.
- Active Veto Gates: Live checklist showing News Guard, Spread Guard, Daily Cap, MTF Counter-Trend, and Macro Bias status.

### Execution Deck & Active Positions Table (Bottom):
- Live 3-Tranche Breakdown:
  - **Tranche 1 (TP1):** 33% of risk, target $1.0R$ — locks immediate profit.
  - **Tranche 2 (TP2):** 33% of risk, target $2.5R$ — captures extended swing.
  - **Tranche 3 (Runner):** 34% of risk, open target with adaptive ATR/Swing trailing stop.
- Shows Real-Time Unrealized PnL (\$), active SL, and status badges (`ACTIVE`, `CLOSED_TP`, `CLOSED_BE`, `CLOSED_TRAIL`).

---

## 6. Strategy Evolution Arena Guide (Multi-Line Fan)

Inspired by quantitative genetic research, the **Evolution Arena** runs continuous background backtests on your historical MT5 data to optimize strategy parameters safely.

### Accessing the Arena:
Click `[ 🧬 EVOLUTION ARENA ]` in the top header.

### Multi-Line Equity Fan Chart:
- Displays **15 unique strategy variants** simultaneously on an HTML5 canvas.
- All equity curves originate at (Trade 0, Equity \$1,000.00) and fan outward trade-by-trade across 80 simulated trades.
- Top performers ascend to \$1,600–\$1,900+; struggling variants flatten or turn red.
- **Active Champion Curve:** Rendered as a distinct bright cyan line with high glow.

### Tournament Leaderboard Table:
- Ranks all 15 variants in real time by Win Rate, Profit Factor, Net Return, and Max Drawdown.
- Displays the exact Strategy DNA parameters (ATR Multiplier, TP1 R-multiple, TP2 R-multiple, Confluence Threshold).
- Status Badges:
  - `CHAMPION`: The currently active trading DNA running on live charts.
  - `CHALLENGER`: Mutated variant competing for the top rank.

### One-Click Live Promotion:
- If a challenger outperforms the champion, click the green `[ PROMOTE TO LIVE ]` button next to its row.
- **Result:** The system instantly hot-swaps the active parameters in `backend/config/strategy_dna.json`, logs the audit entry into `terminal.db`, and updates the live chart execution engine without needing to restart the server!

---

## 7. Prop Firm Safety Shield & Risk Management

The terminal includes strict institutional risk filters specifically designed to safeguard FTMO, FundedNext, and personal prop firm challenge accounts:

1. **Daily Trade Cap Lockout (Max 2 Trades/Day):**
   - Strictly enforces the rule: 1–2 high-probability Grade A+ setups per day maximum.
   - Once 2 trades are taken, the system engages `DAILY_CAP_LOCK` and rejects all new execution signals until the next calendar day.
2. **Daily Drawdown Shield (4.0% Max Loss Limit):**
   - Tracks daily equity loss against the starting day balance.
   - If cumulative losses reach **4.0%**, the system immediately triggers `DAILY_DRAWDOWN_LOCK`, flattens remaining open risk, and blocks trading for the rest of the day.
3. **Max Total Drawdown Shield (8.0% Max Limit):**
   - Monitors lifetime account equity against initial funding.
   - If total drawdown reaches **8.0%**, `MAX_DRAWDOWN_LOCK` activates emergency shutdown to prevent account forfeiture.
4. **Friday Weekend Gap Guard (20:00 GMT Freeze):**
   - At or after **20:00 GMT every Friday** (1–2 hours before market close), new entries are strictly prohibited (`FRIDAY_WEEKEND_LOCK`) to eliminate the risk of weekend news gap opens.
   - Alerts trader to close or tighten runners before weekend shutdown.
5. **Spread Guard:**
   - Blocks execution if broker spread widens beyond configured thresholds (Gold > 3.0 pips, EURUSD > 1.5 pips).

---

## 8. 2-Way Telegram Mobile Command Center

The terminal includes a full 2-way interactive Telegram Bot (`backend/alerts/telegram_bot.py`) that acts as your mobile remote control.

### Setup Instructions:
1. Open Telegram and message `@BotFather` to create a bot. Copy your bot token (e.g. `123456789:ABCdef...`).
2. Message `@userinfobot` to get your numeric Telegram User ID (e.g. `123456789`).
3. Open `backend/config/telegram_config.json` and enter your credentials:
```json
{
  "bot_token": "YOUR_TELEGRAM_BOT_TOKEN_HERE",
  "chat_id": "YOUR_TELEGRAM_CHAT_ID_HERE",
  "authorized_users": ["YOUR_TELEGRAM_CHAT_ID_HERE"],
  "alerts_enabled": true
}
```

### Outbound Real-Time Alerts:
- **Grade A+ Setup Detected:** Sends instant alert with setup details and attaches a **96 KB dark-theme PNG chart snapshot** with Entry, SL, TP1, and TP2 marked visually.
- **TP1 Hit & Auto Break-Even:** Sends notice when TP1 is locked and SL has been automatically moved to Break-Even $+1\text{ pip}$.
- **TP2 Hit & Trailing Stop Updates:** Sends notifications as runners trail in profit.
- **Red Folder Flash:** Warns 15–30 minutes before high-impact economic releases (NFP, CPI, FOMC).

### Inbound Mobile Remote Commands:
Send any of the following commands directly to your bot:
- `/status` — Returns terminal health, account balance, today's PnL, open positions count, and Prop Firm compliance status.
- `/positions` — Lists all open tranches with entry prices, active stop loss, and current floating PnL.
- `/news` — Displays upcoming ForexFactory Red Folder events and countdown timers.
- `/briefing` — Requests Hermes AI's latest macroeconomic dossier and directional bias score.
- `/pause` — Pauses automated execution engine (e.g. during unexpected market turmoil).
- `/resume` — Unpauses the terminal back to active scanning.
- `/closeall` — **Emergency Killswitch Initiation:** Requests safety confirmation.
- `/confirm_kill` — **Emergency Killswitch Execution:** Instantly closes all open MT5 positions and cancels pending orders!

---

## 9. Interactive Bar-Replay Simulator

The **Bar-Replay Engine** (`backend/backtest/bar_replay.py`) allows you to backtest and practice market execution bar-by-bar without financial risk.

### Key Capabilities:
- Simulates realistic multi-day M15 market cycles with Asian range consolidations, London Judas sweeps, and NY trend expansions.
- High-fidelity intra-bar modeling (evaluates Low/High/Close sequences for realistic slippage and stop-loss checks).
- Step forward bar-by-bar (`engine.step()`) or run full multi-week simulations (`engine.run_all()`).
- Automatically computes institutional metrics: Total Trades, Win Rate %, Gross Profit, Gross Loss, Profit Factor, and Max Drawdown %.

---

## 10. REST API & WebSocket Contract

The FastAPI server provides 10 clean REST endpoints and a high-speed WebSocket stream:

### REST Endpoints:
- `GET /api/status` — Terminal system health, broker info, balance, and server GMT time.
- `GET /api/watchlist` — Monitored symbols, live bid/ask, spreads, and daily bias.
- `GET /api/candles?symbol=XAUUSD&timeframe=M15&count=50` — OHLCV candle stream for TradingView charts.
- `GET /api/confluence?symbol=XAUUSD` — Comprehensive Confluence Radar telemetry and veto status.
- `POST /api/execute` — Dispatches institutional 3-tranche trade package.
- `GET /api/positions` — Active open tranches and floating PnL.
- `POST /api/closeall` — Emergency position flattener.
- `GET /api/safety/status` — Prop Firm Safety Shield metrics and active locks.
- `GET /api/evolution/tournament` — Strategy Evolution tournament leaderboard and champion parameters.
- `GET /api/evolution/fan-curves` — Multi-line equity fan curves data for the 15 variants.
- `POST /api/evolution/promote` — Promotes a challenger variant to active champion.
- `POST /api/replay/run` — Runs historical bar-replay simulation.

### WebSocket:
- `ws://127.0.0.1:8000/ws` — Streams JSON tick updates every second:
```json
{
  "type": "TICK_UPDATE",
  "timestamp": "2026-11-07T14:30:00Z",
  "ticks": {
    "XAUUSD": 2742.50,
    "EURUSD": 1.0855,
    "GBPUSD": 1.2960,
    "XAGUSD": 32.85
  },
  "daily_pnl_usd": 185.00,
  "trades_count": 1
}
```

---

## 11. বাংলা ব্যবহার নির্দেশিকা (Bengali User Guide)

### ১. কীভাবে এক ক্লিকে টার্মিনাল চালু করবেন?
- প্রোজেক্ট ফোল্ডারে থাকা **`run_terminal.bat`** ফাইলে ডাবল-ক্লিক করুন।
- এটি স্বয়ংক্রিয়ভাবে পাইথন ব্যাকএন্ড সার্ভার চালু করবে এবং মাইক্রোসফট এজ (Edge) ব্রাউজারের সাহায্যে কোনো প্রকার অ্যাড্রেস বার ছাড়া একটি সম্পূর্ণ ডেস্কটপ সফটওয়্যার আকারে টার্মিনাল উইন্ডো ওপেন করবে।

### ২. টার্মিনাল এবং চার্ট কীভাবে দেখবেন?
- টার্মিনাল চালু হলে উপরে `[ 📈 TERMINAL ]` এবং `[ 🧬 EVOLUTION ARENA ]` দুটি ট্যাব দেখতে পাবেন।
- বাম পাশের ওয়াচলিস্ট থেকে **XAUUSD (গোল্ড)**, **EURUSD**, **GBPUSD** বা **XAGUSD (সিলভার)** সিলেক্ট করলে সাথে সাথে ট্রেডিংভিউ চার্টে রিয়েল-টাইম ক্যান্ডেলস্টিক চলে আসবে।
- ডান পাশের **কনফ্লুয়েন্স রাডার** আপনাকে সরাসরি স্কোর দেখাবে (০ থেকে ১০০%)। স্কোর ৮০% এর বেশি হলে এবং কোনো ভেটো না থাকলে তা **Grade A+** হিসেবে গণ্য হবে।

### ৩. ৩-ট্রাঞ্চ ট্রেড ম্যানেজমেন্ট কীভাবে কাজ করে?
টার্মিনালটি রিস্ক ম্যানেজমেন্টের জন্য প্রতি ট্রেডকে ৩ ভাগে ভাগ করে:
- **Tranche 1 (TP1):** ১:১ রিস্ক-রিওয়ার্ডে পৌঁছালে ৩ ভাগের ১ ভাগ প্রফিট বুক করে নেয়।
- **স্বয়ংক্রিয় ব্রেক-ইভেন (Auto Break-Even):** TP1 হিট করার সাথে সাথেই বাকি দুই ভাগের স্টপ লস (SL) স্বয়ংক্রিয়ভাবে এন্ট্রি প্রাইসের ১ পিপ ওপরে চলে আসে—ফলে ট্রেডটি ১০০% ঝুঁকিমুক্ত (Risk-Free) হয়ে যায়!
- **Tranche 2 (TP2):** ১:২.৫ রিস্ক-রিওয়ার্ডে দ্বিতীয় অংশ প্রফিট বুক করে।
- **Tranche 3 (Runner):** শেষ অংশটি ওপেন থাকে এবং প্রাইস যত বাড়তে থাকে, ট্রেইলিং স্টপ লসও তত ওপরে উঠে প্রফিট লক করতে থাকে।

### ৪. প্রপ ফার্ম সেফটি শিল্ড (Prop Firm Safety Shield):
- **দিনে সর্বোচ্চ ২টি ট্রেড:** দৈনিক ওভারট্রেডিং রুখতে দিনে সর্বোচ্চ ২টি A+ সেটআপেই ট্রেড নেওয়া যাবে।
- **৪% দৈনিক ড্র-ডাউন লক:** দিনে ব্যালেন্সের ৪% লস হওয়া মাত্র টার্মিনাল স্বয়ংক্রিয়ভাবে ট্রেডিং বন্ধ করে দেবে, যাতে কোনোভাবেই আপনার FTMO বা FundedNext অ্যাকাউন্ট নষ্ট না হয়।
- **শুক্রবার রাত ৮টার পর নতুন ট্রেড বন্ধ:** উইকএন্ড গ্যাপ রিক্স এড়াতে শুক্রবার রাত ৮:০০ GMT এর পর নতুন কোনো ট্রেড নেওয়া যাবে না।

### ৫. টেলিগ্রাম মোবাইল রিমোট কন্ট্রোল:
আপনার ফোনে টেলিগ্রামের মাধ্যমে দূরে থেকেও পুরো টার্মিনাল কন্ট্রোল করতে পারবেন:
- `/status` পাঠালে বর্তমান ব্যালেন্স, ইকুইটি এবং আজকের লাভ-লস জানতে পারবেন।
- `/positions` পাঠালে বর্তমান ওপেন ট্রেডগুলোর স্ট্যাটাস দেখা যাবে।
- `/closeall` পাঠালে সাথে সাথে একটি কনফার্মেশন চাইবে এবং `/confirm_kill` দিলে সব ট্রেড সাথে সাথে ক্লোজ হয়ে যাবে।
- কোনো A+ ট্রেড পাওয়া গেলে চার্টের সুন্দর ছবি সহ স্বয়ংক্রিয়ভাবে আপনার ফোনে নোটিফিকেশন চলে আসবে।

### ৬. স্ট্র্যাটেজি ইভোলিউশন অ্যারেনা (Evolution Arena):
- উপরের `[ 🧬 EVOLUTION ARENA ]` ট্যাবে ক্লিক করলে ব্যাকগ্রাউন্ডে ১৫টি আলাদা স্ট্র্যাটেজির মাল্টি-লাইন ইকুইটি ফ্যান চার্ট দেখতে পাবেন।
- যেটি সবচেয়ে বেশি লাভ এবং কম ড্র-ডাউন দিচ্ছে, তার পাশে থাকা সবুজ **`[ PROMOTE TO LIVE ]`** বাটনে এক ক্লিক করলেই সেই স্ট্র্যাটেজি সরাসরি লাইভ চার্টে সেট হয়ে যাবে!

---
> **The Life Terminal — Engineered for Systematic Alpha & Capital Protection.**

# UI/UX Design & Control Wireframe Specification

> **Document Version:** 1.0.0  
> **Interface Paradigm:** Institutional Dark Terminal (Bloomberg / TradingView Pro Aesthetics)  
> **Rendering Engine:** TradingView Lightweight Charts (v5.2.1) + React 18 + Tailwind CSS  
> **Form Factor:** Native Windows Desktop Window (`pywebview` Edge WebView2)

---

## 1. Visual Theme, Color Palette & Typography

| Element | Hex Color | Role / Meaning |
|---|---|---|
| **App Background** | `#0B0E14` (Deep OLED Black) | Base dark background for zero eye fatigue. |
| **Card / Panel Background** | `#151921` (Slate Charcoal) | Container backgrounds with `#222834` 1px border. |
| **Bullish Accent** | `#00E676` (Neon Mint Green) | Buy signals, profit states, bullish FVG / Order Blocks. |
| **Bearish Accent** | `#FF3B30` (Crimson Scarlet) | Sell signals, stop losses, bearish FVG / Order Blocks. |
| **Confluence Accent** | `#00F0FF` (Electric Cyan) | Grade A+ badges, active execution buttons, chart crosshairs. |
| **Warning / News Alert** | `#FFB300` (Amber Gold) | Red Folder news countdown, spread warning, Asian session box. |
| **Veto / Hard Lock** | `#D500F9` (Electric Magenta) | Veto active, system trade lockout. |
| **Typography** | `JetBrains Mono` / `Inter` | Clean monospace for prices/metrics; sans-serif for UI labels. |

---

## 2. Master Dashboard Layout Wireframe

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [● LIVE] THE LIFE CONFLUENCE TERMINAL  │ Broker: FTMO (MT5 #827192) │ Server Time: 14:32:15 GMT │ [⚙] [✕] │
├─────────────────────────┬─────────────────────────────────────────────────┬────────────────────────────┤
│ WATCHLIST (Zone B)      │ MAIN CHART VIEW (Zone C)                        │ LIVE CONFLUENCE RADAR (D)  │
│ ┌─────────────────────┐ │ ┌─────────────────────────────────────────────┐ │ ┌────────────────────────┐ │
│ │ XAUUSD (Gold)  [▲]  │ │ │ [XAUUSD] [M15 ▼] [Candles] [Drawings ▼]     │ │ │ OVERALL SCORE: 91%     │ │
│ │ 2742.80 | +0.45%    │ │ │ ------------------------------------------- │ │ │ [ GRADE A+ SETUP ]     │ │
│ ├─────────────────────┤ │ │                                             │ │ ├────────────────────────┤ │
│ │ EURUSD         [▼]  │ │ │   [Candlestick Chart (Lightweight Charts)]  │ │ │ PILLAR CHECKLIST:      │ │
│ │ 1.08450 | -0.12%    │ │ │   - Asian Range High/Low Box (Amber)        │ │ │ [✓] Macro: +75 Bull    │ │
│ ├─────────────────────┤ │ │   - M15 Bullish FVG Zone (Mint Tint)        │ │ │ [✓] SMC: M15 FVG+Sweep │ │
│ │ GBPUSD         [▲]  │ │ │   - Dynamic Support Level: 2738.00          │ │ │ [✓] Patterns: Dbl Btm  │ │
│ │ 1.29650 | +0.22%    │ │ │   - Entry Target Line: 2742.50              │ │ │ [✓] MTF Bias: H4 Bull  │ │
│ ├─────────────────────┤ │ │   - SL: 2738.00 | TP1: 2747.00              │ │ │ [✓] SMT: Gold/Silver   │ │
│ │ XAGUSD (Silver)[▲]  │ │ │   - TP2: 2753.50 | TP3 (BE): 2762.00        │ │ ├────────────────────────┤ │
│ │ 32.850 | +1.10%     │ │ │                                             │ │ │ HERMES AI BRIEFING:    │ │
│ └─────────────────────┘ │ └─────────────────────────────────────────────┘ │ │ "Middle East risk safe │ │
│ SPREAD: 1.2 pips [OK]   │ [◀ BAR REPLAY] [PLAY ▶] [SPEED: 1x ▼] [RESET]   │ │  haven gold demand."   │ │
│ NEWS GUARD: [CLEAR]     │                                                 │ ├────────────────────────┤ │
│ Next Red Folder:        │                                                 │ │ RED FOLDER COUNTDOWN:  │ │
│ US NFP in 4h 12m        │                                                 │ │ [ ACTIVE - NO VETO ]   │ │
├─────────────────────────┴─────────────────────────────────────────────────┴────────────────────────────┤
│ ACCOUNT & EXECUTION CONTROL DECK (Zone E)                                                              │
│ Balance: $1,000.00 │ Equity: $1,018.50 │ Daily PnL: +$18.50 (+1.85%) │ Daily Trades: [ 1 / 2 Max ]       │
│ Risk %: [ 1.0% ▼ ] │ Calc Lot: 3x 0.01 Lot (Total 0.03) │ SL Buffer: [ 1.4x ATR ▼ ] │ Trailing: [ ON ] │
│ ------------------------------------------------------------------------------------------------------ │
│ [ ⚡ EXECUTE 3-TRANCHE BUY ]     [ ⚡ EXECUTE 3-TRANCHE SELL ]     [ ❌ CLOSE ALL ]    [ 📢 SEND TELEGRAM ]│
│ ------------------------------------------------------------------------------------------------------ │
│ ACTIVE TRADES: #81921 XAUUSD BUY (TP1 Hit @ 2747.00 | SL moved to BE @ 2742.50 | Runner Active)        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Component & Button-by-Button Specification

### Zone A: Top Header & System Status Bar
1. **Connection Pill (`[● LIVE / ● RECONNECTING]`):**
   - Green pulsing dot when MT5 IPC heartbeat is active.
   - Turns Red with auto-reconnect spinner if MT5 closes.
2. **Account Badge:** Displays Broker name (`FTMO` / `FundingPips` / `Exness`) and MT5 Account number.
3. **Server Clock:** Live GMT market time (essential for London/NY session tracking).
4. **Header Actions:**
   - `[⚙ Settings]`: Opens modal for Telegram Bot Token, Chat ID, and Broker paths.
   - `[✕ Minimize / Close]`: Minimizes app to Windows System Tray so it runs 24/5 in background.

---

### Zone B: Left Watchlist & Market Conditions
1. **Asset Cards (`XAUUSD`, `EURUSD`, `GBPUSD`, `XAGUSD`):**
   - Click to switch active chart and analysis.
   - Shows live Bid/Ask price and 24h percentage change.
2. **Live Spread Gauge:**
   - Shows current spread in real-time pips.
   - If spread exceeds safety threshold (>2.5 on Gold), turns Bright Red and displays `[SPREAD VETO]`.
3. **ForexFactory News Guard Pill:**
   - Displays time remaining to next Red Folder news.
   - If under 30 minutes, pulses Magenta with `[NEWS VETO ACTIVE - NO TRADING]`.

---

### Zone C: Center TradingView Interactive Chart
1. **Timeframe Switcher:** Toggle buttons for `[ M5 ]`, `[ M15 ]` *(Default Execution)*, `[ H1 ]`, `[ H4 ]`, `[ D1 ]`.
2. **Visual Chart Overlays:**
   - **Asian Session Range Box:** Shaded amber box covering 00:00 to 08:00 GMT with marked Asian High and Low lines.
   - **Order Blocks & FVG Rectangles:** High-contrast shaded boxes showing unmitigated zones.
   - **Execution Projection Lines:** Horizontal dashed lines for Entry (Cyan), Stop Loss (Red), TP1 (Green), TP2 (Green), TP3 Runner (Electric Mint).
3. **Bar-Replay Controller (Bottom of Chart):**
   - `[◀ Replay Mode]`: Jump back to any date in history.
   - `[Play / Pause]`: Replay market bar-by-bar at 1x, 2x, 5x, 10x speed for practice and backtesting.
   - `[Step Forward]`: Advance 1 candle at a time.

---

### Zone D: Right Institutional Radar & Hermes Dossier
1. **Confluence Gauge (Circular Radial Score):**
   - Displays real-time score from `0%` to `100%`.
   - Dynamic Badge:
     - **85% - 100%:** `[ GRADE A+ SETUP ]` (Bright Cyan Glow)
     - **75% - 84%:** `[ GRADE A SETUP ]` (Emerald Green)
     - **< 75%:** `[ NO TRADE / WAITING ]` (Muted Gray)
2. **Pillar Status Checklist:**
   - 5 interactive check items with pass/fail indicators:
     - `[✓] Layer 0: Macro Sentiment (+75 Bullish)`
     - `[✓] Pillar 1: SMC Liquidity Sweep & FVG`
     - `[✓] Pillar 2: Price Action & Reversal Pattern`
     - `[✓] Pillar 3: Higher Timeframe Bias Alignment`
     - `[✓] Pillar 3: SMT Intermarket Divergence`
3. **Hermes AI Briefing Card:**
   - Displays 2-3 sentence AI summary of current market-moving forex news and geopolitical impact.
4. **News Guard Countdown Box:**
   - Shows exact time until upcoming high-impact economic releases.

---

### Zone E: Bottom Order Execution, Risk & Live Position Deck
1. **Account Telemetry Bar:**
   - **Balance & Equity:** Real-time balance synced from MT5.
   - **Daily PnL Counter:** Green/Red dollar amount and percentage.
   - **Daily Trade Counter:** `[ 1 / 2 Max ]` (Disables execution once 2 trades are taken to preserve discipline).
2. **Dynamic Risk Controls:**
   - **Risk % Selector:** Dropdown presets `[ 0.5% ]`, `[ 1.0% ]`, `[ 2.0% ]` or custom input.
   - **Auto Lot Sizing Display:** Shows automatically calculated lot size broken into 3 equal tranches (e.g. `3x 0.01 lot`).
   - **Break-Even (BE) Toggle:** Switch to auto-move SL to entry price once TP1 is hit.
   - **Adaptive Trailing Toggle:** Switch to trail remaining runner once TP2 is hit.
3. **Execution Action Buttons:**
   - `[ ⚡ EXECUTE 3-TRANCHE BUY ]`: Primary Green button (enables only when Confluence is Grade A/A+ and zero vetos are active).
   - `[ ⚡ EXECUTE 3-TRANCHE SELL ]`: Primary Red button.
   - `[ ❌ CLOSE ALL POSITIONS ]`: Emergency button to flatten all open trades instantly.
   - `[ 📢 SEND TELEGRAM ALERT ]`: One-click button to dispatch formatted chart screenshot and trade dossier to your Telegram channel.
4. **Active Trades & Position Manager Table:**
   - Lists active ticket ID, symbol, tranche number, entry, live PnL, and current SL/TP.
   - Includes quick-action buttons: `[ Manually Move to BE ]`, `[ Close Tranche 1 ]`, `[ Trail Now ]`.

---

## 4. Secondary Views & Modals

### Screen 1: Autonomous Strategy Evolution Arena (The Multi-Line Tournament Fan)
*Directly inspired by the quantitative strategy mutation fan, where hundreds of strategies are continuously backtested in the background 24/7.*

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [ 🧠 AUTONOMOUS STRATEGY EVOLUTION ARENA ]                  ● Lab Worker: ACTIVE (Testing Generation #14) │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ MULTI-STRATEGY EQUITY FAN CHART (100+ Background Backtest Simulations Running)                         │
│ ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ Equity ($)                                                                                         │ │
│ │ $1,500 │                                            ╭──── [Variant #42 - Neon Cyan] +48.2% (WIN)   │ │
│ │        │                                  ╭─────────╯                                              │ │
│ │ $1,300 │                         ╭────────╯────────────── [Variant #38 - Gold]     +31.5%          │ │
│ │        │               ╭─────────╯──────╮──────────────── [Variant #19 - Green]    +22.0%          │ │
│ │ $1,100 │         ╭─────╯────────────────┴──────────────── [Variant #04 - Gray]     +8.5%           │ │
│ │ $1,000 ┼─────────┴─────────────────────────────────────── [Baseline Origin]                       │ │
│ │        │         ╰─────╮───────────────────────────────── [Variant #12 - Red]      -14.2% (CULLED) │ │
│ │   $800 │               ╰─────────╮─────────────────────── [Variant #29 - Purple]   -28.0% (CULLED) │ │
│ │        └────────────────────────────────────────────────────────────────────────────────────────── │ │
│ │        0            50            100           150           200           250 Trades             │ │
│ └────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ TOURNAMENT LEADERBOARD (Top Performing Mutated Strategies)                                             │
│ ┌──────┬──────────────────────┬──────────┬──────────┬───────────┬──────────────┬─────────────────────┐     │
│ │ Rank │ Strategy Variant ID  │ Win Rate │ P. Factor│ Max DD %  │ Trades Tested│ Action / Status     │     │
│ ├──────┼──────────────────────┼──────────┼──────────┼───────────┼──────────────┼─────────────────────┤     │
│ │ 👑 #1│ DNA-GOLD-M15-V42     │ 78.5%    │ 2.45     │ 1.6% (OK) │ 420 trades   │ [ ACTIVE CHAMPION ] │     │
│ │ ⚔️ #2│ DNA-GOLD-M15-V38     │ 74.2%    │ 2.10     │ 1.9% (OK) │ 380 trades   │ [ PROMOTE TO LIVE ] │     │
│ │ 🧪 #3│ DNA-EURUSD-M15-V19   │ 71.0%    │ 1.95     │ 2.2% (OK) │ 510 trades   │ [ DEPLOY TO EURUSD] │     │
│ │ 💀 #4│ DNA-GOLD-M15-V12     │ 48.0%    │ 0.85     │ 5.4% (BAD)│ 200 trades   │ [ CULLED / DEAD ]   │     │
│ └──────┴──────────────────────┴──────────┴──────────┴───────────┴──────────────┴─────────────────────┘     │
│ [ ⚡ AUTO-PROMOTION: ON ]  [ 🧪 GENERATE 10 NEW MUTATIONS ]  [ 💾 EXPORT STRATEGY DNA ]                │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Detailed Features of the Evolution Arena Screen:
1. **The Multi-Line Equity Fan Chart:**
   - Visualizes 20 to 50 active strategy variants simultaneously on an HTML5 Canvas.
   - All curves start at \$1,000 base equity and branch outward as backtested trades accumulate.
   - **Colors:**
     - **Neon Cyan & Gold (Top 10%):** Outperforming variants advancing towards live production.
     - **Translucent Gray (Middle Pack):** Average baseline strategies.
     - **Faded Crimson (Bottom 20%):** Failing strategies automatically pruned (culled) by the genetic algorithm.
2. **Background Non-Blocking Simulation:**
   - Runs on a dedicated Python background worker using zero-cost local MT5 historical data.
   - Does NOT interfere with live M15 execution.
3. **One-Click Promotion:**
   - A single click on `[ PROMOTE TO LIVE ]` instantly hot-swaps the active live parameters in `strategy_dna.json` without needing to restart the software!

---

### Screen 2: System Settings & Integration Modal
- `MT5 Path Input`: Defaults to `C:\Program Files\MetaTrader 5\terminal64.exe`.
- `Telegram Bot Token` and `Chat ID` input fields with a `[ Test Message ]` button.
- `Max Daily Loss %` input (defaults to 2% for Prop Firm safety).
- `High-Impact News Buffer` input (defaults to 30 minutes before and after).


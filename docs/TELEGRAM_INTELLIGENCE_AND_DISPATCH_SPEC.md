# Telegram Intelligence & 2-Way Dispatch Specification

> **Document Version:** 1.0.0  
> **System Architecture:** Asynchronous 2-Way Telegram Bot (Broadcast Dispatcher + Interactive Mobile Remote)  
> **Target Device:** User's Mobile Phone (Telegram App)  
> **Primary Objective:** Provide 100% remote visibility, instant actionable trade alerts with charts, Hermes breaking news briefings, and full emergency control over MT5 from anywhere in the world.

---

## 1. System Architecture Overview

The Telegram Engine operates on two parallel asynchronous pipelines:
1. **Outbound Dispatcher (Push Notifications):** Pushes real-time Grade A+ signals, trade management milestones (TP1, TP2, BE), high-impact news warnings, and session briefings.
2. **Inbound Command Handler (2-Way Mobile Remote):** Listens for user commands (`/status`, `/positions`, `/news`, `/briefing`, `/closeall`, `/pause`) and executes them directly on the local MT5 terminal with strict whitelist authorization.

```
       [ Local Terminal Engine (MT5 / Hermes / Confluence) ]
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▲
 [ Outbound Push Dispatcher ]            [ Inbound Command Listener ]
 - Grade A+ Trade Setups + Charts        - `/status` (Balance, Equity, PnL)
 - TP1 / TP2 / Break-Even Updates        - `/positions` (Active tranches)
 - Hermes Breaking News Flash            - `/news` (Upcoming Red Folders)
 - London / NY Session Briefings         - `/briefing` (Hermes Market Brief)
 - End-of-Day Performance Card          - `/closeall` (Emergency Mobile Kill)
            │                                     │
            └──────────────────┬──────────────────┘
                               ▼
                   [ Telegram Bot API Gateway ]
                               │
                               ▼
               [ User's Mobile Phone (Telegram) ]
```

---

## 2. Outbound Push Notifications & Message Templates

### Category 1: Grade A+ Trade Signal (With High-Res Chart Snapshot)
*Dispatched immediately when Confluence Score $\ge 85\%$ and zero vetos are active.*

```markdown
🚨 [GRADE A+ TRADE SIGNAL DETECTED] 🚨
Pair: XAUUSD (Spot Gold)
Action: BUY (3-Tranche Scaling)
Confluence Score: 92% [GRADE A+]

📊 Execution Parameters:
• Entry Price: 2742.50
• Stop Loss (SL): 2738.00 (45 pips / $4.50)
• Take Profit 1 (TP1): 2747.00 (1:1 R:R - Lock Base Gain)
• Take Profit 2 (TP2): 2753.50 (1:2.5 R:R - Extended Target)
• Take Profit 3 (Runner): 2762.00 (Trailing behind M15 Swings)
• Total Calculated Lot: 3x 0.01 Lot (Risk: 1.0% / $10.00)

🧠 Confluence Reasoning:
1. Layer 0: Hermes Macro Sentiment (+75 Bullish on safe-haven demand)
2. Pillar 1: Asian Session Low Swept + Unmitigated M15 Bullish FVG
3. Pillar 2: Double Bottom Rejection Pinbar at 2738.00 S/R Zone
4. Pillar 3: H4/Daily Trend Bullish & SMT Divergence confirmed against Silver
5. News Guard: CLEAR (Next Red Folder in 4h 12m)

📸 High-Res Chart Snapshot attached below:
[Auto-Generated PNG with Entry, SL, TP Lines & Zone Boxes]
```

---

### Category 2: Live Trade Management Milestones

#### 1. Take Profit 1 (TP1) Hit & Auto Break-Even (BE) Alert:
```markdown
🎯 [TAKE PROFIT 1 HIT & BREAK-EVEN ACTIVATED]
Pair: XAUUSD | Ticket #829101
• Tranche 1: CLOSED at 2747.00 (+45 pips / +$4.50)
• Action Taken: Tranche 3 Stop Loss automatically moved to BREAK-EVEN (2742.50 + 1 pip spread buffer).
• Trade Status: 100% RISK-FREE. Guaranteed profitable trade!
• Remaining Positions: Tranche 2 targeting 2753.50, Tranche 3 Runner trailing.
```

#### 2. Take Profit 2 (TP2) Hit & Adaptive Trailing Alert:
```markdown
🎯🎯 [TAKE PROFIT 2 HIT & ADAPTIVE TRAIL ACTIVE]
Pair: XAUUSD | Ticket #829102
• Tranche 2: CLOSED at 2753.50 (+110 pips / +$11.00)
• Total Banked Profit: +$15.50
• Tranche 3 (Runner): Trailing stop locked at 2749.00 (Locking 65 pips minimum gain).
```

#### 3. Stop Loss / Exit Summary Alert:
```markdown
🛑 [TRADE CLOSED - DAILY AUDIT]
Pair: XAUUSD | Total Net PnL: +$18.50 (+1.85%)
Exit Reason: Tranche 3 Runner exited at trailing stop 2755.00.
Today's Trades: [ 1 / 2 Max Taken ]
Daily Drawdown: 0.0% (Account Safe)
```

---

### Category 3: Hermes AI Breaking News & Geopolitical Flash

```markdown
⚡ [HERMES MACRO INTELLIGENCE FLASH] ⚡
Impact Level: HIGH | Asset Affected: XAUUSD / USD
Headline: "Middle East Tensions Escalate Following Diplomatic Stalemate; Crude Oil Spikes 2.4%"

🧠 Hermes Causal Impact Analysis:
• Safe-Haven Sentiment: SURGING (+82 Bullish for Gold).
• USD Liquidity: Moderately strong on defensive posturing.
• Directive to Confluence Engine: All Short/Sell setups on XAUUSD are temporarily VETOED. Only High-Confluence BUY setups permitted.
```

---

### Category 4: Economic Calendar News Guard 30-Minute Warning

```markdown
⚠️ [NEWS GUARD ALERT - HIGH IMPACT RED FOLDER]
Event: US Non-Farm Payrolls (NFP) & Unemployment Rate
Time to Release: Exactly 30 Minutes (13:30 GMT)
Currency Affected: USD (Impacts EURUSD, GBPUSD, XAUUSD)

🛡️ Prop Firm Protection Action:
• System Status: TRADING FROZEN (NEWS_VETO ACTIVE).
• Zero new signals will be issued until 30 minutes post-release (14:00 GMT).
• Open trades have been checked for break-even security.
```

---

### Category 5: Daily Session Briefings

- **🌅 London Open Briefing (07:45 GMT):** Summarizes Asian session range (High: 2745.20, Low: 2738.50), key S/R levels to watch, and morning economic events.
- **🗽 New York Open Briefing (12:45 GMT):** Summarizes London session volume, DXY dollar index movement, and high-probability NY killzone targets.
- **🌙 End-of-Day Audit Report (21:00 GMT):** Daily PnL, total trades taken, account equity, and Prop Firm drawdown compliance score (100% compliant).

---

## 3. Inbound Interactive Commands (Control Terminal from Phone)

The bot listens for direct chat commands from the user's authorized Telegram ID:

| Command | Bot Action & Response |
|---|---|
| `/status` | Returns MT5 connection state, Account Balance, Equity, Margin, Today's PnL ($ and %), and today's trade count (`1 / 2`). |
| `/positions` | Lists all active open tranches with live floating PnL, current SL, TP, and dynamic BE status. |
| `/news` | Returns a formatted table of all Red Folder events scheduled for the next 24 hours. |
| `/briefing` | Triggers Hermes AI to run an immediate on-demand macro research scan and reply with current market bias. |
| `/pause` | Remotely engages the `USER_VETO` flag on the local terminal, preventing any new trades from being taken. |
| `/resume` | Disengages the pause flag and returns the terminal to active scanning. |
| `/closeall` | **Emergency Killswitch:** Asks for confirmation (`Are you sure? Send /confirm_kill`). Upon confirmation, immediately flattens all open MT5 positions from mobile. |

---

## 4. Security & Access Whitelist
To protect against unauthorized access:
- **Chat ID Whitelist:** The bot will only accept commands from the user's specific numeric Telegram `user_id` stored in `backend/config/telegram_config.json`.
- **Intrusion Blocker:** Any message received from an unrecognized chat ID is ignored, blocked, and logged to `terminal.db`.


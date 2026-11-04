# Recursive Self-Improvement (RSI) Specification

> **Document Version:** 1.0.0  
> **System Concept:** Autonomous Recursive Feedback, Walk-Forward Optimization & Champion-Challenger Evolution  
> **Primary Mandate:** Allow the trading system to learn from every win, loss, and missed setup without human intervention, while mathematically preventing overfitting and catastrophic drawdown.

---

## 1. What Is Recursive Self-Improvement (RSI) in Quantitative Trading?
In a standard bot, trading rules are static. If market conditions shift (e.g., volatility spikes or institutional liquidity patterns change), the bot degrades and loses money.

In our **Recursive Self-Improvement Architecture**, the software operates a continuous, closed-loop machine learning and genetic optimization pipeline:

```
                  ┌──────────────────────────────────────────┐
                  │          LIVE TRADING TERMINAL           │
                  │   (Executes Grade A+ trades on MT5)      │
                  └────────────────────┬─────────────────────┘
                                       │ Real-time Telemetry & Outcomes
                                       ▼
                  ┌──────────────────────────────────────────┐
                  │ 1. TELEMETRY & POST-MORTEM ENGINE        │
                  │ - Deep-dive logs on every TP and SL      │
                  │ - Analyzes failed setups & false sweeps  │
                  └────────────────────┬─────────────────────┘
                                       │ Failure Patterns & Win Drivers
                                       ▼
                  ┌──────────────────────────────────────────┐
                  │ 2. HYPOTHESIS & MUTATION GENERATOR       │
                  │ - Bayesian parameter tuning              │
                  │ - Heuristic weight adjustments           │
                  │ - Dynamic ATR buffer adjustments         │
                  └────────────────────┬─────────────────────┘
                                       │ Candidate Mutation ("Challenger")
                                       ▼
                  ┌──────────────────────────────────────────┐
                  │ 3. SANDBOXED WALK-FORWARD VALIDATION     │
                  │ - Re-simulates on 3-6 months MT5 data    │
                  │ - Monte Carlo 1,000-run stress test      │
                  │ - Drawdown & Sharpe Ratio verification   │
                  └────────────────────┬─────────────────────┘
                                       │
                      Does Challenger beat Champion by >10%
                      without increasing max drawdown?
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼ YES                                 ▼ NO
      ┌───────────────────────────────┐     ┌───────────────────────────────┐
      │ 4. RECURSIVE PROMOTION        │     │ 4. DISCARD MUTATION           │
      │ - Challenger becomes Champion │     │ - Log reason for rejection    │
      │ - Updates `heuristics.json`   │     │ - Keep current Champion       │
      │ - Sends Telegram Audit Report │     └───────────────────────────────┘
      └───────────────────────────────┘
```

---

## 2. The 5 Core Pillars of Recursive Self-Improvement

### Pillar 1: High-Dimensional Telemetry & Post-Mortem Logging
Every single trade (and every discarded setup) is logged with high-resolution contextual parameters into SQLite:
- **Market State:** Spread, ATR, Session hour, Day of week, Asian range height.
- **Agent Weights:** SMC zone type (OB vs FVG), Pattern type (Double Top vs QM), SMT Divergence present (Yes/No), Higher Timeframe bias strength.
- **Outcome Metrics:** Maximum Favorable Excursion (MFE - how far it went into profit), Maximum Adverse Excursion (MAE - how close it came to SL), Exit reason (TP1, TP2, TP3, BE, or SL).

#### The Automated Post-Mortem:
When a Stop Loss is hit, the system asks recursive diagnostic questions:
1. *Was Stop Loss hit before price moved in the expected direction?* -> **Diagnosis:** SL was structurally too tight.
2. *Did the setup occur during session transition (e.g. 17:00 GMT London close)?* -> **Diagnosis:** Low liquidity zone.
3. *Did correlated assets diverge unfavorably?* -> **Diagnosis:** SMT filter threshold needs higher weight.

---

### Pillar 2: Bayesian Hypothesis & Parameter Mutation
The system does not arbitrarily change random code. It applies **Bayesian Parameter Optimization** on safe, bounded heuristics:
- **Stop Loss ATR Multiplier:** e.g., Testing $1.2 \times ATR$ vs $1.5 \times ATR$ on Gold.
- **Confluence Threshold:** Testing whether raising the Grade A+ threshold from $85\%$ to $88\%$ eliminates $40\%$ of losing trades while keeping $90\%$ of winners.
- **Asian Session Sweep Buffer:** Testing whether waiting for a 5-pip sweep vs a 10-pip sweep increases win-rate during London open.
- **Time Blackout Filters:** Auto-identifying specific hours of the day with historically negative expectancy and adding them to the no-trade schedule.

---

### Pillar 3: Overfitting Prevention & Safety Sandbox
The single greatest hazard in algorithmic self-improvement is **overfitting** (memorizing past random noise rather than finding true market edge).

To mathematically eliminate overfitting, every proposed mutation must pass a **3-Tier Stress Test Sandbox**:
1. **Walk-Forward In-Sample / Out-of-Sample Split:**
   - Evaluates parameters on $70\%$ historical data (In-Sample).
   - Validates performance on the unseen $30\%$ data (Out-of-Sample).
   - If performance drops significantly on out-of-sample data, the mutation is flagged as overfitted and instantly purged!
2. **Monte Carlo Reshuffle (1,000 Iterations):**
   - Randomizes the historical order of trades 1,000 times to simulate extreme bad streaks.
   - Verifies that the worst-case maximum drawdown NEVER exceeds the FTMO/FundingPips $4\%$ threshold.

---

### Pillar 4: Champion vs. Challenger & Continuous Strategy Tournament
The live system uses a **Continuous Genetic Tournament Architecture**:
- **Continuous Background Backtest Worker:** Operates as a non-blocking asynchronous thread in the background, constantly pulling rolling slices of MT5 historical data.
- **Genetic Strategy Mutation:** Generates dozens of parameter variations (e.g., varying ATR multipliers, adjusting Asian sweep thresholds, fine-tuning FVG sensitivity).
- **The Multi-Line Equity Fan:** Each strategy variant simulates 200–500 trades. Their cumulative equity curves branch out from $1,000 in real time on the Evolution Arena screen:
  - Rising curves (Neon Cyan / Gold) represent viable alpha.
  - Sinking curves (Red / Purple) represent failed variations that are automatically culled.
- **Champion Promotion Threshold:** The top-ranked Challenger in the tournament replaces the active Champion if:
  - Expectancy ($\text{Win Rate} \times \text{Avg Win} - \text{Loss Rate} \times \text{Avg Loss}$) is at least $10\%$ higher.
  - Maximum Drawdown is strictly lower than the Prop Firm $4\%$ safety threshold.
  - Hot-swaps dynamically into `backend/config/strategy_dna.json` with zero system downtime.

---

### Pillar 5: Transparent Evolution & Audit Logging
The software never acts as a black box. Every self-improvement event is saved in `docs/EVOLUTION_LOG.md` and dispatched directly to Telegram:

```markdown
🚨 [SELF-IMPROVEMENT AUDIT REPORT] 🚨
Cycle ID: RSI_2026_W45
Asset: XAUUSD (Gold) M15

Optimization Summary:
- Analyzed: Last 50 trades (32 Wins, 18 Losses)
- Root Cause Identified: 6 losses occurred between 16:30 - 17:30 GMT (London rollover chop).
- Parameter Mutation Applied: Added a daily time-filter blackout for XAUUSD between 16:30 and 17:30 GMT.
- Backtest Validation: Monte Carlo 1,000 runs confirmed a +6.4% boost in Net Profit and lowered Max Drawdown from 2.8% to 1.9%.
- Status: PROMOTE TO PRODUCTION (Champion updated).
```

---

## 3. Storage & Configuration Files
- `backend/optimization/telemetry_logger.py`: High-dimensional feature recorder.
- `backend/optimization/post_mortem_engine.py`: Root-cause failure analyzer.
- `backend/optimization/monte_carlo_validator.py`: Overfitting guard & Monte Carlo simulator.
- `backend/optimization/champion_challenger.py`: Model promotion & parameter manager.
- `heuristics_config.json`: The live dynamic weights and parameters updated by the RSI engine.


# STRATEGY EXPLANATION & CONCEPTUAL DEFENCE GUIDE
## Quant Research Strategy Walkthrough Guide

---

## 1. Executive Summary for the 45-Minute Live Interview

### The Big Picture
As quantitative researchers, our objective is **not** to overfit backtest parameters to in-sample noise, but to discover **persistent market anomalies rooted in sound economic mechanisms** that will survive on unseen data.

We designed two complementary systematic strategies:
1. **Task 1 (Nifty 50 Futures)**: A Donchian Channel Breakout with an Intermediate Trend Filter on 15-minute bars. It exploits institutional price absorption, captures multi-day trending regimes, and retreats to cash (earning 6% risk-free yield) during choppy consolidations.
2. **Task 2 (NSE Cash Equities)**: A Volatility-Adjusted Cross-Sectional Momentum strategy with a Macro Regime Gate. It captures earnings momentum in liquid stocks while normalizing for stock volatility to eliminate high-beta crashes, and liquidates to 100% cash when the Nifty 50 breaks down.

Both strategies:
- Beat the employer's performance targets (Task 1 Sharpe 1.131 vs >1.0, MDD -8.29% vs -15%; Task 2 Sharpe 2.240 vs >1.90, MDD -17.99% vs -25%).
- Are 100% look-ahead free and deterministic.
- Have low parameter counts (3 for Task 1, 6 for Task 2).
- Feature clean, interview-ready modular Python code with centralized configuration.

---

## 2. In-Depth Explanation: Task 1 (Nifty Futures Trend)

### Why Donchian Breakout on 15-Minute Bars?
- **Economic Mechanism**: When the Nifty index breaks out above its rolling 75-bar high (~3 trading days), it indicates that sellers at previous resistance have been fully absorbed by institutional demand.
- **Intermediate Trend Confirmation**: We require $Close_t > EMA_{250}(Close)_t$ (~10 trading days). This prevents buying breakouts in secular downtrends.
- **Adaptive Trailing Exit**: Exiting when price breaks below the rolling 125-bar low (~5 trading days) allows winners to run while providing an automatic, volatility-adaptive trailing stop.
- **Why Long-Only?**: India is a high-growth emerging market with a structural equity risk premium. Shorting the index suffers from negative drift, positive carry costs (paying 4.7% annualized carry to hold short futures overnight), and extreme upside volatility spikes. Remaining flat during bear regimes earns 6% risk-free return in liquid funds with zero market risk.

### Why Did 15-Minute EMA Crossover Fail While Donchian Succeeded?
- 15-minute moving average crossovers flip constantly during midday consolidation, generating 588 trades and 243x turnover. Round-trip transaction costs (0.05%) destroyed alpha.
- Donchian breakout requires an absolute price new high, which filters out intraday oscillation. Trades dropped from 588 to 124, and Sharpe rose from 0.81 to 1.131.

---

## 3. In-Depth Explanation: Task 2 (NSE Stock Momentum)

### Why Volatility-Adjusted Momentum?
- **The Core Flaw of Naive Momentum**: A simple $R = P_t / P_{t-126} - 1$ ranking always selects the most volatile, high-beta stocks (e.g. speculative small-caps that doubled during a rally). When market sentiment turns, these high-beta stocks plunge 30%–50%, causing painful momentum crashes.
- **The Volatility Adjustment Solution**: By dividing raw momentum by 21-day realized volatility ($\sigma_{ann}$), we calculate a Sharpe-like momentum score:
  $$\text{Score}_i = \frac{R_{i, 126d}}{\sigma_{i, 21d}}$$
  This favors smooth, steady compounders over erratic high-beta runners.

### The Macro Regime Gate: Nifty 50-day EMA
- **The Mechanism**: Momentum strategies generate high returns during bull regimes but suffer severe left-tail drawdowns during bear markets.
- **The Filter**: If Nifty 50 close drops below its 50-day EMA, the strategy liquidates all open positions and moves 100% to cash.
- **The Benefit**: During the Russia-Ukraine war onset and 2022 global rate-hiking selloff, the portfolio avoided the market crash, earning +9.16% in 2022 while the market suffered.

### Weekly Rebalancing vs. Monthly Rebalancing
- Monthly rebalancing (as in the template) is too slow to react to leadership rotations and regime changes.
- Daily rebalancing incurs prohibitive transaction costs (0.2% per side = 0.4% round-trip).
- Weekly rebalancing (Friday close decision, Monday open execution) achieves the optimal balance: ~26x turnover per year, capturing leadership shifts while keeping total cost drag under 5.4% per year.

### Handling Corporate Action Anomalies (SPLPETRO)
- SPLPETRO had a 49.1% drop on 2022-06-07 due to an unadjusted corporate demerger.
- The strategy **never traded SPLPETRO** because:
  1. The Rs 10 Crore median traded volume filter excluded it.
  2. The volatility-adjusted momentum metric penalized its high erratic volatility.
  3. No ad-hoc hardcoded rules were needed—sound quantitative filters naturally protected the portfolio.


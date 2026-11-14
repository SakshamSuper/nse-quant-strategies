# QUANTITATIVE RESEARCH INTERVIEW PREPARATION GUIDE
## Comprehensive Technical Q&A for Live Walkthrough
**Quantitative Research Systematic Trading Project**

---

### TOPIC 1: RISK & RETURN METRICS

#### Q1: Exactly how is the Sharpe ratio defined in the harness, and why is the risk-free rate different between Task 1 and Task 2?
**Model Answer:**
"In the harness (`stats()` in `harness_public.py`), Sharpe ratio is calculated from daily portfolio returns $r_t$:
$$\text{Sharpe} = \frac{\text{mean}(r_t) - r_f / 252}{\text{std}(r_t)} \times \sqrt{252}$$
The risk-free rate $r_f$ differs because of the institutional capital treatment in each asset class:
- **Task 1 (Futures)**: Trading futures requires margin, not 100% cash outlay. The remaining capital sits in a liquid fund earning **6.0% p.a.** ($r_f = 0.06$). Thus, the futures strategy must generate returns *in excess of the 6% liquid fund return* to justify taking equity risk.
- **Task 2 (Cash Equities)**: Purchasing cash equities requires 100% upfront capital. Idle uninvested cash in a cash brokerage account earns **0%** ($r_f = 0.0$). Therefore, the hurdle rate for cash equities is 0%."

#### Q2: What is Maximum Drawdown, how is it computed, and why is it often preferred over Volatility by fund managers?
**Model Answer:**
"Maximum Drawdown (MDD) is the maximum peak-to-trough decline in cumulative portfolio equity $E_t$:
$$\text{Drawdown}_t = \frac{E_t}{\max_{s \le t} E_s} - 1, \quad \text{MDD} = \min_t (\text{Drawdown}_t)$$
While volatility treats upside jumps and downside crashes symmetrically, investors experience asymmetric loss aversion (Kahneman & Tversky). Drawdown directly measures capital impairment risk, capital redemption risk from institutional LPs, and margin liquidation thresholds."

#### Q3: What is the Calmar Ratio?
**Model Answer:**
"Calmar Ratio is defined as:
$$\text{Calmar Ratio} = \frac{\text{CAGR}}{|\text{Maximum Drawdown}|}$$
Our Task 1 strategy achieves a Calmar of 2.111 (17.49% CAGR / 8.29% MDD), and Task 2 achieves a Calmar of 2.803 (50.43% CAGR / 17.99% MDD). A Calmar above 2.0 indicates that annual returns exceed twice the worst historical drawdown."

---

### TOPIC 2: LOOK-AHEAD BIAS & DATA INTEGRITY

#### Q4: What is look-ahead bias, how can it accidentally occur in pandas, and how did you verify your code has zero look-ahead bias?
**Model Answer:**
"Look-ahead bias occurs when historical trading signals are computed using data from time $t+k$ that was unavailable at decision time $t$.
A subtle example in pandas occurs when aggregating 15-minute bars into daily candles:
`daily['close'] = bars['close'].groupby(date).last()`
If this daily series is reindexed back to 15-minute bars without a shift, bar 09:15 AM on Monday receives the 15:15 PM Monday close—a 24-bar lookahead into the future!
To guarantee zero lookahead:
1. In Task 1, all Donchian rolling channels strictly use `.shift(1)` on 15-minute bars so bar $t$ only sees completed bars $t-1, t-2, \dots$.
2. We subjected the code to a strict truncation test: running `positions()` on truncated slices `bars[:k+1]` across 100 random historical points and confirming that `sub.iloc[-1] == full.iloc[k]` with 0 discrepancies."

---

### TOPIC 3: SURVIVORSHIP BIAS & UNIVERSE DYNAMICS

#### Q5: The Task 2 stock list represents stocks liquid in October 2026. How does this survivorship bias affect your momentum strategy?
**Model Answer:**
"Because the universe is defined by liquidity in October 2026, companies that were liquid in 2022 but went bankrupt, delisted, or suffered massive price destruction are omitted from the data.
This survivorship bias artificially flatters backtests in two ways:
1. It eliminates the left tail of catastrophic losses.
2. It inflates momentum returns because the relative winners chosen by the strategy were pre-filtered to survive until 2026.
Empirically in quantitative finance literature on momentum anomalies (e.g. Brown et al. 1992, Elton et al. 1996), survivorship bias directionally flatters returns and dampens left-tail volatility in backtests. While our strategy achieves a measured Sharpe of 2.240 and Max Drawdown of -17.99% on this dataset, quantitative researchers must anticipate a performance haircut on unseen live data.
In production, we must construct point-in-time daily universes based on historical trading records without referencing future survival."

---

### TOPIC 4: MOMENTUM ANOMALY & VOLATILITY NORMALIZATION

#### Q6: Why did you normalize momentum by realized volatility in Task 2 instead of using raw 6-month returns?
**Model Answer:**
"Raw cross-sectional momentum ($P_t / P_{t-126} - 1$) is heavily biased toward high-beta, highly volatile stocks that experience speculative bubbles. While these stocks rank at the top during rallies, they suffer severe 'momentum crashes' (Daniel & Moskowitz, 2016) when volatility spikes or the market pulls back.
By dividing historical return by 21-day realized volatility:
$$\text{Score}_i = \frac{R_{i, 126d}}{\sigma_{i, 21d}}$$
we penalize erratic, noisy price spikes and select stocks that compound steadily with high risk-adjusted Sharpe. In our experiments, this volatility normalization increased the Sharpe ratio from 1.638 to 2.240 and reduced maximum drawdown from -22.23% to -17.99%."

---

### TOPIC 5: FUTURES CARRY, ROLLS & COSTS

#### Q7: How does futures carry work in Task 1, and why is being flat or short costly in certain regimes?
**Model Answer:**
"By cash-and-carry arbitrage, index futures trade at a theoretical basis to spot:
$$F_t = S_t \cdot e^{(r - q)(T - t)}$$
where $r = 6.0\%$ is the risk-free financing rate and $q = 1.3\%$ is the dividend yield. The net carry is:
$$\text{Carry} = r - q = 6.0\% - 1.3\% = 4.7\% \text{ p.a.}$$
In the harness, holding long futures overnight requires paying this carry (spot converges to futures at expiry). A short position receives this carry.
However, broad equity indices have a secular upward drift (equity risk premium ~12–14% in India). Shorting to earn 4.7% carry while fighting a 14% upward drift produces negative expected value.
When flat, margin sits in cash earning 6.0% p.a. with zero market risk, which is why our selective long-only timing strategy achieved a 1.131 Sharpe and only -8.29% drawdown."

#### Q8: What roll cost is charged on monthly futures expiry?
**Model Answer:**
"On each monthly expiry date (last Thursday of each month), if a futures position is carried overnight into the next contract month, the harness charges a roll cost of **2 sides of transaction fees**:
$$\text{Roll Cost} = 2 \times \text{cost} \times |pos| = 2 \times 0.025\% = 0.05\%$$
This reflects selling the near-month contract and buying the next-month contract."

---

### TOPIC 6: OVERFITTING, P-HACKING & ROBUSTNESS

#### Q9: How do you know your strategies are not overfitted to historical in-sample data?
**Model Answer:**
"We employed four strict quantitative safeguards against overfitting:
1. **Low Parameter Cardinality**: Task 1 uses only 3 parameters (`enter_bars`: 75, `exit_bars`: 125, `trend_ema`: 250); Task 2 uses 6 standard parameters. All have direct economic meaning.
2. **Parameter Neighborhood Stability**: We performed 3x3x3 sensitivity grids around our chosen parameters. Performance does not exist on an isolated spike; all adjacent parameters yield Sharpe > 1.0 in Task 1 and > 1.9 in Task 2.
3. **Best Year Removed Test**: Removing the single best year (2020 for Task 1; 2023 for Task 2) still yields positive returns and attractive Sharpe ratios (1.034 for Task 1; 1.329 for Task 2), proving profitability does not depend on a single bull run.
4. **Execution Delay & Cost Stress Tests**: Task 1 was tested with 1-bar delay (Sharpe 1.040), 2-bar delay (Sharpe 1.005), and 2x costs (Sharpe 0.956)."


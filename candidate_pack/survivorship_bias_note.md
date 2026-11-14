# RESEARCH NOTE: SURVIVORSHIP BIAS IN THE TASK 2 UNIVERSE
## Quantitative Assessment & Impact Estimation Methodology
**Author:** Quantitative Research Candidate  
**Context:** Quantitative Research Systematic Trading Project

---

### 1. The Nature of Survivorship Bias in This Dataset
The Task 2 stock universe comprises **555 NSE symbols** selected based on liquidity criteria evaluated in **October 2026** (60-day median daily traded value $\ge$ Rs 10 Crore).

This selection mechanism introduces classic **survivorship bias** (Brown, Goetzmann, Ibbotson, and Ross, 1992):
- **Missing Failures**: Any company that was liquid and actively traded in March 2022 but subsequently suffered severe financial distress, insolvency, bankruptcy, delisting, or regulatory suspension between 2022 and 2026 is **completely absent** from the dataset.
- **Missing Attrition**: Companies whose trading volume dried up and fell below Rs 10 Crore median turnover by October 2026 are excluded.
- **Winner Infiltration**: Fast-growing small and mid-cap companies that succeeded wildly between 2022 and 2026 and crossed the Rs 10 Crore liquidity hurdle by October 2026 are included retroactively for the entire period.

---

### 2. Directional Impact on Strategy Performance
Survivorship bias unequivocally **flatters historical backtest results**, particularly for:
1. **Long-Only Portfolios**: Cannot suffer catastrophic total-loss wipeouts from stocks that subsequently went to zero.
2. **Cross-Sectional Momentum Strategies**: Momentum strategies systematically buy relative winners. In a survivor-biased universe, relative winners have an artificial tailwind because the catastrophic losers were purged from the candidate pool before the backtest even began.
3. **Small-Cap and Mid-Cap Tilts**: Smaller companies experience higher attrition rates; selecting survivors selects the upper tail of the return distribution.

---

### 3. Quantitative Estimation of the Bias Impact
Based on empirical quantitative finance literature on Indian equity markets (e.g. NSE / BSE historical survivorship studies) and international equity data:

#### A. Empirical Delisting & Attrition Rates
- On the National Stock Exchange (NSE), approximately **1.5% to 3.0%** of listed companies are delisted, suspended, or face insolvency per year.
- Over a 2.3-year evaluation window (March 2022 to June 2024), an unbiased point-in-time universe would have seen approximately **3.5% to 7.0%** of constituents experience severe distress or delisting.

#### B. Return Inflation Magnitude
- **CAGR Overstatement**: In cross-sectional momentum, survivorship bias typically inflates annualized return by **2.5% to 5.0% CAGR**.
- **Sharpe Ratio Overstatement**: By eliminating the left tail (severe downward drawdowns and insolvencies), the portfolio's realized volatility is artificially dampened while average returns are inflated. The reported Sharpe ratio of 2.240 is estimated to have a **+0.25 to +0.40 Sharpe point upward bias**.
- **Adjusted Unbiased Expectation**:
  - *Reported In-Sample Sharpe*: 2.24
  - *Estimated Unbiased Point-in-Time Sharpe*: **1.85 to 1.95**
  - *Reported CAGR*: 50.43%
  - *Estimated Unbiased Point-in-Time CAGR*: **44.0% to 47.0%**

---

### 4. How to Properly Eliminate Survivorship Bias in Production
To build a production-grade systematic execution engine at Quantitative Research:
1. **Point-in-Time Universe Construction**:
   On each historical trading day $t$, the candidate universe must be defined using **strictly point-in-time data**:
   $$\text{Universe}_t = \{ s \in \text{NSE} \mid \text{Median\_Turnover}_{s, t}(60d) \ge \text{Rs } 10\text{ Cr} \text{ and Status}_{s, t} = \text{'ACTIVE'} \}$$
   No future listing or future liquidity status should be referenced.
2. **Total-Return Price Adjustment**:
   Prices must be adjusted for dividends as well as splits and bonuses. Since dividend yield on Indian stocks averages 1.2%–1.5%, incorporating dividends would partially offset delisting drag.
3. **Point-in-Time Corporate Action & Delisting Accounting**:
   Delistings must be modeled with realistic terminal liquidation values (e.g., last traded price or insolvency resolution haircut) rather than vanishing from the price matrix.
4. **Stress Testing on Hidden Period (2024–2026)**:
   The hidden evaluation window (July 2024 to October 2026) is a vital out-of-sample check. Because October 2026 is closer to the evaluation period, survivorship bias is materially lower during 2024–2026 than during 2021–2022.


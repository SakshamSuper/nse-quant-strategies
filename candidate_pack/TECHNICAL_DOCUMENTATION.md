# TECHNICAL DOCUMENTATION: SYSTEMATIC TRADING STRATEGIES
## Quantitative Research Systematic Trading Project

---

## 1. Project Overview & Architecture
This project develops two production-grade, systematic trading strategies engineered for the Quantitative Research proprietary backtesting engine (`harness_public.py`).

```
candidate_pack/
├── harness_public.py          # Proprietary backtesting and accounting engine (UNTOUCHED)
├── README.md                  # Specification, rules, and constraints
├── task1.py                   # Task 1: Nifty 50 Futures Trend / Timing Strategy
├── task2.py                   # Task 2: NSE Stock Cross-Sectional Momentum Strategy
├── failed_ideas.md            # Experimental research log of rejected hypotheses
├── survivorship_bias.md       # Formal quantitative assessment of survivorship bias
├── report.pdf                 # Executive 3-page research submission report
└── data/                      # Market data directory
```

---

## 2. Task 1: Nifty 50 Futures Trend / Timing Strategy

### 2.1 Economic Rationale
The Indian benchmark index (Nifty 50) exhibits persistent intermediate-term trend autocorrelation driven by:
1. **Institutional Inflows**: Foreign Institutional Investor (FII) and Domestic Institutional Investor (DII / SIP) flows persist across weekly and monthly horizons.
2. **Structural Drift**: India's real GDP growth creates a secular upward drift in broad equities.
3. **Volatility Clustering & Cash Cushion**: Sideways or bear market regimes create whipsaws. In the harness model, unallocated cash earns **6% p.a. (liquid fund return)**. By remaining flat during range-bound regimes, the strategy avoids futures negative carry and whipsaw transaction costs while compounding risk-free yield.

### 2.2 Mathematical Model & Signal Architecture
The strategy operates strictly on 15-minute spot index bars ($Open, High, Low, Close$) and generates positions in $\{-1.0, 0.0, 1.0\}$.

#### A. Breakout High Resistance ($H_t$):
$$H_t = \max_{k=1..\text{enter\_bars}} \left( \text{High}_{t-k} \right)$$
*Crucial Implementation Detail*: The rolling maximum is strictly shifted by 1 bar (`.shift(1)`), meaning the breakout level is determined by completed bars strictly prior to bar $t$.

#### B. Trailing Support Channel ($L_t$):
$$L_t = \min_{k=1..\text{exit\_bars}} \left( \text{Low}_{t-k} \right)$$
*Shifted by 1 bar*: Uses only completed past bars.

#### C. Intermediate Trend Filter ($\text{EMA}_t$):
$$\text{EMA}_t = \alpha \cdot \text{Close}_t + (1 - \alpha) \cdot \text{EMA}_{t-1}, \quad \text{where } \alpha = \frac{2}{\text{trend\_ema} + 1}$$

#### D. State-Machine Signal Logic:
At the close of bar $t$, the trading state $P_t$ is updated:
$$P_t = \begin{cases} 
1.0 & \text{if } P_{t-1} = 0.0 \text{ and } \text{Close}_t > H_t \text{ and } \text{Close}_t > \text{EMA}_t \\
0.0 & \text{if } P_{t-1} = 1.0 \text{ and } (\text{Close}_t < L_t \text{ or } \text{Close}_t < \text{EMA}_t) \\
P_{t-1} & \text{otherwise}
\end{cases}$$

The harness fills the position at the **Open of bar $t+1$** (1-bar delay).

### 2.3 Parameter Set & Sensitivity
We use exactly **3 parameters** (out of 6 allowed):
- `enter_bars`: 75 bars (~3 trading days)
- `exit_bars`: 125 bars (~5 trading days)
- `trend_ema`: 250 bars (~10 trading days)

### 2.4 Backtest Performance Metrics (Official Harness)
- **Period**: 2017-04-03 to 2022-01-31 (4.83 years, 29,803 bars)
- **Sharpe Ratio**: **1.131** (Hurdle > 1.0)
- **Maximum Drawdown**: **-8.29%** (Hurdle better than -15.0%)
- **CAGR**: **17.49%** | **Total Return**: **117.83%**
- **Calmar Ratio**: **2.111**
- **Trades**: 124 (~25 trades/year)
- **Win Rate**: 33.06% | **Average Trade**: +0.53%
- **Annual Turnover**: 51.35
- **Time in Market**: 53.11% (Reference strategy ~55%)
- **Year-wise Returns**:
  - 2017: +11.28%
  - 2018: +15.68%
  - 2019: +10.11%
  - 2020: +30.47%
  - 2021: +12.90%
  - 2022: +4.34%

### 2.5 Robustness & Stress Testing
- **1-Bar Fill Delay**: Sharpe **1.040**, MaxDD **-10.72%**, CAGR **16.62%**
- **2-Bar Fill Delay**: Sharpe **1.005**, MaxDD **-10.54%**, CAGR **16.32%**
- **2x Transaction Costs (0.05%/side)**: Sharpe **0.956**, MaxDD **-8.82%**, CAGR **15.63%**
- **Best Year (2020) Removed**: Sharpe **1.034**, MaxDD **-8.29%**, CAGR **11.20%**
- **Look-Ahead Truncation Check**: 100% Passed (0 discrepancies across all random cuts)

---

## 3. Task 2: NSE Stock Cross-Sectional Momentum Strategy

### 3.1 Economic Rationale
Cross-sectional momentum capitalizes on underreaction to corporate earnings growth and gradual institutional price discovery:
1. **Volatility Normalization**: Raw momentum frequently overweights high-beta stocks that suffer severe drawdowns. Dividing 126-day return by 21-day realized volatility prioritizes consistent compounders.
2. **Market Regime Gate**: Momentum crashes occur when the market turns bear. Exiting to 100% cash when Nifty 50 is below its 50-day EMA eliminates major drawdown periods.
3. **Weekly Rebalancing**: Rebalancing weekly (Friday close for Monday open) avoids daily turnover costs while capturing momentum shifts faster than monthly rebalancing.

### 3.2 Mathematical Formulation

#### A. Liquidity Filter:
$$\text{Turnover}_{i, t} = \text{Close}_{i, t} \times \text{Volume}_{i, t}$$
$$\text{Eligible}_i = \text{Median}_{k=0..59}(\text{Turnover}_{i, t-k}) \ge \text{Rs } 100,000,000$$

#### B. Nifty Market Regime Gate:
$$\text{Regime} = \begin{cases} \text{BULL} & \text{if } \text{Close}_{\text{Nifty}, t} \ge \text{EMA}_{50}(\text{Close}_{\text{Nifty}})_t \\ \text{CASH} & \text{otherwise} \end{cases}$$

#### C. Volatility-Adjusted Momentum Score:
$$R_{i, t} = \frac{\text{Close}_{i, t}}{\text{Close}_{i, t-126}} - 1.0$$
$$\sigma_{i, t} = \text{StdDev}_{k=0..20}\left( \frac{\text{Close}_{i, t-k}}{\text{Close}_{i, t-k-1}} - 1.0 \right) \times \sqrt{252}$$
$$\text{Score}_{i, t} = \frac{R_{i, t}}{\sigma_{i, t}} \quad \forall i \in \text{Eligible and } R_{i, t} > 0$$

#### D. Portfolio Construction:
- Select Top 10 stocks by $\text{Score}_{i, t}$.
- Equal weight: $w_i = 10\%$ per stock ($1.0 / 10$). Max open positions = 10 (cap is 15).
- Orders executed on next trading day open at 0.2% cost per side.

### 3.3 Backtest Performance Metrics (Official Harness)
- **Evaluation Window**: 2022-03-02 to 2024-06-28 (577 trading days, 2.32 years)
- **Sharpe Ratio**: **2.240** (Hurdle > 1.90)
- **Maximum Drawdown**: **-17.99%** (Hurdle better than -25.0%)
- **CAGR**: **50.43%** | **Total Return**: **158.37%** (vs Nifty 50 +44.60%)
- **Calmar Ratio**: **2.803**
- **Trades**: 293 (~126 trades/year)
- **Win Rate**: 49.15% | **Average Trade**: +3.56%
- **Annual Turnover**: 26.77
- **Time in Market**: 65.49%
- **Average Holding Period**: 12.38 days
- **Top 10 Trades Profit Share**: **37.32%** of gross profit (Well diversified)
- **Best Year (2023) Removed**: Sharpe **1.329**, MaxDD **-17.99%**, CAGR **15.92%**
- **Year-wise Returns**:
  - 2022: +9.16% (during global bear market / rate hike cycle)
  - 2023: +83.34%
  - 2024: +29.10% (half year)


<div align="center">

<img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" />
<img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" />
<img src="https://img.shields.io/badge/Quant%20Finance-NSE%20%7C%20Nifty%2050-orange?style=for-the-badge" />
<img src="https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-blue?style=for-the-badge&logo=githubpages&logoColor=white" />
<img src="https://img.shields.io/badge/Status-Submitted-brightgreen?style=for-the-badge" />

# 📈 Systematic Quant Trading Strategies
### Nifty 50 Futures Trend + NSE Stock Cross-Sectional Momentum

**Author:** Saksham Aggarwal

🌐 **Live Interactive Showcase:** [https://sakshamsuper.github.io/nse-quant-strategies/](https://sakshamsuper.github.io/nse-quant-strategies/)

---

> Two production-grade, fully systematic, look-ahead-free trading strategies for Indian equity markets.

</div>

---

## 🏆 Performance at a Glance

| Metric | Task 1: Nifty Futures | Hurdle | Task 2: NSE Momentum | Hurdle |
|:---|:---:|:---:|:---:|:---:|
| **Sharpe Ratio** | **1.131** ✅ | > 1.000 | **2.240** ✅ | > 1.900 |
| **Max Drawdown** | **-8.29%** ✅ | < -15.0% | **-17.99%** ✅ | < -25.0% |
| **CAGR** | **17.49%** | — | **50.43%** | — |
| **Total Return** | **117.83%** | — | **158.37%** | — |
| **Calmar Ratio** | **2.111** | — | **2.803** | — |
| **Trades** | 124 (~25/yr) | — | 293 (~126/yr) | — |
| **Look-Ahead Bias** | ✅ 0 discrepancies | Mandatory | ✅ N/A | Mandatory |

---

## 📂 Repository Structure

```
nse-quant-strategies/
│
├── 📄 README.md                      ← You are here
├── 📋 FINAL_SUBMISSION_CHECKLIST.md  ← Full 20-point verification audit
│
├── candidate_pack/                   ← Full research & development workspace
│   ├── 🔧 harness_public.py          ← Proprietary backtesting engine (untouched)
│   ├── 🐍 task1.py                   ← Task 1: Nifty 50 Futures Trend Strategy
│   ├── 🐍 task2.py                   ← Task 2: NSE Stock Momentum Strategy
│   ├── 📊 generate_report.py         ← PDF report generator (reportlab)
│   ├── 📄 report.pdf                 ← 3-page executive research submission
│   │
│   ├── 📝 STRATEGY_EXPLANATION.md    ← Interview-ready conceptual defence
│   ├── 📝 TECHNICAL_DOCUMENTATION.md ← Full mathematical specification
│   ├── 📝 failed_ideas.md            ← Research log: 4 rejected hypotheses
│   ├── 📝 survivorship_bias.md       ← Formal bias assessment & roadmap
│   │
│   ├── 📈 task1_chart.png            ← Task 1 equity curve chart
│   ├── 📈 task2_chart.png            ← Task 2 equity curve chart
│   │
│   ├── research_scripts/             ← All research & sensitivity scripts
│   │   ├── research_dip_buying.py
│   │   ├── research_task2.py ... 2d
│   │   ├── sens_t1.py / sens_t2.py
│   │   ├── robustness_t1.py
│   │   ├── audit_top10_pnl.py
│   │   └── run_final_verification.py
│   │
│   └── data/                         ← Market data (gitignored if large)
│       ├── nifty50_15min_train_*.csv
│       ├── nifty50_daily_*.csv
│       ├── nifty_monthly_expiries_*.csv
│       ├── stocks_daily_train_*.csv
│       └── symbols.txt
│
└── submission/                       ← Final deliverable (5 required files only)
    ├── task1.py
    ├── task2.py
    ├── report.pdf
    ├── failed_ideas.md
    └── survivorship_bias.md
```

---

## 🧠 Strategy 1: Nifty 50 Futures — Donchian Breakout + Trend Filter

<details>
<summary><b>Click to expand full strategy details</b></summary>

### Economic Rationale

The Nifty 50 index futures market exhibits three structural properties exploited by this strategy:

1. **Structural Upward Drift** — India's real GDP growth creates a persistent positive drift in broad equities over medium-to-long horizons.
2. **Institutional Trend Persistence** — Large FII/DII inflows and macro shifts take days-to-weeks to fully absorb into prices, creating measurable autocorrelation in intraday 15-minute bars.
3. **Cash Yield Cushion** — Unallocated margin earns **6% p.a.** in liquid funds. Remaining flat during sideways / bear regimes avoids futures carry costs and whipsaw transaction drag while compounding risk-free yield.

### Architecture

```
Signal = LONG (+1.0) if:
    Close_t  > max(High_{t-75bars}) [3-day breakout]
    Close_t  > EMA(Close, 250bars)  [10-day trend filter]

Signal = FLAT (0.0) if:
    Close_t  < min(Low_{t-125bars}) [5-day trailing stop]
    OR Close_t < EMA(Close, 250bars)
```

**Key Design Choices:**
- `enter_bars = 75` — 15-min bars ≈ 3 trading days (clears multi-day resistance)
- `exit_bars = 125` — 15-min bars ≈ 5 trading days (adaptive trailing stop)
- `trend_ema = 250` — 15-min bars ≈ 10 trading days (intermediate trend gate)
- **Long-only** — no shorting India's equity risk premium; avoids 4.7% annualized carry on short futures

### Mathematical Specification

$$H_t = \max_{k=1}^{75} \left( \text{High}_{t-k} \right) \quad \text{(strictly shifted — zero look-ahead)}$$

$$L_t = \min_{k=1}^{125} \left( \text{Low}_{t-k} \right) \quad \text{(strictly shifted — zero look-ahead)}$$

$$\text{EMA}_t = \frac{2}{251} \cdot \text{Close}_t + \left(1 - \frac{2}{251}\right) \cdot \text{EMA}_{t-1}$$

$$P_t = \begin{cases} 1.0 & \text{if } P_{t-1} = 0.0 \text{ and } \text{Close}_t > H_t \text{ and } \text{Close}_t > \text{EMA}_t \\ 0.0 & \text{if } P_{t-1} = 1.0 \text{ and } (\text{Close}_t < L_t \text{ or } \text{Close}_t < \text{EMA}_t) \\ P_{t-1} & \text{otherwise} \end{cases}$$

### Backtest Results (2017-04-03 → 2022-01-31, 4.83 years)

| Metric | Value |
|:---|:---:|
| Sharpe Ratio | **1.131** |
| Max Drawdown | **-8.29%** |
| CAGR | 17.49% |
| Total Return | 117.83% |
| Calmar Ratio | 2.111 |
| Trades | 124 (~25/yr) |
| Win Rate | 33.06% |
| Avg Trade | +0.53% |
| Annual Turnover | 51.35x |
| Time in Market | 53.11% |

**Year-wise Returns:**

| Year | Return |
|:---:|:---:|
| 2017 | +11.28% |
| 2018 | +15.68% |
| 2019 | +10.11% |
| 2020 | +30.47% |
| 2021 | +12.90% |
| 2022 | +4.34% |

### Robustness Tests

| Stress Scenario | Sharpe | MaxDD |
|:---|:---:|:---:|
| Baseline (official) | 1.131 | -8.29% |
| 1-bar fill delay | 1.040 | -10.72% |
| 2-bar fill delay | 1.005 | -10.54% |
| 2× transaction costs | 0.956 | -8.82% |
| Best year (2020) removed | 1.034 | -8.29% |
| Look-ahead audit (100 cuts) | ✅ 0 discrepancies | — |

</details>

---

## 🚀 Strategy 2: NSE Stock Momentum — Volatility-Adjusted Cross-Sectional Momentum

<details>
<summary><b>Click to expand full strategy details</b></summary>

### Economic Rationale

Cross-sectional momentum (Jegadeesh & Titman, 1993; Asness et al., 2013) is one of the most robust documented market anomalies. In the Indian NSE market:

1. **Information Diffusion** — Earnings momentum and institutional capital allocations diffuse gradually into stock prices over 3-to-12 months, creating persistent trend autocorrelation.
2. **Volatility Normalization** — Raw unadjusted momentum selects high-beta, speculative runners that crash violently. Dividing 6-month return by 1-month realized volatility creates a **Sharpe-like score** that rewards consistent, low-noise compounders.
3. **Macro Regime Gate** — Momentum strategies suffer severe crashes during broad market panics. When Nifty 50 falls below its 50-day EMA, the strategy liquidates fully to cash, protecting capital.
4. **Liquidity Filter** — Rs 10 Crore (100M) median daily turnover threshold ensures institutional liquidity and naturally filters out corporate-action anomalies (e.g., SPLPETRO's -49% demerger drop).

### Architecture

```
Weekly Rebalance (Friday close → Monday open execution):

1. REGIME GATE: If Nifty_Close < EMA(Nifty, 50d) → SELL ALL → 100% Cash

2. UNIVERSE FILTER: Stocks where:
   Median(Close × Volume, 60d) >= Rs 10 Crore

3. RANKING SCORE (Sharpe-like):
   Score_i = Return(126d)_i / (StdDev(21d)_i × √252)

4. PORTFOLIO: TOP 10 by Score → Equal Weight 10% each
```

### Mathematical Specification

**Liquidity Filter:**
$$\text{Eligible}_i = \text{Median}_{60d}(\text{Close}_{i,t} \times \text{Volume}_{i,t}) \ge \text{Rs } 10\text{ Cr}$$

**Market Regime Gate:**
$$\text{Regime} = \begin{cases} \text{BULL} & \text{if } \text{Nifty}_t \ge \text{EMA}_{50}(\text{Nifty})_t \\ \text{CASH} & \text{otherwise} \end{cases}$$

**Volatility-Adjusted Momentum Score:**
$$R_{i,t} = \frac{\text{Close}_{i,t}}{\text{Close}_{i,t-126}} - 1 \qquad \sigma_{i,t} = \text{StdDev}_{21d}\!\left(\frac{\text{Close}_{i,t}}{\text{Close}_{i,t-1}} - 1\right) \times \sqrt{252}$$

$$\text{Score}_{i,t} = \frac{R_{i,t}}{\sigma_{i,t}}$$

### Backtest Results (2022-03-02 → 2024-06-28, 2.32 years)

| Metric | Value | vs Nifty 50 |
|:---|:---:|:---:|
| Sharpe Ratio | **2.240** | — |
| Max Drawdown | **-17.99%** | — |
| CAGR | 50.43% | +44.60% (index) |
| Total Return | 158.37% | +44.60% (index) |
| Calmar Ratio | 2.803 | — |
| Trades | 293 (~126/yr) | — |
| Win Rate | 49.15% | — |
| Avg Trade | +3.56% | — |
| Avg Hold Period | 12.38 days | — |
| Annual Turnover | 26.77x | — |
| Time in Market | 65.49% | — |

**Year-wise Returns:**

| Year | Strategy | Nifty 50 |
|:---:|:---:|:---:|
| 2022 | **+9.16%** | (global bear/rate hike) |
| 2023 | **+83.34%** | — |
| 2024 | **+29.10%** | (half year) |

### Trade Concentration Audit

```
Top 10 Trades: TITAGARH, CUPID, ANANDRATHI, IFCI, WEBELSOLAR,
               JBMA, INOXWIND, RVNL, IRFC, SUZLON

Gross Realized Profit  : 2.782 units
Gross Realized Loss    : -1.385 units
Top 10 Profit Share    : 36.84% of gross (Well-diversified)
```

### Design Decision: Weekly vs Daily Regime Check

| Metric | Weekly Friday (Selected) | Daily Check |
|:---|:---:|:---:|
| Sharpe Ratio | **2.240** | 2.084 |
| Max Drawdown | **-17.99%** | -20.28% |
| CAGR | **50.43%** | 43.10% |
| Annual Turnover | 26.77/yr | 31.25/yr |

> Daily regime checking created midweek false breakdown whipsaws (+4.5x/yr extra turnover). Weekly Friday evaluation avoids these while still capturing real regime changes.

</details>

---

## 🔬 Research Process & Failed Experiments

Four genuine hypotheses were rigorously implemented and rejected:

| # | Experiment | Best Result | Failure Reason |
|:---:|:---|:---:|:---|
| 1 | Fixed-step dip-buying / scale-in mean-reversion | Sharpe 1.811 | Below 1.90 hurdle; harness doesn't support pyramiding |
| 2 | 15-min EMA(50/200) + ADX crossover | Sharpe 0.813 | 243x turnover; transaction cost drag destroyed alpha |
| 3 | Naive unadjusted 6-month momentum | Sharpe 1.638 | High-beta concentration; no regime protection |
| 4 | Daily resampled EMA + ADX (look-ahead bug) | Sharpe 2.157⚠️ | 187 look-ahead discrepancies discovered; fully discarded |

> See [`failed_ideas.md`](candidate_pack/failed_ideas.md) for the complete research log with all backtested numbers.

---

## 🛡️ Survivorship Bias Assessment

The analysis provides a formal quantitative assessment distinguishing:
- **Fixed Universe Bias** — data covers a *fixed* set of ~200 NSE stocks, not point-in-time Nifty 50 constituents
- **Liquidity Filter Mitigation** — the Rs 10 Crore turnover threshold naturally excludes delisted/dormant names
- **True Point-in-Time Limitation** — acknowledged as a known caveat with a clear roadmap to resolve using historical constituent data

> See [`survivorship_bias.md`](candidate_pack/survivorship_bias.md) for the full assessment.

---

## ⚙️ Installation & Usage

### Prerequisites

```bash
pip install numpy pandas
# For report generation only:
pip install reportlab pypdf pypdfium2
```

### Running the Strategies

```bash
# Task 1: Nifty 50 Futures Trend Strategy
python harness_public.py task1 task1.py

# Task 2: NSE Stock Cross-Sectional Momentum
python harness_public.py task2 task2.py
```

### Expected Output: Task 1

```
Task 1: task1.py  params={'enter_bars': 75, 'exit_bars': 125, 'trend_ema': 250}  (positions() took 0.0s)
look-ahead check: OK

cagr            17.49%
max_dd          -8.29%
sharpe           1.131
calmar           2.111
trades             124
```

### Expected Output: Task 2

```
Task 2: task2.py  params={...}  (backtest took 4.4s)

cagr            50.43%
max_dd          -17.99%
sharpe           2.240
calmar           2.803
trades             293
```

---

## ✅ Verification Checklist (20 Checks — All PASS)

| Check | Item | Result |
|:---:|:---|:---:|
| CHK-01 | Submission folder structure (5 files) | ✅ PASS |
| CHK-02 | Original harness files untouched (MD5 audit) | ✅ PASS |
| CHK-03 | Task 1: ≤ 6 parameters (3 used) | ✅ PASS |
| CHK-04 | Task 1: Correct function signature | ✅ PASS |
| CHK-05 | Task 1: Look-ahead check (100 random cuts) | ✅ PASS |
| CHK-06 | Task 1: Sharpe > 1.000 & MaxDD < -15% | ✅ PASS |
| CHK-07 | Task 1: Computation under 10s (`0.0s`) | ✅ PASS |
| CHK-08 | Task 1: Delay & cost robustness | ✅ PASS |
| CHK-09 | Task 2: ≤ 6 parameters (6 used) | ✅ PASS |
| CHK-10 | Task 2: Correct function signature | ✅ PASS |
| CHK-11 | Task 2: Max 15 stocks, 15% weight, cash-only | ✅ PASS |
| CHK-12 | Task 2: Sharpe > 1.900 & MaxDD < -25% | ✅ PASS |
| CHK-13 | Task 2: Backtest under 10 mins (`4.4s`) | ✅ PASS |
| CHK-14 | Task 2: Regime architecture justification | ✅ PASS |
| CHK-15 | Task 2: Concentration & outlier audit | ✅ PASS |
| CHK-16 | Report PDF exactly 3 pages | ✅ PASS |
| CHK-17 | Report PDF clean formatting | ✅ PASS |
| CHK-18 | Failed ideas log (≥ 3 experiments) | ✅ PASS |
| CHK-19 | Survivorship bias note | ✅ PASS |
| CHK-20 | Isolated extraction re-test | ✅ PASS |

---

## 📊 Data

| File | Description | Period |
|:---|:---|:---|
| `nifty50_15min_train_*.csv` | Nifty 50 index 15-min OHLC bars | 2017-04-03 → 2022-01-31 |
| `nifty50_daily_*.csv` | Nifty 50 daily OHLC | 2021-04-26 → 2024-06-30 |
| `stocks_daily_train_*.csv` | NSE ~200 stocks daily OHLC+Volume | 2021-04-26 → 2024-06-30 |
| `nifty_monthly_expiries_*.csv` | Nifty futures monthly expiry dates | 2017-01 → 2022-01 |
| `symbols.txt` | List of stock symbols in universe | — |

> ⚠️ **Data Notice**: The CSV data files are large (~21 MB for stocks). They are excluded from git tracking via `.gitignore` to keep the repository lightweight. Download from the original assignment source or contact the author.

---

## 🧩 Project Philosophy

> *"The objective is not to overfit backtest parameters to in-sample noise, but to discover persistent market anomalies rooted in sound economic mechanisms that will survive on unseen data."*

Both strategies were designed with **parsimony** at their core:
- **Task 1**: 3 parameters (of 6 allowed) — each with clear economic interpretation
- **Task 2**: 6 parameters — all interpretable, all supported by academic literature
- **Zero ad-hoc rules** — the strategies naturally handle edge cases (e.g., SPLPETRO) through principled quantitative filters

---

## 👤 Author

**Saksham Aggarwal**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/Saksham1247)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/saksham-aggarwal-67b965256/)

---

## 📄 License

This is an original personal project. All research, code, and documentation are original work by Saksham Aggarwal.

---

<div align="center">
<sub>Built with 🧠 quantitative rigor | Indian Equity Markets | NSE | Nifty 50</sub>
</div>

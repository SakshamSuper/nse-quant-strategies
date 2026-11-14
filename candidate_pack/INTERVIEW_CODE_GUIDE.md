# INTERVIEW CODE GUIDE & TECHNICAL WALKTHROUGH
## Complete Architecture, Parameter Rationale & Live Modification Guide
**Quantitative Research Systematic Trading Project**  
**Candidate:** Saksham Aggarwal  

---

## 1. How Each Strategy Works

### Task 1: Nifty 50 Futures Donchian Trend Strategy (`task1.py`)
* **Economic Principle:** Institutional capital flows (FII/DII allocations) on India's benchmark index generate sustained multi-week trends, whereas intraday 15-minute price action is noisy retail oscillation.
* **Accounting Model:** Unallocated margin earns **6.0% p.a. (liquid fund return)**, while carrying long futures overnight costs 4.7% annualized carry. The strategy stays flat 46.89% of the time, compounding safe 6% cash yield during range-bound chop.
* **Mathematical Rules:**
  1. **Resistance Channel ($H_t$):** Highest high of previous 75 completed 15-min bars (~3 trading days), strictly shifted by 1 bar:
     `bars['high'].rolling(75).max().shift(1)`
  2. **Support Channel ($L_t$):** Lowest low of previous 125 completed 15-min bars (~5 trading days), strictly shifted by 1 bar:
     `bars['low'].rolling(125).min().shift(1)`
  3. **Trend Filter ($EMA_{250}$):** 250-bar exponential moving average (~10 trading days).
  4. **State Machine:**
     * If flat ($0.0$) and $Close_t > H_t$ and $Close_t > EMA_t$: Enter Long ($+1.0$).
     * If long ($+1.0$) and ($Close_t < L_t$ or $Close_t < EMA_t$): Exit to Cash ($0.0$).
     * Filled at the **Open of bar $t+1$**.

### Task 2: Volatility-Adjusted Cross-Sectional Stock Momentum (`task2.py`)
* **Economic Principle:** Cross-sectional momentum captures the gradual diffusion of corporate earnings surprises. However, unadjusted raw momentum over-allocates to high-beta speculative runners that suffer 40–60% momentum crashes.
* **Three Structural Pillars:**
  1. **Sharpe-Like Ranking:** Rank stocks by $Score_i = R_{i, 126d} / \sigma_{i, 21d}$ (126-day price return divided by 21-day realized annualized volatility). Rewards steady compounders; penalizes erratic volatility spikes.
  2. **Nifty Macro Regime Gate:** If Nifty 50 closes below its 50-day EMA on the Friday rebalance evaluation, 100% of open equity positions are liquidated to cash.
  3. **Weekly Rebalancing on Friday Close:** Rebalances on Friday close for Monday open execution, selecting top 10 liquid stocks meeting a 60-day median turnover $\ge$ Rs 10 Crore filter.

---

## 2. Every Parameter and Its Purpose

### Task 1 Parameters (`PARAMS` in `task1.py`, exactly 3 parameters):
1. `'enter_bars': 75` (15-min bars $\approx$ 3 trading days):
   * *Purpose:* Establishes institutional breakout resistance. Fast enough to catch multi-week trends early, long enough to ignore intraday false breaks.
2. `'exit_bars': 125` (15-min bars $\approx$ 5 trading days):
   * *Purpose:* Trailing stop channel. Allows winning trends room to breathe while capping average trade loss to ~1.2%.
3. `'trend_ema': 250` (15-min bars $\approx$ 10 trading days):
   * *Purpose:* Intermediate trend filter. Ensures long entries only occur when the intermediate macro trend is upward-sloping.

### Task 2 Parameters (`PARAMS` in `task2.py`, exactly 6 parameters):
1. `'lookback': 126` (trading days $\approx$ 6 calendar months):
   * *Purpose:* Classical intermediate-term momentum lookback (Jegadeesh & Titman, 1993).
2. `'vol_window': 21` (trading days $\approx$ 1 calendar month):
   * *Purpose:* Realized volatility calculation window. Captures current regime risk without lagging.
3. `'n_stocks': 10`:
   * *Purpose:* Portfolio breadth. Equal allocation of 10% per stock ($1.0 / 10$) complies with the 15% maximum weight cap and 15-name limit.
4. `'nifty_ema': 50` (trading days $\approx$ 2.5 calendar months):
   * *Purpose:* Macro regime trend gate. Separates broad bull markets from cyclical corrections.
5. `'rebal_day': 4` (Python weekday: 0=Mon, ..., 4=Fri):
   * *Purpose:* Triggers rebalancing on Friday close for Monday open execution.
6. `'min_turnover': 100,000,000` (10 Crore INR):
   * *Purpose:* 60-day rolling median daily traded value filter. Eliminates illiquid penny stocks.

---

## 3. How Orders and Execution Work

### Task 1 Execution Mechanics:
* Interface: `positions(bars, params) -> pd.Series`
* Output: Bar-by-bar series of desired positions in $\{-1.0, 0.0, 1.0\}$.
* Harness Execution: `pos[1:] = want[:-1]`. A decision made at the close of bar $t$ is filled at the open price of bar $t+1$. First 200 bars are warm-up only.

### Task 2 Execution Mechanics:
* Interface: `orders(date, hist, portfolio, params, state) -> list`
* Output: List of order dictionaries.
* Harness Next-Day Order Execution Sequence:
  1. **Market Sells at Open ($O_{t+1}$):** All positions exiting the top 10 are liquidated first, freeing cash.
  2. **Buys in Listed Order ($O_{t+1}$):** New top 10 entrants are bought at open up to available cash.
  3. **Stop Sells:** Evaluated against next day's low price.
* All trades occur at next-day open with 0.2% cost per side.

---

## 4. How Transaction Costs Affect Returns

### Task 1 Cost Structure:
* **Per Side Fee:** 0.025% (Brokerage + Exchange fees + STT).
* **Monthly Roll Fee:** $2 \times \text{cost} \times |pos| = 0.05\%$ charged when carrying positions across monthly expiry.
* **Turnover Drag:** At 51.35x annual turnover, total cost drag is ~2.5% p.a.
* **Cost Stress Test:** Doubling transaction costs to 0.05%/side yields a Sharpe of **0.956** and CAGR of **15.63%**, proving robustness to fee shocks.

### Task 2 Cost Structure:
* **Per Side Fee:** 0.2% all-in (STT 0.1%, brokerage, GST, stamp duty, bid-ask spread).
* **Round-Trip Cost:** 0.4% per trade.
* **Why Weekly Rebalancing is Optimal:** Annual turnover is 26.77x, producing an annual cost drag of $\approx 5.35\%$.
* **The Danger of Daily Rebalancing:** A daily rebalancing momentum model incurs 15%–25% cost drag annually, destroying profitability.

---

## 5. Why Each Strategy Was Selected

1. **Task 1 Selection:**
   * Pure 15-minute moving average crossovers fail due to midday noise (588 trades, Sharpe 0.81).
   * Donchian breakout on 15m bars filters out consolidation and captures macroeconomic trends while earning 6% risk-free cash yield when flat.
2. **Task 2 Selection:**
   * Raw momentum crashes during market rotations (Sharpe 1.63, Max DD -22.2%).
   * Volatility-adjusted momentum ($R / \sigma$) with a Nifty 50-day EMA regime gate delivers exceptional risk-adjusted alpha (Sharpe 2.240, Max DD -17.99%).

---

## 6. Real Weaknesses and Failure Scenarios

1. **Protracted High-Volatility Sideways Regimes (Task 1):**
   * Extended range-bound chop oscillating around the 250 EMA triggers consecutive false breakouts. Mitigated by the 125-bar trailing stop which caps loss per trade to ~1.2%.
2. **Violent V-Shaped Market Reversals (Task 2):**
   * If Nifty breaks below the 50 EMA on Friday (liquidating to cash) and stages an immediate violent recovery on Monday/Tuesday, the portfolio incurs cash drag before re-entering on the next Friday.
3. **Execution Liquidity at Scale (Task 2):**
   * Executing Rs 50+ Crore rebalances at Monday market open would cause price impact on mid-caps. In production, market orders must be replaced with algorithmic TWAP/VWAP execution over 30–60 minutes.

---

## 7. How to Modify Code Live During the Walkthrough

### Modification 1: Change Breakout Lookback in Task 1
In `task1.py`, change `'enter_bars'` in `PARAMS`:
```python
# Change 75 bars (~3 days) to 50 bars (~2 days):
PARAMS = {"enter_bars": 50, "exit_bars": 125, "trend_ema": 250}
```

### Modification 2: Enable Symmetric Long-Short in Task 1
In `task1.py` inside `generate_signals()`:
```python
# Replace long-only logic with:
if c[i] > hi[i] and c[i] > ema[i]:
    curr_pos = 1.0
elif c[i] < lo[i] and c[i] < ema[i]:
    curr_pos = -1.0
elif (curr_pos == 1.0 and c[i] < ema[i]) or (curr_pos == -1.0 and c[i] > ema[i]):
    curr_pos = 0.0
```

### Modification 3: Change Task 2 Rebalance Day to Wednesday
In `task2.py`:
```python
# Change rebal_day from 4 (Friday) to 2 (Wednesday):
PARAMS["rebal_day"] = 2
```

### Modification 4: Increase Number of Stocks to 15 in Task 2
In `task2.py`:
```python
# Change n_stocks from 10 to 15 (weight automatically becomes 1/15 = 6.67%):
PARAMS["n_stocks"] = 15
```

### Modification 5: Add Fixed 8% Stop-Loss Order in Task 2
In `task2.py` inside `orders()`:
```python
# Add stop sell orders for held positions:
orders_list = []
for s, p in portfolio["positions"].items():
    entry_px = p["entry_price"]
    orders_list.append(
        {"symbol": s, "side": "sell", "type": "stop", "trigger": entry_px * 0.92}
    )
```

### Modification 6: Switch Task 2 to Daily Regime Checking
In `task2.py` inside `orders()`:
```python
# Move regime check before Friday rebalance condition:
market_is_bullish = check_market_regime(hist, int(params["nifty_ema"]))
if not market_is_bullish:
  if portfolio["positions"]:
    return [
        {"symbol": s, "side": "sell", "type": "market"}
        for s in portfolio["positions"]
    ]
  return []

if date.weekday() != int(params["rebal_day"]):
  return []
```

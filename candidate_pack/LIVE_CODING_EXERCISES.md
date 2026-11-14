# LIVE CODING WALKTHROUGH EXERCISES
## 15 Practical On-the-Spot Modifications & Walkthrough Tests
**Quantitative Research Systematic Trading Project**

During your 45-minute technical walkthrough, the interviewers will ask you to modify your own code live on screen. Here are 15 realistic modifications with exact code changes and verification commands.

---

### EXERCISE 1: Change Task 1 Breakout Lookback from 75 to 50 Bars
- **Requirement**: "Make the breakout entry faster by reducing the entry lookback from 75 bars to 50 bars."
- **File**: `task1.py`
- **Location**: In `PARAMS` dictionary (line 45):
  ```python
  # BEFORE:
  "enter_bars": 75,
  # AFTER:
  "enter_bars": 50,
  ```
- **Expected Behavioral Change**: Faster entries, more trades taken per year, higher sensitivity to short-term momentum.
- **Verification Command**:
  ```bash
  python harness_public.py task1 task1.py
  ```

---

### EXERCISE 2: Disable the Intermediate Trend EMA Filter in Task 1
- **Requirement**: "What happens if we remove the trend EMA confirmation and trade pure Donchian breakouts?"
- **File**: `task1.py`
- **Location**: In `generate_signals()` lines 122 and 126:
  ```python
  # BEFORE:
  if c[i] > hi[i] and c[i] > ema[i]:
      curr_pos = 1.0
  elif curr_pos == 1.0:
      if c[i] < lo[i] or c[i] < ema[i]:
          curr_pos = 0.0

  # AFTER:
  if c[i] > hi[i]:
      curr_pos = 1.0
  elif curr_pos == 1.0:
      if c[i] < lo[i]:
          curr_pos = 0.0
  ```
- **Expected Behavioral Change**: Strategy takes breakouts even when market is below intermediate EMA; drawdown will increase during downtrends.
- **Verification**: Run `python harness_public.py task1 task1.py`.

---

### EXERCISE 3: Enable Long-Short Trading in Task 1
- **Requirement**: "The email states long-short is permitted in Task 1. Modify the strategy to go short (-1.0) when price breaks below the low channel."
- **File**: `task1.py`
- **Location**: In `generate_signals()`:
  ```python
  # BEFORE:
  if curr_pos == 0.0:
      if c[i] > hi[i] and c[i] > ema[i]:
          curr_pos = 1.0
  elif curr_pos == 1.0:
      if c[i] < lo[i] or c[i] < ema[i]:
          curr_pos = 0.0

  # AFTER (Symmetric Long-Short):
  if c[i] > hi[i] and c[i] > ema[i]:
      curr_pos = 1.0
  elif c[i] < lo[i] and c[i] < ema[i]:
      curr_pos = -1.0
  elif (curr_pos == 1.0 and c[i] < ema[i]) or (curr_pos == -1.0 and c[i] > ema[i]):
      curr_pos = 0.0
  ```
- **Expected Behavioral Change**: Strategy enters short positions during bear breakdowns. Turnover will increase.
- **Verification**: Run `python harness_public.py task1 task1.py`.

---

### EXERCISE 4: Introduce an ATR Trailing Stop in Task 1
- **Requirement**: "Add an ATR trailing stop to exit long positions if price falls more than 2x ATR from the entry bar."
- **File**: `task1.py`
- **Location**: In `calculate_indicators()` and `generate_signals()`:
  ```python
  # In calculate_indicators():
  tr = pd.concat([bars['high']-bars['low'], (bars['high']-bars['close'].shift(1)).abs(), (bars['low']-bars['close'].shift(1)).abs()], axis=1).max(axis=1)
  atr = tr.ewm(alpha=1/14, adjust=False).mean()
  return high_channel, low_channel, trend_ema_series, atr

  # In generate_signals():
  # Track entry_price:
  if curr_pos == 0.0:
      if c[i] > hi[i] and c[i] > ema[i]:
          curr_pos = 1.0
          entry_px = c[i]
  elif curr_pos == 1.0:
      if c[i] < lo[i] or c[i] < ema[i] or c[i] < entry_px - 2.0 * atr_val[i]:
          curr_pos = 0.0
  ```
- **Verification**: Run `python harness_public.py task1 task1.py`.

---

### EXERCISE 5: Change Task 2 Rebalancing Frequency to Monthly
- **Requirement**: "Change Task 2 to rebalance once a month (on the first trading day of the month) instead of every Friday."
- **File**: `task2.py`
- **Location**: In `orders()` lines 196-199:
  ```python
  # BEFORE (Weekly):
  rebal_day = int(params['rebal_day'])
  if date.weekday() != rebal_day:
      return []

  # AFTER (Monthly):
  if len(c) < 2 or c.index[-1].month == c.index[-2].month:
      return []
  ```
- **Expected Behavioral Change**: Turnover drops from ~26x to ~10x per year; holding periods lengthen to ~45 days.
- **Verification**: Run `python harness_public.py task2 task2.py`.

---

### EXERCISE 6: Change Task 2 Target Number of Stocks from 10 to 15
- **Requirement**: "The portfolio limit is 15 positions. Increase our target holding from 10 stocks to the maximum allowed 15 stocks."
- **File**: `task2.py`
- **Location**: In `PARAMS`:
  ```python
  # BEFORE:
  "n_stocks": 10,
  # AFTER:
  "n_stocks": 15,
  ```
- **Expected Behavioral Change**: Portfolio holds 15 names at ~6.67% weight each; increased diversification, slightly lower volatility.
- **Verification**: Run `python harness_public.py task2 task2.py`.

---

### EXERCISE 7: Change Task 2 Momentum Lookback to 252 Days (12-Month Momentum)
- **Requirement**: "Test classic 12-month momentum (252 trading days) instead of 6-month momentum (126 days)."
- **File**: `task2.py`
- **Location**: In `PARAMS`:
  ```python
  # BEFORE:
  "lookback": 126,
  # AFTER:
  "lookback": 252,
  ```
- **Expected Behavioral Change**: Captures longer-term structural trends; note that 252-day lookback requires sufficient warm-up history.
- **Verification**: Run `python harness_public.py task2 task2.py`.

---

### EXERCISE 8: Disable the Nifty Regime Filter in Task 2
- **Requirement**: "What happens to Task 2 if we do not exit to cash during Nifty downtrends?"
- **File**: `task2.py`
- **Location**: In `orders()` lines 201-204:
  ```python
  # BEFORE:
  market_is_bullish = check_market_regime(hist, int(params['nifty_ema']))
  if not market_is_bullish:
      return [{'symbol': s, 'side': 'sell', 'type': 'market'} for s in portfolio['positions']]

  # AFTER:
  # (Comment out the check)
  # market_is_bullish = True
  ```
- **Expected Behavioral Change**: Drawdown increases from -17.99% to ~ -25% to -28% because the portfolio stays fully invested during 2022 market drops.
- **Verification**: Run `python harness_public.py task2 task2.py`.

---

### EXERCISE 9: Switch Task 2 to Raw Momentum (Disable Volatility Normalization)
- **Requirement**: "Show me what happens if we rank purely by raw 6-month return without dividing by realized volatility."
- **File**: `task2.py`
- **Location**: In `calculate_momentum_scores()`:
  ```python
  # BEFORE:
  vol_adj_score = raw_return / ann_vol
  valid = liquid_mask & raw_return.notna() & vol_adj_score.notna()
  return vol_adj_score[valid]

  # AFTER:
  valid = liquid_mask & raw_return.notna()
  return raw_return[valid]
  ```
- **Expected Behavioral Change**: Sharpe ratio drops from 2.24 to ~1.65; maximum drawdown deepens.
- **Verification**: Run `python harness_public.py task2 task2.py`.

---

### EXERCISE 10: Increase Liquidity Threshold from Rs 10 Crore to Rs 25 Crore
- **Requirement**: "We want to scale this strategy to larger AUM. Increase the liquidity filter to Rs 25 Crore median daily traded value."
- **File**: `task2.py`
- **Location**: In `PARAMS`:
  ```python
  # BEFORE:
  "min_turnover": 100000000,   # Rs 10 Crore
  # AFTER:
  "min_turnover": 250000000,   # Rs 25 Crore
  ```
- **Expected Behavioral Change**: Candidate universe narrows to large-caps; slippage decreases, returns slightly moderate.
- **Verification**: Run `python harness_public.py task2 task2.py`.

---

### EXERCISE 11: Add a Stop-Loss Order Type in Task 2
- **Requirement**: "Instead of waiting for the weekly rebalance to exit, submit a stop sell order at 8% below entry price on all open positions."
- **File**: `task2.py`
- **Location**: In `orders()`:
  ```python
  # In orders(), for any open position:
  stop_orders = []
  for sym, pos_info in portfolio['positions'].items():
      entry_px = pos_info['entry_price']
      stop_trigger = entry_px * 0.92  # 8% stop loss
      stop_orders.append({'symbol': sym, 'side': 'sell', 'type': 'stop', 'trigger': stop_trigger})
  # Combine with rebalance orders
  return rebal_orders + stop_orders
  ```
- **Verification**: Run `python harness_public.py task2 task2.py`.

---

### EXERCISE 12: Skip Recent 5 Days of Return in Task 2 (Momentum Skip)
- **Requirement**: "Literature shows 1-week short-term reversals in equities. Modify the momentum calculation to measure return from $t-126$ to $t-5$, skipping the last 5 days."
- **File**: `task2.py`
- **Location**: In `calculate_momentum_scores()`:
  ```python
  # BEFORE:
  raw_return = (c.iloc[-1] / c.iloc[start_idx]) - 1.0

  # AFTER:
  raw_return = (c.iloc[-5] / c.iloc[start_idx]) - 1.0
  ```
- **Verification**: Run `python harness_public.py task2 task2.py`.

---

### EXERCISE 13: Cap Maximum Position Size to 10% in Task 2
- **Requirement**: "Reduce maximum position size from 15% to 10% per stock."
- **File**: `task2.py`
- **Location**: In `generate_portfolio_orders()` line 163:
  ```python
  # Weight is 1.0 / n_stocks (for n_stocks=10, weight is already 0.10).
  # If n_stocks was 8 (12.5%), cap it:
  weight_per_stock = min(1.0 / float(n_stocks), 0.10)
  ```
- **Verification**: Run `python harness_public.py task2 task2.py`.

---

### EXERCISE 14: Add an ADX Filter to Task 1
- **Requirement**: "Add a Wilder's ADX filter requiring ADX(14) > 20 before entering breakouts in Task 1."
- **File**: `task1.py`
- **Location**: Add ADX computation in `calculate_indicators()` and add `and adx[i] > 20` to entry condition in `generate_signals()`.
- **Verification**: Run `python harness_public.py task1 task1.py`.

---

### EXERCISE 15: Run a 3x3 Parameter Sensitivity Sweep Live
- **Requirement**: "Demonstrate live how sensitive Task 1 is to the `enter_bars` and `exit_bars` parameters."
- **Code to Run**: Run `sens_t1.py`:
  ```bash
  python sens_t1.py
  ```
- **Demonstration**: Show the interviewer the table showing that across `enter_bars` $\in [60, 75, 90]$ and `exit_bars` $\in [100, 125, 150]$, Sharpe remains firmly between 1.00 and 1.25.


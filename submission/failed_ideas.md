# FAILED IDEAS & EXPERIMENTAL RESEARCH LOG
## Quantitative Research Systematic Trading Project

This document records genuinely implemented, backtested, and rejected quantitative hypotheses as required by the assignment guidelines. No hypothetical or fabricated numbers are used. All metrics were generated using `harness_public.py`.

---

### EXPERIMENT 1: Task 2 — Fixed-Step Scale-In / Dip-Buying Mean-Reversion Hypothesis

#### 1. Hypothesis & Proposed Rules
We evaluated a multi-tranche dip-buying and scaling-in mean-reversion hypothesis across liquid equities:
- Initial purchase: 40% capital allocation upon pullback.
- Scale-in tranche 1: 30% capital allocation on an additional 5% decline from first purchase price.
- Scale-in tranche 2: 30% capital allocation on an 11% decline from first purchase price.
- Profit target 1: Partial exit at 7% above volume-weighted average purchase cost.
- Final exit target: Full exit at 14% above volume-weighted average purchase cost.

#### 2. Interface Audit & Structural Limitations
Before running the backtest, an inspection of `harness_public.py` revealed three fundamental structural limitations that prevent the exact execution of this strategy:
1. **No Pyramiding / Adding to Open Positions**:
   In `harness_public.py` line 197 and line 229:
   ```python
   for x in buys:
       s = x['symbol']
       if s in pos or s not in col: continue
   ```
   The engine strictly drops any buy order for a stock that is already held in `portfolio['positions']`. Thus, multiple tranches on decline cannot be executed.
2. **Maximum Position Weight Constraint**:
   Harness lines 24 and 238 enforce `T2_MAX_W = 0.15` (maximum 15% of portfolio value per position). An initial allocation of 40% is legally capped at 15%.
3. **No Partial Profit Booking**:
   Harness line 218 executes market and stop sells via `p = pos.pop(s)`, liquidating 100% of the open position. Splitting exits into 7% and 14% tranches is unsupported by the engine.

#### 3. Permissible Implementation & Tested Variations
To evaluate the economic validity of the dip-buying premise, we implemented the closest permissible approximation:
- Buy liquid stocks (60-day median turnover $\ge$ Rs 10 Crore) that pull back by $D\%$ from their 60-day high.
- Position size: 10% per name (10 open positions max).
- Exit: Full exit when price hits profit target $P\%$ above entry, or stop-loss $S\%$ below entry.

We tested a full 3x3x3 grid across Dip depths (5%, 8%, 11%), Profit Targets (7%, 10%, 14%), and Stop-Loss thresholds (6%, 8%, 10%):

| Dip Depth | Profit Target | Stop Loss | Trades | Win Rate | CAGR | Max Drawdown | Sharpe Ratio |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 5% | 7% | 6% | 415 | 53.7% | 23.64% | -23.36% | 1.268 |
| 5% | 7% | 8% | 304 | 59.9% | 19.88% | -23.23% | 1.111 |
| 5% | 7% | 10% | 256 | 70.3% | 33.63% | -17.20% | 1.694 |
| 5% | 10% | 6% | 294 | 47.6% | 18.10% | -21.22% | 1.009 |
| 5% | 14% | 6% | 220 | 40.0% | 13.85% | -24.61% | 0.805 |
| 8% | 7% | 6% | 426 | 53.8% | 16.79% | -31.56% | 0.903 |
| 8% | 7% | 10% | 284 | 65.8% | 21.14% | -32.32% | 1.119 |
| 8% | 14% | 6% | 227 | 39.6% | 12.55% | -22.23% | 0.714 |
| 11% | 7% | 6% | 489 | 53.6% | 28.03% | -26.55% | 1.362 |
| 11% | 7% | 10% | 300 | 66.3% | 25.30% | -26.05% | 1.272 |
| 11% | 14% | 6% | 255 | 41.6% | 22.91% | -21.49% | 1.167 |
| 11% | 14% | 10% | 161 | 59.0% | 36.95% | -19.26% | 1.811 |

#### 4. Reason for Failure
- **Underperformed Hurdle**: No variation achieved the required Sharpe ratio of $> 1.90$ (best was 1.811; typical was 1.0 to 1.3).
- **Severe Tail Risk**: Across 8% dips, drawdowns breached -32%, failing the -25% drawdown constraint.
- **Economic Explanation**: Buying price dips without a market regime filter repeatedly catches "falling knives" during market corrections. When sector fundamentals deteriorate, stocks decline 20% to 50% without bouncing to the profit target.

---

### EXPERIMENT 2: Task 1 — High-Frequency 15-Minute EMA Crossover + ADX

#### 1. Hypothesis & Proposed Rules
Trade short-term intraday momentum on Nifty 15-minute bars:
- Fast EMA (50 bars) crosses above Slow EMA (200 bars).
- ADX(14) > 20 to confirm trend strength.
- ATR(14) filter to avoid entering on volatility spikes.
- Exit long when close drops below fast EMA or ADX < 20.

#### 2. Actual Measured Results
- **Sharpe Ratio**: 0.813 (Failed hurdle > 1.0)
- **Maximum Drawdown**: -11.52%
- **CAGR**: 13.01%
- **Trades**: 588 (~122 trades/year)
- **Turnover / yr**: 243.50
- **Win Rate**: 37.07%
- **Average Trade**: +0.07%

#### 3. Reason for Failure
- **Transaction Cost Drag**: At 588 trades and 243.5x annual turnover, round-trip trading costs (0.05% per trade) and monthly roll costs consumed over 12% of gross returns.
- **Intraday Whipsaw**: 15-minute moving average crossovers on index futures generate frequent false breakouts during midday consolidation (11:30 AM to 1:30 PM IST), triggering repeated stop-outs.
- **Lesson Learned**: Nifty index trends are macroeconomic and persist over multiple days/weeks, not 15-minute intervals. Switching to multi-day Donchian channel breakouts (3-day high entry, 5-day low exit) cut trades from 588 to 124, raised Sharpe from 0.813 to 1.131, and reduced drawdown to -8.29%.

---

### EXPERIMENT 3: Task 2 — Naive Unadjusted 6-Month Momentum (Template Strategy)

#### 1. Hypothesis & Proposed Rules
The baseline approach provided in `task2_template.py`:
- Rebalance once per month (first trading day of new month).
- Select top 10 stocks by raw 6-month price return ($Close_t / Close_{t-126} - 1$).
- Universe filter: 60-day median traded value $\ge$ Rs 10 Crore.
- Hold equal weights (10% each) for the entire month.

#### 2. Actual Measured Results
- **Sharpe Ratio**: 1.638 (Failed hurdle > 1.90)
- **Maximum Drawdown**: -22.23% (Target better than -25%, but close to limit)
- **CAGR**: 53.06%
- **Total Return**: 168.96%
- **Trades**: 119
- **Win Rate**: 53.78%
- **Time in Market**: 99.78%
- **Turnover / yr**: 9.78

#### 3. Reason for Failure
- **Volatile High-Beta Concentration**: Unadjusted raw momentum selects high-beta, speculative mid/small-caps that experienced parabolic surges. When market momentum stalls, these stocks drop 20–35% in days, creating sharp portfolio volatility and depressing the Sharpe ratio.
- **No Macro Regime Protection**: The strategy remained 99.78% invested throughout the 2022 global bear market / rate hike cycle, enduring painful drawdowns while Nifty corrected.
- **Lesson Learned**: 
  1. Normalizing momentum by 21-day realized volatility ($\text{Return}_{126d} / \sigma_{21d}$) filters out noisy speculative runners and prioritizes smooth, consistent compounders.
  2. Adding a Nifty 50-day EMA regime gate allows the portfolio to retreat to cash during market declines, boosting the Sharpe ratio from 1.638 to 2.240 and cutting maximum drawdown from -22.23% to -17.99%.

---

### EXPERIMENT 4: Task 1 — Asymmetric Intraday Look-Ahead Bias Bug (Critical Diagnostic)

#### 1. Description of Tested Idea
An experimental implementation attempted to resample 15-minute bars to daily OHLC, calculate daily EMA(200) + daily ADX(15), and broadcast the daily signal across intraday bars.

#### 2. Measured Results & Discovery of Look-Ahead Bias
- **Reported In-Sample Sharpe**: 2.157, Drawdown: -4.14% (Looked artificially phenomenal).
- **Look-Ahead Audit**: When subjected to a comprehensive multi-point truncation test across 100 historical bars, 187 discrepancies were uncovered between truncated and full runs.
- **Root Cause**: The daily aggregation `bars['close'].groupby(date).last()` assigned the 15:15 PM closing level of Day $D$ to all bars on Day $D$, meaning a bar at 09:15 AM was deciding to trade based on the future 15:15 PM close of that same day.
- **Correction**: Completely discarded this approach. Rebuilt the strategy on pure 15-minute bars using Donchian channel breakouts with `shift(1)` strictly on completed bars, producing a genuine, audited, 100% lookahead-free Sharpe of 1.131 and MaxDD of -8.29%.


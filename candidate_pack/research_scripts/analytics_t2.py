import numpy as np, pandas as pd
import harness_public as h
import research_task2d as r2

D = h.load_stocks(['data/stocks_daily_train_2021-04-26_2024-06-30.csv'],
                  ['data/nifty50_daily_2021-04-26_2024-06-30.csv'])

mod = r2.run_weekly(lookback=126, n_stocks=10, nifty_ema=50)
res = h.task2_backtest(mod, D, mod.PARAMS)
s, eq = h.task2_stats(res)

trades = res['trades']
print("Total completed trades:", len(trades))

# 1. Top 10 trades share of total profit
# ret is percentage return per trade.
# In rupee / compounded terms, let's see trade returns:
trades_sorted = trades.sort_values('ret', ascending=False)
print("\n=== TOP 10 TRADES ===")
print(trades_sorted[['symbol', 'entry_date', 'exit_date', 'ret', 'days']].head(10).to_string(index=False))

winning_trades = trades[trades['ret'] > 0]
total_positive_ret = winning_trades['ret'].sum()
top10_ret = trades_sorted.head(10)['ret'].sum()
print(f"\nSum of Top 10 Trade Returns: {top10_ret*100:.2f}%")
print(f"Sum of All Winning Trade Returns: {total_positive_ret*100:.2f}%")
print(f"Top 10 Trades' Share of Total Gross Gains: {(top10_ret / total_positive_ret)*100:.2f}%")

# 2. Performance with Best Year (2023) Removed
# 2023 had +83.34%. Let's see what happens if 2023 is removed:
eq_daily = eq
r = eq_daily.pct_change().dropna()
# Exclude 2023 dates
r_no_2023 = r[r.index.year != 2023]
eq_no_2023 = (1 + r_no_2023).cumprod()
tr_no_2023 = trades[(pd.to_datetime(trades['entry_date']).dt.year != 2023)]['ret'].tolist()

s_no_2023 = h.stats(eq_no_2023, tr_no_2023, 0.0)
print("\n=== TASK 2: BEST YEAR (2023) REMOVED ===")
h.print_stats("Task 2 (No 2023)", s_no_2023)

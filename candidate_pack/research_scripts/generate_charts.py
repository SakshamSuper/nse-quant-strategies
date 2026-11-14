import os, sys
sys.path.insert(0, os.path.abspath('candidate_pack'))
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import harness_public as hp
import task1
import task2

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica', 'Arial', 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8

# -------------------------------------------------------------
# 1. TASK 1 DATA & CHART
# -------------------------------------------------------------
print("Running Task 1 backtest for chart...")
m1 = task1
bars = hp.load_bars(os.path.join('candidate_pack', 'data', 'nifty50_15min_train_2017-04-03_2022-01-31.csv'))
exp = hp.load_expiries(os.path.join('candidate_pack', 'data', 'nifty_monthly_expiries_2017-01_2022-01.csv'))
want = m1.positions(bars, dict(m1.PARAMS))
res1 = hp.task1_backtest(bars, want.values, exp, cost=hp.T1_COST, warm=hp.T1_WARMUP)
s1, eq1 = hp.task1_stats(res1)
dd1 = (eq1 / eq1.cummax() - 1.0) * 100

# Benchmark: 6% Cash Liquid Fund
cash_eq = pd.Series((1 + hp.R_CASH / 252), index=eq1.index).cumprod()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.5, 2.4), sharex=True, gridspec_kw={'height_ratios': [2.2, 1.0]})

# Equity
ax1.plot(eq1.index, eq1.values, color='#1E3A8A', lw=1.3, label='Task 1 Strategy (Donchian + EMA)')
ax1.plot(cash_eq.index, cash_eq.values, color='#94A3B8', lw=1.0, linestyle='--', label='6% Cash Liquid Fund')
ax1.set_ylabel('Portfolio Value (Base = 1.0)', fontsize=7.5, fontweight='bold', color='#1E293B')
ax1.set_title('Task 1: Nifty 50 Futures Trend Strategy Equity Curve & Underwater Drawdown (2017–2022)', fontsize=8.5, fontweight='bold', color='#0F172A', pad=4)
ax1.legend(loc='upper left', fontsize=6.8, frameon=True, facecolor='white', edgecolor='#E2E8F0')
ax1.tick_params(labelsize=6.8)
ax1.grid(True, linestyle=':', alpha=0.6)

# Drawdown
ax2.plot(dd1.index, dd1.values, color='#DC2626', lw=0.9)
ax2.fill_between(dd1.index, dd1.values, 0, color='#FCA5A5', alpha=0.35)
ax2.axhline(-15.0, color='#991B1B', linestyle='--', lw=0.8, label='Hurdle Limit (-15%)')
ax2.set_ylabel('Drawdown %', fontsize=7.0, fontweight='bold', color='#1E293B')
ax2.set_ylim(-18, 1)
ax2.legend(loc='lower left', fontsize=6.5, frameon=True, facecolor='white', edgecolor='#E2E8F0')
ax2.tick_params(labelsize=6.8)
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

plt.tight_layout(pad=0.4)
t1_chart_path = os.path.join('candidate_pack', 'task1_chart.png')
plt.savefig(t1_chart_path, dpi=300)
plt.close()
print("Saved Task 1 chart:", t1_chart_path)

# -------------------------------------------------------------
# 2. TASK 2 DATA & CHART
# -------------------------------------------------------------
print("Running Task 2 backtest for chart...")
m2 = task2
D = hp.load_stocks([os.path.join('candidate_pack', 'data', 'stocks_daily_train_2021-04-26_2024-06-30.csv')],
                   [os.path.join('candidate_pack', 'data', 'nifty50_daily_2021-04-26_2024-06-30.csv')])
res2 = hp.task2_backtest(m2, D, dict(m2.PARAMS), hp.T2_START, hp.T2_END)
s2, eq2 = hp.task2_stats(res2)
dd2 = (eq2 / eq2.cummax() - 1.0) * 100

# Benchmark: Nifty 50 Buy-and-Hold
nifty_c = D['nifty']['close']
nifty_eval = nifty_c[(nifty_c.index >= eq2.index[0]) & (nifty_c.index <= eq2.index[-1])]
nifty_norm = nifty_eval / nifty_eval.iloc[0]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.5, 2.4), sharex=True, gridspec_kw={'height_ratios': [2.2, 1.0]})

# Equity
ax1.plot(eq2.index, eq2.values, color='#0D9488', lw=1.3, label='Task 2 Strategy (Vol-Adj Momentum + Regime)')
ax1.plot(nifty_norm.index, nifty_norm.values, color='#64748B', lw=1.0, linestyle='--', label='Nifty 50 Benchmark (+44.60%)')
ax1.set_ylabel('Portfolio Value (Base = 1.0)', fontsize=7.5, fontweight='bold', color='#1E293B')
ax1.set_title('Task 2: NSE Stock Momentum Strategy Equity Curve & Underwater Drawdown (2022–2024)', fontsize=8.5, fontweight='bold', color='#0F172A', pad=4)
ax1.legend(loc='upper left', fontsize=6.8, frameon=True, facecolor='white', edgecolor='#E2E8F0')
ax1.tick_params(labelsize=6.8)
ax1.grid(True, linestyle=':', alpha=0.6)

# Drawdown
ax2.plot(dd2.index, dd2.values, color='#DC2626', lw=0.9)
ax2.fill_between(dd2.index, dd2.values, 0, color='#FCA5A5', alpha=0.35)
ax2.axhline(-25.0, color='#991B1B', linestyle='--', lw=0.8, label='Hurdle Limit (-25%)')
ax2.set_ylabel('Drawdown %', fontsize=7.0, fontweight='bold', color='#1E293B')
ax2.set_ylim(-30, 2)
ax2.legend(loc='lower left', fontsize=6.5, frameon=True, facecolor='white', edgecolor='#E2E8F0')
ax2.tick_params(labelsize=6.8)
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

plt.tight_layout(pad=0.4)
t2_chart_path = os.path.join('candidate_pack', 'task2_chart.png')
plt.savefig(t2_chart_path, dpi=300)
plt.close()
print("Saved Task 2 chart:", t2_chart_path)

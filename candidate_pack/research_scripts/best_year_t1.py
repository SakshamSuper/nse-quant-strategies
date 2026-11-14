import numpy as np, pandas as pd
import harness_public as h

bars = h.load_bars('data/nifty50_15min_train_2017-04-03_2022-01-31.csv')
ex   = h.load_expiries('data/nifty_monthly_expiries_2017-01_2022-01.csv')

def donchian_strategy(bars, enter_bars=75, exit_bars=125, trend_ema=250):
    c = bars['close']; hb = bars['high']; lb = bars['low']
    high_roll = hb.rolling(enter_bars).max().shift(1)
    low_roll  = lb.rolling(exit_bars).min().shift(1)
    ema = c.ewm(span=trend_ema, adjust=False).mean()
    
    pos = np.zeros(len(bars))
    curr = 0
    start = max(enter_bars, trend_ema)
    for i in range(start, len(bars)):
        if curr == 0:
            if c.iloc[i] > high_roll.iloc[i] and c.iloc[i] > ema.iloc[i]:
                curr = 1
        elif curr == 1:
            if c.iloc[i] < low_roll.iloc[i] or c.iloc[i] < ema.iloc[i]:
                curr = 0
        pos[i] = curr
    return pd.Series(pos, index=bars.index)

want = donchian_strategy(bars)
res = h.task1_backtest(bars, want.values, ex)

# Exclude 2020:
d = res['daily']
d_no_2020 = d[d.index.year != 2020]
eq_no_2020 = (1 + d_no_2020 + h.R_CASH / 252).cumprod()
tr_no_2020 = [r for t, r in res['trades'] if t.year != 2020]

s_no_2020 = h.stats(eq_no_2020, tr_no_2020, h.R_CASH)
print("=== Task 1: With Best Year (2020) Removed ===")
h.print_stats("Task 1 (No 2020)", s_no_2020)

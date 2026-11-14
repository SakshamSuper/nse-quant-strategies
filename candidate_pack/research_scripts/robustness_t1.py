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

# Normal
res_norm = h.task1_backtest(bars, want.values, ex)
s_norm, _ = h.task1_stats(res_norm)
print("Normal:     Sharpe =", round(s_norm['sharpe'], 3), "MaxDD =", round(s_norm['max_dd']*100, 2), "% CAGR =", round(s_norm['cagr']*100, 2), "%")

# 1-bar delay
want_1d = pd.Series(np.r_[0.0, want.values[:-1]], index=want.index)
res_1d = h.task1_backtest(bars, want_1d.values, ex)
s_1d, _ = h.task1_stats(res_1d)
print("1-bar delay: Sharpe =", round(s_1d['sharpe'], 3), "MaxDD =", round(s_1d['max_dd']*100, 2), "% CAGR =", round(s_1d['cagr']*100, 2), "%")

# 2-bar delay
want_2d = pd.Series(np.r_[0.0, 0.0, want.values[:-2]], index=want.index)
res_2d = h.task1_backtest(bars, want_2d.values, ex)
s_2d, _ = h.task1_stats(res_2d)
print("2-bar delay: Sharpe =", round(s_2d['sharpe'], 3), "MaxDD =", round(s_2d['max_dd']*100, 2), "% CAGR =", round(s_2d['cagr']*100, 2), "%")

# 2x costs
res_2c = h.task1_backtest(bars, want.values, ex, cost=0.0005)
s_2c, _ = h.task1_stats(res_2c)
print("2x costs:    Sharpe =", round(s_2c['sharpe'], 3), "MaxDD =", round(s_2c['max_dd']*100, 2), "% CAGR =", round(s_2c['cagr']*100, 2), "%")

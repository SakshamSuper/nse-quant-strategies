import numpy as np, pandas as pd
import harness_public as h

bars = h.load_bars('data/nifty50_15min_train_2017-04-03_2022-01-31.csv')
ex   = h.load_expiries('data/nifty_monthly_expiries_2017-01_2022-01.csv')

def compute_adx_daily(dc, dh, dl, period=14):
    prev_h = dh.shift(1); prev_l = dl.shift(1); prev_c = dc.shift(1)
    up   = dh - prev_h; down = prev_l - dl
    plus_dm  = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=dc.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=dc.index)
    tr = pd.concat([(dh-dl), (dh-prev_c).abs(), (dl-prev_c).abs()], axis=1).max(axis=1)
    alpha = 1.0 / period
    atr = tr.ewm(alpha=alpha, adjust=False).mean()
    pd_i = 100 * plus_dm.ewm(alpha=alpha, adjust=False).mean() / atr.replace(0, np.nan)
    md_i = 100 * minus_dm.ewm(alpha=alpha, adjust=False).mean() / atr.replace(0, np.nan)
    di_sum = pd_i + md_i
    dx = pd.Series(np.where(di_sum > 0, 100 * (pd_i - md_i).abs() / di_sum, 0.0), index=dc.index)
    return dx.ewm(alpha=alpha, adjust=False).mean()

def get_signal(bars, slow_ema=200, adx_thr=15, exit_ema=30):
    c = bars['close']; hb = bars['high']; lb = bars['low']
    date = bars.index.normalize()
    dc = c.groupby(date).last(); dh = hb.groupby(date).max(); dl = lb.groupby(date).min()
    slow_e = dc.ewm(span=slow_ema, adjust=False).mean()
    exit_e = dc.ewm(span=exit_ema, adjust=False).mean()
    adx = compute_adx_daily(dc, dh, dl, 14)
    entry = (dc > slow_e) & (adx > adx_thr)
    exit_ = (dc < exit_e) | (adx < adx_thr * 0.8)
    daily_pos = pd.Series(0.0, index=dc.index)
    in_trade = False
    for i in range(len(dc)):
        if not in_trade:
            if entry.iloc[i] and not exit_.iloc[i]:
                in_trade = True; daily_pos.iloc[i] = 1.0
        else:
            daily_pos.iloc[i] = 0.0 if exit_.iloc[i] else 1.0
            if exit_.iloc[i]: in_trade = False
    bar_signal = daily_pos.reindex(date).ffill().fillna(0)
    return pd.Series(bar_signal.values, index=bars.index).fillna(0)

# Best params
want = get_signal(bars, slow_ema=200, adx_thr=15, exit_ema=30)
res = h.task1_backtest(bars, want.values, ex)
s, eq = h.task1_stats(res)

print('=== BEST TASK 1 RESULTS ===')
h.print_stats('Best Task 1', s)

print()
print('=== ROBUSTNESS: 1-bar delay ===')
want_1d = pd.Series(np.r_[0.0, want.values[:-1]], index=want.index)
res_1d = h.task1_backtest(bars, want_1d.values, ex)
s1d, _ = h.task1_stats(res_1d)
sh1d = round(s1d['sharpe'], 3)
dd1d = round(s1d['max_dd']*100, 2)
cg1d = round(s1d['cagr']*100, 2)
print('Sharpe:', sh1d, 'MDD:', dd1d, 'CAGR:', cg1d)

print()
print('=== ROBUSTNESS: 2-bar delay ===')
want_2d = pd.Series(np.r_[0.0, 0.0, want.values[:-2]], index=want.index)
res_2d = h.task1_backtest(bars, want_2d.values, ex)
s2d, _ = h.task1_stats(res_2d)
sh2d = round(s2d['sharpe'], 3)
dd2d = round(s2d['max_dd']*100, 2)
cg2d = round(s2d['cagr']*100, 2)
print('Sharpe:', sh2d, 'MDD:', dd2d, 'CAGR:', cg2d)

print()
print('=== ROBUSTNESS: 2x costs ===')
res_2c = h.task1_backtest(bars, want.values, ex, cost=0.0005)
s2c, _ = h.task1_stats(res_2c)
sh2c = round(s2c['sharpe'], 3)
dd2c = round(s2c['max_dd']*100, 2)
cg2c = round(s2c['cagr']*100, 2)
print('Sharpe:', sh2c, 'MDD:', dd2c, 'CAGR:', cg2c)


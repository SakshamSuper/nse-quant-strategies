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

print("=== 3x3x3 Parameter Sensitivity Analysis for Task 1 ===")
res_list = []
for ent in [60, 75, 90]:
    for ext in [100, 125, 150]:
        for ema_p in [200, 250, 300]:
            want = donchian_strategy(bars, ent, ext, ema_p)
            res = h.task1_backtest(bars, want.values, ex)
            s, _ = h.task1_stats(res)
            res_list.append({
                'enter_bars': ent, 'exit_bars': ext, 'trend_ema': ema_p,
                'Sharpe': round(s['sharpe'], 3),
                'MaxDD%': round(s['max_dd']*100, 2),
                'CAGR%': round(s['cagr']*100, 2),
                'Trades': s['trades']
            })

df_sens = pd.DataFrame(res_list)
print(df_sens.to_string(index=False))

import pandas as pd, numpy as np
import harness_public as h

bars = h.load_bars('data/nifty50_15min_train_2017-04-03_2022-01-31.csv')
ex = h.load_expiries('data/nifty_monthly_expiries_2017-01_2022-01.csv')

c = bars['close']
h_bars = bars['high']
l_bars = bars['low']

print("--- Testing Pure 15-min Rolling Indicators (Guaranteed 0 Lookahead) ---")
for fast_bars in [75, 125, 250, 500]: # 3, 5, 10, 20 days
    for slow_bars in [1000, 1500, 2500, 3750, 5000]: # 40, 60, 100, 150, 200 days
        fast_ema = c.ewm(span=fast_bars, adjust=False).mean()
        slow_ema = c.ewm(span=slow_bars, adjust=False).mean()
        
        want = (fast_ema > slow_ema).astype(float)
        res = h.task1_backtest(bars, want.values, ex)
        s, _ = h.task1_stats(res)
        sh = round(s['sharpe'], 3)
        dd = round(s['max_dd']*100, 2)
        cagr = round(s['cagr']*100, 2)
        tr = s['trades']
        print(f"fast={fast_bars} slow={slow_bars} -> Sharpe={sh} MaxDD={dd}% CAGR={cagr}% Trades={tr}")

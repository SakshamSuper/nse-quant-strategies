import numpy as np, pandas as pd
import harness_public as h

bars = h.load_bars('data/nifty50_15min_train_2017-04-03_2022-01-31.csv')
ex   = h.load_expiries('data/nifty_monthly_expiries_2017-01_2022-01.csv')

c = bars['close']
hb = bars['high']
lb = bars['low']

# 1. Donchian Breakout (N-bar high / M-bar low)
print("=== 1. Donchian Breakout ===")
for enter_bars in [100, 200, 300, 500, 750]:
    for exit_bars in [50, 100, 150, 250]:
        high_roll = hb.rolling(enter_bars).max().shift(1)
        low_roll  = lb.rolling(exit_bars).min().shift(1)
        
        # Stateful loop or vectorised
        pos = np.zeros(len(bars))
        curr = 0
        for i in range(enter_bars, len(bars)):
            if curr == 0:
                if c.iloc[i] > high_roll.iloc[i]:
                    curr = 1
            elif curr == 1:
                if c.iloc[i] < low_roll.iloc[i]:
                    curr = 0
            pos[i] = curr
            
        want = pd.Series(pos, index=bars.index)
        res = h.task1_backtest(bars, want.values, ex)
        s, _ = h.task1_stats(res)
        if s['sharpe'] > 0.8:
            print(f"enter={enter_bars} exit={exit_bars}: Sharpe={s['sharpe']:.3f} DD={s['max_dd']*100:.2f}% CAGR={s['cagr']*100:.2f}% Trades={s['trades']}")

# 2. MACD / Dual EMA with ADX on 15-min
print("\n=== 2. EMA Crossover with ATR / Trend Filter ===")
for fast in [20, 50, 100, 200]:
    for slow in [200, 500, 1000, 1500]:
        if fast >= slow: continue
        f_ema = c.ewm(span=fast, adjust=False).mean()
        s_ema = c.ewm(span=slow, adjust=False).mean()
        
        want = (f_ema > s_ema).astype(float)
        res = h.task1_backtest(bars, want.values, ex)
        s, _ = h.task1_stats(res)
        if s['sharpe'] > 0.8:
            print(f"fast={fast} slow={slow}: Sharpe={s['sharpe']:.3f} DD={s['max_dd']*100:.2f}% CAGR={s['cagr']*100:.2f}% Trades={s['trades']}")

import numpy as np, pandas as pd
import harness_public as h

bars = h.load_bars('data/nifty50_15min_train_2017-04-03_2022-01-31.csv')
ex   = h.load_expiries('data/nifty_monthly_expiries_2017-01_2022-01.csv')

c = bars['close']
hb = bars['high']
lb = bars['low']

# Donchian Breakout + EMA Trend confirmation
print("=== Donchian Breakout + EMA Filter ===")
results = []
for enter_bars in [75, 100, 125, 150, 200]:
    for exit_bars in [50, 75, 100, 125, 150]:
        for trend_ema in [250, 500, 1000, 1500]:
            high_roll = hb.rolling(enter_bars).max().shift(1)
            low_roll  = lb.rolling(exit_bars).min().shift(1)
            ema = c.ewm(span=trend_ema, adjust=False).mean()
            
            pos = np.zeros(len(bars))
            curr = 0
            for i in range(max(enter_bars, trend_ema), len(bars)):
                # Enter long if close breaks above N-bar high AND close > trend_ema
                if curr == 0:
                    if c.iloc[i] > high_roll.iloc[i] and c.iloc[i] > ema.iloc[i]:
                        curr = 1
                elif curr == 1:
                    # Exit if close drops below exit low OR close drops below trend_ema
                    if c.iloc[i] < low_roll.iloc[i] or c.iloc[i] < ema.iloc[i]:
                        curr = 0
                pos[i] = curr
                
            want = pd.Series(pos, index=bars.index)
            res = h.task1_backtest(bars, want.values, ex)
            s, _ = h.task1_stats(res)
            if s['sharpe'] > 0.95 and s['max_dd'] > -0.15:
                results.append({
                    'enter': enter_bars, 'exit': exit_bars, 'trend_ema': trend_ema,
                    'sharpe': round(s['sharpe'], 3),
                    'max_dd': round(s['max_dd']*100, 2),
                    'cagr': round(s['cagr']*100, 2),
                    'trades': s['trades']
                })

df = pd.DataFrame(results).sort_values('sharpe', ascending=False)
print(df.head(20).to_string(index=False))

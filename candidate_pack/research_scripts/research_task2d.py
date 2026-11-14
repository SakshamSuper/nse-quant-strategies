"""
Task 2 research: finalize best strategy
"""
import numpy as np, pandas as pd
import harness_public as h
import types

D = h.load_stocks(['data/stocks_daily_train_2021-04-26_2024-06-30.csv'],
                  ['data/nifty50_daily_2021-04-26_2024-06-30.csv'])

def run_weekly(lookback=126, n_stocks=10, nifty_ema=50, vol_window=21):
    """Weekly rebalance vol-adjusted momentum with Nifty filter."""
    mod = types.ModuleType('wk')
    mod.PARAMS = {
        'lookback'  : lookback,
        'n_stocks'  : n_stocks,
        'nifty_ema' : nifty_ema,
        'vol_window': vol_window,
        'min_mom'   : 0.0,
        'rebal_day' : 4,   # 0=Mon, 4=Fri
    }
    def orders(date, hist, portfolio, params, state):
        c = hist['close']; v = hist['volume']; nh = hist['nifty']
        lb = params['lookback']; ns = params['n_stocks']
        if len(c) < lb + 10: return []
        # Weekly rebalance on the configured weekday
        if date.weekday() != int(params['rebal_day']): return []
        # Nifty regime filter
        nc = nh['close']
        n_ema = nc.ewm(span=params['nifty_ema'], adjust=False).mean().iloc[-1]
        if nc.iloc[-1] < n_ema:
            return [{'symbol': s, 'side': 'sell', 'type': 'market'} for s in portfolio['positions']]
        # Liquidity
        tc = (c.iloc[-300:] * v.iloc[-300:]).rolling(60, min_periods=40).median().iloc[-1]
        liq = tc >= 1e8
        # Raw momentum (no skip)
        raw = c.iloc[-1] / c.iloc[max(0, len(c)-1-lb)] - 1
        # Vol-adjusted score
        ret = c.pct_change().iloc[-params['vol_window']-1:]
        vol = ret.std() * np.sqrt(252)
        score = raw / vol.replace(0, np.nan)
        ok = score[liq & raw.notna()]
        top = list(ok.sort_values(ascending=False).index[:ns])
        out = [{'symbol': s, 'side': 'sell', 'type': 'market'} for s in portfolio['positions'] if s not in top]
        w = 1.0/ns
        out += [{'symbol': s, 'side': 'buy', 'type': 'market', 'weight': w, 'max_positions': ns}
                for s in top if s not in portfolio['positions']]
        return out
    mod.orders = orders
    return mod

print('=== WEEKLY REBALANCE GRID ===')
results = []
for lb in [84, 105, 126, 147, 168]:
    for nema in [50, 100, 150]:
        for ns in [8, 10, 12]:
            mod = run_weekly(lookback=lb, n_stocks=ns, nifty_ema=nema)
            res = h.task2_backtest(mod, D, mod.PARAMS)
            s, _ = h.task2_stats(res)
            results.append({'lb': lb, 'nema': nema, 'ns': ns,
                            'sharpe': round(s['sharpe'],3),
                            'max_dd': round(s['max_dd']*100,2),
                            'cagr': round(s['cagr']*100,2),
                            'trades': s['trades']})

df = pd.DataFrame(results).sort_values('sharpe', ascending=False)
print(df.head(20).to_string(index=False))

# Show full stats for the best
print()
print('=== BEST: lb=126, nema=50, ns=10 full stats ===')
mod_best = run_weekly(lookback=126, n_stocks=10, nifty_ema=50)
res_best = h.task2_backtest(mod_best, D, mod_best.PARAMS)
s_best, _ = h.task2_stats(res_best)
h.print_stats('Best Task 2 (weekly, lb=126)', s_best)

# Year by year
print()
print('Year-wise:', s_best['yearly'])


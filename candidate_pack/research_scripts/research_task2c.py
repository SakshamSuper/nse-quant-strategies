"""
Task 2 research: systematic approacQuantit Sharpe > 1.9
"""
import numpy as np, pandas as pd
import harness_public as h
import types

D = h.load_stocks(['data/stocks_daily_train_2021-04-26_2024-06-30.csv'],
                  ['data/nifty50_daily_2021-04-26_2024-06-30.csv'])

def run_strat(lookback=189, n_stocks=10, nifty_ema=50, vol_window=21, min_mom=0.0, mom_skip=0):
    """Simple vol-adjusted momentum with monthly rebalance and Nifty filter."""
    
    mod = types.ModuleType('s')
    mod.PARAMS = {
        'lookback'  : lookback,
        'n_stocks'  : n_stocks,
        'nifty_ema' : nifty_ema,
        'vol_window': vol_window,
        'min_mom'   : min_mom,
        'mom_skip'  : mom_skip,
    }

    def orders(date, hist, portfolio, params, state):
        c  = hist['close']
        v  = hist['volume']
        nh = hist['nifty']
        lb  = params['lookback']
        ns  = params['n_stocks']
        skip = params['mom_skip']
        
        if len(c) < lb + skip + 10:
            return []
        # Monthly rebalance only
        if len(c) >= 2 and c.index[-1].month == c.index[-2].month:
            return []
        # Nifty regime filter
        nc = nh['close']
        n_ema = nc.ewm(span=params['nifty_ema'], adjust=False).mean().iloc[-1]
        if nc.iloc[-1] < n_ema:
            return [{'symbol': s, 'side': 'sell', 'type': 'market'} for s in portfolio['positions']]
        # Liquidity
        tail_c = c.iloc[-300:]
        tail_v = v.iloc[-300:]
        to = (tail_c * tail_v).rolling(60, min_periods=40).median().iloc[-1]
        liq = to >= 1e8
        # Momentum
        end_i = len(c) - 1 - skip
        raw = c.iloc[end_i] / c.iloc[max(0, end_i - lb)] - 1
        # Vol adjust
        ret = c.pct_change().iloc[-params['vol_window']-1:]
        vol = ret.std() * np.sqrt(252)
        vol = vol.replace(0, np.nan)
        score = raw / vol
        
        ok = score[liq & (raw >= params['min_mom']) & raw.notna()]
        top = list(ok.sort_values(ascending=False).index[:ns])
        
        out = [{'symbol': s, 'side': 'sell', 'type': 'market'} for s in portfolio['positions'] if s not in top]
        w = 1.0 / ns
        out += [{'symbol': s, 'side': 'buy', 'type': 'market', 'weight': w, 'max_positions': ns}
                for s in top if s not in portfolio['positions']]
        return out
    
    mod.orders = orders
    return mod

# Reproduce best result: lb=189, ns=10, nifty_ema=50, no mom_skip
mod = run_strat(lookback=189, n_stocks=10, nifty_ema=50, vol_window=21, min_mom=0.0, mom_skip=0)
res = h.task2_backtest(mod, D, mod.PARAMS)
s, _ = h.task2_stats(res)
print('=== REPRODUCED BEST ===')
h.print_stats('lb=189 ns=10 nifty=50', s)

# Try: shorter lookback for more responsive signal
print()
print('=== TESTING SHORTER LOOKBACK ===')
for lb in [42, 63, 84]:
    for skip in [0, 5]:
        mod2 = run_strat(lookback=lb, n_stocks=10, nifty_ema=50, mom_skip=skip)
        res2 = h.task2_backtest(mod2, D, mod2.PARAMS)
        s2, _ = h.task2_stats(res2)
        print(f'lb={lb} skip={skip}: Sharpe={s2["sharpe"]:.3f} DD={s2["max_dd"]*100:.2f}% CAGR={s2["cagr"]*100:.2f}%')

# Try: bi-monthly rebalance approach
def run_strat_weekly(lookback=63, n_stocks=10, nifty_ema=50):
    """Weekly rebalance version."""
    mod = types.ModuleType('sw')
    mod.PARAMS = {
        'lookback': lookback, 'n_stocks': n_stocks,
        'nifty_ema': nifty_ema, 'vol_window': 21, 'min_mom': 0.0, 'mom_skip': 0,
    }
    def orders(date, hist, portfolio, params, state):
        c = hist['close']; v = hist['volume']; nh = hist['nifty']
        lb = params['lookback']; ns = params['n_stocks']
        if len(c) < lb + 10: return []
        # Weekly: only rebalance on Fridays (weekday 4)
        if date.weekday() != 4: return []
        nc = nh['close']
        n_ema = nc.ewm(span=params['nifty_ema'], adjust=False).mean().iloc[-1]
        if nc.iloc[-1] < n_ema:
            return [{'symbol': s, 'side': 'sell', 'type': 'market'} for s in portfolio['positions']]
        tc = (c.iloc[-300:] * v.iloc[-300:]).rolling(60, min_periods=40).median().iloc[-1]
        liq = tc >= 1e8
        raw = c.iloc[-1] / c.iloc[max(0, len(c)-1-lb)] - 1
        ret = c.pct_change().iloc[-22:]
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

print()
print('=== WEEKLY REBALANCE ===')
for lb in [63, 126, 189]:
    mod3 = run_strat_weekly(lookback=lb)
    res3 = h.task2_backtest(mod3, D, mod3.PARAMS)
    s3, _ = h.task2_stats(res3)
    print(f'lb={lb}: Sharpe={s3["sharpe"]:.3f} DD={s3["max_dd"]*100:.2f}% CAGR={s3["cagr"]*100:.2f}% trades={s3["trades"]}')


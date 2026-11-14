"""
Task 2 research script: testing momentum strategies
Run from candidate_pack directory: python research_task2.py
"""
import numpy as np, pandas as pd
import harness_public as h
import types

D = h.load_stocks(['data/stocks_daily_train_2021-04-26_2024-06-30.csv'],
                  ['data/nifty50_daily_2021-04-26_2024-06-30.csv'])

# ============================================================
# Helper: liquidity filter
# ============================================================
def liquid_mask(hist, min_turnover=1e8, window=60, min_periods=40):
    """Stocks with 60-day median traded value >= Rs 10 crore."""
    c = hist['close'].iloc[-300:]
    v = hist['volume'].iloc[-300:]
    turnover = (c * v).rolling(window, min_periods=min_periods).median().iloc[-1]
    return turnover >= min_turnover

# ============================================================
# Strategy 1: Enhanced momentum with Nifty regime filter
# ============================================================
def make_strategy(lookback=126, n_stocks=12, nifty_ema=100, mom_skip=5,
                  vol_window=21, min_mom=0.05):
    """
    Volatility-adjusted momentum with Nifty regime filter.
    lookback: momentum lookback in days
    n_stocks: max positions
    nifty_ema: EMA period for Nifty regime (flat if Nifty < its EMA)
    mom_skip: skip last N days of momentum (avoids short-term reversal)
    vol_window: window for volatility normalisation
    min_mom: minimum raw momentum to qualify
    """
    mod = types.ModuleType('strat')
    mod.PARAMS = {
        'lookback' : lookback,
        'n_stocks' : n_stocks,
        'nifty_ema': nifty_ema,
        'mom_skip' : mom_skip,
        'vol_window': vol_window,
        'min_mom'  : min_mom,
    }

    def orders(date, hist, portfolio, params, state):
        c = hist['close']
        v = hist['volume']
        nifty = hist['nifty']

        lb   = params['lookback']
        ns   = params['n_stocks']
        skip = params['mom_skip']

        # Need enough data
        if len(c) < lb + skip + 5:
            return []

        # Monthly rebalance: only rebalance at month end
        if len(c) >= 2 and c.index[-1].month == c.index[-2].month:
            return []

        # Nifty regime filter: only trade when Nifty is above its EMA
        nifty_close = nifty['close']
        nifty_ema_val = nifty_close.ewm(span=params['nifty_ema'], adjust=False).mean().iloc[-1]
        if nifty_close.iloc[-1] < nifty_ema_val:
            # Market in downtrend: sell everything and stay flat
            exits = [{'symbol': s, 'side': 'sell', 'type': 'market'}
                     for s in portfolio['positions']]
            return exits

        # Liquidity filter
        tail_c = c.iloc[-300:]
        tail_v = v.iloc[-300:]
        turnover = (tail_c * tail_v).rolling(60, min_periods=40).median().iloc[-1]
        liquid = turnover >= 1e8

        # Momentum: return from t-lookback to t-skip (skip last few days)
        if len(c) >= lb + skip:
            end_idx  = -1 - skip if skip > 0 else -1
            start_pr = c.iloc[-lb - skip]
            end_pr   = c.iloc[end_idx]
            raw_mom  = end_pr / start_pr - 1
        else:
            raw_mom = c.iloc[-1] * np.nan

        # Volatility normalisation: momentum / annualised vol
        # Stocks with lower volatility get a score boost
        ret21 = c.iloc[-params['vol_window']-1:].pct_change().dropna()
        if len(ret21) >= 10:
            daily_vol = ret21.std()
            ann_vol   = daily_vol * np.sqrt(252)
            ann_vol   = ann_vol.replace(0, np.nan)
            vol_adj_mom = raw_mom / ann_vol   # Sharpe-like momentum score
        else:
            vol_adj_mom = raw_mom

        # Filter: liquid stocks with minimum momentum
        ok = vol_adj_mom[liquid & (raw_mom >= params['min_mom']) & raw_mom.notna()]
        top = list(ok.sort_values(ascending=False).index[:ns])

        # Exit stocks not in new top list
        out = [{'symbol': s, 'side': 'sell', 'type': 'market'}
               for s in portfolio['positions'] if s not in top]

        # Enter new stocks (up to n_stocks total)
        w = 1.0 / ns
        out += [{'symbol': s, 'side': 'buy', 'type': 'market', 'weight': w,
                 'max_positions': ns}
                for s in top if s not in portfolio['positions']]
        return out

    mod.orders = orders
    return mod

# Grid search
print('Testing momentum with Nifty regime filter...')
results = []
for lb in [63, 126, 189]:
    for ns in [10, 12, 15]:
        for nifty_ema in [50, 100, 200]:
            mod = make_strategy(lookback=lb, n_stocks=ns, nifty_ema=nifty_ema)
            try:
                res = h.task2_backtest(mod, D, mod.PARAMS)
                s, _ = h.task2_stats(res)
                results.append({
                    'lb': lb, 'ns': ns, 'nifty_ema': nifty_ema,
                    'sharpe': round(s['sharpe'], 3),
                    'max_dd': round(s['max_dd']*100, 2),
                    'cagr'  : round(s['cagr']*100, 2),
                    'trades': s['trades'],
                    'tim'   : round(s['time_in_market']*100, 1),
                })
            except Exception as e:
                print(f'Error lb={lb} ns={ns} ne={nifty_ema}: {e}')

df = pd.DataFrame(results).sort_values('sharpe', ascending=False)
print(df.head(20).to_string(index=False))


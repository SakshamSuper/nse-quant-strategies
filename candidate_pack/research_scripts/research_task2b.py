"""
Task 2 extended research: fine-tuning around best parameters
"""
import numpy as np, pandas as pd
import harness_public as h
import types

D = h.load_stocks(['data/stocks_daily_train_2021-04-26_2024-06-30.csv'],
                  ['data/nifty50_daily_2021-04-26_2024-06-30.csv'])

def make_strategy_v2(lookback=189, n_stocks=10, nifty_ema=50, mom_skip=5,
                     vol_window=21, min_mom=0.03, rebal='month', 
                     atr_stop=False, atr_mult=2.0):
    """
    Enhanced momentum with additional options:
    - vol-adjusted momentum score
    - optional ATR stop loss
    - weekly or monthly rebalance
    """
    mod = types.ModuleType('strat2')
    mod.PARAMS = {
        'lookback'  : lookback,
        'n_stocks'  : n_stocks,
        'nifty_ema' : nifty_ema,
        'mom_skip'  : mom_skip,
        'vol_window': vol_window,
        'min_mom'   : min_mom,
    }

    def orders(date, hist, portfolio, params, state):
        c  = hist['close']
        v  = hist['volume']
        nh = hist['nifty']

        lb   = params['lookback']
        ns   = params['n_stocks']
        skip = params['mom_skip']

        if len(c) < lb + skip + 10:
            return []

        # Rebalance control: monthly
        is_month_end = (len(c) >= 2 and c.index[-1].month != c.index[-2].month)
        if not is_month_end:
            # Even if not rebalancing, check stop-loss exits every day
            exits = []
            if atr_stop:
                for sym, pos_info in portfolio['positions'].items():
                    if sym not in c.columns: continue
                    col_c = c[sym].dropna()
                    if len(col_c) < 20: continue
                    # ATR-based trailing stop
                    hi_col = hist['high'][sym].dropna()
                    lo_col = hist['low'][sym].dropna()
                    prev_c2 = col_c.shift(1)
                    tr = pd.concat([(hi_col - lo_col), (hi_col - prev_c2).abs(), 
                                    (lo_col - prev_c2).abs()], axis=1).max(axis=1)
                    atr_val = tr.ewm(alpha=1/14, adjust=False).mean().iloc[-1]
                    entry_px = pos_info['entry_price']
                    stop_px  = entry_px - atr_mult * atr_val
                    exits.append({'symbol': sym, 'side': 'sell', 'type': 'stop', 
                                  'trigger': stop_px})
            return exits

        # Nifty regime filter
        nc = nh['close']
        n_ema = nc.ewm(span=params['nifty_ema'], adjust=False).mean().iloc[-1]
        if nc.iloc[-1] < n_ema:
            exits = [{'symbol': s, 'side': 'sell', 'type': 'market'}
                     for s in portfolio['positions']]
            return exits

        # Liquidity filter
        tail_c = c.iloc[-300:]
        tail_v = v.iloc[-300:]
        turnover = (tail_c * tail_v).rolling(60, min_periods=40).median().iloc[-1]
        liquid = turnover >= 1e8

        # Raw momentum (skip last `skip` days to avoid short-term reversal)
        end_idx = len(c) - 1 - skip
        raw_mom = c.iloc[end_idx] / c.iloc[max(0, end_idx - lb)] - 1

        # Volatility adjustment (21-day)
        ret21 = c.pct_change().iloc[-params['vol_window']-1:]
        daily_vol = ret21.std()
        ann_vol   = (daily_vol * np.sqrt(252)).replace(0, np.nan)
        vol_adj   = raw_mom / ann_vol

        # Filter and rank
        ok  = vol_adj[liquid & (raw_mom >= params['min_mom']) & raw_mom.notna()]
        top = list(ok.sort_values(ascending=False).index[:ns])

        out = [{'symbol': s, 'side': 'sell', 'type': 'market'}
               for s in portfolio['positions'] if s not in top]
        w = 1.0 / ns
        out += [{'symbol': s, 'side': 'buy', 'type': 'market', 'weight': w,
                 'max_positions': ns}
                for s in top if s not in portfolio['positions']]
        return out

    mod.orders = orders
    return mod

results = []
print('Testing fine-tuned parameters...')
# Focus on lb=189, ns=10, nifty_ema=50 as base; vary min_mom and mom_skip
for min_mom in [0.0, 0.02, 0.05, 0.08, 0.10]:
    for mom_skip in [0, 5, 10, 21]:
        mod = make_strategy_v2(lookback=189, n_stocks=10, nifty_ema=50,
                               mom_skip=mom_skip, min_mom=min_mom)
        try:
            res = h.task2_backtest(mod, D, mod.PARAMS)
            s, _ = h.task2_stats(res)
            results.append({
                'min_mom': min_mom, 'mom_skip': mom_skip,
                'sharpe': round(s['sharpe'], 3),
                'max_dd': round(s['max_dd']*100, 2),
                'cagr'  : round(s['cagr']*100, 2),
                'trades': s['trades'],
            })
        except Exception as e:
            print(f'Error: {e}')

df = pd.DataFrame(results).sort_values('sharpe', ascending=False)
print('=== min_mom and mom_skip sensitivity ===')
print(df.to_string(index=False))


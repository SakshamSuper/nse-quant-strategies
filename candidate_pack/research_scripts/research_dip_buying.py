"""
Research Script: Independent Investigation of User's Dip-Buying Hypothesis
Quantitative Research Systematic Trading Project

User's Original Proposal:
  - Initial purchase: 40% allocation.
  - Additional purchase at 5% decline: 30%.
  - Additional purchase at 11% decline: 30%.
  - Decline reference: first purchase price.
  - Profit target: 7% above average purchase cost.
  - Final exit target: 14% above average purchase cost.

Harness Rule Audit:
  1. Adding to open positions:
     Harness line 197 explicitly states:
     "No adding to an existing position; orders on symbols with no price that day lapse."
     In harness_public.py line 229:
       if s in pos or s not in col: continue
     Any buy order for a stock already held in portfolio is strictly skipped.
     Pyramiding / averaging down is NOT permitted by the harness interface.

  2. Position size limit:
     Harness line 24 & line 238:
     T2_MAX_W = 0.15 (15% maximum weight per position).
     An allocation of 40% is impossible; any weight > 15% is clamped to 15%.

  3. Partial profit booking:
     Harness line 112 & line 218:
     Market sells and stop sells close the entire position (p = pos.pop(s)).
     Partial profit taking (e.g. 50% at +7% and 50% at +14%) is NOT supported.

Permissible Approximation:
  - Buy when stock dips X% from recent high (e.g. 5% or 11% pullbacks in uptrending stocks).
  - Allocation: max allowed 15% (or 1/N = 10% for 10 stocks).
  - Profit target: exit at +7% or +14% via stop/limit or next-day market exit.
  - Stop loss: exit at -8% or -10% to prevent holding falling knives.
"""

import numpy as np, pandas as pd
import harness_public as h
import types

D = h.load_stocks(['data/stocks_daily_train_2021-04-26_2024-06-30.csv'],
                  ['data/nifty50_daily_2021-04-26_2024-06-30.csv'])

def make_dip_buying_strategy(dip_pct=0.08, profit_target=0.10, stop_loss=0.08, n_stocks=10):
    mod = types.ModuleType('dip_buying')
    mod.PARAMS = {
        'dip_pct': dip_pct,
        'profit_target': profit_target,
        'stop_loss': stop_loss,
        'n_stocks': n_stocks,
        'lookback': 60,
    }

    def orders(date, hist, portfolio, params, state):
        c = hist['close']
        v = hist['volume']
        nh = hist['nifty']

        ns = int(params['n_stocks'])
        dip = float(params['dip_pct'])
        pt = float(params['profit_target'])
        sl = float(params['stop_loss'])

        if len(c) < 65:
            return []

        # Check existing positions for exit (profit target or stop loss)
        out = []
        for sym, pos_data in portfolio['positions'].items():
            if sym not in c.columns:
                continue
            curr_px = c[sym].iloc[-1]
            entry_px = pos_data['entry_price']
            ret = (curr_px / entry_px) - 1.0

            # Profit target exit
            if ret >= pt:
                out.append({'symbol': sym, 'side': 'sell', 'type': 'market'})
            # Stop loss exit
            elif ret <= -sl:
                out.append({'symbol': sym, 'side': 'sell', 'type': 'market'})

        # If already at max positions, don't generate buys
        open_pos_count = len(portfolio['positions']) - len([x for x in out if x['side'] == 'sell'])
        if open_pos_count >= ns:
            return out

        # Find candidate dip-buying opportunities
        # Liquid universe: 60-day median turnover >= 10 crore
        tail_c = c.iloc[-60:]
        tail_v = v.iloc[-60:]
        turnover = (tail_c * tail_v).rolling(60, min_periods=40).median().iloc[-1]
        liquid = turnover >= 1e8

        # 60-day high
        high_60 = c.iloc[-60:].max()
        curr_c  = c.iloc[-1]
        drawdown_from_high = (curr_c / high_60) - 1.0

        # Dip condition: price is between -dip_pct and -(dip_pct + 10%) from 60-day high
        # and stock was in an intermediate uptrend (e.g. 60-day return was positive prior to dip)
        dip_cond = (drawdown_from_high <= -dip) & (drawdown_from_high >= -dip - 0.15) & liquid
        candidates = list(drawdown_from_high[dip_cond].sort_values().index)

        # Place buys up to available slots
        w = 1.0 / ns
        for sym in candidates:
            if sym not in portfolio['positions'] and sym not in [x['symbol'] for x in out]:
                out.append({'symbol': sym, 'side': 'buy', 'type': 'market', 'weight': w, 'max_positions': ns})
                if len(out) >= ns:
                    break

        return out

    mod.orders = orders
    return mod

print("=== Testing Dip-Buying Hypothesis Variations ===")
for dip in [0.05, 0.08, 0.11]:
    for pt in [0.07, 0.10, 0.14]:
        for sl in [0.06, 0.08, 0.10]:
            strat = make_dip_buying_strategy(dip_pct=dip, profit_target=pt, stop_loss=sl)
            res = h.task2_backtest(strat, D, strat.PARAMS)
            s, _ = h.task2_stats(res)
            print(f"Dip={dip*100:.0f}% Target={pt*100:.0f}% Stop={sl*100:.0f}% -> Sharpe={s['sharpe']:.3f} MaxDD={s['max_dd']*100:.2f}% CAGR={s['cagr']*100:.2f}% Trades={s['trades']} WinRate={s['win_rate']*100:.1f}%")

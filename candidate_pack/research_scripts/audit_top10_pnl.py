import os, sys
sys.path.insert(0, os.path.abspath('candidate_pack'))
import numpy as np
import pandas as pd
import harness_public as hp
import task2

D = hp.load_stocks([os.path.join('candidate_pack', 'data', 'stocks_daily_train_2021-04-26_2024-06-30.csv')],
                   [os.path.join('candidate_pack', 'data', 'nifty50_daily_2021-04-26_2024-06-30.csv')])

# Modify backtest to also record cost and realized pnl
m = task2
params = dict(m.PARAMS)
cost = hp.T2_COST
dates = D['close'].index
cols = list(D['close'].columns)
col = {s: j for j, s in enumerate(cols)}
O, H, L, C = D['open'].values, D['high'].values, D['low'].values, D['close'].values
Cf = D['close'].ffill().values
t0 = int(np.searchsorted(dates, pd.Timestamp(hp.T2_START)))
t1 = int(np.searchsorted(dates, pd.Timestamp(hp.T2_END), side='right')) - 1 if hp.T2_END else len(dates) - 1

cash, pos, eq, trades, state = 1.0, {}, [], [], {}
traded, gross = 0.0, []

def value(t): return cash + sum(p['n'] * Cf[t, col[s]] for s, p in pos.items())
def portfolio(t):
    v = value(t)
    return {'cash': cash, 'value': v, 'positions': {s: {'shares': p['n'], 'entry_price': p['px'], 'entry_date': p['in'],
            'value': p['n'] * Cf[t, col[s]]} for s, p in pos.items()}}

def close(s, px, d, t, why):
    global cash, traded
    p = pos.pop(s); pr = p['n'] * px * (1 - cost); cash += pr; traded += p['n'] * px
    pnl = pr - p['cost']
    trades.append({'symbol': s, 'entry_date': p['in'], 'exit_date': d, 'ret': pr / p['cost'] - 1, 'cost': p['cost'], 'proceeds': pr, 'pnl': pnl, 'days': t - p['t'], 'why': why})

pending = m.orders(dates[t0 - 1], hp._slice(D, t0 - 1), portfolio(t0 - 1), dict(params), state) or []
for t in range(t0, t1 + 1):
    d = dates[t]; v_prev = value(t - 1)
    sells = [x for x in pending if x.get('side') == 'sell']; buys = [x for x in pending if x.get('side') == 'buy']
    for x in sells:
        s = x['symbol']
        if x.get('type', 'market') == 'market' and s in pos and not np.isnan(O[t, col[s]]): close(s, O[t, col[s]], d, t, 'market')
    for x in buys:
        s = x['symbol']
        if s in pos or s not in col: continue
        if len(pos) >= min(int(x.get('max_positions', hp.T2_MAX_POS)), hp.T2_MAX_POS): continue
        j = col[s]; o_, h_ = O[t, j], H[t, j]
        if np.isnan(o_) or np.isnan(h_): continue
        if x.get('type', 'market') == 'stop':
            trig = float(x['trigger'])
            if not h_ > trig: continue
            px = max(o_, trig)
        else: px = o_
        amt = min(min(float(x.get('weight', 0)), hp.T2_MAX_W) * v_prev, cash)
        if amt <= 1e-12: continue
        cash -= amt; traded += amt
        pos[s] = {'n': amt * (1 - cost) / px, 'px': px, 'in': d, 't': t, 'cost': amt}
    for x in sells:
        s = x['symbol']
        if x.get('type') == 'stop' and s in pos and pos[s]['t'] < t:
            j = col[s]; trig = float(x['trigger'])
            if not np.isnan(L[t, j]) and L[t, j] < trig: close(s, min(O[t, j], trig), d, t, 'stop')
    v = value(t); eq.append((d, v)); gross.append(1 - cash / v if v > 0 else 0)
    if t < t1: pending = m.orders(d, hp._slice(D, t), portfolio(t), dict(params), state) or []

df_t = pd.DataFrame(trades)
print(f"Total trades: {len(df_t)}")
winning_trades = df_t[df_t['pnl'] > 0]
losing_trades = df_t[df_t['pnl'] <= 0]
total_gross_profit = winning_trades['pnl'].sum()
total_gross_loss = losing_trades['pnl'].sum()
net_realized_pnl = df_t['pnl'].sum()

print(f"Total Gross Realized Profit: {total_gross_profit:.6f}")
print(f"Total Gross Realized Loss:   {total_gross_loss:.6f}")
print(f"Net Realized PnL:            {net_realized_pnl:.6f}")

# Top 10 by Realized PnL
top10_pnl = df_t.sort_values(by='pnl', ascending=False).head(10)
top10_pnl_sum = top10_pnl['pnl'].sum()
top10_profit_share = (top10_pnl_sum / total_gross_profit) * 100
top10_net_share = (top10_pnl_sum / net_realized_pnl) * 100

print(f"\nTop 10 Trades by Realized PnL Sum: {top10_pnl_sum:.6f}")
print(f"Top 10 Share of Gross Realized Profit: {top10_profit_share:.2f}%")
print(f"Top 10 Share of Net Realized Profit:   {top10_net_share:.2f}%")

print("\nTop 10 Realized Trades:")
for i, r in top10_pnl.reset_index().iterrows():
    print(f"{i+1:2d}. {r['symbol']:12} | In: {str(r['entry_date'])[:10]} | Out: {str(r['exit_date'])[:10]} | Cost: {r['cost']:.4f} | PnL: {r['pnl']:.4f} | Ret: {r['ret']*100:6.2f}% | Days: {r['days']}")

# Also show unweighted sum for comparison
winning_ret = df_t[df_t['ret'] > 0]
total_ret_sum = winning_ret['ret'].sum()
top10_by_ret = df_t.sort_values(by='ret', ascending=False).head(10)
top10_ret_sum = top10_by_ret['ret'].sum()
print(f"\nComparison: Unweighted Return Sum share = {top10_ret_sum / total_ret_sum * 100:.2f}%")

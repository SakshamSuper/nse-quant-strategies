import os, sys
sys.path.insert(0, os.path.abspath('candidate_pack'))
import harness_public as hp
import task2

D = hp.load_stocks([os.path.join('candidate_pack', 'data', 'stocks_daily_train_2021-04-26_2024-06-30.csv')],
                   [os.path.join('candidate_pack', 'data', 'nifty50_daily_2021-04-26_2024-06-30.csv')])

lookbacks = [105, 126, 147]
vol_windows = [15, 21, 30]

print("Lookback | VolWindow | Sharpe | MaxDD   | CAGR   | Trades | WinRate")
print("-----------------------------------------------------------------")
for lb in lookbacks:
    for vw in vol_windows:
        p = dict(task2.PARAMS)
        p['lookback'] = lb
        p['vol_window'] = vw
        res = hp.task2_backtest(task2, D, p, hp.T2_START, hp.T2_END)
        s, _ = hp.task2_stats(res)
        sh = s['sharpe']
        mdd = s['max_dd']
        cagr = s['cagr']
        trades = s['trades']
        wr = s['win_rate']
        print(f"{lb:8d} | {vw:9d} | {sh:6.3f} | {mdd*100:6.2f}% | {cagr*100:5.2f}% | {trades:6d} | {wr*100:6.2f}%")


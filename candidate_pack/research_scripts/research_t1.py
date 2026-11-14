"""
Systematic Research for Task 1: Nifty Futures Trend / Timing
Testing genuine, 100% lookahead-free strategies on 15-minute bars.
"""
import numpy as np, pandas as pd
import harness_public as h

bars = h.load_bars('data/nifty50_15min_train_2017-04-03_2022-01-31.csv')
ex   = h.load_expiries('data/nifty_monthly_expiries_2017-01_2022-01.csv')

c = bars['close']
h_b = bars['high']
l_b = bars['low']
o = bars['open']

# Verify zero lookahead test helper
def verify_zero_lookahead(signal_func, bars, sample_points=20):
    full_sig = signal_func(bars)
    diffs = 0
    rng = np.random.default_rng(42)
    cutoffs = sorted(rng.integers(250, len(bars)-1, sample_points))
    for cut in cutoffs:
        trunc_sig = signal_func(bars.iloc[:cut+1])
        if trunc_sig.iloc[-1] != full_sig.iloc[cut]:
            diffs += 1
    return diffs == 0

print("Loaded bars:", len(bars))

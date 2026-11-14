# RESEARCH NOTE: SURVIVORSHIP BIAS IN THE TASK 2 UNIVERSE
## Methodological Analysis & Institutional Production Roadmap
**Role:** Quantitative Research Candidate  
**Context:** Quantitative Research Systematic Trading Project

---

### 1. The Fixed Universe vs. Point-in-Time Reality

The dataset in `stocks_daily_train_2021-04-26_2024-06-30.csv` contains price and volume history for a fixed list of **555 NSE symbols**. As explicitly disclosed in the assignment specification:
> *"The stock list is the set of NSE stocks that were liquid (60-day median traded value >= Rs 10 crore) in **October 2026**. Stocks that were liquid in 2022 but have since been delisted, merged or become illiquid are missing. This flatters every long-only strategy, especially momentum and small-cap tilts."*

To understand the methodological implications, we must clearly distinguish three distinct concepts:

1. **The Fixed Stock Universe (Supplied by the Dataset):**
   The candidate pool was constructed with hindsight by selecting companies that satisfied a liquidity threshold at the end of the full testing horizon (October 2026). Companies that went bankrupt, were suspended by SEBI, entered insolvency resolution, or were delisted between 2022 and 2026 are entirely omitted from the data.
2. **The Dynamic Historical Liquidity Filter (Applied in Code):**
   Our strategy enforces `median_turnover >= Rs 10 Crore` on historical rolling 60-day windows available at decision time. While this successfully prevents the strategy from attempting to trade thinly traded or illiquid stocks *within the provided dataset*, **it does not eliminate survivorship bias**. Filtering a survivor-biased universe on rolling volume still operates only on companies that survived until October 2026.
3. **The Absence of a True Point-in-Time Historical Constituent Universe:**
   In an institutional setting, an unbiased simulation requires knowing which stocks were active, tradable, and met liquidity criteria on *each historical date $t$*, including companies that subsequently collapsed. Such a point-in-time security master was not supplied in the assignment dataset.

---

### 2. Qualitative Directional Impact on Strategy Types

In quantitative finance literature (Brown et al., 1992; Elton, Gruber, & Blake, 1996; Malkiel, 1995), the distortion introduced by survivorship bias is well established:

* **Asymmetric Advantage to Long-Only Portfolios:**
  A long-only equity portfolio cannot suffer a 100% total-loss wipeout from a stock that went to zero if that stock was never in the file. The left tail of the return distribution is mechanically truncated.
* **Compound Benefit to Cross-Sectional Momentum:**
  Cross-sectional momentum systematically buys relative winners. In a survivor-biased universe, relative winners enjoy an unearned tailwind because companies whose upward momentum reversed into sudden insolvency are absent from the backtest.
* **Realistic Expectations on Unseen Data:**
  Because the hidden evaluation period (July 2024 to October 2026) is closer to the October 2026 selection date, survivorship distortion will be lower in the out-of-sample period than in 2021–2022. However, researchers must expect an out-of-sample performance discount compared to in-sample metrics.

---

### 3. Empirical Safeguards Implemented in Task 2

Rather than attempting to construct an artificial mathematical adjustment for survivorship bias (which would be ungrounded without delisting records), our strategy incorporates three structural risk controls:

1. **Volatility Normalization ($\text{Score} = R_{126d} / \sigma_{21d}$):**
   Penalizing high realized volatility steers capital away from speculative runners that might be prone to momentum crashes.
2. **Strict Position Limits (10% max allocation, 10 stocks):**
   Capping positions at 10% ensures that even if an individual constituent experiences sudden distress out-of-sample, total portfolio loss is bounded.
3. **Macro Regime Gate (Nifty 50-day EMA):**
   The strategy liquidates 100% of holdings to cash when the benchmark index enters a downtrend, providing structural portfolio protection regardless of individual stock survival.

---

### 4. Institutional Production Roadmap to Eliminate Survivorship Bias

To deploy this momentum engine in live production at Quantitative Research:

1. **Construct a Point-in-Time Security Master:**
   Reconstruct the investable universe daily from historical NSE Bhavcopy and corporate action archives:
   $$\text{Universe}_t = \{ s \in \text{NSE} \mid \text{Turnover}_{s, t}(60d) \ge \text{Rs } 10\text{ Cr}, \text{TradingStatus}_{s, t} = \text{'ACTIVE'} \}$$
   No knowledge of future listing or survival beyond date $t$ must be utilized.
2. **Model Terminal Liquidation Dynamics:**
   For companies entering insolvency or facing compulsory delisting, model terminal liquidation at the last traded price or an insolvency recovery fraction rather than deleting the ticker from history.
3. **Incorporate Total Return Adjustments:**
   Adjust prices for cash dividends alongside splits and bonus shares to reflect the complete economic holding return.

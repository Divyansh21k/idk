# Phase 4 Uncertainty Audit: Confidence Intervals, Rank Variability & Simulation Evidence

**Phase:** Phase 4 — Statistical Reliability, Shrinkage & Final Rankings  
**Date:** 2026-11-17  
**Branch:** `model-repair`  
**Scope:** Rigorous quantification of player rating uncertainty via match-cluster block-bootstrap, empirical testing of confidence interval coverage, rank intervals, top-10 inclusion probabilities, and clear separation of statistical noise, model specification uncertainty, and fundamental data limitations.

---

## Executive Summary

A critical weakness of naive sports rankings is the presentation of player scores as exact, deterministic scalar quantities (e.g. "Player A is #1 with 38.66, Player B is #2 with 30.47"). 

In T20 cricket, where single-ball variance is high ($\sigma_e \approx 2.88$ runs/ball) and high-pressure sample sizes are small (50 to 600 deliveries), **rankings are inherently stochastic**. 

Our uncertainty audit reveals that:
1. **Rank Intervals are Wide:** For the top-ranked batter (Vaibhav Sooryavanshi), his 90% bootstrap rank interval is **$[1, 27]$** ($P(\text{Top 10}) = 84.2\%$). For the top-ranked bowler (Reece Topley), his 90% rank interval is **$[1, 67]$** ($P(\text{Top 10}) = 55.4\%$).
2. **Empirical Coverage of Nominal 90% CIs is ~71% for Latent Talent:** When synthetic data simulations test whether nominal 90% empirical Bayes intervals cover the player's true unobservable latent talent $\mu_i$, empirical coverage drops to **71.1%** due to shrinkage bias on extreme performers. The interval strictly covers the *sampling variability of the shrunken estimator*, not the unobservable truth.
3. **Point Rankings Cannot Distinguish Adjacent Ranks:** Random delivery luck (an outside edge going for four vs edging to the keeper) can easily shift a player by 10–25 rank positions across a 50-to-100 ball sample.

---

## 1. Methodology: Stratified Match-Cluster Block-Bootstrap

To account for intra-match correlation ($\rho \approx 0.05$) and match-level clustering without making asymptotic parametric assumptions, we implemented a **Stratified Match-Cluster Block-Bootstrap**:

### 1.1 Resampling Algorithm
1. The 802 matches in the dataset are partitioned into four competition strata: `IPL league` ($N=341$), `IPL knockout` ($N=20$), `T20I non-knockout` ($N=436$), and `T20I final` ($N=5$).
2. For each bootstrap iteration $b \in \{1, \dots, 500\}$:
   - Resample matches with replacement within each category to preserve tournament composition.
   - For every player meeting the eligibility floor ($n_{\text{hp}} \ge 50, m_{\text{hp}} \ge 5, n_{\text{total}} \ge 200$), aggregate deliveries and calculate their shrunken rating $R_{\text{HP}}^{(b)}$.
   - Rank all eligible players simultaneously to obtain their bootstrap rank $\text{Rank}_i^{(b)}$.
3. From the 500 resamples:
   - Compute the 90% Confidence Interval: $[CI_{90, \text{lo}}, CI_{90, \text{hi}}] = [\text{Quantile}(R^{(b)}, 0.05), \text{Quantile}(R^{(b)}, 0.95)]$.
   - Compute the Bootstrap Standard Error: $SE_{\text{boot}} = \text{std}(R^{(b)})$.
   - Compute the 90% Rank Interval: $[Rank_{90, \text{lo}}, Rank_{90, \text{hi}}] = [\text{Quantile}(\text{Rank}^{(b)}, 0.05), \text{Quantile}(\text{Rank}^{(b)}, 0.95)]$.
   - Compute the Probability of Top 10 Inclusion: $P(\text{Top 10}) = \frac{1}{500} \sum_{b=1}^{500} \mathbb{I}(\text{Rank}_i^{(b)} \le 10)$.

---

## 2. Top-10 Uncertainty Profiles

### 2.1 Repaired Top 10 Batters Under Pressure

| Rank | Player Name | Role | Rating ($R_{\text{HP}}$) | 90% Rating CI | $SE_{\text{boot}}$ | 90% Rank Interval | $P(\text{Top 10})$ | $n_{\text{hp}}$ | Matches |
|---|---|---|---|---|---|---|---|---|---|
| **1** | **Vaibhav Sooryavanshi** | Opener (1-2) | **+38.66** | $[+12.21, +58.68]$ | 14.55 | **$[1, 27]$** | **84.2%** | 190 | 19 |
| **2** | **Suryakumar Yadav** | Top Order (3-4) | **+30.47** | $[+15.15, +45.04]$ | 9.07 | **$[1, 23]$** | **80.6%** | 598 | 55 |
| **3** | **Abhishek Sharma** | Opener (1-2) | **+29.38** | $[+7.49, +47.86]$ | 12.02 | **$[1, 40]$** | **74.8%** | 560 | 85 |
| **4** | **Yashasvi Jaiswal** | Opener (1-2) | **+25.63** | $[+11.49, +37.60]$ | 7.90 | **$[2, 29]$** | **69.8%** | 604 | 82 |
| **5** | **Pathum Nissanka** | Opener (1-2) | **+22.42** | $[+13.11, +31.49]$ | 5.51 | **$[3, 25]$** | **54.0%** | 619 | 72 |
| **6** | **Phil Salt** | Opener (1-2) | **+21.35** | $[+4.11, +34.65]$ | 9.38 | **$[2, 56]$** | **51.0%** | 494 | 70 |
| **7** | **Ryan Rickelton** | Opener (1-2) | **+20.80** | $[+4.33, +35.09]$ | 9.49 | **$[2, 55]$** | **46.2%** | 283 | 33 |
| **8** | **Virat Kohli** | Opener (1-2) | **+19.73** | $[+6.09, +30.62]$ | 7.23 | **$[4, 49]$** | **39.4%** | 584 | 60 |
| **9** | **Prabhsimran Singh** | Opener (1-2) | **+19.43** | $[-1.17, +41.90]$ | 12.98 | **$[1, 77]$** | **43.2%** | 350 | 35 |
| **10** | **Daryl Mitchell** | Top Order (3-4) | **+18.79** | $[+5.80, +31.74]$ | 7.80 | **$[3, 48]$** | **34.2%** | 183 | 22 |

**Key Batter Observations:**
- The top 4 batters (Sooryavanshi, SKY, Abhishek, Jaiswal) exhibit high top-10 probability ($70\% - 84\%$), confirming their elite tier.
- However, their individual rank intervals span 20 to 40 spots. In particular, Abhishek Sharma has $P(\text{Top 10}) = 74.8\%$, but under stressed resamples his rank can be as low as #40.
- Prabhsimran Singh's 90% CI crosses zero ($[-1.17, +41.90]$), meaning he cannot be definitively distinguished from league average at $\alpha = 0.10$.

---

### 2.2 Repaired Top 10 Bowlers Under Pressure

| Rank | Player Name | Role | Rating ($R_{\text{HP}}$) | 90% Rating CI | $SE_{\text{boot}}$ | 90% Rank Interval | $P(\text{Top 10})$ | $n_{\text{hp}}$ | Matches |
|---|---|---|---|---|---|---|---|---|---|
| **1** | **Reece Topley** | Pace | **+20.65** | $[+4.83, +38.53]$ | 10.37 | **$[1, 67]$** | **55.4%** | 117 | 20 |
| **2** | **Tim Southee** | Pace | **+18.94** | $[+2.38, +37.68]$ | 10.74 | **$[1, 85]$** | **47.0%** | 223 | 30 |
| **3** | **Rashid Khan** | Spin | **+18.28** | $[+8.22, +27.92]$ | 6.01 | **$[2, 44]$** | **47.2%** | 490 | 49 |
| **4** | **Mayank Yadav** | Pace | **+17.47** | $[+3.72, +31.67]$ | 8.44 | **$[1, 76]$** | **42.0%** | 86 | 13 |
| **5** | **Sikandar Raza** | Spin | **+17.40** | $[+5.42, +29.71]$ | 7.42 | **$[2, 61]$** | **39.2%** | 267 | 24 |
| **6** | **Wayne Parnell** | Pace | **+16.32** | $[+1.16, +33.24]$ | 9.87 | **$[1, 90]$** | **37.4%** | 71 | 10 |
| **7** | **Abrar Ahmed** | Spin | **+16.17** | $[+5.92, +27.73]$ | 6.55 | **$[2, 59]$** | **31.6%** | 188 | 20 |
| **8** | **Krunal Pandya** | Spin | **+15.83** | $[+4.55, +26.46]$ | 6.70 | **$[3, 66]$** | **31.6%** | 238 | 25 |
| **9** | **Mehidy Hasan Miraz**| Spin | **+14.46** | $[+3.69, +24.30]$ | 6.28 | **$[3, 74]$** | **26.2%** | 68 | 10 |
| **10** | **Harry Tector** | Spin | **+14.06** | $[+7.23, +21.76]$ | 4.37 | **$[7, 51]$** | **16.6%** | 88 | 9 |

**Key Bowler Observations:**
- Bowler ratings are significantly more clustered and uncertain than batter ratings. The top bowler (Reece Topley, +20.65) is separated from #10 (Harry Tector, +14.06) by just 6.6 runs per 100 balls.
- Top-10 inclusion probabilities for bowlers peak at only **55.4%** (Topley) and **47.2%** (Rashid Khan).
- Highly experienced spinners like Rashid Khan (490 balls) exhibit tight rating CIs ($[+8.22, +27.92]$, SE = 6.01), whereas lower-sample pacers like Wayne Parnell (71 balls) have rank intervals spanning $[1, 90]$.

---

## 3. Simulation Evidence: Empirical Coverage and Rank Recovery

To verify what the uncertainty metrics genuinely establish, we performed controlled synthetic data experiments matching our empirical parameters ($\sigma_e = 2.88, \sigma_{\mu} = 0.187, N=1,000$ simulated players):

### 3.1 Empirical Coverage of the Nominal 90% CI
- **Nominal Coverage:** 90.0%
- **Empirical Coverage for True Latent Talent $\mu_i$:** **71.1%**

**Why undercoverage occurs:**
In empirical Bayes shrinkage, $\hat{R}_i = \lambda_i \bar{y}_i + (1-\lambda_i)\mu_0$ is a **biased estimator** designed to minimize mean squared error (MSE), not to achieve Neyman-Pearson unbiased confidence coverage. For true elite players located in the upper tail of the distribution, shrinkage pulls the interval toward zero, causing the upper bound to occasionally exclude the extreme true value.
- **Reporting Integrity:** We explicitly state that our bootstrap intervals measure the **sampling variability of the shrunken performance score**, not an exact 90% frequentist coverage of unobservable latent talent.

### 3.2 Simulation Rank Recovery Rates
- **Probability of recovering the exact true Top 10 in 1-to-10 order:** **22.7%**
- **Probability that a player in our Top 10 belongs to the true Top 25:** **78.4%**
- **Probability that a true Top-10 player is included in our candidate pool:** **81.6%**

---

## 4. Separation of Uncertainty Sources

To prevent statistical overclaiming, we separate three distinct layers of uncertainty:

```
Total Uncertainty = Statistical Sampling Noise + Model Specification Uncertainty + Data Limitations
```

### 4.1 Statistical Sampling Noise (Quantified)
- Arises from finite delivery samples ($n \in [50, 650]$) and single-ball stochasticity ($\sigma_e \approx 2.88$).
- Rigorously captured and quantified by our **Match-Cluster Bootstrap Standard Errors** and **90% Confidence Intervals**.

### 4.2 Model Specification Uncertainty (Audited)
- Arises from structural choices in earlier phases:
  * Expected-value model: Resource table vs polynomial regression (validated via 5-fold CV in Phase 1).
  * Win-probability model: Logistic regression vs gradient boosting (validated via temporal holdout in Phase 2).
  * Pressure cutoff: Threshold $PI \ge 0.80$ vs continuous leverage weighting $R_{\text{LW}}$.
- Audit shows that $R_{\text{HP}}$ and $R_{\text{LW}}$ have a rank correlation of **0.91**, confirming that specification uncertainty does not overturn the core leaderboard.

### 4.3 Fundamental Data Limitations (Unquantifiable)
- **Extreme Knockout Sparsity:** Only 25 knockout matches across 5 years.
- **Unobserved Confounders:** Pitch deterioration, dew, boundary dimensions, and tactical instructions are not fully recorded in the ball-by-ball feed.
- **Opposition Quality Variation:** T20I bilateral series vary widely in opposition strength compared to the IPL.
- **No model can eliminate these limitations; they must be honestly disclosed.**

---

## 5. Conclusions for Competition Evaluators

1. **Do not treat the Top 10 as an immutable ordered sequence.** The statistical difference between Rank 3 and Rank 7 is smaller than single-match sampling noise.
2. **Present the Top 10 as an evidence-based "Elite Candidate Tier."**
3. **Mandate reporting of Rank Intervals and Top-10 Inclusion Probabilities** in all competition presentations.

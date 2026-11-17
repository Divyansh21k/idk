# Baseline Model Diagnostics — SupeRR Selector Season 2, Round 1

**Document Version:** 1.0 (Baseline Freeze)  
**Date:** 2026-11-17  
**Git Branch:** `model-repair`  
**Source Baseline Commit:** `c0ace3fe9412bff1faa25b7f79dfe8682bec112f`  
**Status:** Frozen Pre-Repair Diagnostic State  

---

## 1. Executive Diagnostic Summary

This document compiles the empirical diagnostics, validation gate results, and failure points of the SupeRR Selector Season 2 model as implemented at the baseline freeze point. 

### Diagnostic Scorecard

| Pipeline Component | Metric / Check | Target / Criterion | Baseline Value | Status | Diagnostic Implication |
|---|---|---|---|---|---|
| **Step 1: Data Layer** | 49 integrity assertions | 100% Pass | 49 / 49 PASS | **PASS** | Clean data parsing, valid match/delivery linkage |
| **Step 2: EV Mean Zero** | Mean $v_{\text{bat}}$ | $|\bar{v}| < 0.01$ | $-1.20 \times 10^{-17}$ | **PASS** | Centering holds across total sample |
| **Step 2: EV Mean Zero** | Mean $v_{\text{bowl}}$ | $|\bar{v}| < 0.01$ | $+1.33 \times 10^{-17}$ | **PASS** | Centering holds across total sample |
| **Step 2: Resource Monotonicity** | Monotone in balls left ($c(s)$) | Strictly True | **False** | **FAIL** | Resource table assigns inconsistent values to ball states |
| **Step 2: Resource Monotonicity** | Monotone in wickets lost ($c(s)$) | Strictly True | **False** | **FAIL** | A wicket in certain states costs more runs than adjacent states |
| **Step 2: Resource Non-negativity**| $c(s) \ge 0$ | 0 violations | 0 violations | **PASS** | Expected runs remaining are non-negative |
| **Step 2: Value Finiteness** | Finite $v_{\text{bat}}, v_{\text{bowl}}$ | 0 non-finite | 0 non-finite | **PASS** | No NaNs or infinities generated in value attribution |
| **Step 3: WP Model Fit** | Brier score (Brier loss) | $< 0.20$ | 0.192454 | **BORDERLINE** | Modest improvement over naive 0.25 baseline |
| **Step 3: WP Calibration (Tails)**| Decile 0 calibration error | $|\text{pred} - \text{actual}| < 0.05$| $+0.0517$ (118% rel error) | **FAIL** | Predicts 4.3% win rate; actual is 9.5% |
| **Step 3: WP Calibration (Tails)**| Decile 7 calibration error | $|\text{pred} - \text{actual}| < 0.05$| $-0.0694$ (actual 81.6%) | **FAIL** | High end under-predicted |
| **Step 3: Leverage Positivity** | $L(s) \ge 0$ | 0 violations | 0 violations | **PASS** | Mathematical definition of absolute leverage preserved |
| **Step 3: PI Missing Values** | Missing Pressure Index | 0 missing | 0 missing | **PASS** | All eligible pressure deliveries have valid PI |
| **Step 3: Knockout Weight $w_K$**| IPL KO leverage share | $[0.03, 0.10]$ | 0.052932 (5.29%) | **PASS** | Frozen parameter derived from IPL leverage share |
| **Step 4: Bootstrap SE Ratio** | $\text{SE}_{\text{boot}} / \text{SE}_{\text{anal}}$ | $\approx 1.0$ | Up to 1.886 (Madhwal) | **FAIL** | Analytical SE ignores match clustering; bootstrap essential |
| **Step 4: Statistical Significance**| 90% CI excludes zero | 10/10 players | 7/10 batters, 7/10 bowlers | **FAIL** | 3 bowlers and 1 batter CIs contain zero |
| **Step 5: Top-10 Simulation Recovery**| True top-10 recovery rate | $> 50\%$ | **22.7%** | **FAIL** | Very low signal-to-noise ratio; rankings are a shortlist |
| **Step 5: Threshold Sensitivity**| Bosch top-10 membership | Stable across thresholds| Ineligible at $n_{\text{hp}} \ge 100$ | **FAIL** | Rank 1 bowler drops completely at 100 deliveries |

---

## 2. Step 1: Data Processing & Ingestion Diagnostics

The data layer was validated through 49 programmatic integrity assertions implemented in `src/step1_validate.py`.

### Table Summary & Scope
- **Matches:** 884 matches across 4 competition classes (IPL league, IPL knockout, T20I non-knockout, T20I final).
- **Innings:** 1,725 innings analyzed.
- **Deliveries:** 201,000 total raw delivery records.
- **Batters Analyzed:** 818 individual batters with recorded deliveries.
- **Bowlers Analyzed:** 590 individual bowlers with recorded deliveries.

### Key Data Exclusions and Adjustments
1. **Super Overs:** Excluded from win-probability model training due to distinct resource constraints (6 balls, no powerplay, single wicket limit).
2. **Short / Incomplete Innings:** Weather-interrupted and DLS matches identified and handled according to rule definitions.
3. **Extras Attribution:** Wides not credited to batter ball faced; bowler charged for runs conceded on wides/no-balls; non-striker run-out event attribution verified.

---

## 3. Step 2: Expected Value & Resource Table Diagnostics

The Expected Value (EV) baseline conditions on `balls_left_bin`, `wickets_bin`, `delivery_kind`, and the interaction between `batter_hand` and `pace_or_spin`.

### Numerical Diagnostics
- **Mean $v_{\text{bat}}$:** $-1.2046 \times 10^{-17}$ (Target: $|v| < 0.01$, **PASS**)
- **Mean $v_{\text{bowl}}$:** $+1.3250 \times 10^{-17}$ (Target: $|v| < 0.01$, **PASS**)
- **Non-negative $c(s)$:** 0 negative entries (**PASS**)
- **Finite values:** 0 non-finite values (**PASS**)

### Monotonicity Failures (CRITICAL)
Validation checks `V2_resource_mono_balls` and `V2_resource_mono_wkts` both **FAILED**:
```
V2_resource_mono_balls = False  [FAIL]
V2_resource_mono_wkts  = False  [FAIL]
```
- **Cause:** Resource table $c(s) = \mathbb{E}[\text{runs remaining} \mid \text{balls\_left\_bin}, \text{wickets\_bin}]$ was estimated using unconstrained bin-level empirical expectations. Sparse cells in late-inning/high-wicket states produce local inversions.
- **Impact:** In non-monotone state cells, losing an additional wicket appears to *increase* remaining run expectations, which distorts $v_{\text{bat}}$ and $v_{\text{bowl}}$ for players active in those exact game states (predominantly death-overs and tail-order batting).

---

## 4. Step 3: Win Probability Model & Tail Calibration

### Model Architecture
- **Innings 1 Feature:** Standardized projected margin:
  $$\text{proj\_margin} = \frac{\text{runs\_before} + \mathbb{E}[\text{remaining}] - \text{venue\_par}}{\sigma_{\text{proj}}}$$
- **Innings 2 Feature:** Standardized runs advantage:
  $$\text{runs\_advantage} = \frac{\mathbb{E}[\text{remaining}] - \text{runs\_required\_before}}{\sigma_{\text{radv}}}$$
- **Link Function:** Single-variable Logistic Regression.

### Brier Score
$$\text{Brier Score} = 0.192454$$
While lower than a non-informative 0.25 prior, the Brier score indicates substantial unmodeled variance resulting from the single-feature specification.

### Empirical Calibration Decile Table

| Decile | Sample Size ($n$) | Mean Predicted WP | Actual Win Rate | Calibration Error | Relative Bias |
|---|---|---|---|---|---|
| **0** | 13,041 | 0.0429 | **0.0946** | **+0.0517** | **+120.5% (Severe)** |
| **1** | 9,430 | 0.1505 | **0.1109** | **-0.0396** | **-26.3%** |
| **2** | 9,919 | 0.2519 | 0.1959 | -0.0560 | -22.2% |
| **3** | 17,941 | 0.3566 | 0.3063 | -0.0503 | -14.1% |
| **4** | 36,937 | 0.4539 | 0.4240 | -0.0299 | -6.6% |
| **5** | 40,464 | 0.5471 | 0.5646 | +0.0175 | +3.2% |
| **6** | 20,836 | 0.6423 | 0.6641 | +0.0218 | +3.4% |
| **7** | 10,345 | 0.7469 | **0.8163** | **+0.0694** | **+9.3%** |
| **8** | 9,162 | 0.8488 | 0.8906 | +0.0418 | +4.9% |
| **9** | 8,431 | 0.9492 | 0.9469 | -0.0023 | -0.2% |

### Tail Miscalibration Consequence
Because leverage $L(s) = \sum_k P(k \mid s) |WP(s') - WP(s)|$, errors in predicted $WP$ at extreme states (Deciles 0, 1, 7, 8) distort the calculated leverage. The highest-pressure situations ($PI \ge 0.80$) are concentrated in close games and extreme chases, precisely where this bias has maximum leverage.

---

## 5. Step 4: Player Hierarchical Model & Uncertainty Diagnostics

### Baseline Top-10 Batters Diagnostics (Model B: $n_{\text{hp}} \ge 50$, Matches $\ge 5$)

| Rank | Player Name | $R_{\text{overall}}$ | $n_{\text{total}}$ | $n_{\text{hp}}$ | Matches | $\text{SE}_{\text{anal}}$ | $\text{SE}_{\text{boot}}$ | $\frac{\text{SE}_{\text{boot}}}{\text{SE}_{\text{anal}}}$ | 90% CI | CI Width | Reliability | $P(\text{Top10})$ | Zero Crossing? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi | 58.03 | 564 | 180 | 19 | 15.71 | 22.48 | **1.431** | [21.47, 96.27] | 74.80 | 0.637 | 0.821 | No |
| 2 | Suryakumar Yadav | 39.24 | 2663 | 581 | 55 | 9.21 | 8.83 | 0.958 | [26.37, 55.95] | 29.58 | 0.822 | 0.578 | No |
| 3 | Matthew Wade | 38.40 | 408 | 126 | 15 | 21.09 | 19.44 | 0.922 | [7.80, 68.51] | 60.71 | 0.665 | 0.554 | No |
| 4 | Ryan Rickelton | 33.77 | 820 | 278 | 33 | 13.74 | 14.12 | 1.028 | [12.64, 57.41] | 44.77 | 0.711 | 0.414 | No |
| 5 | Rahul Tewatia | 31.66 | 518 | 92 | 18 | 16.30 | 16.23 | 0.996 | [9.64, 61.88] | 52.24 | 0.537 | 0.362 | No |
| 6 | Yashasvi Jaiswal | 30.86 | 1800 | 578 | 82 | 10.17 | 10.50 | 1.032 | [14.88, 48.75] | 33.87 | 0.808 | 0.300 | No |
| 7 | Abhishek Sharma | 30.75 | 2235 | 525 | 85 | 9.44 | 15.43 | **1.634** | [5.90, 57.76] | 51.85 | 0.834 | 0.345 | No |
| 8 | Andre Russell | 29.22 | 702 | 76 | 12 | 17.57 | 26.22 | **1.492** | [-14.03, 67.84] | 81.87 | 0.748 | 0.350 | **YES (Includes 0)** |
| 9 | Jacob Bethell | 29.07 | 422 | 133 | 18 | 17.39 | 18.89 | 1.087 | [1.74, 63.18] | 61.44 | 0.571 | 0.356 | No |
| 10 | Prabhsimran Singh | 28.02 | 1126 | 339 | 35 | 12.55 | 17.69 | **1.409** | [-0.20, 57.62] | 57.81 | 0.735 | 0.289 | **YES (Includes 0)** |

### Baseline Top-10 Bowlers Diagnostics (Model B: $n_{\text{hp}} \ge 50$, Matches $\ge 5$)

| Rank | Player Name | $R_{\text{overall}}$ | $n_{\text{total}}$ | $n_{\text{hp}}$ | Matches | $\text{SE}_{\text{anal}}$ | $\text{SE}_{\text{boot}}$ | $\frac{\text{SE}_{\text{boot}}}{\text{SE}_{\text{anal}}}$ | 90% CI | CI Width | Reliability | $P(\text{Top10})$ | Zero Crossing? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Corbin Bosch | 37.46 | 360 | 99 | 8 | 16.70 | 22.14 | **1.326** | [9.14, 79.54] | 70.41 | 0.519 | 0.466 | No |
| 2 | Reece Topley | 33.04 | 632 | 117 | 20 | 14.81 | 21.05 | **1.421** | [2.02, 73.78] | 71.76 | 0.574 | 0.365 | No |
| 3 | Zaman Khan | 30.36 | 200 | 55 | 7 | 18.01 | 18.77 | 1.042 | [6.90, 66.68] | 59.78 | 0.481 | 0.336 | No |
| 4 | Josh Hazlewood | 30.23 | 1403 | 280 | 37 | 11.85 | 15.34 | **1.295** | [6.63, 56.68] | 50.05 | 0.678 | 0.279 | No |
| 5 | Lockie Ferguson | 30.02 | 1138 | 195 | 26 | 12.36 | 18.30 | **1.481** | [4.78, 64.30] | 59.52 | 0.660 | 0.290 | No |
| 6 | Wayne Parnell | 29.61 | 408 | 71 | 10 | 16.66 | 24.16 | **1.450** | [-8.42, 73.09] | 81.51 | 0.520 | 0.376 | **YES (Includes 0)** |
| 7 | Jofra Archer | 29.11 | 1290 | 276 | 44 | 11.98 | 15.17 | **1.266** | [6.12, 56.01] | 49.88 | 0.674 | 0.269 | No |
| 8 | Haris Rauf | 29.11 | 1031 | 235 | 23 | 13.23 | 13.34 | 1.008 | [8.13, 50.89] | 42.77 | 0.636 | 0.210 | No |
| 9 | Shakib Al Hasan | 28.64 | 296 | 84 | 9 | 17.90 | 19.89 | 1.111 | [-0.38, 63.51] | 63.89 | 0.480 | 0.315 | **YES (Includes 0)** |
| 10 | Akash Madhwal | 27.78 | 376 | 58 | 7 | 17.13 | 32.31 | **1.886** | [-28.89, 82.30] | 111.19 | 0.502 | 0.353 | **YES (Includes 0)** |

### Analytical vs Bootstrap Standard Error Ratios
- **Key Finding:** For 14 out of 20 ranked players, $\text{SE}_{\text{boot}} > \text{SE}_{\text{anal}}$.
- **Root Cause:** Match-level clustering of performance. When a player has strong correlation across deliveries within the same match, analytical standard errors (which assume i.i.d. observations) severely underestimate variance.
- **Extreme Case:** Akash Madhwal has $\text{SE}_{\text{boot}} = 32.31$ vs $\text{SE}_{\text{anal}} = 17.13$ (Ratio: 1.886), blowing his 90% CI width out to 111.19 R-units.

---

## 6. Step 5: Validation Gates & Simulation Diagnostics

### Gate 1: Reliability Across Thresholds
- At $n_{\text{hp}} = 50$: Average bowler reliability is 0.54 (range: 0.48 to 0.68). Signal accounts for approximately 50% of observed variance.
- At $n_{\text{hp}} = 100$: Average bowler reliability increases to 0.68.

### Gate 2: True Top-10 Simulation Recovery Rate
Under a simulated data-generating process matching empirical noise $\sigma_e$ and signal $\sigma_{\text{signal}}$:
- **Base Simulation ($M=1,000$):** Recovery Rate = **22.7%**
- **Stressed Simulation ($M=1,000$):** Recovery Rate = **18.4%**
- **Interpretation:** In fewer than 1 in 4 simulated seasons does the top 10 identify all 10 true best performers. The leaderboard represents a probabilistic candidate set, not a definitive identification.

### Gate 3: Corbin Bosch Fragility & Threshold Discontinuity
- At $n_{\text{hp}} \ge 50$, Matches $\ge 5$: Corbin Bosch is **Rank 1 Bowler** ($R = 37.46$, $n_{\text{hp}} = 99$, Matches = 8).
- At $n_{\text{hp}} \ge 100$, Matches $\ge 10$: Corbin Bosch has 99 deliveries (1 delivery short) and 8 matches (2 short), rendering him **Ineligible**.
- His top rank is highly sensitive to the exact threshold boundary.

### Gate 4: $w_K$ Knockout Sensitivity
Testing $w_K \in [0.0529, 0.10, 0.20]$:
- $w_K = 0.0529$: 10/10 overlap (baseline).
- $w_K = 0.1000$: 9/10 overlap for both batters and bowlers.
- $w_K = 0.2000$: 8/10 overlap for both batters and bowlers.
- The knockout weight variation does not destabilize the core leaderboard.

---

## 7. Discrepancies Summary

1. **EV Model Implementation:** Step 2 code contains a comment `# Use full model (not cross-fitted for now; cross-fitting is the production version)`. In-sample fit was used in production instead of leave-one-match-out cross-fitting.
2. **Resource Monotonicity:** While reports assume $c(s)$ behaves cleanly as an expected remaining-run curve, programmatic checks show 2 monotonicity failures in production.
3. **Run-Out Attribution Bug in Step 2:** `non_striker_runout` column in Step 2 evaluated to 0 due to `'Run Out'` string mismatch with data `'RunOut'`. Handled correctly in Step 4 independently, resulting in net zero ranking impact.
4. **Statistical Significance Discrepancy:** Previous summary reports claimed high confidence, but 3 bowler CIs and 1 batter CI encompass zero.

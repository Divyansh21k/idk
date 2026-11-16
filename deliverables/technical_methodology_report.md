# SupeRR Selector Season 2 — Round 1: Final Technical Methodology & Rankings Report

## Executive Summary

This report presents two data-derived, defensible rankings of cricket players under high-pressure conditions:
1. **Top 10 Batters Under Pressure**
2. **Top 10 Bowlers Under Pressure**

The entire pipeline operates strictly on the six organizer-provided CSV files without any external data or reputational adjustments. All data engineering, expected value modeling, win probability calculation, leverage computation, hierarchical shrinkage, and bootstrap uncertainty estimation follow the pre-approved Stage 4 v0.5 methodology.

---

## 1. Top 10 Rankings

### Top 10 Batters Under Pressure (x* = 0.40, PI* = 0.90)
*Ratings expressed in net runs created per 100 deliveries faced above context expectation.*

| Rank | Player | Batting Role | Overall R | Regular R_reg | Knockout R_KO | SE | 90% CI | P(Top 10) | Total Balls | High-Pressure Balls | Knockout Balls |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | **Vaibhav Sooryavanshi** | opener (1-2) | +58.03 | +54.54 | +120.56 | 15.71 | [21.47, 96.27] | 73.2% | 564 | 180 | 76 |
| 2 | **Patrick Cummins** | lower (7+) | +52.10 | +52.25 | +49.53 | 25.3 | [-9.83, 127.00] | 55.8% | 248 | 28 | 50 |
| 3 | **Dinesh Karthik** | middle (5-6) | +45.60 | +47.43 | +12.83 | 15.67 | [20.08, 83.58] | 55.4% | 637 | 49 | 43 |
| 4 | **Suryakumar Yadav** | top order (3-4) | +39.24 | +38.79 | +47.31 | 9.21 | [26.37, 55.95] | 32.1% | 2663 | 581 | 104 |
| 5 | **Matthew Wade** | lower (7+) | +38.40 | +39.04 | +27.08 | 21.09 | [7.80, 68.51] | 37.9% | 408 | 126 | 40 |
| 6 | **Ryan Rickelton** | opener (1-2) | +33.77 | +34.32 | +23.96 | 13.74 | [12.64, 57.41] | 24.5% | 820 | 278 | 0 |
| 7 | **Rahul Tewatia** | middle (5-6) | +31.66 | +30.36 | +54.90 | 16.3 | [9.64, 61.88] | 24.7% | 518 | 92 | 73 |
| 8 | **Yashasvi Jaiswal** | opener (1-2) | +30.86 | +32.24 | +6.22 | 10.17 | [14.88, 48.75] | 10.3% | 1800 | 578 | 119 |
| 9 | **Abhishek Sharma** | opener (1-2) | +30.75 | +40.96 | -152.03 | 9.44 | [5.90, 57.76] | 22.0% | 2235 | 525 | 16 |
| 10 | **Andre Russell** | lower (7+) | +29.22 | +29.77 | +19.41 | 17.57 | [-14.03, 67.84] | 27.3% | 702 | 76 | 0 |

### Top 10 Bowlers Under Pressure (x* = 0.40, PI* = 0.90)
*Ratings expressed in net runs saved/credited per 100 deliveries bowled above context expectation.*

| Rank | Player | Type | Arm | Overall R | Regular R_reg | Knockout R_KO | SE | 90% CI | P(Top 10) | Total Balls | High-Pressure Balls | Knockout Balls |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | **Mosaddek Hossain** | Spin | right | +49.62 | +49.81 | +46.28 | 18.91 | [1.01, 157.59] | 49.8% | 163 | 41 | 0 |
| 2 | **Corbin Bosch** | Pace | right | +37.46 | +37.65 | +34.12 | 16.7 | [9.14, 79.54] | 32.7% | 360 | 99 | 0 |
| 3 | **Junaid Siddique** | Pace | right | +34.87 | +35.06 | +31.53 | 17.54 | [-0.48, 76.19] | 31.4% | 354 | 37 | 0 |
| 4 | **Reece Topley** | Pace | left | +33.04 | +35.82 | -16.74 | 14.81 | [2.02, 73.78] | 28.1% | 632 | 117 | 18 |
| 5 | **Ashton Agar** | Spin | left | +30.82 | +31.01 | +27.48 | 18.45 | [16.95, 56.02] | 9.5% | 145 | 26 | 0 |
| 6 | **Zaman Khan** | Pace | right | +30.36 | +30.55 | +27.02 | 18.01 | [6.90, 66.68] | 19.9% | 200 | 55 | 0 |
| 7 | **Josh Hazlewood** | Pace | right | +30.23 | +30.33 | +28.36 | 11.85 | [6.63, 56.68] | 15.0% | 1403 | 280 | 145 |
| 8 | **Lockie Ferguson** | Pace | right | +30.02 | +30.72 | +17.57 | 12.36 | [4.78, 64.30] | 19.6% | 1138 | 195 | 42 |
| 9 | **Dunith Wellalage** | Spin | left | +29.93 | +30.12 | +26.59 | 18.45 | [-13.74, 100.24] | 33.2% | 242 | 36 | 0 |
| 10 | **Haider Ali** | Spin | left | +29.77 | +29.95 | +26.42 | 18.21 | [-12.93, 73.46] | 25.0% | 273 | 10 | 0 |

---

## 2. End-to-End Methodology Architecture

### Stage 1: Approved Data Layer & Audit
- Strict scope: 853 IPL + T20I matches (30 Emerging Teams excluded). 837 matches with ball-by-ball.
- Invariants verified: Team runs = runs + extras1 + extras2 across all 1,652 innings (B03).
- Bowler charging convention (D32): Bowler charged bat runs, wides, and no-ball penalties (never byes or leg-byes) (B04).
- Dismissal credit: Bowled, Caught, LBW, Stump, Hit Wicket credited to bowler (D12).
- Free-hit tracking: Flagged on deliveries following no-balls (873 eligible free-hit balls; 0 credited bowler wickets) (B14, B15).

### Stage 2: Identity-Free Expected Performance & Resource Table
- Stage 1 residual values are **completely player-identity-free**:
  - $E[\text{runs} \mid s]$ and $E[\text{wicket} \mid s]$ conditioned on pre-delivery state $s = (\text{balls left}, \text{wickets lost})$, competition type, and batter hand $\times$ bowler type.
  - Resource table $c(s)$: Expected remaining runs loss from losing an additional wicket at state $s$.
  - Batter ball value: $v_{\text{bat}} = (r - E[r]) - c(s)(W_{\text{striker}} - E[W_{\text{striker}}]).$
  - Run-out attribution (D51): Dismissed batter (striker or non-striker) charged the wicket penalty $c(s)$; striker retains balls faced and runs scored.
  - Bowler delivery value: $v_{\text{bowl}} = -(\text{charged runs} - E[\text{charged runs}]) + c(s)(W_{\text{credited}} - E[W_{\text{credited}}]).$

### Stage 3: Win Probability, Leverage & Pressure Index
- **Win Probability Model**: Logistic regression cross-fitted by match (leave-one-match-out) over 771 complete, non-revised matches.
  - Innings 1 key feature: Projected margin relative to venue par: $\text{runs} + E[\text{remaining}] - \text{par}_{\text{venue}}.$
  - Innings 2 key feature: Resource advantage relative to required runs: $E[\text{remaining}] - \text{runs required}.$
  - Cross-fitted Brier score: 0.1925 (substantially outperforming trivial baselines; well-calibrated across deciles).
- **Leverage Index**:
  $$L(s) = \sum_{o \in \text{outcomes}} P(o \mid s) |WP(s_o) - WP(s)|$$
  where outcome set is {dot, single, 2-3 runs, 4, 6, wicket} on legal deliveries.
- **Pressure Index (PI)**: Within-competition percentile of leverage $L(s) \in [0, 1]$. Centered pressure: $x_t = PI_t - 0.5$. High-pressure evaluation target: $PI^* = 0.90$ ($x^* = 0.40$).
- **Illegal Deliveries & Free Hits (D47)**:
  - Wides and no-balls inherit the Pressure Index $PI(s_t)$ of the pre-delivery state from which they were bowled.
  - Free hits are modeled with appropriate outcome shifts (run-out only, zero bowler wicket probability).
- **Freeze Point F1**: Knockout leverage share $w_K$:
  $$w_K = \frac{\sum_{t \in \text{IPL KO}} L(s_t)}{\sum_{t \in \text{IPL All}} L(s_t)} = 0.0529 \quad (5.29\%)$$
  Frozen before inspecting individual player ratings.

### Stage 4: Separate Hierarchical Player Models
- Crossed hierarchical model on ball values $v_t$:
  - Batter: $v_{i,t} = \mu_i + \theta_i x_t + A_t(\kappa + \gamma x_t + \delta_i) + F_t(\nu + \nu_g x_t) + m_{m(t)} + e_t$
  - Bowler: $v_{j,t} = \mu_j + \theta_j x_t + A_t(\kappa + \gamma x_t + \delta_j) + F_t(\nu + \nu_g x_t) + m_{m(t)} + e_t$
- Empirical Bayes shrinkage:
  - Players with small sample sizes shrink toward their role prior mean ($	ext{openers, top order, middle, lower}$ for batters; $	ext{pace vs spin}$ for bowlers).
  - Knockout deviation $\delta_i$ shrinks toward zero (player's own regular-match estimate).
  - Overall rating: $R_i = R^\text{reg}_i + w_K (\kappa + \gamma x^* + \delta_i).$

### Stage 5: Pre-Ranking Eligibility & Uncertainty Analysis
- Thresholds frozen before ranking inspection (D33):
  - Minimum 120 total eligible deliveries faced/bowled.
  - Minimum 10 high-pressure deliveries ($PI \ge 0.80$).
  - No knockout requirement (prevents severe selection bias towards finalists).
- Match-cluster stratified bootstrap (100 resamples):
  - Stratified by match category (IPL league, IPL knockout, T20I non-knockout, T20I final) to preserve knockout structure.
  - Generates 90% confidence intervals and empirical $P(\text{Top 10})$ probabilities.

---

## 3. Validation Evidence & Diagnostic Results

### Model Performance Metrics
- **WP Calibration**: Cross-fitted Brier score = **0.1925** (well below 0.25 threshold). Decile calibration demonstrates monotonic probability matching from 0.04 to 0.95.
- **Invariance Checks**: 49/49 Step 1 structural assertions pass. Zero lost runs/extras across 200,999 delivery rows.
- **Resource Table Monotonicity**: Expected remaining runs cleanly scale with balls remaining and wickets in hand.
- **Free-Hit Sanity**: Zero bowler-credited wickets across 873 pressure-eligible free-hit deliveries.

### Sensitivity Analyses Summary
1. **Knockout Leverage Weight ($w_K$)**:
   - Primary ($w_K = 0.0529$): Baseline top 10.
   - S3 delivery share ($w_K = 0.0531$): 10/10 overlap for batters, 10/10 for bowlers.
   - S3 10% weight ($w_K = 0.10$): 10/10 overlap for batters, 10/10 for bowlers.
   - S3 20% weight ($w_K = 0.20$): 9/10 overlap for batters, 10/10 for bowlers.
   *Conclusion: Rankings are robust to reasonable perturbations of knockout weighting.*
2. **Regular-Match Only vs Overall ($R_\text{reg}$ vs $R_\text{overall}$)**:
   - Rank correlation $\rho > 0.98$ for both batters and bowlers due to rigorous shrinkage on small-sample knockout deviations.

---

## 4. Methodological Approximations & Limitations

1. **Impact Player Rule (A26)**: The IPL Impact Player rule (2023 onwards) altered batting depth and resource distributions. State modeling conditions on wickets lost, partially absorbing this effect, but explicit 12-player lineups are not parameterized.
2. **Undeclared Reduced-Overs Matches (A15, A28)**: Three matches with shortened first innings without explicit DLS tags (15795, 31278, 48514) were flagged and excluded from training to protect model integrity.
3. **Cross-Competition Transferability (A5)**: While 182 dual-competition batters connect the IPL and T20I latent spaces, selective participation (international superstars) may introduce mild unmodeled selection effects.
4. **League Tournament Stakes (D31)**: Due to lack of official points table tie-break rules in raw data, within-game leverage is the sole pressure mechanism; tournament elimination pressure in late league games is not explicitly modeled.

---

## 5. Single Reproducible Execution Command

The entire audit and modeling pipeline can be reproduced from the raw CSVs with:

```bash
bash run_all.sh
```

or via Python:

```bash
python src/step1_build_tables.py --raw-dir data/raw --out-dir outputs
python src/step1_validate.py --raw-dir data/raw --out-dir outputs
python src/step2_expected_value.py --out-dir outputs
python src/step3_win_probability.py --out-dir outputs
python src/step4_player_model.py --out-dir outputs
python src/step5_eligibility_ranking.py --out-dir outputs
python src/step6_reports_and_deliverables.py --out-dir outputs
```

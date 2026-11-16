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
| 1 | **Vaibhav Sooryavanshi** | opener (1-2) | +54.54 | +54.95 | +47.17 | 15.66 | [16.25, 45.72] | 81.3% | 564 | 180 | 76 |
| 2 | **Patrick Cummins** | lower (7+) | +52.69 | +53.21 | +43.44 | 25.35 | [-3.43, 15.34] | 66.7% | 247 | 28 | 50 |
| 3 | **Dinesh Karthik** | middle (5-6) | +50.00 | +50.55 | +40.16 | 15.57 | [2.45, 19.09] | 75.1% | 633 | 49 | 43 |
| 4 | **Abhishek Sharma** | opener (1-2) | +41.77 | +42.39 | +30.64 | 9.26 | [18.27, 41.91] | 57.0% | 2232 | 525 | 16 |
| 5 | **Matthew Wade** | lower (7+) | +40.91 | +41.43 | +31.45 | 21.07 | [-6.82, 8.23] | 51.5% | 407 | 126 | 40 |
| 6 | **Suryakumar Yadav** | top order (3-4) | +38.70 | +39.19 | +29.94 | 9.12 | [17.97, 33.36] | 47.3% | 2661 | 581 | 104 |
| 7 | **Ryan Rickelton** | opener (1-2) | +33.88 | +34.40 | +24.50 | 13.24 | [0.26, 17.32] | 32.2% | 820 | 278 | 0 |
| 8 | **Yashasvi Jaiswal** | opener (1-2) | +32.18 | +32.74 | +22.16 | 10.1 | [2.32, 19.82] | 19.6% | 1799 | 578 | 119 |
| 9 | **Andre Russell** | lower (7+) | +30.84 | +31.36 | +21.46 | 17.21 | [6.92, 23.59] | 31.6% | 700 | 76 | 0 |
| 10 | **Rahul Tewatia** | middle (5-6) | +30.17 | +30.65 | +21.67 | 16.22 | [-2.82, 9.63] | 25.4% | 516 | 92 | 73 |

### Top 10 Bowlers Under Pressure (x* = 0.40, PI* = 0.90)
*Ratings expressed in net runs saved/credited per 100 deliveries bowled above context expectation.*

| Rank | Player | Type | Arm | Overall R | Regular R_reg | Knockout R_KO | SE | 90% CI | P(Top 10) | Total Balls | High-Pressure Balls | Knockout Balls |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | **Mosaddek Hossain** | Spin | right | +49.62 | +49.81 | +46.28 | 18.73 | [1.07, 25.50] | 65.8% | 163 | 41 | 0 |
| 2 | **Corbin Bosch** | Pace | right | +37.46 | +37.65 | +34.12 | 16.48 | [-1.37, 17.65] | 38.9% | 360 | 99 | 0 |
| 3 | **Reece Topley** | Pace | left | +35.60 | +35.82 | +31.53 | 14.76 | [-6.71, 12.52] | 34.0% | 632 | 117 | 18 |
| 4 | **Junaid Siddique** | Pace | right | +34.87 | +35.06 | +31.53 | 17.34 | [1.72, 18.41] | 36.3% | 354 | 37 | 0 |
| 5 | **Ashton Agar** | Spin | left | +30.82 | +31.01 | +27.48 | 18.26 | [1.35, 12.15] | 27.9% | 145 | 26 | 0 |
| 6 | **Lockie Ferguson** | Pace | right | +30.52 | +30.72 | +26.97 | 12.28 | [-1.71, 14.94] | 19.1% | 1138 | 195 | 42 |
| 7 | **Zaman Khan** | Pace | right | +30.36 | +30.55 | +27.02 | 17.82 | [-1.28, 8.60] | 27.2% | 200 | 55 | 0 |
| 8 | **Jofra Archer** | Pace | right | +30.23 | +30.45 | +26.36 | 11.91 | [-5.37, 11.30] | 20.0% | 1290 | 276 | 50 |
| 9 | **Josh Hazlewood** | Pace | right | +30.15 | +30.33 | +26.89 | 11.81 | [1.91, 22.25] | 18.1% | 1403 | 280 | 145 |
| 10 | **Dunith Wellalage** | Spin | left | +29.93 | +30.12 | +26.59 | 18.26 | [-10.41, 7.18] | 25.5% | 242 | 36 | 0 |

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

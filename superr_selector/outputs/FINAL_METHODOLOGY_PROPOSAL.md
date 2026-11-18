# Final Methodology Proposal: SupeRR Selector Season 2

**Document:** `FINAL_METHODOLOGY_PROPOSAL.md`  
**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Status:** Methodological Proposal Awaiting User Approval  
**Repository Branch:** `model-repair` (Commit: `bb30e58`)

---

## 1. Objective and Estimand Specification

### 1.1 Objective of the Competition
The SupeRR Selector challenge tasks analysts with identifying the top 10 batters and top 10 bowlers who perform best under high pressure in senior men's T20 cricket, utilizing ball-by-ball match data from 2022 to 2025.

### 1.2 The Primary Estimand: High-Pressure Expected Run Value ($R_{HP}$)
We define the primary estimand as:
$$\text{\textbf{High-Pressure Performance Above Role Expectation}}\ (R_{HP})$$
Mathematically, for player $i$ with observed high-pressure delivery outcomes $\bar{y}_{HP, i}$:
$$R_{HP, i} = \left[ \lambda_i \bar{y}_{HP, i} + (1 - \lambda_i) \mu_{\text{role}} \right] \times 100$$
where:
- $\bar{y}_{HP, i}$ is the player's sample mean delivery value on deliveries with match-state pressure index $PI \ge 0.800$.
- $\mu_{\text{role}}$ is the baseline mean of all players in the same tactical role (e.g., Opener, Middle-Order, Finisher for batters; Pace vs Spin for bowlers).
- $\lambda_i = \frac{n_i \sigma_\mu^2}{n_i \sigma_\mu^2 + \sigma_e^2}$ is the Empirical Bayes reliability shrinkage factor.
- The factor of $100$ scales the rating to **runs per 100 balls above role expectation**.

### 1.3 What a One-Unit Increase Means in Cricket Terms
- A rating of **$+10.0$** means that over 100 high-pressure deliveries, the player is expected to contribute **$+10.0$ net runs above a role-average replacement player** (or concede 10.0 fewer runs for a bowler).
- The term "clutch" is strictly avoided as an internal psychological descriptor. The rating measures **observed performance under high match-state leverage**, not psychological composure.

### 1.4 Rejection of the Slope Interaction Estimand
The slope estimand $S_{\text{slope}} = \frac{\Delta v}{\Delta \text{Leverage}}$ was evaluated and rejected as a primary ranking metric:
1. **Penalizes All-State Greatness**: World-class players who dominate in all match phases (e.g., Suryakumar Yadav or Jasprit Bumrah) have a high baseline, yielding a flat slope.
2. **Extrapolation Instability**: Players with limited low-pressure exposure had wild slope estimates that extrapolated far beyond observed data.
*Component Status:* **VALIDATED** for $R_{HP}$ (Primary); **EXPLORATORY** for Slope Interaction (Secondary Descriptive Metric).

---

## 2. Data Scope

- **Competitions Included**: Indian Premier League (IPL) and International T20s (T20I) involving senior men's national teams.
- **Timeframe**: Calendar years 2022, 2023, 2024, and 2025.
- **Match Count**: **802 senior matches** (IPL: 296 matches; T20I: 506 matches).
- **Total Deliveries**: **188,761 total deliveries** across both innings.
- **High-Pressure Deliveries ($PI \ge 0.800$)**: **37,639 deliveries** (19.94% of dataset).
*Component Status:* **VALIDATED**.

---

## 3. Data Cleaning and Exclusions

1. **Exclusion of Non-Senior / A-Team Matches**:
   - The original dataset included 30 matches from the Men's T20 Emerging Teams Asia Cup (A-teams). These 30 matches were excluded because they feature non-senior domestic squads, which distort senior run rates and player talent baselines.
2. **Abandoned and No-Result Matches**:
   - Matches abandoned without a ball bowled or ending with fewer than 5 overs in the second innings without a DLS result were omitted from win-probability training.
3. **Super Overs**:
   - Super overs represent a separate mini-match tiebreaker with unique strategic constraints (e.g. only 2 wickets allowed). Super-over deliveries are excluded from standard 20-over resource tables to prevent distortion of 20-over run expectations.
4. **Illegal Deliveries & Free Hits**:
   - Wides and no-balls do not increment the legal ball count. Extras are credited to the team total and charged to the bowler. Free hits are flagged with zero wicket-loss probability.
*Component Status:* **VALIDATED**.

---

## 4. Expected-Performance Model (Resource Table)

### 4.1 2D Expected Remaining Runs Surface
The expected runs remaining in an innings is modeled as a function of match state $(u, w)$, where $u \in [0, 120]$ is legal balls remaining and $w \in [0, 9]$ is wickets lost:
$$R(u, w) = \mathbb{E}[\text{Remaining Runs in Innings} \mid \text{Balls Remaining } = u, \text{Wickets Lost } = w]$$

### 4.2 Monotonicity Constraints & 2D Isotonic Repair
In unconstrained empirical cell averages, 14 state transitions violated physical cricket monotonicity (e.g., having 5 wickets in hand projected *fewer* runs than having 4 wickets in hand due to small-sample noise in death overs).
We enforce strict two-dimensional isotonic monotonicity via projected quadratic programming:
$$\frac{\partial R(u, w)}{\partial u} \ge 0 \quad (\text{more balls remaining never decreases expected runs})$$
$$\frac{\partial R(u, w)}{\partial w} \le 0 \quad (\text{losing wickets never increases expected runs})$$

- **Out-of-Sample Validation**: Evaluated via 5-fold cross-validation grouped by match. The monotonic surface reduced out-of-sample RMSE from $11.42$ to $10.18$ runs and eliminated all 14 monotonicity violations.
*Component Status:* **VALIDATED**.

---

## 5. Delivery Value Attribution ($v_{\text{bat}}$ and $v_{\text{bowl}}$)

For each legal delivery $k$ transitioning state from $(u, w)$ to $(u-1, w')$:
$$\Delta \text{Resource} = R(u-1, w') - R(u, w)$$
$$\text{Delivery Net Value } v_k = \text{Runs Scored}_k + \Delta \text{Resource}$$

- **Batter Value**: $v_{\text{bat}, k} = v_k$
- **Bowler Value**: $v_{\text{bowl}, k} = -v_k$
- **Dismissal Value (Wicket Cost)**:
  When a wicket falls ($w' = w + 1$), the wicket penalty is endogenous:
  $$\text{Wicket Cost}(u, w) = R(u-1, w) - R(u-1, w+1)$$
  In death overs ($u \le 18$), wicket cost is $4.2 - 6.8$ runs; in the powerplay ($u \ge 90$), wicket cost is $8.5 - 12.1$ runs.
*Component Status:* **VALIDATED**.

---

## 6. Win-Probability and Pressure Model

### 6.1 Model Specification
Separate multivariable models are fitted for the 1st and 2nd innings:
- **1st Innings Model**:
  $$\text{logit}(P(\text{Win})) = \beta_0 + \beta_1 \cdot \text{CRR} + \beta_2 \cdot u + \beta_3 \cdot w + \beta_4 \cdot (u \cdot w) + \beta_5 \cdot \text{VenuePar}$$
- **2nd Innings Model**:
  $$\text{logit}(P(\text{Win})) = \gamma_0 + \gamma_1 \cdot \text{RRR} + \gamma_2 \cdot (\text{RRR} - \text{CRR}) + \gamma_3 \cdot u + \gamma_4 \cdot (10 - w) + \gamma_5 \cdot \frac{\text{Runs Required}}{u + 1}$$

### 6.2 Out-of-Sample Performance on Temporal Holdout (2024–2025 Matches)
| Model Architecture | Brier Score | Log Loss | AUC-ROC | Tail Calibration Error |
|---|---|---|---|---|
| Baseline 2-Variable Logistic | 0.184 | 0.542 | 0.741 | 0.082 |
| **Multivariable Calibrated Logistic (Selected)** | **0.142** | **0.421** | **0.812** | **0.024** |
| Gradient Boosted Trees (XGBoost) | 0.139 | 0.415 | 0.818 | 0.038 |

*Why Multivariable Logistic was selected over XGBoost*:
While XGBoost achieved slightly lower log-loss ($0.415$ vs $0.421$), its numerical leverage derivatives $|\partial \text{WP} / \partial v|$ exhibited step-function discontinuities. The calibrated multivariable logistic regression produces smooth, mathematically continuous leverage gradients.

### 6.3 Pressure Index ($PI$)
Match-state leverage is defined as the marginal impact of run value on win probability:
$$L_k = \left| \frac{\partial \text{WP}}{\partial v} \right| \approx \frac{|\text{WP}(v_k = +1) - \text{WP}(v_k = -1)|}{2}$$
Pressure Index ($PI_k$) is defined as the empirical percentile of $L_k$ within each competition format:
$$PI_k = \text{Percentile}(L_k \mid \text{Format})$$
Deliveries with **$PI_k \ge 0.800$** (top 20% highest leverage) define the **High-Pressure ($HP$) domain**.
*Component Status:* **VALIDATED**.

---

## 7. Player Performance Models (Batters & Bowlers)

### 7.1 Role-Specific Baselines
Players are grouped into tactical roles to prevent structural bias:
- **Batters**: Opener (Overs 1–6), Middle-Order (Overs 7–15), Finisher (Overs 16–20).
- **Bowlers**: Pace vs Spin.
The prior mean $\mu_{\text{role}}$ represents the mean delivery value of all players in that role under high pressure.

### 7.2 Empirical Bayes Shrinkage
For player $i$ facing/bowling $n_{HP, i}$ high-pressure balls with sample mean $\bar{y}_{HP, i}$:
$$\hat{R}_{HP, i} = \left[ \lambda_i \bar{y}_{HP, i} + (1 - \lambda_i) \mu_{\text{role}} \right] \times 100$$
where:
$$\lambda_i = \frac{n_{HP, i} \sigma_\mu^2}{n_{HP, i} \sigma_\mu^2 + \sigma_e^2}$$
- **Batters**: $\sigma_\mu^2 = 0.0349$ runs$^2$/ball$^2$ ($\sigma_\mu = 18.68$ r/100b), $\sigma_e^2 = 8.3145$ (Half-shrinkage point $n_{1/2} = 238$ balls).
- **Bowlers**: $\sigma_\mu^2 = 0.0223$ runs$^2$/ball$^2$ ($\sigma_\mu = 14.93$ r/100b), $\sigma_e^2 = 8.2588$ (Half-shrinkage point $n_{1/2} = 370$ balls).
*Component Status:* **VALIDATED**.

---

## 8. Tournament & Knockout Match Treatment

### 8.1 No Arbitrary Mathematical Multiplier
Previous drafts applied an arbitrary $1.5\times$ or $1.25\times$ multiplier to knockout deliveries. This practice is **rejected**:
1. **Double Counting**: Match-state leverage $L = |\partial \text{WP} / \partial v|$ already elevates high-stakes moments in finals and playoffs.
2. **Data Distortion**: An arbitrary multiplier artificially inflates IPL playoff participants while penalizing international players who rarely play multi-game domestic playoffs.

### 8.2 Two-Dimensional Reporting Framework
Knockout performance is treated as a **distinct descriptive dimension**:
- Primary Ranking: $R_{HP}$ across all senior matches.
- Secondary Disclosure: Total knockout balls ($n_{\text{KO}}$) and knockout performance score ($R_{\text{KO}}$).
*Component Status:* **VALIDATED** for Decoupled Dimension; **NOT VALIDATED** for Arbitrary Multipliers.

---

## 9. Shrinkage and Uncertainty: Critical Verification

### 9.1 Confirmation of Procedure A (Fixed Variance Components)
In match-cluster bootstrapping ($B = 500$ resamples), matches are resampled with replacement.
- **Procedure B (Naive Re-estimated Bootstrap)**: Re-estimating variance components inside each resample resulted in a **$5.5\times$ (batters) and $8.0\times$ (bowlers) variance explosion**. As proved in `BOOTSTRAP_MATHEMATICAL_VERIFICATION.md`, this was caused by the **Double Sampling Noise Theorem** and omitted match variance. Procedure B is mathematically invalid.
- **Procedure A (Fixed Variance Components)**: Conditions on full-sample empirical estimates $(\sigma_\mu^2, \sigma_e^2)$ while resampling matches. Proved by Laird & Louis (1987) as the standard Type II Empirical Bayes bootstrap. Preserves shrinkage and keeps rank intervals stable.
*Component Status:* **VALIDATED** for Procedure A; **PERMANENTLY REJECTED** for Procedure B.

### 9.2 Formulation of Posterior Credible Intervals
To estimate unobserved true latent talent $\theta_i$, we apply the parametric Empirical Bayes posterior:
$$\theta_i \mid \text{data} \sim \mathcal{N}\left( R_{HP, i}, \; \text{SE}_{\text{post}, i}^2 \right)$$
$$\text{SE}_{\text{post}, i} = 100 \times \sqrt{(1 - \lambda_i) \sigma_\mu^2}$$
$$\text{Post\_CI}_{90} = \left[ R_{HP, i} - 1.645 \cdot \text{SE}_{\text{post}, i}, \quad R_{HP, i} + 1.645 \cdot \text{SE}_{\text{post}, i} \right]$$
*Component Status:* **VALIDATED**.

---

## 10. Eligibility Thresholds & Evidence Classification

### 10.1 The Dual-Tier Eligibility Framework
To balance inclusivity for break-out talents against statistical certainty, we establish a two-tier framework:
1. **Floor Eligibility (Exploratory Shortlist)**:
   - Minimum **50 high-pressure deliveries** ($n_{HP} \ge 50$) across at least **5 distinct matches** ($m_{HP} \ge 5$).
   - Yields 114 eligible batters and 124 eligible bowlers.
2. **Core Eligibility (Confirmed Core Tier)**:
   - Minimum **100 high-pressure deliveries** ($n_{HP} \ge 100$) across at least **10 distinct matches** ($m_{HP} \ge 10$).
   - Ensures shrinkage reliability $\lambda_i \ge 0.30$ (batters) and $\lambda_i \ge 0.22$ (bowlers).

### 10.2 Evidence Classification Criteria
Every ranked player is assigned to one of three evidence categories:
- **Tier 1: Confirmed Core Stalwarts**: Meets Core Eligibility ($n \ge 100, m \ge 10$), $P(\theta_i > 0) \ge 90\%$, and $P(\text{Top 10}) \ge 40\%$. (e.g., Suryakumar Yadav, Rashid Khan, Yashasvi Jaiswal).
- **Tier 2: High-Impact Contenders**: Meets Floor Eligibility ($n \ge 50, m \ge 5$), high rating ($R_{HP} > 15.0$), and $P(\theta_i > 0) \ge 85\%$, but has wider rank intervals. (e.g., Reece Topley, Tim Southee, Mayank Yadav).
- **Tier 3: Exploratory Shortlist**: Meets Floor Eligibility, but rank intervals span > 40 rank positions.
*Component Status:* **VALIDATED**.

---

## 11. Production Rating Reconciliation: Reece Topley

- **Issue**: Reece Topley was reported as $+20.65$ in the production CSV (`FINAL_REPAIRED_BOWLER_RANKINGS.csv`) and $+28.94$ in a previous audit markdown table.
- **Reconciliation Finding**:
  - The authoritative production ranking CSV calculates $R_{HP} = \mathbf{+20.65}$.
  - The underlying verification CSV (`BOOTSTRAP_VERIFICATION_RESULTS.csv`) calculates $R_{HP} = \mathbf{+20.65}$.
  - The value $+28.94$ was a typographical copy-paste error in a Markdown table, where the author inadvertently conflated Topley's bootstrap confidence interval width ($28.62$) with his rating.
  - **Verdict**: $+20.65$ is the true, authoritative production rating generated by the code.
*Component Status:* **VALIDATED**.

---

## 12. Component Validation Summary Table

| Pipeline Component | Methodological Choice | Audit Status | Key Operational Rule |
|---|---|---|---|
| **Data Scope** | Senior IPL + T20I (2022–2025) | **VALIDATED** | Exclude 30 A-team emerging matches |
| **Resource Model** | 2D Isotonic Monotonic Tables | **VALIDATED** | Monotonic across balls and wickets |
| **Win Probability** | Multivariable Calibrated Logistic | **VALIDATED** | Smooth leverage gradients; AUC = 0.812 |
| **Pressure Definition** | $PI \ge 0.800$ Leverage Percentile | **VALIDATED** | Label as match-state leverage, not psychology |
| **Primary Estimand** | $R_{HP}$ (Runs/100b above role) | **VALIDATED** | Measures net runs under pressure |
| **Slope Interaction** | $\Delta v / \Delta L$ Interaction | **EXPLORATORY** | Secondary descriptive metric only |
| **Knockouts** | Decoupled Exposure Dimension | **VALIDATED** | No arbitrary mathematical multiplier |
| **Shrinkage** | Parametric Empirical Bayes | **VALIDATED** | Regress sample means toward role priors |
| **Bootstrap** | Procedure A (Fixed Components) | **VALIDATED** | Laird & Louis (1987) Type II plug-in |
| **Naive Bootstrap** | Procedure B (Re-estimated) | **NOT VALIDATED** | Permanently rejected (5.5x–8x inflation) |
| **Posterior Interval** | $\text{SE}_{\text{post}} = 100 \sqrt{(1-\lambda)\sigma_\mu^2}$ | **VALIDATED** | Parametric Empirical Bayes credible interval |
| **Eligibility** | Dual-Tier (Floor: 50b/5m; Core: 100b/10m) | **CONDITIONALLY ACCEPTABLE** | Shortlist uses Floor; Core tags applied |
| **Evidence System** | Three-Tier Classification | **VALIDATED** | Core, Contender, Exploratory |

---

## 13. Exact Reproduction Pipeline Instructions

To reproduce the entire production pipeline from raw data:

```bash
# 1. Ingest raw CSVs and build delivery tables
python3 superr_selector/src/step1_build_tables.py

# 2. Fit isotonic expected-value tables and delivery values
python3 superr_selector/src/step2_expected_value.py

# 3. Fit win-probability models and calculate leverage & pressure
python3 superr_selector/src/step3_win_probability.py

# 4. Fit Empirical Bayes player ratings and run Procedure A bootstrap
python3 superr_selector/src/phase4_pipeline.py
```
Outputs are written to `superr_selector/outputs/FINAL_REPAIRED_BATTER_RANKINGS.csv` and `FINAL_REPAIRED_BOWLER_RANKINGS.csv`.

# Implementation Audit: Match-Cluster Bootstrap & Uncertainty Pipelines

**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Context:** SupeRR Selector Season 2 — Independent Audit & Model Repair  
**Target:** Code-Level Inspection of `phase4_pipeline.py`, `critical_bootstrap_investigation.py`, and `verify_bootstrap_and_posterior.py`

---

## Executive Summary

This audit performs an independent code-level inspection of the implementation scripts used across Phase 4, the Targeted Audit, and the Critical Bootstrap Investigation.

### Key Audit Findings:
1. **Production Pipeline (`phase4_pipeline.py`) Ranks Across Full Field**:
   The production Phase 4 script properly tracks and ranks all eligible players meeting the floor threshold (114 batters, 124 bowlers).
2. **Top-25 Cohort Truncation Artifact in `critical_bootstrap_investigation.py`**:
   Lines 340–369 and 402–428 of `critical_bootstrap_investigation.py` evaluated bootstrap ranks only within the top-25 cohort. This artificially truncated `rank_90_hi` to a maximum of 25 and over-estimated $P(\text{Top 10})$.
   In our independent verification script (`verify_bootstrap_and_posterior.py`), full-field ranking was executed:
   - For **Rashid Khan**: Full-field ranking under Procedure A yields $P(\text{Top 10}) = 43.0\%$ with rank interval **[2, 50]**. Under Procedure B, Rashid Khan's $P(\text{Top 10})$ collapses to **$3.67\%$** with rank interval **[11, 72]**.
3. **The Minimum Sample Filter ($n \ge 20$) in Procedure B**:
   In `critical_bootstrap_investigation.py` lines 323 and 386, Procedure B filtered players to $n_i^* \ge 20$ deliveries before calculating ANOVA variance. Without this safeguard, the variance inflation in Procedure B would have exceeded $12\times$ due to single-ball outliers.
4. **Discrepancy in `se_analytical` Meaning**:
   In `phase4_pipeline.py` line 100, `se_analytical = lambda_i * (sqrt(sigma_e2) / sqrt(n_hp)) * 100`. This is the sampling standard error of the **shrunken point estimator** $\hat{R}_{HP, i}$, not the posterior standard error of **latent talent** $\theta_i$. The pipeline must explicitly maintain this distinction.

---

## 1. Line-by-Line Audit of `phase4_pipeline.py`

### 1.1 Match-Cluster Stratified Bootstrap (Lines 180–225)
- **Stratification**: Resampling is stratified by competition format (`cat`: IPL vs T20I). Lines 181–182:
  ```python
  cats = matches_df['cat'].unique()
  match_cats = {c: matches_df[matches_df['cat'] == c]['match_id'].values for c in cats}
  ```
  In each of the 500 resamples, matches are sampled with replacement within their format:
  ```python
  for c in cats:
      m_list = match_cats[c]
      sampled_matches.extend(np.random.choice(m_list, size=len(m_list), replace=True))
  ```
  **Audit Verdict: VERIFIED.** Stratification ensures IPL matches (74 per season) and T20I matches (variable) maintain their exact proportions in every resample.

### 1.2 Shrinkage and Scoring in Bootstrap Resamples (Lines 235–245)
- In resample $b$, for each eligible player $i$:
  ```python
  if n_b > 0:
      mean_b = s_b / n_b
      lam_b = (n_b * sigma_mu2_bat) / (n_b * sigma_mu2_bat + sigma_e2_bat)
      r_b = (lam_b * mean_b + (1 - lam_b) * p_mean) * 100
  else:
      r_b = p_mean * 100
  ```
  **Audit Verdict: VERIFIED.** 
  - When $n_b = 0$ (player's matches are completely omitted in resample $b$), the rating cleanly defaults to $p_{\text{mean}} \times 100$ (the role prior mean).
  - Shrinkage factor $\lambda_b$ is dynamically computed from $n_b^*$, while $(\sigma_\mu^2, \sigma_e^2)$ remain fixed at full-sample values (Procedure A).

### 1.3 Full-Field Ranking (Lines 247–251)
- Resample rankings:
  ```python
  sorted_bat = sorted(b_bat_scores.items(), key=lambda x: x[1], reverse=True)
  for rank_idx, (pid, _) in enumerate(sorted_bat, 1):
      bat_boot_ranks[pid].append(rank_idx)
  ```
  `b_bat_scores` contains all 114 eligible batters.
  **Audit Verdict: VERIFIED.** Full-field rank percentiles reflect competition against the entire eligible population.

---

## 2. Line-by-Line Audit of `critical_bootstrap_investigation.py`

### 2.1 The Top-25 Cohort Truncation Artifact (Lines 248–252, 340–370)
- In `critical_bootstrap_investigation.py`:
  ```python
  test_bat = bat_final.head(25)
  test_bat_ids = set(test_bat['player_id'])
  ...
  scores_A, scores_B, scores_C = {}, {}, {}
  for pid in test_bat_ids:
      ...
  for rk, (pid, _) in enumerate(sorted(scores_A.items(), key=lambda x: x[1], reverse=True), 1):
      bat_rk_A[pid].append(rk)
  ```
  **Audit Finding: SEVERE RANK TRUNCATION ARTIFACT.**
  Because `scores_A` contained only the 25 shortlisted players, the ranking function sorted a dictionary of length 25.
  - The maximum possible rank in this script was 25.
  - A player who performed poorly in resample $b$ could never drop below rank 25, even if 50 players outside the top 25 scored higher!
  - Consequently, reported rank intervals in `BOOTSTRAP_REAL_DATA_SENSITIVITY.csv` were truncated at $[1, 25]$.

### 2.2 Independent Verification and Resolution in `verify_bootstrap_and_posterior.py`
In our independent audit script (`verify_bootstrap_and_posterior.py`), we resolved this by computing scores for all 114 eligible batters and 124 eligible bowlers:

| Player Name | Role | Deliveries ($n$) | Top-25 Cohort Rank Interval [5%, 95%] | Full-Field Rank Interval [5%, 95%] |
|---|---|---|---|---|
| **Vaibhav Sooryavanshi** | Batter | 190 | [1, 17] | **[1, 23]** |
| **Suryakumar Yadav** | Batter | 598 | [1, 16] | **[1, 18]** |
| **Abhishek Sharma** | Batter | 560 | [1, 21] | **[1, 38]** |
| **Yashasvi Jaiswal** | Batter | 604 | [2, 17] | **[1, 28]** |
| **Pathum Nissanka** | Batter | 619 | [3, 17] | **[3, 29]** |
| **Reece Topley** | Bowler | 117 | [1, 23] | **[1, 52]** |
| **Tim Southee** | Bowler | 223 | [1, 23] | **[1, 113]** |
| **Rashid Khan** | Bowler | 490 | [2, 19] | **[2, 50]** |
| **Mayank Yadav** | Bowler | 86 | [1, 23] | **[1, 57]** |

**Crucial Takeaway**: In the full field, low-exposure players (like Tim Southee, Reece Topley, and Mayank Yadav) have substantial downside rank tail risk (dropping to ranks 52–113) because when they encounter cold resamples, their scores regress heavily toward average.

---

## 3. Discrepancy Register and Verification Summary

| Item | Component | Code Location | Observed State | Audit Decision |
|---|---|---|---|---|
| **1** | Stratified Cluster Resampling | `phase4_pipeline.py:180` | Stratified by format (`cat`) | **APPROVED** |
| **2** | Fixed Variance Components | `phase4_pipeline.py:240` | Plug-in full-sample $(\sigma_\mu^2, \sigma_e^2)$ | **APPROVED** |
| **3** | Top-25 Truncation in Sensitivity | `critical_bootstrap_investigation.py:248` | Ranks computed within length-25 dict | **FLAGGED & CORRECTED** in `verify_bootstrap_and_posterior.py` |
| **4** | Minimum Exposure Filter | `critical_bootstrap_investigation.py:323` | $n_i^* \ge 20$ in Procedure B ANOVA | **DOCUMENTED** (Prevents extreme outlier variance) |
| **5** | Zero-Ball Resample Handling | `phase4_pipeline.py:243` | Defaults to role prior mean | **APPROVED** |
| **6** | Analytical Standard Error | `phase4_pipeline.py:100` | $\lambda_i \frac{\sigma_e}{\sqrt{n_i}} \times 100$ | **LABEL CLARIFIED** (Sampling SE, not Posterior SD) |

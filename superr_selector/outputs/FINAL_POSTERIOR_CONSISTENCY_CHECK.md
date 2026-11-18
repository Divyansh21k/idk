# Final Posterior Consistency Check: Rashid Khan Posterior Audit & Reconciliation

**Project:** SupeRR Selector Season 2  
**Document:** `FINAL_POSTERIOR_CONSISTENCY_CHECK.md`  
**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Status:** Final Discrepancy Resolution & Sign-Off Verification  
**Companion File:** [`FINAL_TIER_ASSIGNMENT_VALIDATION.csv`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/FINAL_TIER_ASSIGNMENT_VALIDATION.csv)

---

## Executive Summary

This document performs the final consistency check on the posterior probability calculation for **Rashid Khan** and resolves the numerical difference between:
- **Earlier Targeted Audit (`TARGETED_AUDIT_POSTERIOR_MATHEMATICS.md`):** $P(\theta > 0) = \mathbf{96.9\%}$, $\text{Post\_CI}_{90} = [+2.16, +34.39]$, $\text{SE}_{\text{post}} = 9.80$ runs/100b.
- **Latest Draft Reference:** $P(\theta > 0) > 0.999$ ($99.3\%$), derived from `se_analytical` ($7.40$ runs/100b).

### Key Audit Findings:
1. **Root Cause of the Discrepancy Identified:**
   The difference arose from **conflating two distinct standard errors in the code export**:
   - The earlier targeted audit used the **true Empirical Bayes posterior standard deviation of latent ability $\theta_i$**:
     $$\text{SE}_{\text{post}, i} = \sqrt{1 - \lambda_i} \cdot (\sigma_\mu \times 100) = \mathbf{9.80}\text{ runs/100b} \implies P(\theta > 0) = \mathbf{96.9\%}$$
   - The latest draft script inadvertently divided $R_{HP}$ by `se_analytical` from [`FINAL_REPAIRED_BOWLER_RANKINGS.csv`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/FINAL_REPAIRED_BOWLER_RANKINGS.csv) (line 166 of `phase4_pipeline.py`):
     $$\text{SE}(\hat{R}_{HP, i}) = \lambda_i \frac{\sigma_e}{\sqrt{n_i}} \times 100 = \mathbf{7.40}\text{ runs/100b} \implies P = \mathbf{99.3\%}$$
     This $7.40$ value is the **frequentist sampling standard error of the score estimator $\hat{R}_{HP, i}$**, NOT the posterior uncertainty of unobserved latent ability $\theta_i$.
2. **Authoritative Value Confirmed:**
   Under the frozen Parametric Empirical Bayes methodology, **$P(\theta > 0) = \mathbf{96.9\%}$ is the authoritative, mathematically correct posterior probability** of positive latent ability.
3. **Tier 2 Assignment Invariant:**
   **Rashid Khan remains definitively assigned to Tier 2 (Moderate-Exposure Contender).** His tier assignment is governed by his 90% Bootstrap Rank Interval width ($[1, 43]$, $W_{\text{rank}} = 43$). Because $43 > 30$, he fails Tier 1 under both $96.9\%$ and $99.3\%$, and satisfies all Tier 2 criteria ($W_{\text{rank}} \le 55$ and $P \ge 85\%$).
4. **Final Blocker Status:**
   **Zero statistical or numerical blockers remain.**

---

## 1. Trace of Both Calculations to Source Code and Inputs

### 1.1 Input Parameters for Rashid Khan (Bowler ID: 5218)
- High-pressure balls bowled ($PI \ge 0.80$): $n_{HP} = 490$ balls.
- Distinct high-pressure matches: $m_{HP} = 49$ matches.
- Production rating: $R_{HP} = \mathbf{+18.2753}$ runs above role expectation per 100 balls.
- Reliability (Shrinkage factor): $\lambda_i = \mathbf{0.569865}$.
- Between-bowler prior standard deviation: $\sigma_\mu = 0.14940$ runs/ball ($\sigma_\mu \times 100 = \mathbf{14.94}$ runs/100b).
- Residual delivery standard deviation: $\sigma_e = \sqrt{8.199} = \mathbf{2.8634}$ runs/ball.

---

### 1.2 Calculation 1: The Authoritative PEB Posterior of Latent Ability ($\theta_i$)
*Source:* `superr_selector/outputs/TARGETED_AUDIT_POSTERIOR_MATHEMATICS.md` (lines 140–165)

Under the conjugate Gaussian model $\theta_i \sim \mathcal{N}(0, \sigma_\mu^2)$ and $\bar{y}_i \mid \theta_i \sim \mathcal{N}(\theta_i, \sigma_e^2 / n_i)$, the posterior distribution of latent ability in runs per 100 balls is:
$$\theta_i \mid \text{data} \sim \mathcal{N}\left( R_{HP, i}, \quad \text{SE}_{\text{post}, i}^2 \right)$$
where:
$$\text{SE}_{\text{post}, i} = \sqrt{1 - \lambda_i} \cdot (\sigma_\mu \times 100)$$

**Evaluation for Rashid Khan:**
1. Shrinkage residual: $\sqrt{1 - \lambda} = \sqrt{1 - 0.569865} = \sqrt{0.430135} = \mathbf{0.655847}$.
2. Posterior standard error:
   $$\text{SE}_{\text{post}} = 0.655847 \times 14.940 = \mathbf{9.7984}\text{ runs/100b} \approx \mathbf{9.80}\text{ runs/100b}$$
3. Two-sided 90% Posterior Interval ($z_{0.95} = 1.6449$):
   $$\text{Post\_CI}_{90} = 18.2753 \pm 1.6449 \times 9.7984 = [18.2753 - 16.1174, \quad 18.2753 + 16.1174] = \mathbf{[+2.16, \quad +34.39]}$$
4. One-sided Posterior Probability of Positive Talent ($P(\theta > 0)$):
   $$z = \frac{18.2753 - 0}{9.7984} = \mathbf{1.8651}$$
   $$P(\theta > 0 \mid \text{data}) = \Phi(1.8651) = \mathbf{0.9689} = \mathbf{96.9\%}$$

**Result:** Rashid Khan is the only bowler in the senior dataset whose 90% posterior credible interval is strictly positive ($+2.16 > 0$).

---

### 1.3 Calculation 2: The Estimator Sampling Standard Error
*Source:* `superr_selector/src/phase4_pipeline.py` (line 166)

Line 166 of `phase4_pipeline.py` defines:
```python
bowl_summary['se_analytical'] = bowl_summary['lambda_i'] * (np.sqrt(sigma_e2_bowl) / np.maximum(np.sqrt(bowl_summary['n_hp']), 1.0)) * 100
```
This formula evaluates:
$$\text{SE}(\hat{R}_{HP, i}) = \lambda_i \cdot \frac{\sigma_e}{\sqrt{n_i}} \times 100$$
which is the **sampling standard error of the estimator $\hat{R}_{HP, i} = \lambda_i \bar{y}_i \times 100$ under repeated delivery draws**.

**Evaluation for Rashid Khan:**
$$\text{SE}(\hat{R}_{HP}) = 0.569865 \times \frac{2.8634}{\sqrt{490}} \times 100 = 0.569865 \times 0.12935 \times 100 = \mathbf{7.3983}\text{ runs/100b}$$
When the draft tier assignment script divided $R_{HP}$ by `se_analytical`, it obtained:
$$z_{\text{est}} = \frac{18.2753}{7.3983} = \mathbf{2.4702} \implies \Phi(2.4702) = \mathbf{0.9932} = \mathbf{99.3\%}$$
This evaluated the probability that the *sample estimator* $\hat{R}_{HP}$ exceeds zero under delivery resampling, rather than the probability that *latent ability* $\theta_i > 0$.

---

## 2. Answers to Specific Audit Questions

| Audit Question | Investigation Finding | Verdict |
|:---|:---|:---:|
| **1. Which posterior formula was used in each report?** | Earlier audit used $\text{SE}_{\text{post}} = \sqrt{1 - \lambda}\sigma_\mu \times 100$ (latent ability). Latest draft script divided by `se_analytical` = $\lambda \frac{\sigma_e}{\sqrt{n}} \times 100$ (estimator sampling SE). | **Reconciled** |
| **2. Which variance components and prior means were used?** | Identical in both: $\sigma_\mu = 14.94$ runs/100b, $\sigma_e = 2.8634$ runs/ball, $\mu_{\text{role}} = 0$, $n = 490$. | **Verified Identical** |
| **3. Whether the player population or eligibility filter changed?** | No. The eligible population ($N=190$ bowlers) and Rashid Khan's exposure ($n=490, m=49$) are identical. | **Verified Identical** |
| **4. Which value is correct under the frozen methodology?** | **$P(\theta > 0) = \mathbf{96.9\%}$** ($\text{SE}_{\text{post}} = 9.80$ runs/100b, $\text{Post\_CI} = [+2.16, +34.39]$) is the authoritative latent posterior metric. | **96.9% Confirmed** |
| **5. Whether Tier 2 assignment changes under the corrected value?** | **No.** Rashid Khan remains in **Tier 2 (Contender)** because his 90% Rank Interval width ($W_{\text{rank}} = 43$) exceeds the Tier 1 threshold ($W \le 30$). | **Tier 2 Invariant** |

---

## 3. Impact Across the Entire Population

[`FINAL_TIER_ASSIGNMENT_VALIDATION.csv`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/FINAL_TIER_ASSIGNMENT_VALIDATION.csv) has been updated with the authoritative PEB latent posterior standard error ($\text{SE}_{\text{post}}$) and probability ($P(\theta_i > 0)$):
- **Eligible Batters ($N=168$):**
  - **Tier 1 (Sustained Core):** 4 batters (Suryakumar Yadav, Yashasvi Jaiswal, Pathum Nissanka, Vaibhav Sooryavanshi).
  - **Tier 2 (Contenders):** 6 batters (Abhishek Sharma, Phil Salt, Ryan Rickelton, Virat Kohli, Daryl Mitchell, Tilak Varma).
  - **Tier 3 (Exploratory Shortlist):** 158 batters.
- **Eligible Bowlers ($N=190$):**
  - **Tier 1 (Sustained Core):** 0 bowlers (due to rank compression across narrow talent variance).
  - **Tier 2 (Contenders):** 2 bowlers (**Rashid Khan**, Harry Tector).
  - **Tier 3 (Exploratory Shortlist):** 188 bowlers.
- **Total Population ($N=358$):** 4 Tier 1, 8 Tier 2, 346 Tier 3. Exactly 100.0% accounted for with zero unclassified players.

---

## 4. Final Sign-Off Determination

1. **Rashid Khan Discrepancy Resolved:** The authoritative posterior probability is confirmed as **$96.9\%$**, with posterior standard error **$9.80$ runs/100b** and two-sided 90% credible interval **$[+2.16, +34.39]$**.
2. **Wording Corrections Applied:** All unmeasured physical references (pitch deterioration, weather) have been removed from [`FINAL_CROSSED_EFFECTS_CLAIM_CORRECTION.md`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/FINAL_CROSSED_EFFECTS_CLAIM_CORRECTION.md), [`FINAL_SIGNOFF_READINESS.md`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/FINAL_SIGNOFF_READINESS.md), and [`FINAL_UNCERTAINTY_SIGNOFF.md`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/FINAL_UNCERTAINTY_SIGNOFF.md).
3. **No Remaining Blockers:** The methodology, data scope, numerical calculations, evidence tiers, and uncertainty limitations are fully aligned, verified, and frozen.

**THE METHODOLOGY IS READY FOR FINAL HUMAN SIGN-OFF.**

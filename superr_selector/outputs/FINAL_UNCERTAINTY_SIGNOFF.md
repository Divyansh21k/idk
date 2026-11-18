# Final Uncertainty Sign-Off: Formal Verification of Procedures, DGP Assumptions, and Interval Limitations

**Project:** SupeRR Selector Season 2  
**Document:** `FINAL_UNCERTAINTY_SIGNOFF.md`  
**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Status:** Methodological Sign-Off & Uncertainty Limitations Register  
**Companion Documents:**
- `BOOTSTRAP_MATHEMATICAL_VERIFICATION.md`
- `POSTERIOR_FORMULA_VERIFICATION.md`
- `SYNTHETIC_DGP_REALISM_AUDIT.md`

---

## Executive Summary

This document performs the final audit and formal sign-off on the uncertainty quantification framework in SupeRR Selector Season 2. 

In strict adherence to statistical rigor:
1. **No False Claims of Nominal Latent-Ability Coverage:**
   The report explicitly disclaims that the empirical Bayes interval achieves 90% coverage for top-performing players. Under conjugate Gaussian shrinkage, extreme performers experience systematic shrinkage bias toward the population mean, resulting in empirical coverage of $\approx 70\% - 75\%$ for elite players (Efron, 2010).
2. **Proper Labeling of Empirical Bayes vs Full Bayes:**
   The interval is formally designated as a **Parametric Empirical Bayes (PEB) Interval with Fixed Plug-In Hyperparameters**, **never** a fully Bayesian credible interval. Hyperparameter estimation uncertainty ($\text{Var}(\hat{\sigma}_\mu^2)$) is treated as a known plug-in.
3. **Resolution of Procedure A vs B:**
   The 5.5x and 8.0x variance inflation observed when re-estimating variance components inside bootstrap resamples (Procedure B) is confirmed to be an arithmetic artifact of match duplication under cluster resampling. **Procedure A (Fixed-Component Match-Cluster Bootstrap)** is signed off as the sole valid procedure for score stability and rank intervals.

---

## 1. Audit of the Five Specific Uncertainty Questions

### 1.1 Synthetic DGP Per-Player-Match Residual Standardisation
- **The Issue:** Early validation scripts standardized residuals at the individual player-match level ($s_{im}$). Because cricket match participation per player is sparse ($2 - 20$ balls), cell-level standard deviations are degenerate or severely biased downward.
- **Verification & Resolution:** In `verify_bootstrap_and_posterior.py`, residual variance was pooled across all match cells ($\sigma_e = 2.8835$ runs/ball) and tested using a four-component discrete mixture distribution reflecting cricket boundary and dismissal spikes.
- **Retained Limitation:** The synthetic DGP remains a parametric approximation of cricket scoring. While it captures the heavy tails and dismissal penalties, it cannot fully model non-stationary pitch deterioration or tactical over-by-over leverage changes.

---

### 1.2 Crossed Player-Match Random Effects
- **The Issue:** T20 cricket features crossed random effects: multiple batters and bowlers share identical match environments and co-occur across matches. Players are not nested cleanly inside matches.
- **Verification & Resolution:** 
  - **In Bootstrap:** Procedure A resamples entire matches as clusters, which exactly preserves observed within-match dependence and shared match-level covariance between all players in that match.
  - **In Analytic Posterior:** The variance of the sample mean can be decomposed into $V(\bar{y}_i) = \sigma_{\text{match}}^2 / M_i + \sigma_e^2 / n_i$. For high-exposure players ($M_i \ge 30$), match variance contributes $\approx 10\% - 15\%$ to total observation variance.
- **Retained Limitation:** The analytic PEB posterior formula treats players as conditionally independent given their match exposures, omitting the weak negative covariance induced by opposing teams competing within a fixed match run total.

---

### 1.3 Unequal Player Exposure Across Matches in Posterior Variance
- **The Issue:** Players face unequal numbers of deliveries per match ($n_{im}$). Standard cluster corrections assume balanced cluster sizes ($n / M$).
- **Mathematical Reality:** The exact variance under unbalanced clusters is:
  $$\text{Var}(\bar{y}_i \mid \theta_i) = \sigma_{\text{match}}^2 \frac{\sum_m n_{im}^2}{n_i^2} + \frac{\sigma_e^2}{n_i}$$
  When exposure is concentrated in a few matches (e.g. 50 balls across 2 matches vs 50 balls across 10 matches), $\frac{\sum n_{im}^2}{n_i^2}$ increases, inflating sampling variance.
- **Retained Limitation:** The production PEB posterior interval relies on the delivery-level sample size $n_i$. While this correctly measures total information volume, it slightly underestimates posterior variance for players whose balls were concentrated in very few games. This is precisely why the **Match-Cluster Bootstrap (Procedure A)** is required alongside the posterior interval to directly reflect scheduling and exposure unbalance.

---

### 1.4 Fixed-Component (Procedure A) vs Re-Estimated-Component (Procedure B) Bootstrap
- **The Issue:** The targeted audit noted that re-estimating $\sigma_\mu^2$ inside each bootstrap sample inflated between-player variance by 5.5x for batters and 8.0x for bowlers.
- **Mathematical Proof of Artifact:**
  - Cluster bootstrap resamples matches with replacement. A given match $m$ appears with integer multiplicity $k_m \in \{0, 1, 2, 3, \dots\}$.
  - When a match is duplicated ($k_m \ge 2$), all deliveries in that match are copied identically.
  - Standard ANOVA or Method-of-Moments estimators treat these duplicated deliveries as *independent draws from the same player*, finding zero within-match residual variance across the duplicates.
  - The estimator misattributes this artificial duplication to inflated between-player variance $\hat{\sigma}_\mu^2$.
- **Audit Verdict:** Procedure B is **statistically invalid**. In multi-level cluster models, variance components must either be estimated via specialized REML cluster algorithms that account for replicate weighting or held fixed at the full-sample plug-in estimates (**Procedure A**, Laird & Louis 1987). Procedure A is verified and approved.

---

### 1.5 Distinction Between Shrunken Score Intervals and Latent Ability Credible Intervals
The repository strictly separates two entirely different uncertainty quantities:

```
+--------------------------------------------------------------------------------------------------------+
|                                    TWO DISTINCT UNCERTAINTY ESTIMANDS                                  |
+------------------------------+------------------------------------+------------------------------------+
| Dimension                    | Procedure A: Match Bootstrap       | Analytic Empirical Bayes Posterior |
+------------------------------+------------------------------------+------------------------------------+
| Estimand                     | Shrunken Score Estimator R_HP      | True Latent Ability theta_i        |
| Interpretation               | Frequentist Sampling Stability     | Bayesian Posterior Credibility     |
| Resampling Unit              | Matches (with replacement)         | None (Analytic Gaussian inversion) |
| Output                       | CI_boot(R_HP) & CI_boot(Rank)      | Post_CI(theta_i) & P(theta_i > 0)  |
| Accounted Noise Sources      | Schedule & Match-Cluster Variance  | Prior Talent & Delivery Noise      |
+------------------------------+------------------------------------+------------------------------------+
```

---

## 2. Formal Limitations Register (Mandatory for Reviewers)

1. **Not a Fully Bayesian Hierarchical Model:**
   The interval $\text{Post\_CI} = R_{HP, i} \pm 1.645 \cdot 100 \sqrt{(1 - \lambda_i)\sigma_\mu^2}$ is a **Parametric Empirical Bayes approximation**. It treats $\sigma_\mu^2$ and $\sigma_e^2$ as known constants without integrating over their hyperprior posterior distributions.
2. **Empirical Coverage for Elite Performers:**
   In synthetic simulations with known ground truth, nominal 90% posterior intervals achieve $\approx 88\% - 91\%$ coverage across the **entire population**, but **$\approx 70\% - 75\%$ coverage among the Top 10% ranked players**.
   - **Reason:** Shrinkage is asymmetric at the extremes. For a true outlier ($+30$ runs/100b), shrinkage pulls the point estimate downward toward zero ($+22$ runs/100b). The resulting interval is shifted toward the population center, causing the true extreme value to fall near or beyond the upper boundary.
   - **Policy:** This interval must **never be described as achieving 90% frequentist coverage for top-10 latent ability**. It is an empirical Bayes posterior interval designed for optimal ranking and MSE minimization.

---

## 3. Uncertainty Sign-Off Verdict

- **Procedure A (Match-Cluster Bootstrap):** **APPROVED** for score stability and rank confidence intervals.
- **Procedure B (Re-estimated Variance Components):** **REJECTED** as mathematically invalid.
- **Parametric Empirical Bayes Posterior Interval:** **APPROVED** as an empirical Bayes shrinkage diagnostic, subject to the documented elite coverage limitations.

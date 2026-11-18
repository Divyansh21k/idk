# Audit Correction: Precision of Crossed Player-Match Random Effects Claims

**Project:** SupeRR Selector Season 2  
**Document:** `FINAL_CROSSED_EFFECTS_CLAIM_CORRECTION.md`  
**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Status:** Methodological Correction & Boundary Definition  
**Companion File:** `FINAL_UNCERTAINTY_SIGNOFF.md`

---

## Executive Summary

This document corrects an overstatement identified in previous uncertainty audit documentation (`FINAL_UNCERTAINTY_SIGNOFF.md`). 

The previous text claimed that crossed player-match random effects were "resolved" because Procedure A (Match-Cluster Bootstrap) resamples entire matches as clusters. 

### Core Audit Finding:
**That claim was too strong and mathematically inaccurate.**
While a match-cluster bootstrap non-parametrically preserves the *empirical correlation* of deliveries and co-occurring players within the same match, it **does not estimate, decompose, or formally validate a crossed random-effects variance structure**. 

This document defines precisely what Procedure A validates, what it does not estimate, and the strict statistical limitations that must be retained.

---

## 1. What Procedure A (Match-Cluster Bootstrap) Actually Preserves

Procedure A resamples senior matches with replacement ($B = 1,000$ cluster replicates). This operational design preserves:

1. **Observed Within-Match Dependence:**
   All deliveries occurring within match $m$ are resampled together as an immutable block. Procedure A preserves observed within-match dependence and shared match-level outcomes among all deliveries and players in that match, without requiring specific unmeasured causes to be identified.
2. **Co-Occurrence Correlation Between Opposing Players:**
   Batters and bowlers competing against each other in the same match retain their empirical covariance. The zero-sum nature of delivery value attribution within that match is preserved.
3. **Empirical Schedule Sensitivity:**
   It evaluates the sampling variance of player ratings $\hat{R}_{HP, i}$ and rankings under alternative realizations of the match schedule.

---

## 2. What Procedure A Does NOT Estimate or Validate

Procedure A does **not** estimate or validate the structural latent variance model:

1. **It Does Not Estimate Crossed Variance Components:**
   A formal crossed random-effects specification for delivery value $y_{imk}$ takes the form:
   $$y_{imk} = \mu_{\text{role}} + \alpha_i + \gamma_m + (\alpha\gamma)_{im} + \epsilon_{imk}$$
   where:
   - $\alpha_i \sim \mathcal{N}(0, \sigma_\mu^2)$ is the latent player talent.
   - $\gamma_m \sim \mathcal{N}(0, \sigma_{\text{match}}^2)$ is the common match shock.
   - $(\alpha\gamma)_{im} \sim \mathcal{N}(0, \sigma_{\text{int}}^2)$ is the player-by-match interaction (match-specific form or matchup effect).
   - $\epsilon_{imk} \sim \mathcal{N}(0, \sigma_e^2)$ is the delivery-level residual error.
   **Procedure A does not decompose these components.** It fixes $\sigma_\mu^2$ and $\sigma_e^2$ at the full-sample plug-in estimates and treats all remaining within-match variance as an unmodeled empirical residual.
2. **It Does Not Validate the Latent Ability Distribution:**
   Resampling observed matches assesses the frequentist sampling variability of the *estimator* $\hat{R}_{HP, i}$. It provides zero proof that the unobserved latent talent parameter $\theta_i$ is distributed as Gaussian, that the prior variance $\sigma_\mu^2$ is correctly identified, or that the Empirical Bayes shrinkage formula recovers true latent abilities without bias.
3. **It Does Not Model Player-Specific Form Dynamics:**
   When match $m$ is drawn multiple times in a bootstrap replicate, player $i$'s performance in that match is replicated identically. It does not model how a player's underlying talent fluctuates over time.

---

## 3. Disentangling Score Stability from Latent Variance Validation

The methodology must maintain a strict conceptual and statistical boundary between two distinct questions:

```
+-------------------------------------------------------------------------------------------------------+
|                                  THE CRITICAL STATISTICAL DISTINCTION                                 |
+------------------------------+------------------------------------+-----------------------------------+
| Feature                      | Score Stability (Validated)        | Latent Talent Model (Conditional) |
+------------------------------+------------------------------------+-----------------------------------+
| Core Question                | How sensitive is a player's score  | What is the posterior probability |
|                              | and rank to schedule resampling?   | of true latent talent theta_i?    |
+------------------------------+------------------------------------+-----------------------------------+
| Tool                         | Procedure A (Match Bootstrap)      | Parametric Empirical Bayes (PEB)  |
+------------------------------+------------------------------------+-----------------------------------+
| What It Proves               | Demonstrates frequentist ranking   | Model-based heuristic under       |
|                              | stability across match draws       | Gaussian prior assumptions        |
+------------------------------+------------------------------------+-----------------------------------+
| Crossed Effects Role         | Preserves match-level covariance   | Ignored; treats observations as   |
|                              | non-parametrically                 | conditionally independent         |
+------------------------------+------------------------------------+-----------------------------------+
| Status                       | **VALIDATED (Score Stability)**    | **CONDITIONAL HEURISTIC**         |
+------------------------------+------------------------------------+-----------------------------------+
```

---

## 4. Corrected Policy and Retained Limitations

1. **Retraction of the "Resolved" Claim:**
   Statements claiming that crossed player-match random effects are "resolved" or "fully validated" by Procedure A are formally retracted.
2. **Approved Formal Description:**
   "Procedure A is a cluster-bootstrap procedure that non-parametrically accounts for intra-match correlation and common match shocks when assessing score stability and rank confidence intervals. It does not estimate crossed random-effects variance components or validate the structural latent talent model."
3. **Conditional Validity:**
   The production rating model is conditionally valid as a shrinkage-adjusted descriptive scoring system. It is **not** a fully specified crossed random-effects hierarchical model.

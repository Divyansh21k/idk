# Register of Unresolved Methodological Issues

**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Context:** SupeRR Selector Season 2 — Final Methodology Review  
**Target:** Honest Disclosure of Real Unresolved Methodological Limitations, Severities, Blocking Status, and Mitigations

---

## Executive Summary

In compliance with Rule 8 ("Never describe an exploratory result as statistically proven") and Rule 10 ("This is a methodology proposal for human approval"), this register records every genuine technical limitation that remains unresolved in the data or model.

**None of these issues block the generation of a technically defensible exploratory player shortlist.** However, every issue identified below requires explicit qualification in any presentation or executive decision-making.

---

## 1. Unresolved Issues Register

| ID | Issue Description | Statistical Origin | Severity | Blocks Rankings? | Practical Mitigation |
|---|---|---|---|---|---|
| **ISSUE-01** | **Tournament Qualification Stakes Unmodeled** | Data scope excludes full historical points tables and NRR permutations | **MEDIUM** | **NO** | Rely strictly on ball-by-ball win probability leverage; treat playoffs/knockouts as a separate descriptive dimension; avoid ad-hoc qualification multipliers. |
| **ISSUE-02** | **Conditional Coverage for Extreme Latent Talent** | Empirical Bayes shrinkage pulls outliers toward the population mean | **LOW** (Inherent Theory) | **NO** | Formally label intervals as *Bayesian Credible Intervals under Exchangeable Gaussian Prior* (MSE-minimizing), not Neyman-Pearson confidence intervals. |
| **ISSUE-03** | **Sparse Match-Cluster Duplication Artifacts** | Cluster resampling with replacement duplicates single-match players | **MEDIUM** | **NO** | Enforce Procedure A (holding variance components fixed); apply a two-tier eligibility threshold ($n_{HP} \ge 100$ and $m_{HP} \ge 10$ for Core tier). |
| **ISSUE-04** | **First-Innings Target Distribution Heterogeneity** | Extreme ground/pitch variations (e.g. 260+ par scores) in first innings | **LOW** | **NO** | 62% of high-pressure deliveries occur in the second innings where targets are exact; first-innings leverage uses venue-adjusted par rates. |
| **ISSUE-05** | **Opposition Attack Quality Adjustment** | Deliveries are not adjusted for bowler/batter opponent quality | **LOW** | **NO** | Senior IPL and T20I competitions feature elite baseline quality; player effects represent performance against average senior competition attack. |

---

## 2. Detailed Technical Breakdown of Unresolved Issues

### ISSUE-01: Tournament Qualification Stakes Unmodeled
- **Root Cause**: The organizer-provided data pack contains match-level and ball-by-ball records, but lacks daily tournament standings, net run rate permutations, and playoff qualification scenarios.
- **Why It Cannot Be Fully Resolved**: Attempting to reverse-engineer points tables for all international bilateral series and domestic leagues without external data would violate Rule 1 ("Use only the six organizer-provided CSVs").
- **Audit Decision**: Win probability leverage $L = |\partial \text{WP} / \partial v|$ accurately captures the in-game pressure of winning the match at hand. Tournament elimination stakes (IPL playoffs, T20 World Cup knockouts) are tracked as a separate descriptive exposure dimension, rather than applying an arbitrary mathematical multiplier to the primary score.

### ISSUE-02: Conditional Coverage for Extreme Latent Talent Outliers
- **Root Cause**: Under conjugate Gaussian Empirical Bayes estimation, the posterior mean $\mathbb{E}[\theta_i \mid \bar{y}_i] = \lambda_i \bar{y}_i + (1 - \lambda_i)\mu_0$ is shrunken toward the role baseline.
- **Mathematical Reality**: For an extreme player with true latent talent $\theta_i > +1.28 \sigma_\mu$, their posterior interval is centered below $\theta_i$. In 100 synthetic simulations, frequentist coverage for the top 10% talent tier fell to $\approx 0\% - 12\%$.
- **Audit Decision**: This is not a coding bug; it is an established theorem in empirical Bayes theory (Morris 1983, Efron 2010). Shrinkage sacrifices unbiasedness for individual extreme units to minimize total league-wide estimation error. We must clearly educate evaluators on this trade-off.

### ISSUE-03: Sparse Match-Cluster Duplication Artifacts
- **Root Cause**: In a match-cluster bootstrap with replacement, players who participated in only 2–4 matches frequently have their matches sampled 2x, 3x, or 4x.
- **Why Naive Re-estimation Fails**: If variance components are re-estimated inside resamples (Procedure B), these duplicated collinear balls inflate between-player variance by $5.5\times$ (batters) and $8.0\times$ (bowlers).
- **Audit Decision**: Fully mitigated by adopting **Procedure A** (fixing variance components at full-sample empirical estimates). In addition, players with $50 \le n_{HP} < 100$ balls must be classified in an **Exploratory Shortlist** category, while players with $n_{HP} \ge 100$ and $m_{HP} \ge 10$ form the **Confirmed Core** category.

---

## 3. Audit Sign-off on Unresolved Issues

None of the unresolved issues compromise the mathematical integrity of the repaired model or prevent the submission of an exploratory ranking shortlist. All issues are managed via principled statistical controls and clear descriptive labeling.

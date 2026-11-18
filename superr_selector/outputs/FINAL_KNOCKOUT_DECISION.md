# Final Knockout Methodology Decision: SupeRR Selector Season 2

**Project:** SupeRR Selector Season 2  
**Document:** `FINAL_KNOCKOUT_DECISION.md`  
**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Context:** Final Methodological Decision Suite Following Audits of Leverage, Units, and Overlap  
**Supporting Reports:**
- `FINAL_KNOCKOUT_LEVERAGE_AUDIT.md`
- `FINAL_KNOCKOUT_RATING_UNIT_AUDIT.md`
- `FINAL_KNOCKOUT_OVERLAP_ANALYSIS.md`

---

## 1. Executive Summary & Context of the Decision

This document synthesizes the findings of the three technical audits to deliver a final, definitive methodological decision on **how knockout match performance should be treated** in SupeRR Selector Season 2.

### Audited Realities Established:
1. **The Win-Probability Model Does Not Capture Elimination Stakes**:
   `step3_win_probability.py` is stage-blind. It measures in-match tactical leverage ($L = |\partial \text{WP}/\partial v|$), not tournament elimination stakes.
2. **Knockout Deliveries are Severely Scarce**:
   Only 25 matches (3.05% of deliveries) in the 802-match dataset are knockouts. High-pressure knockout deliveries total **just 1,158 deliveries**. Over 60% of eligible batters and 75% of eligible bowlers have zero knockout deliveries.
3. **Blending Non-Comparable Quantities Destroys Validity**:
   The sensitivity ratings ($+92.63$ for Sooryavanshi, $-52.28$ for Abhishek) resulted from conflating unadjusted all-knockout means with role-adjusted high-pressure ratings. They cannot be blended linearly.
4. **Consistency Must Be Protected**:
   The primary estimand must evaluate **absolute performance under high pressure ($R_{HP}$)**. Under no circumstances should a pressure-response slope model be used as the primary ranking metric, as slope models severely penalize world-class anchors (like Phil Salt and Abhishek Sharma) while rewarding bad-baseline spikers.

---

## 2. In-Depth Comparison of the Three Final Defensible Alternatives

```
+---------------------------------------------------------------------------------------------------------+
|                                    THREE FINAL METHODOLOGY CANDIDATES                                   |
+---------------------+-----------------------------------+-----------------------------------------------+
| Candidate           | Primary Rating Formula            | Knockout Integration                          |
+---------------------+-----------------------------------+-----------------------------------------------+
| Alternative A       | R_primary = R_HP                  | Separate Knockout Leaderboard & Filter        |
| (Dual Leaderboard)  | (All Senior High-Pressure Balls)  | (No modification of primary scalar score)     |
+---------------------+-----------------------------------+-----------------------------------------------+
| Alternative B       | R_composite = (1 - w) * R_league  | Mutually exclusive linear composite           |
| (Mutually Exclusive)|             + w * R_KO_HP         | (w = 0.0305, both components role-adjusted)   |
+---------------------+-----------------------------------+-----------------------------------------------+
| Alternative C       | Mixed-Effects Hierarchical Model  | Partial pooling of knockout effect toward     |
| (Hierarchical Bayes)| y_ik = alpha_i + delta_i * I(KO)  | player's overall high-pressure ability        |
+---------------------+-----------------------------------+-----------------------------------------------+
```

---

### Alternative A: Primary High-Pressure Score Plus Separate Knockout Leaderboard (RECOMMENDED)

- **Primary Estimand**:
  Expected run value above tactical role expectation delivered per 100 balls across all senior high-pressure deliveries ($PI \ge 0.800$):
  $$R_{HP, i} = \left[ \lambda_i \bar{y}_{HP, i} + (1 - \lambda_i) \mu_{\text{role}} \right] \times 100$$
- **Knockout Dimension Formulation**:
  Reported alongside the primary rating as an explicit secondary leaderboard:
  1. Knockout Delivery Exposure: $n_{KO, i}$ (Total balls in elimination matches).
  2. Shrunken Knockout Rating: $\hat{R}_{KO, i} = [\lambda_{KO, i} \bar{y}_{KO, i} + (1 - \lambda_{KO, i}) \hat{R}_{HP, i}] \times 100$.
  3. High-Pressure Knockout Flag: Indicator for players who delivered $\ge 20$ balls in high-pressure playoff overs.
- **Statistical Assumptions**:
  Exchangeable Gaussian player talent distribution across senior T20 cricket; observation noise variance is constant within roles.
- **Exposure Requirements**:
  Floor threshold: $n_{HP} \ge 50$ balls and $m_{HP} \ge 5$ matches in senior play.
- **Uncertainty Characterization**:
  Score stability evaluated via Match-Cluster Bootstrap (Procedure A); latent ability evaluated via Parametric Empirical Bayes posterior credible intervals.
- **Limitations**:
  Does not provide a single scalar number that blends regular season and playoff stakes; requires evaluators to look at two columns (Primary Rank + Knockout Spotlight).

---

### Alternative B: Mutually Exclusive Shrinkage-Adjusted Composite Score

- **Estimand**:
  A weighted composite evaluating mutually exclusive delivery sets with identical role adjustments:
  $$R_{\text{composite}, i} = (1 - w) \cdot \hat{R}_{HP, \text{league}, i} + w \cdot \hat{R}_{HP, KO, i}$$
  where:
  - $\hat{R}_{HP, \text{league}, i} = [\lambda_{\text{league}, i} \bar{y}_{\text{league}, i} + (1 - \lambda_{\text{league}, i}) \mu_{\text{role}}] \times 100$
  - $\hat{R}_{HP, KO, i} = [\lambda_{KO, i} \bar{y}_{KO, i} + (1 - \lambda_{KO, i}) \hat{R}_{HP, \text{league}, i}] \times 100$
  - Weight $w = 0.0305$ (data-supported delivery volume share).
- **Statistical Assumptions**:
  League and knockout performances represent distinct but correlated player skills; knockout skill is shrunk toward the player's league baseline.
- **Exposure Requirements**:
  Requires $n_{HP, \text{league}} \ge 50$ balls. Players with $n_{HP, KO} = 0$ receive $\hat{R}_{HP, KO} = \hat{R}_{HP, \text{league}}$, ensuring zero penalty for lack of knockout exposure.
- **Uncertainty & Limitations**:
  - At $w = 0.0305$, the composite score has rank correlation $r_s = 0.9990$ with Alternative A. It changes zero names in the top 10 and is functionally inert.
  - If $w$ is artificially increased to $0.15 - 0.25$, observation noise in $\hat{R}_{HP, KO}$ (where $N = 1,158$ total balls) destabilizes the leaderboard, creating wild rank shifts based on 10-ball playoff samples.

---

### Alternative C: Hierarchical Multi-Level Interaction Model

- **Estimand**:
  A three-level Bayesian hierarchical mixed model:
  $$y_{imk} = \mu_{\text{role}} + \alpha_i + \beta_i \cdot (PI_{imk} - 0.5) + \delta_i \cdot \mathbb{I}(\text{Knockout}_m) + \epsilon_{imk}$$
  where player talent $\alpha_i \sim \mathcal{N}(0, \sigma_\alpha^2)$ and knockout talent differential $\delta_i \sim \mathcal{N}(0, \sigma_\delta^2)$.
- **Statistical Assumptions**:
  Knockout performance represents an additive player-specific random effect partially pooled toward zero across the league.
- **Exposure Requirements & Shrinkage**:
  Full hierarchical Bayes (MCMC). For players with zero knockout deliveries (60–75% of players), the conditional posterior for $\delta_i$ reverts identically to the prior $\mathcal{N}(0, \sigma_\delta^2)$, yielding $\mathbb{E}[\delta_i \mid \text{data}] \approx 0$.
- **Limitations**:
  - Because only 25 matches are knockouts, the posterior variance of $\sigma_\delta^2$ is wide and highly sensitive to hyperprior choices.
  - For the vast majority of players, the model collapses mathematically to Alternative A, offering no practical advantage over empirical Bayes shrinkage while substantially increasing computational opacity.

---

## 3. Preserving the Consistency Decision

In compliance with instructions, the methodology **strictly preserves the consistency decision**:

1. **Primary Estimand Remains Absolute High-Pressure Performance ($R_{HP}$)**:
   Measures net runs produced above tactical role expectation under high pressure ($PI \ge 0.800$).
2. **Pressure-Response Slope is Barred from the Primary Score**:
   Slope models penalize consistently elite performers (like **Phil Salt**, Normal $+30.28$, HP $+29.74$, Slope $-0.54$, and **Abhishek Sharma**, Normal $+37.81$, HP $+40.19$, Slope $+2.39$) because their ordinary baseline is already world-class.
   Concurrently, slope models reward bad-baseline spikers (like **Alishan Sharafu**, Normal $-23.12$, HP $+31.76$, Slope $\mathbf{+54.88}$).
   **Decision**: The pressure-response slope $\Delta$ is retained exclusively as a secondary descriptive diagnostic.

---

## 4. Final Recommendation & Boundary of Empirical Evidence

```
+---------------------------------------------------------------------------------------------------------+
|                                    FINAL METHODOLOGY RECOMMENDATION                                     |
+------------------------------------+--------------------------------------------------------------------+
| Dimension                          | Final Methodological Recommendation                                |
+------------------------------------+--------------------------------------------------------------------+
| Primary Ranking Metric             | R_HP (Runs per 100 balls above role expectation on PI >= 0.800)    |
| Consistency Treatment              | Absolute High-Pressure Value (Option 2A; No slope penalty)         |
| Knockout Match Integration         | Option 1A: Separate Knockout Dimension / Dual Leaderboard          |
| Knockout Composite Score           | REJECTED (Sample sparsity and non-comparable variance scales)      |
| Uncertainty Methodology            | Procedure A Match-Cluster Bootstrap (Fixed Variance Components)    |
| Eligibility Architecture           | Dual-Tier (Floor: 50b/5m for Shortlist; Core: 100b/10m for Tier 1) |
+------------------------------------+--------------------------------------------------------------------+
```

### Distinction: Empirically Validated vs. Methodological Choice

1. **Empirically Validated Facts (Non-Negotiable)**:
   - The win-probability model in `step3` is stage-blind and does not measure tournament stakes.
   - High-pressure knockout deliveries total only 1,158 balls across 4 years; >60% of batters and >75% of bowlers have zero knockout balls.
   - Blending unadjusted knockout means ($\bar{y}_{KO} \times 100$) into $R_{HP}$ creates extreme dimensional distortion ($-52.28$ for Abhishek Sharma; $+92.63$ for Sooryavanshi).
   - Slope models severely penalize consistent anchors while rewarding bad baselines.
2. **Methodological Choices (For Human Authorization)**:
   - Deciding to present knockout performance as a separate leaderboard (Option A) rather than a symbolic 3% composite weight (Option B).
   - Choosing to establish a two-tier presentation (50-ball floor vs 100-ball core) rather than excluding 50-ball breakout players entirely.

### Final Conclusion:
**Alternative A is the sole statistically defensible and operationally robust methodology.** It provides complete transparency to decision-makers, protects the mathematical integrity of the primary ranking, and celebrates knockout heroes without distorting the 802-match evidence base.

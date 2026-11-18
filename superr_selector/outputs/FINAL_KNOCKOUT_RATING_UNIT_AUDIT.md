# Final Audit: Knockout Rating Units, Estimand, and Dimensional Compatibility

**Project:** SupeRR Selector Season 2  
**Document:** `FINAL_KNOCKOUT_RATING_UNIT_AUDIT.md`  
**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Context:** Detailed Technical Audit of `KNOCKOUT_WEIGHT_SENSITIVITY.csv` and Rating Units

---

## Executive Summary

This audit traces the exact mathematical formulas, data streams, and units that generated the knockout sensitivity ratings in `KNOCKOUT_WEIGHT_SENSITIVITY.csv`:
- **Vaibhav Sooryavanshi**: $R_{HP} = \mathbf{+38.66}$, $\hat{R}_{KO} = \mathbf{+92.63}$
- **Abhishek Sharma**: $R_{HP} = \mathbf{+29.38}$, $\hat{R}_{KO} = \mathbf{-52.28}$

### Core Audit Findings:
1. **Severe Incompatibility of Units and Estimands**:
   $R_{HP}$ and $\hat{R}_{KO}$ in the sensitivity script estimated **two completely different statistical quantities**:
   - $R_{HP}$ measured **High-Pressure Performance Above Tactical Role Expectation** (deliveries with $PI \ge 0.800$, centered at $\mu_{\text{role}}$).
   - $\hat{R}_{KO}$ measured **Unadjusted Total Delivery Value in Knockout Matches** (averaged across all knockout deliveries, without role adjustment, centered at the player's own $R_{HP}$).
2. **Prior and Likelihood Scaling Flaws**:
   - The sample mean $\bar{y}_{KO}$ was raw runs per ball, multiplied by 100 to yield runs per 100 balls.
   - For Abhishek Sharma, facing 23 balls in IPL playoffs with early dismissals yielded $\bar{y}_{KO} = -2.920$ runs/ball $\implies \mathbf{-292.00}$ runs/100 balls!
   - Because the variance component $\sigma_{\mu, KO}^2 = 0.1168$ was estimated on noisy small samples, the shrinkage factor was under-regularized ($\lambda_{KO} = 0.2541$).
   - Consequently, Abhishek Sharma's $\hat{R}_{KO}$ collapsed to:
     $$\hat{R}_{KO} = 0.2541 \times (-292.00) + (1 - 0.2541) \times (+29.38) = \mathbf{-52.28}\text{ runs/100b}$$
   - For Vaibhav Sooryavanshi, scoring heavily in 79 knockout balls ($\bar{y}_{KO} = +1.3875$ runs/ball $\implies +138.75$ r/100b), his rating surged to:
     $$\hat{R}_{KO} = 0.5392 \times (+138.75) + (1 - 0.5392) \times (+38.66) = \mathbf{+92.63}\text{ runs/100b}$$
3. **Audit Verdict**:
   The two ratings are **dimensionally and conceptually non-comparable**. Blending them into a composite score $R_{\text{final}} = (1 - w_K) R_{HP} + w_K \hat{R}_{KO}$ is mathematically invalid and must not be used.

---

## 1. Trace of the Calculations Producing +92.63 and -52.28

We trace the exact lines executed in the sensitivity script:

### Step 1: Delivery Value Extraction
For player $i$, delivery values $v_{\text{bat}}$ were extracted from `step2/deliveries_with_ev.csv.gz`.
- For **Abhishek Sharma**: Across all 4 years, he participated in IPL playoffs (Qualifiers, Eliminators, Finals) totaling **$n_{KO} = 23$ balls**.
  Sum of delivery values: $\sum v = -67.159$ runs.
  Sample mean: $\bar{y}_{KO} = \frac{-67.159}{23} = \mathbf{-2.91997}\text{ runs/ball}$.
- For **Vaibhav Sooryavanshi**: He faced **$n_{KO} = 79$ balls** in knockout matches.
  Sum of delivery values: $\sum v = +109.612$ runs.
  Sample mean: $\bar{y}_{KO} = \frac{+109.612}{79} = \mathbf{+1.38749}\text{ runs/ball}$.

### Step 2: Variance Component Estimation
Variance components were naively estimated across players with $n_{KO} \ge 20$:
- Residual variance: $\sigma_{e, KO}^2 = 7.8857$
- Between-player variance: $\sigma_{\mu, KO}^2 = 0.1168$

### Step 3: Shrinkage Calculation
Shrinkage factor $\lambda_{KO, i} = \frac{n_{KO, i} \sigma_{\mu, KO}^2}{n_{KO, i} \sigma_{\mu, KO}^2 + \sigma_{e, KO}^2}$:
- For Abhishek Sharma ($n = 23$):
  $$\lambda_{KO} = \frac{23 \times 0.1168}{23 \times 0.1168 + 7.8857} = \frac{2.6864}{2.6864 + 7.8857} = \mathbf{0.25410}$$
- For Vaibhav Sooryavanshi ($n = 79$):
  $$\lambda_{KO} = \frac{79 \times 0.1168}{79 \times 0.1168 + 7.8857} = \frac{9.2272}{9.2272 + 7.8857} = \mathbf{0.53920}$$

### Step 4: Shrunken Rating Calculation
The script attempted to shrink $\bar{y}_{KO}$ toward the player's primary rating $R_{HP}$:
$$\hat{R}_{KO, i} = \lambda_{KO, i} \cdot (\bar{y}_{KO, i} \times 100) + (1 - \lambda_{KO, i}) \cdot R_{HP, i}$$
- **For Abhishek Sharma**:
  $$\hat{R}_{KO} = 0.2541 \times (-291.997) + (1 - 0.2541) \times (+29.381)$$
  $$\hat{R}_{KO} = -74.196 + 21.915 = \mathbf{-52.2816}\text{ runs/100b}$$
- **For Vaibhav Sooryavanshi**:
  $$\hat{R}_{KO} = 0.5392 \times (+138.749) + (1 - 0.5392) \times (+38.660)$$
  $$\hat{R}_{KO} = +74.814 + 17.814 = \mathbf{+92.6278}\text{ runs/100b}$$

---

## 2. Seven Flaws in the Sensitivity Formulation

| Audit Dimension | Primary Rating ($R_{HP}$) | Sensitivity Knockout Rating ($\hat{R}_{KO}$) | Incompatibility Verdict |
|---|---|---|---|
| **1. Pressure Condition** | Strictly high pressure ($PI \ge 0.800$) | All knockout balls (including $PI < 0.10$) | **INCOMPATIBLE** |
| **2. Tactical Role Adjustment** | Centered at role baseline ($\mu_{\text{role}}$) | Raw unadjusted delivery value | **INCOMPATIBLE** |
| **3. Baseline Reference** | Role replacement level | Shrunk toward player's own $R_{HP}$ | **INCOMPATIBLE** |
| **4. Variance Scale** | $\sigma_\mu^2 = 0.0349$ (SD = $18.68$) | $\sigma_\mu^2 = 0.1168$ (SD = $34.18$) | **INCOMPATIBLE** |
| **5. Extreme Value Scaling** | Scaled across 37,639 balls | Extreme $-292$ / $+139$ runs/100b | **INCOMPATIBLE** |
| **6. Sample Truncation** | Minimum $n_{HP} \ge 50$ balls required | Evaluated on as few as $n = 1$ ball | **INCOMPATIBLE** |
| **7. Cross-Player Comparability** | Directly comparable across all players | Undefined for 60% of players ($n=0$) | **INCOMPATIBLE** |

### Detailed Flaw Explanations:
1. **Flaw 1 (Conflating All-Knockout with High-Pressure)**:
   $\bar{y}_{KO}$ included deliveries in the 1st innings powerplay of playoff games where $PI \approx 0.15$. These are low-pressure deliveries. $R_{HP}$ excludes them.
2. **Flaw 2 (Absence of Role Adjustment)**:
   In $R_{HP}$, open powerplay overs and death overs are adjusted against role averages. In $\bar{y}_{KO}$, a top-order batter dismissed for 0 off 3 balls is charged $-292$ runs/100b without adjusting for the natural risk profile of an opening batter.
3. **Flaw 3 (Circular Shrinkage Target)**:
   Shrinking $\bar{y}_{KO}$ toward $R_{HP}$ implicitly assumes that $R_{HP}$ is the prior distribution for knockout play. But $R_{HP}$ was already estimated from data that included high-pressure knockout deliveries!
4. **Flaw 4 (Runaway Variance Inflation)**:
   Because $\sigma_{\mu, KO}^2$ was estimated on small samples of players, between-player variance was inflated by $3.3\times$. This allowed a 23-ball sample to pull Abhishek Sharma's score downward by **$-81.66$ rating points**!

---

## 3. Conclusion and Final Rule on Blending

1. **Ratings Cannot Be Blended**:
   $R_{HP}$ and $\hat{R}_{KO}$ as computed in the sensitivity analysis do not share the same estimand, the same baseline, or the same variance scale. Blending them into a linear composite:
   $$R_{\text{final}} = (1 - w_K) R_{HP} + w_K \hat{R}_{KO}$$
   is **statistically indefensible**.
2. **Proper Formulation Required**:
   If knockout performance is to be recognized, it must either:
   - Be reported as a separate descriptive statistic on its own independent scale (Option A), or
   - Be derived from a formally unified, mutually exclusive delivery partitioning where both components share identical role adjustments and variance scaling (Option B/C).

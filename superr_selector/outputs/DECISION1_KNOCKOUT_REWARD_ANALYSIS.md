# Decision 1 Analysis: How Should Knockout Performance Be Rewarded?

**Project:** SupeRR Selector Season 2  
**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Context:** Targeted Methodology Decision Review  
**Supporting Dataset:** `KNOCKOUT_WEIGHT_SENSITIVITY.csv`

---

## Executive Summary

This investigation evaluates how tournament knockout performances (IPL playoffs, T20 World Cup finals/semi-finals, Asia Cup finals) should be incorporated into the SupeRR Selector rating architecture.

### Key Empirical Findings:
1. **Severe Knockout Sample Scarcity**: Across the entire 4-year senior dataset (2022–2025, 802 matches), only **25 matches** (3.12%) are knockouts (20 IPL playoffs, 5 T20I finals/semi-finals), encompassing **5,763 deliveries** (3.05% of all deliveries).
2. **Extreme Player Exposure Skew**: 
   - **69 of 114 eligible batters (60.5%)** and **93 of 124 eligible bowlers (75.0%)** have **zero knockout deliveries**.
   - Median knockout exposure among all eligible players is **9.5 deliveries**. Only 10 batters and 10 bowlers have faced/bowled $\ge 100$ knockout deliveries.
   - For high-pressure knockout deliveries ($PI \ge 0.800$ in knockouts), the total data volume across 4 years is **just 1,158 deliveries** (0.61% of all balls). Over 85% of eligible players have zero high-pressure knockout balls.
3. **Double-Counting Overlap**: Deliveries in knockout matches already receive elevated match-state leverage ($L = |\partial \text{WP} / \partial v|$) because winning probability swings are naturally sharper in elimination games. Applying an additional explicit knockout score multiplier or weight double-counts the same deliveries.
4. **Instability of Option B (Weighted Combination)**:
   - For weights $w_K \ge 0.10$, players with tiny knockout exposures experience wild rank distortions. For example, **Abhishek Sharma** (Rank #3, $+29.38$, $n_{HP} = 560$) drops to **Rank #18 at $w_K = 0.20$ and Rank #30 at $w_K = 0.25$** simply because he happened to have 23 cheap dismissals in IPL playoffs across 4 years.
   - Conversely, half of the top 10 bowlers (Sikandar Raza, Mayank Yadav, Wayne Parnell, Mehidy Hasan Miraz, Harry Tector) have **0 knockout deliveries** because their national teams (Zimbabwe, Ireland, Bangladesh) or IPL franchises did not qualify for finals.
5. **Definitive Recommendation**: **Option A (Separate Knockout Dimension / Dual-Leaderboard)** is the only statistically defensible methodology. Option B is mathematically rejected due to severe sample sparsity and franchise qualification bias. Option C is conditionally acceptable only as a descriptive hierarchical shrinkage model.

---

## 1. Architectural Comparison of the Three Alternatives

```
+---------------------------------------------------------------------------------------------------------+
|                                    THREE KNOCKOUT ARCHITECTURES                                         |
+---------------------+-----------------------------------+-----------------------------------------------+
| Option              | Mathematical Formulation          | Primary Mechanism                             |
+---------------------+-----------------------------------+-----------------------------------------------+
| Option A            | R_primary = R_HP                  | Primary score measures all high-pressure balls; |
| (Separate Dimension)| Secondary: (n_KO, R_KO)           | knockout performance presented as separate    |
|                     |                                   | leaderboard and qualification filter.         |
+---------------------+-----------------------------------+-----------------------------------------------+
| Option B            | R_final = (1 - wK) * R_base       | Linear combination of non-knockout base and   |
| (Weighted Score)    |         + wK * R_KO               | shrunken knockout score with global weight wK.|
+---------------------+-----------------------------------+-----------------------------------------------+
| Option C            | y_imk = mu + alpha_i + beta_i*PI  | Multi-level hierarchical model partially      |
| (Hierarchical Pool) |       + delta_i * I(KO) + e_imk   | pooling knockout effect toward player base.   |
+---------------------+-----------------------------------+-----------------------------------------------+
```

---

## 2. Detailed Technical Audit of Each Alternative

### Alternative A: Separate Knockout Dimension (Recommended)

- **Exact Estimand**:
  - Primary Estimand: High-Pressure Expected Run Value ($R_{HP}$) evaluated across all senior matches (league and knockout).
  - Secondary Descriptive Metric: Knockout Volume ($n_{KO}$) and Knockout Expected Run Value ($R_{KO}$), shrunk toward the player's role baseline.
- **Data Requirement**: Supported by 100% of the dataset.
- **Mathematical Treatment of Overlap**:
  - High-pressure deliveries in knockout matches are naturally included in $R_{HP}$ and receive their true, data-driven leverage weighting.
  - Zero double-counting occurs because no secondary multiplier is applied to the primary score.
- **Handling of Players with No Knockout Exposure**:
  - Players from non-qualifying teams (e.g., Sikandar Raza, Harry Tector) are not penalized for lack of playoff opportunities. Their rating reflects their proven performance in the 802-match pool.
  - In reporting, they are cleanly designated: `Knockout Exposure: 0 balls (N/A)`.

### Alternative B: Weighted Knockout Contribution ($R_{\text{final}} = (1 - w_K) R_{\text{base}} + w_K R_{KO}$)

- **Exact Estimand**:
  A composite index blending general high-pressure performance with knockout performance:
  $$R_{\text{final}, i} = (1 - w_K) R_{\text{base}, i} + w_K \hat{R}_{KO, i}$$
  where $\hat{R}_{KO, i} = \lambda_{KO, i} \bar{y}_{KO, i} + (1 - \lambda_{KO, i}) R_{\text{base}, i}$.
- **Data-Driven Weight Investigation**:
  To avoid an arbitrary weight (such as $0.25$ or $0.30$), we investigated data-supported ways to determine $w_K$:
  1. *Delivery Volume Fraction*: In the 802-match senior dataset, knockout deliveries are 5,763 of 188,761 total deliveries:
     $$w_K^{\text{volume}} = \frac{5,763}{188,761} = \mathbf{0.0305 \ (3.05\%)}$$
  2. *High-Pressure Volume Fraction*: High-pressure knockout deliveries are 1,158 of 37,639 total HP deliveries:
     $$w_K^{\text{HP-volume}} = \frac{1,158}{37,639} = \mathbf{0.0308 \ (3.08\%)}$$
  3. *Information Ratio (Signal-to-Noise)*: Between-player variance in knockouts ($\sigma_{\mu, KO}^2 = 0.1168$) relative to total observation noise ($\sigma_{e, KO}^2 = 7.8857$) indicates that for the median player with 9.5 balls, knockout reliability is:
     $$\lambda_{KO} = \frac{9.5 \times 0.1168}{9.5 \times 0.1168 + 7.8857} = \mathbf{0.123}$$
- **Sensitivity Across Weights ($w_K \in [0.03, 0.25]$)**:
  *Extracted from `KNOCKOUT_WEIGHT_SENSITIVITY.csv`*:

| Player Name | Role | Total HP ($n$) | KO Balls ($n$) | Baseline Rank ($w_K = 0$) | Rank at $w_K = 0.03$ | Rank at $w_K = 0.10$ | Rank at $w_K = 0.20$ | Rank at $w_K = 0.25$ |
|---|---|---|---|---|---|---|---|---|
| **Vaibhav Sooryavanshi** | Batter | 190 | 79 | 1 | 1 | 1 | 1 | 1 |
| **Suryakumar Yadav** | Batter | 598 | 110 | 2 | 2 | 2 | 2 | 2 |
| **Abhishek Sharma** | Batter | 560 | 23 | **3** | **3** | **5** | **18** | **30** |
| **Yashasvi Jaiswal** | Batter | 604 | 120 | 4 | 4 | 4 | 7 | 9 |
| **Pathum Nissanka** | Batter | 619 | 19 | 5 | 6 | 7 | 11 | 12 |
| **Phil Salt** | Batter | 494 | 37 | 6 | 5 | 3 | 3 | 3 |
| **Ryan Rickelton** | Batter | 283 | 0 | 7 | 7 | 6 | 6 | 6 |
| **Virat Kohli** | Batter | 584 | 173 | 8 | 8 | 9 | 8 | 8 |
| **Reece Topley** | Bowler | 117 | 18 | 1 | 1 | 1 | 1 | 2 |
| **Tim Southee** | Bowler | 223 | 25 | 2 | 2 | 2 | 2 | 1 |
| **Rashid Khan** | Bowler | 490 | 199 | **3** | **3** | **3** | **5** | **7** |
| **Mayank Yadav** | Bowler | 86 | 0 | 4 | 4 | 4 | 4 | 5 |
| **Sikandar Raza** | Bowler | 267 | 0 | 5 | 5 | 5 | 6 | 6 |

- **Why Option B Fails**:
  - At data-supported weights ($w_K \approx 0.03$), the rank correlation with baseline is **$0.9990$**, meaning the knockout component is virtually inert.
  - At arbitrary higher weights ($w_K \ge 0.15$), the score becomes heavily contaminated by tiny-sample playoff noise (e.g., Abhishek Sharma dropping 27 rank positions based on just 23 deliveries).

---

### Alternative C: Hierarchical Knockout Interaction

- **Exact Estimand**:
  A three-level Bayesian mixed-effects model:
  $$y_{imk} = \mu_{\text{role}} + \alpha_i + \beta_i \cdot PI_{imk} + \delta_i \cdot \mathbb{I}(\text{Knockout}_m) + \epsilon_{imk}$$
  where:
  $$\alpha_i \sim \mathcal{N}(0, \sigma_\alpha^2), \quad \beta_i \sim \mathcal{N}(0, \sigma_\beta^2), \quad \delta_i \sim \mathcal{N}(0, \sigma_\delta^2)$$
  The knockout effect $\delta_i$ is partially pooled toward zero (or the player's overall talent $\alpha_i$).
- **Statistical Evaluation**:
  - *Theoretical Appeal*: Eliminates arbitrary weights by allowing the data likelihood to determine how much information knockout games provide.
  - *Empirical Limitation in 802 Matches*: Because only 25 matches are knockouts, the design matrix for $\delta_i$ has zero observations for 60% of batters and 75% of bowlers.
  - In Markov Chain Monte Carlo (MCMC) hierarchical fitting, the posterior variance of $\delta_i$ for unobserved players collapses entirely to the prior variance $\sigma_\delta^2$. The player's point estimate receives $\hat{\delta}_i \approx 0$, which is mathematically equivalent to Option A.

---

## 3. Overlap and Double-Counting Audit

Consider a tense death-over delivery in an IPL Final (e.g. 12 runs required off 6 balls):
1. **In the Win-Probability Model**:
   The required run rate ($RRR = 12.0$) and remaining balls ($u = 6$) generate an extreme win-probability gradient:
   $$L_k = \left| \frac{\partial \text{WP}}{\partial v} \right| \approx 0.185 \implies PI_k = 0.992 \quad (\text{Top 1\% highest pressure})$$
2. **In Delivery Value Attribution**:
   The run value $v_k$ is multiplied by this elevated leverage. The player is already credited with a massive leverage-weighted contribution.
3. **If Option B is Implemented**:
   That exact same delivery is included in $R_{\text{base}}$ *and* included again in $R_{KO}$, and then blended via $w_K$.
   **This counts the same delivery twice.**

In Option A, the delivery is counted once at its true physical leverage.

---

## 4. Synthesis and Recommendation for Decision 1

| Dimension | Option A: Separate Dimension | Option B: Weighted Score | Option C: Hierarchical Model |
|---|---|---|---|
| **Mathematical Soundness** | **VALIDATED** | **NOT VALIDATED** (Double-counts) | **CONDITIONALLY ACCEPTABLE** |
| **Sample Size Support** | Supported across all 802 matches | Fails for 60–75% of players ($n=0$) | Collapses to Option A for $n=0$ |
| **Sensitivity to Outliers** | Robust and stable | Highly volatile for $w_K \ge 0.10$ | Moderately volatile |
| **Treatment of Non-Playoff Stars** | Fair (no penalty for team failure) | Penalizes stars on weaker teams | Requires subjective hyperpriors |
| **Cricket Interpretability** | Clear dual-leaderboard format | Opaque composite score | Complex posterior distribution |

### Recommendation:
**ADOPT OPTION A (Separate Knockout Dimension).**  
Retain $R_{HP}$ as the primary scalar rating across all senior matches. Present Knockout Performance ($n_{KO}$, $R_{KO}$) as a dedicated secondary leaderboard and filter. Reject Option B to protect against sample scarcity and double-counting.

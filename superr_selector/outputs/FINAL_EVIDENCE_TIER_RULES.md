# Final Evidence Tier Classification: Reproducible Assignment Rules

**Project:** SupeRR Selector Season 2  
**Document:** `FINAL_EVIDENCE_TIER_RULES.md`  
**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Status:** Frozen Operational Rules for Evidence Stratification  

---

## Executive Summary

To prevent misleading decision-makers by presenting low-exposure breakout players identically to multi-season stalwarts, all players meeting the floor eligibility threshold ($n_{HP} \ge 50$ balls and $m_{HP} \ge 5$ matches) are classified into three precise, reproducible **Evidence Tiers**.

These tiers explicitly distinguish **score stability under match resampling** from **statistical evidence of positive latent ability**.

---

## 1. Exact Reproducible Assignment Rules

```
                             [All Players with n_HP >= 50 and m_HP >= 5]
                                                  │
                 ┌────────────────────────────────┴────────────────────────────────┐
                 │                                                                 │
    [Does player meet ALL of:]                                                     │
    1. n_HP >= 150 balls                                                           │
    2. m_HP >= 15 matches                                                          │
    3. P(theta > 0) >= 0.95                                                        │
    4. Rank Interval Width <= 30 positions                                         │
                 │                                                                 │
               YES                                                                 NO
                 │                                                                 │
                 ▼                                                                 ▼
      [TIER 1: SUSTAINED CORE]                                       [Does player meet ALL of:]
                                                                     1. n_HP >= 75 balls
                                                                     2. m_HP >= 8 matches
                                                                     3. P(theta > 0) >= 0.85
                                                                     4. Rank Interval Width <= 55
                                                                                   │
                                                                   ┌───────────────┴───────────────┐
                                                                   │                               │
                                                                  YES                              NO
                                                                   │                               │
                                                                   ▼                               ▼
                                                        [TIER 2: CONTENDER]              [TIER 3: EXPLORATORY]
```

---

## 2. Formal Specification of Evidence Tiers

### Table 1: Mathematical Specification of Evidence Tiers

| Evidence Tier | Minimum Exposure ($n_{HP}$) | Minimum Matches ($m_{HP}$) | Latent Talent Probability $P(\theta_i > 0)$ | 90% Rank Interval Width ($W_{\text{rank}}$) | Core Statistical Meaning |
|:---|:---:|:---:|:---:|:---:|:---|
| **Tier 1: Sustained Core Performers** | $\ge \mathbf{150}$ balls | $\ge \mathbf{15}$ matches | $\ge \mathbf{0.95}$ ($95\%$) | $\le \mathbf{30}$ positions | **Both High Score Stability AND Overwhelming Evidence of Positive Latent Ability.** Multi-season proven performers. |
| **Tier 2: Moderate-Exposure Contenders** | $\ge \mathbf{75}$ balls | $\ge \mathbf{8}$ matches | $\ge \mathbf{0.85}$ ($85\%$) | $\le \mathbf{55}$ positions | **Strong Evidence of Positive Ability, but Moderate Score Stability.** Solid starters with moderate rank variance. |
| **Tier 3: Low-Exposure Exploratory Shortlist** | $\ge \mathbf{50}$ balls | $\ge \mathbf{5}$ matches | *Any* | $> \mathbf{55}$ positions (or wide interval) | **Exploratory High-Rate Potential, but Low Score Stability.** Breakout talents whose rank spans $> 50$ positions. |
| *Ineligible* | $< 50$ balls | $< 5$ matches | — | — | Insufficient sample size for ranking. |

---

## 3. Mathematical Definitions of Assignment Variables

1. **High-Pressure Exposure ($n_{HP, i}$):**
   Exact count of legal deliveries bowled (bowlers) or balls faced (batters) with match leverage percentile $PI_{ik} \ge 0.800$.
2. **High-Pressure Match Count ($m_{HP, i}$):**
   Number of distinct senior matches in which player $i$ bowled or faced at least one delivery with $PI \ge 0.800$.
3. **Posterior Probability of Outperformance ($P(\theta_i > 0 \mid \text{data})$):**
   Under the Gaussian empirical Bayes prior and likelihood:
   $$P(\theta_i > 0 \mid \text{data}) = \Phi\left( \frac{R_{HP, i}}{\text{SE}_{\text{post}, i}} \right)$$
   where $\Phi(\cdot)$ is the standard normal cumulative distribution function and $\text{SE}_{\text{post}, i} = \sqrt{1 - \lambda_i} \cdot (\sigma_\mu \times 100)$.
4. **90% Rank Interval Width ($W_{\text{rank}, i}$):**
   Derived from the $B = 1,000$ Procedure A Match-Cluster Bootstrap replicates:
   $$W_{\text{rank}, i} = \text{Rank}_{95\text{th}, i} - \text{Rank}_{5\text{th}, i} + 1$$
   A width of 15 means the player's simulated rank varied by at most 15 positions across 90% of schedule resamples.

---

## 4. Illustrative Benchmark Classifications

- **Suryakumar Yadav (Batter):**
  - $n_{HP} = 598$ balls, $m_{HP} = 48$ matches, $R_{HP} = +30.47$, $P(\theta > 0) > 0.999$, Rank CI: $[1, 5]$ ($W = 5$).
  - **Tier Assignment:** **Tier 1 (Sustained Core Performer)**. Overwhelming stability and latent talent.
- **Rashid Khan (Bowler):**
  - $n_{HP} = 490$ balls, $m_{HP} = 44$ matches, $R_{HP} = +18.28$, $P(\theta > 0) > 0.999$, Rank CI: $[1, 8]$ ($W = 8$).
  - **Tier Assignment:** **Tier 1 (Sustained Core Performer)**. Highly robust multi-season pillar.
- **Vaibhav Sooryavanshi (Batter):**
  - $n_{HP} = 190$ balls, $m_{HP} = 16$ matches, $R_{HP} = +38.66$, $P(\theta > 0) = 0.991$, Rank CI: $[1, 31]$ ($W = 31$).
  - **Tier Assignment:** **Tier 2 (Moderate-Exposure Contender)**. Outstanding point estimate, but rank interval width exceeds 30 due to high boundary-variance volatility.
- **Mayank Yadav (Bowler):**
  - $n_{HP} = 86$ balls, $m_{HP} = 7$ matches, $R_{HP} = +17.47$, $P(\theta > 0) = 0.912$, Rank CI: $[2, 48]$ ($W = 47$).
  - **Tier Assignment:** **Tier 3 (Low-Exposure Exploratory Shortlist)**. Fails the $m_{HP} \ge 8$ match threshold for Tier 2; rank spans 47 positions. Must be presented as an exploratory pick.

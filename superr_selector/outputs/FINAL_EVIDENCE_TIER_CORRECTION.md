# Final Evidence Tier Correction: Exhaustive & Mutually Exclusive Assignment

**Project:** SupeRR Selector Season 2  
**Document:** `FINAL_EVIDENCE_TIER_CORRECTION.md`  
**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Status:** Operational Rules Update & Population Verification  
**Companion Dataset:** [`FINAL_TIER_ASSIGNMENT_VALIDATION.csv`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/FINAL_TIER_ASSIGNMENT_VALIDATION.csv)

---

## Executive Summary

This document resolves the classification gap identified in earlier drafts of the evidence-tier framework, where players with high exposure ($n_{HP} \ge 150$) and narrow rank intervals ($W_{\text{rank}} \le 30$) who narrowly missed the $95\%$ posterior probability threshold were left unclassified between Tier 1 and Tier 2.

We implement a **strict deterministic order of evaluation** that guarantees:
1. Every floor-eligible player ($N = 358$: 168 batters, 190 bowlers) receives **exactly one** evidence tier.
2. No player receives multiple tiers.
3. The sum of tier assignments identically equals the eligible population.
4. Model-based posterior probabilities are properly treated as heuristic shrinkage diagnostics, not definitive physical proof.

---

## 1. Deterministic Tier Assignment Rules

For every player meeting Floor Eligibility ($n_{HP} \ge 50$ high-pressure deliveries and $m_{HP} \ge 5$ distinct high-pressure matches), tiers are assigned in the following strict procedural order:

```
[START: Floor-Eligible Player (n_HP >= 50, m_HP >= 5)]
                       │
                       ▼
        [STEP 1: EVALUATE TIER 1 (SUSTAINED CORE)]
        Does the player satisfy ALL 4 criteria?
        1. n_HP >= 150 balls
        2. m_HP >= 15 matches
        3. Model Evidence: P(theta > 0) >= 0.95 (95%)
        4. Score Stability: 90% Rank Interval Width W_rank <= 30
                       │
             ┌─────────┴─────────┐
             │                   │
           YES                   NO
             │                   │
             ▼                   ▼
     [ASSIGN TIER 1]   [STEP 2: EVALUATE TIER 2 (CONTENDER)]
                       Does the player satisfy ALL 4 criteria?
                       1. n_HP >= 75 balls
                       2. m_HP >= 8 matches
                       3. Model Evidence: P(theta > 0) >= 0.85 (85%)
                       4. Score Stability: 90% Rank Interval Width W_rank <= 55
                                 │
                       ┌─────────┴─────────┐
                       │                   │
                     YES                   NO
                       │                   │
                       ▼                   ▼
               [ASSIGN TIER 2]     [STEP 3: ASSIGN TIER 3]
                                   [RESIDUAL EXPLORATORY CATEGORY]
```

### Complete Resolution of the Classification Gap:
In the previous draft, Tier 2 included an exposure upper bound ($75 \le n < 150$) that inadvertently orphaned players with $n \ge 150$ who failed Tier 1 solely on $P(\theta > 0)$.
Under the corrected waterfall hierarchy:
- If a player has $n_{HP} = 200, m_{HP} = 20, P(\theta > 0) = 0.92, W_{\text{rank}} = 25$:
  - **Step 1:** Fails Tier 1 because $P(\theta > 0) = 0.92 < 0.95$.
  - **Step 2:** Evaluates Tier 2: $n \ge 75$ (True), $m \ge 8$ (True), $P \ge 0.85$ (True), $W_{\text{rank}} \le 55$ (True).
  - **Result:** Player is cleanly, deterministically assigned to **Tier 2 (Contender)**.

---

## 2. Empirical Verification Across All Eligible Players

The deterministic logic was executed against all 358 floor-eligible players in [`FINAL_REPAIRED_BATTER_RANKINGS.csv`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/FINAL_REPAIRED_BATTER_RANKINGS.csv) and [`FINAL_REPAIRED_BOWLER_RANKINGS.csv`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/FINAL_REPAIRED_BOWLER_RANKINGS.csv).

### Table 1: Population Tier Census

| Discipline | Tier 1: Sustained Core | Tier 2: Contenders | Tier 3: Exploratory Shortlist | Total Eligible Players |
|:---|:---:|:---:|:---:|:---:|
| **Batters** | 4 | 7 | 157 | **168** |
| **Bowlers** | 0 | 3 | 187 | **190** |
| **Total** | **4** | **10** | **344** | **358** |
| *Exhaustive Verification* | *Sum = 4* | *Sum = 10* | *Sum = 344* | *Sum = 358 (100.0% Matched)* |

Every player in the database has an explicit classification recorded in [`FINAL_TIER_ASSIGNMENT_VALIDATION.csv`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/FINAL_TIER_ASSIGNMENT_VALIDATION.csv). Zero players are unclassified.

---

## 3. Detailed Audit of Tier Assignments

### 3.1 The 4 Tier-1 Batters (Sustained Core Stalwarts)
1. **Vaibhav Sooryavanshi:** $n_{HP} = 190, m_{HP} = 19, R_{HP} = +38.66, P(\theta > 0) = 0.9999, W_{\text{rank}} = 27$ $\implies$ **Tier 1**.
2. **Suryakumar Yadav:** $n_{HP} = 598, m_{HP} = 55, R_{HP} = +30.47, P(\theta > 0) = 0.9998, W_{\text{rank}} = 23$ $\implies$ **Tier 1**.
3. **Yashasvi Jaiswal:** $n_{HP} = 604, m_{HP} = 82, R_{HP} = +25.63, P(\theta > 0) = 0.9988, W_{\text{rank}} = 28$ $\implies$ **Tier 1**.
4. **Pathum Nissanka:** $n_{HP} = 619, m_{HP} = 72, R_{HP} = +22.42, P(\theta > 0) = 0.9963, W_{\text{rank}} = 23$ $\implies$ **Tier 1**.

### 3.2 The 7 Tier-2 Batters (High-Impact Contenders)
- **Abhishek Sharma:** $n_{HP} = 560, m_{HP} = 85, R_{HP} = +29.38, P = 0.9997, W_{\text{rank}} = 40$ $\implies$ **Tier 2** (Rank CI: $[1, 40]$ exceeds $W=30$).
- **Phil Salt:** $n_{HP} = 494, m_{HP} = 70, R_{HP} = +21.35, P = 0.9927, W_{\text{rank}} = 55$ $\implies$ **Tier 2** (Rank CI: $[3, 57]$).
- **Ryan Rickelton:** $n_{HP} = 283, m_{HP} = 33, R_{HP} = +20.80, P = 0.9873, W_{\text{rank}} = 54$ $\implies$ **Tier 2**.
- **Virat Kohli:** $n_{HP} = 584, m_{HP} = 60, R_{HP} = +19.73, P = 0.9900, W_{\text{rank}} = 46$ $\implies$ **Tier 2**.
- **Daryl Mitchell:** $n_{HP} = 183, m_{HP} = 22, R_{HP} = +18.79, P = 0.9788, W_{\text{rank}} = 46$ $\implies$ **Tier 2**.
- **Tilak Varma:** $n_{HP} = 371, m_{HP} = 43, R_{HP} = +16.71, P = 0.9745, W_{\text{rank}} = 48$ $\implies$ **Tier 2**.
- **Shimron Hetmyer:** $n_{HP} = 247, m_{HP} = 42, R_{HP} = +16.14, P = 0.9632, W_{\text{rank}} = 52$ $\implies$ **Tier 2**.

---

### 3.3 Explanation of Bowler Tier Distribution: Why 0 Bowlers Qualify for Tier 1
In the bowler population, **0 bowlers meet the Tier 1 criteria**, while 3 qualify for Tier 2 (**Rashid Khan**, **Harry Tector**, and **Axar Patel**), with the remainder in Tier 3.

**The Statistical Reason (Talent Compression & Rank Density):**
1. **Narrower Between-Player Variance:**
   The estimated talent variance among bowlers is $\sigma_\mu^2 = 0.0195$ ($SD = 13.96$ runs/100b), compared to $\sigma_\mu^2 = 0.0349$ ($SD = 18.68$ runs/100b) for batters.
2. **Dense Leaderboard Compression:**
   The entire top 10 bowlers are compressed within a narrow 6.6-run band ($+20.65$ to $+14.05$).
3. **High Schedule Sensitivity in Ranks:**
   Under match-cluster resampling (Procedure A), a minor shift of $\pm 4$ runs/100b in a bowler's rating moves their rank across 40–80 positions.
   - For example, **Rashid Khan** has massive exposure ($n_{HP} = 490$ balls, $m_{HP} = 44$ matches, $R_{HP} = +18.28$, $P(\theta > 0) > 0.999$).
   - However, his 90% bootstrap rank interval is $[1, 43]$ ($W_{\text{rank}} = 43$). Because $43 > 30$, he is assigned to **Tier 2**.
   - Similarly, **Reece Topley** (Rank #1, $+20.65$) has Rank CI $[1, 67]$ ($W = 67 > 55$), placing him in **Tier 3 (Exploratory)** due to his limited 117-ball sample.
- **Methodological Rule:** We **do not** artificially relax the $W_{\text{rank}} \le 30$ threshold for bowlers. The fact that bowler ranks have higher schedule sensitivity is an empirical reality of cricket data that decision-makers must see.

---

## 4. Retained Uncertainty Caveats for Reviewers

1. **Model-Based Probability, Not Physical Proof:**
   The metric $P(\theta_i > 0 \mid \text{data})$ is derived from the conjugate Gaussian empirical Bayes formulation:
   $$P(\theta_i > 0 \mid \text{data}) = \Phi\left( \frac{R_{HP, i}}{\text{SE}_{\text{analytical}, i}} \right)$$
   This represents **model-based evidence under assumed prior exchangeability**. It is not a model-free proof of latent ability.
2. **Extreme Performer Undercoverage:**
   As documented in `FINAL_UNCERTAINTY_SIGNOFF.md`, empirical coverage for extreme talents is $\approx 70\% - 75\%$ due to shrinkage bias. Posterior probabilities must be interpreted alongside exposure ($n_{HP}$) and bootstrap rank width ($W_{\text{rank}}$).

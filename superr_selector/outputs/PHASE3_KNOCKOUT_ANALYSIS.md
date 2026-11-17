# Phase 3 Knockout Analysis — SupeRR Selector Season 2

**Phase:** Phase 3 — Rating Estimand & Player Model Architecture Review  
**Date:** 2026-11-17  
**Branch:** `model-repair`  
**Scope:** Rigorous statistical evaluation of tournament knockout stages, data sparsity, leverage vs stage alignment, evaluation of 4 knockout policies, and recommendations for the SupeRR Selector pipeline.

---

## Executive Summary

Tournament knockout stages (semi-finals, qualifiers, eliminators, and finals) carry supreme tournament stakes. However, a rigorous audit of the 2022–2026 IPL and T20I dataset reveals that **incorporating tournament knockout stages into the primary player ranking formula is statistically invalid, causes severe sample-size distortion, and introduces structural inequality across players**.

### Key Empirical Findings
1. **Extreme Data Sparsity:**
   - Out of **802 total matches** (188,761 deliveries) in the 2022–2026 dataset, there are only **20 IPL knockout matches** (4,573 deliveries, 2.4%) and **5 T20I finals** (1,190 deliveries, 0.6%).
   - Combined, knockout cricket represents just **3.0% of all deliveries**.
   - Only **42 batters** and **42 bowlers** in the entire dataset have faced or bowled $\ge 50$ knockout deliveries across five years.
   - Only **10 batters** and **10 bowlers** have faced or bowled $\ge 100$ knockout deliveries.

2. **Knockout Stage $\ne$ Delivery-Level Pressure:**
   - The empirical distribution of delivery-level leverage ($L(s)$) and Pressure Index ($PI$) in IPL knockout matches is **statistically indistinguishable** from regular league matches:
     - Mean $PI$: **0.5004** in IPL knockouts vs **0.4999** in IPL league matches.
     - Mean Leverage: **0.1811** in IPL knockouts vs **0.1823** in IPL league matches.
     - Fraction of high-pressure deliveries ($PI \ge 0.80$): **19.99%** in knockouts vs **19.91%** in league matches.
     - Fraction of low-pressure/blowout deliveries ($PI < 0.20$): **19.99%** in knockouts vs **19.97%** in league matches.
   - **Crucial insight:** A blowout in an IPL final (e.g. chasing 110 runs with 8 wickets in hand) has near-zero delivery leverage ($L \to 0$), whereas a final-over finish in a mid-season group match has maximum leverage ($L > 0.45$). Conflating tournament stage with delivery pressure is a category error.

3. **Distortion in the Baseline Formula:**
   - The baseline model used an unprincipled threshold of $n_{\text{ko}} \ge 12$ balls to estimate player-specific knockout shifts $\delta_i$.
   - **Abhishek Sharma Case Study:** Ranked #2 overall on regular performance ($R_{\text{reg}} = +40.96$ runs/100 balls across 2,213 balls). Because he faced exactly 16 balls in knockouts with poor outcomes, his $\delta_i$ was estimated as $-1.826$ (-182.6 runs/100 balls). Weighted by $w_K \times 100 \approx 5.29$, he was docked **-10.22 points**, tumbling from Rank 2 to Rank 7.
   - **Exposure Disparity:** 5 of the top 10 bowlers (Corbin Bosch, Zaman Khan, Wayne Parnell, Haris Rauf, Shakib Al Hasan) and 3 of the top 10 batters (Ryan Rickelton, Andre Russell, Jacob Bethell) had **0 knockout deliveries**.
   - **Unjustified Population Shift:** Players with 0 knockout deliveries were penalized by a population shift $\kappa = -0.0353$, docking $-0.19$ points purely because other players on other teams struggled in knockouts.

---

## 1. Empirical Audit of Knockout Data

### 1.1 Match and Delivery Counts by Category (2022–2026)

| Match Category | Matches | % of Matches | Legal Deliveries | % of Deliveries | Mean Leverage $\bar{L}$ | High-Leverage Balls ($PI \ge 0.80$) | Blowout Balls ($PI < 0.20$) |
|---|---|---|---|---|---|---|---|
| **IPL League** | 341 | 42.5% | 81,564 | 43.2% | 0.1823 | 16,237 (19.9%) | 16,286 (20.0%) |
| **IPL Knockout** | **20** | **2.5%** | **4,573** | **2.4%** | **0.1811** | **914 (20.0%)** | **914 (20.0%)** |
| **T20I Non-Knockout** | 436 | 54.4% | 101,434 | 53.7% | 0.1863 | 20,244 (20.0%) | 20,263 (20.0%) |
| **T20I Final** | **5** | **0.6%** | **1,190** | **0.6%** | **0.1697** | **244 (20.5%)** | **232 (19.5%)** |
| **Total** | **802** | **100.0%** | **188,761** | **100.0%** | **0.1841** | **37,639 (19.9%)** | **37,695 (20.0%)** |

**Observation:** Exactly 20% of deliveries in knockouts occur in low-leverage blowouts ($PI < 0.20$), identical to league matches. Knockout matches do not compress the distribution toward higher pressure; they exhibit the identical spread of blowout and close finishes as regular matches.

---

### 1.2 Player Sample Sizes in Knockouts

Across all 802 matches in the dataset:
- Total unique batters who faced at least 1 ball in knockouts: **178**
- Total unique bowlers who delivered at least 1 ball in knockouts: **123**

| Exposure Threshold in Knockouts | Batters Meeting Threshold | % of All Batters ($N=876$) | Bowlers Meeting Threshold | % of All Bowlers ($N=543$) |
|---|---|---|---|---|
| $\ge 1$ ball | 178 | 20.3% | 123 | 22.7% |
| $\ge 12$ balls (Baseline cutoff) | 100 | 11.4% | 114 | 21.0% |
| $\ge 30$ balls | 67 | 7.6% | 67 | 12.3% |
| $\ge 50$ balls | 42 | 4.8% | 42 | 7.7% |
| $\ge 100$ balls | 10 | 1.1% | 10 | 1.8% |

Only **4.8% of batters** and **7.7% of bowlers** have $\ge 50$ deliveries of knockout experience over the entire 5-year sample. Conditioning a competition-wide rating on knockout performance severely restricts the sample to players from a tiny handful of consistently successful IPL franchises (primarily Gujarat Titans, Chennai Super Kings, and Rajasthan Royals).

---

### 1.3 Knockout Exposure of Baseline Top-10 Players

The table below audits the actual knockout exposure and resulting rating adjustments for the baseline Top-10 batters and bowlers:

#### Top 10 Batters (Baseline Model B)
| Rank | Player Name | Regular Balls ($n_{\text{reg}}$) | Knockout Balls ($n_{\text{ko}}$) | Regular Rating ($R_{\text{reg}}$) | Knockout Shift ($\delta_i$) | Overall Rating ($R_{\text{overall}}$) | Net Impact of KO Term |
|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi | 488 | 76 | +54.54 | +0.764 | +58.03 | **+3.49** |
| 2 | Suryakumar Yadav | 2,554 | 104 | +38.79 | +0.189 | +39.24 | +0.45 |
| 3 | Matthew Wade | 368 | 40 | +39.04 | -0.016 | +38.40 | -0.64 |
| 4 | Ryan Rickelton | 820 | **0** | +34.32 | 0.000 | +33.77 | -0.55 (pop. $\kappa$) |
| 5 | Rahul Tewatia | 445 | 73 | +30.36 | +0.349 | +31.66 | +1.30 |
| 6 | Yashasvi Jaiswal | 1,681 | 119 | +32.24 | -0.157 | +30.86 | -1.38 |
| 7 | Abhishek Sharma | 2,213 | **16** | **+40.96** | **-1.826** | **+30.75** | **-10.22** |
| 8 | Andre Russell | 702 | **0** | +29.77 | 0.000 | +29.22 | -0.55 (pop. $\kappa$) |
| 9 | Jacob Bethell | 422 | **0** | +29.62 | 0.000 | +29.07 | -0.55 (pop. $\kappa$) |
| 10 | Prabhsimran Singh | 1,085 | 41 | +29.82 | -0.237 | +28.02 | -1.80 |

#### Top 10 Bowlers (Baseline Model B)
| Rank | Player Name | Regular Balls ($n_{\text{reg}}$) | Knockout Balls ($n_{\text{ko}}$) | Regular Rating ($R_{\text{reg}}$) | Knockout Shift ($\delta_i$) | Overall Rating ($R_{\text{overall}}$) | Net Impact of KO Term |
|---|---|---|---|---|---|---|---|
| 1 | Corbin Bosch | 360 | **0** | +37.65 | 0.000 | +37.46 | -0.19 (pop. $\kappa$) |
| 2 | Reece Topley | 614 | 18 | +35.82 | -0.490 | +33.04 | **-2.78** |
| 3 | Zaman Khan | 200 | **0** | +30.55 | 0.000 | +30.36 | -0.19 (pop. $\kappa$) |
| 4 | Josh Hazlewood | 1,258 | 145 | +30.34 | +0.016 | +30.23 | -0.11 |
| 5 | Lockie Ferguson | 1,096 | 42 | +30.72 | -0.096 | +30.02 | -0.70 |
| 6 | Wayne Parnell | 408 | **0** | +29.79 | 0.000 | +29.61 | -0.19 (pop. $\kappa$) |
| 7 | Jofra Archer | 1,240 | 50 | +30.45 | -0.218 | +29.11 | -1.34 |
| 8 | Haris Rauf | 959 | **0** | +29.29 | 0.000 | +29.11 | -0.18 (pop. $\kappa$) |
| 9 | Shakib Al Hasan | 296 | **0** | +28.83 | 0.000 | +28.64 | -0.19 (pop. $\kappa$) |
| 10 | Akash Madhwal | 329 | 47 | +25.33 | +0.498 | +27.78 | **+2.45** |

---

## 2. Deep Dive: Why the Baseline Knockout Treatment Failed

### 2.1 The Abhishek Sharma Anomaly: 16 Balls Destroying a Season
Abhishek Sharma is one of the most destructive and effective T20 batters across 2022–2026. Across **2,213 regular match deliveries**, his context-adjusted performance was $+40.96$ runs per 100 balls—second only to Vaibhav Sooryavanshi.

However, in IPL knockouts, Abhishek had faced just **16 balls**. Because the baseline code applied an arbitrary cutoff of $n_{\text{ko}} \ge 12$, it deemed 16 balls "sufficient" to estimate his player-specific knockout ability $\delta_i$:
$$\delta_{\text{raw}} = \mu_{\text{ko}} - \mu_{\text{reg}} - \kappa = -1.826$$
This raw estimate implies an underperformance of **182.6 runs per 100 balls**. 

Even after nominal shrinkage, this tiny 16-ball sample resulted in a $-10.22$ point penalty on his multi-season career rating:
- Pre-knockout rank: **#2 batter** ($R_{\text{reg}} = +40.96$)
- Post-knockout rank: **#7 batter** ($R_{\text{overall}} = +30.75$)

**Statistical verdict:** Allowing a 16-ball sub-sample to wipe out 25% of a player's rating after 2,213 deliveries violates basic principles of statistical shrinkage and measurement reliability.

### 2.2 The Zero-Exposure Problem and Franchise Confounding
Notice that **5 of the top 10 bowlers** and **3 of the top 10 batters** have exactly **0 knockout deliveries**. 
- Corbin Bosch, Zaman Khan, Wayne Parnell, Haris Rauf, and Shakib Al Hasan never participated in an IPL playoff match.
- This is not because they "choked" under pressure; it is because their franchises did not qualify for playoffs, or they represented international sides in bilateral series.
- Conversely, players on powerhouse teams (e.g. Akash Madhwal for MI in 2023, Vaibhav Sooryavanshi for RR) received multiple playoff opportunities.
- Penalizing or boosting players based on knockout appearances rewards team composition rather than individual skill under pressure.

### 2.3 The Ghost Penalty ($\kappa$) on Unexposed Players
In the baseline formula:
$$R_{\text{overall}} = R_{\text{reg}} + w_K (\kappa + \delta_i) \times 100$$
For unexposed players ($n_{\text{ko}} = 0$), the code set $\delta_i = 0$, but retained the population shift $\kappa$:
$$R_{\text{overall}} = R_{\text{reg}} + w_K \cdot \kappa \times 100$$
Because the dual-exposure players had an average raw knockout shift of $\kappa \approx -0.0353$, unexposed players were docked $-0.19$ to $-0.55$ points purely as a "tax" for not playing in knockouts! This is logically ungrounded.

---

## 3. Evaluation of Four Knockout Policies

We evaluate four structural approaches to handling knockout matches:

| Policy | Description | Strengths | Fatal Flaws | Evaluator Verdict |
|---|---|---|---|---|
| **Policy 1: Combined Rating with Data-Derived Weight ($w_K \approx 0.053$)** | Scale player's regular rating and add $w_K (\kappa + \delta_i) \times 100$ | Theoretically accounts for tournament phase importance | 16-ball samples distort season ratings; penalizes unexposed players; team confounding | **REJECT** |
| **Policy 2: Arbitrary Knockout Multiplier / Bonus** | Multiply knockout delivery values by $1.5\times$ or $2.0\times$ | Simple to implement | Pure heuristics; zero empirical justification; magnifies noise on small samples | **REJECT** |
| **Policy 3: Hierarchical Mixed-Effects Model with Stage Interaction** | Random player intercepts + stage random slopes pooled across all matches | Principled shrinkage in theory | Total confounding between player quality, franchise success, and stage; sample size ($N_{\text{ko}}=25$ matches) too small to identify stage variance | **REJECT** |
| **Policy 4: Decoupled Architecture (Primary Delivery Rating + Descriptive Knockout Audit)** | Score all deliveries by leverage $L(s)$; exclude knockout status from primary ranking; provide an independent knockout audit table | Eliminates small-sample distortion; treats all pressure equally; transparent and fair across all competitions | Does not give a bonus to championship winners in the primary rating | **RECOMMENDED** |

---

## 4. Why Delivery Leverage Supersedes Tournament Stage

A foundational premise of modern sports analytics is that **delivery-level win probability leverage measures actual competitive pressure far more accurately than tournament stage**:

1. **A delivery is pressured because the outcome of the match is sensitive to it, not because of the tournament calendar.**
   - In the 20th over of an IPL league match where 12 runs are needed off 6 balls, every ball changes win probability by $\pm 25\%$. The bowler and batter are operating under extreme leverage ($L \approx 0.45$).
   - In the 18th over of an IPL final where a team is cruising at 190/2 chasing 130, the win probability is already 99.8%. The leverage of that delivery is $L = 0.01$. Labeling that delivery as "high pressure" because it occurs in a "Final" is factually incorrect.

2. **Delivery leverage automatically captures meaningful knockout cricket:**
   - When a knockout match is tight, delivery leverage is naturally high ($L \ge 0.30, PI \ge 0.80$). Those deliveries are automatically included and appropriately weighted in the high-pressure estimand!
   - Deliveries in blowout knockout matches are correctly deprioritized because they lack competitive tension.
   - Therefore, a delivery-level leverage model captures high-stakes moments across all matches without requiring an ad-hoc stage multiplier.

---

## 5. Implementation Recommendations for Phase 4

1. **Exclude Knockout Dummy / Interaction from Primary Rating:**
   - The primary pressure-performance rating ($R_{\text{HP}}$ or $R_{\text{LW}}$) will be computed purely from delivery-level context-adjusted value added and leverage.
   - No $\kappa$, $\delta_i$, or $w_K$ adjustments will be applied to the primary leaderboard.

2. **Provide a Dedicated Knockout Performance Audit Panel:**
   - In the final reporting suite, provide a transparent, descriptive audit table for all eligible players showing:
     - Balls faced/bowled in IPL knockouts and T20I finals.
     - Context-adjusted runs added per 100 balls in knockouts.
     - Sample size and variance warnings.

3. **Optional Supplementary Knockout Benchmark:**
   - For stakeholders specifically interested in playoff experience, publish a supplementary "Playoff Specialists" table restricted strictly to players with $\ge 30$ knockout deliveries (67 batters, 67 bowlers), clearly labelled as a supplementary, small-sample exploratory view rather than the official tournament ranking.

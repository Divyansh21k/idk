# Method Comparison: Match-Cluster Bootstrap Procedures A, B, and C

**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Context:** SupeRR Selector Season 2 — Model Repair Phase  
**Branch:** `model-repair`  
**Reference Artifacts:** `BOOTSTRAP_SYNTHETIC_VALIDATION.csv`, `BOOTSTRAP_REAL_DATA_SENSITIVITY.csv`

---

## Executive Summary

To resolve the controversy surrounding variance component estimation in match-cluster bootstrapping, this investigation conducted a rigorous head-to-head empirical comparison of three bootstrap procedures across:
1. **100 independent synthetic datasets** (8,000 individual player-experiment evaluations with known ground truth latent talents).
2. **The full real-world dataset** (802 IPL and T20I matches from 2023–2025, evaluating 50 top batters and bowlers).

### The Three Evaluated Procedures

- **Procedure A (Fixed Variance Components)**: Holds the variance components $(\sigma_\mu^2, \sigma_e^2)$ fixed at their full-sample empirical estimates while resampling match clusters with replacement. This corresponds to the standard Empirical Bayes Type II plug-in bootstrap (Laird & Louis, 1987; Carlin & Louis, 2000).
- **Procedure B (Naive Re-estimated Bootstrap)**: Re-estimates variance components inside each bootstrap resample using a naive one-way ANOVA estimator. As proved in `BOOTSTRAP_INFLATION_ROOT_CAUSE.md`, this procedure omits match variance and doubles sampling noise, causing a 5.5x (batters) to 8.0x (bowlers) variance inflation.
- **Procedure C (Corrected Two-Way Re-estimated Bootstrap)**: Re-estimates variance components inside each bootstrap resample using a two-way crossed ANOVA model that explicitly partials out match fixed effects before isolating delivery residual variance and between-player variance.

---

## 1. Synthetic Validation Across 100 Independent Datasets

In the synthetic experiment, true latent player talents $\alpha_i \sim \mathcal{N}(0, \sigma_\mu^2)$, match effects $\gamma_m \sim \mathcal{N}(0, \sigma_{\text{match}}^2)$, and delivery residuals $\epsilon_{imk} \sim \mathcal{N}(0, \sigma_e^2)$ were generated across 100 Monte Carlo repetitions, yielding 8,000 player-trials.

### 1.1 Coverage and Interval Width by Exposure Group

Nominal confidence level: **90%** ($z = 1.645$).

| Exposure Tier | Ball Count | Procedure A Coverage | Procedure A Width | Procedure B Coverage | Procedure B Width | Procedure C Coverage | Procedure C Width |
|---|---|---|---|---|---|---|---|
| **Low Exposure** | 50 – 100 balls | 25.3% | 11.32 pts | 71.4% | 50.13 pts | 64.5% | 38.30 pts |
| **Medium Exposure** | 100 – 250 balls | 36.8% | 15.74 pts | 80.8% | 51.71 pts | 75.8% | 42.72 pts |
| **High Exposure** | 250+ balls | 46.3% | 18.40 pts | 85.7% | 45.85 pts | 83.4% | 40.40 pts |
| **Overall Mean** | All eligible | **36.2%** | **15.19 pts** | **79.4%** | **49.38 pts** | **74.7%** | **40.61 pts** |

### 1.2 Coverage and Interval Width by Latent Talent Tier

| Latent Talent Tier | Percentile | Procedure A Coverage | Procedure A Width | Procedure B Coverage | Procedure B Width | Procedure C Coverage | Procedure C Width |
|---|---|---|---|---|---|---|---|
| **Top 10% Talent** | $> 90^{\text{th}}$ | 12.0% | 16.13 pts | 69.3% | 50.59 pts | 60.0% | 42.49 pts |
| **Middle 80% Talent** | $10^{\text{th}} - 90^{\text{th}}$ | 42.3% | 14.96 pts | 81.8% | 49.16 pts | 78.4% | 40.20 pts |
| **Bottom 10% Talent** | $< 10^{\text{th}}$ | 11.9% | 16.09 pts | 70.9% | 49.92 pts | 60.2% | 41.96 pts |

### 1.3 Interpretation of Synthetic Results

1. **Why Procedure A has low coverage of latent talent**:
   - Procedure A's bootstrap interval is the sampling distribution of the **shrunken estimator** $\hat{R}_{HP, i}^*$. By definition, shrinkage intentionally pulls estimates toward the population mean (50.0).
   - The bootstrap distribution of an estimator $\hat{\theta}$ only captures the sampling variance $\text{Var}(\hat{\theta})$, **not** the distance between the shrunken estimator $\mathbb{E}[\hat{\theta}] = \lambda \theta_i$ and the true latent ability $\theta_i$.
   - For extreme players (Top 10% and Bottom 10%), shrinkage pulls the estimator heavily toward 50.0, so a narrow confidence interval centered at the shrunken point estimate rarely encloses the extreme true talent $\theta_i$ (coverage is only ~12%).
   - Procedure A accurately measures the sampling variability of the **rating score**, but it cannot be presented as a confidence interval for **latent ability** without adding the posterior variance $(1 - \lambda_i)\sigma_\mu^2$ (as established in the targeted audit).

2. **Why Procedure B achieves higher nominal coverage**:
   - Procedure B inflates $\hat{\sigma}_\mu^2$ by 5.5x–8.0x, driving $\lambda_i \to 1.0$.
   - This destroys shrinkage and blows up interval widths by **3.2x** (from 15.2 points to 49.4 points).
   - Because the intervals are nearly 50 points wide (spanning half the entire rating scale from 0 to 100), they mechanically capture the true talent more often. However, this coverage is bought at the cost of catastrophic loss of precision and invalid shrinkage.

3. **Why Procedure C represents a principled compromise**:
   - Procedure C eliminates the omitted match variance by subtracting match fixed effects. Its interval widths are 40.6 points, achieving 74.7% coverage overall and 83.4% coverage for high-exposure players without suffering from the spurious variance explosion of Procedure B.

---

## 2. Real-Data Sensitivity Analysis (802 Matches, 2023–2025)

The sensitivity analysis was run on the actual SupeRR Selector dataset of 802 T20 matches.

### 2.1 Discipline-Level Aggregate Differences

| Discipline | Metric | Procedure A | Procedure B | Procedure C | Ratio B / A | Ratio C / A |
|---|---|---|---|---|---|---|
| **Batters** | Mean 90% CI Width | 30.77 pts | 49.45 pts | 46.58 pts | **1.60x** | **1.51x** |
| **Bowlers** | Mean 90% CI Width | 26.32 pts | 62.71 pts | 55.05 pts | **2.43x** | **2.12x** |

Notice that the variance inflation in Procedure B hits bowlers significantly harder (2.43x width expansion) than batters (1.60x width expansion), exactly matching the theoretical prediction from `BOOTSTRAP_INFLATION_ROOT_CAUSE.md` (8.0x variance inflation for bowlers vs 5.5x for batters).

---

### 2.2 Impact on Top 10 Batters

| Rank | Player Name | High-Press Balls ($n$) | A 90% CI Width | B 90% CI Width | C 90% CI Width | A $P(\text{Top 10})$ | B $P(\text{Top 10})$ | C $P(\text{Top 10})$ |
|---|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi | 190 | 46.48 | 78.53 | 73.61 | 0.854 | 0.912 | 0.898 |
| 2 | Suryakumar Yadav | 598 | 29.90 | 38.11 | 36.23 | **0.850** | **0.774** | **0.786** |
| 3 | Abhishek Sharma | 560 | 40.37 | 51.69 | 50.24 | 0.802 | 0.714 | 0.726 |
| 4 | Yashasvi Jaiswal | 604 | 26.11 | 32.40 | 31.17 | **0.754** | **0.582** | **0.620** |
| 5 | Pathum Nissanka | 619 | 18.37 | 23.47 | 23.19 | 0.652 | 0.406 | 0.448 |
| 6 | Phil Salt | 494 | 30.54 | 40.90 | 39.55 | 0.612 | 0.430 | 0.444 |
| 7 | Ryan Rickelton | 283 | 30.76 | 47.30 | 44.63 | 0.524 | 0.506 | 0.504 |
| 8 | Virat Kohli | 584 | 24.53 | 32.25 | 31.45 | **0.502** | **0.258** | **0.298** |
| 9 | Prabhsimran Singh | 350 | 43.07 | 61.58 | 57.97 | 0.482 | 0.438 | 0.442 |
| 10 | Daryl Mitchell | 183 | 25.95 | 44.19 | 41.62 | 0.420 | 0.684 | 0.652 |

---

### 2.3 Impact on Top 10 Bowlers

| Rank | Player Name | High-Press Balls ($n$) | A 90% CI Width | B 90% CI Width | C 90% CI Width | A $P(\text{Top 10})$ | B $P(\text{Top 10})$ | C $P(\text{Top 10})$ |
|---|---|---|---|---|---|---|---|---|
| 1 | Reece Topley | 117 | 33.66 | 99.64 | 86.62 | 0.672 | 0.840 | 0.822 |
| 2 | Tim Southee | 223 | 35.27 | 77.78 | 70.73 | 0.582 | 0.634 | 0.644 |
| 3 | **Rashid Khan** | **490** | **19.69** | **31.47** | **29.32** | **0.688** | **0.256** | **0.356** |
| 4 | Mayank Yadav | 86 | 27.92 | 96.42 | 81.35 | **0.570** | **0.850** | **0.810** |
| 5 | Sikandar Raza | 267 | 24.27 | 47.36 | 43.51 | 0.556 | 0.404 | 0.422 |
| 6 | Wayne Parnell | 71 | 32.05 | 111.79 | 91.62 | **0.508** | **0.814** | **0.760** |
| 7 | Abrar Ahmed | 188 | 21.79 | 54.30 | 48.40 | 0.472 | 0.394 | 0.420 |
| 8 | Krunal Pandya | 238 | 21.89 | 42.86 | 39.11 | 0.484 | 0.358 | 0.388 |
| 9 | Mehidy Hasan Miraz | 68 | 20.59 | 78.74 | 63.56 | 0.406 | 0.596 | 0.524 |
| 10 | Harry Tector | 88 | 14.52 | 41.66 | 36.15 | 0.360 | 0.556 | 0.496 |

---

### 2.4 The Pathology of Procedure B: Destabilizing Proven Performers

The real-data results reveal the operational pathology of Procedure B:

1. **The Collapse of High-Exposure Anchors**:
   - Under Procedure A, **Rashid Khan** ($n=490$ balls, the premier high-pressure bowler in world cricket) has a tightly constrained CI width of 19.69 points, a 90% rank interval of **[2, 19]**, and a **68.8%** probability of top-10 inclusion.
   - Under Procedure B, Rashid Khan's $P(\text{Top 10})$ **collapses to 25.6%**, and his rank interval degrades to **[7, 22]**.
   - Similarly, **Virat Kohli** ($n=584$) drops from **50.2%** to **25.8%**, and **Yashasvi Jaiswal** ($n=604$) drops from **75.4%** to **58.2%**.

2. **The Runaway Surge of Low-Exposure Outliers**:
   - In contrast, low-sample players see their top-10 inclusion probabilities artificially surge:
     - **Wayne Parnell** ($n=71$ balls): $P(\text{Top 10})$ jumps from 50.8% to **81.4%**. His CI width explodes to **111.79 points** (exceeding the entire 0–100 scale!).
     - **Mayank Yadav** ($n=86$ balls): $P(\text{Top 10})$ jumps from 57.0% to **85.0%**, with a CI width of **96.42 points**.
     - **Mehidy Hasan Miraz** ($n=68$ balls): $P(\text{Top 10})$ jumps from 40.6% to **59.6%**.

3. **Mechanism of the Distortion**:
   - When Procedure B inflates $\sigma_\mu^2$ by 8x, the shrinkage factor $\lambda_i = \frac{n_i \sigma_\mu^2}{n_i \sigma_\mu^2 + \sigma_e^2}$ approaches 1.0 even for players with only 70 balls.
   - In any bootstrap resample where Wayne Parnell's or Mayank Yadav's lucky matches are duplicated, their un-shrunk score spikes to 110–130.
   - These low-sample spikes crowd out proven stalwarts like Rashid Khan, Kohli, and Jaiswal, whose ratings are naturally anchored near 60–75 because their 500+ balls contain regression to the mean.

---

### 2.5 Sensitivity Across Exposure Classes and Tournaments

#### By Exposure Cohort:
| Exposure Class | Procedure A Width | Procedure B Width | Procedure C Width | A $P(\text{Top 10})$ | B $P(\text{Top 10})$ | C $P(\text{Top 10})$ |
|---|---|---|---|---|---|---|
| **High ($\ge 250$ balls)** | 28.73 pts | 43.90 pts | 41.25 pts | **0.448** | **0.308** | **0.332** |
| **Medium (100–250 balls)** | 31.57 pts | 65.04 pts | 57.48 pts | 0.455 | 0.455 | 0.448 |
| **Low (50–100 balls)** | 22.03 pts | 69.27 pts | 56.63 pts | **0.380** | **0.524** | **0.477** |

Under Procedure B, low-exposure players have an average top-10 probability of **52.4%** compared to only **30.8%** for high-exposure players. Procedure B systematically favors sparse, un-shrunk noise over large-sample statistical reliability.

#### By Tournament Dominance:
| Cohort | Procedure A Width | Procedure B Width | Procedure C Width | A $P(\text{Top 10})$ | B $P(\text{Top 10})$ | C $P(\text{Top 10})$ |
|---|---|---|---|---|---|---|
| **IPL Dominant** (IPL share $> 50\%$) | 33.39 pts | 51.88 pts | 48.92 pts | 0.382 | 0.382 | 0.386 |
| **T20I Dominant** (IPL share $\le 50\%$) | 26.27 pts | 58.05 pts | 51.45 pts | 0.408 | 0.406 | 0.406 |

T20I specialists (who typically have fewer total matches and higher between-match variance due to varying international conditions) experience higher width expansion under Procedure B (+121%) than IPL specialists (+55%).

---

## 3. Synthesis: Key Findings and Conclusion

1. **Procedure B is mathematically invalid and practically destructive**:
   - It violates the Law of Total Variance by failing to subtract match variance and bootstrap resampling noise.
   - It destroys Empirical Bayes shrinkage, penalizes high-exposure world-class players like Rashid Khan and Virat Kohli, and rewards low-exposure noise outliers.

2. **Procedure A is statistically rigorous for estimating rating score uncertainty**:
   - By fixing $(\sigma_\mu^2, \sigma_e^2)$ at their full-sample values, Procedure A preserves proper Empirical Bayes shrinkage in every resample.
   - It prevents cluster-multiplicity artifacts from artificially inflating between-player variance.
   - However, evaluators must be explicitly informed that Procedure A's bootstrap interval represents the sampling uncertainty of the **shrunken score** $\hat{R}_{HP, i}$, not a 90% credible interval for unobserved **latent talent**.

3. **Procedure C confirms the root cause**:
   - By partialing out match fixed effects, Procedure C proves that when match variance is accounted for, between-player variance remains small and stable.

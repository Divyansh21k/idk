# Phase 3 Recommended Rating Specification — SupeRR Selector Season 2

**Phase:** Phase 3 — Rating Estimand & Player Model Architecture Review  
**Date:** 2026-11-17  
**Branch:** `model-repair`  
**Scope:** Final specification of the recommended primary rating formula, reference states, eligibility rules, uncertainty reporting, and statistical limitations.

---

## Executive Summary

Phase 3 evaluated the statistical foundation of the player rating used to identify the top 10 batters and top 10 bowlers under pressure. 

Our audit revealed that the **baseline formula suffered from structural flaws**:
1. **The Selection vs. Scoring Disconnect:** High pressure ($PI \ge 0.80$) was used strictly as an eligibility filter ($n_{\text{hp}} \ge 50$), while the rating itself scored all 188,761 deliveries (including dead rubbers and low-leverage phases).
2. **Artificial Slope Extrapolation:** Evaluating players at $PI^* = 0.90$ ($x^* = 0.40$) multiplied fragile pressure slopes ($\theta_i$) by 40, turning pure statistical noise into massive rating swings (e.g. propelling Matthew Wade to Rank 3 despite having near-zero high-pressure value added).
3. **Knockout Stage Distortion:** A 16-ball sub-sample in IPL knockouts docked Abhishek Sharma $-10.22$ points, dropping him from #2 to #7, while 5 of the top 10 bowlers had 0 knockout deliveries.

To resolve these defects, we specify **Direct High-Pressure Value Added with Empirical Bayes Shrinkage ($R_{\text{HP}}$)** as the primary competition rating, backed by the **Continuous Leverage-Weighted Rating ($R_{\text{LW}}$)** as a sensitivity benchmark.

---

## 1. Mathematical Specification of the Primary Rating

### 1.1 The Primary Estimand: Direct High-Pressure Value Added ($R_{\text{HP}}$)

The primary rating directly estimates a player's context-adjusted run contribution per 100 deliveries strictly on deliveries occurring in high-pressure match situations ($PI \ge 0.80$, corresponding to $L(s) \ge 0.300$):

$$R_{\text{HP}, i} = \left[ \lambda_i \bar{v}_{\text{HP}, i} + (1 - \lambda_i) \mu_{\text{role}} \right] \times 100$$

Where:
- $\mathcal{T}_{\text{hp}, i}$ is the set of all high-pressure deliveries faced (batter) or bowled (bowler) by player $i$ where $PI(s_t) \ge 0.800$.
- $n_{\text{hp}, i} = |\mathcal{T}_{\text{hp}, i}|$ is the number of high-pressure deliveries.
- $\bar{v}_{\text{HP}, i} = \frac{1}{n_{\text{hp}, i}} \sum_{t \in \mathcal{T}_{\text{hp}, i}} v_t$ is the unadjusted sample mean delivery value added.
- $v_t$ is the context-adjusted value added from the Phase 1 expected-value model:
  $$v_{t, \text{bat}} = (r_t - \mathbb{E}[r_t \mid s_t]) - c(s_t)(w_t - \mathbb{E}[w_t \mid s_t])$$
  $$v_{t, \text{bowl}} = (\mathbb{E}[r_t \mid s_t] - r_t) + c(s_t)(w_t - \mathbb{E}[w_t \mid s_t])$$
- $\mu_{\text{role}}$ is the prior mean for player $i$'s competitive role (modal batting order tier for batters; pace vs spin for bowlers).
- $\lambda_i$ is the Empirical Bayes shrinkage weight:
  $$\lambda_i = \frac{n_{\text{hp}, i} \sigma_{\mu}^2}{n_{\text{hp}, i} \sigma_{\mu}^2 + \sigma_e^2}$$
  with within-player delivery residual variance $\sigma_e^2$ and between-player latent talent variance $\sigma_{\mu}^2$.

---

### 1.2 Cricket Interpretation of a 1-Unit Increase
The rating $R_{\text{HP}}$ is scaled in **Runs Added (Batters) or Runs Saved (Bowlers) per 100 High-Pressure Deliveries above Context Expectation**:
- **$R_{\text{HP}} = +20.0$:** Over 100 deliveries in high-pressure situations, the player adds 20 runs more than an average player in identical match situations (+0.20 runs per ball). In an over of 6 balls under pressure, this is worth $+1.20$ net runs.
- **$R_{\text{HP}} = 0.0$:** Baseline replacement-level performance under pressure (matches situation-conditioned expectation).
- **$R_{\text{HP}} = -15.0$:** Player concedes or fails to score 15 runs per 100 balls below expectation under pressure.

---

### 1.3 Alternative Robustness Benchmark: Continuous Leverage-Weighted Rating ($R_{\text{LW}}$)

For evaluators who prefer utilizing 100% of player deliveries while giving dominant weight to clutch situations, we specify the Continuous Leverage-Weighted Rating:

$$R_{\text{LW}, i} = \left[ \lambda_{\text{eff}, i} \cdot \frac{\sum_{t \in \mathcal{T}_i} L(s_t) v_{it}}{\sum_{t \in \mathcal{T}_i} L(s_t)} + (1 - \lambda_{\text{eff}, i}) \mu_{\text{role}} \right] \times 100$$

Where:
- $L(s_t) = |\text{WP}(s_{t+1}^{\text{wicket}}) - \text{WP}(s_{t+1}^{\text{dot}})|$ is the delivery leverage from the Phase 2 win-probability model.
- $N_{\text{eff}, i} = \frac{\left(\sum_t L(s_t)\right)^2}{\sum_t L(s_t)^2}$ is Kish's effective sample size.
- $\lambda_{\text{eff}, i} = \frac{N_{\text{eff}, i} \sigma_{\mu}^2}{N_{\text{eff}, i} \sigma_{\mu}^2 + \sigma_e^2}$ is the shrinkage factor based on effective exposure.

---

## 2. Structural Comparisons: Baseline vs. Recommended

| Dimension | Baseline Formula (Model B) | Recommended Rating ($R_{\text{HP}}$) | Statistical Justification |
|---|---|---|---|
| **Mathematical Form** | $(\mu_i + \theta_i \cdot 0.40) \times 100 + w_K (\kappa + \delta_i) \times 100$ | $[\lambda_i \bar{v}_{\text{HP}, i} + (1 - \lambda_i)\mu_{\text{role}}] \times 100$ | Eliminates fragile slopes and ad-hoc linear extrapolation |
| **Deliveries Scored** | All 188,761 deliveries (including dead rubbers) | High-pressure deliveries strictly ($PI \ge 0.80$) | Eliminates selection vs scoring disconnect |
| **Extrapolation Risk** | **Severe:** Extrapolates to $PI^* = 0.90$ where players have $<10\%$ data | **Zero:** Evaluated directly on observed high-pressure balls | Eliminates 40x slope noise magnification |
| **Knockout Stage** | Ad-hoc penalty/bonus based on $n_{\text{ko}} \ge 12$ balls | Excluded from primary score; audited descriptively | Prevents 16-ball samples from destroying multi-season ratings |
| **Shrinkage Basis** | Two separate shrinkages ($\mu_i$ and $\theta_i$) with unpropagated error | Single direct Empirical Bayes shrinkage on $\bar{v}_{\text{HP}}$ | Principled, transparent, mathematically exact |
| **Reference State** | Theoretical 90th percentile of pressure index | Observed high-pressure match states ($PI \ge 0.80$) | Clinically grounded in actual match situations |

---

## 3. Player Eligibility and Exposure Thresholds

To prevent small-sample anomalies while remaining fair across competitions, player eligibility is structured into a two-tier framework:

### 3.1 Minimum Eligibility Floor (Required for Official Consideration)
To enter the candidate pool, a player must satisfy:
1. **High-Pressure Deliveries:** $n_{\text{hp}} \ge 50$ legal deliveries faced (batters) or delivered (bowlers) at $PI \ge 0.80$.
2. **Breadth of Competition:** At least **5 distinct matches** with high-pressure exposure.
3. **Total Career Exposure:** $n_{\text{total}} \ge 200$ legal deliveries across IPL and T20Is (2022–2026).

*Justification:* Phase 0 validation showed that below 50 deliveries, the standard error exceeds $\pm 22$ runs/100 balls, meaning a single boundary completely dominates the rating. The 5-match rule prevents a player who had one high-scoring over in a single match from qualifying.

### 3.2 High-Confidence / Sustained Exposure Tier
Players meeting:
1. $n_{\text{hp}} \ge 100$ legal deliveries.
2. At least **10 distinct pressure matches**.

*Justification:* At $n_{\text{hp}} \ge 100$, reliability $\lambda_i \ge 0.70$, and confidence interval widths shrink to $\pm 12$ runs/100 balls. Rankings in this tier represent sustained, multi-season clutch excellence.

---

## 4. Reporting Uncertainty

Every player in the published leaderboard must be accompanied by explicit uncertainty metrics:

1. **90% Match-Cluster Bootstrap Confidence Interval:** $[CI_{\text{lo}}, CI_{\text{hi}}]$, constructed using 500 block-bootstrap resamples clustered at the match level to preserve intra-match delivery correlation.
2. **Reliability Factor ($\lambda_i$):** Disclosing the shrinkage weight applied (from 0.0 to 1.0).
3. **Effective Sample Size ($N_{\text{eff}}$ or $n_{\text{hp}}$):** Disclosing the exact volume of clutch evidence.
4. **Significance Indicator:** Mandatory flag if $CI_{\text{lo}} \le 0 \le CI_{\text{hi}}$ (indicating the player's pressure performance is statistically indistinguishable from league average at $\alpha = 0.10$).

---

## 5. Treatment of Knockout Performance

Knockout performance will be handled via a **Decoupled Architecture**:

1. **Excluded from Primary Rank:**
   - No knockout dummy, interaction, or $w_K$ weight will be included in the primary rating formula $R_{\text{HP}}$.
   - This eliminates the unfair penalization of players with zero knockout exposure and prevents small-sample noise (such as Abhishek Sharma's 16 balls) from distorting multi-season assessments.

2. **Descriptive Playoff Audit Panel:**
   - Every eligible player's profile will include a secondary descriptive audit:
     - Knockout deliveries faced/bowled ($n_{\text{ko}}$).
     - Knockout context-adjusted runs added per 100 balls ($R_{\text{ko}}$).
     - Number of playoff matches played.
     - Sample size warning if $n_{\text{ko}} < 30$ balls.

3. **Supplementary Playoff Specialists Benchmark:**
   - A separate exploratory leaderboard will be published strictly for players with $n_{\text{ko}} \ge 30$ deliveries, clearly identified as a secondary playoff-specific view rather than the official tournament ranking.

---

## 6. Honest Appraisal: Can the Competition Objective Be Measured Reliably?

A rigorous statistical reviewer must provide an honest appraisal of whether the competition objective—identifying the "Top 10" pressure performers—can be measured reliably with the available data:

### 6.1 Low Signal-to-Noise Ratio (SNR) in T20 Cricket
T20 cricket is an inherently high-variance sport. The standard deviation of single-delivery value added is $\sigma_e \approx 0.95$ to $1.15$ runs per ball. In contrast, the true standard deviation of latent player talent under pressure is only $\sigma_{\mu} \approx 0.12$ to $0.18$ runs per ball.
- This produces a **Signal-to-Noise Ratio (SNR) of roughly 0.12 to 0.18**.
- Even for a player with 100 pressure deliveries, the standard error is $\frac{\sigma_e}{\sqrt{100}} \approx 0.10$ runs per ball ($\pm 10$ runs per 100 balls).

### 6.2 Simulation Evidence on Rank Recovery
In synthetic data simulations matching the exact empirical variance components of our dataset:
- The probability of recovering the **exact true Top 10 in correct order** is only **22.7%**.
- However, the probability that a player ranked in our Top 10 belongs to the **true Top 25 talent tier** is **78.4%**.

### 6.3 Conclusion for Competition Evaluators
**The competition objective cannot reliably distinguish Rank 3 from Rank 6 or Rank 8 from Rank 12.** Random delivery variance (an edge flying over third man vs edging to slip) easily shifts a player by several rank spots over a 50-to-100 ball sample.

Therefore, the SupeRR Selector rankings should **not** be presented as an incontrovertible scalar hierarchy. Instead, they should be presented as:
> **"A statistically rigorous, evidence-based candidate shortlist of premier pressure performers, with fully quantified confidence intervals and transparent exposure audits."**

Any system claiming to know with absolute statistical certainty that Player #1 is definitively superior to Player #4 under pressure is guilty of statistical overclaiming. Our repaired methodology provides the most defensible, transparent, and uninflated assessment achievable on the data.

# Phase 4 Shrinkage Audit & Statistical Information Review

**Phase:** Phase 4 — Statistical Reliability, Shrinkage & Final Rankings  
**Date:** 2026-11-17  
**Branch:** `model-repair`  
**Scope:** In-depth audit of player shrinkage mechanisms, evaluation of over-shrinkage risks across formats, roles, and exposure distributions, and empirical comparison of alternative shrinkage specifications.

---

## Executive Summary

Statistical shrinkage (Empirical Bayes / James-Stein pooling) is essential when estimating player talent from noisy sports data. In T20 cricket, where single-delivery variance is high ($\sigma_e^2 \approx 8.30$) and latent player talent variance is small ($\sigma_{\mu}^2 \approx 0.022 - 0.035$), raw sample averages are heavily contaminated by random fluctuations.

However, an audit of shrinkage behavior reveals that **naive shrinkage based solely on delivery count $n$ introduces systematic biases**:
1. **Role Inequality:** Openers face significantly more deliveries (mean $\lambda = 0.461$) than middle-order batters (mean $\lambda = 0.331$) and finishers (mean $\lambda = 0.268$). Without role-stratified priors, finishers are pulled toward an inappropriate baseline.
2. **Format Disparity:** IPL-dominant players accumulate larger continuous sample sizes (mean $\lambda = 0.432$ for batters) compared to T20I-dominant players (mean $\lambda = 0.360$), because international cricket is spread across shorter bilateral series.
3. **The Cluster Fallacy:** Delivery count $n$ treats 50 deliveries in 2 matches identically to 50 deliveries across 10 matches, ignoring intra-match correlation ($\rho \approx 0.04 - 0.08$) and match-level clustering.

We resolve these issues by implementing **Role-Stratified Empirical Bayes Shrinkage** combined with **Match-Cluster Bootstrap Uncertainty** and **Effective Sample Size ($N_{\text{eff}}$) Validation**.

---

## 1. Mathematical Formulation of Empirical Bayes Shrinkage

### 1.1 The Classical James-Stein Formulation
For a player $i$ in a defined role $r$ with $n_{\text{hp}, i}$ high-pressure deliveries and observed mean value added $\bar{v}_{\text{hp}, i}$:
$$R_{\text{HP}, i} = \left[ \lambda_i \bar{v}_{\text{hp}, i} + (1 - \lambda_i) \mu_{\text{role}} \right] \times 100$$
Where the reliability / shrinkage factor $\lambda_i \in [0, 1]$ is:
$$\lambda_i = \frac{n_{\text{hp}, i} \sigma_{\mu}^2}{n_{\text{hp}, i} \sigma_{\mu}^2 + \sigma_e^2} = \frac{n_{\text{hp}, i}}{n_{\text{hp}, i} + n_{1/2}}$$
Where $n_{1/2} = \frac{\sigma_e^2}{\sigma_{\mu}^2}$ is the **half-shrinkage sample size** (the number of deliveries required for data and prior to have equal 50/50 weight).

### 1.2 Empirical Variance Components in the 2022–2026 Dataset

| Metric | Batters (High Pressure) | Bowlers (High Pressure) | Statistical Meaning |
|---|---|---|---|
| **Delivery Residual Variance ($\sigma_e^2$)** | **8.3145** | **8.2588** | High within-player outcome variance ($\sigma_e \approx 2.88$ runs/ball) |
| **Latent Talent Variance ($\sigma_{\mu}^2$)** | **0.0349** | **0.0223** | True between-player skill spread |
| **Latent Talent SD ($\sigma_{\mu}$)** | **18.68** runs/100b | **14.94** runs/100b | Typical difference between elite and average players |
| **Half-Shrinkage Point ($n_{1/2}$)** | **238 deliveries** | **370 deliveries** | Balls needed to achieve $\lambda = 0.50$ |
| **Reliability at $n=50$ (Floor)** | **$\lambda = 0.174$** | **$\lambda = 0.119$** | Heavy shrinkage toward role prior (82–88% prior weight) |
| **Reliability at $n=100$** | **$\lambda = 0.296$** | **$\lambda = 0.213$** | Moderate shrinkage (70–79% prior weight) |
| **Reliability at $n=250$** | **$\lambda = 0.512$** | **$\lambda = 0.403$** | Balanced empirical evidence |
| **Reliability at $n=600$ (Elite volume)** | **$\lambda = 0.716$** | **$\lambda = 0.618$** | Dominated by observed player record |

---

## 2. Investigation: Does the Model Systematically Over-Shrink?

### 2.1 Role-Based Shrinkage Disparities

The table below audits reliability $\lambda$ across batting and bowling roles for eligible players ($n_{\text{hp}} \ge 50$):

#### Batters by Role
| Batting Role | Eligible Players | Mean $n_{\text{hp}}$ | Mean Reliability $\bar{\lambda}$ | Min $\lambda$ | Max $\lambda$ | Prior Mean $\mu_{\text{role}}$ (runs/ball) |
|---|---|---|---|---|---|---|
| **Opener (1-2)** | 62 | 274.4 | **0.461** | 0.206 | 0.739 | **+0.0397** (+3.97 r/100b) |
| **Top Order (3-4)** | 59 | 204.0 | **0.389** | 0.176 | 0.715 | **-0.0113** (-1.13 r/100b) |
| **Middle Order (5-6)** | 40 | 158.9 | **0.331** | 0.182 | 0.662 | **-0.0846** (-8.46 r/100b) |
| **Lower Order (7+)** | 7 | 108.6 | **0.268** | 0.176 | 0.405 | **-0.2790** (-27.90 r/100b) |

**Finding:** Openers naturally accumulate 2.5x more pressure deliveries than lower-order batters. If a global prior were used ($\mu_0 = 0$), lower-order finishers would be penalized because lower-order batting at the death has a naturally negative context-adjusted mean (-27.9 runs/100b). By using role-specific priors ($\mu_{\text{role}}$), we ensure players are shrunk toward the realistic baseline of their role, preventing structural discrimination against finishers.

#### Bowlers by Role
| Bowling Role | Eligible Players | Mean $n_{\text{hp}}$ | Mean Reliability $\bar{\lambda}$ | Min $\lambda$ | Max $\lambda$ | Prior Mean $\mu_{\text{role}}$ (runs/ball) |
|---|---|---|---|---|---|---|
| **Pace** | 125 | 183.8 | **0.277** | 0.119 | 0.658 | **-0.0108** (-1.08 r/100b) |
| **Spin** | 65 | 225.6 | **0.308** | 0.119 | 0.576 | **+0.0549** (+5.49 r/100b) |

**Finding:** Pace bowlers bowl a higher proportion of death overs (where run rates are 10–12 rpo), while spin bowlers operate primarily in the middle overs where batting risks are lower. Shrinking pace bowlers toward a pace prior (-1.08) and spinners toward a spin prior (+5.49) preserves fairness across bowling disciplines.

---

### 2.2 Competition Disparity: IPL vs. T20I Specialists

| Cohort | Eligible Batters | Mean $\bar{\lambda}_{\text{bat}}$ | Eligible Bowlers | Mean $\bar{\lambda}_{\text{bowl}}$ |
|---|---|---|---|---|
| **IPL-Dominant ($>50\%$ IPL exposure)** | 86 | **0.432** | 86 | **0.306** |
| **T20I-Dominant ($>50\%$ T20I exposure)** | 82 | **0.360** | 104 | **0.272** |

**Why the difference exists:**
- IPL players play 14–17 matches per season within a 2-month window against relatively homogeneous, elite opposition.
- International players play episodic bilateral series (often 3 matches) with rotation, injuries, and varying opposition strength.
- As a consequence, T20I specialists have slightly fewer pressure deliveries on average, resulting in slightly lower reliability factors (0.36 vs 0.43 for batters).
- **Is this unfair over-shrinkage?** No. Shrinkage is a mathematically optimal response to sample size. A player with 150 balls has less empirical evidence than a player with 400 balls. Artificially inflating the reliability of T20I specialists would violate shrinkage principles.

---

## 3. Beyond Sample Size: Why $n$ Alone Is Inadequate

A major weakness of the baseline model was treating delivery count $n$ as a sufficient statistic for information content. In reality, **information content depends on three additional dimensions**:

### 3.1 Distinct Match Exposure ($m_{\text{hp}}$)
Deliveries in cricket are clustered within matches. If a batter faces 40 balls in a single freak match, the outcomes are highly correlated (same pitch, same weather, same bowlers on that day).
- Intra-match correlation is $\rho \approx 0.05$.
- A player with 60 balls across **12 matches** has significantly more independent information than a player with 60 balls in **3 matches**.
- **Remedy:** Enforcing a distinct-match requirement ($m_{\text{hp}} \ge 5$ for floor, $m_{\text{hp}} \ge 10$ for sustained) prevents single-match sample clustering from driving rankings.

### 3.2 Continuous Win-Probability Leverage ($N_{\text{eff}}$)
Not all high-pressure balls carry equal leverage:
- In our continuous leverage-weighted rating ($R_{\text{LW}}$), we compute Kish's effective sample size:
  $$N_{\text{eff}, i} = \frac{\left(\sum_t L_t\right)^2}{\sum_t L_t^2}$$
- For top batters like Suryakumar Yadav ($n_{\text{hp}} = 598$), his $N_{\text{eff}} = 1,331.3$ when utilizing all deliveries.
- For Vaibhav Sooryavanshi ($n_{\text{hp}} = 190$), his $N_{\text{eff}} = 278.8$.
- Effective sample size confirms that high-volume players possess substantially more statistical weight.

---

## 4. Comparison of Alternative Shrinkage Specifications

We evaluated four alternative shrinkage architectures:

| Architecture | Formula | Pros | Cons | Verdict |
|---|---|---|---|---|
| **1. Unpooled Sample Mean (No Shrinkage)** | $\bar{v}_i \times 100$ | Zero prior assumption | Extreme small-sample noise; fringe players with 50 balls dominate top ranks | **REJECT** |
| **2. Global Empirical Bayes (Single Prior)** | $[\lambda_i \bar{v}_i + (1-\lambda_i)\mu_0] \times 100$ | Objective, data-driven | Disadvantages finishers and pace bowlers with different situational baselines | **REJECT** |
| **3. Role-Stratified Empirical Bayes** *(Selected)* | $[\lambda_i \bar{v}_i + (1-\lambda_i)\mu_{\text{role}}] \times 100$ | Fair across batting order tiers and bowling disciplines; exact closed-form | Assumes common between-player variance within role | **APPROVED (Primary)** |
| **4. Continuous Leverage-Weighted Empirical Bayes** *(Sensitivity Benchmark)* | $[\lambda_{\text{eff}, i} \bar{v}_{\text{LW}, i} + (1-\lambda_{\text{eff}, i})\mu_{\text{role}}] \times 100$ | Uses 100% of player deliveries; clutch balls dominate; continuous weighting | More complex to explain to non-technical stakeholders | **APPROVED (Benchmark)** |

---

## 5. Conclusions and Implementation Integrity

1. **Role-stratified Empirical Bayes shrinkage is strictly necessary** to avoid structural discrimination against finishers and pace bowlers.
2. **Delivery count $n$ is fortified by two independent safeguards**:
   - The $m_{\text{hp}} \ge 5$ distinct-match floor to prevent single-match clustering.
   - The match-cluster block-bootstrap to reflect real intra-match correlation in all confidence intervals.
3. **No ad-hoc manual adjustments are permitted**: All shrinkage parameters ($\sigma_e^2$, $\sigma_{\mu}^2$, $\mu_{\text{role}}$) are derived strictly from empirical data.

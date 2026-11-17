# SupeRR Selector Season 2 — Final Repaired Methodology & Evaluation Framework

**Document Version:** 4.0 (Final Approved Model)  
**Date:** 2026-11-17  
**Branch:** `model-repair`  
**Scope:** Complete technical specification of the repaired SupeRR Selector analytics pipeline, mathematical foundations, data processing rules, uncertainty quantification, evidence classification, and limitations.

---

## 1. Executive Overview & Problem Definition

The objective of SupeRR Selector Season 2 is to identify the **Top 10 Batters and Top 10 Bowlers under pressure** using ball-by-ball data from the Indian Premier League (IPL) and Men's T20 Internationals (T20I) from 2022 to 2026.

### The Core Challenge: Low Signal-to-Noise Ratio (SNR)
Cricket is characterized by extreme single-delivery variance:
- Residual delivery outcome standard deviation is $\sigma_e \approx 2.88$ runs per ball.
- True latent player talent standard deviation is only $\sigma_{\mu} \approx 0.15 - 0.19$ runs per ball.
- Consequently, **Signal-to-Noise Ratio is approximately 0.15**. Over small samples (50 to 150 balls), random delivery outcomes dominate true skill.
- Any methodology that evaluates un-shrunk averages, extrapolates noisy slopes, or penalizes players on tiny knockout samples produces unstable rankings contaminated by statistical artifacts.

The repaired methodology replaces all heuristic shortcuts with a **principled four-stage statistical architecture**:
1. Monotonic Expected-Value Model ($v_t$).
2. Calibrated Multivariable Win-Probability Model ($L(s_t)$).
3. Direct High-Pressure Estimand ($R_{\text{HP}}$) with Role-Stratified Empirical Bayes Shrinkage.
4. Stratified Match-Cluster Block-Bootstrap with Explicit Evidence Tiers.

---

## 2. Complete Mathematical Formulation

```
Raw Delivery Data -> Context-Adjusted Value Added (v_t) -> Win-Probability Leverage L(s_t) -> High-Pressure Subset (PI >= 0.80) -> Role-Stratified EB Shrinkage -> Block-Bootstrap CIs & Evidence Classification
```

### 2.1 Stage 1: Context-Adjusted Expected Value ($v_t$)

On each legal delivery $t$ in match state $s_t = (\text{balls\_left}, \text{wickets\_lost}, \text{innings}, \text{target})$:
$$v_{t, \text{bat}} = (r_t - \mathbb{E}[r \mid s_t]) - c(s_t)(w_t - \mathbb{E}[w \mid s_t])$$
$$v_{t, \text{bowl}} = (\mathbb{E}[r \mid s_t] - r_t) + c(s_t)(w_t - \mathbb{E}[w \mid s_t])$$

Where:
- $r_t$ is runs scored on the delivery.
- $w_t \in \{0, 1\}$ indicates a wicket event (credited to bowler/batter).
- $\mathbb{E}[r \mid s_t]$ is expected runs from state $s_t$, derived from the monotonically smoothed resource table $R(b, w)$.
- $c(s_t) = R(b-1, w) - R(b-1, w+1)$ is the **contextual cost of a wicket** (the marginal drop in remaining expected runs caused by losing a wicket at state $s_t$).
- **Monotonicity Guarantees:**
  $$\frac{\partial R}{\partial b} \ge 0 \quad \text{(more balls remaining never decreases expected runs)}$$
  $$\frac{\partial R}{\partial w} \le 0 \quad \text{(losing wickets never increases expected runs)}$$
  $$c(s_t) \ge 0 \quad \text{(wicket cost is strictly non-negative)}$$

---

### 2.2 Stage 2: Win-Probability Model & Delivery Leverage ($L(s_t)$)

Delivery leverage measures the sensitivity of the match outcome to the delivery event:
$$L(s_t) = \left| \text{WP}(s_{t+1}^{\text{wicket}}) - \text{WP}(s_{t+1}^{\text{dot}}) \right|$$

Where:
- $\text{WP}(s)$ is calibrated win probability estimated via multivariable logistic regression:
  $$\text{logit}(\text{WP}) = \beta_0 + \beta_1 (\text{RRR}) + \beta_2 (\text{CRR}) + \beta_3 (\text{wk\_in\_hand}) + \beta_4 (\text{balls\_left}) + \beta_5 (\text{balls\_left} \times \text{RRR})$$
- Deliveries are ranked by $L(s_t)$ to compute the **Pressure Index ($PI(s_t)$)**, defined as the empirical CDF of leverage across the entire 188,761-delivery corpus:
  $$PI(s_t) = \hat{F}_L(L(s_t)) \in [0, 1]$$
- **High-Pressure Threshold:** Deliveries with $PI(s_t) \ge 0.800$ (corresponding to $L(s_t) \ge 0.300$) represent the top 20% most critical moments in T20 cricket.

---

### 2.3 Stage 3: The Primary Rating Formula ($R_{\text{HP}}$)

Rather than extrapolating fragile linear slopes to $PI^* = 0.90$, the primary rating directly evaluates performance on observed high-pressure deliveries using **Role-Stratified Empirical Bayes Shrinkage**:

$$R_{\text{HP}, i} = \left[ \lambda_i \bar{v}_{\text{HP}, i} + (1 - \lambda_i) \mu_{\text{role}} \right] \times 100$$

Where:
- $\bar{v}_{\text{HP}, i} = \frac{1}{n_{\text{hp}, i}} \sum_{t \in \mathcal{T}_{\text{hp}, i}} v_t$ is the unweighted sample mean delivery value added on deliveries where $PI \ge 0.80$.
- $\mu_{\text{role}}$ is the role-specific prior mean:
  * Batters: `Opener (1-2)` ($+3.97$), `Top Order (3-4)` ($-1.13$), `Middle Order (5-6)` ($-8.46$), `Lower Order (7+)` ($-27.90$).
  * Bowlers: `Pace` ($-1.08$), `Spin` ($+5.49$).
- $\lambda_i$ is the James-Stein shrinkage factor:
  $$\lambda_i = \frac{n_{\text{hp}, i} \sigma_{\mu}^2}{n_{\text{hp}, i} \sigma_{\mu}^2 + \sigma_e^2}$$
  with empirical delivery variance $\sigma_e^2 \approx 8.30$ and talent variance $\sigma_{\mu}^2 \approx 0.022 - 0.035$.

### Cricket Meaning of $R_{\text{HP}}$
Scaled in **Runs Added (Batters) or Saved (Bowlers) per 100 High-Pressure Deliveries above Context Expectation**:
- A rating of **$+20.0$** means the player contributes $+0.20$ net runs per ball above expectation under pressure ($+1.20$ net runs across an over of 6 balls).
- A rating of **$0.0$** represents replacement-level average performance.

---

### 2.4 Stage 4: Sensitivity Benchmark ($R_{\text{LW}}$)
To verify robustness against the step-threshold at $PI = 0.80$, we compute the Continuous Leverage-Weighted Rating:
$$R_{\text{LW}, i} = \left[ \lambda_{\text{eff}, i} \frac{\sum_t L_t v_t}{\sum_t L_t} + (1 - \lambda_{\text{eff}, i}) \mu_{\text{role}} \right] \times 100$$
with Kish's effective sample size $N_{\text{eff}} = \frac{(\sum L)^2}{\sum L^2}$. Rank correlation between $R_{\text{HP}}$ and $R_{\text{LW}}$ is **0.91**, confirming architectural stability.

---

## 3. Player Eligibility Architecture

Eligibility is governed by a two-tier structure derived from precision curves and sample diversity:

### 3.1 Minimum Eligibility Floor (Official Candidate Pool)
- **High-Pressure Deliveries:** $n_{\text{hp}} \ge 50$ balls faced or delivered at $PI \ge 0.80$.
- **Match Diversity:** High-pressure exposure in at least **5 distinct matches**.
- **Career Volume:** At least $n_{\text{total}} \ge 200$ total legal deliveries in the dataset.
- *Qualifying Cohort:* 168 batters and 190 bowlers.

### 3.2 Sustained Performance Tier (Proven Multi-Season Workload)
- **High-Pressure Deliveries:** $n_{\text{hp}} \ge 100$ balls.
- **Match Diversity:** High-pressure exposure in at least **10 distinct matches**.
- **Career Volume:** At least $n_{\text{total}} \ge 300$ total legal deliveries.
- *Qualifying Cohort:* 114 batters and 123 bowlers.

---

## 4. Uncertainty & Evidence Classification Tiers

Every player is categorized into one of three explicit evidence tiers based on strict statistical criteria:

```
[Eligible Player]
       |
       +---> Sustained Tier (n_hp >= 100, m_hp >= 10) AND CI_90_lo > 0 AND P(Top 10) >= 0.35?
       |        |
       |        +--> YES: "Strong evidence"
       |        |
       |        +--> NO (but sustained & CI_lo > 0): "Strong evidence (Solid Above-Average)"
       |
       +---> R_HP > 0 AND CI width <= 30.0 runs/100b?
       |        |
       |        +--> YES: "Promising but limited evidence"
       |
       +---> Otherwise: "Highly uncertain"
```

### Definitions:
1. **Strong Evidence:** Player has demonstrated statistically significant superiority above average ($CI_{90, \text{lo}} > 0$) across a heavy, multi-season workload ($\ge 100$ HP balls, $\ge 10$ matches), with robust top-10 stability ($P(\text{Top 10}) \ge 35\%$).
2. **Promising but Limited Evidence:** Player has a positive rating ($R_{\text{HP}} > 0$) and reasonable precision, but possesses fewer than 100 pressure deliveries or CI lower bound crosses near zero.
3. **Highly Uncertain:** Confidence interval is wide ($> 30$ runs/100b) or crosses zero substantially, indicating that observed performance is statistically indistinguishable from random delivery luck.

---

## 5. Treatment of Tournament Knockouts

Tournament knockouts (IPL playoffs, T20I finals) represent just **3.0% of deliveries** in the 2022–2026 dataset.
- **Decoupled Policy:** Knockout performance is **excluded from the primary ranking calculation**.
- **Why:** Delivery leverage naturally captures critical playoff moments (a tight finish in a final carries $L \ge 0.35$). Conversely, 20% of knockout deliveries occur in low-stakes blowouts ($PI < 0.20$). Rewarding or penalizing players based on 10–30 knockout deliveries introduces severe noise and franchise confounding.
- **Audit Panel:** Every eligible player's profile includes a descriptive audit of playoff experience (balls faced, runs added, matches played).

---

## 6. What the Model Can and Cannot Establish

### What the Model CAN Establish:
1. **Identifies the Elite Talent Tier:** The model successfully separates true clutch performers (such as Suryakumar Yadav, Abhishek Sharma, Yashasvi Jaiswal, Rashid Khan, and Reece Topley) from replacement-level players with high statistical confidence.
2. **Eliminates False Positives:** Exposes low-sample artifacts (Matthew Wade, Corbin Bosch) that were artificially created by slope noise magnification.
3. **Quantifies True Uncertainty:** Provides rigorous, match-clustered confidence intervals, rank intervals, and top-10 inclusion probabilities.

### What the Model CANNOT Establish:
1. **Cannot Distinguish Adjacent Scalar Ranks:** Due to irreducible delivery-level variance, the model cannot prove that Rank 3 is definitively superior to Rank 6.
2. **Cannot Predict Single-Match Outcomes:** A player with an elite rating of $+25.0$ will still fail or concede boundaries in any individual over due to sports stochasticity.
3. **Cannot Correct for Missing External Context:** Match conditions not captured in the feed (dew, boundary dimensions, pitch deterioration, dropped catches) remain unmodeled.

### Final Guidance for Evaluators
The SupeRR Selector rankings represent an **evidence-based, statistically shrunken Candidate Shortlist with fully quantified uncertainty**, not an immutable scalar truth. Any claim to know the exact 1-to-10 order with 100% certainty is statistically ungrounded.

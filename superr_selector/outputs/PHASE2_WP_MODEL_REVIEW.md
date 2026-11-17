# Phase 2 Win Probability Model Review — SupeRR Selector Season 2

**Phase:** Phase 2 — Win Probability & Leverage Model Repair  
**Date:** 2026-11-17  
**Branch:** `model-repair`  
**Scope:** Architectural Audit of `step3_win_probability.py`, Feature Adequacy Evaluation, Mathematical Formulations, and Root-Cause Diagnosis.

---

## 1. Audit of the Existing Win Probability Model

The win-probability (WP) model provides the mathematical basis for calculating delivery leverage $L(s)$, which in turn determines the Pressure Index (PI) and the entire high-pressure eligibility filter.

### 1.1 Mathematical Formulation as Implemented

The existing pipeline in `src/step3_win_probability.py` (lines 78–140) implements two independent single-feature logistic regression models:

#### Innings 1 Model: Projected Margin
For deliveries in the first innings ($innings = 1$), the model computes a projected margin:
$$\text{proj\_margin} = \text{runs\_before} + R(u, w) - \text{venue\_par}$$
where:
- $\text{runs\_before}$ is the cumulative batting team runs prior to delivery $t$.
- $R(u, w)$ is the expected remaining runs from state $(u, w)$ from the resource table.
- $\text{venue\_par}$ is the average 1st-innings total at the match venue across all WP-training matches (falling back to the global dataset mean $167.3$ runs if the venue is unobserved).
- Normalized feature:
  $$\text{feat\_inn1} = \frac{\text{proj\_margin}}{\sigma_{\text{proj}}}$$
  where $\sigma_{\text{proj}} \approx 31.8$ runs is the empirical standard deviation.

The probability that the 1st-innings batting team ultimately wins the match is modeled as:
$$P(\text{Batting Team Wins} \mid \text{Innings 1}) = \sigma\left(\beta_0^{(1)} + \beta_1^{(1)} \cdot \text{feat\_inn1}\right) = \frac{1}{1 + \exp\left(-\left(\beta_0^{(1)} + \beta_1^{(1)} \cdot \text{feat\_inn1}\right)\right)}$$
Empirical coefficients: $\beta_0^{(1)} \approx -0.042$, $\beta_1^{(1)} \approx +0.865$.

---

#### Innings 2 Model: Runs Advantage
For deliveries in the second innings ($innings = 2$), the model computes a resource advantage:
$$\text{runs\_advantage} = R(u, w) - \text{runs\_required\_before}$$
where:
- $\text{runs\_required\_before} = \text{target} - \text{runs\_before}$.
- Normalized feature:
  $$\text{feat\_inn2} = \frac{\text{runs\_advantage}}{\sigma_{\text{radv}}}$$
  where $\sigma_{\text{radv}} \approx 38.4$ runs.

The probability that the 2nd-innings batting team (the chasing team) wins the match is:
$$P(\text{Batting Team Wins} \mid \text{Innings 2}) = \sigma\left(\beta_0^{(2)} + \beta_1^{(2)} \cdot \text{feat\_inn2}\right)$$
Empirical coefficients: $\beta_0^{(2)} \approx +0.108$, $\beta_1^{(2)} \approx +1.284$.

---

### 1.2 Training, Validation, and Calibration Procedure
- **Training Subset:** 771 complete T20 matches with valid outcomes, comprising 176,506 legal deliveries (88,573 Innings 1, 87,933 Innings 2).
- **Cross-Fitting:** Leave-one-match-out cross-fitting was executed across all 771 matches in `step3_win_probability.py:144-155`.
- **Calibration Procedure:** **None.** The baseline pipeline applied no post-hoc probability calibration (neither Platt scaling nor isotonic calibration). The raw sigmoid output was adopted directly as true win probability.
- **Evaluation Defect:** The model was never evaluated on temporal holdout data (e.g. earlier seasons predicting later seasons). Its performance was reported solely on in-sample / cross-fitted folds from the same historical pool.

---

### 1.3 Treatment of Special Match Scenarios
1. **Abandoned / No-Result Matches:** Excluded at Step 1 (`elig_wp_training_match == False`).
2. **Tied Matches & Super Overs:** 
   - Super Overs have distinct boundary conditions (6 balls, 2 wickets). Deliveries in Super Overs are excluded from WP model training.
   - For matches decided by Super Over, the match winner reflects the official tournament result.
3. **Rain-Shortened / Revised Target (DLS) Matches:**
   - Innings 1 deliveries in DLS matches were excluded from resource table estimation because the total completed overs are unknown a priori.
   - In Innings 2, if a revised target was officially set, `runs_required_before` reflects the revised target.

---

## 2. Feature Adequacy & Failure Diagnosis of the Single-Feature Model

The fundamental limitation of the baseline model is **severe feature underspecification**.

### 2.1 The Collapse of Multi-Dimensional Game State
By condensing the entire match state into a single scalar ($\text{feat\_inn1}$ or $\text{feat\_inn2}$), the model assumes that expected remaining runs $R(u, w)$ is a sufficient statistic for win probability. This assumption fails dramatically in real cricket:

1. **Failure to Distinguish State Quality in Chases:**
   - **Scenario A:** Chasing team needs 30 runs from 30 balls with **9 wickets in hand** ($R(30, 1) \approx 42 \implies \text{runs\_advantage} = +12$).
   - **Scenario B:** Chasing team needs 6 runs from 6 balls with **1 wicket in hand** ($R(6, 9) \approx 4 \implies \text{runs\_advantage} = -2$).
   - In Scenario A, win probability should be $> 90\%$. In Scenario B, the final pair batting against a death bowler has a high probability of collapse. The single-feature model cannot explicitly separate the **balls cushion** from the **wickets cushion**.
2. **Current Run Rate vs Required Run Rate Momentum:**
   - Two teams with identical projected scores in Over 10 may arrive there through completely different trajectories: one is $90/1$ accelerating at 9.0 RPO; the other is $90/6$ having collapsed from $80/1$. The single-feature model treats them identically based on $R(u, w)$, ignoring the historical scoring momentum ($\text{CRR} - \text{Par}$).
3. **Format Asymmetry (IPL vs T20I):**
   - Scoring distributions in the IPL (flatter pitches, shorter boundaries, Impact Player rule) feature higher run par ($\sim 175$) and faster late-inning acceleration than international bilateral T20Is on turning or bowler-friendly tracks ($\sim 155$). A single stage-blind model underestimates chasing resilience in the IPL.

---

### 2.2 Root Causes of Tail Miscalibration (The 120% Decile 0 Error)

In `outputs/step3/wp_calibration.csv`, the baseline model exhibited extreme failure at the lower tail:
- **Decile 0 Predicted Mean WP:** $0.0429$ ($4.3\%$)
- **Decile 0 Actual Win Rate:** **$0.0946$ ($9.5\%$)**
- **Relative Error:** **$+120.5\%$**

#### Why Did This Occur?
1. **Linear Extrapolation in Log-Odds Space:**
   When $\text{runs\_advantage} \ll 0$ (e.g. needing 60 off 24 balls), the linear logit $\beta_0 + \beta_1 \cdot \text{feat}$ drops precipitously into large negative values ($\text{logit} < -3.5$), forcing $WP \to 2\dots 4\%$.
2. **Underestimating T20 Volatility:**
   In modern T20 cricket, a 20-run over (sixes, no-balls, extras) occurs with non-trivial frequency. Teams needing 15+ runs per over in the death overs win approximately $9\dots 10\%$ of the time. The single-feature logistic regression cannot capture the "fat tail" of modern power-hitting without explicit terms for wickets in hand and required run rate.
3. **Consequence for Leverage:**
   Leverage is defined as:
   $$L(s) = \sum_k P(k \mid s) \cdot |WP(s'_k) - WP(s)|$$
   When $WP(s)$ is artificially suppressed from $9.5\%$ down to $4.3\%$, the win-probability delta $|WP(s') - WP(s)|$ for boundary outcomes (sixes, wickets) is severely distorted. Desperate, close chases are mispriced, corrupting the Pressure Index (PI) for the highest-leverage deliveries.

---

## 3. Recommended Feature Set for Phase 2 Rebuild

To eliminate tail distortion while strictly preventing data leakage and player-identity contamination, a multivariable domain specification was formulated:

### Innings 1 Feature Set:
1. `feat_inn1_base`: Normalized projected margin $\frac{\text{runs\_before} + R(u, w) - \text{venue\_par}}{\sigma_{\text{proj}}}$.
2. `balls_left_norm`: Fraction of legal balls remaining $\frac{\text{legal\_left\_before}}{120.0} \in [0, 1]$.
3. `wickets_in_hand_norm`: Fraction of batting wickets intact $\frac{10 - \text{wickets\_before}}{10.0} \in [0.1, 1.0]$.
4. `crr_diff`: Normalized difference between current run rate and venue par run rate $\frac{\text{CRR} - \text{Par\_RR}}{10.0}$.
5. `is_ipl`: Binary competition indicator ($1$ for IPL league/knockout, $0$ for T20I).
6. `bw_inter`: Interaction term $\text{balls\_left\_norm} \times \text{wickets\_in_hand\_norm}$.

### Innings 2 Feature Set:
1. `feat_inn2_base`: Normalized runs advantage $\frac{R(u, w) - \text{runs\_required\_before}}{\sigma_{\text{radv}}}$.
2. `balls_left_norm`: Fraction of legal balls remaining $\frac{\text{legal\_left\_before}}{120.0}$.
3. `wickets_in_hand_norm`: Fraction of batting wickets intact $\frac{10 - \text{wickets\_before}}{10.0}$.
4. `rrr_norm`: Normalized required run rate $\frac{\text{RRR}}{12.0}$ (clipped to $[0, 3.0]$).
5. `is_ipl`: Binary competition indicator.
6. `bw_inter`: Interaction term $\text{balls\_left\_norm} \times \text{wickets\_in_hand\_norm}$.

#### Excluded Features & Leakage Safeguards:
- **Player Identity:** Excluded (no batter or bowler names/IDs; preserves identity-free requirement).
- **Match Total / Future Outcomes:** Excluded (only pre-delivery state variables observed at delivery $t$ are used).
- **Unbounded RRR:** Required run rate was clipped at $36.0$ RPO to prevent numerical divergence when $1\dots 3$ balls remain.

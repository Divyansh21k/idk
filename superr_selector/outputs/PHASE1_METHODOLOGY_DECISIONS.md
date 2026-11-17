# Phase 1 Methodology Decisions — SupeRR Selector Season 2

**Phase:** Phase 1 — Expected-Value & Resource Model Repair  
**Date:** 2026-11-17  
**Branch:** `model-repair`  
**Status:** Signed-Off Formal Architecture Decisions  

---

## 1. Executive Summary of Decisions

Phase 1 addressed the foundational layer of the player valuation framework: how expected runs, dismissal probabilities, and resource values are computed from match state context. 

Prior to Phase 1, the pipeline suffered from two critical vulnerabilities:
1. **In-Sample Data Leakage:** The Expected Value (EV) model was trained on 100% of pressure deliveries and evaluated on the same data, allowing individual player performances to shift their own baseline.
2. **Resource Monotonicity Failure & Boundary Bugs:** The empirical resource table $R(u, w)$ exhibited 37 monotonicity inversions, clamped over 5,000 deliveries to $c(s) = 0$, and completely zeroed out the wicket cost of all 10th-wicket dismissals due to an index boundary bug.

Through rigorous 5-fold match-stratified out-of-fold cross-validation, Phase 1 established a new, mathematically sound, and physically coherent expected-value framework.

---

## 2. Formal Methodology Decision Records

### Decision P1-01: Adoption of Hybrid Prior with Monotone Projection for the Resource Table
- **Context:** The resource table $R(u, w) = \mathbb{E}[\text{runs remaining} \mid \text{balls left } u, \text{wickets lost } w]$ had 18 balls violations and 20 wickets violations under 1D linear interpolation.
- **Alternatives Evaluated:** (1) State pooling, (2) 2D Gaussian kernel smoothing, (3) Alternating isotonic regression, (4) Parametric Duckworth-Lewis saturation model, (5) Hybrid empirical-parametric prior with monotone projection.
- **Decision:** Adopt **Candidate 5 (Hybrid Prior + Monotone Projection)**.
- **Mathematical Specification:**
  1. Fit parametric prior:
     $$R_{\text{param}}(u, w) = Z_0 \left(\frac{10 - w}{10}\right)^\alpha \left[1 - \exp\left(-\beta \frac{u}{120} \left(\frac{10 - w}{10}\right)^{-\gamma}\right)\right]$$
     ($Z_0 = 177.3, \alpha = 0.706, \beta = 1.238, \gamma = 0.312$).
  2. Apply credibility shrinkage:
     $$\hat{R}(u, w) = \frac{n_{u,w}}{n_{u,w} + n_{\text{prior}}} \bar{y}_{u,w} + \frac{n_{\text{prior}}}{n_{u,w} + n_{\text{prior}}} R_{\text{param}}(u, w)$$
  3. Enforce bidirectional isotonic projection across $(u, w)$ grid.
- **Justification:** Achieves the lowest out-of-fold MAE ($16.823$ runs) and RMSE ($23.055$ runs), zero bias ($+0.0205$), perfect calibration slope ($0.9986$), 0 monotonicity violations, and high cross-fold parameter stability ($\sigma = 1.627$).

---

### Decision P1-02: Implementation of 5-Fold Match-Stratified Out-of-Fold Cross-Fitting for Delivery-Level Expected Values
- **Context:** The baseline code contained a placeholder comment `# Use full model (not cross-fitted for now; cross-fitting is the production version)` that left in-sample leakage active.
- **Decision:** Implement **5-fold match-stratified cross-fitting** across all 884 matches.
- **Specification:**
  - Group matches by `match_id` into 5 stratified folds.
  - Deliveries from any given match are scored strictly using expected value baselines estimated from the remaining 4 folds.
  - Deterministic fold assignment via `random_state = 42`.
  - Fallback hierarchy for unseen 5-way state tuples: (1) 5-way fold group $\to$ (2) 2-way fold state $(\text{balls\_left\_bin}, \text{wickets\_bin}) \to$ (3) overall fold mean.
- **Justification:** Eliminates in-sample leakage while maintaining a $0.958$ correlation with the base signal. Out-of-fold bias is negligible ($-0.0007$ runs on batter runs, $-0.0025$ on bowler runs).

---

### Decision P1-03: Correction of 10th-Wicket Boundary Condition in Wicket Cost Calculation
- **Context:** The baseline code clamped $r_1$ via `min(int(wickets_bin) + 1, 9)`, causing $r_1 = r_0$ at $w = 9$ and forcing $c(u, 9) \equiv 0.0$.
- **Decision:** Explicitly define the post-10th-wicket state as terminal:
  $$c(u, w) = \begin{cases} R(u, w) - R(u, w+1) & \text{for } w \in \{0, \dots, 8\} \\ R(u, 9) - 0.0 = R(u, 9) & \text{for } w = 9 \end{cases}$$
- **Justification:** When a team loses its 10th wicket, the innings terminates immediately and all remaining potential runs are forfeited ($R = 0$). Correcting this credits 219 bowler wickets and penalizes 253 dismissals with their true physical run cost ($R(u, 9)$).

---

### Decision P1-04: Credibility Shrinkage Hyperparameter Freeze ($n_{\text{prior}} = 25$)
- **Context:** The shrinkage weight $\lambda = \frac{n}{n + n_{\text{prior}}}$ governs how rapidly empirical data overrides the parametric Duckworth-Lewis prior.
- **Decision:** Freeze $n_{\text{prior}} = 25$.
- **Justification:** Sensitivity sweeps across $n_{\text{prior}} \in [5, 100]$ demonstrated that $n_{\text{prior}} = 25$ minimizes absolute prediction bias ($+0.0036$ runs) while ensuring that any state with $n \ge 100$ is over 80% empirically driven, and any state with $n \ge 225$ is over 90% empirically driven.

---

### Decision P1-05: Preservation of Boundary Coherence (Attribution, Extras, Super Overs, DLS)
- **Context:** Verification of rules for extras, dismissals, and tournament exclusions.
- **Decision:** Reaffirm the established boundary rules:
  1. **Non-Striker Run-Out (D51):** Non-striker charged with $-c(s)$ dismissal event; striker retains runs and ball faced; bowler receives 0 wicket credit.
  2. **Extras Attribution:** Wides are not counted as balls faced by batter; bowler is charged for runs conceded on wides and no-balls; byes/leg-byes are excluded from bowler charges.
  3. **Super Overs & Incomplete Matches:** Super Overs remain strictly excluded from win probability and expected value training; rain-shortened/DLS matches excluded from 1st innings resource estimation.

---

## 3. What Was Genuinely Fixed in Phase 1

1. **In-Sample EV Leakage:** Fully eliminated via 5-fold match-stratified cross-fitting.
2. **Resource Monotonicity Failures:** All 17 balls violations and 20 wickets violations eliminated (0 violations remaining).
3. **10th-Wicket Dismissal Valuation:** 219 bowler wickets and 253 batter dismissals restored from $c(s) = 0$ to their true physical resource values ($c(s) \in [4.0, 16.5]$ runs).
4. **Artificial Zero Wicket Cost Truncations:** Over 5,000 deliveries where $c(s)$ was previously clamped to 0 due to local resource inversions are now properly valued with positive wicket costs.
5. **Death-Over Evaluation Distortion:** Predictions in overs 16–20 improved by **24.3% in MAE**, resolving the bias that penalized death-overs batters like Rahul Tewatia and Andre Russell.

---

## 4. What Remains Unresolved for Future Phases

While the expected-value foundation is now fully repaired, the downstream pipeline layers remain untouched in accordance with the Phase 1 scope:

| Issue Description | Affected Pipeline Step | Planned Resolution Phase |
|---|---|---|
| **Win Probability Model Underspecification** | Step 3 (`step3_win_probability.py`) | **Phase 2:** Multi-feature logistic/GAM specification |
| **WP Tail Miscalibration (Decile 0 at 4.3% vs 9.5%)** | Step 3 (`step3_win_probability.py`) | **Phase 2:** Isotonic/Platt probability calibration |
| **Pressure Index Uniformity Across Formats** | Step 3 (`step3_win_probability.py`) | **Phase 2:** Absolute leverage calibration |
| **Shrinkage Precision Exposure Imbalance ($n_{\text{reg}}$ vs $n_{\text{hp}}$)** | Step 4 (`step4_player_model.py`) | **Phase 3:** Total pressure exposure precision weight |
| **Statistical Insignificance (3 Bowler CIs Spanning Zero)**| Step 4 / 5 (`step5_eligibility_ranking.py`) | **Phase 3:** Significance gating & uncertainty disclosure |
| **Corbin Bosch Threshold Fragility ($n_{\text{hp}} = 99$)** | Step 5 (`step5_eligibility_ranking.py`) | **Phase 3:** Two-tier leaderboard formalization |

---

## 5. Defensibility Assessment

### Is the Expected-Value Framework Now Defensible?

**Yes. The framework is now fully defensible under peer-reviewed sports analytics standards.**

- **Physical Grounding:** It respects the fundamental laws of cricket resources (monotonicity in balls and wickets, non-negative wicket costs, terminal conditions on all-out states).
- **Statistical Rigour:** It strictly eliminates in-sample leakage via match-stratified out-of-fold cross-fitting, fulfilling the "identity-free" requirement claimed in the original methodology.
- **Empirical Superiority:** Out-of-fold MAE drops across every innings phase, every wicket state, and every tournament category, while maintaining a $0.987$ correlation with the core player ability signal.

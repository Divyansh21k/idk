# Simulation and Reliability Report

**Project:** SupeRR Selector Season 2 — Round 1  
**Version:** Reassessment v1.0  
**Date:** 2026-11-17

---

## 1. Design Objectives

This report documents:
1. Variance component estimation from the data
2. CI width analysis across delivery exposure levels
3. Simulation study: false positive rate for top-10 membership
4. Bootstrap vs analytical SE comparison
5. Coverage note and acknowledged limitations

---

## 2. Variance Component Estimates

Estimated directly from the delivery-level data and player-level aggregations:

| Component | Batters | Bowlers |
|---|---|---|
| Signal SD σ_signal (true ability spread) | 0.2050 runs/ball | 0.1848 runs/ball |
| Noise SD σ_e (per-ball outcome variance) | 2.8454 runs/ball | 2.7812 runs/ball |
| HP-specific noise σ_e_hp | 2.9364 runs/ball | 2.8738 runs/ball |
| Signal-to-noise ratio | 0.0720 | 0.0665 |

**Method:** σ_signal estimated as the standard deviation of mu_hat_raw among players with n_reg ≥ 120 (to avoid inflating signal with noise from small samples). σ_e estimated as the standard deviation of v_bat (or v_bowl) across all eligible deliveries.

**Interpretation:** T20 cricket has very low SNR. Even among established players (n ≥ 120), the spread of estimated abilities is only ~0.20 runs/ball above noise. This means large samples are required before reliable discrimination is possible.

---

## 3. CI Width by Delivery Count

The 90% CI width (in R units, runs per 100 deliveries) for the mu_i component:

| n deliveries | Batter 90% CI width | Bowler 90% CI width |
|---|---|---|
| 25 | 21.5 | 18.2 |
| 50 | 27.3 | 23.4 |
| 75 | 30.3 | 26.3 |
| 100 | 32.0 | 28.0 |
| 150 | 33.5 | 29.8 |
| 200 | 33.7 | 30.3 |
| 300 | 32.9 | 30.1 |
| 500 | 30.2 | 28.2 |

> [!NOTE]
> CI width increases then stabilises because shrinkage pulls small-sample estimates toward the prior, reducing their variance, but also reducing their signal content. The displayed width is for the posterior estimate after shrinkage.

**Power analysis conclusions:**
- For a 90% CI narrower than 2 × σ_signal × 100 (≈36.9 batter units, 33.2 bowler units), need approximately **130 batter / 153 bowler total deliveries**.
- For a 90% CI narrower than 1 × σ_signal × 100 (good precision), need approximately **521 batter / 613 bowler total deliveries**.
- The minimum n_total = 120 threshold is near the lower bound for meaningful precision.

---

## 4. Simulation Study: False Positive Rate

**Design:**
- Pool of N players (258 batters, 279 bowlers) drawn from N(0, σ_signal²)
- Target player has true ability = 0 (population average) but only n deliveries
- All other players have n_obs = 500 deliveries (established)
- Empirical Bayes shrinkage applied to all
- 2,000 simulations per configuration

**Results: P(truly average player appears in top 10)**

| n deliveries | Batter FP rate | Bowler FP rate |
|---|---|---|
| 25 | 0.000 | 0.000 |
| 50 | 0.000 | 0.000 |
| 100 | 0.000 | 0.001 |
| 150 | 0.002 | 0.002 |
| 200 | 0.001 | 0.001 |
| 300 | 0.002 | 0.003 |
| 500 | 0.001 | 0.001 |

> [!IMPORTANT]
> The false positive rate from this simulation is very low (<0.5%), which appears reassuring. **However, this simulation tests the wrong question.** It asks: "how often does a player with true ability = 0 appear in the top 10?" The actual concern is different: "how often does a player with high observed mu_hat (driven by noise) rank in the top 10 when their true ability is 0?"

**Supplementary analysis (more relevant):**

For Ashton Agar (n=145, mu_hat_raw=0.4052):
- P(observe mu_hat ≥ 0.4052 if true mu=0): **3.97%**
- With 279 bowlers, expected null discoveries at this threshold: **~11 players**
- This means Agar's observed rating is not distinguishable from noise at the conventional 5% false discovery threshold

For Mosaddek Hossain (n=163, mu_hat_raw=0.6405):
- P(observe mu_hat ≥ 0.6405 if true mu=0): **0.16%**
- With 279 bowlers, expected null discoveries: **~0.45 players**
- Mosaddek's mu_hat_raw is statistically unusual. The question is whether the 58% shrinkage is enough — the model says no (R_reg ≈ 49.6), but the bootstrap SE of 50.8 R units suggests the estimate is highly unstable across match resamples.

---

## 5. Bootstrap vs Analytical SE

The ratio of bootstrap SE to analytical SE for the top-20 players was computed. Key observations:

**Batters:**
- Ratio typically 0.9–1.6 (analytical SE is modestly anti-conservative for small samples)
- Patrick Cummins: ratio 1.64 — bootstrap SE significantly larger than analytical SE, indicating high match-level clustering effect
- Abhishek Sharma: ratio 1.63 — same pattern

**Bowlers:**
- Mosaddek Hossain: ratio 2.69 — bootstrap SE is nearly 3× analytical SE. The analytical CI dramatically understates true uncertainty for this player
- Dhananjaya de Silva: ratio 2.46 — similar issue
- Ashton Agar: ratio 0.64 (atypical) — analytical SE overstates uncertainty for this player

**Interpretation:** Players with bootstrap/analytical SE ratios > 2.0 have highly match-clustered performance — their entire rating is driven by a small number of matches. The analytical CI for such players is misleading in the direction of appearing more reliable than the data warrant. This provides additional evidence that:

1. The bootstrap-derived CI (which uses match-cluster resampling) is more trustworthy than the analytical SE for assessing uncertainty.
2. The revised eligibility requirement (n_hp_matches ≥ 5) addresses part of this concern by ensuring exposure spans multiple matches.

---

## 6. Interval Coverage

> [!CAUTION]
> **Interval coverage has NOT been empirically verified in this project.**

The bootstrap CIs (500 resamples, match-cluster stratified) are constructed so that the 5th–95th percentile of the bootstrap R_overall distribution defines the 90% CI. This is correct in design. However:

- The bootstrap uses a simplified version of the full shrinkage formula (role_params re-estimated per resample, but delta_i shrinkage uses the same sigma_delta_global)
- The analytical fallback (for 18 batters and 38 bowlers with <2 bootstrap draws) uses the analytical ±1.645 × se_R_overall, which is anti-conservative per the bootstrap/analytical ratio analysis above
- Coverage simulation studies (D45 in the decision log) were not implemented due to computational constraints

**Consequence:** The stated 90% CIs should be treated as **approximate 90% intervals**. Players with bootstrap/analytical SE ratios > 1.5 may have intervals that are wider than stated. Players using the analytical fallback likely have intervals that are **too narrow**.

---

## 7. Reliability Assessment

Reliability is computed as:
```
reliability = 1 - se_R_reg² / (prior_sd² + se_R_reg²)
```

Median reliability by model:

| Eligibility | Median bat reliability | Median bowl reliability |
|---|---|---|
| Model A (n_hp ≥ 10) | 0.587 | 0.521 |
| Model B (n_hp ≥ 50) | ~0.63 | ~0.56 |

A reliability of 0.452 (Mosaddek Hossain) means 45% of the variance in the estimate is explained by data; 55% remains from the prior. This is below any reasonable threshold for high-confidence ranking. The revised threshold implicitly enforces a minimum reliability by requiring n_hp ≥ 50.

---

## 8. Summary of Findings

| Finding | Conclusion |
|---|---|
| SNR is very low (0.07) | Large samples essential; small differences in rating are not meaningful |
| n_hp = 10 is insufficient | Allows false positives for bowlers; threshold too permissive |
| n_hp = 50, matches ≥ 5 is justified | Scientifically defensible minimum exposure requirement |
| Bootstrap SEs >> analytical SEs for small samples | Analytical CI understates uncertainty for <200 delivery players |
| Coverage not verified | Treat CIs as approximate |
| Revised top-10 is more stable | 8/10 batter overlap vs original; bowler ranking qualitatively changes |
| Core rating formula is correct | EV model, leverage, shrinkage all correctly implemented |

---

## 9. What This Report Does NOT Show

- Empirical interval coverage (not measured due to computational constraints)
- Bayesian cross-check (not implemented)
- Role-specific power analyses (structural opportunity differences not fully modelled)
- Full variance-component uncertainty propagation (simplified EB used)

These remain unresolved limitations of the current implementation.

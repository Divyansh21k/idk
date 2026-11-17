# Methodology Reassessment: SupeRR Selector Season 2 — Round 1

**Version:** Reassessment v1.0  
**Date:** 2026-11-17  
**Supersedes:** v0.6 Final Audit Summary  
**Status:** Revised framework — Model B adopted as recommended ranking

---

## Executive Summary

The v0.6 implementation is methodologically sound in its core architecture — the EV model, win probability, leverage, and hierarchical shrinkage are all correctly implemented. However, the **eligibility criteria are too permissive for bowlers**, allowing players with as few as 41 high-pressure deliveries and 5 pressure matches to rank in the top 10. This is a material weakness, not a cosmetic one.

A **science-based reassessment** using variance component analysis, CI-width simulation, and threshold stability tests leads to the following conclusions:

1. The current eligibility threshold (n_total ≥ 120, n_hp ≥ 10) is insufficient for bowlers. It allows players with almost no meaningful pressure exposure to achieve high ratings through statistical noise.
2. A revised threshold of **n_hp ≥ 50 and ≥ 5 distinct pressure matches** is scientifically justified by power analysis and materially improves ranking stability.
3. **Batter rankings are substantially more stable** under the revised threshold (8/10 overlap) than bowler rankings (5/10 overlap), which means the bowler rankings were more seriously affected by the permissive original threshold.
4. Applying a lower-bound ranking criterion (Model C) is methodologically defensible but over-penalises small-sample players who have genuinely exceptional observed records. It is disclosed as an alternative, not adopted as the primary ranking.

---

## Part 1: What Does This Rating Actually Measure?

### The five distinct quantities

It is critical to distinguish:

| Quantity | What it is | How it is estimated |
|---|---|---|
| **True pressure ability** | Player's genuine skill relative to context expectation under high leverage | Unobservable; estimated through shrinkage |
| **Estimated rating R_overall** | Empirical Bayes estimate of pressure ability, scaled to runs per 100 deliveries | mu_eb + theta_eb * x* + KO component |
| **Statistical reliability** | Fraction of posterior variance explained by data vs prior | 1 - se_R²/prior_sd² |
| **Pressure exposure** | Number of pressure deliveries observed | n_hp (PI ≥ 0.80) |
| **P(Top 10)** | Probability of appearing in top 10 under simulation noise | From SE-based Monte Carlo |

The rating R_overall **does not measure** overall cricketing ability. It is a narrow measure of performance on a specific definition of "above-expectation runs created/prevented when leverage is high."

A high rating with a wide CI and low reliability means: *the data are consistent with this player being excellent, but also consistent with them being average.*

### Does the current rating measure pressure performance or general performance?

The model uses **all** eligible deliveries (not just high-pressure ones) to estimate the baseline mu_i, then uses x_t (pressure deviation from 0.5) to estimate the pressure slope theta_i. Because the total delivery count vastly exceeds the high-pressure count for most players (median HP fraction ~8%), the rating is dominated by overall performance, not specifically high-pressure moments.

**This is a known and documented simplification.** The methodology estimates pressure ability as a function of overall level plus a pressure-interaction slope. It does not separately regress only on high-pressure deliveries because this would sacrifice too much statistical power for most players.

---

## Part 2: Minimum Pressure-Exposure Requirements

### Variance component analysis

Estimated from the data:

| Quantity | Batters | Bowlers |
|---|---|---|
| Signal SD (σ_signal) | 0.2050 runs/ball | 0.1848 runs/ball |
| Noise SD (σ_e) | 2.8454 runs/ball | 2.7812 runs/ball |
| Signal-to-Noise Ratio | 0.0720 | 0.0665 |

The SNR is very low for both groups (~0.07), which is expected in T20 cricket where outcomes are highly stochastic ball-by-ball. This has an important implication: **large samples are required before ratings become reliable.**

### Power analysis: how many deliveries are needed?

For a 90% CI width ≤ 2 × σ_signal × 100 (i.e., the CI is narrow enough to be meaningful):

| Standard | Batters | Bowlers |
|---|---|---|
| CI ≤ 2× signal SD (minimal precision) | ~130 total deliveries | ~153 total deliveries |
| CI ≤ 1× signal SD (good precision) | ~521 total deliveries | ~613 total deliveries |

**Critically, these figures refer to** ***total*** **deliveries, not high-pressure deliveries.** High-pressure deliveries have slightly higher per-ball noise, requiring even more HP-specific observations.

### Minimum HP thresholds evaluated

The following HP thresholds were tested (combined with n_total ≥ 120 and n_hp_matches ≥ 5):

| HP Threshold | Bat eligible | Bowl eligible | Bat top-10 overlap w/ v0.6 | Bowl top-10 overlap w/ v0.6 |
|---|---|---|---|---|
| 10 (current v0.6) | 258 | 279 | 10/10 | 10/10 |
| 25 | 204 | 224 | 9/10 | 8/10 |
| 50 | 174 | 197 | 8/10 | 5/10 |
| 75 | 143 | 156 | 8/10 | 4/10 |
| 100 | 115 | 126 | 6/10 | 3/10 |
| 150 | 79 | 87 | 5/10 | 2/10 |
| 200 | 53 | 55 | 4/10 | 1/10 |

The dramatic divergence in bowler overlap (10/10 → 5/10 at n_hp=50) confirms that the bowler top 10 under v0.6 was disproportionately populated by low-exposure players.

### Recommended threshold: n_hp ≥ 50, n_hp_matches ≥ 5

**Justification:**
- At n_hp = 50 deliveries (with σ_e ≈ 2.78), SE of mu_hat ≈ 0.393, which after ~40% shrinkage gives posterior SE ≈ 0.235 → 90% CI half-width ≈ 15.3 R units. This is meaningful (top of distribution ~50 R units).
- Requiring ≥ 5 distinct pressure matches ensures the exposure is spread across matches, not concentrated in 1–2 exceptional innings/spells. This guards against influence of single-match outliers.
- This threshold **does not eliminate** low-exposure players from the dataset — it simply requires a minimum bar before claiming top-10 eligibility.
- The threshold was frozen **before** inspecting which players the revised top 10 would contain.

---

## Part 3: Thresholds — Scientific Justification

### Why n_hp = 10 (v0.6) is insufficient

At n_hp = 10 deliveries with σ_e = 2.78:
- SE of mu_hat ≈ 0.879 runs/ball
- 90% CI half-width (shrunk) ≈ 25+ R units
- This means a player who is truly average (mu = 0) can have a 90% CI spanning [-50, +50] purely from noise
- Empirical Bayes shrinkage reduces this but is not sufficient at this sample size

### False positive analysis

Using a simulation of a truly-average bowler (true mu = 0) in a pool of 279 bowlers:

The probability that an average bowler's observed mu_hat exceeds Mosaddek's mu_hat_raw (0.6405) with n=163 deliveries is **0.16%** — this is not vanishingly small when considering 279 bowlers.

For Ashton Agar (mu_hat_raw = 0.4052, n = 145): probability = **3.97%**. With 279 eligible bowlers, the expected number of truly average players achieving this mu_hat by chance alone is 279 × 0.0397 ≈ **11 players**. This directly means Ashton Agar's observed rating is not statistically distinguishable from noise at this exposure level.

### Coverage note

Interval coverage (whether the stated 90% CI actually contains the true parameter 90% of the time) has **not been empirically verified** in this project. The bootstrap provides match-cluster resampling, but the simplification in the shrinkage formula means intervals should be treated as approximate. This remains an unresolved limitation.

---

## Part 4: Shrinkage Assessment

### Is current shrinkage sufficient?

The empirical Bayes shrinkage factor B = σ_e² / (n × σ_signal² + σ_e²) for key flagged players:

| Player | n_del | mu_hat_raw | Shrinkage B | mu_eb (R_reg/100) |
|---|---|---|---|---|
| Mosaddek Hossain | 163 | 0.640 | 58.1% | 0.376 (R=49.6) |
| Ashton Agar | 145 | 0.405 | 61.0% | 0.223 (R=30.8) |
| Junaid Siddique | 354 | 0.298 | 39.0% | 0.205 (R=34.9) |
| Vaibhav Sooryavanshi | 564 | 0.545 | 25.5% | 0.371 (R=58.0) |
| Patrick Cummins | 247 | 0.523 | 43.8% | 0.368 (R=52.1) |
| Dinesh Karthik | 637 | 0.474 | 23.2% | 0.345 (R=45.6) |

**Key finding:** The shrinkage is correctly applied and significant (40–61% for small-sample players). However, the remaining estimated ability after shrinkage can still be large enough to produce top-10 rankings when the **observed** mu_hat_raw is exceptionally high — as it is for Mosaddek Hossain.

The bootstrap SE for Mosaddek is 50.8 R units (much higher than the analytical 18.9), reflecting high instability in the bootstrap distribution. This confirms the analytical SE understates true uncertainty for this player.

### Role of the pressure slope (theta_i)

The pressure slope theta_i is estimated from the within-player covariance of v_t with x_t. For small samples, this slope estimate is very noisy and may be capturing sampling variation rather than true pressure responsiveness. The slope is shrunk toward the role prior, which helps, but the shrinkage is computed jointly with mu — additional caution is warranted for players with n_del < 150.

---

## Part 5: Alternative Ranking Models

Three models are compared. No model is chosen based on which produces more recognisable names.

### Model A — Current (v0.6)
- Eligibility: n_total ≥ 120, n_hp ≥ 10
- Ranking: R_overall (descending)
- **Issue:** Permissive eligibility allows small-sample noise to drive rankings, particularly for bowlers.

### Model B — Revised eligibility (Recommended)
- Eligibility: n_total ≥ 120, **n_hp ≥ 50**, **n_hp_matches ≥ 5**
- Ranking: R_overall (descending)
- **Rationale:** Scientifically justified by power analysis. Requires a minimum of meaningful pressure exposure before ranking. Does not change the rating formula or shrinkage.
- **Limitation:** Still ranks by point estimate (which favours high-but-uncertain players over lower-but-reliable ones). Acknowledged explicitly.

### Model C — Conservative lower-bound ranking
- Eligibility: Same as Model B
- Ranking: R_overall_lo90 (5th percentile of bootstrap CI, descending)
- **Rationale:** Rewards players whose performance is more certain. Only ranks a player highly if even their pessimistic estimate is strong.
- **Issue:** Over-penalises genuinely exceptional small-sample performers. Rashid Khan, Wanindu Hasaranga, and Virat Kohli emerge — these are recognisable but the reason is their lower uncertainty (from larger samples), not necessarily superior performance.
- **Decision:** Disclosed as alternative. Not adopted as primary ranking because it conflates statistical certainty with actual performance.

### Comparison

| Criterion | Model A | Model B | Model C |
|---|---|---|---|
| Statistical validity | Moderate | High | High |
| Ranking stability | Lower (bowlers) | Higher | High |
| Fairness to exposure | Low | High | High |
| Interpretability | Simple | Simple | Requires explanation |
| Sensitivity to small samples | High | Lower | Low |
| Suitability for stated objective | Moderate | High | Lower |

**Model B is recommended** as the final methodology for submission.

---

## Part 6: Cricket-Specific Fairness Checks

### Batting position comparison

The model uses role-specific shrinkage (opener, top order, middle, lower). This partially adjusts for the fact that openers face powerplay bowling in predictable contexts while finishers face death bowling. **However**, the model does not explicitly model the role-specific distributions of pressure — an opener's PI distribution differs from a finisher's because they face different over-bands. This is a residual fairness concern that cannot be fully resolved without explicit over-band modelling.

**Finding:** Openers have more HP deliveries on average (larger n_hp), which gives them more reliable estimates. Finishers (lower order, 7+) tend to have fewer HP deliveries but face genuinely critical situations more often per ball faced. The shrinkage toward role means partially compensates but does not fully resolve this.

### Pace vs Spin

Spinners have a lower-volume role in T20I than pace bowlers (fewer powerplay overs, bowl in middle overs). This means spin bowlers systematically have fewer HP deliveries than pace bowlers with comparable total deliveries, making spin bowler rankings more uncertain on average. The revised eligibility threshold (n_hp ≥ 50) partially mitigates this but does not eliminate the structural difference.

**Finding:** Under Model B, 7/10 of the revised bowler top 10 are pace bowlers. This likely reflects the structural opportunity advantage for pace bowlers rather than a systematic model bias, but the distinction cannot be fully verified with available data.

### IPL vs T20I

The model pools IPL and T20I performance using the cross-competition transfer assumption (A5), justified by 86 dual-competition batters connecting the two pools. However, the pressure distributions differ: IPL matches tend to have higher leverages in death overs due to higher run-rates and tighter finishes. T20I matches can have lower overall leverages. The leverage percentile is computed within-competition, which should address this, but the shrinkage prior is estimated from the pooled distribution. This is a residual source of non-comparability.

---

## Part 7: Flagged Player Analysis

See `METHODOLOGY_DECISION_LOG.md` for full per-player analysis. Summary:

| Player | Concern | Explanation | Remains in top 10 (B)? |
|---|---|---|---|
| Mosaddek Hossain | 163 deliveries, reliability 0.452 | mu_hat_raw=0.64 survives 58% shrinkage but bootstrap SE=50.8. Not meaningfully distinguishable from noise at this exposure. | ❌ Eliminated by n_hp<50 |
| Ashton Agar | 145 deliveries, 2 HP matches | P(observe mu_hat by chance)=4%. Plausible noise. | ❌ Eliminated by n_hp<50, matches<5 |
| Junaid Siddique | 37 HP deliveries | Strong across 14 matches — the match diversity is genuine, but 37 HP deliveries is insufficient. | ❌ Eliminated by n_hp<50 |
| Vaibhav Sooryavanshi | 564 total, 180 HP, 19 matches | Genuinely large and consistent exposure. Rating survives all threshold checks. Wide CI but model output is real. | ✅ Rank #1 |
| Patrick Cummins | 247 total, 28 HP, 3 HP matches | Very few HP deliveries (28) across only 3 HP matches. Bootstrap SE=41.5. | ❌ Eliminated by n_hp<50 |
| Dinesh Karthik | 637 total, 49 HP, 11 matches | 49 HP deliveries is just below the revised threshold. | ❌ Marginally eliminated |

---

## Part 8: Stability Assessment

The revised Model B top-10 batters are **more stable** across wK variants (Abhishek Sharma moves dramatically but all others are stable). The bowler rankings have more instability, particularly for Akash Madhwal (rank 10 overall → rank 2 at wK=20%) and Reece Topley (rank 2 overall → rank 16 at lo90). These players should be treated as provisionally ranked.

The ranking that is **most stable** across all scenarios for bowlers is: Corbin Bosch, Josh Hazlewood, Lockie Ferguson, Haris Rauf, Jofra Archer. These 5 appear in top 10 under most reasonable specifications.

---

## Unresolved Limitations

1. **Interval coverage not empirically verified.** The bootstrap CI may not achieve 90% coverage exactly.
2. **Role-stability across seasons not tested.** Modal batting position may not reflect actual exposure distribution.
3. **Opposition quality not modelled.** No crossed random effects for bowling strength faced or batting strength faced.
4. **Free-hit expected value not separately modelled.** Free hits use the overall delivery-kind conditioning.
5. **IPL/T20I structural differences partially addressed** but not fully removed by percentile normalisation.
6. **Theta_i (pressure slope) estimation is noisy** for small-sample players; the slope component should be treated with additional caution.

---

## Conclusion

The core methodology is sound. The critical correction required was to the eligibility criteria, specifically for bowlers. The revised Model B framework produces a more defensible ranking that:

- Has stronger statistical backing for the minimum required evidence standard
- Shows greater stability across reasonable perturbations
- Correctly removes players whose ratings are plausibly attributable to noise
- Does not arbitrarily penalise players — it simply requires minimum evidence

The question "why should I believe this player deserves to be ranked above another player?" can now be answered more credibly: every player in the Model B top 10 has at least 50 high-pressure deliveries across at least 5 distinct pressure matches, and their estimated rating has survived empirical Bayes shrinkage of at least 20–65% toward the role mean.

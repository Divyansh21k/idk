# Independent Model Review — SupeRR Selector Season 2, Round 1

**Reviewer role:** Independent statistical reviewer, sports analytics researcher, and sceptical competition evaluator.  
**Review scope:** Full pipeline from raw data to final top-10 rankings.  
**Review basis:** Direct inspection of all source code, raw outputs, and intermediate validation files. Every finding cites a file and line reference where possible. Where a claim cannot be confirmed from code or data it is labelled **UNVERIFIED**.  
**Constraint:** This review does not modify production code, intermediate outputs, or final rankings.  
**Review date:** 2026-11-17  
**Git HEAD at time of review:** `e62bc33`

---

## Preamble

This document is a genuine critique. It is not a congratulatory summary of a sophisticated pipeline. The model contains real conceptual ambiguities, confirmed implementation bugs with critical severity, and a signal-to-noise ratio so low that the rankings cannot be treated as definitive identifications of the best pressure performers.

The pipeline is technically ambitious and demonstrates sound statistical intentions. But ambition and intention do not substitute for correctness, and the model has not been validated end-to-end in any way that would satisfy a methodologically rigorous evaluator.

---

## Section 1 — Conceptual Definition of "Pressure Performance"

### What the model actually measures

The model computes, for each player:

$$R_i = \left(\hat{\mu}_i + \hat{\theta}_i \times 0.40\right) \times 100$$

where $\hat{\mu}_i$ is a shrunk empirical Bayes estimate of mean value-added per delivery, $\hat{\theta}_i$ is a pressure slope (marginal increase in value-added at higher PI), and 0.40 is a fixed PI centre for the slope evaluation.

This is equivalent to: **"a player's estimated value-added per delivery in a moderate-to-high-PI delivery, relative to population and role priors, shrunk towards the population mean based on sample size."**

### What the model does NOT measure

The model is frequently described as measuring "performance under pressure." This is imprecise in several ways:

1. **It does not measure performance specifically in high-pressure situations.** The HP threshold (PI ≥ 0.80) is used as an *eligibility gate* — a player must have ≥50 HP deliveries to qualify — but the actual rating $R_i$ is computed from performance across *all* pressure-eligible deliveries (PI above a lower filter). This is a critical distinction. A player could be rated highly because they performed well in moderate-PI deliveries, not necessarily in extreme-PI situations.

2. **It does not measure psychological pressure response.** Leverage L(s) measures the *mathematical sensitivity* of win probability to outcomes in a given game state. This is a property of the game, not of the player. A delivery at L(s) = 0.15 is a high-leverage delivery because the match is close and the outcome matters — but the player facing or bowling it may not perceive it as more stressful than any other delivery. Conversely, a bowler defending 6 runs off the final over when already 3 wickets down may face high psychological pressure regardless of whether L(s) = 0.15 or 0.05.

3. **It does not measure performance in clutch moments specifically.** The model uses PI as a continuous weight; it does not separately estimate a "clutch" effect (performance specifically at PI > 0.90, say). The pressure slope $\hat{\theta}_i$ estimates whether a player performs marginally better at higher PI than lower PI, but this parameter is estimated from all pressure-eligible deliveries, most of which are moderate-PI.

4. **It is not a pure batting or bowling quality measure.** The EV baseline accounts for game state, delivery type, and batter-bowler matchup type (pace/spin × hand) but does not explicitly control for opposition quality. A player who faced only weak bowling attacks in high-leverage situations could appear to have high value-added.

### Verdict on conceptual definition

The model has a defensible conceptual core — measuring value-added above a context-adjusted expected performance, weighted by situational importance — but the gap between this definition and the marketing label "pressure performer" is large enough to invite legitimate challenge. Any presentation of these rankings must be precise about what is and is not being measured.

**Severity: HIGH** — not a bug, but a communication and validity risk.

---

## Section 2 — Pressure Index and Win Probability Implementation

### 2.1 Win Probability model

**File:** `src/step3_win_probability.py`, lines 127–136.

The WP model uses one engineered feature per innings:

- **Innings 1:** `proj_margin = (runs_before + E_remaining - venue_par) / proj_std`
- **Innings 2:** `runs_advantage = (E_remaining - runs_required_before) / radv_std`

Both features depend on E_remaining from the resource table. Because E_remaining = E[runs | balls_left_bin, wickets_lost], wickets and balls are captured *implicitly* but the WP model cannot separately weight them. A team 50 runs behind needing 50 off 50 balls with 0 wickets lost and the same team needing 50 off 50 balls with 9 wickets lost are assigned the same WP, because E_remaining already incorporates the wicket loss. This is the best the single-feature model can do — but it means WP cannot distinguish between these strategically very different states.

**Calibration evidence (outputs/step3/wp_calibration.csv):**

| Decile | mean_wp | actual_win_rate | Error |
|--------|---------|-----------------|-------|
| 0 | 0.043 | 0.095 | +120% (overestimates losing probability) |
| 1 | 0.150 | 0.111 | −26% |
| 7 | 0.747 | 0.816 | −9% |
| 4–6 | ≈ correct | ≈ correct | |

The tail miscalibration is **critical** because leverage is computed from |WP_after − WP_before|. In extreme match states (decile 0 and decile 7+) the model's WP values are wrong, which means the magnitude and direction of leverage attribution is wrong for the highest-PI deliveries — precisely the deliveries that determine eligibility.

**Brier score = 0.1925** is marginal. A climatological baseline (predict the marginal win rate always) achieves a Brier score of approximately `2 × p × (1−p)` where p ≈ 0.5, giving ~0.25. The model achieves 0.1925 — a modest but not impressive improvement. A model with wickets, balls, run rate, and over explicitly as features would likely achieve 0.15–0.17 and calibrate much better at the tails.

**Finding I-02 (CRITICAL), I-03 (CRITICAL).**

### 2.2 Pressure Index construction

**File:** `src/step3_win_probability.py`, lines 350–355.

PI is computed as within-competition-class percentile rank of leverage:

```python
PI_t = legal_press['leverage'].rank(pct=True)
```

This guarantees PI is **exactly uniform U(0,1) by construction**. The practical consequences:

- PI = 0.80 is always the top-20% threshold regardless of how much actual match leverage exists in that competition class. A set of T20I group games with uniformly low leverage still produces PI = 0.80 as its threshold.
- Cross-format PI values are not interpretable in absolute terms. A PI = 0.90 in an IPL game is not equivalent to PI = 0.90 in a T20I group game.
- The model defends this design by saying it normalises for different competition contexts. That is a legitimate argument within-format, but it means the model cannot answer "who performed in genuinely high-leverage situations overall."

**Finding I-05 (HIGH).**

### 2.3 Illegal delivery PI assignment

**Decision D47:** Illegal deliveries inherit PI from the state at `legal_before = k` (the state before the illegal delivery).

This is consistent and approximately correct — a no-ball followed by a free hit is legitimately in the same game state as the preceding ball. However, it means consecutive illegals (back-to-back wides) all receive the same PI regardless of cumulative run-giving. This is a minor but known simplification.

**Finding I-11 (LOW).**

### 2.4 Leverage computation outcome lumping

**File:** `src/step3_win_probability.py`, lines 211–227. `RUNS_BY['two_three'] = 2.5` averages 2s and 3s. 3s are rare in T20 and the bias is small.

**Finding I-18 (LOW).**

---

## Section 3 — Expected Performance Baseline (EV Model)

### 3.1 Feature specification

**File:** `src/step2_expected_value.py`, full file.

The EV model predicts expected runs and wicket probability for each delivery conditioned on:
- `balls_left_bin` (over-phase proxy)
- `wickets_bin`
- `delivery_kind` (legal/wide/no-ball)
- `batter_hand` × `pace_or_spin`

**Strengths:** Delivery-kind granularity is appropriate. The batter-hand × pace-spin interaction captures the dominant matchup effect without overfitting.

**Weaknesses:**
1. No competition-class indicator — IPL and T20I deliveries are pooled despite different scoring patterns (IPL averages ~8.5 runs/over, T20I averages ~8.0–8.5). A player's value-added is measured against a pooled baseline that underestimates IPL run rates and overestimates T20I run rates.
2. No explicit batting position (wickets_bin captures innings wickets lost but not individual batter's slot, which affects expected scoring rate).
3. No opposition quality adjustment.
4. No venue effect in the EV model (only in the WP model).
5. No era/season effect.

### 3.2 In-sample bias (Critical)

**File:** `src/step2_expected_value.py`, lines 143–150.

```python
# Use full model (not cross-fitted for now; cross-fitting is the production version)
...
full_ev = ...
```

The EV model is fitted on **all deliveries** including WP-training matches, then applied to **all deliveries** including those used in training. This creates in-sample bias: a player's own performances inform the expected performance against which they are measured. The "identity-free" property claimed in the methodology documentation is violated for WP-training matches.

The magnitude of bias depends on how much any individual player dominates the training data. For a dataset with ~thousands of players this bias is small on average, but for players with large delivery counts (Suryakumar Yadav: 2663 total) or unusual performance patterns, the bias is non-negligible.

**Finding I-01 (CRITICAL).**

### 3.3 Resource table monotonicity failure

**File:** `outputs/step2/step2_validation.csv`.

```
V2_resource_mono_balls = False  *** FAIL ***
V2_resource_mono_wkts  = False  *** FAIL ***
```

The resource table c(s) = expected remaining runs given (balls_left_bin, wickets_bin) is non-monotone in both dimensions. Specifically: c(s) does not strictly decrease as balls_left decreases for some wicket bins, and does not strictly decrease as wickets_lost increases for some ball bins. This means the resource table assigns inconsistent value to game states — a wicket in some states costs *more* runs than the adjacent state implies.

Non-monotonicity is a data artefact from finite-sample estimation with sparse state cells (particularly in late-inning, high-wicket-loss states). The fix is straightforward (isotonic regression) but requires modifying production code.

**Impact:** v_bat and v_bowl are computed using c(s) differences. In non-monotone states, the direction and magnitude of value attribution can be incorrect. Death-over players with tailenders are most exposed.

**Finding I-04 (CRITICAL).**

### 3.4 Free-hit EV

The EV model assigns the same expected wicket probability to free-hit deliveries as to normal legal deliveries. On a free hit a batter cannot be dismissed (except run out). The c(s) × E[wicket] component therefore **overstates bowler expected wicket value and understates batter expected survival value** on free hits.

This is a small bias (free hits are ~2% of deliveries) but is directionally consistent: bowlers are slightly over-penalised for free-hit wicket outcomes, batters slightly under-rewarded.

**Finding I-14 (LOW).**

---

## Section 4 — Player Attribution and Fairness

### 4.1 Run-out attribution

**Decision D51:** Approved non-striker run-out handling.

**Implementation status:** Partially correct. `src/step2_expected_value.py` line 205 uses `dismissal_type == 'Run Out'` (with space) but the data contains `'RunOut'` (no space). The step2 `non_striker_runout` column is therefore always 0. However, `src/step4_player_model.py` independently re-identifies run-outs from the pressure CSV using the correct string. The net effect on ranked outputs is zero.

**Finding I-11 (MEDIUM — zero net impact).**

### 4.2 Wide and no-ball attribution

Wides: not counted as balls faced by batter (consistent with D32 ✓); bowler charged for wide runs ✓.  
No-balls: counted as ball faced by batter ✓; bowler charged ✓.  
Attribution is correct.

### 4.3 Knockout competition fairness

Players with no IPL knockout exposure (e.g. Zaman Khan: 0 KO deliveries; Haris Rauf: 0 IPL at all) have $R_{overall} = R_{reg}$ because their KO adjustment is zero by definition. This is not unfair — they simply did not play in qualifying matches — but it means the KO adjustment is not a pressure amplifier for all players equally. For players with KO exposure, the KO term adds a moderate uplift (w_K = 0.0529, so the adjustment is 5.29% of the KO rating). This is a small and defensible modification.

### 4.4 T20I specialist disadvantage

**File:** `src/step4_player_model.py`, line 246.

```python
n = max(row['n_reg'], 1)
```

Shrinkage uses regular-match delivery count only. Regular matches = IPL league + T20I non-knockout. KO matches are excluded. A player with 200 T20I deliveries (all non-KO) and 20 IPL deliveries has n_reg = 220 and is appropriately shrunk. But a player with 200 T20I deliveries and 20 IPL deliveries where the IPL appears only in the KO bucket has n_reg = 200 (T20I only), which is correct. 

**Actual concern:** If a T20I-only player appears in few IPL matches (n_reg_IPL = 0) but many T20I matches (n_reg_T20I = 150), n_reg = 150 — which is reasonable. The concern is narrower: players whose only substantial exposure is in KO matches are very rare. This issue is real but affects fewer players than initially characterised.

However: the formula `n_reg` excludes KO deliveries from the precision weight. If a player has 40 deliveries in regular matches and 60 in KO matches (n_reg = 40, n_hp = 100), the shrinkage is based only on 40 deliveries. This is a genuine inconsistency: the player qualifies as "sustained" on n_hp = 100 but their shrinkage uses only n_reg = 40.

**Finding I-07 (HIGH).**

### 4.5 Super Over and Impact Player handling

**UNVERIFIED:** Super Over exclusion from elig_pressure was not independently confirmed in the audit. Impact Player batting-role misclassification was not investigated. Both are low-probability but non-trivial risks.

**Findings I-15, I-16 (LOW — UNVERIFIED).**

---

## Section 5 — Hierarchical Model and Final Rating

### 5.1 Model structure

The hierarchical model (step4) implements:

1. **Empirical Bayes shrinkage:** $\hat{\mu}_i = \bar{v}_i \times \lambda_i + \mu_{prior} \times (1 - \lambda_i)$ where $\lambda_i = \sigma^2_{signal} / (\sigma^2_{signal} + \sigma^2_e / n_i)$.
2. **Pressure slope:** $\hat{\theta}_i$ estimated from linear interaction of PI with v_i within each player's delivery set.
3. **R_reg:** Combines shrunk mean and slope evaluated at PI = 0.40.
4. **KO adjustment:** $\kappa + \delta_i$ estimated from KO-only deliveries; $R_{overall} = R_{reg} + w_K \times (\kappa + \delta_i) \times 100$.

### 5.2 Double-counting concern resolved

Initial audit concern: KO deliveries contribute twice — once to R_reg and once to the KO term. After careful code inspection:

**R_reg is computed from reg_cats = ['IPL league', 'T20I non-knockout'].**  KO deliveries are explicitly excluded from R_reg. The KO term adds to R_overall independently. There is NO double-counting.

However: the pressure slope $\hat{\theta}_i$ is estimated from n_reg deliveries only (line 246). If a player has better data in KO matches than regular matches, the slope estimate is based on a smaller, potentially less representative subset. This is a second-order issue.

**Initial finding I-08 severity revised from HIGH to MEDIUM.**

### 5.3 KO weighting w_K

w_K = 0.0529 is the ratio of sum(leverage in IPL KO matches) to sum(leverage in all IPL matches). This is a data-derived constant, not a subjective choice. Its small value (5.3%) reflects that KO matches are a minority of total IPL leverage. This is methodologically appropriate.

**BUT:** w_K is a leverage-share proportion, not a "importance multiplier" in a normative sense. Using it assumes that the fraction of leverage in KO matches is the right weight for the KO performance adjustment. A different assumption (e.g. KO matches are twice as important per delivery) would produce a different w_K. The current choice is data-derived but not uniquely defensible.

### 5.4 Bootstrap standard errors

The model uses 500 match-cluster bootstrap resamples. Bootstrap SE > analytical SE for most players, correctly capturing match-level clustering not accounted for in the analytical formula.

**Finding I-13 (MEDIUM):** P(top10) is computed via Gaussian Monte Carlo from summary statistics rather than from actual per-draw bootstrap rankings. This assumes normality of the bootstrap distribution, which may not hold for borderline players. The fix (storing per-draw rankings) is straightforward.

---

## Section 6 — Statistical Reliability and Eligibility

### 6.1 Thresholds

The approved eligibility criteria are: n_hp ≥ 50 and n_hp_matches ≥ 5.

The validation report (Gate 1) confirms reliability at n_hp = 50 is approximately:
- Batters: 0.537–0.822 (range across top-10)
- Bowlers: 0.480–0.678 (range across top-10)

These reliability values mean the signal accounts for 48–82% of observed variance. At reliability = 0.50 the model is roughly as uncertain about player ability as it is about game noise. This is a low but disclosed threshold.

**CI half-widths at n_hp = 50 (bowlers):** approximately 36–55 R-units. For reference, the difference between rank 1 (Bosch, 37.46) and rank 10 (Madhwal, 27.78) is 9.68 R-units — well within the CI half-width of most players. **The rankings are not statistically distinguishable within the top 10.**

### 6.2 Top-10 recovery simulation

The validation simulation (Gate 2) finds top-10 recovery rate = **22.7%**. This means:

> In a simulated dataset with the same true signal-to-noise ratio as the real data, in 100 trials only 22-23 of them correctly identify all 10 true top players.

This is not a methodological failure — it reflects genuine data sparsity — but it has a stark implication: **the rankings should be treated as a probabilistic shortlist, not a definitive ordered list.** A presentation that ranks players 1–10 without prominent CI disclosure is overstating the precision of the evidence.

### 6.3 Statistical significance of bowler rankings

Three of the 10 bowler 90% CIs include zero:

| Player | 90% CI | Statistical status |
|--------|--------|-------------------|
| Shakib Al Hasan | [-0.382, 63.510] | Not significant |
| Wayne Parnell | [-8.420, 73.095] | Not significant |
| Akash Madhwal | [-28.894, 82.298] | Not significant |

Prabhsimran Singh (rank 10 batter) CI barely excludes zero: [-0.198, 57.617].

Presenting these players as "top 10 pressure performers" with equal standing to SKY (CI: [26.4, 56.0]) or Hazlewood (CI: [6.6, 56.7]) is methodologically misleading without explicit CI disclosure.

**Finding I-09 (HIGH).**

### 6.4 Corbin Bosch threshold sensitivity

Corbin Bosch (rank 1 bowler, n_hp = 99, n_hp_matches = 8) is ineligible under any threshold ≥ 100 HP deliveries. With only 8 pressure matches his bootstrap SE (22.1) substantially exceeds the analytical SE (16.7). His point estimate (37.46) is the highest of any bowler, but his CI ([9.1, 79.5]) is wide. **His rank-1 position is data-sparse and threshold-sensitive.**

This does not mean Bosch is not a good pressure performer. It means the data does not robustly support the conclusion that he is the *best* pressure bowler. He may equally well rank anywhere from 1 to beyond 10 if more data were available.

**Finding I-10 (HIGH).**

---

## Section 7 — Validation and Robustness

### 7.1 Validation tests that were run

| Test | Result | Status |
|------|--------|--------|
| EV mean-zero check | V1: PASS (1.3e-17) | ✓ |
| Resource monotonicity | V2: FAIL (both dimensions) | ✗ |
| WP Brier score | 0.1925 (marginal) | Borderline |
| WP calibration by decile | Tails miscalibrated | ✗ |
| Leverage positivity | V3: PASS (0 violations) | ✓ |
| PI missing values | V4: PASS (0 missing) | ✓ |
| w_K range | V5: PASS (0.0529) | ✓ |
| Eligibility gate | n_hp≥50, matches≥5: PASS for all ranked | ✓ |
| CI plausibility | 3/10 bowler CIs include 0 | ✗ |
| Top-10 recovery simulation | 22.7% | Low |
| Threshold sensitivity | Corbin Bosch drops at n_hp≥100 | ✗ |

### 7.2 Validation tests that are MISSING

The following tests would materially strengthen confidence in the rankings and are achievable with the existing dataset:

1. **Temporal holdout:** Train on 2022–2023, evaluate whether ranked players perform better in HP situations in 2024–2025. This is the most direct test of whether the model identifies genuine ability.
2. **Out-of-sample WP evaluation:** Reserve one IPL season for WP model calibration testing.
3. **Role-specific EV validation:** Confirm v_bat mean ≈ 0 separately for openers, top-order, middle-order, lower-order. Currently only the overall mean is validated.
4. **Opposition-quality sensitivity:** Recompute ratings weighting deliveries by opposition bowling/batting quality. Test if rankings change substantially.
5. **Cross-fitting EV test:** Compare in-sample fitted v_bat/v_bowl with leave-one-match-out equivalents for WP-training matches.
6. **Super Over exclusion audit:** Confirm Super Over deliveries are correctly handled.
7. **Impact Player role verification:** Confirm batting-role bins are correct for Impact Player substitutes.
8. **Free-hit v_bat/v_bowl spot check:** Confirm free-hit deliveries do not create systematic outliers.

**None of these tests were run.** This is a significant gap in validation. For a competition submission, the absence of temporal holdout testing is particularly concerning because it means the model has never been evaluated on out-of-sample data.

---

## Section 8 — Alternative Approaches

### Alternative A: Leverage-Weighted Runs Above Par (RAP-L)

**Description:** Compute runs above par empirically (actual runs − state mean runs) for each delivery. Weight each delivery by its leverage L(s). Sum per player and normalise by total weighted deliveries.

**Formula:** $RAP_i = \frac{\sum_t L(s_t) \times (r_t - \bar{r}_{s_t})}{\sum_t L(s_t)}$

**Advantages:** Fully non-parametric. No shrinkage, no hierarchical model, no EV model fitting. Interpretable as "runs added per unit of match importance." Completely transparent — no tuning parameters.

**Disadvantages:** No shrinkage means noisy estimates for small samples. No pressure slope — treats all HP deliveries equally regardless of within-HP variation. Does not separate knockout performance. No cross-format normalisation.

**When preferable:** When the evaluator demands maximum transparency and interpretability, or when the existing model's complexity cannot be defended without the full methodology documentation.

### Alternative B: Cross-Fitted Mixed-Effects WPA Model

**Description:** Win Probability Added (WPA) accumulated directly at player level: $WPA_i = \sum_{t: i \text{ acted}} (WP_{t+1} - WP_t)$. WP is estimated via a cross-fitted logistic model with features: balls_left, wickets_lost, runs_required, innings, competition_class, venue_par. Player effects estimated via REML mixed model with player-level random intercept (ability) and pressure slope random effect.

**Advantages:** Statistically rigorous. Cross-fitting eliminates in-sample bias. Mixed effects correctly propagate match clustering to standard errors. Direct win-probability framing is intuitive.

**Disadvantages:** More complex implementation. Requires REML or Stan. WPA is noisier than RAP because it compounds WP model errors. Cross-fitting is computationally expensive for large datasets.

**When preferable:** When statistical rigour is the highest priority and computational cost is acceptable.

### Alternative C: Bayesian Hierarchical WPA with Explicit Pressure Interaction

**Description:** A fully Bayesian hierarchical model where each player has a prior over (ability, pressure_response). Pressure is included as a continuous variable in the likelihood. Posterior distribution over player ability is estimated via MCMC (Stan/PyMC). Eligibility replaced by credible interval width — only players with 90% CI half-width < X are presented.

**Advantages:** Full uncertainty quantification. CI-based eligibility is principled. Posterior predictive checks provide built-in validation. Handles sample imbalance gracefully. Most defensible at the highest statistical standard.

**Disadvantages:** Requires significant implementation effort (~2–3 weeks). MCMC chains must converge. Output is a posterior distribution, not a point estimate — ranking becomes "expected rank" or "P(rank ≤ 10)." More difficult to communicate non-technically.

**When preferable:** If the competition requires the highest possible statistical rigour and the audience is technically sophisticated.

### Comparison summary

| Criterion | Current Model | RAP-L (A) | Mixed WPA (B) | Bayesian (C) |
|-----------|-------------|-----------|---------------|--------------|
| In-sample bias | YES (critical) | Partial | No (cross-fitted) | No |
| WP calibration | Marginal | N/A | Better | Best |
| Shrinkage | EB (correct) | None | REML (correct) | Full Bayes (correct) |
| Transparency | Medium | High | Medium | Low |
| Implementation | Done | Simple | Moderate | Complex |
| Validation | Partial | Partial | Strong | Strongest |

---

## Section 9 — Final Verdict

### Is the model conceptually well-defined?

**Mostly, with important caveats.** The model measures "value-added above context-adjusted expected performance, weighted by within-competition leverage percentile." This is a coherent definition. The critical gap is that this is not the same as "performance under psychological pressure," and the distinction is not disclosed prominently enough in the methodology documentation or presentation materials. The PI filter conflates leverage (mathematical game-state property) with pressure (psychological or situational player experience).

### Is the model statistically defensible?

**Partially.** The hierarchical Bayesian shrinkage structure is correct. The bootstrap CI methodology is sound in principle. The eligibility thresholds (n_hp ≥ 50, matches ≥ 5) were validated empirically and are reasonable floors. The CI half-widths are appropriately wide and are reported alongside point estimates.

However: (1) The EV model uses full-data fit — in-sample bias is real and unquantified. (2) The WP model is under-specified and miscalibrated at the tails. (3) The resource table fails monotonicity, introducing V-bat/v_bowl anomalies in sparse states. (4) Three bowler CIs include zero, making those rankings statistically unsupported.

### Is the implementation correct?

**Mostly, with two critical bugs.** (1) EV model uses `full_ev` (all-data fit) despite the comment explicitly noting that cross-fitting is the production version — this is an unfinished implementation. (2) Resource monotonicity fails V2 checks. The RunOut D51 fix is correctly applied in step4. Bootstrap CI computation is correct. Leverage formula is mathematically correct conditional on WP model accuracy.

### Are the rankings sufficiently reliable?

**No.** The key evidence:

- Top-10 recovery rate: 22.7% (less than 1 in 4 simulated trials recovers the true top 10)
- 3/10 bowler CIs include zero (statistically insignificant)
- Rank-1 bowler (Corbin Bosch) becomes ineligible at n_hp ≥ 100
- Rank-1 batter (Vaibhav Sooryavanshi) has only 180 HP deliveries and a wide CI [21.5, 96.3]
- Rank 10 batter CI barely excludes zero: [-0.2, 57.6]
- Mean bowler CI half-width: ~36 R-units vs inter-player spread of ~10 R-units

This level of uncertainty is not a methodological failure — it reflects the true sparsity of the data. But the rankings **cannot be presented as a definitive identification of the 10 best pressure performers.** They are the best-supported candidates given the available data, with substantial uncertainty that must be disclosed.

### Overall assessment

| Criterion | Assessment |
|-----------|-----------|
| Conceptual definition | Mostly valid; leverage ≠ psychological pressure must be disclosed |
| WP and PI implementation | Structurally sound but WP underspecified and miscalibrated at tails |
| EV baseline | Structurally sound but in-sample bias (critical unfinished implementation) |
| Player attribution | Mostly correct; RunOut fix applied correctly |
| Hierarchical model | Correct structure; shrinkage uses n_reg only (T20I specialists at modest disadvantage) |
| Eligibility criteria | Empirically validated; 50 HP deliveries is a defensible floor |
| Statistical reliability | Low; rankings are probabilistic shortlists, not definitive identifications |
| Validation coverage | Significant gaps; no temporal holdout; WP tail calibration fails |

### Actionable changes required before any further presentation or submission

1. **Disclose CI prominently** in all ranking presentations. Never present a rank without its 90% CI.
2. **Flag non-significant rankings:** Shakib, Parnell, Madhwal CIs include zero — these players should be presented with an asterisk noting the CI includes zero.
3. **Present two leaderboards:** n_hp ≥ 50 (eligible) and n_hp ≥ 100 (sustained), with Corbin Bosch's absence from the latter explicitly noted.
4. **Correct the EV cross-fitting:** Implement leave-one-match-out as already described in the step2 code comments. This is the highest-priority fix for a future version.
5. **Fix resource monotonicity:** Apply isotonic regression to enforce c(s) monotonicity along the wickets dimension.
6. **Improve WP model:** Add at least one explicit state feature (wickets_before or run_rate) and apply tail calibration correction.
7. **State clearly that leverage = win-probability sensitivity ≠ psychological pressure** in all methodology documentation and presentations.

---

*This review was conducted by independent inspection of all source code, intermediate outputs, and validation files at git HEAD `e62bc33`. No production code was modified during the review.*

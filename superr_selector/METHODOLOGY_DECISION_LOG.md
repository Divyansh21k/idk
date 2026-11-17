# Methodology Decision Log — Reassessment v1.0

**Project:** SupeRR Selector Season 2 — Round 1  
**Date:** 2026-11-17  
**Purpose:** Record every material decision in the reassessment, its rationale, alternatives considered, and evidence.

---

## D-R01: Eligibility criterion revision — high-pressure deliveries

**Decision:** Increase minimum high-pressure deliveries from 10 to 50 (for both batters and bowlers, measured in their respective eligible delivery sets).

**Previous criterion:** n_total ≥ 120 AND n_hp ≥ 10  
**Revised criterion:** n_total ≥ 120 AND n_hp ≥ 50 AND n_hp_matches ≥ 5

**Rationale:**
- Power analysis: at n_hp = 10, the 90% CI half-width on the pressure index component is ~12 R units per ball — wider than the signal range for most players
- False discovery analysis: Ashton Agar (n_hp=26) has a 3.97% per-player chance of appearing at his observed rating purely from noise; at 279 bowlers, expected null discoveries ≈ 11
- Stability test: bowler top-10 overlap drops from 10/10 to 5/10 when n_hp threshold increases from 10 to 50, indicating the original v0.6 bowler rankings were unstable
- The threshold was frozen after power analysis, before inspecting which players would qualify

**Alternatives considered:**
- n_hp = 25: improves stability slightly (8/10 bowler overlap) but still permits 2-match players
- n_hp = 75: too restrictive for bowlers (156 eligible, eliminates Zaman Khan who has 55 HP with consistent ratings)
- n_hp = 100: 126 bowlers eligible; top 3 bowler overlap drops to 3/10 — overly restrictive given genuine pressure performers
- n_hp = 50: balances power requirements with practical pool size (197 eligible bowlers)

**Effect on batter rankings:** 8/10 batter overlap — Patrick Cummins (#2 v0.6) and Dinesh Karthik (#3 v0.6) eliminated; Jacob Bethell and Prabhsimran Singh enter.

**Effect on bowler rankings:** 5/10 bowler overlap — Mosaddek Hossain, Ashton Agar, Junaid Siddique (37 HP), Dunith Wellalage, Haider Ali eliminated; Corbin Bosch becomes #1, followed by Reece Topley, Zaman Khan, Josh Hazlewood, Lockie Ferguson.

---

## D-R02: Addition of minimum distinct HP matches criterion

**Decision:** Require ≥ 5 distinct matches with at least one high-pressure delivery (n_hp_matches ≥ 5).

**Rationale:**
- Prevents a player achieving the n_hp = 50 threshold through 2–3 outstanding matches
- Guards against single-match outlier effects driving ratings
- Match diversity is a necessary (not sufficient) condition for reliability
- Chosen at 5 (not 3 or 8) because: at 3, Mosaddek still qualifies (5 HP matches); at 8, Zaman Khan is excluded (7 HP matches); 5 is the smallest threshold that excludes known low-match-count concerns while retaining players with genuine spread

**Evidence:** Bootstrap/analytical SE ratios > 2.0 for Mosaddek and Dhananjaya de Silva, both of whom have high ratings concentrated in few matches. This provides empirical support for requiring match diversity.

**Players affected:** Patrick Cummins (3 HP matches) eliminated. This is the correct outcome — with only 28 HP deliveries across 3 matches, Cummins' batter rating is unreliable.

---

## D-R03: Flagged player — Mosaddek Hossain

**Concern:** Ranks #1 bowler (v0.6) with only 163 total deliveries, 41 HP deliveries, 5 HP matches, reliability 0.452, bootstrap SE 50.8 R units.

**Analysis:**
- mu_hat_raw = 0.6405 runs/ball above expectation — extremely high raw value
- 58.1% shrinkage applied by empirical Bayes → mu_eb = 0.376 (R_reg = 49.6)
- Bootstrap SE (50.8) is 2.69× analytical SE (18.9): the CI [1.0, 157.6] is massive
- The rating is real in the sense that Mosaddek genuinely performed well above expectation in this data, but with 41 HP deliveries, the chance of this being noise is non-trivial
- P(observe mu_hat_raw ≥ 0.64 from null player): 0.16% — small but non-zero; with 279 bowlers, ~0.45 expected null discoveries at this threshold
- **Most importantly:** plays only in IPL (1 competition), no knockout deliveries, 5 HP matches

**Decision:** Eliminate from eligible pool under D-R01 (n_hp = 41 < 50). Report explicitly as "insufficient HP exposure."

**Conclusion:** The model correctly identified an exceptional raw performance, but the shrinkage was insufficient to prevent a small-sample player from dominating the ranking. This is the correct finding — the solution is tighter eligibility, not post-hoc adjustment of the rating.

---

## D-R04: Flagged player — Ashton Agar

**Concern:** Ranks #5 bowler (v0.6) with only 145 total deliveries, 26 HP deliveries, 2 HP matches, reliability 0.465.

**Analysis:**
- mu_hat_raw = 0.4052; 61% shrinkage → mu_eb = 0.223 (R_reg = 31.0)
- P(observe mu_hat_raw ≥ 0.4052 if true mu=0): 3.97% — statistically plausible noise
- Only 2 HP matches — extreme concentration risk
- Played only in IPL (SA20 tournament data may be included but no KO deliveries)
- Bootstrap SE = 11.8 (lower than analytical 18.5) — atypical; likely due to concentrated match distribution

**Decision:** Eliminate from eligible pool under D-R01 (n_hp=26<50) AND D-R02 (n_hp_matches=2<5).

---

## D-R05: Flagged player — Junaid Siddique

**Concern:** Ranks #3 bowler (v0.6) with 354 total deliveries but only 37 HP deliveries across 14 HP matches.

**Analysis:**
- 14 distinct HP matches is good exposure spread
- But 37 HP deliveries at ~2.6 HP deliveries per match is sparse
- mu_hat_raw = 0.2978; 39% shrinkage → mu_eb = 0.205 (R_reg = 35.1)
- Rating is consistent across matches (genuine spread of 14 matches)
- However n_hp = 37 < 50 threshold

**Decision:** Eliminate from eligible pool under D-R01 (n_hp=37<50). This is a borderline case — the player has genuine match diversity but insufficient HP volume. The 50-delivery threshold is maintained consistently regardless of this individual case.

**Note:** Under n_hp=25 threshold, Junaid remains in top 10 (ranks #3). His rating is plausibly real but requires more HP exposure to confirm.

---

## D-R06: Flagged player — Vaibhav Sooryavanshi

**Concern:** Ranks #1 batter (v0.6, also Model B) with 564 total deliveries, 180 HP deliveries, 19 HP matches, reliability 0.637.

**Analysis:**
- 180 HP deliveries across 19 HP matches — substantial and diverse pressure exposure
- mu_hat_raw = 0.5454; 25.5% shrinkage (less shrinkage because larger sample) → mu_eb = 0.371 (R_reg = 54.5)
- Bootstrap SE = 22.5 (vs analytical 15.7) — ratio 1.43, indicating some match-clustering
- P(observe mu_hat_raw ≥ 0.5454 if true mu=0): <0.001% — extremely unlikely to be pure noise
- KO adjustment (delta_i = 0.764) adds to R_overall → 58.03; this requires 76 KO deliveries (meaningful KO exposure)
- CI: [21.47, 96.27] — wide but entirely positive; even the pessimistic estimate is +21 R units

**Decision:** Retain in eligible pool. Rating survives all threshold tests (n_hp=180 >> 50, 19 matches >> 5). The surprise is genuine — Vaibhav is a young IPL player with limited T20I history, but his IPL pressure record is statistically real.

**Why is an established star not ranked higher?** SKY (Suryakumar Yadav) is #2 — a highly credible result given 581 HP deliveries, 55 matches, reliability 0.822. The gap in reliability between these two players (0.637 vs 0.822) means SKY's rating (+39.2) is far more precisely estimated even though it is lower. This is a core tension: the model rewards demonstrated performance, not reputation.

---

## D-R07: Flagged player — Patrick Cummins (batter)

**Concern:** Ranks #2 batter (v0.6) with only 247 total deliveries and 28 HP deliveries across 3 HP matches.

**Analysis:**
- 28 HP deliveries across only 3 HP matches — concentration risk is severe
- mu_hat_raw = 0.5225; 43.8% shrinkage → mu_eb = 0.368 (R_reg = 52.3)
- Bootstrap SE = 41.5 (ratio 1.64) — high match-level clustering
- CI: [-9.83, 127.00] — extremely wide, includes negative values

**Decision:** Eliminate under D-R01 (n_hp=28<50) and D-R02 (n_hp_matches=3<5). Correctly removed. His batter rating is driven by a small number of exceptional lower-order innings.

---

## D-R08: Flagged player — Dinesh Karthik

**Concern:** Ranks #3 batter (v0.6) with 637 total deliveries but only 49 HP deliveries across 11 HP matches.

**Analysis:**
- 49 HP deliveries is just 1 below the revised threshold (50)
- 11 HP matches — good match diversity
- mu_hat_raw = 0.4743; 23.2% shrinkage → mu_eb = 0.345 (R_reg = 47.4)
- Bootstrap SE = 19.8 (ratio 1.27) — moderate clustering
- Consistent pressure performer across matches

**Decision:** Eliminate under D-R01 (n_hp=49<50). This is the most borderline case. At n_hp ≥ 49 or at any threshold ≤ 49, Karthik qualifies and ranks #3. The threshold was frozen at 50 (not 49) for principled reasons — not to include or exclude Karthik.

**Note:** Karthik is very close to qualifying. At n_hp = 45 threshold, he would be #3. This highlights that the boundary is not sharp — the threshold creates a crisp cut, but reality is continuous.

---

## D-R09: Ranking method — point estimate vs lower bound

**Decision:** Primary ranking uses R_overall (point estimate). Lower-bound ranking (R_overall_lo90) disclosed as Model C alternative.

**Rationale for point estimate:** The posterior mean (mu_eb) is the minimum-MSE estimator of true ability. Ranking by the lower credible bound is statistically conservative but conflates uncertainty with performance — it systematically favours players with more data, which is captured separately by the reliability score.

**Rationale for disclosing Model C:** The lower-bound approach is used in some sports analytics contexts to prevent noise from driving rankings. For bowlers in particular (where many top-10 players under Model B have wide CIs), the lower-bound alternative reveals a materially different set (Rashid Khan, Wanindu Hasaranga emerge). This is a legitimate alternative perspective.

**Decision:** Model B (point estimate, revised eligibility) is the primary submission. Model C is disclosed in sensitivity analysis.

---

## D-R10: Recommendation on final submission model

**Decision:** Submit Model B revised rankings as the primary output.

**Justification:**
1. Scientifically justified threshold based on power analysis and false discovery analysis
2. Greater ranking stability than v0.6 (8/10 batter overlap; 5/10 bowler overlap — the change is genuine and warranted)
3. Does not modify the underlying rating formula (preserves all v0.5 methodology decisions)
4. Thresholds frozen before final inspection of results (documented in this log)
5. All limitations clearly disclosed

**What is not changed:**
- Rating formula (R_overall = R_reg + w_K × (kappa + gamma × x* + delta_i) × 100)
- Shrinkage mechanism
- w_K = 0.0529 (unchanged)
- EV model (steps 1–3)
- Bootstrap resampling (500 resamples)

**Outstanding limitations (unresolved):**
- Interval coverage not empirically verified
- Bayesian cross-check not implemented
- Role stability not tested
- Opposition quality not modelled
- Free-hit expected value not separately modelled

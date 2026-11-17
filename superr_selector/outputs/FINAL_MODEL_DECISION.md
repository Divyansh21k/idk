# Final Model Decision Memo — SupeRR Selector Season 2 Round 1

**Date:** 2026-11-17
**Decision:** Adopt **Model B** as the primary submitted methodology.

---

## Decision Summary

We adopt **Model B** (n_hp ≥ 50, n_hp_matches ≥ 5, n_total ≥ 120) for the final submission.

### Rationale

**Against Model A** (n_hp ≥ 10):
- Under Model A, several bowlers with 10–49 HP deliveries appeared in the top 10.
- For bowlers (σ_e ≈ 2.87), 10 deliveries gives SE ≈ 0.91 in raw units, or ≈ 91 R-units. This is larger than any plausible true ability signal.
- The top-10 bowler overlap between Model A and Model B is only 5/10, confirming Model A rankings are substantially noise-driven.
- Specifically, Mosaddek Hossain (41 HP), Ashton Agar (26 HP), Junaid Siddique (37 HP), Dunith Wellalage (36 HP) and Haider Ali (10 HP) all appeared in Model A's top 10. None meet the Model B threshold.

**Against Model C** (n_hp ≥ 75):
- Model C is more restrictive without a proportionate gain in statistical reliability at the top of the rankings.
- It eliminates players with genuine and meaningful pressure exposure in a data-limited T20 context.
- Top-10 overlap B↔C is 7/10 bowlers (batters: 10/10), indicating the rankings are broadly consistent, so the additional restriction provides marginal benefit.

**For Model B:**
- Reliability at n_hp = 50 is ≈ 0.48–0.52, the signal-to-noise inflection point.
- 90% CI half-widths are ≈ 18–22 R-units at n_hp = 50 — wide but defensible for a T20 pressure analysis with high delivery-level noise.
- Top-10 membership is stable across w_K variants (all 4 variants produce 8/10 batter overlap, 8/10 bowler overlap or better).
- The thresholds were frozen and justified before examining the final ranking output.

---

## Final Pool Sizes

| Category | Model A | Model B | Model C |
|----------|---------|---------|---------|
| Eligible batters | 258 | 174 | 138 |
| Eligible bowlers | 279 | 197 | 154 |

---

## Final Top-10 Rankings (Model B)

**Batters:**
1. Vaibhav Sooryavanshi (R_overall=58.03, n_hp=180, P_top10=0.821)
2. Suryakumar Yadav (R_overall=39.24, n_hp=581, P_top10=0.578)
3. Matthew Wade (R_overall=38.40, n_hp=126, P_top10=0.554)
4. Ryan Rickelton (R_overall=33.77, n_hp=278, P_top10=0.414)
5. Rahul Tewatia (R_overall=31.66, n_hp=92, P_top10=0.362)
6. Yashasvi Jaiswal (R_overall=30.86, n_hp=578, P_top10=0.300)
7. Abhishek Sharma (R_overall=30.75, n_hp=525, P_top10=0.345)
8. Andre Russell (R_overall=29.22, n_hp=76, P_top10=0.350)
9. Jacob Bethell (R_overall=29.07, n_hp=133, P_top10=0.356)
10. Prabhsimran Singh (R_overall=28.02, n_hp=339, P_top10=0.289)

**Bowlers:**
1. Corbin Bosch (R_overall=37.46, n_hp=99, P_top10=0.466)
2. Reece Topley (R_overall=33.04, n_hp=117, P_top10=0.365)
3. Zaman Khan (R_overall=30.36, n_hp=55, P_top10=0.336)
4. Josh Hazlewood (R_overall=30.23, n_hp=280, P_top10=0.279)
5. Lockie Ferguson (R_overall=30.02, n_hp=195, P_top10=0.290)
6. Wayne Parnell (R_overall=29.61, n_hp=71, P_top10=0.376)
7. Jofra Archer (R_overall=29.11, n_hp=276, P_top10=0.269)
8. Haris Rauf (R_overall=29.11, n_hp=235, P_top10=0.210)
9. Shakib Al Hasan (R_overall=28.64, n_hp=84, P_top10=0.315)
10. Akash Madhwal (R_overall=27.78, n_hp=58, P_top10=0.353)

---

## Key Disclosures

1. Rankings reflect value-added above expected performance in high-pressure contexts, not overall batting/bowling quality.
2. Confidence intervals are wide (20–80 R-units) because T20 pressure deliveries are noisy and players accumulate them slowly.
3. Several top-10 players (particularly those ranked 7–10) have CIs that may include zero, meaning we cannot rule out that their true effect is zero or negative. Rankings represent best estimates, not statistical certainties.
4. The n_hp = 50 threshold was chosen empirically based on reliability analysis, not to include or exclude specific players.
5. Players near the cutoff (Cummins: 28 HP, Karthik: 49 HP) are excluded on procedural grounds. They are not characterised as substantially worse; they simply have insufficient data for defensible inference.

---

*Signed off by: SupeRR Selector Season 2 Project Team*
*All analysis uses organiser-provided CSV files only. No external data introduced.*

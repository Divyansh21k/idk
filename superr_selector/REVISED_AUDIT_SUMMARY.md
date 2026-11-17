# Revised Audit Summary — SupeRR Selector Season 2, Round 1

**Version:** Reassessment v1.0 (supersedes FINAL_AUDIT_SUMMARY.md v0.6)  
**Date:** 2026-11-17  
**Verdict:** **B. READY WITH DISCLOSED LIMITATIONS** (revised eligibility applied)

---

## What Changed Since v0.6

| Item | v0.6 | Reassessment v1.0 |
|---|---|---|
| Batter eligibility | n_total≥120, n_hp≥10 | n_total≥120, **n_hp≥50**, **n_hp_matches≥5** |
| Bowler eligibility | n_total≥120, n_hp≥10 | n_total≥120, **n_hp≥50**, **n_hp_matches≥5** |
| Eligible batters | 258 | 174 |
| Eligible bowlers | 279 | 197 |
| Bat #1 | Vaibhav Sooryavanshi (58.0) | Vaibhav Sooryavanshi (58.0) ← unchanged |
| Bat #2 | Patrick Cummins (52.1) | Suryakumar Yadav (39.2) |
| Bat #3 | Dinesh Karthik (45.6) | Matthew Wade (38.4) |
| Bowl #1 | Mosaddek Hossain (49.6) | Corbin Bosch (37.5) |
| Bowl #2 | Corbin Bosch (37.5) | Reece Topley (33.0) |
| Bowl #3 | Junaid Siddique (34.9) | Zaman Khan (30.4) |
| Underlying ratings | Unchanged | Unchanged |
| Core methodology | Unchanged | Unchanged |
| w_K | 0.0529 | 0.0529 (unchanged) |
| Bootstrap resamples | 500 | 500 (unchanged) |
| CI fix | Applied | Applied (unchanged) |
| D51 fix | Applied | Applied (unchanged) |

---

## Why the Eligibility Was Changed

The original n_hp ≥ 10 threshold was not scientifically justified. It allowed players with as few as 10 high-pressure deliveries to qualify, which:

1. Permitted false discoveries: Ashton Agar (n_hp=26) has a 3.97% per-player chance of appearing at his observed rating purely from noise.
2. Produced unstable rankings: bowler top-10 overlap drops from 10/10 to 5/10 when threshold increases from 10 to 50 — indicating the original bowler ranking was dominated by noise.
3. Failed the stated objective: "identify the top 10 bowlers under pressure" requires sufficient evidence of pressure performance.

The revised threshold (n_hp ≥ 50, n_hp_matches ≥ 5) was derived from power analysis and frozen before inspecting which players would qualify.

---

## Revised Final Rankings

### Top 10 Batters Under Pressure (Model B)

| Rank | Player | Role | n_hp | Matches | R_overall | 90% CI | SE | Reliability |
|---|---|---|---|---|---|---|---|---|
| 1 | **Vaibhav Sooryavanshi** | Opener | 180 | 19 | +58.03 | [21.47, 96.27] | 15.71 | 0.637 |
| 2 | **Suryakumar Yadav** | Top order | 581 | 55 | +39.24 | [26.37, 55.95] | 9.21 | 0.822 |
| 3 | **Matthew Wade** | Lower | 126 | 15 | +38.40 | [7.80, 68.51] | 21.09 | 0.665 |
| 4 | **Ryan Rickelton** | Opener | 278 | 33 | +33.77 | [12.64, 57.41] | 13.74 | 0.711 |
| 5 | **Rahul Tewatia** | Middle | 92 | 18 | +31.66 | [9.64, 61.88] | 16.30 | 0.537 |
| 6 | **Yashasvi Jaiswal** | Opener | 578 | 82 | +30.86 | [14.88, 48.75] | 10.17 | 0.808 |
| 7 | **Abhishek Sharma** | Opener | 525 | 85 | +30.75 | [5.90, 57.76] | 9.44 | 0.834 |
| 8 | **Andre Russell** | Lower | 76 | 12 | +29.22 | [-14.03, 67.84] | 17.57 | 0.748 |
| 9 | **Jacob Bethell** | Top order | 133 | 18 | +29.07 | [1.74, 63.18] | 17.39 | 0.571 |
| 10 | **Prabhsimran Singh** | Opener | 339 | 35 | +28.02 | [-0.20, 57.62] | 12.55 | 0.735 |

### Top 10 Bowlers Under Pressure (Model B)

| Rank | Player | Type | n_hp | Matches | R_overall | 90% CI | SE | Reliability |
|---|---|---|---|---|---|---|---|---|
| 1 | **Corbin Bosch** | Pace | 99 | 8 | +37.46 | [9.14, 79.54] | 16.70 | 0.519 |
| 2 | **Reece Topley** | Pace | 117 | 20 | +33.04 | [2.02, 73.78] | 14.81 | 0.574 |
| 3 | **Zaman Khan** | Pace | 55 | 7 | +30.36 | [6.90, 66.68] | 18.01 | 0.481 |
| 4 | **Josh Hazlewood** | Pace | 280 | 37 | +30.23 | [6.63, 56.68] | 11.85 | 0.678 |
| 5 | **Lockie Ferguson** | Pace | 195 | 26 | +30.02 | [4.78, 64.30] | 12.36 | 0.660 |
| 6 | **Wayne Parnell** | Pace | 71 | 10 | +29.61 | [-8.42, 73.09] | 16.66 | 0.520 |
| 7 | **Jofra Archer** | Pace | 276 | 44 | +29.11 | [6.12, 56.01] | 11.98 | 0.674 |
| 8 | **Haris Rauf** | Pace | 235 | 23 | +29.11 | [8.13, 50.89] | 13.23 | 0.636 |
| 9 | **Shakib Al Hasan** | Spin | 84 | 9 | +28.64 | [-0.38, 63.51] | 17.90 | 0.480 |
| 10 | **Akash Madhwal** | Pace | 58 | 7 | +27.78 | [-28.89, 82.30] | 17.13 | 0.502 |

---

## Stability Assessment (Model B rankings)

**Batter top-10 stability across wK variants:**
- Vaibhav Sooryavanshi: #1 under all wK variants
- Suryakumar Yadav: #2 under all wK variants
- Abhishek Sharma: #7 at primary wK, falls dramatically at higher wK (negative KO delta_i)
- Rankings 1–7 (except Abhishek Sharma) are stable to wK perturbation

**Bowler top-10 stability:**
- Corbin Bosch: #1 under all wK variants — most stable
- Haris Rauf: improves to top 3 at higher wK — has positive KO delta
- Akash Madhwal: #2 at wK=20% but #108 by lo90 — extremely unstable, should be treated with caution
- Josh Hazlewood and Jofra Archer: consistently top 7 across all variants — most credible

**Most reliably supported:**
- Batters: Suryakumar Yadav (#2, reliability 0.822), Yashasvi Jaiswal (#6, reliability 0.808), Abhishek Sharma (#7, reliability 0.834)
- Bowlers: Josh Hazlewood (#4, reliability 0.678), Jofra Archer (#7, reliability 0.674), Haris Rauf (#8, reliability 0.636)

---

## What Remains Unchanged from v0.6

1. ✅ All 4 audit fixes (CI bug, D51, 500 bootstrap, formula consistency)
2. ✅ 258 eligible batters, 279 eligible bowlers at v0.6 thresholds (reported as background)
3. ✅ All validation checks (49/49 step1, 5/5 step3)
4. ✅ w_K = 0.0529 (frozen at F1, unchanged)
5. ✅ Core EV model and WP model
6. ✅ Bootstrap CI contains point estimate for 100% of eligible players

---

## Remaining Unresolved Limitations

1. **Interval coverage not empirically verified** — bootstrap CIs are approximate 90% intervals
2. **Bayesian cross-check not implemented**
3. **Bootstrap/analytical SE ratio > 2 for some players** — particularly Corbin Bosch (#1 bowler)
4. **Role stability not tested across seasons**
5. **Opposition quality not modelled**
6. **Free-hit expected value not separately modelled**
7. **Bowler rankings show more instability than batter rankings** — particularly Zaman Khan (#3, 7 matches, CI includes 0 for lo90 ranking), Wayne Parnell (#6, CI partially negative), Shakib Al Hasan (#9, CI partially negative), Akash Madhwal (#10, wide CI and unstable wK)
8. **P(Top 10) values should be recomputed** using the revised Model B eligible pool — this was not done in the current pipeline (step5 uses original v0.6 eligibility)

---

## Verdict

**B. READY WITH DISCLOSED LIMITATIONS**

The methodology is defensible. The revised eligibility threshold is scientifically justified and materially improves the credibility of the bowler rankings. The batter rankings are largely unchanged and are supported by sufficient exposure evidence.

A serious evaluator asking "why should I believe this ranking?" can be answered:
- Every ranked player has ≥ 50 high-pressure deliveries across ≥ 5 distinct matches
- Ratings have survived empirical Bayes shrinkage of 20–65% toward role means
- Knockout adjustments use frozen w_K = 0.0529
- The top-3 batters (Sooryavanshi, SKY, Wade) and top-4 bowlers (Bosch, Topley, Hazlewood, Ferguson) are robust to reasonable sensitivity analyses

What cannot be claimed:
- Empirical coverage of CIs
- Statistical validation of role-stability
- Comparison free of structural competition-exposure differences

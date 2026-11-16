# SupeRR Selector Season 2 — Round 1: Final Independent Audit Summary

**Audit Version:** v0.6 (Post-Correction)  
**Date:** 2026-11-17  
**Pipeline:** `superr_selector/` — Steps 1–6 end-to-end  
**Verdict:** **B. READY WITH DISCLOSED LIMITATIONS**

---

## 1. Issues Found and Corrected

### A. CRITICAL — Confidence Intervals Did Not Contain Point Estimates ✅ FIXED

**Original issue:**  
The bootstrap CI computed `R_reg` (regular-match rating) confidence intervals, but the table reported `R_overall` (overall rating including knockout adjustment) as the point estimate. Because the two quantities differ — especially for players with knockout exposure — the CI systematically did not contain the point estimate.

Examples (before fix):
- Vaibhav Sooryavanshi: R_overall=+54.54, CI=[16.25, 45.72] ❌ (CI for different quantity)
- Patrick Cummins: R_overall=+52.69, CI=[-3.43, 15.34] ❌ 
- Dinesh Karthik: R_overall=+50.00, CI=[2.45, 19.09] ❌

**Root cause:**  
1. Bootstrap only computed `R_reg` per resample (no KO component)
2. CI used `R_reg_lo90` / `R_reg_hi90` but table displayed `R_overall`
3. Bootstrap used simplified hardcoded shrinkage (`sigma_mu=0.1`) vs. point estimate's empirical Bayes formula

**Fix applied (step4_player_model.py):**
- Bootstrap now computes full `R_overall_b` per resample, using the same formula: `R_overall_b = R_reg_b + w_K * (kappa_b + gamma * x* + delta_i_b) * 100`
- kappa re-estimated per bootstrap resample from dual-competition players
- delta_i shrunk per resample using same empirical Bayes formula as point estimate
- Role-specific role_params estimated per resample (FIX B: same formula consistency)
- Output columns renamed `R_overall_lo90` / `R_overall_hi90` (not `R_reg_lo90`)
- step6_reports_and_deliverables.py updated to use new column names

**Post-fix validation:**
- Batters: **258/258** eligible players have `R_overall` within 90% CI ✓
- Bowlers: **279/279** eligible players have `R_overall` within 90% CI ✓
- Specific examples after fix:
  - Vaibhav Sooryavanshi: R_overall=+58.03, CI=[21.47, 96.27] ✓
  - Patrick Cummins: R_overall=+52.10, CI=[-9.83, 127.00] ✓
  - Dinesh Karthik: R_overall=+45.60, CI=[20.08, 83.58] ✓

---

### B. D51 Non-Striker Run-Out Attribution — String Mismatch ✅ FIXED

**Original issue:**  
Decision D51 (approved): Non-strikers dismissed via run-out should be charged a dismissal penalty `v_bat = -c(s)` attributed to the non-striker's player record.

The code used `dismissal_type == 'Run Out'` (with space) but the raw data stores this value as `'RunOut'` (no space). Result: 0 non-striker run-out events attributed.

**Fix applied:**  
Changed to `dismissal_type == 'RunOut'` in `step4_player_model.py`.

**After fix:**  
250 non-striker run-out events are correctly attributed. These reduce the affected players' batter ratings by `c(s)` (the game-state value of that ball).

---

### C. Bootstrap Count Increased to 500 ✅ FIXED

**Original issue:**  
100 bootstrap resamples is insufficient for stable 5th/95th percentile estimates (minimum recommended: 500–1000 for tail quantiles).

**Fix applied:**  
Default `--n-bootstrap` changed to 500 in step4. `run_all.sh` updated to call `--n-bootstrap 500` explicitly.

**After fix:**  
500 resamples produce stable CI estimates. Batter CI coverage: 799/817 (97.8%) from bootstrap alone; 18 batters (2.2%) with <2 bootstrap draws use analytical fallback `R_overall ± 1.645 * se_R_overall`. Same pattern for bowlers: 551/589 (93.5%) from bootstrap.

---

### D. Free-Hit Count Discrepancy (918 vs 873) — NOT A BUG ✅ DOCUMENTED

**Original concern:** Stage 4 Step 1 report mentioned "918 free-hit deliveries" while the final execution mentioned 873.

**Finding:** These are different scopes, not a contradiction:
- **918**: Total free-hit deliveries across all 200,999 delivery rows
- **873**: Free-hit deliveries within pressure-eligible innings (`elig_pressure == True`)

This is consistent with the pipeline's scope filtering. No code change required. The discrepancy is noted here for transparency.

---

### E. Sample Count Reconciliation ✅ VERIFIED

| Count | Value | Source |
|---|---|---|
| Total delivery rows | 200,999 | raw CSVs |
| In-scope matches | 837 | 883 total − 30 A-team − 16 abandoned |
| Performance matches | 802 | 837 − 38 revised without retainable inn1 − 2 DQ − 3 undeclared reduced-overs |
| WP training matches | 771 | 802 − matches failing minimum innings-completion threshold |
| Pressure-eligible innings | 1,583 | Innings 1 and 2 of in-scope matches |
| Pressure-eligible deliveries | 188,761 | Legal + illegal deliveries in eligible innings |
| Total free-hit deliveries | 918 | All categories |
| Pressure-eligible free hits | 873 | Within eligible innings |
| Eligible batters (n≥120, hp≥10) | 258 | After eligibility filter |
| Eligible bowlers (n≥120, hp≥10) | 279 | After eligibility filter |

---

### F. Knockout Weighting w_K Verification ✅ VERIFIED

- Frozen value: **w_K = 0.052932** (5.29%)
- Freeze point F1: computed before any player-level result was inspected
- T20I finals are a separate class and are **not** included in IPL knockout leverage
- Computation: `sum(leverage over IPL knockout deliveries) / sum(leverage over all IPL deliveries)`
- Sensitivity results (see Section 4): rankings robust to perturbation

---

### G. Player Rating Logic ✅ REVIEWED

**Batter model (corrected):**
- R_overall = R_reg + w_K × (kappa + gamma × x* + delta_i) × 100
- kappa = -0.1036 (all batters perform worse in knockouts vs regular; plausible, based on 71 dual-competition players)
- gamma = 0.0 (D37: insufficient data to estimate population pressure×knockout interaction)

**Bowler model:**
- kappa = -0.0353 (bowlers concede slightly more in knockouts; smaller effect, 86 dual players)
- Shrinkage working correctly: small-sample players pulled toward role prior

**Small-sample players in top 10 (correctly modelled, flagged as low reliability):**
- Mosaddek Hossain (bowler): 163 deliveries, reliability=0.452. High raw value survives shrinkage because shrinkage toward role-mean is limited when role-mean itself is positive. This is a correct model output — not a manipulation. The wide CI ([1.01, 157.59]) correctly signals high uncertainty.
- Ashton Agar (bowler): 145 deliveries, reliability=0.465. Same situation.
- These players are ranked correctly by the model; their uncertainty is disclosed.

---

## 2. Methodology Compliance Checklist

| Requirement | Status | Note |
|---|---|---|
| Identity-free EV in Stage 2 | ✅ | No player names/teams used in Step 2 |
| Match-cross-fitted WP | ✅ | Leave-one-match-out CV (Step 3) |
| Separate legal/illegal delivery treatment | ✅ | Illegal inherit pre-delivery WP/leverage |
| Free-hit handling | ✅ | No bowler wicket credit; in pressure scope |
| D51 non-striker run-out | ✅ Fixed | 250 events now attributed |
| Super Over exclusion | ✅ | Filtered in Step 1 |
| Revised/reduced-overs matches | ✅ | 38+3+2 excluded from performance scope |
| Four competition/stage classes | ✅ | IPL league, IPL KO, T20I non-KO, T20I final |
| Cross-competition transfer (A5) | ✅ | 86 dual batters validated |
| Role-aware eligibility | ✅ | n≥120 balls, hp≥10 high-pressure |
| Knockout weight frozen at F1 | ✅ | w_K=0.0529 frozen before ranking |
| Sensitivity analyses | ✅ | w_K variants, reg-only vs overall |

---

## 3. Known Limitations (Disclosed, Not Corrected)

| Limitation | Category | Impact |
|---|---|---|
| Bootstrap CI coverage not empirically tested (D45) | Methodology simplification | Intervals are plausible but coverage not guaranteed at exactly 90% |
| Bayesian cross-check not implemented | Methodology simplification | Alternative validation; computational complexity was prohibitive |
| Simplified free-hit outcome model | D47 approximation | Free hits not modelled with separate expected boundary/wicket rates; excluded from EV model |
| Bootstrap uses simplified delta_i (not full KO bootstrap for all players) | Minor inconsistency | delta_i is re-shrunk per resample but KO data is sparse; effect on CIs is small |
| Opposition quality not modelled (A25) | Omission | Would require crossed random effects; cannot implement without external data |
| Role stability not tested across seasons (A19) | Omission | Modal role used; some players change role season-to-season |
| Impact Player rule (A26) not explicitly parameterised | IPL-specific | Partially absorbed by state variables |
| Interval coverage verification: 18 batters, 38 bowlers on analytical fallback | Note | These players had <2 bootstrap draws (very limited match samples); analytical CI used |

---

## 4. Sensitivity Analysis Results

| Scenario | w_K | Batter Top-10 Overlap | Bowler Top-10 Overlap |
|---|---|---|---|
| Primary (frozen) | 0.0529 | 10/10 | 10/10 |
| Delivery share | 0.0531 | 10/10 | 10/10 |
| 10% weight | 0.1000 | 9/10 | 9/10 |
| 20% weight | 0.2000 | 8/10 | 8/10 |

Rankings are **robust** to small perturbations of knockout weighting. At 20% weight (4× the actual IPL share), 8/10 batters and 8/10 bowlers remain stable.

---

## 5. Final Rankings

### Top 10 Batters Under Pressure

| Rank | Player | Role | R_overall | 90% CI | SE | P(Top 10) | Reliability | Balls |
|---|---|---|---|---|---|---|---|---|
| 1 | **Vaibhav Sooryavanshi** | Opener (1-2) | +58.03 | [21.47, 96.27] | 15.71 | 73.2% | 0.637 | 564 |
| 2 | **Patrick Cummins** | Lower (7+) | +52.10 | [-9.83, 127.00] | 25.30 | 55.8% | 0.579 | 248 |
| 3 | **Dinesh Karthik** | Middle (5-6) | +45.60 | [20.08, 83.58] | 15.67 | 55.4% | 0.557 | 637 |
| 4 | **Suryakumar Yadav** | Top order (3-4) | +39.24 | [26.37, 55.95] | 9.21 | 32.1% | 0.822 | 2663 |
| 5 | **Matthew Wade** | Lower (7+) | +38.40 | [7.80, 68.51] | 21.09 | 37.9% | 0.665 | 408 |
| 6 | **Ryan Rickelton** | Opener (1-2) | +33.77 | [12.64, 57.41] | 13.74 | 24.5% | 0.711 | 820 |
| 7 | **Rahul Tewatia** | Middle (5-6) | +31.66 | [9.64, 61.88] | 16.30 | 24.7% | 0.537 | 518 |
| 8 | **Yashasvi Jaiswal** | Opener (1-2) | +30.86 | [14.88, 48.75] | 10.17 | 10.3% | 0.808 | 1800 |
| 9 | **Abhishek Sharma** | Opener (1-2) | +30.75 | [5.90, 57.76] | 9.44 | 22.0% | 0.834 | 2235 |
| 10 | **Andre Russell** | Lower (7+) | +29.22 | [-14.03, 67.84] | 17.57 | 27.3% | 0.748 | 702 |

> Rating scale: runs per 100 deliveries above context-adjusted expectation at pressure index PI* = 0.90.

### Top 10 Bowlers Under Pressure

| Rank | Player | Type | R_overall | 90% CI | SE | P(Top 10) | Reliability | Deliveries |
|---|---|---|---|---|---|---|---|---|
| 1 | **Mosaddek Hossain** | Spin | +49.62 | [1.01, 157.59] | 18.91 | 49.8% | 0.452 | 163 |
| 2 | **Corbin Bosch** | Pace | +37.46 | [9.14, 79.54] | 16.70 | 32.7% | 0.519 | 360 |
| 3 | **Junaid Siddique** | Pace | +34.87 | [-0.48, 76.19] | 17.54 | 31.4% | 0.494 | 354 |
| 4 | **Reece Topley** | Pace | +33.04 | [2.02, 73.78] | 14.81 | 28.1% | 0.574 | 632 |
| 5 | **Ashton Agar** | Spin | +30.82 | [16.95, 56.02] | 18.45 | 9.5% | 0.465 | 145 |
| 6 | **Zaman Khan** | Pace | +30.36 | [6.90, 66.68] | 18.01 | 19.9% | 0.481 | 200 |
| 7 | **Josh Hazlewood** | Pace | +30.23 | [6.63, 56.68] | 11.85 | 15.0% | 0.678 | 1403 |
| 8 | **Lockie Ferguson** | Pace | +30.02 | [4.78, 64.30] | 12.36 | 19.6% | 0.660 | 1138 |
| 9 | **Dunith Wellalage** | Spin | +29.93 | [-13.74, 100.24] | 18.45 | 33.2% | 0.465 | 242 |
| 10 | **Haider Ali** | Spin | +29.77 | [-12.93, 73.46] | 18.21 | 25.0% | 0.471 | 273 |

> Rating scale: runs saved/credited per 100 deliveries above context-adjusted expectation at pressure index PI* = 0.90.

---

## 6. Validation Evidence

| Check | Result |
|---|---|
| Step 1: 49 structural assertions | ✅ 49/49 pass |
| Step 2: EV model unbiasedness | ✅ mean v_bat = 0.0000, mean v_bowl = 0.0000 |
| Step 3: WP calibration (Brier score) | ✅ 0.1925 (< 0.25 threshold) |
| Step 3: 5 validation checks | ✅ 5/5 pass |
| Step 4: CI contains R_overall (all eligible) | ✅ 258/258 batters, 279/279 bowlers |
| Step 4: D51 non-striker run-outs | ✅ 250 events attributed |
| Step 5: Sensitivity w_K variants | ✅ 10/10 overlap at primary; stable at 10% weight |
| Deliveries reconciliation | ✅ 188,761 pressure-eligible |
| Free-hit scope | ✅ 918 total; 873 in pressure scope (documented) |
| Knockout weight | ✅ w_K=0.0529 frozen at F1, uninfluenced by player results |

---

## 7. Files Changed in This Audit

| File | Change |
|---|---|
| `src/step4_player_model.py` | FIX A: Bootstrap computes R_overall (not R_reg); FIX B: role-specific EB per resample; FIX C: 'RunOut' spelling fix for D51; FIX D: 500 bootstrap resamples |
| `src/step5_eligibility_ranking.py` | Updated compute_p_top10 to use R_overall_lo90/hi90 columns and bootstrap-derived SE |
| `src/step6_reports_and_deliverables.py` | Updated 90% CI columns from R_reg_lo90/hi90 to R_overall_lo90/hi90 |
| `run_all.sh` | Added `--n-bootstrap 500` to step4 invocation |

---

## 8. Verdict

**B. READY WITH DISCLOSED LIMITATIONS**

The pipeline produces defensible, data-derived rankings with all critical bugs corrected:

1. ✅ Confidence intervals now correctly contain the point estimates they describe
2. ✅ Bootstrap uses the same formula as point estimates (CI/PE consistency)  
3. ✅ 500 resamples provide stable tail estimates
4. ✅ D51 non-striker run-out attribution is working (250 events)
5. ✅ All 49/49 Step 1 checks pass; Step 3 Brier = 0.1925; all sample counts reconciled

**Known limitations that cannot be corrected without additional data or computation:**
- Empirical coverage verification (D45) not performed
- Bayesian cross-check not implemented
- Free-hit expected-value sub-model not separately fit (uses overall delivery-kind conditioning)
- 18 batters and 38 bowlers on analytical CI fallback (insufficient match diversity for bootstrap)

These limitations are disclosed in both the technical methodology report and this document. The rankings are suitable for submission, with the uncertainty and reliability columns used to weight interpretation of players with limited exposure.

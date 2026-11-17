# Validation Plan — SupeRR Selector Season 2, Round 1

This document describes a structured validation plan for the existing pipeline. Tests are ordered by priority. Each test specifies: what it validates, how to run it with existing data, success criteria, and what action follows if it fails.

---

## Validation Status Overview

| Test ID | Category | Status | Priority |
|---------|----------|--------|----------|
| VT-01 | EV model zero-mean | PASS (run in audit) | — |
| VT-02 | Resource monotonicity | **FAIL** (run in audit) | Critical |
| VT-03 | WP Brier score | Borderline pass (0.1925) | High |
| VT-04 | WP calibration by decile | **FAIL** at tails | Critical |
| VT-05 | Leverage positivity | PASS | — |
| VT-06 | PI missing values | PASS | — |
| VT-07 | w_K range | PASS | — |
| VT-08 | Eligibility gate | PASS for all ranked | — |
| VT-09 | CI plausibility | Partial fail (3/10 bowlers include 0) | High |
| VT-10 | Top-10 recovery simulation | 22.7% (disclosed) | High |
| VT-11 | Threshold sensitivity | Bosch drops at n_hp≥100 | Medium |
| VT-12 | Role-specific EV validation | NOT RUN | Medium |
| VT-13 | Temporal holdout | NOT RUN | High |
| VT-14 | WP cross-competition calibration | NOT RUN | Medium |
| VT-15 | EV cross-fit bias check | NOT RUN | Critical |
| VT-16 | Super Over exclusion audit | NOT RUN | Low |
| VT-17 | Impact Player role audit | NOT RUN | Low |
| VT-18 | Free-hit v_bat spot check | NOT RUN | Low |
| VT-19 | Bootstrap distribution normality | NOT RUN | Medium |
| VT-20 | Opposition-quality sensitivity | NOT RUN | Medium |

---

## Tests Available with Current Data and Pipeline

### VT-12 — Role-Specific EV Validation

**What it validates:** The EV model should produce mean v_bat ≈ 0 separately for each batting role (opener, top-order, middle-order, lower-order). If a role has systematically positive or negative mean v_bat, the EV baseline is miscalibrated for that role.

**How to run:**
```python
import pandas as pd
press = pd.read_csv('outputs/step3/pressure.csv')

role_check = press.groupby('batting_role').agg(
    n=('v_bat', 'count'),
    mean_v_bat=('v_bat', 'mean'),
    mean_v_bowl=('v_bowl', 'mean')
).reset_index()
print(role_check)
```

**Success criterion:** |mean_v_bat| < 0.05 for each batting role with n > 100 deliveries.

**Action if fail:** Investigate which role-state combinations drive the offset. Add batting_position or role indicator to EV model features.

---

### VT-15 — EV Cross-Fit Bias Check

**What it validates:** Whether the full-data EV fit introduces material in-sample bias compared to a leave-one-match-out estimate.

**How to run:**
```python
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_predict, LeaveOneGroupOut
# Load the same pipeline from step2
# ... (reproduce EV pipeline from step2.py)

press_ev = pd.read_csv('outputs/step2/ev_data.csv')  # intermediate if saved
groups = press_ev['match_id'].values

v_bat_xfit = cross_val_predict(ev_pipeline, X_bat, y_bat, groups=groups,
                                cv=LeaveOneGroupOut(), method='predict')
v_bat_full = ev_pipeline.fit(X_bat, y_bat).predict(X_bat)

bias = (v_bat_full - v_bat_xfit).mean()
print(f"Mean in-sample bias: {bias:.6f}")
print(f"Player-level bias std: {pd.Series(v_bat_full - v_bat_xfit).std():.4f}")
```

**Success criterion:** Mean bias < 0.001 (effectively zero). Player-level bias standard deviation < 0.5.

**Action if fail:** Implement cross-fitting in production step2 (Fix 1 in RECOMMENDED_METHODOLOGY.md). Expected runtime: ~30–60 minutes on full dataset.

**Note:** This requires step2 intermediate data to be preserved. If not available, the pipeline must be partially rerun.

---

### VT-16 — Super Over Exclusion Audit

**What it validates:** Super Over deliveries should not be included in pressure scoring (they have unusual game structure — 6 balls, simplified target, no powerplay).

**How to run:**
```python
import pandas as pd
bbb = pd.read_csv('data/raw/ball_by_ball.csv')
press = pd.read_csv('outputs/step3/pressure.csv')

# Identify super over deliveries
so_deliveries = bbb[bbb['super_over'] == 1]['delivery_id'] if 'super_over' in bbb.columns else None
if so_deliveries is None:
    print("WARNING: super_over column not found — UNVERIFIED")
else:
    so_in_press = press[press['delivery_id'].isin(so_deliveries)]
    print(f"Super Over deliveries in pressure CSV: {len(so_in_press)}")
    print(f"Of these with elig_pressure=1: {so_in_press['elig_pressure'].sum()}")
```

**Success criterion:** 0 Super Over deliveries with elig_pressure = 1.

**Action if fail:** Add Super Over filter to step1 eligibility gate.

---

### VT-17 — Impact Player Role Audit

**What it validates:** Impact Player substitutes in IPL should have correct batting_role assignment.

**How to run:**
```python
# Check if any top-10 batter has an unexpected role assignment
top10_batters = ['Vaibhav Sooryavanshi', 'Suryakumar Yadav', 'Matthew Wade',
                 'Ryan Rickelton', 'Rahul Tewatia', 'Yashasvi Jaiswal',
                 'Abhishek Sharma', 'Andre Russell', 'Jacob Bethell', 'Prabhsimran Singh']

press = pd.read_csv('outputs/step3/pressure.csv')
batter_roles = press[press['player_name'].isin(top10_batters)].groupby(
    ['player_name', 'batting_role', 'innings_position']
).size().reset_index(name='n')
print(batter_roles)
```

**Success criterion:** Each top-10 batter has a consistent batting_role matching their known team position.

**Action if fail:** Verify batting_order assignment in step1. Add a batting_position correction step for known Impact Player substitutes.

---

### VT-18 — Free-Hit v_bat Spot Check

**What it validates:** Free-hit deliveries should not have systematic v_bat outliers.

**How to run:**
```python
press = pd.read_csv('outputs/step3/pressure.csv')
free_hits = press[press['delivery_kind'] == 'free_hit']
print(f"Free-hit deliveries: {len(free_hits)}")
print(f"Mean v_bat (free hits): {free_hits['v_bat'].mean():.4f}")
print(f"Mean v_bat (normal legal): {press[press['delivery_kind']=='legal']['v_bat'].mean():.4f}")
print(f"Free-hit dismissals (should be ~0): {free_hits['is_wicket'].sum()}")
```

**Success criterion:** Free-hit v_bat mean is not dramatically different from normal legal v_bat mean. Wicket count on free hits is 0 or very low.

**Action if fail:** Add delivery_kind == 'free_hit' interaction to EV model (dismissal probability set to near-zero).

---

### VT-19 — Bootstrap Distribution Normality Check

**What it validates:** P(top10) is computed assuming Gaussian bootstrap distributions. This test checks whether that assumption holds.

**How to run:**
```python
# Requires storing per-draw bootstrap ratings — currently not done.
# WORKAROUND: Check if bootstrap distribution is approximately symmetric
# by comparing (R_overall - CI_90_lo) vs (CI_90_hi - R_overall)
batters = pd.read_csv('outputs/FINAL_TOP10_BATTERS.csv')
batters['ci_lo_dist'] = batters['R_overall'] - batters['CI_90_lo']
batters['ci_hi_dist'] = batters['CI_90_hi'] - batters['R_overall']
batters['asymmetry'] = abs(batters['ci_hi_dist'] - batters['ci_lo_dist'])
print(batters[['player_name', 'ci_lo_dist', 'ci_hi_dist', 'asymmetry']])
```

**Success criterion:** Asymmetry (|upper_half - lower_half|) < 20% of total CI width for all players.

**Action if fail:** Store per-draw rankings from bootstrap and compute P(top10) empirically from counts rather than Gaussian approximation.

---

### VT-20 — Opposition Quality Sensitivity Check

**What it validates:** Whether rankings are robust to controlling for opposition quality.

**How to run (approximate, with available data):**
```python
# Use bowling quality as proxy: mean v_bat conceded by opposition bowlers
# in non-HP deliveries (their "baseline" quality)
press = pd.read_csv('outputs/step3/pressure.csv')

# Compute bowler baseline ability (mean v_bowl per bowler, non-HP)
non_hp = press[press['is_high_pressure'] == 0]
bowler_baseline = non_hp.groupby('bowler_id')['v_bowl'].mean().rename('bowler_baseline')

# Merge onto pressure deliveries
press_hp = press[press['is_high_pressure'] == 1]
press_hp = press_hp.join(bowler_baseline, on='bowler_id')

# Check correlation between batter v_bat and bowler_baseline
correlation = press_hp[['v_bat', 'bowler_baseline']].corr().iloc[0, 1]
print(f"Correlation v_bat vs opponent quality: {correlation:.4f}")
# High positive correlation means batters with high v_bat faced weak bowlers
```

**Success criterion:** |correlation| < 0.15. If |correlation| > 0.30, opposition-quality adjustment is recommended.

**Action if fail:** Add opposition-quality residualisation to v_bat/v_bowl computation.

---

## Tests Requiring External Data or Structural Changes

### VT-13 — Temporal Holdout Test

**What it validates:** Whether players ranked in the top 10 from 2022–2024 data actually outperform other eligible players in 2024–25 HP situations (the strongest available test of model validity).

**Data requirements:** A clean split of the dataset into training (2022–2024) and holdout (2025) seasons.

**How to run:**
1. Add `season` column to the dataset based on match date.
2. Run the full pipeline (steps 1–5) on training seasons only.
3. Compute v_bat/v_bowl for all players in the holdout season without refitting the EV or WP models.
4. Compare the holdout HP performance of top-10 players vs the next-10 eligible players.

**Success criterion:** Top-10 training players have statistically higher mean holdout v_bat/v_bowl (in HP deliveries) than the next-10 players. A one-sided t-test with p < 0.10 would be an acceptable threshold given sample size constraints.

**Action if fail:** The model is overfitting or the signal is too weak to generalise. Consider simplifying to RAP-L (Alternative A) which has lower variance and may generalise better.

**Effort:** Medium (~1 week including data preparation). Requires the dataset to span enough seasons to have a meaningful holdout — with 2022–2025 data, a 2025 holdout is feasible but will have limited power.

---

### VT-14 — WP Calibration by Competition Class

**What it validates:** Whether WP calibration differs between IPL and T20I. If T20I calibration is substantially worse, PI for T20I deliveries is less reliable than for IPL.

**How to run:**
```python
cal = pd.read_csv('outputs/step3/wp_calibration.csv')
# If not already stratified by competition_class, rerun calibration:
press = pd.read_csv('outputs/step3/pressure.csv')
for cat in ['IPL league', 'T20I non-knockout', 'IPL knockout']:
    sub = press[press['competition_class'] == cat]
    # Decile-stratify sub['wp_before'] vs sub['actual_win']
    # ... (reproduce wp calibration by group)
```

**Success criterion:** Calibration error (|mean_wp - actual_win_rate|) < 0.05 in each decile for each competition class.

**Action if fail:** Fit separate WP models for IPL and T20I. This is straightforward (add competition_class indicator to WP model, or fit independently). Requires rerunning steps 3–5.

---

## Validation Report Template

For each future run of the pipeline, the following validation table must be populated and confirmed before rankings are finalised:

| Test | Expected Result | Actual Result | Pass/Fail | Action Taken |
|------|----------------|---------------|-----------|--------------|
| VT-01 EV mean-zero | |mean_v| < 1e-10 | ___ | ___ | ___ |
| VT-02 Resource monotonicity | PASS | ___ | ___ | ___ |
| VT-03 WP Brier score | < 0.19 | ___ | ___ | ___ |
| VT-04 WP calibration | |error| < 0.05 all deciles | ___ | ___ | ___ |
| VT-05 Leverage positivity | 0 violations | ___ | ___ | ___ |
| VT-06 PI missing | 0 missing | ___ | ___ | ___ |
| VT-07 w_K range | 0 < w_K < 0.15 | ___ | ___ | ___ |
| VT-08 Eligibility gate | All ranked players pass | ___ | ___ | ___ |
| VT-09 CI significance | Record count with CI∋0 | ___ | ___ | ___ |
| VT-10 Top-10 recovery | > 20% (disclose actual) | ___ | ___ | ___ |
| VT-11 Threshold sensitivity | Record Bosch-equivalent cases | ___ | ___ | ___ |
| VT-12 Role-specific EV | |mean_v| < 0.05 per role | ___ | ___ | ___ |
| VT-15 EV cross-fit bias | Mean bias < 0.001 | ___ | ___ | ___ |
| VT-16 Super Over | 0 deliveries with elig_pressure=1 | ___ | ___ | ___ |
| VT-18 Free-hit check | No systematic v_bat outliers | ___ | ___ | ___ |
| VT-19 Bootstrap normality | Asymmetry < 20% CI width | ___ | ___ | ___ |

> [!IMPORTANT]
> Rankings must NOT be finalised until VT-01, VT-02, VT-03, VT-04, VT-05, VT-06, VT-08, and VT-15 all pass.
> VT-02 (resource monotonicity) and VT-15 (EV cross-fit bias) currently FAIL and must be fixed before the next round.

---

## Current Validation Gaps Summary

| Gap | Severity | Effort to close |
|-----|----------|-----------------|
| VT-15 EV cross-fit bias | Critical | 2–3 days |
| VT-13 Temporal holdout | High | 1 week |
| VT-02 Resource monotonicity fix | Critical | 1 day |
| VT-04 WP tail calibration fix | Critical | 1–3 days |
| VT-14 WP by competition class | Medium | 1 day |
| VT-12 Role-specific EV | Medium | 2 hours |
| VT-19 Bootstrap normality | Medium | 1 day |
| VT-16 Super Over audit | Low | 2 hours |
| VT-17 Impact Player audit | Low | 2 hours |
| VT-18 Free-hit check | Low | 1 hour |
| VT-20 Opposition quality | Medium | 1 day |

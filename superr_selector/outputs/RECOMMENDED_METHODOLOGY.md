# Recommended Methodology — SupeRR Selector Season 2, Round 1

This document describes the minimum changes required to make the existing pipeline statistically defensible, and the preferred architecture for future rounds. It is not a proposal to modify the submitted rankings.

---

## Philosophy

The existing pipeline has the right architectural ambition: context-adjusted value-added, leverage-weighted, with hierarchical shrinkage and uncertainty quantification. The problems are implementation gaps, not fundamental design flaws.

The recommended methodology keeps the core structure and fixes the confirmed critical issues. Changes are ranked by impact:

1. **Must fix before resubmission or future rounds (critical)**
2. **Should fix for statistical defensibility (high)**
3. **Consider for future rounds (medium/low)**

---

## Priority 1 — Must Fix (Critical)

### Fix 1: Implement EV cross-fitting

**Problem (I-01):** The EV model uses a full-data fit for all deliveries. In-sample bias violates the identity-free property claimed in the methodology. The code at step2 line 143–150 has a comment explicitly noting cross-fitting as the production version — this is an unfinished implementation.

**Fix:** Use leave-one-match-out cross-fitting. For each match m:
1. Fit the EV model on all deliveries from matches ≠ m.
2. Score deliveries in match m using the held-out model.

```python
# Pseudocode (skeleton already exists in step2 comments)
from sklearn.model_selection import cross_val_predict, LeaveOneGroupOut

logo = LeaveOneGroupOut()
groups = press_ev['match_id'].values

v_bat_xfit = cross_val_predict(
    ev_pipeline, X_bat, y_bat,
    groups=groups, cv=logo, method='predict'
)
```

**Impact:** Eliminates in-sample bias. Expected change in individual ratings: 1–5 R-units for high-volume players. Essential for the identity-free claim to hold.

**Effort:** Medium (~2–3 days). The EV model pipeline is already modular.

---

### Fix 2: Enforce resource table monotonicity

**Problem (I-04):** V2_resource_mono_balls and V2_resource_mono_wkts both FAIL. The resource table c(s) is non-monotone in both dimensions, causing v_bat/v_bowl anomalies in sparse states.

**Fix:** Apply isotonic regression after the initial resource table estimation to enforce constraints:
- c(s) weakly decreases as `wickets_lost` increases (more wickets lost → fewer expected runs remaining)
- c(s) weakly decreases as `balls_left` decreases (fewer balls → fewer expected runs)

```python
from sklearn.isotonic import IsotonicRegression

# For each wickets_bin, enforce monotonicity along balls_left
for wkt_bin in resource_table['wickets_bin'].unique():
    mask = resource_table['wickets_bin'] == wkt_bin
    ir = IsotonicRegression(increasing=True)  # more balls = more runs
    resource_table.loc[mask, 'c_s'] = ir.fit_transform(
        resource_table.loc[mask, 'balls_left'],
        resource_table.loc[mask, 'c_s']
    )
```

**Impact:** Removes V-bat/v_bowl inconsistencies in non-monotone states. Death-over and tailender deliveries most affected. Direction of change is non-obvious without rerunning.

**Effort:** Low (~1 day). Requires rerunning steps 2–5.

---

### Fix 3: Tail-calibrate the WP model

**Problem (I-02, I-03):** WP model is miscalibrated at decile 0 (predicted 4.3%, actual 9.5%) and decile 7+ (predicted 74.7%, actual 81.6%). This distorts leverage in extreme match states.

**Fix (minimal, no retraining):** Apply isotonic calibration post-hoc to WP outputs:

```python
from sklearn.calibration import CalibratedClassifierCV

# Or post-hoc isotonic regression calibration:
from sklearn.isotonic import IsotonicRegression

ir = IsotonicRegression(out_of_bounds='clip')
wp_calibrated = ir.fit_transform(wp_raw, actual_win_indicator)
```

**Fix (better, requires retraining):** Add at least one explicit feature to the WP model — `wickets_before` as a direct feature independent of E_remaining. Currently wickets are captured implicitly through E_remaining but the WP model cannot separately weight the wicket state from the run state.

**Impact:** Corrects leverage attribution in extreme match states, which affects PI for the highest-leverage deliveries. Expected change in individual ratings: small on average but potentially large for players with many extreme-state deliveries.

**Effort:** Low for isotonic post-hoc calibration (1 day). Medium for model retraining (2–3 days + validation).

---

## Priority 2 — Should Fix (High)

### Fix 4: Use n_total_press for shrinkage (not n_reg)

**Problem (I-07):** Shrinkage uses n_reg (regular-match delivery count) for precision weight. KO deliveries are excluded from the precision calculation even though they are included in R_overall and in eligibility counting.

**Fix:** Replace `n = max(row['n_reg'], 1)` at step4 line 246 with `n = max(row['n_hp'], 1)` where n_hp is the total HP delivery count across all categories.

**Impact:** Most consequential for players with substantial KO-only HP exposure. Direction: players with high KO/total HP ratios get slightly less shrinkage (pulled less toward population mean). Effect on current top-10: moderate.

**Effort:** Minimal (1 line of code + validation run). Low risk of unintended consequences.

---

### Fix 5: Flag non-significant rankings

**Problem (I-09):** Three bowler 90% CIs include zero. These players cannot be distinguished from zero pressure effect.

**Fix:** Add a `ci_includes_zero` column to the final CSV. In any presentation or report, mark these players with an asterisk and the note: "90% CI includes zero — ranking is not statistically distinguishable from no pressure effect."

This is not a code fix — it is a documentation and presentation fix. Already partially addressed by CI disclosure but should be more prominent.

**Impact:** None on point estimates. High impact on how rankings are perceived. Shakib, Parnell, Madhwal should be clearly flagged.

**Effort:** Minimal (output formatting only).

---

### Fix 6: Report absolute leverage alongside PI percentile

**Problem (I-05):** PI is uniform by construction within each competition class. Absolute leverage magnitude is discarded. Cross-format PI comparisons are not interpretable.

**Fix:** Add `leverage_abs` column to pressure output. In reports, note: "PI represents the within-competition percentile of leverage; for cross-competition comparison use leverage_abs."

Report summary statistics: mean leverage in IPL league deliveries vs T20I non-KO deliveries vs KO deliveries. If IPL KO mean leverage is substantially higher than T20I group mean leverage, the percentile normalisation is hiding that information.

**Effort:** Low (1 day). No change to rankings, only to output tables.

---

### Fix 7: Align role-prior estimation with eligibility criteria

**Problem (I-12):** compute_role_params() uses min_n=60 (n_reg) but eligibility requires n_total ≥ 120 (or n_hp ≥ 50). The estimation set for priors differs from the eligible pool.

**Fix:** Set min_n for role-prior computation consistently with the main eligibility filter. Use n_hp ≥ 50 as the filter for role-prior estimation. This ensures priors are estimated from players who represent the same population as the ranked players.

**Effort:** Minimal (1 parameter change + validation).

---

## Priority 3 — Consider for Future Rounds (Medium/Low)

### Fix 8: Temporal holdout validation

**Gap (Section 7.2):** No temporal holdout test was run. The model has never been evaluated on out-of-sample data.

**Fix:** Reserve 2024–25 IPL season as a holdout. Train on 2022–2023 data. Evaluate whether ranked players in the training period outperform non-ranked players in the holdout period in HP situations. This is the strongest available test of whether the model identifies genuine ability rather than overfitting.

**Effort:** Medium (~1 week including data preparation and analysis).

---

### Fix 9: Separate competition-class EV baseline

**Problem (Section 3.1):** IPL and T20I deliveries are pooled in the EV model despite different scoring rates.

**Fix:** Add `competition_class` as a feature in the EV model (or fit separate EV models per class). This ensures v_bat/v_bowl are measured against the correct baseline for each format.

**Effort:** Low (1 feature addition + validation). Potential impact: moderate for T20I specialists.

---

### Fix 10: Super Over and Impact Player audit

**Problem (I-15, I-16):** Super Over exclusion and Impact Player role classification are unverified.

**Fix:** 
- Run a targeted audit: `press_csv[press_csv['super_over'] == 1]['elig_pressure'].sum()` — confirm this is 0.
- Check Impact Player batting-order classifications for top-10 batters.

**Effort:** Low (1–2 hours of investigation).

---

## Recommended Architecture for Future Rounds

For SupeRR Selector Season 3 and beyond, the recommended architecture is:

```
Step 1: Data ingestion and state construction
        [Same as current — no changes needed]
        
Step 2: Cross-fitted EV model (Leave-One-Match-Out)
        [Replace full_ev with cross_val_predict via LOGO-CV]
        
Step 3: WP model (improved — add wickets_before as direct feature)
        [Add isotonic calibration post-training]
        [Monitor Brier score target: < 0.17]
        
Step 4: Leverage and PI computation
        [Add leverage_abs to outputs alongside PI percentile]
        [Separate percentile computation per competition class — unchanged]
        
Step 5: Player rating (hierarchical EB — largely unchanged)
        [Fix: use n_hp for shrinkage instead of n_reg]
        [Fix: align role-prior estimation set with eligibility]
        [Add: enforce CI-includes-zero flag in outputs]
        
Step 6: Eligibility and ranking
        [n_hp >= 50, matches >= 5 as floor — maintained]
        [n_hp >= 100, matches >= 10 as 'sustained' tier — maintained]
        [Add: temporal holdout validation as annual gate]
        [Add: mandatory CI disclosure in all ranking outputs]
```

**Expected improvement in top-10 recovery rate:** Moving from 22.7% to ~35–45% with cross-fitting and monotone resource table. Recovery rate above 50% would require substantially more data (more seasons) rather than methodological improvements.

---

## Changes That Are NOT Recommended

The following changes were considered and rejected:

1. **Replace leverage with subjective pressure scoring:** Leverage has mathematical rigour and reproducibility. Subjective pressure scoring introduces evaluator bias. Do not replace.

2. **Use external data (opposition ratings, venue ratings):** The organiser provided specific datasets. Using external data risks disqualification. Do not add.

3. **Change eligibility thresholds to manipulate specific rankings:** All threshold changes must be justified from reliability curves and stability analysis. Do not select thresholds to include or exclude specific players.

4. **Replace Bayesian shrinkage with simple averages:** Shrinkage is essential for fair comparison between high-data and low-data players. Do not remove.

5. **Rank players by P(top10) rather than R_overall:** P(top10) depends on the assumed prior over true abilities and the assumed set of competing players. R_overall is a direct, interpretable estimate of pressure performance. Use R_overall as the primary ranking criterion with P(top10) as a supplementary uncertainty indicator.

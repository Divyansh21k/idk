# Baseline Manifest — SupeRR Selector Season 2, Round 1

**Document ID:** `BASELINE_MANIFEST.md`  
**Execution Context:** Methodology Repair Phase — Baseline Establishment  
**Establishment Date:** 2026-11-17  
**Repository:** [https://github.com/Divyansh21k/idk](https://github.com/Divyansh21k/idk)  

---

## 1. Git Version Control State

- **Pre-Repair Base Commit Hash:** `c0ace3fe9412bff1faa25b7f79dfe8682bec112f`
- **Dedicated Repair Branch:** `model-repair`
- **Branch Point:** Created from `main` at commit `c0ace3f`
- **Working Tree Status:** Clean; all previous stage deliverables, raw datasets, source code, and intermediate outputs preserved intact.
- **Commit History at Base:**
  - `c0ace3f` — `review: 5 independent-review deliverables — issues register, model review, alternatives, recommended methodology, validation plan`
  - `e62bc33` — `pressure-audit: 6 deliverables, two-leaderboard recommendation, robustness analysis`
  - `5a9bfee` — `validation-gate: all 6 gates pass, final deliverables written`
  - `6dbe5b5` — `reassessment: revised eligibility (n_hp>=50, matches>=5), 9 deliverables`
  - `8346b2b` — `audit: fix CI bug, D51 RunOut spelling, 500 bootstrap resamples, final rankings v0.6`
  - `6585b7d` — `feat: complete end-to-end SupeRR Selector Round 1 pipeline with final rankings and methodology reports`
  - `4d5003a` — `checkpoint: initial extraction + project setup`

---

## 2. Environment & System Specifications

### Python & Operating System
- **OS Platform:** macOS (Darwin arm64)
- **Python Version:** Python 3.14.2

### Core Library Versions
| Package | Baseline Version | Purpose in Pipeline |
|---|---|---|
| `pandas` | `2.3.3` | Dataframe manipulation, aggregation, and tabular export |
| `numpy` | `2.4.2` | Numerical computation, matrix operations, random sampling |
| `scipy` | `1.17.1` | Statistical distributions and hypothesis testing |
| `scikit-learn` | `1.8.0` | Logistic regression (WP model) and calibration evaluation |
| `statsmodels` | `0.15.0` | Statistical modeling and diagnostics |

### Random Seeds Configured
- **Step 4 Hierarchical Bootstrap:** `seed = 42` (configured via `np.random.seed(42)` at line 639)
- **Validation Gate Bootstrap / Ranking:** `seed = 42` (default argument in `src/validation_gate.py`)
- **Simulation Gate 2 (Base DGP):** `seed = 99`
- **Simulation Gate 2 (Stressed DGP):** `seed = 100`
- **Pressure Experience Audit:** `seed = 42`

---

## 3. Raw Input Data Inventory & Checksums

The pipeline operates strictly on the 6 original CSV datasets provided by the competition organisers. No external data sources are injected.

| File Path | Byte Size | Row Count | SHA-256 Checksum |
|---|---|---|---|
| `data/raw/ball_by_ball.csv` | 40,893,212 bytes | 201,000 | `01e2b4379edfbab6a6e456d304cb3c70f554cb312ef93d9588f3f32a82cb396e` |
| `data/raw/competition_team_player_mapping.csv` | 462,810 bytes | 6,414 | `1ded4e42a933618572d6e2c3a521c3257eb1844fab4456d567d77cbb2d3bbb12` |
| `data/raw/competitions.csv` | 7,549 bytes | 142 | `507ceb7189f972d4e4f299ddcfc97f3c3247af1913f6291106f161fa8353fd9b` |
| `data/raw/matches.csv` | 123,737 bytes | 884 | `bb100ab84b8b9a15160c1f2315cf675210131a30e779ec5079fd5403dcf56eef` |
| `data/raw/playing_eleven.csv` | 966,612 bytes | 28,382 | `7517c73722a28d5d61c808ccf0cbed315a8780586d02e946eb9a7f5daf011c27` |
| `data/raw/teams.csv` | 6,966 bytes | 354 | `a65e5922a9b3bf49247b24fc9471782e700efb31f8dcc5042923238b87c50a5d` |

All checksums have been re-verified against the unpacked data directory before establishing this baseline.

---

## 4. Pipeline Reproduction Commands

To reproduce the complete pipeline from scratch from the `superr_selector` directory:

```bash
cd /Users/divyanshkharnal/Downloads/idk/superr_selector

# 1. Build cleaned delivery, match, and innings tables
python3 src/step1_build_tables.py --raw-dir data/raw --out-dir outputs

# 2. Execute 49 programmatic integrity assertions
python3 src/step1_validate.py --raw-dir data/raw --out-dir outputs

# 3. Fit Expected Value (EV) baseline and resource table c(s)
python3 src/step2_expected_value.py --out-dir outputs

# 4. Fit Win Probability (WP) models, compute Leverage L(s), and generate Pressure Index (PI)
python3 src/step3_win_probability.py --out-dir outputs

# 5. Fit hierarchical empirical Bayes player models and execute 500 match-cluster bootstraps
python3 src/step4_player_model.py --out-dir outputs --n-bootstrap 500

# 6. Apply initial eligibility filtering and produce Stage 4 v0.6 deliverables
python3 src/step5_eligibility_ranking.py --out-dir outputs
python3 src/step6_reports_and_deliverables.py --out-dir outputs

# 7. Execute validation gate suite and produce revised Model B rankings (n_hp >= 50, matches >= 5)
python3 src/validation_gate.py --raw-dir data/raw --out-dir outputs --seed 42

# 8. Run pressure exposure and robustness audit
python3 src/pressure_experience_audit.py --raw-dir data/raw --out-dir outputs --seed 42
```

---

## 5. Baseline Rankings Freeze

The frozen rankings represent the approved **Model B** framework ($n_{\text{hp}} \ge 50$ high-pressure deliveries across $\ge 5$ distinct pressure matches).

### Batters Baseline (`outputs/baseline/BASELINE_RANKINGS_BATTERS.csv`)

| Rank | Player Name | Role | $n_{\text{total}}$ | $n_{\text{hp}}$ | Matches | $R_{\text{overall}}$ | $R_{\text{reg}}$ | 90% CI | Reliability | $P(\text{Top10})$ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi | opener (1-2) | 564 | 180 | 19 | 58.03 | 54.54 | [21.47, 96.28] | 0.637 | 0.821 |
| 2 | Suryakumar Yadav | top order (3-4) | 2663 | 581 | 55 | 39.24 | 38.79 | [26.38, 55.95] | 0.822 | 0.578 |
| 3 | Matthew Wade | lower (7+) | 408 | 126 | 15 | 38.40 | 39.04 | [7.80, 68.51] | 0.665 | 0.554 |
| 4 | Ryan Rickelton | opener (1-2) | 820 | 278 | 33 | 33.77 | 34.32 | [12.64, 57.41] | 0.711 | 0.414 |
| 5 | Rahul Tewatia | middle (5-6) | 518 | 92 | 18 | 31.66 | 30.36 | [9.64, 61.88] | 0.537 | 0.362 |
| 6 | Yashasvi Jaiswal | opener (1-2) | 1800 | 578 | 82 | 30.86 | 32.24 | [14.88, 48.75] | 0.808 | 0.300 |
| 7 | Abhishek Sharma | opener (1-2) | 2235 | 525 | 85 | 30.75 | 40.96 | [5.90, 57.76] | 0.834 | 0.345 |
| 8 | Andre Russell | lower (7+) | 702 | 76 | 12 | 29.22 | 29.77 | [-14.03, 67.84] | 0.748 | 0.350 |
| 9 | Jacob Bethell | top order (3-4) | 422 | 133 | 18 | 29.07 | 29.62 | [1.74, 63.18] | 0.571 | 0.356 |
| 10 | Prabhsimran Singh | opener (1-2) | 1126 | 339 | 35 | 28.02 | 29.82 | [-0.20, 57.62] | 0.735 | 0.289 |

### Bowlers Baseline (`outputs/baseline/BASELINE_RANKINGS_BOWLERS.csv`)

| Rank | Player Name | Type | $n_{\text{total}}$ | $n_{\text{hp}}$ | Matches | $R_{\text{overall}}$ | $R_{\text{reg}}$ | 90% CI | Reliability | $P(\text{Top10})$ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Corbin Bosch | Pace | 360 | 99 | 8 | 37.46 | 37.65 | [9.14, 79.54] | 0.519 | 0.466 |
| 2 | Reece Topley | Pace | 632 | 117 | 20 | 33.04 | 35.82 | [2.02, 73.78] | 0.574 | 0.365 |
| 3 | Zaman Khan | Pace | 200 | 55 | 7 | 30.36 | 30.55 | [6.90, 66.68] | 0.481 | 0.336 |
| 4 | Josh Hazlewood | Pace | 1403 | 280 | 37 | 30.23 | 30.34 | [6.63, 56.68] | 0.678 | 0.279 |
| 5 | Lockie Ferguson | Pace | 1138 | 195 | 26 | 30.02 | 30.72 | [4.78, 64.30] | 0.660 | 0.290 |
| 6 | Wayne Parnell | Pace | 408 | 71 | 10 | 29.61 | 29.79 | [-8.42, 73.09] | 0.520 | 0.376 |
| 7 | Jofra Archer | Pace | 1290 | 276 | 44 | 29.11 | 30.45 | [6.12, 56.01] | 0.674 | 0.269 |
| 8 | Haris Rauf | Pace | 1031 | 235 | 23 | 29.11 | 29.29 | [8.13, 50.89] | 0.636 | 0.210 |
| 9 | Shakib Al Hasan | Spin | 296 | 84 | 9 | 28.64 | 28.83 | [-0.38, 63.51] | 0.480 | 0.315 |
| 10 | Akash Madhwal | Pace | 376 | 58 | 7 | 27.78 | 25.33 | [-28.89, 82.30] | 0.502 | 0.353 |

---

## 6. Documented vs Implemented Methodology

| Methodological Area | Described in Reports / Documentation | Actual Code Implementation | Discrepancy Severity |
|---|---|---|---|
| **EV Cross-Fitting** | Stated as "Identity-free leave-one-match-out cross-fitted model" | Code explicitly comments out cross-fitting and fits on 100% of data (`step2_expected_value.py:143`) | **CRITICAL** (In-sample bias) |
| **Resource Monotonicity** | Documented as monotone expected remaining run surface $c(s)$ | Unconstrained bin means; fails monotonicity in both balls and wickets | **CRITICAL** (Inverted state values) |
| **WP Model Specification** | Implied full state dynamic win probability model | Single engineered linear feature per innings in Logistic Regression | **CRITICAL** (Tail miscalibration) |
| **Run-Out Event Tracking** | D51 specifies non-striker charged with dismissal penalty | Step 2 checked `Run Out` (0 matches); Step 4 fixed with `RunOut` independently | **RESOLVED** (Zero net impact) |
| **Knockout Integration** | Knockout performances weighted by importance $w_K$ | $w_K = 0.0529$ is leverage share; shrinkage formula uses $n_{\text{reg}}$ only, ignoring $n_{\text{ko}}$ | **HIGH** (Shrinkage imbalance) |
| **Statistical Significance** | Documented as robust top-10 identifications | 3 bowler CIs and 1 batter CI cross zero; recovery rate is only 22.7% | **HIGH** (Overstated confidence) |
| **Probability of Top 10** | Derived from posterior bootstrap distribution | Computed via parametric Gaussian Monte Carlo on summary stats | **MEDIUM** (Normality assumption) |

---

## 7. Baseline Deliverable Artifact Inventory

All five baseline freeze deliverables are permanently archived in `outputs/baseline/`:
1. `outputs/baseline/BASELINE_MANIFEST.md` (This document)
2. `outputs/baseline/BASELINE_RANKINGS_BATTERS.csv` (Frozen Model B Top-10 Batters)
3. `outputs/baseline/BASELINE_RANKINGS_BOWLERS.csv` (Frozen Model B Top-10 Bowlers)
4. `outputs/baseline/BASELINE_MODEL_DIAGNOSTICS.md` (Comprehensive diagnostic report across all 6 steps)
5. `outputs/baseline/BASELINE_PARAMETERS.json` (Machine-readable hyperparameter freeze)

---

## 8. Reproducibility Status

| Output Artifact | Reproducibility Status | Notes |
|---|---|---|
| `outputs/step1/*` | **Fully Reproducible** | Deterministic sorting and parsing |
| `outputs/step2/*` | **Fully Reproducible** | Deterministic bin aggregation |
| `outputs/step3/*` | **Fully Reproducible** | Scikit-learn LogisticRegression deterministic given features |
| `outputs/step4/*` | **Fully Reproducible** | Deterministic given seed=42 for 500-cluster bootstrap |
| `outputs/FINAL_TOP10_BATTERS.csv` | **Fully Reproducible** | Matches validation_gate.py with seed=42 |
| `outputs/FINAL_TOP10_BOWLERS.csv` | **Fully Reproducible** | Matches validation_gate.py with seed=42 |

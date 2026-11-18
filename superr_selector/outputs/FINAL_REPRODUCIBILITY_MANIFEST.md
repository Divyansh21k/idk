# Final Reproducibility Manifest: SupeRR Selector Season 2

**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Repository:** `https://github.com/Divyansh21k/idk`  
**Current Branch:** `model-repair`  
**Current Verification Commit:** `bb30e5877b0c85b65621d3d61601f5b81c4c60ca`  
**Working Tree Status:** Clean (fully tracked and synchronized with `origin/model-repair`)

---

## 1. System Environment & Package Versions

| Component | Specification / Version |
|---|---|
| **Operating System** | macOS 15.x (Darwin 24.3.0, arm64) |
| **Python Runtime** | Python 3.14.2 |
| **NumPy** | 2.4.2 |
| **Pandas** | 2.3.3 |
| **SciPy** | 1.17.1 |
| **Git Version** | git version 2.39.5 (Apple Git-154) |

---

## 2. Input Data Integrity & SHA-256 Checksums

The project uses strictly the six official organizer-provided CSV files located in `data_pack_extracted/Data Pack/`:

| Filename | File Size (Bytes) | SHA-256 Checksum |
|---|---|---|
| `ball_by_ball.csv` | 41,071,837 | `01e2b4379edfbab6a6e456d304cb3c70f554cb312ef93d9588f3f32a82cb396e` |
| `competition_team_player_mapping.csv` | 462,969 | `1ded4e42a933618572d6e2c3a521c3257eb1844fab4456d567d77cbb2d3bbb12` |
| `competitions.csv` | 7,624 | `507ceb7189f972d4e4f299ddcfc97f3c3247af1913f6291106f161fa8353fd9b` |
| `matches.csv` | 123,864 | `bb100ab84b8b9a15160c1f2315cf675210131a30e779ec5079fd5403dcf56eef` |
| `playing_eleven.csv` | 966,287 | `7517c73722a28d5d61c808ccf0cbed315a8780586d02e946eb9a7f5daf011c27` |
| `teams.csv` | 6,922 | `a65e5922a9b3bf49247b24fc9471782e700efb31f8dcc5042923238b87c50a5d` |

*Data Scope Rules Applied:*
1. Filter to seasons 2022, 2023, 2024, 2025.
2. Exclude the 30 out-of-scope non-senior A-team matches (e.g. Men's T20 Emerging Teams Asia Cup, match IDs 1406833–1406847).
3. Resulting clean dataset: **802 senior matches** (IPL and T20 International).

---

## 3. Production Pipeline Execution Commands & Random Seeds

To reproduce all model components from raw CSVs from scratch:

```bash
# 1. Step 1: Ingest raw CSVs, apply exclusions, build delivery tables
python3 superr_selector/src/step1_build_tables.py

# 2. Step 2: Fit expected-value resource tables and delivery values (Seed: 42)
python3 superr_selector/src/step2_expected_value.py

# 3. Step 3: Fit multivariable win-probability model, calculate leverage & pressure (Seed: 42)
python3 superr_selector/src/step3_win_probability.py

# 4. Step 4: Fit Empirical Bayes player ratings, run match-cluster bootstrap (Seed: 42)
python3 superr_selector/src/phase4_pipeline.py

# 5. Targeted Statistical Verification (Seed: 42)
python3 superr_selector/src/targeted_verification_pipeline.py

# 6. Critical Bootstrap Investigation (Seed: 42)
python3 superr_selector/src/critical_bootstrap_investigation.py

# 7. Independent Bootstrap & Posterior Verification Suite (Seed: 12345)
python3 superr_selector/src/verify_bootstrap_and_posterior.py
```

---

## 4. Key Production & Audit Output Checksums

| Output Filename | SHA-256 Checksum | Primary Role |
|---|---|---|
| `FINAL_REPAIRED_BATTER_RANKINGS.csv` | `41f58d4e22502d4e6089afe126704d29562cd43bfa217c9053244f8252404342` | Authoritative Repaired Batter Rankings |
| `FINAL_REPAIRED_BOWLER_RANKINGS.csv` | `eba8945ab63cf62f08af09a6a0515d98245bfa70bf9b6a70925676b20d4c2a7f` | Authoritative Repaired Bowler Rankings |
| `BOOTSTRAP_VERIFICATION_RESULTS.csv` | `a111acf3653dea90d4d3d2601e2594c9fe84ab8bb1c18354a619acf3492ec3d1` | Full-field ranking results across all eligible players |
| `TARGETED_AUDIT_PLAYER_PROBABILITIES.csv` | `07c6c742fb6b347682d1bd1bf00ecc594d9ca70f2fe65ab5678714349c79ec56` | Posterior intervals, $P(\mu > 0)$, and bootstrap comparison |
| `BOOTSTRAP_SYNTHETIC_VALIDATION.csv` | `2cc211c48c93ab824b2bc87eba5106ab7f220a811618cec2822ea10ea1bcd51a` | 100-dataset synthetic validation records (8,000 player trials) |
| `BOOTSTRAP_REAL_DATA_SENSITIVITY.csv` | `224c48b39dd42a9c434985dece3f311cbfe59e8cda0ca49e506738b69319ebb5` | Real-data sensitivity comparison of Procedures A, B, and C |

---

## 5. Historical Baseline Preservation

All original historical outputs and baseline Model B rankings are preserved without modification in `superr_selector/outputs/baseline/`:
- `BASELINE_MANIFEST.md`
- `BASELINE_RANKINGS_BATTERS.csv`
- `BASELINE_RANKINGS_BOWLERS.csv`
- `BASELINE_DIAGNOSTICS.md`
- `deliverables/top10_batters_under_pressure.csv`
- `deliverables/top10_bowlers_under_pressure.csv`

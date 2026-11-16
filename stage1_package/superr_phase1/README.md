# SupeRR Selector S2 — Round 1: data audit pipeline (Stages 1–2)

Read-only audit of the organiser CSVs. **Raw data is never modified.** No cleaning is applied at this stage.
Only organiser-supplied files are used (no external data).

## Requirements
Python 3.9+; `pip install -r requirements.txt` (pandas, numpy).

## Layout
```
data/raw/           <- put the 6 organiser CSVs here (or pass --raw-dir / set SUPERR_RAW_DIR)
src/common.py       loading, schema validation (fails early with a clear message), helpers
src/crossfile.py    competition/team/match-specific assertions (37 checks)
src/stage1_audit.py Stage 1: profiles, scope, assertions, XI duplicate accounting
src/stage2_investigate.py  Stage 2: record-level investigations
src/stage3_stage_audit.py  Stage 3 pre-cleaning audit of stage/knock_out (earlier preliminary base)
src/rules.py               shared rules used from Step 1 onwards
src/step1_build_tables.py  Stage 4 Step 1 data layer (analysis tables; no models)
src/step1_validate.py      Step 1 validation suite (50 checks)
tests/mutation_test_step1.py negative controls for the validation suite
src/stage3b_eligibility.py Stage 3b task-specific eligibility, exact exclusion intersections, extras mapping, role-specific knockout reliability (flags and counts only)
outputs/            created automatically (--out-dir / SUPERR_OUT_DIR)
```
Required files: ball_by_ball.csv, matches.csv, competitions.csv, playing_eleven.csv, teams.csv, competition_team_player_mapping.csv
(all columns listed in `src/common.py::REQUIRED` must be present).

## Run
```
python -m venv .venv && . .venv/bin/activate      # optional
pip install -r requirements.txt
python src/stage1_audit.py     --raw-dir data/raw --out-dir outputs [--strict]
python src/stage2_investigate.py --raw-dir data/raw --out-dir outputs
python src/stage3_stage_audit.py --raw-dir data/raw --out-dir outputs   # needs Stage 2 output (reads s2_innings_summary.csv)
python src/stage3b_eligibility.py --raw-dir data/raw --out-dir outputs   # needs Stage 2 output
python src/step1_build_tables.py --raw-dir data/raw --out-dir outputs   # Stage 4 Step 1 (reads raw only)
python src/step1_validate.py --raw-dir data/raw --out-dir outputs       # 50 checks, exit code 1 on failure
python tests/mutation_test_step1.py --raw-dir data/raw --out-dir outputs # 6 negative controls
```
`--strict` (Stage 1) returns exit code 1 if any *hard* assertion fails. The organiser data contains known anomalies, so a plain run is expected to report FAILs; they are findings, not crashes.

## Expected outputs
- `outputs/cross_file_assertions.csv` — one row per assertion: relationship, rows checked, violations, PASS/FAIL, severity, violations if only a *global* ID lookup were used, violations by scope (IPL/T20I/OTHER), exception file.
- `outputs/exceptions/*.csv` — the violating records (`assert_<ID>.csv`) plus `matches_without_bbb.csv`, `revised_target_matches.csv`, `playing_eleven_duplicates_detail.csv` and Stage 2 exception files (`s2_*.csv`).
- `outputs/stage1/stage1_audit_report.md`, `outputs/stage1/column_profile.csv`
- `outputs/stage2/stage2_investigation_report.md` and supporting tables (`s2_*.csv`: innings summary, result reconciliation, legal-ball subset test)
- `outputs/stage3/` — stage/knock_out audit, exposure and sample-size tables, descriptive league-vs-knockout comparison (`s3_*.csv`, `s3_stage_audit_report.md`)
- `outputs/stage3b/` — eligibility flags per match and innings, task sample sizes, extras mapping, role-specific reliability, population knockout deviation (`s3b_*`)
- `outputs/step1/` — Step 1 analysis tables, validation results and report; `outputs/stage4_step1_report.md` — Step 1 sign-off report; `outputs/extras_exception_review.md`; `outputs/assumptions_register.md|csv`
- `outputs/stage3_proposal.md` — proposed cleaning rules, league/knockout scoring framework, sensitivity plan (awaiting approval)
- `outputs/technical_methodology.md`, `outputs/plain_english_methodology.md`, `outputs/decision_log.md|csv` — the three living documents (v0.4; kept consistent; plain-English describes only what is implemented)
Raw-file SHA-256 hashes are printed at the top of the Stage 1 report so you can confirm the inputs were unchanged.

# Stage 4, Step 1: data layer. Report and sign-off request

**Scope of this step:** build the analysis tables from the approved flags and unit definitions, with automatic validation. **Not done:** no expected-value model, win probability, leverage, player model, rating or ranking; nothing deleted from the raw files; no player-level performance value has been computed or inspected.

## 1. Code (in `src/`)
| File | Purpose |
|---|---|
| `rules.py` | single source of truth for the rules: illegal delivery kinds, no-ball-like kinds, bowler-credited dismissal types, data-quality match ids, result classifier, batting-order bands, bowling arm |
| `step1_build_tables.py` | builds the tables below from the raw CSVs (reads only) |
| `step1_validate.py` | 50 checks: approved-document counts (A), independent invariants recomputed from raw (B), cross-check against the separate Stage 3b implementation (C); exit code 1 on any failure |
| `tests/mutation_test_step1.py` | 6 negative controls: corrupts copies of the tables and confirms the validator catches each corruption |
Run: `python src/step1_build_tables.py --raw-dir data/raw --out-dir outputs`, then `python src/step1_validate.py ...`, then `python tests/mutation_test_step1.py ...` (README has the full sequence).

## 2. Outputs (`outputs/step1/`)
| Table | Rows | Content |
|---|---|---|
| `deliveries_analysis.csv.gz` | 200,999 | every delivery with raw fields plus derived columns below |
| `matches_analysis.csv` | 883 | match flags: class, result class, revised, undeclared reduced-overs, data-quality, no-result/partial, tie/super-over, innings 3/4, WP-training match |
| `innings_analysis.csv` | 1,652 | in-scope innings 1-2 with task flags (WP training, pressure, batting, bowling), completeness, incomplete-innings-1 flag, target |
| `player_exposure_batters.csv` / `_bowlers.csv` | 816 / 589 | counts only (balls faced or deliveries bowled by class, IPL and T20I totals, innings rows); role keys (modal batting order and band; pace/spin and arm). **No performance values** |
| `transfer_diagnostic_feasibility.csv` | 6 | players with at least N eligible balls in both competitions |
| `extras_label_counts.csv`, `step1_validation.csv`, `step1_build_report.md` | | label counts before and after cleaning; all 50 check results; free-hit evidence |
**Derived delivery columns:** `extras_type_clean` (raw label with the 3 reviewed rows handled); `delivery_kind` (legal, wide, overstep, other); `is_legal`; `batter_ball_faced` (not a wide); `batter_runs`; `bowler_charged_runs` (bat runs + wides + no-ball penalty); `uncharged_extras` (byes, leg-byes, penalty, untyped, extras2); `team_runs`; `bowler_wicket_credit`; `dismissed_role` (striker / non_striker / unattributed / none); pre-delivery state `legal_before`, `legal_left_before`, `wickets_before`, `runs_before`, `target`, `runs_required_before`; `free_hit`; class (`cat`), scope, season; task flags `elig_wp_training`, `elig_pressure`, `elig_batting`, `elig_bowling`, `batting_row_eligible`, `bowling_row_eligible`.

## 3. Validation evidence
- **50 of 50 checks pass**, including: 883 / 853 / 837 waterfall; exclusive flag combinations (772 / 28 / 10 / 14 / 8 / 3 / 2); task sizes (WP training 771 matches, 1,542 innings; pressure, batting and bowling 802 matches, 1,583 innings, by class); 35 matches with no eligible innings; exposure (188,761 deliveries, 180,716 legal, 181,517 balls faced, 12,749 batter-innings rows, 816 batters, 9,376 bowler-innings rows, 589 bowlers; WP-training deliveries 184,377); extras label counts.
- **Independent invariants (recomputed from the raw files):** team total per innings equals raw runs + extras1 + extras2 for every innings; bowler-charged runs plus uncharged extras equal the team total in every innings, so no extras category is lost or double counted; batter runs on balls faced equal total bat runs; legal balls per innings match an independent count and never exceed 120 in innings 1-2; the state bookkeeping reproduces each innings' total runs and wickets; innings-2 targets equal innings-1 total + 1; batter_ball_faced, delivery_kind and bowler_charged_runs equal independent recomputations on every delivery.
- **Free-hit flag:** no flagged delivery has a bowler-credited dismissal and no innings' first delivery is flagged.
- **Cross-check:** Step 1 innings flags equal the independent Stage 3b implementation in all 1,652 innings.
- **Negative controls: 6 of 6 caught** (treating `other` as legal; dropping an eligible innings; counting wides as balls faced; charging byes to the bowler; not charging the no-ball penalty; mis-flagging free hits). The first run caught only 4 of 5: counting wides as balls faced slipped through because one count used a derived column, so I added independent checks B20-B23 and re-ran.
- **Manual review** of the extras exception rows: `extras_exception_review.md` (3 rows, not 2; none affects an out-of-scope or revised match's ratings except the two unlabelled single extra runs, which are handled identically whether they were byes or leg-byes).
- **Reproducibility:** a fresh virtual environment reproduced all reports identically.

## 4. Results of this step [DATA]
- Eligible deliveries: wides 7,244; no-ball-like 801; free hits 873.
- Roles from the frozen rule: openers 139, top order 152, middle 131, lower 394; pace 341, spin 248 (every bowler has exactly one arm and one pace/spin value).
- Transfer-diagnostic feasibility: batters with at least 60 / 120 / 300 eligible balls in both competitions 87 / 68 / 37; bowlers 97 / 79 / 38.

## 5. Unresolved issues
1. **Run-out wicket cost (D51, needs your decision before Step 2):** 271 of 600 run-outs dismiss the non-striker, who faced no ball. Proposal: charge the dismissal to the dismissed batter through a dismissal-event record; the striker keeps the runs and the ball faced.
2. `other` extras: behaviour is now strongly supported (including the free-hit pattern), the name is not in the data.
3. Who is charged for extras is convention, not in the files (A2).
4. The three unlabelled/mislabelled extras rows are interpreted, not proven (A16, A17).
5. Undeclared reduced-overs matches are detected by a rule (A15); undetectable ones may remain (A28). Sensitivity S14 will show whether the three matter.
6. Match 14164 (119 legal balls in a completed innings) and 41509 (one extra delivery) are kept with flags.
7. IPL 2025 ordering anomaly (71 league matches, one team with 15, dates out of order) is unresolved (D36); no step depends on it yet.
8. Role stability across seasons (A19) and opposition-quality connectivity (A25) are untested.

## 6. Sign-off request
Please confirm: (a) the Step 1 tables and the 50-check validation are accepted; (b) the free-hit and illegal-delivery rules (D47) and the exception-row decisions (D50); (c) your decision on the run-out attribution (D51). On approval the next step is **Step 2 (stage-1 expected value and resource table, identity-free, cross-fitted)**. It will not start until you say so, and no rankings will be generated or inspected before freeze points F1 (w_K) and F2 (role thresholds).

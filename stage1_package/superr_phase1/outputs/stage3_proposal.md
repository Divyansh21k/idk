# Stage 3 proposal v3 (revised after your five-decision review; no cleaning has been executed and no model has been fitted)

Scope: competition-wide pressure-performance evaluation of eligible IPL and T20I players, organiser data only; no franchise-specific analysis (D38). Living documents: `technical_methodology.md`, `plain_english_methodology.md`, `decision_log.md` (46 decisions). Labels: [DATA] derived from supplied files, [KNOW] convention, [ASSUME] choice to be frozen, [OPEN] unresolved.

## 0. Where each of your corrections is addressed
| Your point | Revised treatment | Where |
|---|---|---|
| D1 leverage-share weight | w_K = leverage on eligible IPL knockout deliveries / leverage on all eligible IPL deliveries, computed after validation and before any player result; high-pressure-delivery share as sensitivity; match vs delivery vs pressure-exposure explained | tech sec 6; plain K13; D29, D44 |
| D2 T20I finals | Four classes shown separately; finals do not estimate IPL knockout parameters; not in the "League" output; contribute to general stage-blind parameters through nuisance terms | tech sec 3, 6; D26, D43 |
| D3 shrinkage | Full hierarchical (crossed, match-clustered) model with joint draws; simple formula only as intuition | tech sec 6; D28, D45 |
| D4 margins | 0.025 primary, 0.01 and 0.05 tested; wide CI = inconclusive | tech sec 8; D30 |
| D5 units | Balls faced vs legal balls vs deliveries bowled; extras table | section 2 below; tech sec 2; D32 |
| C3 | No-result/partial matches retained for pressure and performance; excluded only from WP training | section 3 below; D03 |
| C5 | Uncurtailed first innings of revised matches retained (8 of 38) | D05 |
| C10 | Exposure from delivery records, not is_played | D16, D41 |
| K=0 terminology | "League" = IPL league only; combined output renamed Regular-match | D43 |
| 797 reconciliation | exact intersections and task-specific sizes below | section 3 |
| Stage-1 own-effect | Stage 1 identity-free; opposition crossed effect estimated jointly | tech sec 4, 6; D42 |
| Worked examples | K2 (E[W] = 1/12), K5 (probabilities, 14.64 and 1.34), K12 role-specific | plain K2, K5, K12; D46 |

## 1. Revised decision log
`decision_log.md` v0.4 (46 decisions, each with evidence, alternatives, reason, limitations, status).

## 2. Cleaning and eligibility rules (flags first; raw files untouched)
C1 scope: IPL + T20I; 30 A-team matches excluded. C2 16 abandoned matches without ball-by-ball excluded. C3 (revised) no-result/partial matches excluded **only** from WP training. C4 innings 3/4 never used; ties and super-over matches excluded from WP training labels but usable for pressure and performance. C5 (revised) revised/D-L matches: innings 2 never used; innings 1 retained only if `first_inn_revised_overs` is null and the innings is complete. C6 data-quality exclusions 14130 and 20190; 14164 and 41509 retained with a flag. C6b (new) undeclared reduced-overs matches 15795, 31278, 48514 excluded. C7 legal-ball rule (not wide/Overstep/other). C8 totals = runs + extras1 + extras2. C9 `is_wicket` authoritative; bowler credit by type; batter dismissal by `dismissed_player_id`. C10 (revised) key on player_id; exposure from delivery records; `is_played` only for squad membership; XI duplicates resolved to the row matching ball-by-ball order. C11 `bowl_speed` dropped; bowler type = pace/spin + arm. C12 timestamps unused. C13 `knock_out` the only stage variable.

**Extras mapping** (every category; full evidence columns in technical document section 2):
| extras_type | Legal ball | Batter runs | Batter ball faced | Bowler runs charged | Bowler delivery |
|---|---|---|---|---|---|
| (none) | yes | runs | yes | runs | yes |
| wide (7,714) | no | 0 | no | extras1 (1-5) | yes |
| Overstep / no-ball (576) | no | runs | yes | runs + 1 penalty; extras2 not charged | yes |
| other (264) | no | runs | assumed yes (sensitivity no) | runs + 1; extras2 not charged | yes |
| byes (529) | yes | 0 | yes | 0 | yes |
| legbyes (2,748) | yes | 0 (1 exception row) | yes | 0 | yes |
| Penalty (1) | yes (ball 4 of a complete over) | 0 | yes | 0 (5 penalty runs not charged) | yes |

## 3. Task-specific eligibility and exact reconciliation [DATA] (`stage3b/s3b_eligibility_report.md`)
Waterfall: 883 - 30 A-team = 853 - 16 no ball-by-ball = **837**. Exclusive flag combinations: none 772; revised only 28; revised + no-result/partial 10; no-result/partial only 14; tie/super-over 8; undeclared reduced-overs 3; data-quality 2. Totals: revised 38, no-result/partial 24, tie/super-over 8, undeclared 3, data-quality 2. The earlier "797" = 837 - 38 - 2 and still contained 14 no-result/partial, 8 tie/super-over and 3 undeclared reduced-overs matches; the earlier C3 would have removed the 14.
| Task | Matches (innings) | IPL league | IPL knockout | T20I non-knockout | T20I final |
|---|---|---|---|---|---|
| WP training | 771 (1,542) | 331 (662) | 19 (38) | 416 (832) | 5 (10) |
| Pressure calculation | 802 (1,583) | 341 (676) | 20 (39) | 436 (858) | 5 (10) |
| Batting performance | 802 (1,583) | 341 (676) | 20 (39) | 436 (858) | 5 (10) |
| Bowling performance | 802 (1,583) | 341 (676) | 20 (39) | 436 (858) | 5 (10) |
35 matches have no eligible innings: 30 revised matches without a retainable innings 1, 2 data-quality, 3 undeclared reduced-overs. 8 revised matches contribute innings 1 only. 14 no-result/partial and 8 tie/super-over matches are retained. 10 incomplete innings 1 are retained with a flag.
Exposure (pressure-eligible deliveries; balls faced; batter-innings rows; batters / bowler-innings rows; bowlers): IPL league 81,564; 78,248; 5,259; 334 / 4,022; 259. IPL knockout 4,573; 4,403; 313; 128 / 223; 92. T20I non-knockout 101,434; 97,712; 7,086; 658 / 5,073; 470. T20I final 1,190; 1,154; 91; 66 / 58; 41. Total 188,761 deliveries (180,716 legal), 816 batters, 589 bowlers.

## 4. League / knockout classification and league importance [DATA] (`stage3/s3_stage_audit_report.md`)
`knock_out` agrees with `stage` in 883 of 883 matches (31 knockouts: IPL 20, T20I 5, A-team 6). IPL knockouts are the last four matches of each season by number and date, all with ball-by-ball. T20I knockouts are 5 finals; `stage` text differs between IPL and T20I (T20I has `Others` 226 and `Super 4` 6), so only `knock_out` is comparable. League importance is not measurable from the supplied fields (no points table, qualification or tie-break rules) and no score is built (D31).

## 5. Scoring framework (technical document section 6)
Same stage-blind ball value and pressure everywhere. Joint hierarchical model per discipline with player baseline and pressure response, IPL-knockout shift and interaction (population), player knockout deviation (shrunk), nuisance terms for T20I finals, crossed opposition effect, match effect. Outputs: Regular-match, IPL Knockout, Overall = (1 - w_K) Regular + w_K Knockout, plus IPL league, T20I non-knockout and T20I finals reported separately. Reliability and intervals for each component.

## 6. Sample-size and reliability assessment [DATA, unadjusted upper bounds, IPL]
Role-specific knockout reliability at the median knockout sample: batters overall 0.15 (17.5 balls), openers 0.42 (42), top order 0.10 (37.5), middle 0.18 (31.5), lower 0.09 (5); bowlers overall 0.14 (44), pace 0.13 (46), spin 0.08 (27.5). Balls for reliability 0.5: batters about 97 (openers 57, middle 149, top order 331), bowlers about 270. Population knockout deviation: kappa batters -0.052 (-0.134 to 0.032), bowlers -0.029 (-0.108 to 0.050); psi batters 0.151 (0 to 0.248), bowlers 0.120 (0 to 0.219). Weight proxies: 5.39% / 5.54% (matches), 5.31% (deliveries), 5.05% (overs 16-20); the leverage share is not yet computable. Verdict: knockout scores will exist for every player but, for most, rest mainly on the regular-match estimate; each player's own-knockout weight is reported.

## 7. Sensitivity plan (S0-S13, frozen; technical document section 9)
Adds to v0.3: weight definitions (leverage share vs high-pressure share vs delivery vs match share, 10%, 20%), T20I finals as knockout / regular / excluded, revised-innings retention off, no-result matches excluded, `other` legal / not faced, role-specific psi, player-fold stage-1 cross-fitting. Output per scenario: overlap with S0, Spearman and Kendall correlation, each player's P(top 10), stability class.

## 8. Proposed implementation plan (Stage 4; each step ends at a gate you sign off; documents updated at every gate)
1. **Data layer:** build analysis tables from the flags (innings eligibility, unit definitions, extras mapping), with unit tests against the numbers in section 3. Gate: counts match this document exactly.
2. **Stage-1 expected value and resource table**, identity-free, cross-fitted. Gate: diagnostics.
3. **Win probability model**, trained on the 771 matches, cross-fitted; calibration overall and by class. Gate: calibration, monotonicity, martingale check.
4. **Leverage, pressure index and w_K**; w_K computed once, value and code hash recorded in the decision log and frozen **before any player-level model is fitted**. Gate: validation of pressure (behaviour changes with pressure; placebo).
5. **Player models M0, M1, M2** (batters, bowlers), Bayesian cross-check. Gate: model comparison and equivalence tests at 0.01 / 0.025 / 0.05, with inconclusive outcomes reported as such.
6. **Ratings, intervals, rank uncertainty, reliability**, then sensitivity scenarios. Gate: your review of dossiers for outliers.
7. **Final top 10** from the frozen Overall rating; methodology documents finalised.

## Awaiting
Your approval of this implementation plan. Nothing in steps 1-7 runs until you approve.

## v0.5 addendum (your Stage 4 review)
Corrections incorporated: (1) illegal deliveries and free hits defined (technical 5.1, D47); (2) undeclared reduced-overs matches stay excluded, with sensitivity S14 (D39); (3) cross-competition transfer diagnostic (technical 6.3, D48); (4) what the REML/bootstrap/Bayes intervals contain, with a pre-specified simulation demonstration (technical 6.4, D45); (5) role-aware thresholds from a pre-ranking power analysis, frozen at F2 (D49); extras exception rows verified by hand (`extras_exception_review.md`); assumptions register kept (`assumptions_register.md`). **Step 1 is executed and awaiting sign-off (`stage4_step1_report.md`); Steps 2-7 have not been started.**

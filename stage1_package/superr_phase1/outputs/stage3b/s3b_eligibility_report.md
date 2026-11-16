# Stage 3b eligibility and extras audit (generated; flags and counts only)

## A. Extras-treatment mapping

```
extras_type   rows                                         legal_ball                batter_runs_credited            batter_ball_faced                                 bowler_runs_charged bowler_delivery_counted
     (none) 189167                                                yes                                runs                          yes                                                runs                     yes
   Overstep    576                                                 no                          runs (0-6)                          yes runs + extras1 (1 penalty run); extras2 NOT charged         yes (not legal)
    Penalty      1 yes (row occupies ball 4 of a complete 6-row over)                                   0                          yes        0 (5 penalty runs not charged to the bowler)                     yes
       byes    529                                                yes                                   0                          yes                     0 (extras1 = byes, not charged)                     yes
    legbyes   2748                                                yes 0 (1 row has bat runs=1: exception)                          yes                 0 (extras1 = leg-byes, not charged)                     yes
      other    264                                                 no                          runs (0-6) ASSUME yes (sensitivity: no)             runs + extras1 (1); extras2 NOT charged         yes (not legal)
       wide   7714                                                 no        0 (runs=0 in all 7,714 rows)                           NO           extras1 (wide + any runs run or boundary)         yes (not legal)
```

Evidence columns:
```
extras_type   rows  bat_runs  extras1_sum  extras2_sum  rows_bat_runs_gt0                                          extras1_values              extras2_values                                                                                                       basis
     (none) 189167    268285            1            1             121138                                   {"0": 189166, "1": 1}       {"0": 189166, "1": 1}                          DATA: ordinary delivery (1 row has extras1=1 and extras2=1 but no type: exception)
   Overstep    576       852          576           48                337                                              {"1": 576} {"0": 555, "1": 12, "4": 9} DATA: extras1=1 always; KNOW: no-balls count as balls faced; ASSUME extras2 = byes/leg-byes off the no-ball
    Penalty      1         0            5            0                  0                                                {"5": 1}                    {"0": 1}     DATA: 1 row, runs=0, extras1=5, over has exactly 6 rows; KNOW: penalty runs go to the batting side only
       byes    529         0         1000            0                  0           {"1": 348, "2": 35, "3": 3, "4": 142, "5": 1}                  {"0": 529}                                          DATA: runs=0 in all rows; KNOW: byes are not charged to the bowler
    legbyes   2748         1         3603            0                  1 {"0": 1, "1": 2376, "2": 127, "3": 5, "4": 237, "5": 2}                 {"0": 2748}                                                   DATA: runs=0 except 1 row; KNOW: leg-byes are not charged
      other    264       412          264           35                136                                              {"1": 264}  {"0": 250, "1": 7, "4": 7}             DATA: identical value pattern to Overstep and consumes no legal ball; label undocumented [OPEN]
       wide   7714         0         9174            0                  0        {"1": 7107, "2": 296, "3": 39, "4": 2, "5": 270}                 {"0": 7714}                      DATA: runs=0, extras2=0; KNOW: wides are not balls faced and are charged to the bowler
```
[OPEN] The files do not state who is charged for extras; the charging column follows standard convention [KNOW] and is an assumption. Team totals are unaffected (total = runs + extras1 + extras2, reconciled in Stage 2).
[DATA] extras exception rows (2): 
```
                              issue  match_id  innings  overid  over_ball_num  runs extras_type  extras1_runs  extras_2_runs
extras present but extras_type null     17555        1       5              4     0         NaN             0              1
extras present but extras_type null     36097        2       8              6     0         NaN             1              0
              legbyes with bat runs     37099        1      14              1     1     legbyes             0              0
```

## B. Match-level flags and exact intersections

[DATA] result classes (all 883): {"won_margin": 833, "no_result": 21, "abandoned": 19, "superover_decided": 9, "tie_no_superover": 1}
[DATA] waterfall:
```
                                              step  matches
                                       All matches      883
           minus A-team tournaments (out of scope)      -30
                                      = IPL + T20I      853
minus matches without ball-by-ball (all abandoned)      -16
                    = IPL + T20I with ball-by-ball      837
```
[DATA] exact (mutually exclusive) flag combinations among the 837 in-scope matches with ball-by-ball:
```
                 flagset  matches
                  (none)      772
                 revised       28
        noresult/partial       14
revised noresult/partial       10
           tie/superover        8
undeclared-reduced-overs        3
                      dq        2
```
[DATA] flag totals among the 837: {"revised_any": 38, "undeclared_reduced": 3, "dq": 2, "noresult_partial": 24, "tie_or_superover": 8, "has_innings34": 4, "minor_flag": 2}; revised via fields 34, via result text only 4
[DATA] undeclared reduced-overs matches (innings 1 shorter than 120 legal balls without all-out, normal result, no revised field or D/L text): [15795, 31278, 48514]
[DATA] earlier "preliminary base" = 837 - (revised or dq) = 797 matches; of those, 14 are no-result/partial matches (C3) and 8 are ties/super-over decided. Under the earlier C3 these 14 would also have been removed (-> 783); under the revised rules they are not removed wholesale (see section C).

## C. Task-specific eligibility (innings level)

[DATA/PROPOSED] rules:
```
                task                                                                                                                                                                                                                                                                                            innings/match rule                                                                                       reason
         WP training                                                                                                                                                                Match decided by a margin (not tie/super over/no result), not revised/D-L, not data-quality excluded, both innings present, innings 1 complete                                                           match-level label needs an outcome
Pressure calculation IPL/T20I, ball-by-ball present, innings 1-2, not data-quality excluded, not an undeclared reduced-overs match; revised matches: innings 1 only if first_inn_revised_overs is null and the innings is complete; no-result/abandoned/tie/super-over matches ARE eligible (win probability needs only the state) WP of a state does not need the match result; revised innings 2 has a different target/overs
 Batting performance                                                                                                                                                                                                                Same innings as pressure calculation (separate flag; may diverge on delivery-level exceptions)                                                 needs pressure index and stage-1 expectation
 Bowling performance                                                                                                                                                                                                                                  Same innings as pressure calculation plus the extras mapping (separate flag)                                 needs pressure index, stage-1 expectation and charging rules
```
[DATA] task-specific matches and innings by category:
```
              cat                       task  matches  innings
       IPL league                WP training      331      662
     IPL knockout                WP training       19       38
T20I non-knockout                WP training      416      832
       T20I final                WP training        5       10
            TOTAL                WP training      771     1542
       IPL league       Pressure calculation      341      676
     IPL knockout       Pressure calculation       20       39
T20I non-knockout       Pressure calculation      436      858
       T20I final       Pressure calculation        5       10
            TOTAL       Pressure calculation      802     1583
       IPL league        Batting performance      341      676
     IPL knockout        Batting performance       20       39
T20I non-knockout        Batting performance      436      858
       T20I final        Batting performance        5       10
            TOTAL        Batting performance      802     1583
       IPL league        Bowling performance      341      676
     IPL knockout        Bowling performance       20       39
T20I non-knockout        Bowling performance      436      858
       T20I final        Bowling performance        5       10
            TOTAL        Bowling performance      802     1583
       IPL league All innings 1-2 in the 837      347      690
     IPL knockout All innings 1-2 in the 837       20       40
T20I non-knockout All innings 1-2 in the 837      465      912
       T20I final All innings 1-2 in the 837        5       10
            TOTAL All innings 1-2 in the 837      837     1652
```
[DATA] task-specific delivery and player exposure by category:
```
         category  wp_train_deliveries  pressure_deliveries  pressure_legal  batting_balls_faced  batter_innings_rows  distinct_batters  bowling_deliveries  bowler_innings_rows  distinct_bowlers
       IPL league                80141                81564           77896                78248                 5259               334               81564                 4022               259
     IPL knockout                 4451                 4573            4383                 4403                  313               128                4573                  223                92
T20I non-knockout                98595               101434           97285                97712                 7086               658              101434                 5073               470
       T20I final                 1190                 1190            1152                 1154                   91                66                1190                   58                41
            TOTAL               184377               188761          180716               181517                12749               816              188761                 9376               589
```
[DATA] reconciliation: 837 in-scope matches with ball-by-ball -> innings-level: pressure-eligible matches 802, of which revised matches retained for innings 1 only: 8 (innings 8); matches with NO eligible innings: 35; no-result/partial matches retained: 14; tie/super-over matches retained: 8; eligible innings 1 that are incomplete (flagged): 10
[DATA] IPL knockouts: pressure-eligible innings 39 of 40 (the DLS 2023 Final contributes innings 1 only if its first innings was uncurtailed).
Revised matches by innings retained:
```
 innings  elig_pressure  n_innings
       1          False         30
       1           True          8
       2          False         29
```

## D. Role-specific knockout reliability (IPL, unadjusted; replaces the single pooled figure)

```
                                     group            role  players_league_ge120  players_with_KO_balls  players_KO_ge30  median_KO_balls  sigma_per_ball  tau_between_player  reliability_at_median_KO  reliability_at_median_league_n  KO_balls_needed_for_rel_0p5
             batters (runs per ball faced)     ALL batters                   127                    128               52             17.5           1.793               0.182                     0.153                           0.824                       96.680
             batters (runs per ball faced)      lower (7+)                    16                     45                2              5.0           1.763               0.253                     0.093                           0.782                       48.660
             batters (runs per ball faced)    middle (5-6)                    30                     22               11             31.5           1.770               0.145                     0.175                           0.762                      148.559
             batters (runs per ball faced)    opener (1-2)                    38                     25               20             42.0           1.809               0.240                     0.424                           0.907                       57.012
             batters (runs per ball faced) top order (3-4)                    43                     36               19             37.5           1.798               0.099                     0.102                           0.598                      330.753
bowlers (charged runs per delivery bowled)     ALL bowlers                   141                     92               57             44.0           1.765               0.107                     0.140                           0.606                      270.205
bowlers (charged runs per delivery bowled)            Pace                    94                     60               41             46.0           1.803               0.102                     0.128                           0.576                      313.116
bowlers (charged runs per delivery bowled)            Spin                    47                     32               16             27.5           1.691               0.095                     0.080                           0.560                      317.310
```
[DATA/METHOD] same method-of-moments estimator as Stage 3 (tau = between-player SD of true per-ball means from IPL non-knockout data; reliability = tau^2/(tau^2 + sigma^2/n)); values are runs only (no wicket cost), unadjusted for state, so they are upper bounds. Role = modal batting-order band (batters) or pace/spin (bowlers). Units follow the proposed definitions (balls faced exclude wides; bowlers charged runs + wide/no-ball extras, not byes/leg-byes/penalty).

## E. Revised-match innings 1 retention, population knockout deviation and reference-weight proxies (current rules)

[DATA] innings 1 of the 38 revised/D-L matches:
```
                                                            reason  matches
excluded: first innings overs revised (timing of revision unknown)       25
              excluded: innings 1 incomplete with no revised field        5
         retained (first_inn_revised_overs null, innings complete)        8
```
```
                                     group  players  kappa_hat  kappa_ci_low  kappa_ci_high  psi_hat  psi_ci_low  psi_ci_high  median_KO_balls  weight_on_own_KO_deviation_at_median  share_boot_psi_zero
             batters (runs per ball faced)       64    -0.0524       -0.1337         0.0318   0.1513         0.0       0.2478             46.5                                0.2488               0.1250
bowlers (charged runs per delivery bowled)       76    -0.0290       -0.1077         0.0495   0.1200         0.0       0.2188             46.5                                0.1768               0.2395
```
[DATA/METHOD] unadjusted for match state; IPL knockouts vs IPL league only (T20I finals excluded); players with >=120 league and >=12 knockout balls; kappa_hat = mean of (knockout mean - league mean); psi^2 = Var(difference) minus mean sampling variance, floored at 0; bootstrap over players. A rough guide only: the adjusted joint model replaces it.
[DATA] reference-weight PROXIES (the primary w_K, a leverage share, cannot be computed until the validated pressure model exists): {"IPL knockout share of all IPL matches (20/371)": 0.0539, "IPL knockout share of pressure-eligible IPL matches": 0.0554, "IPL knockout share of pressure-eligible IPL deliveries": 0.0531, "IPL knockout share of pressure-eligible IPL overs 16-20 deliveries": 0.0505, "IPL knockout share of pressure-eligible IPL innings-2 overs 16-20 deliveries": 0.0483}
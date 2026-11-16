# Stage 3 pre-cleaning audit: stage / knock_out (generated)

## A. Field audit

[DATA] `stage` dtype str, nulls 0; `knock_out` dtype int64, nulls 0, values [0, 1]
[DATA] stage x knock_out by scope:
```
scope      stage   0  1
  IPL Eliminator   0  5
  IPL      Final   0  5
  IPL     League 351  0
  IPL  Qualifier   0 10
OTHER      Final   0  2
OTHER     League  24  0
OTHER Semi Final   0  4
 T20I      Final   0  5
 T20I     League 245  0
 T20I     Others 226  0
 T20I    Super 4   6  0
```
[DATA] matches where knock_out=1 disagrees with stage in ['Eliminator', 'Final', 'Qualifier', 'Semi Final']: 0
[DATA] knockout matches by competition:
```
scope                                 comp_name      stage  matches
  IPL                                  IPL 2022 Eliminator        1
  IPL                                  IPL 2022      Final        1
  IPL                                  IPL 2022  Qualifier        2
  IPL                                  IPL 2023 Eliminator        1
  IPL                                  IPL 2023      Final        1
  IPL                                  IPL 2023  Qualifier        2
  IPL                                  IPL 2024 Eliminator        1
  IPL                                  IPL 2024      Final        1
  IPL                                  IPL 2024  Qualifier        2
  IPL                                  IPL 2025 Eliminator        1
  IPL                                  IPL 2025      Final        1
  IPL                                  IPL 2025  Qualifier        2
  IPL                                  IPL 2026 Eliminator        1
  IPL                                  IPL 2026      Final        1
  IPL                                  IPL 2026  Qualifier        2
OTHER                Asia Cup Rising Stars 2025      Final        1
OTHER                Asia Cup Rising Stars 2025 Semi Final        2
OTHER     Mens T20 Emerging Teams Asia Cup 2024      Final        1
OTHER     Mens T20 Emerging Teams Asia Cup 2024 Semi Final        2
 T20I                             Asia Cup 2025      Final        1
 T20I               Mens Twenty20 Asia Cup 2022      Final        1
 T20I       New Zealand T20I Tri Series 2022/23      Final        1
 T20I             Pakistan T20I Tri-Series 2025      Final        1
 T20I United Arab Emirates T20I Tri-Series 2025      Final        1
```
[DATA] IPL structure: do the 4 knockouts sit after all league matches (by match_number and by date), and in what stage order?
```
    comp  n  league  knockouts ko_match_numbers  last_league_number  ko_all_after_league_by_number  ko_all_after_league_by_date                            order_by_number  has_bbb_all
IPL 2022 74      70          4 [71, 72, 73, 74]                  70                           True                         True Qualifier > Eliminator > Qualifier > Final         True
IPL 2023 74      70          4 [71, 72, 73, 74]                  70                           True                         True Qualifier > Eliminator > Qualifier > Final         True
IPL 2024 74      70          4 [71, 72, 73, 74]                  70                           True                         True Qualifier > Eliminator > Qualifier > Final        False
IPL 2025 75      71          4 [72, 73, 74, 75]                  71                           True                         True Qualifier > Eliminator > Qualifier > Final        False
IPL 2026 74      70          4 [71, 72, 73, 74]                  70                           True                         True Qualifier > Eliminator > Qualifier > Final         True
```
[DATA] T20I competitions: 131; with >= 8 matches (tournament-like): 2; with any knock_out: 5; names containing "World": 0
[DATA] T20I competitions with >= 8 matches, and every competition with a knockout:
```
                                comp_name  n  ko      first       last                                   stages
              Mens Twenty20 Asia Cup 2022 13   1 2022-08-27 2022-09-11               {"League": 12, "Final": 1}
      New Zealand T20I Tri Series 2022/23  7   1 2022-10-07 2022-10-14                {"League": 6, "Final": 1}
United Arab Emirates T20I Tri-Series 2025  7   1 2025-08-29 2025-09-07                {"League": 6, "Final": 1}
                            Asia Cup 2025 19   1 2025-09-09 2025-09-28 {"League": 12, "Super 4": 6, "Final": 1}
            Pakistan T20I Tri-Series 2025  7   1 2025-11-17 2025-11-29                {"League": 6, "Final": 1}
```
[DATA] T20I stage value counts: {"League": 245, "Others": 226, "Super 4": 6, "Final": 5} -> "Others" = 226 matches; the label never appears in IPL.
[INFERENCE, [KNOW]-assisted] Asia Cup 2022 has 12 "League" matches + Final = 13, while Asia Cup 2025 has 12 League + 6 "Super 4" + Final = 19: the 2022 Super-Four matches are most likely labelled "League". The files cannot confirm this.
[OPEN] `stage` has different semantics in IPL (League = round robin) and T20I (League = group/tournament OR series match; Others = series match). Only `knock_out` (Final/Qualifier/Eliminator/Semi Final) is comparable across competitions, and in T20I it flags only 5 finals.
[DATA/KNOW] IPL playoff role inferred from chronological order within season (Q1, Eliminator, Q2, Final): stage label agrees for 20 of 20 matches
```
comp_name  match_number match_date      stage  playoff_role_inferred  stage_label_agrees  has_bbb                                             result
 IPL 2022            71 2022-05-24  Qualifier Qualifier-1 (by order)                True     True                    Gujarat Titans Won by 7 Wickets
 IPL 2022            72 2022-05-25 Eliminator  Eliminator (by order)                True     True         Royal Challengers Bengaluru Won by 14 Runs
 IPL 2022            73 2022-05-27  Qualifier Qualifier-2 (by order)                True     True                  Rajasthan Royals won by 7 wickets
 IPL 2022            74 2022-05-29      Final                  Final                True     True                    Gujarat Titans Won by 7 Wickets
 IPL 2023            71 2023-05-23  Qualifier Qualifier-1 (by order)                True     True                 Chennai Super Kings Won by 15 runs
 IPL 2023            72 2023-05-24 Eliminator  Eliminator (by order)                True     True                      Mumbai Indians won by 81 runs
 IPL 2023            73 2023-05-26  Qualifier Qualifier-2 (by order)                True     True                      Gujarat Titans won by 62 runs
 IPL 2023            74 2023-05-29      Final                  Final                True     True Chennai Super Kings Won by 5 wickets  (DLS method)
 IPL 2024            71 2024-05-21  Qualifier Qualifier-1 (by order)                True     True             Kolkata Knight Riders Won by 8 wickets
 IPL 2024            72 2024-05-22 Eliminator  Eliminator (by order)                True     True                  Rajasthan Royals Won by 4 wickets
 IPL 2024            73 2024-05-24  Qualifier Qualifier-2 (by order)                True     True                 Sunrisers Hyderabad Won by 36 runs
 IPL 2024            74 2024-05-26      Final                  Final                True     True             Kolkata Knight Riders Won by 8 wickets
 IPL 2025            72 2025-05-29  Qualifier Qualifier-1 (by order)                True     True       Royal Challengers Bengaluru Won by 8 wickets
 IPL 2025            73 2025-05-30 Eliminator  Eliminator (by order)                True     True                      Mumbai Indians Won by 20 runs
 IPL 2025            74 2025-06-01  Qualifier Qualifier-2 (by order)                True     True                      Punjab Kings Won by 5 wickets
 IPL 2025            75 2025-06-03      Final                  Final                True     True          Royal Challengers Bengaluru Won by 6 runs
 IPL 2026            71 2026-05-26  Qualifier Qualifier-1 (by order)                True     True         Royal Challengers Bengaluru Won by 92 runs
 IPL 2026            72 2026-05-27 Eliminator  Eliminator (by order)                True     True                    Rajasthan Royals Won by 47 runs
 IPL 2026            73 2026-05-29  Qualifier Qualifier-2 (by order)                True     True                    Gujarat Titans Won by 7 wickets
 IPL 2026            74 2026-05-31      Final                  Final                True     True       Royal Challengers Bengaluru Won by 5 wickets
```

## B. Preliminary analysis base (flags, nothing deleted)

[DATA] preliminary flags: scope IPL+T20I only; excluded matches: revised/D-L 38, data-quality [14130, 20190]; innings 1-2 only (super-over innings and OTHER competitions excluded); legal = not wide/Overstep/other. Deliveries kept: 188,260 of 200,999
[DATA] matches by category (with ball-by-ball, after preliminary flags):
```
                  cat  matches
         IPL knockout       19
           IPL league      340
T20I knockout (final)        5
    T20I non-knockout      433
```
[DATA] IPL knockouts by season and stage (all 20 have ball-by-ball and none is revised): {"IPL 2022": 4, "IPL 2023": 4, "IPL 2024": 4, "IPL 2025": 4, "IPL 2026": 4}; any IPL knockout excluded by flags: 1
[DATA] player appearances (playing_eleven is_played=True) in the same preliminary base, by category:
```
                  cat  player_appearances  distinct_players
         IPL knockout                 447               164
           IPL league                8000               380
T20I knockout (final)                 110                76
    T20I non-knockout                9569               706
```

## C. Exposure by category

[DATA] legal deliveries, batter-match rows, bowler-match rows, distinct players, and a crude proxy of late-innings deliveries (overs 16-20; NOT the leverage-based pressure measure, which does not exist yet):
```
                  cat  deliveries  late_16_20  distinct_batters  distinct_bowlers  batter_innings_rows  bowler_match_rows  innings2_overs16_20_deliveries
         IPL knockout        4263         913               128                92                  308                218                             385
           IPL league       77848       17518               334               259                 5261               4022                            7607
T20I knockout (final)        1152         252                66                41                   91                 58                             112
    T20I non-knockout       96961       20988               658               470                 7067               5066                            8526
```
[DATA] eligibility proxy (minimum legal balls in the preliminary base) vs knockout exposure of those players:
```
                        metric      0      1      2      3
                          role batter batter bowler bowler
      eligible_min_legal_balls    300    500    300    500
              eligible_players    167    116    173    118
             with_any_KO_balls    107     81     96     79
                  KO_balls>=12     84     70     94     78
                  KO_balls>=30     62     52     62     56
                  KO_balls>=60     30     29     32     31
                 KO_balls>=120      6      6      8      8
median_KO_balls_among_eligible   13.0   22.5   18.0   24.0
                  p75_KO_balls   45.0   58.5   46.0   60.0
                  max_KO_balls    241    241    198    198
       median_league_IPL_balls  299.0  489.5  296.0  452.5
```

## D. Descriptive league vs knockout comparison (IPL only, UNADJUSTED; EARLIER preliminary base and legal-ball unit; the current eligibility rules and units are in stage3b)

```
      subset              metric  league  knockout  diff_KO_minus_league  ci95_low  ci95_high  ko_matches  ko_deliveries
both innings runs_per_legal_ball  1.4700    1.4654               -0.0046   -0.0989     0.0886          19           4263
both innings           dot_share  0.3378    0.3404                0.0025   -0.0197     0.0248          19           4263
both innings      boundary_share  0.2037    0.2024               -0.0012   -0.0213     0.0190          19           4263
both innings     wicket_per_ball  0.0525    0.0575                0.0050   -0.0018     0.0115          19           4263
   innings 1 runs_per_legal_ball  1.4786    1.4702               -0.0084   -0.1404     0.1283          19           2233
   innings 1           dot_share  0.3327    0.3274               -0.0054   -0.0375     0.0275          19           2233
   innings 1      boundary_share  0.2032    0.1953               -0.0079   -0.0337     0.0202          19           2233
   innings 1     wicket_per_ball  0.0516    0.0609                0.0093   -0.0007     0.0187          19           2233
   innings 2 runs_per_legal_ball  1.4606    1.4601               -0.0005   -0.1158     0.1111          19           2030
   innings 2           dot_share  0.3433    0.3547                0.0113   -0.0266     0.0500          19           2030
   innings 2      boundary_share  0.2041    0.2103                0.0062   -0.0172     0.0304          19           2030
   innings 2     wicket_per_ball  0.0533    0.0537                0.0003   -0.0108     0.0116          19           2030
```
[DATA] bootstrap: 2000 resamples of whole matches within each group (seeded). These are population-level, state-UNADJUSTED differences: they mix who plays, innings state and opposition quality, so they show size/uncertainty, not a causal knockout effect.

## E. (earlier base; superseded by stage3b section D) How much of a player's knockout sample is signal? (method-of-moments reliability, unadjusted per-ball values)

```
                                 role  players_league_ge  sigma_per_ball  tau_between_player  median_KO_balls_all_KO_players  KO_players  reliability_at_median_KO_n  reliability_at_league_median_n  n_for_reliability_0p5
     batter (bat runs per legal ball)                127           1.793               0.183                            17.5         128                       0.155                           0.825                 95.707
bowler (runs conceded per legal ball)                140           1.793               0.111                            41.0          92                       0.137                           0.606                259.087
```
[DATA/METHOD] tau = estimated between-player SD of true per-ball means (league sample, players with >=120 legal IPL league balls); sigma = per-ball SD; reliability = tau^2/(tau^2 + sigma^2/n). Unadjusted for state, so tau is inflated by role and exposure differences; adjusted tau is smaller and reliabilities lower. Treat these as an UPPER bound.
[DATA] batters with >=120 league and >=12 knockout IPL legal balls: 64; mean (KO - league) per-ball value -0.058 (SE 0.042); correlation league vs knockout per-ball means: 0.35; median KO balls in this group 46
[DATA] bowlers with >=120 league and >=12 knockout IPL legal balls: 75; mean (KO - league) per-ball value -0.047 (SE 0.041); correlation league vs knockout per-ball means: 0.10; median KO balls in this group 42

## F. (earlier base; superseded by stage3b section E) Population-level knockout deviation

```
   role  players  kappa_hat  kappa_ci_low  kappa_ci_high  psi_hat  psi_ci_low  psi_ci_high  sigma_per_ball  median_KO_balls  shrink_weight_on_own_KO_deviation_at_median  share_of_players_psi_boot_is_zero
batters       64    -0.0577       -0.1386         0.0252   0.1404         0.0       0.2399          1.7923             45.5                                       0.2183                              0.173
bowlers       75    -0.0472       -0.1296         0.0332   0.1338         0.0       0.2471          1.7923             42.0                                       0.1896                              0.239
```
[DATA/METHOD] d_i = knockout mean minus league mean per ball (players with >=120 league and >=12 knockout IPL legal balls); psi^2 = Var(d) minus average sampling variance, floored at 0; bootstrap over players. UNADJUSTED for match state, so this is a rough guide; the adjusted model replaces it in Stage 4. A shrink weight near 0 means a player's own knockout sample barely moves his estimate away from "league estimate + population shift".
[DATA] reference-weight candidates (preliminary proxies; the final value is computed once from the leverage model before any player result is viewed): {"IPL knockout share of IPL legal deliveries": 0.0519, "IPL knockout share of IPL overs 16-20 deliveries": 0.0495, "IPL knockout share of IPL matches (all, incl. excluded)": 0.0539, "IPL knockout share of all IPL+T20I legal deliveries in base": 0.0237}

## G. League-match importance: what the supplied fields do and do not support

[DATA] IPL league matches per team per season, ordering and result availability:
```
comp_name  teams  min  max  date_monotonic_by_match_number  match_numbers_contiguous  league_matches  no_winner  matches_per_date_max
 IPL 2022     10   14   14                            True                      True              70          0                     2
 IPL 2023     10   14   14                            True                      True              70          1                     2
 IPL 2024     10   14   14                            True                      True              70          3                     2
 IPL 2025     10   14   15                           False                      True              71          4                     2
 IPL 2026     10   14   14                            True                      True              70          1                     2
```
[DATA] T20I: 131 competitions; matches per competition: {"1": 1, "2": 13, "3": 80, "4": 3, "5": 25, "6": 3, "7": 4, "13": 1, "19": 1} (key = matches in the competition)
[DATA] Fields available for league-match importance: competition, season, `stage` (all IPL league matches carry the single value "League"), `match_number`, `match_date`, `win_team_id`, `result`. There is no points table, no qualification rule, no tie-break rule and no remaining-fixture/qualification information in the files.
[DATA/OPEN] Cumulative win-loss records could be computed from `win_team_id` (supported by the data), but converting a record into "how important was this league match" needs qualification rules (how many teams qualify, points for no-result, tie-breaks) that the supplied files do not contain. Therefore league-match tournament importance is NOT measurable here and no numerical importance score will be built.
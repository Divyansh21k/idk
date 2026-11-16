# Stage 2 investigation (generated). Labels: [DATA] derived from supplied files; [KNOW] general cricket convention (not verifiable from the files); [OPEN] unresolved.

## 1. Result-text formats (digits masked)

```
result
<team> Won by # wickets                                              272
<team> Won by # runs                                                 258
<team> Won by # Runs                                                  85
<team> Won by # Wickets                                               81
<team> won by # runs                                                  42
<team> won by # wickets                                               30
No Result                                                             21
Match Abandoned                                                       19
<team> Won by # Wkts                                                   7
<team> Won by # Runs (DLS method)                                      3
<team> Won by # run                                                    3
<team> won by # Runs                                                   2
<team> won by # run                                                    2
Rajasthan Royals Won By # Runs                                         2
Delhi Capitals Won By # Wickets                                        2
Mumbai Indians Won By # Wickets                                        2
<team> Won by # Wickets(D/L Method)                                    2
<team> Won by # wicket                                                 2
<team> Won by # wickets (DLS Method)                                   2
<team> Won by # runs (DLS method)                                      2
<team> Won by # Run                                                    1
<team> Won by # runs (D/L method)                                      1
Australia Won the one over Eliminator                                  1
Royal Challengers Bengaluru Won # Wkts                                 1
<team> Won by # wkts                                                   1
<team> won by # wicket                                                 1
Lucknow Super Giants Won #  Runs                                       1
<team> Won by # Wicket                                                 1
Match Tied                                                             1
<team> Won by # Runs(D/L Method)                                       1
Kolkata Knight Riders Won By # Runs                                    1
Kolkata Knight Riders Won By # Wickets                                 1
Gujarat Titans Won By # Wickets                                        1
Sunrisers Hyderabad Won By # Runs                                      1
Punjab Kings Won By #Runs                                              1
Royal Challengers Bengaluru Won By # Runs                              1
Punjab Kings Won By  # wickets                                         1
Royal Challengers Bengaluru Won  by # Runs                             1
Gujarat Titans Won By # Runs                                           1
<team> won by # Wickets                                                1
<team> Won by # wickets  (DLS method)                                  1
Sri Lanka won the super over                                           1
Bangladesh Won  by # Wickets                                           1
West Indies Won   by # runs                                            1
<team> won by # wickets (DLS)                                          1
England Won By # Wickets                                               1
<team> won by #runs (DLS Method)                                       1
India Won Super Over By # Runs                                         1
Zimbabwe Won By # Wicket                                               1
Ireland Won By # Wickets                                               1
Sri Lanka Won By # Wickets                                             1
Afghanistan Won By #Runs                                               1
<team> Won by # wickets (DLS)                                          1
<team> Won by # wickets(D/L Method)                                    1
India Tied with Srilanka (India Won the Super Over by # wickets)       1
<team> Won by # runs(DLS method)                                       1
Delhi Capitals Tied with Rajasthan Royals (DC won the Super Over)      1
Australia Won By # Wickets                                             1
<team> Won by # runs(DLS Method)                                       1
India won the Super Over(Match Tied)                                   1
Bangladesh A Won The Super Over                                        1
Pakistan A Won the super over                                          1
<team> Won by Super over (Match Tied)                                  1
<team> Won by # wickets(DLS Method)                                    1
```

[DATA] results that are not "<team> won by N runs/wickets" (tail text after margin, if any):
```
                                                           result  n
                                                        No Result 21
                                                  Match Abandoned 19
                            Australia Won the one over Eliminator  1
                                                       Match Tied  1
                                     Sri Lanka won the super over  1
                                  India Won Super Over By 10 Runs  1
 India Tied with Srilanka (India Won the Super Over by 2 wickets)  1
Delhi Capitals Tied with Rajasthan Royals (DC won the Super Over)  1
                             India won the Super Over(Match Tied)  1
                                  Bangladesh A Won The Super Over  1
                                    Pakistan A Won the super over  1
             Kolkata Knight Riders Won by Super over (Match Tied)  1
```
```
    res_tail  n
(D/L Method)  4
(D/L method)  1
(DLS Method)  5
(DLS method)  7
       (DLS)  2
```

## 2. Legal-delivery semantics: which extras types consume a legal ball? (empirical over-structure test)

[DATA] 30626 complete overs (an over followed by a later over in the same innings, innings 1-2). A correct illegal-delivery set should leave exactly 6 legal balls in each. Best 8 of 128 candidate sets:
```
                            illegal_set  complete_overs_not_6_legal  any_over_gt6_legal
                  {wide,Overstep,other}                           4                   1
          {wide,Overstep,other,Penalty}                           5                   1
        {wide,Overstep,other,RetireOut}                          10                   1
{wide,Overstep,other,Penalty,RetireOut}                          11                   1
                        {wide,Overstep}                         220                 244
                {wide,Overstep,Penalty}                         221                 244
              {wide,Overstep,RetireOut}                         226                 244
      {wide,Overstep,Penalty,RetireOut}                         227                 244
... (128 rows total)
```

[DATA] {wide,Overstep}: 220 bad complete overs; adding `other`: 4.
[DATA] Best-fitting illegal set in this file: ['wide', 'Overstep', 'other']
[DATA] deliveries where over_ball_num != position within the over (by innings_ball_num order): 0

## 3. The `other` extras category - actual records, no assumption


[DATA] value pattern of `other` (n=264): (runs, extras1_runs, extras_2_runs, is_wicket)
```
 runs  extras1_runs  extras_2_runs  is_wicket   n
    0             1              0      False 111
    0             1              0       True   3
    0             1              1      False   7
    0             1              4      False   7
    1             1              0      False  49
    2             1              0      False  18
    3             1              0      False   1
    4             1              0      False  42
    6             1              0      False  26
```

[DATA] value pattern of `Overstep` (n=576): (runs, extras1_runs, extras_2_runs, is_wicket)
```
 runs  extras1_runs  extras_2_runs  is_wicket   n
    0             1              0      False 215
    0             1              0       True   3
    0             1              1      False  12
    0             1              4      False   9
    1             1              0      False 173
    1             1              0       True   1
    2             1              0      False  32
    2             1              0       True   1
    3             1              0      False   2
    4             1              0      False  81
    6             1              0      False  47
```
[DATA] `other` by scope / season (compare share of all deliveries):
```
scope  season  deliveries  other  overstep
  IPL    2022       17909     25        47
  IPL    2023       17863     36        64
  IPL    2024       17103     19        56
  IPL    2025       17285     19        51
  IPL    2026       17527     24        39
OTHER    2024        3519      3         9
OTHER    2025        3466      1         2
 T20I    2022       21718     24        61
 T20I 2022/23        2838      4         6
 T20I    2023       14386     13        46
 T20I 2023/24         739      1         0
 T20I    2024       23672     34        65
 T20I 2024/25         754      1         6
 T20I    2025       26661     33        78
 T20I    2026       15559     27        46
```
[DATA] matches / bowlers with `other`: 215 matches, 145 bowlers; top matches by count:
```
 match_id  n_other
    36096        5
    42784        4
    20249        3
    32618        3
    36562        3
    45391        3
    13614        2
    21407        2
```
[DATA] 12 sample `other` deliveries with the previous and next delivery:
```
 case  pos  match_id  inn  over  ob  ib              bowler  runs     ext  e1  e2   wkt   dism
  532 prev     13513    1     9   6  56           Moeen Ali     1     NaN   0   0 False    NaN
  532 THIS     13513    1    10   1  57         Tymal Mills     0   other   1   0 False    NaN
  532 next     13513    1    10   2  58         Tymal Mills     6     NaN   0   0 False    NaN
 1079 prev     13515    1    16   5  98       Saqib Mahmood     1     NaN   0   0 False    NaN
 1079 THIS     13515    1    16   6  99       Saqib Mahmood     0   other   1   0 False    NaN
 1079 next     13515    1    16   7 100       Saqib Mahmood     0     NaN   0   0 False    NaN
 1226 prev     13515    2    19   4 118    Sheldon Cottrell     0 legbyes   2   0 False    NaN
 1226 THIS     13515    2    19   5 119    Sheldon Cottrell     2   other   1   0 False    NaN
 1226 next     13515    2    19   6 120    Sheldon Cottrell     0     NaN   0   0 False    NaN
 2588 prev     13614    1    18   4 110      Mitchell Starc     1     NaN   0   0 False    NaN
 2588 THIS     13614    1    18   5 111      Mitchell Starc     0   other   1   4 False    NaN
 2588 next     13614    1    18   6 112      Mitchell Starc     1     NaN   0   0 False    NaN
 2609 prev     13614    2     1   6   6  Maheesh Theekshana     0     NaN   0   0 False    NaN
 2609 THIS     13614    2     2   1   7      Nuwan Thushara     0   other   1   0 False    NaN
 2609 next     13614    2     2   2   8      Nuwan Thushara     0 legbyes   1   0 False    NaN
 3309 prev     14094    1    19   6 118         Shivam Mavi     4     NaN   0   0 False    NaN
 3309 THIS     14094    1    19   7 119         Shivam Mavi     6   other   1   0 False    NaN
 3309 next     14094    1    19   8 120         Shivam Mavi     0     NaN   0   0 False    NaN
 4413 prev     14098    2    19   8 118         Trent Boult     1     NaN   0   0 False    NaN
 4413 THIS     14098    2    20   1 119 Nathan Coulter Nile     0   other   1   0 False    NaN
 4413 next     14098    2    20   2 120         Riyan Parag     1     NaN   0   0 False    NaN
 5012 prev     14101    1    17   3 104         Tim Southee     6     NaN   0   0 False    NaN
 5012 THIS     14101    1    17   4 105         Tim Southee     0   other   1   0 False    NaN
 5012 next     14101    1    17   5 106         Tim Southee     1     NaN   0   0 False    NaN
 5365 prev     14102    2    19   8 121     Prasidh Krishna     4     NaN   0   0 False    NaN
 5365 THIS     14102    2    19   9 122     Prasidh Krishna     0   other   1   0  True RunOut
 5365 next     14102    2    19  10 123     Prasidh Krishna     0     NaN   0   0 False    NaN
 6575 prev     14107    2    16   4  94         Daniel Sams     6     NaN   0   0 False    NaN
 6575 THIS     14107    2    16   5  95         Daniel Sams     2   other   1   0 False    NaN
 6575 next     14107    2    16   6  96         Daniel Sams     4     NaN   0   0 False    NaN
 6782 prev     14108    2    13   6  80         Lalit Yadav     2     NaN   0   0 False    NaN
 6782 THIS     14108    2    14   1  81       Anrich Nortje     6   other   1   0 False    NaN
 6782 next     14108    2    14   2  82       Anrich Nortje     1     NaN   0   0 False    NaN
 6797 prev     14108    2    16   2  95       Anrich Nortje     0     NaN   0   0 False    NaN
 6797 THIS     14108    2    16   3  96       Anrich Nortje     0   other   1   0 False    NaN
 6797 next     14108    2    16   4  97       Kuldeep Yadav     1     NaN   0   0 False    NaN
```
[OPEN] The files give no label definition for `other`. What the data supports: its value pattern matches `Overstep` (1 penalty run in extras1, bat runs allowed), and the over-structure test above shows whether treating it as a non-legal delivery makes overs complete. The *name/meaning* (e.g. which kind of no-ball) cannot be resolved from the supplied data.

[DATA] extras_2_runs > 0 by extras_type:
```
extras_type  size  sum  max
   Overstep    21   48    4
      other    14   35    4
```
[DATA] `Penalty` record(s):
```
 match_id  innings  overid  over_ball_num  innings_ball_num  runs  extras1_runs  extras_2_runs
    16753        2       6              4                34     0             5              0
```

## 4. Innings reconciliation (totals, extras, legal balls, wickets)

[DATA] innings rows: 1724 (innings 1: 867, 2: 845, 3: 6, 4: 6). Legal balls/innings (innings 1-2): max 120, median 120.0.
[DATA] innings with >120 legal balls: 0; with wickets >10: 0; innings where max(overid) != ceil(legal/6): 1
```
 match_id  innings scope  team  rows  bat  e1  e2  wkts  maxover  legal  T_bat_e1_e2  T_bat_e1  overs_by_legal
    24353        2  T20I    18   106  168  11   0     1       18    102          179       179            17.0
```

[DATA] "won by N runs/wickets" matches with both innings in ball-by-ball: 833  (non-revised: 809, revised: 24)
- non-revised: n=809; margin reconciles with total=bat+extras1+extras2: 804; with total=bat+extras1 only: 776; winner team named in result is a match team: 809; win_team_id agrees with result text: 809
- revised (D/L-type): n=24; margin reconciles with total=bat+extras1+extras2: 11; with total=bat+extras1 only: 11; winner team named in result is a match team: 24; win_team_id agrees with result text: 24
- by unit (non-revised): {"run": [402, 398], "wicket": [407, 406]}  [n, reconciled]

[DATA] Reconciliation failures (total=bat+e1+e2), all 18 records (exception file s2_result_reconciliation_failures.csv):
```
 match_id scope  revised                                             result  T1_a  T2_a  wk1  wk2  legal1  legal2  winner_batted_first  win_team_id_agrees
    13612  T20I     True              Australia Won by 20 runs (D/L method)   149   122    9    8     120     114                 True                True
    14130   IPL    False                  Lucknow Super Giants Won 36  Runs   167   130    6    8     119     119                 True                True
    16754  T20I     True               Ireland Won by 7 Wickets(D/L Method)    95    56    5    3      90      40                False                True
    20182   IPL    False             Punjab Kings Won by 7 Runs(D/L Method)   191   146    5    7     120      96                 True                True
    20190   IPL    False              Lucknow Super Giants Won by 6 wickets   121   127    8    5     120      96                False                True
    21586   IPL     True Chennai Super Kings Won by 5 wickets  (DLS method)   214   171    4    5     120      90                False                True
    21070  T20I     True             Bangladesh Won by 22 Runs (DLS method)   207    81    5    5     116      48                 True                True
    24822  T20I    False                   India Won by 2 Runs (DLS method)   139    47    7    2     120      41                False                True
    28046  T20I     True                South Africa won by 5 wickets (DLS)   180   154    7    5     117      83                False                True
    28334  T20I    False             New Zealand won by 17runs (DLS Method)   110    95   10    5     116      88                False                True
    29984  T20I     True              Australia Won by 27 Runs (DLS method)   118    98    4    3      64      60                 True                True
    34428  T20I     True                 India Won by 7 wickets(D/L Method)   161    81    9    3     120      39                False                True
    36208  T20I     True            South Africa Won by 14 runs(DLS method)    97    54    5    5      47      30                 True                True
    40749   IPL     True       Gujarat Titans Won by 3 wickets (DLS Method)   155   147    8    7     120     114                False                True
    41851  T20I     True              West Indies Won by 6 runs(DLS Method)   114   118    3    6      60      60                 True                True
    50371   IPL     True    Lucknow Super Giants Won by 9 runs (DLS method)   209   203    3    6     114     114                 True                True
    48610  T20I     True                England Won by 11 runs (DLS method)   133   125   10    4      98      90                False                True
    48611  T20I     True               England Won by 6 wickets(DLS Method)   189   173    5    4     120     100                False                True
```

[DATA] matches with ball-by-ball whose result text is not a plain margin (tie / no result / abandoned / other), innings present:
```
 match_id scope                                                            result innings_present  win_team_id
    13613  T20I                             Australia Won the one over Eliminator             1,2         20.0
    15410  T20I                                                   Match Abandoned               1          NaN
    15546  T20I                                                         No Result               1          NaN
    17765  T20I                                                         No Result             1,2          NaN
    18532  T20I                                                        Match Tied             1,2          NaN
    20226   IPL                                                   Match Abandoned               1          NaN
    21176  T20I                                      Sri Lanka won the super over             1,2         27.0
    21406  T20I                                                   Match Abandoned               1          NaN
    28333  T20I                                                         No Result               1          NaN
    28962  T20I                                   India Won Super Over By 10 Runs             1,2         18.0
    31707  T20I                                                         No Result               1          NaN
    37353  T20I                                                         No Result               1          NaN
    34429  T20I  India Tied with Srilanka (India Won the Super Over by 2 wickets)         1,2,3,4         18.0
    35424  T20I                                                         No Result               1          NaN
    40725   IPL Delhi Capitals Tied with Rajasthan Royals (DC won the Super Over)         1,2,3,4          7.0
    40737   IPL                                                         No Result             1,2          NaN
    40748   IPL                                                         No Result               1          NaN
    40751   IPL                                                         No Result               1          NaN
    39983  T20I                                                         No Result               1          NaN
    39985  T20I                                                         No Result               1          NaN
    41975  T20I                                                         No Result               1          NaN
    41979  T20I                                                         No Result               1          NaN
    45390  T20I                                                         No Result               1          NaN
    45512  T20I                              India won the Super Over(Match Tied)         1,2,3,4         18.0
    45908  T20I                                                         No Result               1          NaN
    46311  T20I                                                         No Result               1          NaN
    46747  T20I                                                         No Result               1          NaN
    46749  T20I                                                         No Result               1          NaN
    47968  T20I                                                         No Result               1          NaN
    48027 OTHER                                   Bangladesh A Won The Super Over         1,2,3,4       3093.0
    48029 OTHER                                     Pakistan A Won the super over         1,2,3,4        341.0
    50136   IPL                                                         No Result               1          NaN
    50359   IPL              Kolkata Knight Riders Won by Super over (Match Tied)         1,2,3,4          8.0
    50408  T20I                                                         No Result               1          NaN
```

## 5. Innings that do not look like complete 20-over or all-out innings (innings 1-2)

[DATA] 467 innings with <120 legal balls and <10 wickets: explained by successful chase 394; in revised-target matches 51; unexplained remainder:
```
 match_id scope  innings  legal  wkts  T_bat_e1_e2                            match_result                            match_result
    14130   IPL        1    119     6          167       Lucknow Super Giants Won 36  Runs       Lucknow Super Giants Won 36  Runs
    14130   IPL        2    119     8          130       Lucknow Super Giants Won 36  Runs       Lucknow Super Giants Won 36  Runs
    14164   IPL        1    119     8          156           Punjab Kings Won by 5 wickets           Punjab Kings Won by 5 wickets
    15409  T20I        2    101     9           87                    India Won by 82 runs                    India Won by 82 runs
    15795  T20I        1     72     4          108                  India Won by 7 Wickets                  India Won by 7 Wickets
    17627  T20I        2    111     9          178             South Africa Won by 49 Runs             South Africa Won by 49 Runs
    18532  T20I        2     54     4           75                              Match Tied                              Match Tied
    20182   IPL        2     96     7          146  Punjab Kings Won by 7 Runs(D/L Method)  Punjab Kings Won by 7 Runs(D/L Method)
    20226   IPL        1    116     7          125                         Match Abandoned                         Match Abandoned
    21406  T20I        1    113     5          164                         Match Abandoned                         Match Abandoned
    23674  T20I        1    102     7          116 Bangladesh Won by 6 Wickets(D/L Method) Bangladesh Won by 6 Wickets(D/L Method)
    24822  T20I        2     41     2           47        India Won by 2 Runs (DLS method)        India Won by 2 Runs (DLS method)
    28333  T20I        1     66     2           72                               No Result                               No Result
    28334  T20I        2     88     5           95  New Zealand won by 17runs (DLS Method)  New Zealand won by 17runs (DLS Method)
    29983  T20I        2    102     9          102                Australia Won by 72 Runs                Australia Won by 72 Runs
    31278   IPL        1     96     7          157    Kolkata Knight Riders Won by 18 runs    Kolkata Knight Riders Won by 18 runs
    31278   IPL        2     96     8          139    Kolkata Knight Riders Won by 18 runs    Kolkata Knight Riders Won by 18 runs
    37353  T20I        1     30     0           44                               No Result                               No Result
    40737   IPL        2      6     0            7                               No Result                               No Result
    40751   IPL        1     61     1          122                               No Result                               No Result
    41979  T20I        1     29     0           52                               No Result                               No Result
    42743  T20I        2    114     9          144                 Pakistan Won by 57 runs                 Pakistan Won by 57 runs
    45908  T20I        1    110     4          164                               No Result                               No Result
    47968  T20I        1     39     1           38                               No Result                               No Result
    48514  T20I        1     72     6          160                Sri Lanka Won by 14 runs                Sri Lanka Won by 14 runs
    48514  T20I        2     72     8          146                Sri Lanka Won by 14 runs                Sri Lanka Won by 14 runs
    48917  T20I        2    101     9           96                Pakistan Won by 111 runs                Pakistan Won by 111 runs
    50136   IPL        1     22     2           25                               No Result                               No Result
    50407  T20I        2    117     9          223              West Indies Won by 24 runs              West Indies Won by 24 runs
```

## 6. Innings 3 and 4 matches

```
 match_id scope                                comp       date                 home                  away                                                            result  win_team_id   rev                    inn1                    inn2                inn3                inn4
    34429  T20I India in Sri Lanka T20I Series 2024 2024-07-30            Sri Lanka                 India  India Tied with Srilanka (India Won the Super Over by 2 wickets)         18.0 False   137/9 (120b, team 18)   137/8 (120b, team 27)   2/2 (3b, team 27)   4/0 (1b, team 18)
    40725   IPL                            IPL 2025 2025-04-16       Delhi Capitals      Rajasthan Royals Delhi Capitals Tied with Rajasthan Royals (DC won the Super Over)          7.0 False    188/5 (120b, team 7)    188/4 (120b, team 3)   11/2 (5b, team 3)   13/0 (4b, team 7)
    45512  T20I                       Asia Cup 2025 2025-09-26                India             Sri Lanka                              India won the Super Over(Match Tied)         18.0 False   202/5 (120b, team 18)   202/5 (120b, team 27)   2/2 (5b, team 27)   3/0 (1b, team 18)
    48027 OTHER          Asia Cup Rising Stars 2025 2025-11-21         Bangladesh A               India A                                   Bangladesh A Won The Super Over       3093.0 False 194/6 (120b, team 3093)  194/6 (120b, team 222)  0/2 (2b, team 222) 1/1 (1b, team 3093)
    48029 OTHER          Asia Cup Rising Stars 2025 2025-11-23         Bangladesh A            Pakistan A                                     Pakistan A Won the super over        341.0 False 125/10 (120b, team 341) 125/9 (120b, team 3093) 6/2 (3b, team 3093)  7/0 (4b, team 341)
    50359   IPL                            IPL 2026 2026-04-26 Lucknow Super Giants Kolkata Knight Riders              Kolkata Knight Riders Won by Super over (Match Tied)          8.0 False    155/7 (120b, team 8) 155/8 (120b, team 3509) 1/2 (3b, team 3509)    4/0 (1b, team 8)
```
[DATA] matches with innings 3/4: 6; result types in ties: tie-results in file = 5; tie-result matches that have innings 3/4: 4
[DATA] all tie-result matches:
```
 match_id scope match_date            home_team             away_team                                                            result  win_team_id  has_innings34
    18532  T20I 2022-11-22          New Zealand                 India                                                        Match Tied          NaN          False
    34429  T20I 2024-07-30            Sri Lanka                 India  India Tied with Srilanka (India Won the Super Over by 2 wickets)         18.0           True
    40725   IPL 2025-04-16       Delhi Capitals      Rajasthan Royals Delhi Capitals Tied with Rajasthan Royals (DC won the Super Over)          7.0           True
    45512  T20I 2025-09-26                India             Sri Lanka                              India won the Super Over(Match Tied)         18.0           True
    50359   IPL 2026-04-26 Lucknow Super Giants Kolkata Knight Riders              Kolkata Knight Riders Won by Super over (Match Tied)          8.0           True
```

## 7. Revised-target matches (any of first_inn_revised_overs / second_inn_revised_overs / revised_target non-null)

[DATA] 34 matches; revised_target non-null 23; first-inn overs revised 25; second-inn 25; with ball-by-ball 34; revised_target == innings-1 total + 1: 8
```
 match_id scope  first_inn_revised_overs  second_inn_revised_overs  revised_target  T_bat_e1_e2_1  legal_1  T_bat_e1_e2_2  legal_2  wkts_2                                             result
    13612  T20I                      NaN                     114.0           143.0            149      120          122.0    114.0     8.0              Australia Won by 20 runs (D/L method)
    15410  T20I                    114.0                       NaN             NaN             28       21            NaN      NaN     NaN                                    Match Abandoned
    15546  T20I                     84.0                       NaN             NaN            105       78            NaN      NaN     NaN                                          No Result
    16753  T20I                     66.0                       NaN             NaN            132       66          105.0     66.0    10.0                         Afghanistan Won by 27 Runs
    16754  T20I                      NaN                      42.0            56.0             95       90           56.0     40.0     3.0               Ireland Won by 7 Wickets(D/L Method)
    17395  T20I                     48.0                      48.0            91.0             90       48           92.0     44.0     4.0                             India Won by 6 Wickets
    17765  T20I                     72.0                      72.0           130.0            112       72           30.0     23.0     3.0                                          No Result
    21586   IPL                      NaN                      90.0           171.0            214      120          171.0     90.0     5.0 Chennai Super Kings Won by 5 wickets  (DLS method)
    19959  T20I                     66.0                       NaN             NaN            131       66          132.0     63.0     7.0                       West Indies won by 3 wickets
    21070  T20I                      NaN                      48.0           104.0            207      116           81.0     48.0     5.0             Bangladesh Won by 22 Runs (DLS method)
    21071  T20I                    102.0                     102.0           203.0            202      102          125.0    102.0     9.0                          Bangladesh Won by 77 Runs
    28046  T20I                      NaN                      90.0           152.0            180      117          154.0     83.0     5.0                South Africa won by 5 wickets (DLS)
    29984  T20I                      NaN                      60.0           126.0            118       64           98.0     60.0     3.0              Australia Won by 27 Runs (DLS method)
    31707  T20I                     30.0                       NaN             NaN              2        2            NaN      NaN     NaN                                          No Result
    37354  T20I                     42.0                      42.0            94.0             93       42           64.0     42.0     9.0                           Australia Won by 29 runs
    36098  T20I                     78.0                      78.0           116.0            108       78          116.0     56.0     2.0                 West Indies Won by 8 wickets (DLS)
    34428  T20I                      NaN                      48.0            78.0            161      120           81.0     39.0     3.0                 India Won by 7 wickets(D/L Method)
    36208  T20I                     54.0                      30.0            69.0             97       47           54.0     30.0     5.0            South Africa Won by 14 runs(DLS method)
    40727   IPL                     84.0                      84.0            96.0             95       84           98.0     73.0     5.0                      Punjab Kings Won by 5 wickets
    40749   IPL                      NaN                     114.0           147.0            155      120          147.0    114.0     7.0       Gujarat Titans Won by 3 wickets (DLS Method)
    39809  T20I                     90.0                      90.0           136.0            135       90          137.0     79.0     5.0                       New Zealand Won by 5 wickets
    39983  T20I                     54.0                       NaN             NaN             77       54            NaN      NaN     NaN                                          No Result
    39985  T20I                    108.0                       NaN             NaN            142      108            NaN      NaN     NaN                                          No Result
    41851  T20I                     60.0                      60.0           125.0            114       60          118.0     60.0     6.0              West Indies Won by 6 runs(DLS Method)
    41975  T20I                    108.0                       NaN             NaN             97       58            NaN      NaN     NaN                                          No Result
    46311  T20I                     54.0                      54.0             NaN             16       13            NaN      NaN     NaN                                          No Result
    46749  T20I                     84.0                       NaN             NaN             38       22            NaN      NaN     NaN                                          No Result
    50137   IPL                     66.0                      66.0           151.0            150       66          123.0     66.0     9.0                    Rajasthan Royals Won by 27 runs
    50371   IPL                    114.0                     114.0           213.0            209      114          203.0    114.0     6.0    Lucknow Super Giants Won by 9 runs (DLS method)
    48610  T20I                    102.0                      90.0           115.0            133       98          125.0     90.0     4.0                England Won by 11 runs (DLS method)
    48611  T20I                      NaN                     102.0           168.0            189      120          173.0    100.0     4.0               England Won by 6 wickets(DLS Method)
    50190  T20I                     90.0                      90.0           103.0            102       86          104.0     70.0     4.0          New Zealand Won by 6 wickets (DLS Method)
    50408  T20I                     54.0                      54.0             NaN            118       46            NaN      NaN     NaN                                          No Result
    54711  T20I                     30.0                      30.0            33.0             32       30           30.0     30.0     3.0                                India Won by 2 runs
```
[DATA] combinations of (first_inn_revised_overs, second_inn_revised_overs) present: {"(-1.0, 42.0)": 1, "(-1.0, 48.0)": 2, "(-1.0, 60.0)": 1, "(-1.0, 90.0)": 2, "(-1.0, 102.0)": 1, "(-1.0, 114.0)": 2, "(30.0, -1.0)": 1, "(30.0, 30.0)": 1, "(42.0, 42.0)": 1, "(48.0, 48.0)": 1, "(54.0, -1.0)": 1, "(54.0, 30.0)": 1, "(54.0, 54.0)": 2, "(60.0, 60.0)": 1, "(66.0, -1.0)": 2, "(66.0, 66.0)": 1, "(72.0, 72.0)": 1, "(78.0, 78.0)": 1, "(84.0, -1.0)": 2, "(84.0, 84.0)": 1, "(90.0, 90.0)": 2, "(102.0, 90.0)": 1, "(102.0, 102.0)": 1, "(108.0, -1.0)": 2, "(114.0, -1.0)": 1, "(114.0, 114.0)": 1}
[OPEN] The file has no DLS par-score or interruption timeline, so ball-level pressure inside these matches cannot be modelled from the supplied data. Treatment decision belongs to Stage 3.

## 8. Timestamp discrepancies

[DATA] first-ball date minus match_date (days): {"-1": 9, "0": 841, "1": 14, "2": 3}; last-ball date minus match_date: {"-1": 8, "0": 795, "1": 61, "2": 3}
[DATA] match duration (last-first ts, hours): median 3.55, p95 4.14, max 24.52; matches with span >8h: 2
[DATA] matches where first or last ball date != match_date: 73 ({'T20I': 69, 'IPL': 4}). Records:
```
 match_id scope match_date            first_ts             last_ts  first_day_diff  last_day_diff    span_h
    13511  T20I 2022-01-22 2022-01-23 00:00:00 2022-01-23 04:28:50               1              1  4.480556
    13512  T20I 2022-01-23 2022-01-24 01:32:49 2022-01-24 05:04:32               1              1  3.528611
    13513  T20I 2022-01-26 2022-01-27 02:20:52 2022-01-27 05:29:55               1              1  3.150833
    13514  T20I 2022-01-29 2022-01-30 01:30:15 2022-01-30 04:51:20               1              1  3.351389
    13515  T20I 2022-01-30 2022-01-31 01:30:27 2022-01-31 05:01:58               1              1  3.525278
    15188   IPL 2022-05-25 2022-05-25 20:11:17 2022-05-26 00:19:38               0              1  4.139167
    15546  T20I 2022-07-02 2022-07-03 00:43:30 2022-07-03 02:30:20               1              1  1.780556
    15547  T20I 2022-07-03 2022-07-03 23:24:14 2022-07-04 02:42:06               0              1  3.297778
    15548  T20I 2022-07-07 2022-07-07 23:33:12 2022-07-08 02:38:20               0              1  3.085556
    15795  T20I 2022-06-26 2022-06-26 23:20:09 2022-06-27 01:17:52               0              1  1.961944
    15796  T20I 2022-06-28 2022-06-28 21:01:35 2022-06-29 00:41:34               0              1  3.666389
    16040  T20I 2022-07-07 2022-07-07 22:31:18 2022-07-08 02:04:31               0              1  3.553611
    16063  T20I 2022-08-01 2022-08-01 23:02:05 2022-08-02 02:27:17               0              1  3.420000
    16064  T20I 2022-08-02 2022-08-02 21:30:10 2022-08-03 01:00:47               0              1  3.510278
    16065  T20I 2022-08-06 2022-08-06 20:47:33 2022-08-07 00:22:15               0              1  3.578333
    16258  T20I 2022-07-18 2022-07-18 20:31:34 2022-07-19 00:00:06               0              1  3.475556
    16315  T20I 2022-07-27 2022-07-27 23:00:22 2022-07-28 02:28:14               0              1  3.464444
    16316  T20I 2022-07-28 2022-07-28 23:02:46 2022-07-29 02:17:50               0              1  3.251111
    16646  T20I 2022-08-03 2022-08-03 23:03:46 2022-08-04 02:23:32               0              1  3.329444
    16647  T20I 2022-08-05 2022-08-05 23:00:53 2022-08-06 02:18:29               0              1  3.293333
    16753  T20I 2022-08-15 2022-08-15 22:01:13 2022-08-16 00:07:55               0              1  2.111667
    16866  T20I 2022-08-24 2022-08-24 21:30:22 2022-08-25 01:00:34               0              1  3.503333
    19961  T20I 2023-03-28 2023-03-28 21:31:00 2023-03-29 01:18:18               0              1  3.788333
    20208   IPL 2023-04-20 2023-04-20 20:31:28 2023-04-21 00:18:34               0              1  3.785000
    20250   IPL 2023-05-21 2023-05-21 20:25:10 2023-05-22 00:07:15               0              1  3.701389
    20878  T20I 2023-03-24 2023-03-24 21:32:43 2023-03-25 00:39:59               0              1  3.121111
    20879  T20I 2023-03-26 2023-03-26 21:34:20 2023-03-27 00:57:55               0              1  3.393056
    20880  T20I 2023-03-27 2023-03-27 21:32:17 2023-03-28 00:56:40               0              1  3.406389
    21403  T20I 2023-04-14 2023-04-14 21:31:30 2023-04-15 00:49:19               0              1  3.296944
    21404  T20I 2023-04-15 2023-04-15 21:29:54 2023-04-16 00:52:40               0              1  3.379444
    21405  T20I 2023-04-17 2023-04-17 21:30:20 2023-04-18 01:15:43               0              1  3.756389
    21407  T20I 2023-04-24 2023-04-24 21:30:01 2023-04-25 01:00:33               0              1  3.508889
    21586   IPL 2023-05-29 2023-05-29 19:31:22 2023-05-30 01:33:35               0              1  6.036944
    24354  T20I 2023-08-13 2023-08-13 00:00:00 2023-08-14 00:31:07               0              1 24.518611
    25155  T20I 2023-08-30 2023-08-30 21:31:48 2023-08-31 00:51:58               0              1  3.336111
    25156  T20I 2023-09-01 2023-09-01 21:30:53 2023-09-02 00:26:52               0              1  2.933056
    25158  T20I 2023-08-30 2023-08-30 22:33:25 2023-08-31 01:24:25               0              1  2.850000
    25159  T20I 2023-09-01 2023-09-01 22:31:00 2023-09-02 01:23:22               0              1  2.872778
    25161  T20I 2023-09-05 2023-09-05 22:32:14 2023-09-06 01:31:40               0              1  2.990556
    28046  T20I 2023-12-12 2023-12-12 20:30:54 2023-12-13 00:25:06               0              1  3.903333
    28057  T20I 2023-12-07 2023-12-07 22:04:18 2023-12-08 01:36:22               0              1  3.534444
    28064  T20I 2023-12-14 2023-12-14 23:00:18 2023-12-15 02:26:03               0              1  3.429167
    28065  T20I 2023-12-16 2023-12-16 23:00:11 2023-12-17 02:27:29               0              1  3.455000
    30728  T20I 2024-03-15 2024-03-15 21:31:22 2024-03-16 01:05:01               0              1  3.560833
    30729  T20I 2024-03-17 2024-03-17 21:29:58 2024-03-18 01:01:10               0              1  3.520000
    30730  T20I 2024-03-18 2024-03-18 21:30:34 2024-03-19 00:55:46               0              1  3.420000
    32613  T20I 2024-05-30 2024-05-30 23:01:48 2024-05-31 02:15:52               0              1  3.234444
    36562  T20I 2024-09-11 2024-09-11 23:17:16 2024-09-12 02:41:08               0              1  3.397778
    36563  T20I 2024-09-13 2024-09-13 23:00:33 2024-09-14 02:19:10               0              1  3.310278
    37015  T20I 2024-09-29 2024-09-29 21:01:54 2024-09-30 00:47:57               0              1  3.767500
    37349  T20I 2024-11-10 2024-11-09 20:00:15 2024-11-09 23:56:50              -1             -1  3.943056
    37350  T20I 2024-11-11 2024-11-10 20:01:28 2024-11-10 23:12:03              -1             -1  3.176389
    37351  T20I 2024-11-15 2024-11-14 20:54:18 2024-11-15 00:40:22              -1              0  3.767778
    37353  T20I 2024-11-18 2024-11-17 20:01:45 2024-11-17 20:23:07              -1             -1  0.356111
    38626  T20I 2024-12-09 2024-12-11 11:35:44 2024-12-11 15:03:13               2              2  3.458056
    38627  T20I 2024-12-11 2024-12-13 11:34:14 2024-12-13 14:50:36               2              2  3.272778
    38628  T20I 2024-12-12 2024-12-14 11:33:14 2024-12-14 15:27:04               2              2  3.897222
    41505  T20I 2025-07-20 2025-07-21 00:02:00 2025-07-21 03:31:42               1              1  3.495000
    41506  T20I 2025-07-22 2025-07-23 00:01:02 2025-07-23 03:17:41               1              1  3.277500
    41507  T20I 2025-07-25 2025-07-25 23:02:05 2025-07-26 02:21:40               0              1  3.326389
    41508  T20I 2025-07-26 2025-07-26 23:00:30 2025-07-27 03:42:05               0              1  4.693056
    41509  T20I 2025-07-28 2025-07-28 23:00:56 2025-07-29 02:26:56               0              1  3.433333
    41510  T20I 2025-07-31 2025-08-01 00:02:21 2025-08-01 03:45:38               1              1  3.721389
    41511  T20I 2025-08-02 2025-08-03 00:03:04 2025-08-03 03:38:04               1              1  3.583333
    41512  T20I 2025-08-03 2025-08-04 00:01:05 2025-08-04 03:37:14               1              1  3.602500
    41851  T20I 2026-02-01 2026-01-31 17:16:20 2026-01-31 20:17:54              -1             -1  3.026111
    46250  T20I 2025-09-28 2025-09-29 14:32:02 2025-09-29 17:41:23               1              1  3.155833
    46941  T20I 2025-10-30 2025-10-29 12:00:40 2025-10-29 15:40:02              -1             -1  3.656111
    46942  T20I 2025-11-01 2025-10-31 12:01:33 2025-10-31 15:25:13              -1             -1  3.394444
    47976  T20I 2025-11-17 2025-11-18 13:02:15 2025-11-18 16:27:45               1              1  3.425000
... (73 rows total)
```
[DATA] hour-of-day (clock value in the timestamp) of each match's first innings-1 ball, by scope:
```
match_id  IPL  OTHER  T20I
ts                        
0           0      0    25
1           0      0     9
2           0      0     2
3           0      0     1
5           0      0     6
6           0      2    19
7           0      0     7
8           0      0    15
9           0     12     6
10         35      0     2
11          0      2    33
12          0      0    23
13          0      8    59
14        177      6    46
15         33      0    26
16          4      0    23
17          0      0    15
18          0      0     6
19        113      0    68
20          5      0    37
21          0      0    19
22          0      0     7
23          0      0    16
```
[DATA] within-innings timestamp decreases vs innings_ball_num order: 4; zero gaps: 39; gaps >30 min: 37
[OPEN] Column is named `delivery_ist_time` but values carry a "UTC" suffix; the files do not say which is correct. Use `innings_ball_num` for ordering, never the timestamp. If the clock hours above look like UTC-converted IST that is an inference, not a documented fact.

## 9. Dismissal and bowler-credit logic

[DATA] dismissal_type_id <-> dismissal_type:
```
 dismissal_type_id        dismissal_type    n
               1.0                Bowled 1775
               2.0                Caught 7557
               3.0                   LBW  709
               4.0                RunOut  600
               5.0                 Stump  214
               6.0            Hit Wicket   17
               9.0            Retire Out    6
              10.0 Obstracting the field    2
              10.0 Obstructing the field    1
```
[DATA] who was dismissed, by type:
```
       dismissal_type  non_striker  null  striker
               Bowled            0     0     1775
               Caught            0     0     7557
           Hit Wicket            0     0       17
                  LBW            0     0      709
Obstracting the field            1     0        1
Obstructing the field            0     0        1
           Retire Out            2     1        3
               RunOut          271     0      329
                Stump            0     0      214
```
[DATA] dismissal type x delivery type (extras_type):
```
       dismissal_type  (legal/none)  Overstep  byes  other  wide
               Bowled          1775         0     0      0     0
               Caught          7557         0     0      0     0
           Hit Wicket            17         0     0      0     0
                  LBW           709         0     0      0     0
Obstracting the field             2         0     0      0     0
Obstructing the field             1         0     0      0     0
           Retire Out             6         0     0      0     0
               RunOut           576         5     1      3    15
                Stump           189         0     0      0    25
```
[DATA/KNOW] Bowled/Caught/LBW recorded on a wide/Overstep/other delivery: 0 (not possible under standard laws [KNOW]; would indicate mis-labelled extras or dismissal): 
```
Empty DataFrame
Columns: [match_id, overid, over_ball_num, bowler_name, extras_type, dismissal_type]
Index: []
```
[KNOW] Proposed rule (standard convention; not stated in the files): bowler-credited = Bowled, Caught, LBW, Stump, Hit Wicket; not credited = RunOut, Retire Out, Obstructing the field (both spellings in the file).
[DATA] naive is_wicket=10881; bowler-credited by rule=10272; over-credit if is_wicket used: 609; bowlers with a different count: 248 of 561 with any wicket-flag delivery
[DATA] all Retire Out / Obstructing records:
```
 match_id  innings  overid  over_ball_num  innings_ball_num     bowler_name         striker_name     non_striker_name  dismissed_player_id         who  runs extras_type        dismissal_type
    14113        1      19              2               116      Avesh Khan  Ravichandran Ashwin      Shimron Hetmyer                305.0     striker     1         NaN            Retire Out
    20244        2      15              6                91    Mukesh Kumar     Liam Livingstone        Atharwa Taide               6466.0 non_striker     1         NaN            Retire Out
    21585        1      19              6               120   Akash Madhwal        Sai Sudharsan        Hardik Pandya              23450.0     striker     0         NaN            Retire Out
    31279        2      16              5               100      Avesh Khan      Ravindra Jadeja      Ruturaj Gaikwad                152.0     striker     1         NaN Obstracting the field
    37097        2       3              3                15 Shahnawaz Dhani         Lahiru Udara       Yashodha Lanka               2001.0 non_striker     2         NaN Obstracting the field
    40709        2      19              5               117  Shardul Thakur        Hardik Pandya Namboori Tilak Varma                  NaN        null     1         NaN            Retire Out
    40715        2      18              5               115 Lockie Ferguson Mahendra Singh Dhoni         Devon Conway               1941.0 non_striker     6         NaN            Retire Out
    41512        2      17              7               105      Haris Rauf         Roston Chase  Sherfane Rutherford               2687.0     striker     1         NaN            Retire Out
    50359        1       5              7                32    Prince Yadav Angkrish Raghuvanshi        Cameron Green              26906.0     striker     0         NaN Obstructing the field
```
[DATA] the 13 wicket-flag/dismissed-id anomaly records (actual rows):
```
scope  match_id  innings  overid  over_ball_num           bowler_name         striker_name     non_striker_name  is_wicket dismissal_type  dismissed_player_id       dismissed_name  runs extras_type
  IPL     14114        2      14              1         Rahul Tewatia       Rahul Tripathi      Kane Williamson      False            NaN               1440.0       Rahul Tripathi     6         NaN
 T20I     15610        1       6              6           Luke Jongwe      Darwish Rasooli    Najibullah Zadran      False            NaN               6433.0      Darwish Rasooli     0         NaN
 T20I     16064        2       2              4        Alzarri Joseph         Rohit Sharma     Suryakumar Yadav      False            NaN                126.0         Rohit Sharma     0         NaN
  IPL     20188        1      11              1   Ravichandran Ashwin       Shikhar Dhawan    Bhanuka Rajapaksa      False            NaN               2003.0    Bhanuka Rajapaksa     0         NaN
  IPL     20243        1      16              6         Cameron Green       Marcus Stoinis        Krunal Pandya      False            NaN               4219.0        Krunal Pandya     0         NaN
 T20I     20880        2      11              3 Ihsanullah Ihsanullah    Najibullah Zadran          Usman Ghani      False            NaN               2533.0    Najibullah Zadran     0         NaN
 T20I     28964        1      10              6           Aamer Jamal      Kane Williamson           Finn Allen      False            NaN               1568.0      Kane Williamson     4         NaN
 T20I     29926        2       9              4            Noor Ahmad      Pathum Nissanka    Wanindu Hasaranga      False            NaN               6931.0      Pathum Nissanka     6         NaN
 T20I     31709        1      13              3             Ish Sodhi           Usman Khan      Mohammad Rizwan      False            NaN               3024.0      Mohammad Rizwan     1         NaN
OTHER     37094        2       6              7         Eshan Malinga Mohammad Saif Hassan      Mohammad Sheikh      False            NaN               4780.0 Mohammad Saif Hassan     0         NaN
  IPL     40709        2      19              5        Shardul Thakur        Hardik Pandya Namboori Tilak Varma       True     Retire Out                  NaN                  NaN     1         NaN
  IPL     40725        2       6              4          Vipraj Nigam         Sanju Samson     Yashasvi Jaiswal      False            NaN               2258.0         Sanju Samson     0         NaN
  IPL     40763        2      18              5        Shardul Thakur       Kamindu Mendis         Aniket Verma      False            NaN               4904.0       Kamindu Mendis     1         NaN
```
[DATA] wickets per innings: {"0": 11, "1": 32, "2": 83, "3": 139, "4": 171, "5": 225, "6": 224, "7": 200, "8": 207, "9": 156, "10": 264}
[DATA] striker==non_striker record(s):
```
 match_id  innings  overid  over_ball_num  striker_id       striker_name   non_striker_name     bowler_name  runs  is_wicket
    37086        1      18              6        3550 Sharafuddin Ashraf Sharafuddin Ashraf Dushan Hemantha     1      False
```

## 10. Playing-XI issues

[DATA] played rows per team-match vs impact flags, by scope:
```
scope  n_played  n_impact  team_matches
  IPL        11         0           178
  IPL        12         1           552
  IPL        13         1             6
OTHER        11         0            60
 T20I        10         0             1
 T20I        11         0           930
 T20I        12         0             4
 T20I        16         0             1
 T20I        17         0             3
 T20I        19         0             1
 T20I        20         0             1
```
[DATA] team-matches that are NOT (11 played, 0 impact) or (12 played, 1 impact): 17 - actual records:
```
 match_id  team_id  n_played  n_impact  n_impact_off  n_dup_keys scope                                  comp_name match_date             home_team             away_team
    13613       20        17         0             0           6  T20I    Sri Lanka in Australia T20I Series 2022 2022-02-13             Australia             Sri Lanka
    13613       27        17         0             0           6  T20I    Sri Lanka in Australia T20I Series 2022 2022-02-13             Australia             Sri Lanka
    20880       78        12         0             0           0  T20I    Afghanistan v Pakistan T20I Series 2023 2023-03-27           Afghanistan              Pakistan
    21176       17        17         0             0           6  T20I  Sri Lanka in New Zealand T20I Series 2023 2023-04-02           New Zealand             Sri Lanka
    21176       27        16         0             0           5  T20I  Sri Lanka in New Zealand T20I Series 2023 2023-04-02           New Zealand             Sri Lanka
    21585        2        13         1             1           0   IPL                                   IPL 2023 2023-05-26        Gujarat Titans        Mumbai Indians
    28333       17        10         0             0           0  T20I Bangladesh in New Zealand T20I Series 2023 2023-12-29           New Zealand            Bangladesh
    28962       18        19         0             0           8  T20I      Afghanistan in India T20I Series 2024 2024-01-17                 India           Afghanistan
    28962       78        20         0             0           9  T20I      Afghanistan in India T20I Series 2024 2024-01-17                 India           Afghanistan
    29926       78        12         0             0           0  T20I  Afghanistan in Sri Lanka T20I Series 2024 2024-02-21             Sri Lanka           Afghanistan
    31272     3509        13         1             1           0   IPL                                   IPL 2024 2024-05-05  Lucknow Super Giants Kolkata Knight Riders
    32132       72        12         0             0           0  T20I    Zimbabwe in Bangladesh T20I Series 2024 2024-05-03            Bangladesh              Zimbabwe
    40039       18        12         0             0           0  T20I          England in India T20I Series 2025 2025-01-31                 India               England
    40749        2        13         1             1           0   IPL                                   IPL 2025 2025-05-06        Mumbai Indians        Gujarat Titans
    50354        2        13         1             1           0   IPL                                   IPL 2026 2026-04-23        Mumbai Indians   Chennai Super Kings
    50356        7        13         1             1           0   IPL                                   IPL 2026 2026-04-25        Delhi Capitals          Punjab Kings
    50386        8        13         1             1           0   IPL                                   IPL 2026 2026-05-20 Kolkata Knight Riders        Mumbai Indians
```
[DATA] XI batting_order vs bbb striker batting_order (mode) for batters present in both: agree 13716 of 13763; disagreements outside the 3 duplicate-XI matches: 7; inside: 40
[DATA] duplicate-XI keys: 35; keys where exactly one duplicate option equals the ball-by-ball batting order: 35; zero options equal: 0; more than one: 0
```
 match_id  team_id  player_id         options  bbb_order  n_options  n_matching               player
    13613       20        223      [5.0, 6.0]          5          2           1         Steven Smith
    13613       20        250      [2.0, 4.0]          2          2           1          Aaron Finch
    13613       20        838      [1.0, 4.0]          4          2           1        Glenn Maxwell
    13613       20       2639      [2.0, 6.0]          6          2           1       Marcus Stoinis
    13613       20       3539      [1.0, 3.0]          1          2           1        Ben McDermott
    13613       20       4736      [3.0, 5.0]          3          2           1          Josh Inglis
    13613       27       1100      [2.0, 5.0]          5          2           1     Dinesh Chandimal
    13613       27       2351      [2.0, 4.0]          2          2           1 Danushka Gunathilaka
    13613       27       2436      [1.0, 6.0]          6          2           1        Dasun Shanaka
    13613       27       4895      [4.0, 6.0]          4          2           1     Charith Asalanka
    13613       27       4902      [3.0, 5.0]          3          2           1     Avishka Fernando
    13613       27       6931      [1.0, 3.0]          1          2           1      Pathum Nissanka
    21176       17       2246      [3.0, 6.0]          3          2           1           Tom Latham
    21176       17       3323      [2.0, 6.0]          6          2           1        Jimmy Neesham
    21176       17       3374      [3.0, 5.0]          5          2           1         Mark Chapman
    21176       17       3700      [2.0, 5.0]          2          2           1          Tim Seifert
    21176       17       4106      [1.0, 4.0]          4          2           1       Daryl Mitchell
    21176       17      25534      [1.0, 4.0]          1          2           1           Chad Bowes
    21176       27       1481      [3.0, 4.0]          3          2           1         Kusal Perera
    21176       27       2407      [4.0, 5.0]          4          2           1  Dhananjaya de Silva
    21176       27       3672      [1.0, 2.0]          2          2           1         Kusal Mendis
    21176       27       4895      [2.0, 5.0]          5          2           1     Charith Asalanka
    21176       27       6931      [1.0, 3.0]          1          2           1      Pathum Nissanka
    28962       18         47      [3.0, 5.0]          3          2           1          Virat Kohli
    28962       18        126      [1.0, 2.0]          2          2           1         Rohit Sharma
    28962       18       2258      [3.0, 5.0]          5          2           1         Sanju Samson
    28962       18       4708 [2.0, 3.0, 6.0]          6          3           1          Rinku Singh
    28962       18       4755      [4.0, 6.0]          4          2           1          Shivam Dube
    28962       18       6819 [1.0, 2.0, 4.0]          1          3           1     Yashasvi Jaiswal
    28962       78       1107 [1.0, 3.0, 5.0]          5          3           1        Mohammad Nabi
    28962       78       2214 [1.0, 3.0, 4.0]          3          3           1        Gulbadin Naib
    28962       78       5808 [3.0, 4.0, 6.0]          6          3           1          Karim Janat
    28962       78       6448      [2.0, 5.0]          2          2           1       Ibrahim Zadran
    28962       78       6674      [1.0, 2.0]          1          2           1   Rahmanullah Gurbaz
    28962       78       6676      [4.0, 6.0]          4          2           1   Azmatullah Omarzai
```
[DATA] innings present in the three duplicate-XI matches (to test the "extra batting innings" explanation):
```
 match_id innings
    13613  [1, 2]
    21176  [1, 2]
    28962  [1, 2]
```
[DATA] ball-by-ball participants absent from XI for their team/match (14 participant-role rows):
```
 match_id scope  team_id  player_id       player        role  xi_rows_for_team_match
    37087 OTHER      272      36153  Syed Haider     striker                      15
    37087 OTHER      272      39444 Basil Hameed     striker                      15
    37092 OTHER      272      36153  Syed Haider     striker                      15
    37092 OTHER      272      39444 Basil Hameed     striker                      15
    37095 OTHER      272      36153  Syed Haider     striker                      15
    37095 OTHER      272      39444 Basil Hameed     striker                      15
    37087 OTHER      272      36153  Syed Haider non_striker                      15
    37087 OTHER      272      39444 Basil Hameed non_striker                      15
    37092 OTHER      272      39444 Basil Hameed non_striker                      15
    37095 OTHER      272      36153  Syed Haider non_striker                      15
    37095 OTHER      272      39444 Basil Hameed non_striker                      15
    37087 OTHER      272      39444 Basil Hameed      bowler                      15
    37092 OTHER      272      39444 Basil Hameed      bowler                      15
    37095 OTHER      272      39444 Basil Hameed      bowler                      15
```
[DATA] these participant-match pairs: 6; scopes {"OTHER": 14}
[DATA] XI rows absent from the (comp,team) squad but present in mapping under another team/competition: players [29833] (['Bashir Ahmad']), team [4444], comp [2670], is_played [False]
[DATA] is_played=True players who never appear as striker/non-striker/bowler in their match ("did not bat or bowl" - not an error):
```
scope  is_impact  has_batting_order   n
  IPL          0               True 335
  IPL          1               True  23
OTHER          0               True  22
 T20I          0               True 441
```
[DATA] is_played=True rows with null batting_order:
```
 match_id scope  team_id  player_id           player  is_impact  is_impact_off
    48512  T20I       25       7690        Saim Ayub          0              0
    48512  T20I       25       3091 Sahibzada Farhan          0              0
    48512  T20I       25      20327       Usman Khan          0              0
    48512  T20I       25       7696   Mohammad Wasim          0              0
    48512  T20I       25      20704     Salman Mirza          0              0
    48512  T20I       25       2921     Fakhar Zaman          0              0
    48512  T20I       25       2490   Mohammad Nawaz          0              0
    48512  T20I       25       5979      Abrar Ahmed          0              0
    48512  T20I       25       4926      Shadab Khan          0              0
    48512  T20I       25       5189    Faheem Ashraf          0              0
    48512  T20I       25       3489      Salman Agha          0              0
```
[DATA] matches with no XI rows: [{"match_id": 36210, "result": "Match Abandoned", "scope": "T20I"}, {"match_id": 41503, "result": "Match Abandoned", "scope": "T20I"}, {"match_id": 48513, "result": "Match Abandoned", "scope": "T20I"}]

## 11. Supplementary record-level checks

[DATA] result text mentions D/L or DLS vs revised_* fields populated:
```
 dls_text  False  True
    False    845    19
     True      4    15
```
[DATA] matches whose result text says D/L-DLS but have NO revised_* field: 4
```
 match_id scope match_date    home_team             away_team                                  result
    20182   IPL 2023-04-01 Punjab Kings Kolkata Knight Riders  Punjab Kings Won by 7 Runs(D/L Method)
    23674  T20I 2023-07-16   Bangladesh           Afghanistan Bangladesh Won by 6 Wickets(D/L Method)
    24822  T20I 2023-08-18      Ireland                 India        India Won by 2 Runs (DLS method)
    28334  T20I 2023-12-31  New Zealand            Bangladesh  New Zealand won by 17runs (DLS Method)
```
[DATA] revised_*_overs values: n=50, min 30.0, max 114.0, divisible by 6: 50, > 20: 50  -> values behave like BALLS (e.g. 114 = 19 overs), not overs, despite the column name
[DATA] first_inn_revised_overs == legal balls actually bowled in innings 1: 15 of 25
[DATA] second_inn_revised_overs == legal balls bowled in innings 2: 13 of 23 (chases that ended early on success/all-out are expected to be lower)
[DATA] IPL first-ball clock hour by season (a consistent time zone would give the same hours every season):
```
 hour  2022  2023  2024  2025  2026
   10     0     0    11    12    12
   14     0     0    59    59    59
   15    12    17     1     1     2
   16     0     1     0     2     1
   19    60    53     0     0     0
   20     2     3     0     0     0
```
[OPEN] IPL first-ball hours cluster at 14 and 19 across seasons: both are plausible start-clock values (14 = a 19:30 IST start expressed in UTC; 19 = a 19:30 start expressed in IST). The organiser files do not say which rows use which zone; whether the zone changes by season is shown above. Ordering/phase logic must not rely on timestamps.
[DATA] For each of the 13 anomalous rows: does the player named in dismissed_player_id (or, if null, each batter at the crease) still bat later in that innings? (a player who bats on cannot have been dismissed on that ball):
```
 match_id  innings  ball  is_wicket  dism_type               player role_on_ball  appears_after_in_innings
    14114        2    80      False        NaN       Rahul Tripathi      striker                     False
    15610        1    38      False        NaN      Darwish Rasooli      striker                     False
    16064        2    10      False        NaN         Rohit Sharma      striker                     False
    20188        1    64      False        NaN    Bhanuka Rajapaksa  non_striker                     False
    20243        1    99      False        NaN        Krunal Pandya  non_striker                     False
    20880        2    65      False        NaN    Najibullah Zadran      striker                     False
    28964        1    65      False        NaN      Kane Williamson      striker                     False
    29926        2    54      False        NaN      Pathum Nissanka      striker                     False
    31709        1    80      False        NaN      Mohammad Rizwan  non_striker                     False
    37094        2    38      False        NaN Mohammad Saif Hassan      striker                     False
    40709        2   117       True Retire Out        Hardik Pandya      striker                      True
    40709        2   117       True Retire Out Namboori Tilak Varma  non_striker                     False
    40725        2    36      False        NaN         Sanju Samson      striker                     False
    40763        2   116      False        NaN       Kamindu Mendis      striker                     False
```
[DATA] overs still not consistent with 6 legal balls under ['Overstep', 'other', 'wide'] (4 records):
```
 match_id  innings  overid  n  legal_best  complete  c_wide  c_Overstep  c_other  c_Penalty  c_byes  c_legbyes  c_RetireOut
    14130        1      14  5           5      True       0           0        0          0       0          0            0
    14130        2      14  6           5      True       1           0        0          0       0          0            0
    14164        1      14  5           5      True       0           0        0          0       0          0            0
    41509        1      12  7           7      True       0           0        0          0       0          0            0
```
[DATA] non-revised reconciliation failures - innings components:
```
 match_id  innings  bat  e1  e2  total  wkts  legal                                 result
    14130        1  159   8   0    167     6    119      Lucknow Super Giants Won 36  Runs
    14130        2  116  14   0    130     8    119      Lucknow Super Giants Won 36  Runs
    20182        1  187   4   0    191     5    120 Punjab Kings Won by 7 Runs(D/L Method)
    20182        2  140   6   0    146     7     96 Punjab Kings Won by 7 Runs(D/L Method)
    20190        1  117   4   0    121     8    120  Lucknow Super Giants Won by 6 wickets
    20190        2  110  17   0    127     5     96  Lucknow Super Giants Won by 6 wickets
    24822        1  132   7   0    139     7    120       India Won by 2 Runs (DLS method)
    24822        2   44   3   0     47     2     41       India Won by 2 Runs (DLS method)
    28334        1   99  11   0    110    10    116 New Zealand won by 17runs (DLS Method)
    28334        2   88   7   0     95     5     88 New Zealand won by 17runs (DLS Method)
```
[DATA] all wicket records, match 20190 innings 2 (result says 6 wickets, ball-by-ball has 5 wicket rows):
```
 overid  over_ball_num       bowler_name     striker_name dismissal_type  dismissed_player_id
      5              3  FazalHaq Farooqi      Kyle Mayers         Caught               2416.0
      6              6 Bhuvneshwar Kumar     Deepak Hooda         Caught               3648.0
     13              2       Umran Malik    Krunal Pandya         Caught               4219.0
     15              1       Adil Rashid     Lokesh Rahul            LBW                953.0
     15              2       Adil Rashid Romario Shepherd            LBW               6726.0
```
[DATA] XI batting_order vs ball-by-ball batting order disagreements outside the three duplicate-XI matches:
```
 match_id  team_id  player_id                  player  batting_order  bbb_order  is_impact
    48512       25       7690               Saim Ayub            NaN          2          0
    48512       25       3091        Sahibzada Farhan            NaN          1          0
    48512       25      20327              Usman Khan            NaN          5          0
    48512       25       2921            Fakhar Zaman            NaN          4          0
    48512       25       4926             Shadab Khan            NaN          6          0
    48512       25       3489             Salman Agha            NaN          3          0
    51385       21       8380 Mohammad Rishad Hossain            9.0          6          0
```

## 12. Bowler metadata: multiple bowling_type labels, pace_or_spin, bowl_speed

[DATA] bowlers with >1 bowling_type label: 47 of 647; with >1 pace_or_spin value: 0
[DATA] which label sets co-occur (most common):
```
                                                label_set  bowlers
                   Right-arm medium-fast | Right-arm Fast        6
                   Right-arm fast-medium | Right-arm Fast        4
                 Right-arm medium-fast | Right-arm medium        4
                        Right-arm Fast | Right-arm medium        4
                 Right-arm medium | Right-arm fast-medium        4
                 Right-arm medium | Right-arm medium-fast        4
                     Left-arm Fast | Left-arm fast-medium        3
                   Left-arm medium | Left-arm fast-medium        3
                 Right-arm fast-medium | Right-arm medium        2
                   Left-arm medium-fast | Left-arm medium        2
                   Right-arm Fast | Right-arm fast-medium        2
                        Right-arm medium | Right-arm Fast        2
            Right-arm fast-medium | Right-arm medium-fast        1
                   Right-arm Fast | Right-arm medium-fast        1
Right-arm medium | Right-arm fast-medium | Right-arm Fast        1
... (19 rows total)
```
[DATA] share of each multi-label bowler's deliveries carried by the minority label(s):
```
 bowler_id              bowler                                                    labels             shares matches_by_label
       332      Angelo Mathews                  Right-arm fast-medium | Right-arm medium        0.64 | 0.36            6 | 3
       470       Mohammad Amir                      Left-arm Fast | Left-arm fast-medium        0.77 | 0.23            5 | 2
      1071      Jaydev Unadkat                    Left-arm medium-fast | Left-arm medium        0.63 | 0.37          19 | 11
      1318       Andre Russell                    Right-arm fast-medium | Right-arm Fast        0.80 | 0.20          44 | 13
      1389         Sean Abbott             Right-arm fast-medium | Right-arm medium-fast        0.65 | 0.35           13 | 8
      2261       Harshal Patel                    Right-arm medium-fast | Right-arm Fast        0.79 | 0.21          61 | 18
      2399 Dushmantha Chameera                    Right-arm Fast | Right-arm medium-fast        0.54 | 0.46          29 | 24
      2411      Sandeep Sharma                    Right-arm medium-fast | Right-arm Fast        0.64 | 0.36          27 | 16
      2681        Taskin Ahmed                    Right-arm Fast | Right-arm fast-medium        0.56 | 0.44          26 | 20
      2756      Shashank Singh                  Right-arm medium-fast | Right-arm medium        0.67 | 0.33            4 | 4
      2878        Mohit Sharma                    Right-arm medium-fast | Right-arm Fast        0.76 | 0.24           25 | 8
      2933      Jasprit Bumrah                         Right-arm Fast | Right-arm medium        0.57 | 0.43          43 | 32
      2985           Mark Wood                    Right-arm fast-medium | Right-arm Fast        0.63 | 0.37            8 | 5
      3275      Alzarri Joseph                    Right-arm medium-fast | Right-arm Fast        0.71 | 0.29          38 | 15
      3298        Jofra Archer                    Right-arm Fast | Right-arm fast-medium        0.85 | 0.15           48 | 8
      3627  Andile Phehlukwayo                         Right-arm medium | Right-arm Fast        0.72 | 0.28            5 | 2
      3653          Avesh Khan Right-arm medium | Right-arm fast-medium | Right-arm Fast 0.68 | 0.26 | 0.06      54 | 20 | 5
      3660           Luke Wood                    Left-arm fast-medium | Left-arm medium        0.55 | 0.45           10 | 7
      4288       Navdeep Saini                         Right-arm medium | Right-arm Fast        0.81 | 0.19            4 | 1
      4373   Mustafizur Rahman                    Left-arm medium | Left-arm fast-medium        0.56 | 0.44          40 | 31
      4807       Joshua Little                      Left-arm Fast | Left-arm fast-medium        0.86 | 0.14           31 | 5
      4816       Khaleel Ahmed                    Left-arm medium | Left-arm fast-medium        0.69 | 0.31          37 | 19
      4842     Shamar Springer                  Right-arm medium | Right-arm fast-medium        0.87 | 0.13            9 | 2
      5562     Richard Gleeson                  Right-arm medium | Right-arm fast-medium        0.89 | 0.11            8 | 1
      6287         Yash Thakur                  Right-arm medium | Right-arm fast-medium        0.71 | 0.29           19 | 8
      6354     Spencer Johnson                      Left-arm Fast | Left-arm fast-medium        0.55 | 0.45          13 | 10
      6523 Blessing Muzarabani                    Right-arm fast-medium | Right-arm Fast        0.67 | 0.33          25 | 12
      6726    Romario Shepherd                    Right-arm fast-medium | Right-arm Fast        0.58 | 0.42          57 | 35
      7008        Gus Atkinson                  Right-arm medium | Right-arm medium-fast        0.82 | 0.18            3 | 1
      7094      Curtis Campher                  Right-arm medium | Right-arm medium-fast        0.81 | 0.19           22 | 7
      7312       Nandre Burger               Left-arm fast-medium | Left-arm medium-fast        0.72 | 0.28           16 | 6
      7690           Saim Ayub                  Right-arm offbreak | Right-arm Leg-Break        0.94 | 0.06           29 | 3
      7808        Marco Jansen                      Left-arm medium-fast | Left-arm Fast        0.61 | 0.39          37 | 23
      7905        Tanzim Sakib                  Right-arm fast-medium | Right-arm medium        0.80 | 0.20           25 | 6
      7912     Vikramjit Singh                  Right-arm medium-fast | Right-arm medium        0.93 | 0.07            3 | 1
      7920        Nathan Ellis                  Right-arm medium | Right-arm fast-medium        0.57 | 0.43          24 | 19
      8009     Junaid Siddique                         Right-arm Fast | Right-arm medium        0.61 | 0.39            9 | 6
      8221        Nitish Reddy                    Right-arm medium-fast | Right-arm Fast        0.91 | 0.09           36 | 3
      8661 Matheesha Pathirana                         Right-arm Fast | Right-arm medium        0.54 | 0.46          30 | 24
     19781       Mitchell Owen                  Right-arm medium | Right-arm medium-fast        0.79 | 0.21            3 | 1
     20005         Arshad Khan                    Left-arm medium | Left-arm fast-medium        0.73 | 0.27           19 | 6
     20310       Ahmed Daniyal                  Right-arm medium-fast | Right-arm medium        0.64 | 0.36            5 | 3
     25011       Liam Mccarthy                    Right-arm medium-fast | Right-arm Fast        0.63 | 0.37            2 | 1
     27960        Mayank Yadav                         Right-arm Fast | Right-arm medium        0.61 | 0.39           13 | 9
     27964       Anshul Kamboj                  Right-arm medium-fast | Right-arm medium        0.56 | 0.44          14 | 14
     29066      Zakary Foulkes                  Right-arm medium | Right-arm medium-fast        0.60 | 0.40           10 | 8
     42548 Muhammad Jawadullah                    Left-arm medium-fast | Left-arm medium        0.82 | 0.18           11 | 2
```
[DATA] (bowler,match) pairs where the label changes WITHIN a match: 0; label sets by match_date order - bowlers whose label changes over time in one direction vs flips back and forth is in the CSV (s2_bowlers_multiple_bowling_type.csv)
[DATA] number of label changes between consecutive matches per multi-label bowler (1 = clean one-time change; >1 = flip-flopping): {"1": 42, "2": 2, "3": 3}
[DATA] bowling_type x pace_or_spin:
```
          bowling_type pace_or_spin     n
     Left-arm Chinaman         Spin  4685
         Left-arm Fast         Pace  4453
  Left-arm fast-medium         Pace  7780
       Left-arm medium         Pace  6082
  Left-arm medium-fast         Pace 12492
        Right-arm Fast         Pace 26637
   Right-arm Leg-Break         Spin 28027
 Right-arm fast-medium         Pace 15380
      Right-arm medium         Pace 23919
 Right-arm medium-fast         Pace 27014
    Right-arm offbreak         Pace    12
    Right-arm offbreak         Spin 20936
Slow left-arm orthodox         Pace   117
Slow left-arm orthodox         Spin 23465
```
[OPEN] The files carry no definition for bowling_type. Whether multi-label bowlers are real changes of style or labelling noise cannot be established from the supplied data alone; the one-time vs flip-flop evidence above is the only discriminating information available.
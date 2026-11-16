# Stage 4 Step 1: data layer report (generated)

Raw SHA-256 (first 16): {"ball_by_ball": "01e2b4379edfbab6", "matches": "bb100ab84b8b9a15", "competitions": "507ceb7189f972d4", "playing_eleven": "7517c73722a28d5d", "teams": "a65e5922a9b3bf49", "competition_team_player_mapping": "1ded4e42a9336185"}

## Free-hit flag evidence [DATA]

free_hit deliveries: 918 (0.46% of all); deliveries following a no-ball-like delivery with a wide in between are included.
```
          population  deliveries  wicket_rate  boundary_rate  bowler_credited_wicket_rate
     free_hit (flag)         918       0.0044         0.3355                       0.0000
all other deliveries      200081       0.0544         0.1789                       0.0513
```
dismissal types on flagged free-hit deliveries: {"RunOut": 4}

## Sizes

```
                                   table   rows
                     deliveries_analysis 200999
                        matches_analysis    883
innings_analysis (innings 1-2, in scope)   1652
                 player_exposure_batters    816
                 player_exposure_bowlers    589
```

## Transfer-diagnostic feasibility (players with at least N eligible balls in BOTH IPL and T20I)

```
                      group  threshold_each_competition  players_IPL_ge  players_T20I_ge  players_both_ge
      batters (balls faced)                          60             164              295               87
      batters (balls faced)                         120             128              201               68
      batters (balls faced)                         300              84              108               37
bowlers (deliveries bowled)                          60             178              305               97
bowlers (deliveries bowled)                         120             145              214               79
bowlers (deliveries bowled)                         300              90              109               38
```
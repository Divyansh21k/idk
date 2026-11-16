# Stage 1 raw audit (generated)

SHA-256 of raw files:
```
{
 "ball_by_ball": "01e2b4379edfbab6a6e456d304cb3c70f554cb312ef93d9588f3f32a82cb396e",
 "matches": "bb100ab84b8b9a15160c1f2315cf675210131a30e779ec5079fd5403dcf56eef",
 "competitions": "507ceb7189f972d4e4f299ddcfc97f3c3247af1913f6291106f161fa8353fd9b",
 "playing_eleven": "7517c73722a28d5d61c808ccf0cbed315a8780586d02e946eb9a7f5daf011c27",
 "teams": "a65e5922a9b3bf49247b24fc9471782e700efb31f8dcc5042923238b87c50a5d",
 "competition_team_player_mapping": "1ded4e42a933618572d6e2c3a521c3257eb1844fab4456d567d77cbb2d3bbb12"
}
```

## ball_by_ball.csv  shape=(200999, 33)
- full-row duplicates: 0; duplicate-key extra rows ['match_id', 'innings', 'innings_ball_num']: 0

## matches.csv  shape=(883, 22)
- full-row duplicates: 0; duplicate-key extra rows ['match_id']: 0

## competitions.csv  shape=(141, 4)
- full-row duplicates: 0; duplicate-key extra rows ['comp_id']: 0

## playing_eleven.csv  shape=(28381, 9)
- full-row duplicates: 0; duplicate-key extra rows ['match_id', 'team_id', 'player_id']: 40

## teams.csv  shape=(353, 3)
- full-row duplicates: 0; duplicate-key extra rows ['comp_id', 'team_id']: 0

## competition_team_player_mapping.csv  shape=(6413, 6)
- full-row duplicates: 0; duplicate-key extra rows ['comp_id', 'team_id', 'player_id']: 0

## A. Scope
scope  match_format
IPL    T20               5
OTHER  T20               2
T20I   T20I            134

Matches by scope x season x has_bbb:
has_bbb        False  True 
scope season               
IPL   2022         0     74
      2023         0     74
      2024         3     71
      2025         1     74
      2026         0     74
OTHER 2024         0     15
      2025         0     15
T20I  2022         0     94
      2022/23      0     12
      2023         0     63
      2023/24      0      3
      2024         5    104
      2024/25      0      3
      2025         5    121
      2026         2     70

Result types: {"won": 838, "no_result": 21, "abandoned": 19, "tie": 5}

## B. Cross-file assertions (competition/team/match-specific)
 id                                                                                       relationship                                                                                                     description  rows_checked  violations status severity violations_if_only_global_id_lookup               violations_by_scope
 U1                               ball_by_ball: unique key ['match_id', 'innings', 'innings_ball_num']                                                                                               No duplicate keys        200999           0   PASS     hard                                                                      
 U2                                                                   matches: unique key ['match_id']                                                                                               No duplicate keys           883           0   PASS     hard                                                                      
 U3                                                               competitions: unique key ['comp_id']                                                                                               No duplicate keys           141           0   PASS     hard                                                                      
 U4                                    playing_eleven: unique key ['match_id', 'team_id', 'player_id']                                                                                               No duplicate keys         28381          75   FAIL     hard                                                          {"T20I": 75}
 U5                                                           teams: unique key ['comp_id', 'team_id']                                                                                               No duplicate keys           353           0   PASS     hard                                                                      
 U6                    competition_team_player_mapping: unique key ['comp_id', 'team_id', 'player_id']                                                                                               No duplicate keys          6413           0   PASS     hard                                                                      
 R1                                                            matches.comp_id -> competitions.comp_id                                                                     Every match belongs to a listed competition           883           0   PASS     hard                                                                      
 R2                                                              teams.comp_id -> competitions.comp_id                                                                  Every team row belongs to a listed competition           353           0   PASS     hard                                                                      
 R3                                                            mapping.comp_id -> competitions.comp_id                                                               Every mapping row belongs to a listed competition          6413           0   PASS     hard                                                                      
 R4                                               mapping (comp_id,team_id) -> teams (comp_id,team_id)                                                        Squad rows only for teams registered in that competition          6413           0   PASS     hard                                   0                                  
 R5                                          matches (comp_id,home_team_id) -> teams (comp_id,team_id)                                                                   Home team registered in the match competition           883           0   PASS     hard                                   0                                  
 R6                                          matches (comp_id,away_team_id) -> teams (comp_id,team_id)                                                                   Away team registered in the match competition           883           0   PASS     hard                                   0                                  
 R7                             matches.home/away_team (name) == teams.team_name for (comp_id,team_id)                                                                                  Team names agree between files           883           0   PASS     hard                                                                      
 R8                                                              matches: home_team_id != away_team_id                                                                                                  Teams distinct           883           0   PASS     hard                                                                      
 R9                                                 matches.toss_win_team_id (non-null) in {home,away}                                                                                     Toss winner is a match team           868           0   PASS     hard                                                                      
R10                                                      matches.win_team_id (non-null) in {home,away}                                                                                          Winner is a match team           842           0   PASS     hard                                                                      
R11                                        matches captain ids: (comp_id,team_id,player_id) -> mapping                                                          Captain belongs to that team squad in that competition          1677           0   PASS     hard                                   0                                  
R12            matches.man_of_the_match (non-zero): (comp_id, either match team, player_id) -> mapping                                       MoM id (semantics undocumented) is a squad player of one of the two teams           764           0   PASS     soft                                                                      
R13                                                                   ball_by_ball.match_id -> matches                                                                        Every delivery belongs to a listed match        200999           0   PASS     hard                                                                      
R14                              ball_by_ball (batting_team_id,bowling_team_id) == matches {home,away}                                                  Delivery teams are the two teams of that match, opposite sides        200999           0   PASS     hard                                                                      
R15                      ball_by_ball (comp_id,batting_team_id) and (comp_id,bowling_team_id) -> teams                                                              Delivery teams registered in the match competition        200999           0   PASS     hard                                                                      
R16                                                 ball_by_ball: one batting team per (match,innings)                                                                         Batting team constant within an innings          1712           0   PASS     hard                                                                      
R17                                                 ball_by_ball: innings 1 and 2 batting teams differ                                                                           Opposite teams bat in innings 1 and 2           845           0   PASS     hard                                                                      
R18                                  ball_by_ball participants: (comp_id,team_id,player_id) -> mapping Striker/non-striker (batting team) and bowler (bowling team) are squad members of that team in that competition         36419           0   PASS     hard                                   0                                  
R19          ball_by_ball participants: (match_id,team_id,player_id) -> playing_eleven[is_played=True]                                                      Participants listed as playing for that team in that match         36419          14   FAIL     hard                                  14                     {"OTHER": 14}
R20                ball_by_ball participants: (match_id,team_id,player_id) -> playing_eleven (any row)                                                        Participants appear in the XI table for that team at all         36419          14   FAIL     hard                                  14                     {"OTHER": 14}
R21                                                                 playing_eleven.match_id -> matches                                                                                XI rows belong to a listed match         28381           0   PASS     hard                                                                      
R22                                                 playing_eleven.team_id in {home,away} of its match                                                                             XI row team is a team in that match         28381           0   PASS     hard                                                                      
R23                                              playing_eleven (comp_id,team_id,player_id) -> mapping                                                              XI player is in the competition squad of that team         28381           5   FAIL     hard                                   0                      {"OTHER": 5}
R24                                      playing_eleven: a played player is on only one team per match                                                                     No player plays for both sides of one match         19674           0   PASS     hard                                                                      
R25                                         playing_eleven: both match teams present for each XI match                                                                                         Both teams have XI rows           880           0   PASS     hard                                                                      
R26                                                                 matches -> playing_eleven coverage                                                                                          Each match has XI rows           883           3   FAIL     soft                                                           {"T20I": 3}
R27                                    playing_eleven: <=1 captain among played players per team-match                                                                                     At most one captain flagged          1737           5   FAIL     soft                                                           {"T20I": 5}
R28                 ball_by_ball: dismissed_player_id in {striker_id, non_striker_id} of that delivery                                                                              Dismissed player was at the crease         10880           0   PASS     hard                                                                      
R29 ball_by_ball dismissed player: (match_id,batting team,player_id) -> playing_eleven[is_played=True]                                                              Dismissed batter is in that team XI for that match         10870           5   FAIL     hard                                                          {"OTHER": 5}
R30                                                         ball_by_ball: striker_id != non_striker_id                                                                             Two different batters at the crease        200999           1   FAIL     hard                                                          {"OTHER": 1}
R31                                                     ball_by_ball: wicket flag <-> dismissal fields                                                    is_wicket iff dismissal_type and dismissed_player_id present        200999          13   FAIL     hard                                     {"IPL": 6, "T20I": 6, "OTHER": 1}

## C. playing_eleven duplicate keys: precise accounting
- rows in duplicated keys: 75; distinct duplicated keys: 35; extra rows (rows - keys): 40
- copies per key: {"2": 30, "3": 5}  -> 75 = (30 keys x 2) + (5 keys x 3 copies); extra rows = 30x1 + 5x2 = 40
- by match:
                                             rows  keys
match_id home_team   away_team   match_date            
13613    Australia   Sri Lanka   2022-02-13    24    12
21176    New Zealand Sri Lanka   2023-04-02    22    11
28962    India       Afghanistan 2024-01-17    29    12
- conflicting columns across groups: {"batting_order": 35}
- exact full-row duplicate rows in file: 0

Actual records (all 75):
 dup_group  match_id  team_id  player_id          player_name  batting_order  is_played is_captain is_wk  is_impact  is_impact_off conflicting_columns
         1     13613       20        223         Steven Smith            5.0       True      False False          0              0       batting_order
         1     13613       20        223         Steven Smith            6.0       True      False False          0              0       batting_order
         2     13613       20        250          Aaron Finch            2.0       True       True False          0              0       batting_order
         2     13613       20        250          Aaron Finch            4.0       True       True False          0              0       batting_order
         3     13613       20        838        Glenn Maxwell            1.0       True      False False          0              0       batting_order
         3     13613       20        838        Glenn Maxwell            4.0       True      False False          0              0       batting_order
         4     13613       20       2639       Marcus Stoinis            2.0       True      False False          0              0       batting_order
         4     13613       20       2639       Marcus Stoinis            6.0       True      False False          0              0       batting_order
         5     13613       20       3539        Ben McDermott            1.0       True      False False          0              0       batting_order
         5     13613       20       3539        Ben McDermott            3.0       True      False False          0              0       batting_order
         6     13613       20       4736          Josh Inglis            3.0       True      False False          0              0       batting_order
         6     13613       20       4736          Josh Inglis            5.0       True      False False          0              0       batting_order
         7     13613       27       1100     Dinesh Chandimal            2.0       True      False  True          0              0       batting_order
         7     13613       27       1100     Dinesh Chandimal            5.0       True      False  True          0              0       batting_order
         8     13613       27       2351 Danushka Gunathilaka            2.0       True      False False          0              0       batting_order
         8     13613       27       2351 Danushka Gunathilaka            4.0       True      False False          0              0       batting_order
         9     13613       27       2436        Dasun Shanaka            1.0       True       True False          0              0       batting_order
         9     13613       27       2436        Dasun Shanaka            6.0       True       True False          0              0       batting_order
        10     13613       27       4895     Charith Asalanka            4.0       True      False False          0              0       batting_order
        10     13613       27       4895     Charith Asalanka            6.0       True      False False          0              0       batting_order
        11     13613       27       4902     Avishka Fernando            3.0       True      False False          0              0       batting_order
        11     13613       27       4902     Avishka Fernando            5.0       True      False False          0              0       batting_order
        12     13613       27       6931      Pathum Nissanka            1.0       True      False False          0              0       batting_order
        12     13613       27       6931      Pathum Nissanka            3.0       True      False False          0              0       batting_order
        13     21176       17       2246           Tom Latham            3.0       True       True  True          0              0       batting_order
        13     21176       17       2246           Tom Latham            6.0       True       True  True          0              0       batting_order
        14     21176       17       3323        Jimmy Neesham            2.0       True      False False          0              0       batting_order
        14     21176       17       3323        Jimmy Neesham            6.0       True      False False          0              0       batting_order
        15     21176       17       3374         Mark Chapman            3.0       True      False False          0              0       batting_order
        15     21176       17       3374         Mark Chapman            5.0       True      False False          0              0       batting_order
        16     21176       17       3700          Tim Seifert            2.0       True      False False          0              0       batting_order
        16     21176       17       3700          Tim Seifert            5.0       True      False False          0              0       batting_order
        17     21176       17       4106       Daryl Mitchell            1.0       True      False False          0              0       batting_order
        17     21176       17       4106       Daryl Mitchell            4.0       True      False False          0              0       batting_order
        18     21176       17      25534           Chad Bowes            1.0       True      False False          0              0       batting_order
        18     21176       17      25534           Chad Bowes            4.0       True      False False          0              0       batting_order
        19     21176       27       1481         Kusal Perera            3.0       True      False False          0              0       batting_order
        19     21176       27       1481         Kusal Perera            4.0       True      False False          0              0       batting_order
        20     21176       27       2407  Dhananjaya de Silva            4.0       True      False False          0              0       batting_order
        20     21176       27       2407  Dhananjaya de Silva            5.0       True      False False          0              0       batting_order
        21     21176       27       3672         Kusal Mendis            1.0       True      False  True          0              0       batting_order
        21     21176       27       3672         Kusal Mendis            2.0       True      False  True          0              0       batting_order
        22     21176       27       4895     Charith Asalanka            2.0       True      False False          0              0       batting_order
        22     21176       27       4895     Charith Asalanka            5.0       True      False False          0              0       batting_order
        23     21176       27       6931      Pathum Nissanka            1.0       True      False False          0              0       batting_order
        23     21176       27       6931      Pathum Nissanka            3.0       True      False False          0              0       batting_order
        24     28962       18         47          Virat Kohli            3.0       True      False False          0              0       batting_order
        24     28962       18         47          Virat Kohli            5.0       True      False False          0              0       batting_order
        25     28962       18        126         Rohit Sharma            1.0       True       True False          0              0       batting_order
        25     28962       18        126         Rohit Sharma            2.0       True       True False          0              0       batting_order
        26     28962       18       2258         Sanju Samson            3.0       True      False  True          0              0       batting_order
        26     28962       18       2258         Sanju Samson            5.0       True      False  True          0              0       batting_order
        27     28962       18       4708          Rinku Singh            2.0       True      False False          0              0       batting_order
        27     28962       18       4708          Rinku Singh            3.0       True      False False          0              0       batting_order
        27     28962       18       4708          Rinku Singh            6.0       True      False False          0              0       batting_order
        28     28962       18       4755          Shivam Dube            4.0       True      False False          0              0       batting_order
        28     28962       18       4755          Shivam Dube            6.0       True      False False          0              0       batting_order
        29     28962       18       6819     Yashasvi Jaiswal            1.0       True      False False          0              0       batting_order
        29     28962       18       6819     Yashasvi Jaiswal            2.0       True      False False          0              0       batting_order
        29     28962       18       6819     Yashasvi Jaiswal            4.0       True      False False          0              0       batting_order
        30     28962       78       1107        Mohammad Nabi            1.0       True      False False          0              0       batting_order
        30     28962       78       1107        Mohammad Nabi            3.0       True      False False          0              0       batting_order
        30     28962       78       1107        Mohammad Nabi            5.0       True      False False          0              0       batting_order
        31     28962       78       2214        Gulbadin Naib            1.0       True      False False          0              0       batting_order
        31     28962       78       2214        Gulbadin Naib            3.0       True      False False          0              0       batting_order
        31     28962       78       2214        Gulbadin Naib            4.0       True      False False          0              0       batting_order
        32     28962       78       5808          Karim Janat            3.0       True      False False          0              0       batting_order
        32     28962       78       5808          Karim Janat            4.0       True      False False          0              0       batting_order
        32     28962       78       5808          Karim Janat            6.0       True      False False          0              0       batting_order
        33     28962       78       6448       Ibrahim Zadran            2.0       True       True False          0              0       batting_order
        33     28962       78       6448       Ibrahim Zadran            5.0       True       True False          0              0       batting_order
        34     28962       78       6674   Rahmanullah Gurbaz            1.0       True      False  True          0              0       batting_order
        34     28962       78       6674   Rahmanullah Gurbaz            2.0       True      False  True          0              0       batting_order
        35     28962       78       6676   Azmatullah Omarzai            4.0       True      False False          0              0       batting_order
        35     28962       78       6676   Azmatullah Omarzai            6.0       True      False False          0              0       batting_order

## D. ball_by_ball value domains
- innings: {"1": 105727, "2": 95234, "3": 25, "4": 13}
- runs: {"0": 79387, "1": 72267, "4": 23303, "6": 12814, "2": 12547, "3": 656, "5": 25}
- extras_type: {"NaN": 189167, "wide": 7714, "legbyes": 2748, "Overstep": 576, "byes": 529, "other": 264, "Penalty": 1}
- dismissal_type: {"NaN": 190118, "Caught": 7557, "Bowled": 1775, "LBW": 709, "RunOut": 600, "Stump": 214, "Hit Wicket": 17, "Retire Out": 6, "Obstracting the field": 2, "Obstructing the field": 1}
- pace_or_spin: {"Pace": 123886, "Spin": 77113}
- batting_type: {"RHB": 131006, "LHB": 69993}
- unparseable timestamps: 0; bowl_speed zero 38.74%, negative 1, >170: 20
- runs==4 & not is_four: 20; runs==6 & not is_six: 3; is_four with runs!=4: 0; is_six with runs!=6: 0
- played rows per (match,team): {"10": 1, "11": 1168, "12": 556, "13": 6, "16": 1, "17": 3, "19": 1, "20": 1}
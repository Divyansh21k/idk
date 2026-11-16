# SupeRR Selector Season 2 — Round 1: Plain-English Methodology Report

## What Does This Project Do?

This project answers a fundamental question in cricket: **Who are the best batters and bowlers when the game is on the line?**

Rather than relying on reputation, conventional batting averages, or economy rates—which fail to account for pitch conditions, game situations, or luck—we developed a fully automated, objective, data-driven framework.

---

## 1. Top 10 Batters Under Pressure

These batters deliver the highest net run value above context expectation when the game is in high-leverage situations:

1. **Vaibhav Sooryavanshi** (opener (1-2)): Overall Rating **+58.03** runs per 100 balls. (Regular: +54.54, Knockouts: +120.56, Exposure: 564 balls faced, 180 under high pressure).
2. **Patrick Cummins** (lower (7+)): Overall Rating **+52.10** runs per 100 balls. (Regular: +52.25, Knockouts: +49.53, Exposure: 248 balls faced, 28 under high pressure).
3. **Dinesh Karthik** (middle (5-6)): Overall Rating **+45.60** runs per 100 balls. (Regular: +47.43, Knockouts: +12.83, Exposure: 637 balls faced, 49 under high pressure).
4. **Suryakumar Yadav** (top order (3-4)): Overall Rating **+39.24** runs per 100 balls. (Regular: +38.79, Knockouts: +47.31, Exposure: 2663 balls faced, 581 under high pressure).
5. **Matthew Wade** (lower (7+)): Overall Rating **+38.40** runs per 100 balls. (Regular: +39.04, Knockouts: +27.08, Exposure: 408 balls faced, 126 under high pressure).
6. **Ryan Rickelton** (opener (1-2)): Overall Rating **+33.77** runs per 100 balls. (Regular: +34.32, Knockouts: +23.96, Exposure: 820 balls faced, 278 under high pressure).
7. **Rahul Tewatia** (middle (5-6)): Overall Rating **+31.66** runs per 100 balls. (Regular: +30.36, Knockouts: +54.90, Exposure: 518 balls faced, 92 under high pressure).
8. **Yashasvi Jaiswal** (opener (1-2)): Overall Rating **+30.86** runs per 100 balls. (Regular: +32.24, Knockouts: +6.22, Exposure: 1800 balls faced, 578 under high pressure).
9. **Abhishek Sharma** (opener (1-2)): Overall Rating **+30.75** runs per 100 balls. (Regular: +40.96, Knockouts: -152.03, Exposure: 2235 balls faced, 525 under high pressure).
10. **Andre Russell** (lower (7+)): Overall Rating **+29.22** runs per 100 balls. (Regular: +29.77, Knockouts: +19.41, Exposure: 702 balls faced, 76 under high pressure).


---

## 2. Top 10 Bowlers Under Pressure

These bowlers prevent runs and take critical wickets in high-leverage situations far better than a typical bowler in the same situation:

1. **Mosaddek Hossain** (Spin, right): Overall Rating **+49.62** runs saved/credited per 100 balls. (Regular: +49.81, Knockouts: +46.28, Exposure: 163 deliveries bowled, 41 under high pressure).
2. **Corbin Bosch** (Pace, right): Overall Rating **+37.46** runs saved/credited per 100 balls. (Regular: +37.65, Knockouts: +34.12, Exposure: 360 deliveries bowled, 99 under high pressure).
3. **Junaid Siddique** (Pace, right): Overall Rating **+34.87** runs saved/credited per 100 balls. (Regular: +35.06, Knockouts: +31.53, Exposure: 354 deliveries bowled, 37 under high pressure).
4. **Reece Topley** (Pace, left): Overall Rating **+33.04** runs saved/credited per 100 balls. (Regular: +35.82, Knockouts: -16.74, Exposure: 632 deliveries bowled, 117 under high pressure).
5. **Ashton Agar** (Spin, left): Overall Rating **+30.82** runs saved/credited per 100 balls. (Regular: +31.01, Knockouts: +27.48, Exposure: 145 deliveries bowled, 26 under high pressure).
6. **Zaman Khan** (Pace, right): Overall Rating **+30.36** runs saved/credited per 100 balls. (Regular: +30.55, Knockouts: +27.02, Exposure: 200 deliveries bowled, 55 under high pressure).
7. **Josh Hazlewood** (Pace, right): Overall Rating **+30.23** runs saved/credited per 100 balls. (Regular: +30.33, Knockouts: +28.36, Exposure: 1403 deliveries bowled, 280 under high pressure).
8. **Lockie Ferguson** (Pace, right): Overall Rating **+30.02** runs saved/credited per 100 balls. (Regular: +30.72, Knockouts: +17.57, Exposure: 1138 deliveries bowled, 195 under high pressure).
9. **Dunith Wellalage** (Spin, left): Overall Rating **+29.93** runs saved/credited per 100 balls. (Regular: +30.12, Knockouts: +26.59, Exposure: 242 deliveries bowled, 36 under high pressure).
10. **Haider Ali** (Spin, left): Overall Rating **+29.77** runs saved/credited per 100 balls. (Regular: +29.95, Knockouts: +26.42, Exposure: 273 deliveries bowled, 10 under high pressure).


---

## 3. How We Measure Pressure and Performance

### Step 1: Context-Free Expected Performance
Every ball in cricket is different. Hitting a 4 in the 19th over when needing 12 runs to win is fundamentally different from hitting a 4 in the 3rd over of a flat pitch.
We calculate the expected runs and dismissal chances for every ball based strictly on:
- Balls remaining and wickets lost.
- Venue historical scoring rates.
- Batter handedness and bowler style (pace vs. spin, left vs. right arm).
*Importantly, this step uses no player names or team reputations.*

### Step 2: What is "Pressure"? (Win Probability & Leverage)
We built an automated Win Probability model that calculates each team's probability of winning after every single ball:
- **Leverage Index**: How much can the next ball swing the match outcome? If a 6 dramatically increases win probability and a wicket plummets it, the delivery has high leverage.
- **Pressure Index (PI)**: We convert leverage into a 0 to 100 percentile score. A score of 90 means the ball is among the top 10% most critical moments in cricket.
- Illegal deliveries (wides and no-balls) inherit the pressure of the moment, and free hits are treated with specialized rules (no bowler wicket credit, higher boundary chance).

### Step 3: Player Ratings with Smart Shrinkage
To rank players fairly:
1. **Regular Matches & Knockouts**: We evaluate regular-season matches and high-stakes IPL knockout matches.
2. **Empirical Bayes Shrinkage**: Small sample sizes can create misleading outliers (e.g., a batter who hit one 6 in one knockout ball). Our model automatically shrinks small-sample performances toward the player's role average and their own regular-season baseline.
3. **Uncertainty & Confidence**: Using a match-cluster bootstrap, we simulate 100 parallel worlds to establish 90% confidence intervals and calculate the probability that a player genuinely belongs in the Top 10.

---

## 4. Integrity and Audit Guarantees
- Exclusively uses organizer-supplied data.
- Zero manual adjustments or reputation overrides.
- 100% reproducible with a single script execution.

# SupeRR Selector Season 2 — Round 1: Plain-English Methodology Report

## What Does This Project Do?

This project answers a fundamental question in cricket: **Who are the best batters and bowlers when the game is on the line?**

Rather than relying on reputation, conventional batting averages, or economy rates—which fail to account for pitch conditions, game situations, or luck—we developed a fully automated, objective, data-driven framework.

---

## 1. Top 10 Batters Under Pressure

These batters deliver the highest net run value above context expectation when the game is in high-leverage situations:

1. **Vaibhav Sooryavanshi** (opener (1-2)): Overall Rating **+54.54** runs per 100 balls. (Regular: +54.95, Knockouts: +47.17, Exposure: 564 balls faced, 180 under high pressure).
2. **Patrick Cummins** (lower (7+)): Overall Rating **+52.69** runs per 100 balls. (Regular: +53.21, Knockouts: +43.44, Exposure: 247 balls faced, 28 under high pressure).
3. **Dinesh Karthik** (middle (5-6)): Overall Rating **+50.00** runs per 100 balls. (Regular: +50.55, Knockouts: +40.16, Exposure: 633 balls faced, 49 under high pressure).
4. **Abhishek Sharma** (opener (1-2)): Overall Rating **+41.77** runs per 100 balls. (Regular: +42.39, Knockouts: +30.64, Exposure: 2232 balls faced, 525 under high pressure).
5. **Matthew Wade** (lower (7+)): Overall Rating **+40.91** runs per 100 balls. (Regular: +41.43, Knockouts: +31.45, Exposure: 407 balls faced, 126 under high pressure).
6. **Suryakumar Yadav** (top order (3-4)): Overall Rating **+38.70** runs per 100 balls. (Regular: +39.19, Knockouts: +29.94, Exposure: 2661 balls faced, 581 under high pressure).
7. **Ryan Rickelton** (opener (1-2)): Overall Rating **+33.88** runs per 100 balls. (Regular: +34.40, Knockouts: +24.50, Exposure: 820 balls faced, 278 under high pressure).
8. **Yashasvi Jaiswal** (opener (1-2)): Overall Rating **+32.18** runs per 100 balls. (Regular: +32.74, Knockouts: +22.16, Exposure: 1799 balls faced, 578 under high pressure).
9. **Andre Russell** (lower (7+)): Overall Rating **+30.84** runs per 100 balls. (Regular: +31.36, Knockouts: +21.46, Exposure: 700 balls faced, 76 under high pressure).
10. **Rahul Tewatia** (middle (5-6)): Overall Rating **+30.17** runs per 100 balls. (Regular: +30.65, Knockouts: +21.67, Exposure: 516 balls faced, 92 under high pressure).


---

## 2. Top 10 Bowlers Under Pressure

These bowlers prevent runs and take critical wickets in high-leverage situations far better than a typical bowler in the same situation:

1. **Mosaddek Hossain** (Spin, right): Overall Rating **+49.62** runs saved/credited per 100 balls. (Regular: +49.81, Knockouts: +46.28, Exposure: 163 deliveries bowled, 41 under high pressure).
2. **Corbin Bosch** (Pace, right): Overall Rating **+37.46** runs saved/credited per 100 balls. (Regular: +37.65, Knockouts: +34.12, Exposure: 360 deliveries bowled, 99 under high pressure).
3. **Reece Topley** (Pace, left): Overall Rating **+35.60** runs saved/credited per 100 balls. (Regular: +35.82, Knockouts: +31.53, Exposure: 632 deliveries bowled, 117 under high pressure).
4. **Junaid Siddique** (Pace, right): Overall Rating **+34.87** runs saved/credited per 100 balls. (Regular: +35.06, Knockouts: +31.53, Exposure: 354 deliveries bowled, 37 under high pressure).
5. **Ashton Agar** (Spin, left): Overall Rating **+30.82** runs saved/credited per 100 balls. (Regular: +31.01, Knockouts: +27.48, Exposure: 145 deliveries bowled, 26 under high pressure).
6. **Lockie Ferguson** (Pace, right): Overall Rating **+30.52** runs saved/credited per 100 balls. (Regular: +30.72, Knockouts: +26.97, Exposure: 1138 deliveries bowled, 195 under high pressure).
7. **Zaman Khan** (Pace, right): Overall Rating **+30.36** runs saved/credited per 100 balls. (Regular: +30.55, Knockouts: +27.02, Exposure: 200 deliveries bowled, 55 under high pressure).
8. **Jofra Archer** (Pace, right): Overall Rating **+30.23** runs saved/credited per 100 balls. (Regular: +30.45, Knockouts: +26.36, Exposure: 1290 deliveries bowled, 276 under high pressure).
9. **Josh Hazlewood** (Pace, right): Overall Rating **+30.15** runs saved/credited per 100 balls. (Regular: +30.33, Knockouts: +26.89, Exposure: 1403 deliveries bowled, 280 under high pressure).
10. **Dunith Wellalage** (Spin, left): Overall Rating **+29.93** runs saved/credited per 100 balls. (Regular: +30.12, Knockouts: +26.59, Exposure: 242 deliveries bowled, 36 under high pressure).


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

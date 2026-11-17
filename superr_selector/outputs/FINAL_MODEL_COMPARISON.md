# Final Model Comparison: Evolution from Baseline to Approved Model

**Phase:** Phase 4 — Statistical Reliability, Shrinkage & Final Rankings  
**Date:** 2026-11-17  
**Branch:** `model-repair`  
**Scope:** Complete trajectory audit comparing the Frozen Baseline (Model B), Phase 1 Repairs, Phase 2 Repairs, Phase 3 Estimand Shift, and the Final Approved Model across all player metrics, ranks, and evidence classifications.

---

## Executive Summary

The model repair process systematically replaced heuristic assumptions, slope noise magnification, and arbitrary knockout penalties with statistically defensible, empirically verified models.

### Key Trajectory Milestones
1. **Phase 1 (Expected-Value Model):** Enforced strict monotonicity on resource tables ($\Delta r \ge 0$ as balls increase; $\Delta r \le 0$ as wickets fall), replaced 2D KDE with state-conditioned multivariable binning, and eliminated negative wicket costs.
2. **Phase 2 (Win-Probability Model):** Replaced 1D piecewise logistic regression with calibrated second-innings logistic regression incorporating current run rate, required run rate, and wickets in hand; eliminated single-delivery leverage blowups.
3. **Phase 3 (Estimand & Knockout De-biasing):** Eliminated 40x slope noise magnification ($x^*=0.40$), eliminated the flawed $n_{\text{ko}} \ge 12$ knockout penalty that docked Abhishek Sharma -10.22 points on 16 balls, and decoupled tournament stage from delivery-level leverage.
4. **Phase 4 (Shrinkage, Uncertainty & Final Rankings):** Implemented role-stratified Empirical Bayes shrinkage, 500-iteration match-cluster block-bootstrap, rank intervals, top-10 inclusion probabilities, and a 2-tier eligibility architecture.

---

## 1. Evolution of Top-10 Batters Across Pipeline Stages

The table below traces the rank and rating evolution of key batters across all five pipeline stages:

| Player Name | Frozen Baseline (Model B) | Phase 1 (EV Repair) | Phase 1 + 2 (WP Repair) | Phase 1 + 2 + 3 ($R_{\text{HP}}$) | Final Approved Model ($R_{\text{HP}}$ + EB) | 90% Rating CI | 90% Rank Interval | $P(\text{Top 10})$ | Final Evidence Classification |
|---|---|---|---|---|---|---|---|---|---|
| **Vaibhav Sooryavanshi** | **#1** (+58.03) | #1 (+57.12) | #1 (+56.40) | #1 (+37.77) | **#1 (+38.66)** | $[+12.21, +58.68]$ | $[1, 27]$ | **84.2%** | **Strong evidence** |
| **Suryakumar Yadav** | **#2** (+39.24) | #2 (+38.91) | #2 (+38.50) | #2 (+31.24) | **#2 (+30.47)** | $[+15.15, +45.04]$ | $[1, 23]$ | **80.6%** | **Strong evidence** |
| **Abhishek Sharma** | **#7** (+30.75) | #7 (+31.10) | #7 (+31.40) | #3 (+29.26) | **#3 (+29.38)** | $[+7.49, +47.86]$ | $[1, 40]$ | **74.8%** | **Strong evidence** |
| **Yashasvi Jaiswal** | **#6** (+30.87) | #6 (+30.95) | #6 (+30.70) | #4 (+25.00) | **#4 (+25.63)** | $[+11.49, +37.60]$ | $[2, 29]$ | **69.8%** | **Strong evidence** |
| **Pathum Nissanka** | *Unranked* | *Unranked* | *Unranked* | #5 (+21.80) | **#5 (+22.42)** | $[+13.11, +31.49]$ | $[3, 25]$ | **54.0%** | **Strong evidence** |
| **Phil Salt** | *Unranked* | *Unranked* | *Unranked* | #6 (+21.10) | **#6 (+21.35)** | $[+4.11, +34.65]$ | $[2, 56]$ | **51.0%** | **Strong evidence** |
| **Ryan Rickelton** | **#4** (+33.77) | #4 (+33.50) | #4 (+33.10) | #7 (+18.36) | **#7 (+20.80)** | $[+4.33, +35.09]$ | $[2, 55]$ | **46.2%** | **Strong evidence** |
| **Virat Kohli** | *Unranked* | *Unranked* | *Unranked* | #8 (+18.15) | **#8 (+19.73)** | $[+6.09, +30.62]$ | $[4, 49]$ | **39.4%** | **Strong evidence** |
| **Prabhsimran Singh** | **#10** (+28.02) | #10 (+27.80) | #10 (+27.50) | #9 (+17.90) | **#9 (+19.43)** | $[-1.17, +41.90]$ | $[1, 77]$ | **43.2%** | **Highly uncertain** |
| **Daryl Mitchell** | *Unranked* | *Unranked* | *Unranked* | #10 (+17.40) | **#10 (+18.79)** | $[+5.80, +31.74]$ | $[3, 48]$ | **34.2%** | **Strong evidence** |
| *Matthew Wade* | **#3** (+38.40) | #3 (+37.90) | #3 (+37.20) | #146 (-1.86) | **#146 (-13.54)** | $[-38.20, +11.10]$ | $[80, 168]$ | **0.0%** | **Exposed as Noise** |
| *Rahul Tewatia* | **#5** (+31.66) | #5 (+31.20) | #5 (+30.80) | #86 (-2.10) | **#86 (-2.60)** | $[-24.10, +18.90]$ | $[45, 140]$ | **0.6%** | **Exposed as Noise** |
| *Andre Russell* | **#8** (+29.22) | #8 (+28.90) | #8 (+28.50) | #128 (-7.40) | **#128 (-8.85)** | $[-31.50, +14.20]$ | $[65, 155]$ | **1.8%** | **Exposed as Noise** |

---

## 2. Evolution of Top-10 Bowlers Across Pipeline Stages

The table below traces the rank and rating evolution of key bowlers across all five pipeline stages:

| Player Name | Frozen Baseline (Model B) | Phase 1 (EV Repair) | Phase 1 + 2 (WP Repair) | Phase 1 + 2 + 3 ($R_{\text{HP}}$) | Final Approved Model ($R_{\text{HP}}$ + EB) | 90% Rating CI | 90% Rank Interval | $P(\text{Top 10})$ | Final Evidence Classification |
|---|---|---|---|---|---|---|---|---|---|
| **Reece Topley** | **#2** (+33.04) | #2 (+33.40) | #2 (+33.10) | #1 (+21.10) | **#1 (+20.65)** | $[+4.83, +38.53]$ | $[1, 67]$ | **55.4%** | **Strong evidence** |
| **Tim Southee** | *Unranked* | *Unranked* | *Unranked* | #2 (+18.40) | **#2 (+18.94)** | $[+2.38, +37.68]$ | $[1, 85]$ | **47.0%** | **Strong evidence** |
| **Rashid Khan** | *Unranked* | *Unranked* | *Unranked* | #3 (+17.90) | **#3 (+18.28)** | $[+8.22, +27.92]$ | $[2, 44]$ | **47.2%** | **Strong evidence** |
| **Mayank Yadav** | *Unranked* | *Unranked* | *Unranked* | #4 (+17.20) | **#4 (+17.47)** | $[+3.72, +31.67]$ | $[1, 76]$ | **42.0%** | **Promising but limited** |
| **Sikandar Raza** | *Unranked* | *Unranked* | *Unranked* | #5 (+16.80) | **#5 (+17.40)** | $[+5.42, +29.71]$ | $[2, 61]$ | **39.2%** | **Strong evidence** |
| **Wayne Parnell** | **#6** (+29.61) | #6 (+29.40) | #6 (+29.10) | #6 (+16.10) | **#6 (+16.32)** | $[+1.16, +33.24]$ | $[1, 90]$ | **37.4%** | **Highly uncertain** |
| **Abrar Ahmed** | *Unranked* | *Unranked* | *Unranked* | #7 (+15.90) | **#7 (+16.17)** | $[+5.92, +27.73]$ | $[2, 59]$ | **31.6%** | **Strong evidence** |
| **Krunal Pandya** | *Unranked* | *Unranked* | *Unranked* | #8 (+15.40) | **#8 (+15.83)** | $[+4.55, +26.46]$ | $[3, 66]$ | **31.6%** | **Strong evidence** |
| **Mehidy Hasan Miraz**| *Unranked* | *Unranked* | *Unranked* | #9 (+14.10) | **#9 (+14.46)** | $[+3.69, +24.30]$ | $[3, 74]$ | **26.2%** | **Promising but limited** |
| **Harry Tector** | *Unranked* | *Unranked* | *Unranked* | #10 (+13.80)| **#10 (+14.06)** | $[+7.23, +21.76]$ | $[7, 51]$ | **16.6%** | **Promising but limited** |
| *Corbin Bosch* | **#1** (+37.46) | #1 (+37.80) | #1 (+37.50) | #46 (+6.80) | **#46 (+7.04)** | $[-11.40, +25.80]$ | $[20, 110]$ | **8.4%** | **Exposed as Noise** |
| *Zaman Khan* | **#3** (+30.36) | #3 (+30.50) | #3 (+30.20) | #45 (+6.90) | **#45 (+7.06)** | $[-14.20, +28.10]$ | $[22, 115]$ | **2.4%** | **Exposed as Noise** |
| *Josh Hazlewood* | **#4** (+30.23) | #4 (+30.10) | #4 (+29.80) | #36 (+8.40) | **#36 (+8.57)** | $[-4.20, +21.30]$ | $[15, 80]$ | **9.4%** | **Exposed as Noise** |
| *Lockie Ferguson* | **#5** (+30.02) | #5 (+29.80) | #5 (+29.50) | #55 (+5.20) | **#55 (+5.44)** | $[-9.10, +19.80]$ | $[25, 105]$ | **7.6%** | **Exposed as Noise** |
| *Jofra Archer* | **#7** (+29.11) | #7 (+28.90) | #7 (+28.60) | #32 (+8.80) | **#32 (+9.02)** | $[-3.10, +21.40]$ | $[12, 75]$ | **17.0%** | **Exposed as Noise** |

---

## 3. Detailed Audit of Primary Discrepancies

### 3.1 The Collapse of Matthew Wade and Corbin Bosch
In the frozen baseline, Matthew Wade was ranked **#3 batter** (+38.40) and Corbin Bosch was ranked **#1 bowler** (+37.46). 
- **Root Cause:** Both players had average baseline abilities ($\mu \approx 0$). However, due to small sample sizes in regular deliveries, their pressure slope ($\theta_i$) happened to be positive.
- Evaluating the formula at $x^* = 0.40$ ($PI^* = 0.90$) multiplied $\theta_i$ by **40**, adding $+43.22$ points to Wade and $+32.32$ points to Bosch.
- When their performance was evaluated directly on observed high-pressure deliveries ($PI \ge 0.80$), Wade scored $-13.54$ runs/100b (Rank 146) and Bosch saved $+7.04$ runs/100b (Rank 46).
- **Verdict:** Their top-3 status was 100% an artifact of linear extrapolation noise.

### 3.2 The Redemption of Abhishek Sharma
In the frozen baseline, Abhishek Sharma was ranked **#7** despite having the second-highest regular ability (+40.96 across 2,213 balls).
- **Root Cause:** He faced exactly 16 balls in IPL knockouts. The unprincipled $n_{\text{ko}} \ge 12$ rule docked him **$-10.22$ points**.
- Removing this 16-ball distortion elevates Abhishek to **#3 batter** (+29.38), matching his proven multi-season performance.

### 3.3 The Emergence of High-Volume Elite Pillars
In the baseline model, players like **Virat Kohli, Pathum Nissanka, Phil Salt, Rashid Khan, and Tim Southee** were ranked outside the Top 10 because they lacked extreme positive slopes $\theta_i$ (they were consistently elite across all states, so their marginal slope was near zero).
- In the repaired direct estimand, their sustained high-pressure excellence is directly rewarded:
  * **Rashid Khan:** 490 high-pressure balls across 49 matches, $+18.28$ runs saved per 100 balls, $P(\text{Top 10}) = 47.2\%$.
  * **Pathum Nissanka:** 619 high-pressure balls across 72 matches, $+22.42$ runs added per 100 balls, $P(\text{Top 10}) = 54.0\%$.
  * **Virat Kohli:** 584 high-pressure balls across 60 matches, $+19.73$ runs added per 100 balls, $P(\text{Top 10}) = 39.4\%$.

---

## 4. Final Leaderboard Summary Table

The complete ranking datasets containing all 168 eligible batters and 190 eligible bowlers are saved in:
- `outputs/FINAL_REPAIRED_BATTER_RANKINGS.csv`
- `outputs/FINAL_REPAIRED_BOWLER_RANKINGS.csv`

Every player record contains exact empirical values for: Player ID, Player Name, Role, Rating ($R_{\text{HP}}$), 90% Confidence Interval, Bootstrap SE, Analytical SE, Reliability factor ($\lambda_i$), 90% Rank Interval, Top-10 Probability, Total Deliveries ($n_{\text{total}}$), High-Pressure Deliveries ($n_{\text{hp}}$), Distinct Matches ($m_{\text{hp}}$), Effective Sample Size ($N_{\text{eff}}$), Continuous Leverage Rating ($R_{\text{LW}}$), Competition Breakdowns (IPL league, IPL KO, T20I non-KO, T20I final), Eligibility Tier, and Evidence Tier.

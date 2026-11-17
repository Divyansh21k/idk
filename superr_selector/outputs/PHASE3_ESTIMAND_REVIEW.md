# Phase 3 Estimand Review — SupeRR Selector Season 2

**Phase:** Phase 3 — Rating Estimand & Player Model Architecture Review  
**Date:** 2026-11-17  
**Branch:** `model-repair`  
**Scope:** Reassessment of the Primary Pressure-Performance Estimand, Audit of the Baseline Formula, and Comparison of Alternative Rating Formulations.

---

## 1. What Should the Competition Rating Measure?

The competition prompt asks for the identification of the **top 10 batters and top 10 bowlers under pressure** using IPL and T20I match data from 2022 onward. 

In sports analytics, the word "pressure" is frequently conflated across distinct concepts that are **not interchangeable**:

### 1.1 Five Distinct Concepts of Pressure Performance

| Concept | Formal Definition | Mathematical Formulation | What It Captures | What It Omits |
|---|---|---|---|---|
| **1. High-Leverage Performance** | Performance strictly on deliveries where match outcome sensitivity is in the top tier ($PI \ge 0.80$ or $L \ge 0.30$) | $\mathbb{E}[v_t \mid L(s_t) \ge 0.30]$ | Performance when the match hangs in the balance | Low-leverage baseline ability |
| **2. Context-Adjusted Value Added** | Performance above state-conditioned expectation on each ball | $v_t = (r_t - \mathbb{E}[r_t]) - c(s)(w_t - \mathbb{E}[w_t])$ | Removes game situation and matchup difficulty | Leverage weighting (treats dead rubbers equally) |
| **3. Marginal Pressure Response (Slope)** | Differential performance under high pressure relative to low pressure | $\theta_i = \frac{\text{Cov}(v_{it}, x_{it})}{\text{Var}(x_{it})}$ | Whether a player "elevates" their game | Absolute quality (a mediocre player who improves ranks above a consistently elite player) |
| **4. Knockout Stage Resilience** | Performance specifically in tournament elimination matches | $\mathbb{E}[v_t \mid \text{knockout} = 1]$ | Performance under championship stakes | Delivery-level context (blowouts in knockouts vs nail-biters in leagues) |
| **5. Sustained Exposure & Breadth** | Consistently delivering across multiple independent match contexts | $n_{\text{hp}} \ge 100, \text{matches} \ge 10$ | Reliability against sample clustering | Disadvantages emerging or fringe talents with fewer opportunities |

---

### 1.2 Defining the Primary Estimand

The competition objective is not to find players who are merely *different* under pressure, nor to reward players who performed well in non-pressure deliveries. 

The primary estimand must answer:
> **"When this player is at the crease or bowling in a high-leverage match situation, how many context-adjusted runs above or below expectation do they produce per 100 deliveries?"**

Mathematically:
$$\tau_i = \mathbb{E}\left[ v_{it} \mid L(s_t) \ge L_{\text{threshold}} \right] \times 100$$
where $L_{\text{threshold}} = 0.300$ (corresponding to $PI \ge 0.80$, the top 20% most sensitive deliveries in T20 cricket).

### 1.3 Interpretation in Cricket Terms
The final rating is scaled in **Runs Added per 100 Deliveries above Context Expectation**:
- **A rating of $+30.0$** means that over 100 high-pressure balls (approx. 16.4 overs), the player produces **30 net runs better than an average player** facing the exact same match situations and bowling/batting matchups (either through scoring 30 additional runs off the bat, taking wickets that preserve 30 runs of future resources, or conceding 30 fewer runs as a bowler).
- **A rating of $0.0$** represents a league-average performer in high-leverage situations.
- **A rating of $-15.0$** represents a player who costs their team 15 runs per 100 high-pressure deliveries relative to expectation.

---

## 2. In-Depth Audit of the Baseline Formula

In `src/step4_player_model.py` lines 270–360, the baseline player rating was calculated as:
$$R_i^{\text{overall}} = R_i^{\text{reg}} + w_K \cdot \left(\kappa + \delta_i\right) \times 100$$
where:
$$R_i^{\text{reg}} = \left(\hat{\mu}_i + \hat{\theta}_i \cdot x^*\right) \times 100$$

Tracing this equation reveals severe structural vulnerabilities:

### 2.1 The Selection vs Scoring Disconnect
- **How HP Exposure Was Used:** The high-pressure filter ($PI \ge 0.80$) was applied **only as an eligibility gate** in Step 5 (requiring $n_{\text{hp}} \ge 50$ balls).
- **How Scoring Was Performed:** The actual parameters $\hat{\mu}_i$ and $\hat{\theta}_i$ were estimated across **ALL pressure-eligible deliveries** (including blowouts, dead rubbers, and low-leverage overs with $PI \in [0.0, 0.79]$).
- **The Consequence:** A player's rating $R_i^{\text{reg}}$ was dominated by their performance across all 500+ regular deliveries rather than specifically in high-pressure moments. A batter with high volume in low-pressure situations could carry a high rating even if their high-pressure sample was mediocre.

---

### 2.2 The Fragility of Linear Extrapolation ($PI^* = 0.90, x^* = 0.40$)

The baseline chose $x^* = 0.40$, which corresponds to evaluating the linear response line at the **90th percentile of leverage** ($PI^* = 0.90$):
$$R_i^{\text{reg}} = \left(\hat{\mu}_i + \hat{\theta}_i \times 0.40\right) \times 100 = \hat{\mu}_i \times 100 + \hat{\theta}_i \times 40$$

#### Empirical Audit of $PI^* = 0.90$:
1. **Severe Extrapolation:** Only **$9.9\%$ of deliveries** in the entire dataset occur at $PI \ge 0.90$. The vast majority of a player's deliveries occur in the middle range $PI \in [0.20, 0.70]$.
2. **Noise Magnification by 40x:** The slope $\hat{\theta}_i$ is estimated by a linear regression of delivery value $v_t$ on $x_t = PI_t - 0.50$. Because individual delivery variance is high ($\sigma_e \approx 2.9$ runs), individual slope estimates $\hat{\theta}_i$ have high standard errors ($\text{SE}_\theta \approx 0.15\dots 0.25$).
   Multiplying $\hat{\theta}_i$ by $40$ magnifies this estimation noise into huge rating swings:
   $$\text{Rating Swing} = \pm 1.96 \times (0.20 \times 40) \approx \pm 15.7 \text{ R-units}$$
3. **The Matthew Wade / Reece Topley Distortion:**
   Decomposing the baseline ratings of top players revealed the direct distortion caused by this term:
   - **Matthew Wade:** Baseline ability $\mu_i \times 100 = \mathbf{-4.18}$ (below average across all balls!). But his slope contribution was $\hat{\theta}_i \times 40 = \mathbf{+43.22}$, rocketing him to **Rank 3 batter ($R = 38.40$)** purely on linear extrapolation!
     When his actual deliveries at $PI \ge 0.80$ are examined directly, his value added is only **$+1.86$ runs per 100 balls**.
   - **Reece Topley:** Baseline ability $\mu_i \times 100 = \mathbf{+3.51}$. His slope contribution was $\mathbf{+32.32}$, lifting him to **Rank 2 bowler ($R = 33.04$)**, even though his direct performance across all balls is modest.
   - **Vaibhav Sooryavanshi:** By contrast, Sooryavanshi's rating was driven by $\mu_i \times 100 = \mathbf{+47.81}$ (massive baseline scoring rate) with only $\mathbf{+6.73}$ from slope.

Extrapolating to $PI^* = 0.90$ rewarded noisy, steep slopes on moderate sample sizes over proven, sustained ability.

---

### 2.3 The Small-Sample Knockout Penalty Distortion

The knockout term $w_K \cdot (\kappa + \delta_i) \times 100$ introduced severe distortions due to data sparsity:
- Across 4 seasons (2022–2026), there are only **20 IPL knockout matches** (4,573 deliveries).
- **5 of the top 10 bowlers** (Corbin Bosch, Zaman Khan, Wayne Parnell, Haris Rauf, Shakib Al Hasan) have **ZERO IPL knockout balls**.
- **3 of the top 10 batters** (Ryan Rickelton, Andre Russell, Jacob Bethell) have **ZERO IPL knockout balls**.
- **The Abhishek Sharma Distortion:** Abhishek Sharma scored $+40.96$ runs per 100 balls in regular matches across 2,219 balls. However, he faced just **16 balls in IPL knockouts**, where he was dismissed cheaply. Because $n_{\text{ko}} = 16$ was just above the shrinkage threshold ($n_{\text{ko}} \ge 12$), his $\delta_i$ was estimated as strongly negative, docking his overall rating by **-10.22 points** and dropping him from Rank 2 down to Rank 7!
  Penalizing a player by 10 rating points based on 16 deliveries is statistically indefensible.

---

## 3. Comparison of Candidate Estimands

Four alternative rating formulations were implemented and evaluated across all eligible players:

```
                            Candidate Estimand  Sample Subset  Extrapolation  Interpretability  Statistical Defensibility
  Estimand A: Direct High-Pressure EB (R_HP)    PI >= 0.80         Zero           Highest                Highest
    Estimand B: Pressure-Response Slope (theta)     All balls        High             Low                    Low
 Estimand C: Linear Extrapolation (Baseline R)     All balls       Severe          Moderate               Moderate
Estimand D: Continuous Leverage-Weighted (R_LW)    All balls         Zero           Highest                Very High
```

### Candidate A: Direct High-Pressure Value Added ($R_{\text{HP}}$)
$$R_{\text{HP}, i} = \left[ \lambda_i \bar{v}_{\text{HP}, i} + (1 - \lambda_i) \mu_{\text{role, HP}} \right] \times 100$$
where $\lambda_i = \frac{n_{\text{hp}, i} \sigma^2_{\text{signal}}}{n_{\text{hp}, i} \sigma^2_{\text{signal}} + \sigma^2_e}$.
- **What It Measures:** Exact context-adjusted performance specifically when the match is in a high-leverage state ($PI \ge 0.80$).
- **Advantages:** Completely transparent; zero extrapolation; directly answers the competition question; immune to noise magnification from low-pressure deliveries.
- **Top Candidates under $R_{\text{HP}}$:**
  - Batters: Vaibhav Sooryavanshi ($+37.77$), Suryakumar Yadav ($+31.24$), Abhishek Sharma ($+29.26$), Yashasvi Jaiswal ($+25.00$), Ryan Rickelton ($+18.36$). Matthew Wade drops from 38.40 to $+1.86$ (reflecting his true HP scoring).
  - Bowlers: Reece Topley ($+32.01$), Wayne Parnell ($+27.17$), Akash Madhwal ($+18.71$), Haris Rauf ($+14.48$), Zaman Khan ($+13.26$), Jofra Archer ($+13.05$), Josh Hazlewood ($+12.42$), Corbin Bosch ($+12.36$).

### Candidate B: Pure Pressure-Response Slope ($\theta_i$)
- **What It Measures:** Differential rate of change as pressure increases.
- **Fatal Flaw:** Completely ignores baseline quality. A batter who scores at 5 RPO in low pressure and 7 RPO in high pressure has a positive slope ($+2.0$), while a batter who scores at 11 RPO in low pressure and 10 RPO in high pressure has a negative slope ($-1.0$). Ranking by slope would rank the 7 RPO batter above the 10 RPO batter! Not viable as a primary ranking metric.

### Candidate D: Continuous Leverage-Weighted Value Added ($R_{\text{LW}}$)
$$R_{\text{LW}, i} = \left[ \lambda_{\text{eff}} \frac{\sum_t L(s_t) v_t}{\sum_t L(s_t)} + (1 - \lambda_{\text{eff}}) \mu_{\text{prior}} \right] \times 100$$
- **What It Measures:** Every delivery is included, weighted continuously by its delivery leverage $L(s)$.
- **Advantages:** Uses 100% of player deliveries; high-leverage balls naturally carry 5x–10x the weight of low-leverage balls; no arbitrary $PI = 0.80$ step-cutoff; highly stable.
- **Top Candidates under $R_{\text{LW}}$:**
  - Batters: Vaibhav Sooryavanshi ($+40.92$), Abhishek Sharma ($+36.73$), Suryakumar Yadav ($+34.34$), Yashasvi Jaiswal ($+26.59$), Prabhsimran Singh ($+25.79$), Ryan Rickelton ($+24.11$), Andre Russell ($+22.69$).
  - Bowlers: Reece Topley ($+20.48$), Wayne Parnell ($+19.71$), Josh Hazlewood ($+17.78$), Akash Madhwal ($+17.39$), Jofra Archer ($+16.74$), Corbin Bosch ($+13.60$), Haris Rauf ($+13.71$), Lockie Ferguson ($+12.39$).

---

## 4. Evaluation of Knockout Stage Treatment

Should knockout-stage performance be added as a score multiplier or adjustment in the primary rating?

### Four Policy Alternatives:
1. **Alternative 1: Single Combined Rating with Knockout Adjustment ($R_{\text{overall}}$):**
   - *Verdict:* **REJECT.** Data is too sparse (only 20 matches in 4 years). Over half of the top bowlers have 0 knockout balls. Adjusting regular-season performance with noisy knockout samples creates wild distortions (e.g. Abhishek Sharma docked -10.22 points on 16 deliveries).
2. **Alternative 2: Arbitrary Knockout Point Bonus:**
   - *Verdict:* **REJECT.** Statistically indefensible and unsupported by data.
3. **Alternative 3: Primary Rating Based on High-Leverage Delivery Performance, with Knockout Performance Reported as a Supplementary Exposure & Verification Dimension:**
   - *Verdict:* **RECOMMENDED.** Delivery-level leverage $L(s)$ already accounts for match tension (a close game in the IPL group stage or T20I bilateral has genuine high leverage, while a blowout knockout match has low leverage). Knockout performance should be reported alongside the primary rating with explicit sample sizes, but not used to penalize players who never had the opportunity to play in knockouts.
4. **Alternative 4: Dedicated Knockout Leaderboard:**
   - *Verdict:* **VALUABLE BENCHMARK.** Publish a separate, transparent knockout leaderboard for players with $n_{\text{ko}} \ge 30$ deliveries as a dedicated spotlight.

---

## 5. Summary Recommendation

| Model Component | Baseline Specification | Phase 3 Recommended Specification | Methodological Justification |
|---|---|---|---|
| **Primary Estimand** | Extrapolated linear composite $\mu + 0.40\theta + w_K\delta$ | **Direct High-Pressure Value Added ($R_{\text{HP}}$)** (or Leverage-Weighted $R_{\text{LW}}$) | Eliminates 40x slope noise magnification; measures actual performance in high-pressure moments |
| **Reference State** | Artificial extrapolation to $PI^* = 0.90$ ($x^* = 0.40$) | **Observed High-Pressure Deliveries ($PI \ge 0.80$, $L \ge 0.30$)** | Grounded strictly in observed data; zero extrapolation |
| **Shrinkage Basis** | Empirical Bayes on regular deliveries only ($n_{\text{reg}}$) | **Empirical Bayes on Target High-Pressure Deliveries ($n_{\text{hp}}$)** | Correct precision weighting; treats all formats equally |
| **Knockout Handling** | Linear penalty/bonus docked directly into rating | **Dual Presentation: Primary HP Rating + Descriptive Knockout Audit** | Prevents 16-ball sample noise from destroying valid season-long evaluations |
| **Uncertainty Reporting** | Gaussian Monte Carlo $P(\text{top10})$ | **Empirical 90% Bootstrap CIs + Mandatory Zero-Crossing Disclosure** | Honest, transparent quantification of data sparsity |

The estimand review is complete. All findings confirm that shifting from linear extrapolation to direct high-pressure value-added restores mathematical defensibility and cricketing credibility.

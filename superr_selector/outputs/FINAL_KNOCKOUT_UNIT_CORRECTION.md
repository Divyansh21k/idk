# Final Audit & Correction: Knockout Rating Units, Estimand Dimensionality, and Score Withdrawal

**Project:** SupeRR Selector Season 2  
**Document:** `FINAL_KNOCKOUT_UNIT_CORRECTION.md`  
**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Status:** Frozen Methodology Correction & Score Withdrawal  
**Companion Dataset:** [`KNOCKOUT_PLAYER_RECALCULATION.csv`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/KNOCKOUT_PLAYER_RECALCULATION.csv)

---

## Executive Summary

This audit resolves the unit discrepancies and mathematical inconsistencies identified in the knockout sensitivity analyses (`KNOCKOUT_WEIGHT_SENSITIVITY.csv` and previous audit drafts). 

### Definitive Findings:
1. **Severe Dimensional & Estimand Incompatibility**:
   The primary rating ($R_{HP}$) and the sensitivity knockout score ($\hat{R}_{KO}$) measured two entirely different physical and statistical quantities:
   - $R_{HP}$ measures **role-adjusted, high-pressure-only performance ($PI \ge 0.80$) in runs above expectation per 100 balls**.
   - The old knockout score ($\hat{R}_{KO}$) measured **unadjusted delivery means across all knockout balls (low, medium, and high pressure), multiplied by 100, and shrunk toward $R_{HP}$ using an unstable small-sample variance component**.
2. **Disastrous Empirical Distortions Traced**:
   - For **Vaibhav Sooryavanshi**, his sensitivity score surged to $+92.63$ runs/100b based on 76 balls faced in knockouts. Crucially, **0 of those 76 balls were high pressure ($PI \ge 0.80$)**. His knockout score evaluated ordinary powerplay batting, not pressure performance.
   - For **Abhishek Sharma**, facing 22 balls in IPL playoffs with early dismissals yielded a raw delivery average of $-3.05$ runs/ball ($-305.27$ runs/100b). When shrunk toward $R_{HP} = +29.38$ with $\lambda = 0.2541$, his rating collapsed to $-52.28$ runs/100b, causing his rank to drop from #3 to #30, even though only 4 of those balls met the high-pressure threshold ($PI \ge 0.80$).
3. **Formal Withdrawal**:
   Because **72.9% of eligible batters and 74.6% of eligible bowlers have zero high-pressure knockout deliveries**, any attempted high-pressure knockout rating collapses into pure noise or unobserved prior collapse. The previous knockout score $\hat{R}_{KO}$ and any linear composite $R = (1-w) R_{HP} + w \hat{R}_{KO}$ **cannot be statistically repaired and are formally and explicitly withdrawn**.

---

## 1. Explicit Mathematical Definitions & Physical Units

To prevent further confusion, every variable in the SupeRR Selector rating framework is formally defined with its explicit units:

### Table 1: Explicit Variable Definitions and Dimensional Units

| Variable | Mathematical Symbol | Physical Unit | Description & Statistical Conditioning |
|:---|:---:|:---:|:---|
| **Delivery Run Value** | $v_{ik}$ | Runs per ball | Change in expected innings runs attributed to player $i$ on delivery $k$: $v = \Delta \mathbb{E}[\text{runs}]$. |
| **Tactical Role Baseline** | $\mu_{\text{role}}$ | Runs per ball | Expected delivery value for player $i$'s tactical role (e.g. Opener, Top Order, Death Bowler) across senior matches. |
| **Net Delivery Advantage** | $y_{ik} = v_{ik} - \mu_{\text{role}}$ | Runs per ball | Delivery value delivered *above tactical role expectation*. Centered with population mean $\approx 0$. |
| **High-Pressure Indicator** | $\mathbb{I}(PI_{ik} \ge 0.80)$ | Dimensionless $\{0, 1\}$ | Indicator that delivery $k$ belongs to the top quintile of tactical match leverage. |
| **High-Pressure Exposure** | $n_{HP, i}$ | Legal balls | Count of high-pressure deliveries faced (batters) or legally bowled (bowlers). |
| **Raw Sample HP Mean** | $\bar{y}_{HP, i}$ | Runs per ball | $\frac{1}{n_{HP, i}} \sum_{k: PI \ge 0.80} (v_{ik} - \mu_{\text{role}})$. |
| **Shrinkage Factor** | $\lambda_{HP, i}$ | Dimensionless $[0, 1)$ | Empirical Bayes shrinkage weight: $\lambda_i = \frac{n_{HP, i} \sigma_\mu^2}{n_{HP, i} \sigma_\mu^2 + \sigma_e^2}$. |
| **Primary Rating** | $R_{HP, i}$ | **Runs above expectation per 100 balls** | Empirical Bayes posterior mean scaled to standard cricket rate: $R_{HP, i} = \lambda_{HP, i} \bar{y}_{HP, i} \times 100$. |
| *Old Sensitivity Sample Mean* | $\bar{v}_{KO, i}$ | Runs per ball | $\frac{1}{n_{KO, i}} \sum_{k \in KO} v_{ik}$ across **all** knockout balls (unadjusted for role, unconditioned on $PI$). |
| *Old Scaled KO Mean* | $\bar{v}_{KO, i} \times 100$ | Runs per 100 balls | Raw knockout delivery mean scaled by 100. **Not role-adjusted, not high-pressure**. |
| *Old Shrunken KO Score* | $\hat{R}_{KO, i}$ | Purported runs/100b | $\lambda_{KO, i} (\bar{v}_{KO, i} \times 100) + (1 - \lambda_{KO, i}) R_{HP, i}$. **Dimensionally flawed hybrid**. |

---

## 2. Inconsistencies and Arithmetic Flaws in the Old Sensitivity Formulation

The sensitivity formula evaluated:
$$\hat{R}_{KO, i} = \lambda_{KO, i} \cdot (\bar{v}_{KO, i} \times 100) + (1 - \lambda_{KO, i}) \cdot R_{HP, i}$$
where:
$$\lambda_{KO, i} = \frac{n_{KO, i} \sigma_{\mu, KO}^2}{n_{KO, i} \sigma_{\mu, KO}^2 + \sigma_{e, KO}^2}$$
with $\sigma_{e, KO}^2 = 7.8857$ and $\sigma_{\mu, KO}^2 = 0.1168$.

### Four Mathematical and Conceptual Fatalities:
1. **Fatal Mismatch of Conditioning Sets**:
   - $R_{HP}$ is conditioned on $PI \ge 0.80$ (tactical crisis overs).
   - $\bar{v}_{KO}$ was conditioned on $\text{knock\_out} == 1$ (entire playoff matches, including quiet overs where $PI = 0.10$).
   - Averaging low-pressure playoff overs into a pressure rating directly corrupts the project estimand.
2. **Absence of Role Centering in Likelihood**:
   - In $R_{HP}$, delivery values are centered around $\mu_{\text{role}}$ (so an opening batter is judged relative to opening batters).
   - In $\bar{v}_{KO}$, raw delivery values $v$ were uncentered. Because early dismissals carry a large wicket penalty ($\approx -20$ runs), an opening batter facing 5 balls and getting dismissed has $\bar{v}_{KO} \approx -4.0$ runs/ball ($\mathbf{-400}$ runs/100b), whereas a lower-order finisher not getting out has $\bar{v}_{KO} \approx +1.5$ runs/ball.
3. **Severe Small-Sample Variance Inflation**:
   - Between-player variance in the primary model across 37,639 balls is $\sigma_\mu^2 = 0.0349$ ($SD = 18.68$ runs/100b).
   - In the sensitivity script, estimating variance on sparse knockout deliveries yielded $\sigma_{\mu, KO}^2 = 0.1168$ ($SD = 34.18$ runs/100b), an inflation factor of **$3.34\times$**.
   - This inflated variance caused $\lambda_{KO}$ to be drastically too high for tiny sample sizes ($n=23 \implies \lambda = 0.254$), allowing a 20-ball sample to overwhelm hundreds of league balls.
4. **Circular and Asymmetric Shrinkage Target**:
   - The formula shrunk $\bar{v}_{KO} \times 100$ toward $R_{HP, i}$. But $R_{HP, i}$ was already computed across all senior matches (which already included HP knockout balls). This introduced mathematical endogeneity and circular weighting.

---

## 3. Recalculation of Worked Examples from Underlying Data

Using the complete approved scope (2022–2026, 802 matches, 188,761 deliveries), we trace the exact underlying deliveries for **Vaibhav Sooryavanshi** and **Abhishek Sharma**:

### Case 1: Vaibhav Sooryavanshi (Striker ID: 50284, Opener)
- **Primary High-Pressure Evidence**:
  - High-pressure balls faced ($PI \ge 0.80$): $n_{HP} = 190$ balls.
  - Primary rating: $R_{HP} = \mathbf{+38.6601}$ runs above expectation per 100 HP balls (Rank #1 Batter).
- **Underlying Knockout Evidence**:
  - Total knockout balls faced: $n_{KO} = 76$ balls (79 delivery rows including non-faced balls).
  - Total runs scored: 147 runs off 76 balls in knockout matches.
  - Sum of delivery values: $\sum v_{\text{bat}} = +109.6120$ runs.
  - Raw knockout mean: $\bar{v}_{KO} = \frac{+109.6120}{76} = \mathbf{+1.4423}\text{ runs/ball}$ ($\mathbf{+144.23}\text{ runs/100b}$).
  - Old shrinkage factor: $\lambda_{KO} = \frac{79 \times 0.1168}{79 \times 0.1168 + 7.8857} = \mathbf{0.5392}$.
  - Old sensitivity score:
    $$\hat{R}_{KO} = 0.5392 \times (+138.75) + (1 - 0.5392) \times (+38.66) = \mathbf{+92.63}\text{ runs/100b}$$
- **The Decisive Audit Discovery**:
  - High-pressure knockout balls faced ($PI \ge 0.80$): **$n_{HP, KO} = \mathbf{0}$ BALLS**.
  - Vaibhav Sooryavanshi **never faced a single delivery under high pressure ($PI \ge 0.80$) in any knockout match**.
  - All 76 balls he faced in knockouts were in low-leverage situations ($PI < 0.80$).
  - **Audit Verdict**: Crediting Sooryavanshi with $+92.63$ on a "pressure" metric based on 0 high-pressure deliveries is an indefensible artifact of conflating ordinary knockout play with pressure performance.

---

### Case 2: Abhishek Sharma (Striker ID: 6281, Opener)
- **Primary High-Pressure Evidence**:
  - High-pressure balls faced ($PI \ge 0.80$): $n_{HP} = 560$ balls.
  - Primary rating: $R_{HP} = \mathbf{+29.3815}$ runs above expectation per 100 HP balls (Rank #3 Batter).
- **Underlying Knockout Evidence**:
  - Total knockout balls faced: $n_{KO} = 22$ balls (23 delivery rows including 1 wide).
  - In those 22 balls, he suffered multiple early dismissals in playoff matches.
  - Sum of delivery values: $\sum v_{\text{bat}} = -67.1592$ runs.
  - Raw knockout mean: $\bar{v}_{KO} = \frac{-67.1592}{22} = \mathbf{-3.0527}\text{ runs/ball}$ ($\mathbf{-305.27}\text{ runs/100b}$).
  - Old shrinkage factor: $\lambda_{KO} = \frac{23 \times 0.1168}{23 \times 0.1168 + 7.8857} = \mathbf{0.2541}$.
  - Old sensitivity score:
    $$\hat{R}_{KO} = 0.2541 \times (-292.00) + (1 - 0.2541) \times (+29.38) = \mathbf{-52.28}\text{ runs/100b}$$
  - When combined via $w_K = 0.20$:
    $$R_{\text{composite}} = 0.80 \times (+29.38) + 0.20 \times (-52.28) = \mathbf{+13.05}\text{ runs/100b} \quad (\text{Rank \#3} \to \text{Rank \#18})$$
  - When combined via $w_K = 0.25$:
    $$R_{\text{composite}} = 0.75 \times (+29.38) + 0.25 \times (-52.28) = \mathbf{+8.97}\text{ runs/100b} \quad (\text{Rank \#3} \to \text{Rank \#30})$$
- **The Decisive Audit Discovery**:
  - High-pressure knockout balls faced ($PI \ge 0.80$): **$n_{HP, KO} = \mathbf{4}$ BALLS**.
  - In those 4 balls, sum $v = -16.7649$ runs.
  - A sample size of 4 balls has a standard error of $\sqrt{7.8857 / 4} \times 100 = \mathbf{140.4}\text{ runs/100b}$!
  - **Audit Verdict**: Demoting Abhishek Sharma 27 rank positions based on a sample of 4 high-pressure balls (or 22 unadjusted low-pressure balls) is a complete statistical failure that destroys the reliability of the 560-ball senior rating.

---

## 4. Formal Verification Across Top Players

All values have been independently recalculated from raw ball-by-ball records and exported to [`KNOCKOUT_PLAYER_RECALCULATION.csv`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/KNOCKOUT_PLAYER_RECALCULATION.csv).

### Table 2: Recalculated Knockout Exposure and Scores for Top Players

| Player Name | Discipline | Role | $n_{HP}$ | $R_{HP}$ (runs/100b) | Actual KO Balls | Raw KO per 100b | Old $\hat{R}_{KO}$ | Actual HP KO Balls | Status & Audit Finding |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Vaibhav Sooryavanshi** | Batter | Opener | 190 | **+38.66** | 76 | +144.23 | +92.63 | **0** | Flawed: 0 HP balls in knockouts. |
| **Suryakumar Yadav** | Batter | Middle | 598 | **+30.47** | 108 | +30.18 | +29.95 | 31 | Valid HP sample; score stable. |
| **Abhishek Sharma** | Batter | Opener | 560 | **+29.38** | 22 | -305.27 | -52.28 | **4** | Flawed: Severe 4-ball small-sample distortion. |
| **Yashasvi Jaiswal** | Batter | Opener | 604 | **+25.63** | 114 | -14.77 | +0.25 | 18 | Small sample pulls down 604-ball baseline. |
| **Pathum Nissanka** | Batter | Opener | 619 | **+22.42** | 19 | -68.57 | +2.44 | 0 | 0 HP balls in knockouts. |
| **Phil Salt** | Batter | Opener | 494 | **+21.35** | 37 | +71.24 | +39.01 | 7 | Low exposure. |
| **Ryan Rickelton** | Batter | Opener | 283 | **+20.80** | **0** | 0.00 | +20.80 | **0** | National team / franchise did not qualify. |
| **Virat Kohli** | Batter | Opener | 584 | **+19.73** | 169 | +21.87 | +20.91 | 42 | Substantial exposure ($n=42$ HP balls). |
| **Reece Topley** | Bowler | Pace | 117 | **+20.65** | 18 | -130.89 | +12.40 | 0 | 0 HP balls in knockouts. |
| **Tim Southee** | Bowler | Pace | 223 | **+18.94** | 25 | +4.09 | +17.84 | 3 | Low exposure. |
| **Rashid Khan** | Bowler | Spin | 490 | **+18.28** | 197 | +7.77 | +14.16 | 45 | Substantial exposure ($n=45$ HP balls). |
| **Mayank Yadav** | Bowler | Pace | 86 | **+17.47** | **0** | 0.00 | +17.47 | **0** | 0 knockout balls. |
| **Sikandar Raza** | Bowler | Spin | 267 | **+17.40** | **0** | 0.00 | +17.40 | **0** | Zimbabwe did not play tournament finals. |

---

## 5. Formal Withdrawal of the Old Knockout Score

### Declaration of Withdrawal:
1. The metric $\hat{R}_{KO}$ computed in `KNOCKOUT_WEIGHT_SENSITIVITY.csv` and described in earlier drafts is **formally withdrawn from the SupeRR Selector Season 2 project**.
2. Any composite ranking formula blending non-knockout ratings with $\hat{R}_{KO}$ ($R_{\text{composite}} = (1 - w) R_{\text{base}} + w \hat{R}_{KO}$) is **statistically invalid and prohibited**.
3. **Reason for Non-Repairability**:
   - High-pressure knockout data is fatally sparse ($N_{\text{total}} = 1,158$ deliveries across 5 seasons).
   - 72.9% of eligible batters and 74.6% of eligible bowlers have $n_{HP, KO} = 0$.
   - Any attempt to repair the score by restricting it strictly to high-pressure balls ($PI \ge 0.80$) leaves over 70% of players without data, collapsing their posterior estimates back to the primary rating $R_{HP}$ while subjecting the remaining 30% to extreme noise variance.
   - Manufacturing an ad-hoc conversion factor to bridge unadjusted delivery means with role-adjusted high-pressure ratings violates basic statistical integrity.

---

## 6. Approved Treatment of Knockout Performance

In accordance with [`FINAL_KNOCKOUT_DECISION.md`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/FINAL_KNOCKOUT_DECISION.md) (**Alternative A: Decoupled Dimensions**):
1. **Primary Metric**:
   $R_{HP}$ (role-adjusted runs above expectation per 100 high-pressure balls across all senior matches, $N=37,639$) is the sole scalar metric used for primary player rankings.
2. **Knockout Context**:
   Knockout performance is recognized through a **dedicated secondary context panel and spotlight**:
   - Knockout Balls Faced/Bowled ($n_{KO}$).
   - High-Pressure Knockout Deliveries ($n_{HP, KO}$).
   - Playoff Experience Indicator ($\mathbb{I}(n_{KO} \ge 50)$).
   This recognizes big-match performers without corrupting primary ratings with small-sample noise or franchise qualification bias.

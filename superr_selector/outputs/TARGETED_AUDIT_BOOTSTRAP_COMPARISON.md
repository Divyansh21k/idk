# Targeted Audit: Variance-Component Bootstrap Comparison

**Document:** `TARGETED_AUDIT_BOOTSTRAP_COMPARISON.md`  
**Date:** 2026-11-18  
**Branch:** `model-repair`  
**Audit Target:** Empirical Comparison of Fixed vs. Re-estimated Variance Components in the 500-Iteration Match-Cluster Bootstrap

---

## Executive Summary

Phase 4 utilized a **Fixed-Component Match-Cluster Bootstrap**, which resampled matches with replacement while holding variance components ($\sigma_e^2, \sigma_{\mu}^2$) and role prior means ($\mu_{\text{role}}$) fixed at full-sample estimates.

To verify whether this simplification masked ranking instability, we executed a **Full Variance-Component Re-estimation Bootstrap (500 resamples)**, re-estimating $\sigma_e^{2(b)}$, $\sigma_{\mu}^{2(b)}$, and $\mu_{\text{role}}^{(b)}$ from scratch within every single match-cluster resample using identical stratified match units.

### Key Audit Findings
1. **Computational Feasibility:** Re-estimating all variance components and role parameters across 500 stratified match resamples is **fully computationally feasible**, executing in **6.4 seconds**.
2. **Massive Interval Expansion for Low-Exposure Players:**
   - For high-exposure players ($250+$ balls), rating interval width expands moderately (+45.8% for batters; +85.7% for bowlers).
   - For low-exposure players (50–100 balls), rating interval width **explodes by +175.2% for batters and +271.4% for bowlers** (e.g. Wayne Parnell's CI width increases from 32.1 to 112.9; Mayank Yadav from 28.0 to 96.6).
3. **The Cluster-Duplication Bias Mechanism:**
   - In match-cluster resampling, individual matches are duplicated 2x, 3x, or 4x. This cluster duplication artificially inflates the empirical between-player variance of sample means:
     * Full-sample $\sigma_{\mu}^2 = 0.0349 \implies$ Bootstrap mean $\sigma_{\mu}^{2(b)} = \mathbf{0.1921}$ (a 5.5x inflation!).
   - Artificially inflated $\sigma_{\mu}^2$ increases the shrinkage factor $\lambda_i^{(b)}$ toward 1.0, **dismantling empirical shrinkage** and causing resampled ratings to track noisy raw means.
4. **Distortion of Top-10 Inclusion Probabilities:**
   - When shrinkage collapses in resamples, small-sample players produce extreme lucky spikes that leapfrog high-volume anchors.
   - For **Rashid Khan** (490 balls), under-shrinkage of rival low-sample pacers drops his $P(\text{Top 10})$ from **47.2% to 2.8%**!
   - Conversely, low-sample pacers (Wayne Parnell, Mayank Yadav) have their $P(\text{Top 10})$ artificially inflated to $68\% - 71\%$.
5. **Audit Ruling:** Holding population hyperparameters fixed at full-sample empirical estimates is **strictly necessary** to prevent match-duplication artifacts from destroying empirical Bayes shrinkage.

---

## 1. Experimental Design: Fixed vs. Re-estimated Bootstrap

Both procedures were executed on the identical 802 matches, partitioned into the four competition strata (`IPL league`, `IPL knockout`, `T20I non-knockout`, `T20I final`), with 500 resamples using seed 42:

```
[Match Resampling (500 iterations)]
       |
       +---> Procedure 1: Fixed-Component Bootstrap (Phase 4 Baseline)
       |        - sigma_e^2 held at 8.31 (bat) / 8.26 (bowl)
       |        - sigma_mu^2 held at 0.035 (bat) / 0.022 (bowl)
       |        - Role prior means held at full-sample values
       |
       +---> Procedure 2: Full Re-estimation Bootstrap (Audit Test)
                - In each resample b:
                  * sigma_e^{2(b)} = Var(v_t^{(b)})
                  * mu_{role}^{(b)} = mean(v_t^{(b)} in role)
                  * sigma_mu^{2(b)} = max(Var(y_bar_i^{(b)}) - sigma_e^{2(b)} * mean(1/n_i^{(b)}), 0.005)
                  * lambda_i^{(b)} = (n_i^{(b)} * sigma_mu^{2(b)}) / (n_i^{(b)} * sigma_mu^{2(b)} + sigma_e^{2(b)})
```

---

## 2. Quantitative Comparison of Rating Interval Widths

The table below contrasts the 90% rating interval width ($\text{Width} = CI_{90, \text{hi}} - CI_{90, \text{lo}}$) across exposure tiers and competition classes:

### 2.1 Interval Width Expansion by Exposure Tier

| Discipline | Exposure Tier (HP Balls) | Fixed CI Width (runs/100b) | Re-estimated CI Width (runs/100b) | Mean Width Expansion (%) |
|---|---|---|---|---|
| **Batter** | **High ($250+$ balls)** | 29.62 | 43.18 | **+45.8%** |
| | **Medium (100–250 balls)** | 28.68 | 58.11 | **+102.6%** |
| | **Low (50–100 balls)** | 24.59 | 67.67 | **+175.2%** |
| **Bowler** | **High ($250+$ balls)** | 25.18 | 46.74 | **+85.7%** |
| | **Medium (100–250 balls)** | 21.17 | 55.44 | **+161.9%** |
| | **Low (50–100 balls)** | 18.53 | 68.82 | **+271.4%** |

### 2.2 Interval Width Expansion by Competition Class

| Discipline | Competition Dominance | Fixed CI Width (runs/100b) | Re-estimated CI Width (runs/100b) | Mean Width Expansion (%) |
|---|---|---|---|---|
| **Batter** | **IPL-Dominant ($>50\%$ IPL)** | 29.20 | 59.52 | **+103.8%** |
| | **T20I-Dominant** | 25.99 | 58.36 | **+124.6%** |
| **Bowler** | **IPL-Dominant ($>50\%$ IPL)** | 21.09 | 58.06 | **+175.3%** |
| | **T20I-Dominant** | 20.93 | 61.46 | **+193.6%** |

---

## 3. Impact on Top 10 Batters & Bowlers

### 3.1 Top 10 Batters Comparison

| Rank | Player Name | HP Balls ($n_{\text{hp}}$) | Fixed CI Width | Re-estimated CI Width | Width Change (%) | Fixed $P(\text{Top 10})$ | Re-estimated $P(\text{Top 10})$ | Fixed Rank Interval | Re-estimated Rank Interval |
|---|---|---|---|---|---|---|---|---|---|
| **1** | **Vaibhav Sooryavanshi** | 190 | 46.47 | 79.08 | **+70.2%** | 84.2% | 87.6% | $[1, 27]$ | $[1, 29]$ |
| **2** | **Suryakumar Yadav** | 598 | 29.90 | 38.30 | **+28.1%** | 80.6% | 60.6% | $[1, 23]$ | $[2, 35]$ |
| **3** | **Abhishek Sharma** | 560 | 40.37 | 51.97 | **+28.7%** | 74.8% | 56.4% | $[1, 40]$ | $[2, 56]$ |
| **4** | **Yashasvi Jaiswal** | 604 | 26.11 | 33.07 | **+26.7%** | 69.8% | 39.4% | $[2, 29]$ | $[4, 45]$ |
| **5** | **Pathum Nissanka** | 619 | 18.37 | 23.62 | **+28.6%** | 54.0% | 14.8% | $[3, 25]$ | $[8, 55]$ |
| **6** | **Phil Salt** | 494 | 30.54 | 40.80 | **+33.6%** | 51.0% | 23.4% | $[2, 56]$ | $[4, 68]$ |
| **7** | **Ryan Rickelton** | 283 | 30.76 | 48.25 | **+56.8%** | 46.2% | 34.8% | $[2, 55]$ | $[3, 64]$ |
| **8** | **Virat Kohli** | 584 | 24.53 | 32.51 | **+32.5%** | 39.4% | 11.8% | $[4, 49]$ | $[9, 66]$ |
| **9** | **Prabhsimran Singh** | 350 | 43.07 | 62.17 | **+44.4%** | 43.2% | 35.0% | $[1, 77]$ | $[2, 79]$ |
| **10** | **Daryl Mitchell** | 183 | 25.94 | 44.18 | **+70.3%** | 34.2% | 46.4% | $[3, 48]$ | $[3, 52]$ |

---

### 3.2 Top 10 Bowlers Comparison

| Rank | Player Name | HP Balls ($n_{\text{hp}}$) | Fixed CI Width | Re-estimated CI Width | Width Change (%) | Fixed $P(\text{Top 10})$ | Re-estimated $P(\text{Top 10})$ | Fixed Rank Interval | Re-estimated Rank Interval |
|---|---|---|---|---|---|---|---|---|---|
| **1** | **Reece Topley** | 117 | 33.70 | 99.47 | **+195.2%** | 55.4% | 70.4% | $[1, 67]$ | $[1, 76]$ |
| **2** | **Tim Southee** | 223 | 35.30 | 78.11 | **+121.3%** | 47.0% | 40.2% | $[1, 85]$ | $[1, 95]$ |
| **3** | **Rashid Khan** | **490** | **19.70** | **31.67** | **+60.8%** | **47.2%** | **2.8%** | **$[2, 44]$** | **$[7, 72]$** |
| **4** | **Mayank Yadav** | 86 | 27.95 | 96.57 | **+245.5%** | 42.0% | 70.6% | $[1, 76]$ | $[1, 74]$ |
| **5** | **Sikandar Raza** | 267 | 24.29 | 47.23 | **+94.4%** | 39.2% | 13.2% | $[2, 61]$ | $[7, 78]$ |
| **6** | **Wayne Parnell** | 71 | 32.08 | 112.86 | **+251.8%** | 37.4% | 67.6% | $[1, 90]$ | $[1, 80]$ |
| **7** | **Abrar Ahmed** | 188 | 21.81 | 55.05 | **+152.4%** | 31.6% | 16.6% | $[2, 59]$ | $[5, 76]$ |
| **8** | **Krunal Pandya** | 238 | 21.91 | 43.05 | **+96.5%** | 31.6% | 8.2% | $[3, 66]$ | $[12, 85]$ |
| **9** | **Mehidy Hasan Miraz**| 68 | 20.61 | 80.00 | **+288.2%** | 26.2% | 35.8% | $[3, 74]$ | $[2, 92]$ |
| **10** | **Harry Tector** | 88 | 14.53 | 40.93 | **+181.7%** | 16.6% | 15.4% | $[7, 51]$ | $[11, 78]$ |

---

## 4. Why Re-estimation Under-Shrinks: The Cluster Duplication Mechanism

The drastic expansion of interval widths and the collapse of Rashid Khan's $P(\text{Top 10})$ is caused by a known statistical phenomenon in hierarchical bootstrap theory:

### 4.1 Match Duplication Inflates Between-Player Variance
In standard i.i.d. bootstrap, observations are sampled individually. In cluster bootstrap, **entire matches with all deliveries are resampled simultaneously**.
- When a match is sampled 3 times, a batter's runs in that match are multiplied by 3.
- This creates artificial between-player dispersion in the sample means $\bar{y}_i^{(b)}$.
- The Method-of-Moments estimator for talent variance:
  $$\hat{\sigma}_{\mu}^{2(b)} = \max\left( \text{Var}(\bar{y}_i^{(b)}) - \sigma_e^2 \cdot \overline{n^{-1}}, \quad 0.005 \right)$$
  interprets this artificial clustering dispersion as true talent spread!
- As reported in Section 5 of our script:
  * Batters $\sigma_{\mu}^2$: Full sample $= 0.0349 \implies$ Bootstrap mean $= \mathbf{0.1921}$ (5.5x inflation).
  * Bowlers $\sigma_{\mu}^2$: Full sample $= 0.0223 \implies$ Bootstrap mean $= \mathbf{0.1795}$ (8.0x inflation).

### 4.2 Collapse of Shrinkage Protection
When $\sigma_{\mu}^2$ is inflated by 8x:
$$\lambda_i = \frac{n_i \sigma_{\mu}^2}{n_i \sigma_{\mu}^2 + \sigma_e^2}$$
For a player with only 70 balls (like Wayne Parnell):
- Full sample: $\lambda = \frac{70 \times 0.0223}{70 \times 0.0223 + 8.26} = \mathbf{0.159}$ (heavily shrunk to role prior).
- Re-estimated bootstrap: $\lambda = \frac{70 \times 0.1795}{70 \times 0.1795 + 8.26} = \mathbf{0.603}$ (minimally shrunk!).
Because low-sample players are barely shrunk in the re-estimation resamples, their noisy delivery fluctuations produce massive score swings ($\pm 112$ runs/100b), allowing random spikes to overwhelm stable, high-volume pillars like Rashid Khan.

---

## 5. Audit Conclusions

1. **Fixed-Parameter Bootstrap is Methodologically Superior:** Holding the population variance components fixed at full-sample estimates prevents cluster-duplication bias from destroying empirical Bayes shrinkage.
2. **Re-estimation Confirms Sensitivity:** The re-estimation experiment proves that low-exposure players (50–100 balls) are extremely sensitive to shrinkage assumptions. This reinforces the decision to treat them as **exploratory candidates rather than established performers**.

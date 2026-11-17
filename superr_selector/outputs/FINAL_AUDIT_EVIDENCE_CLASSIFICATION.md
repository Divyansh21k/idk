# Final Independent Audit: Evidence Classification Rules & Latent Talent Defensibility

**Document:** `FINAL_AUDIT_EVIDENCE_CLASSIFICATION.md`  
**Date:** 2026-11-17  
**Branch:** `model-repair`  
**Audit Target:** Statistical Validity of Evidence Tier Classifications in Phase 4 Output Tables

---

## Executive Summary

Phase 4 introduced a three-tier qualitative classification framework:
- `Strong evidence`
- `Promising but limited evidence`
- `Highly uncertain`

Our independent audit examined the implementation in `phase4_pipeline.py`.

### Key Audit Findings
1. **Critical Statistical Fallacy Identified:** The Phase 4 classification rule assigned "Strong evidence" whenever `row['elig_sustained'] and row['CI_90_lo'] > 0 and row['P_top10'] >= 0.35`. 
   - However, `row['CI_90_lo']` is the lower bound of the **shrunken score interval**, which is compressed by the shrinkage factor $\lambda_i \in [0.15, 0.45]$.
   - Treating `CI_90_lo > 0` of a shrunken score as proof that the player's **true latent talent $\mu_i$ is positive** is a statistical fallacy.
2. **Impact on Bowlers:** Because bowler shrinkage is heavy ($\bar{\lambda} \approx 0.28$) and between-player variance is small ($\sigma_{\mu} = 14.94$), three bowlers (Reece Topley, Tim Southee, and Sikandar Raza) were classified as "Strong evidence" even though their **Bayesian posterior credible intervals for true talent cross zero** (`Post_CI_lo` is $-0.77$ for Topley, $-0.47$ for Southee, and $-1.33$ for Raza).
3. **Only ONE Bowler in the Dataset Has True "Strong Evidence":**
   - **Rashid Khan** is the sole bowler whose 90% posterior credible interval for latent ability is strictly positive (`Post_CI_lo = +2.16` runs saved per 100 balls across 490 high-pressure deliveries).
4. **Impact on Batters:** The top 8 batters (Sooryavanshi, SKY, Abhishek, Jaiswal, Nissanka, Salt, Rickelton, Kohli) all maintain strictly positive posterior credible intervals (`Post_CI_lo > 0`). However, Daryl Mitchell (Rank 10) was incorrectly classified as "Strong evidence" when his posterior lower bound is $-4.32$.
5. **Audit Action:** We provide the corrected, defensible classification rules and identify every player whose label changes.

---

## 1. Reproduction of Phase 4 Rules

In `superr_selector/src/phase4_pipeline.py` (lines 332–347), the code executed:

```python
def classify_evidence(row):
    if not row['elig_floor']:
        return "Ineligible"
    # Strong evidence: Sustained tier, CI lower bound > 0, and substantial Top 10 probability
    if row['elig_sustained'] and row['CI_90_lo'] > 0 and row['P_top10'] >= 0.35:
        return "Strong evidence"
    # If sustained and CI_lo > 0 but P_top10 < 0.35 (solid above-average performer)
    elif row['elig_sustained'] and row['CI_90_lo'] > 0:
        return "Strong evidence (Solid Above-Average)"
    # Promising but limited evidence: meets floor, positive point estimate, but narrower sample
    elif row['R_HP'] > 0 and (row['CI_90_hi'] - row['CI_90_lo']) <= 30.0:
        return "Promising but limited evidence"
    else:
        return "Highly uncertain"
```

### Why This Rule Is Flawed:
The bootstrap interval $[CI_{90, \text{lo}}, CI_{90, \text{hi}}]$ reflects the sampling variability of the estimator:
$$\hat{R}_i = \lambda_i \bar{y}_i + (1 - \lambda_i)\mu_{\text{role}}$$
Its standard error is:
$$\text{SE}(\hat{R}_i) \approx \lambda_i \frac{\sigma_e}{\sqrt{n_i}}$$
Because $\lambda_i \le 0.40$ for most players, multiplying by $\lambda_i$ artificially compresses the interval to $25\% - 40\%$ of the uncertainty of the true latent talent. Testing whether $\hat{R}_{i, \text{lo}} > 0$ does **NOT** prove that $\mu_i > 0$ with 90% confidence.

---

## 2. The Defensible Evidence Classification Standard

To legitimately classify a player as having **"Strong Evidence" of positive clutch talent**, the standard must test whether the player's **true latent talent $\mu_i$ is statistically significantly positive at $\alpha = 0.10$**:

Under the conjugate normal model, the posterior distribution of latent talent given data is:
$$\mu_i \mid \bar{y}_i \sim \mathcal{N}\left( R_{\text{HP}, i}, \quad \sigma_{\text{post}, i}^2 \right)$$
Where the posterior variance is:
$$\sigma_{\text{post}, i}^2 = (1 - \lambda_i)\sigma_{\mu}^2$$
The 90% Bayesian Posterior Credible Interval for latent talent is:
$$\left[ \text{Post\_CI}_{\text{lo}}, \text{Post\_CI}_{\text{hi}} \right] = \left[ R_{\text{HP}, i} - 1.645 \sqrt{1 - \lambda_i} \sigma_{\mu}, \quad R_{\text{HP}, i} + 1.645 \sqrt{1 - \lambda_i} \sigma_{\mu} \right]$$

### Defensible Classification Rules:
1. **Strong Evidence (Elite Candidate):**
   - Meets Sustained Tier ($n_{\text{hp}} \ge 100$, $m_{\text{hp}} \ge 10$, $n_{\text{total}} \ge 300$).
   - Posterior credible interval strictly positive: **$\text{Post\_CI}_{\text{lo}} > 0$**.
   - Stable top-tier inclusion: $P(\text{Top 10}) \ge 0.35$.
2. **Strong Evidence (Solid Above-Average):**
   - Meets Sustained Tier.
   - Posterior credible interval strictly positive: $\text{Post\_CI}_{\text{lo}} > 0$.
   - $P(\text{Top 10}) < 0.35$ (proven above-average, but rank is in the 10–25 range).
3. **Promising but Limited Evidence:**
   - Meets Floor Tier ($n_{\text{hp}} \ge 50$, $m_{\text{hp}} \ge 5$, $n_{\text{total}} \ge 200$).
   - Point rating $R_{\text{HP}} > 0$.
   - Posterior interval spans near or slightly below zero ($-10.0 \le \text{Post\_CI}_{\text{lo}} \le 0.0$).
4. **Highly Uncertain:**
   - Confidence interval spans zero widely ($\text{Post\_CI}_{\text{lo}} < -10.0$ or CI width $> 45$ runs/100b).

---

## 3. Player-by-Player Classification Audit (Top 15)

### 3.1 Batters Re-Classification Audit

| Rank | Player Name | Rating ($R_{\text{HP}}$) | Reliability ($\lambda$) | Phase 4 $CI_{\text{lo}}$ | Posterior Talent $\text{Post\_CI}_{\text{lo}}$ | Phase 4 Tier | Defensible Tier | Status Change |
|---|---|---|---|---|---|---|---|---|
| **1** | **Vaibhav Sooryavanshi** | +38.66 | 0.444 | +12.21 | **+15.74** | Strong evidence | **Strong evidence** | Unchanged |
| **2** | **Suryakumar Yadav** | +30.47 | 0.715 | +15.15 | **+14.07** | Strong evidence | **Strong evidence** | Unchanged |
| **3** | **Abhishek Sharma** | +29.38 | 0.702 | +7.49 | **+12.59** | Strong evidence | **Strong evidence** | Unchanged |
| **4** | **Yashasvi Jaiswal** | +25.63 | 0.717 | +11.49 | **+9.28** | Strong evidence | **Strong evidence** | Unchanged |
| **5** | **Pathum Nissanka** | +22.42 | 0.722 | +13.11 | **+6.22** | Strong evidence | **Strong evidence** | Unchanged |
| **6** | **Phil Salt** | +21.35 | 0.674 | +4.11 | **+3.82** | Strong evidence | **Strong evidence** | Unchanged |
| **7** | **Ryan Rickelton** | +20.80 | 0.543 | +4.33 | **+0.02** | Strong evidence | **Strong evidence** | Unchanged |
| **8** | **Virat Kohli** | +19.73 | 0.710 | +6.09 | **+3.19** | Strong evidence | **Strong evidence** | Unchanged |
| **9** | **Prabhsimran Singh** | +19.43 | 0.595 | -1.17 | -0.12 | Highly uncertain | **Promising but limited** | **CORRECTED** |
| **10** | **Daryl Mitchell** | +18.79 | 0.435 | +5.80 | **-4.32** | Strong evidence (Solid) | **Promising but limited** | **DOWNGRADED** |
| **11** | **Jonny Bairstow** | +18.33 | 0.463 | -0.61 | **-5.32** | Highly uncertain | **Promising but limited** | **CORRECTED** |
| **12** | **Muhammad Waseem** | +16.83 | 0.467 | +1.01 | **-5.58** | Strong evidence (Solid) | **Promising but limited** | **DOWNGRADED** |
| **13** | **Harry Brook** | +15.78 | 0.419 | +1.20 | **-7.58** | Strong evidence (Solid) | **Promising but limited** | **DOWNGRADED** |

---

### 3.2 Bowlers Re-Classification Audit

| Rank | Player Name | Rating ($R_{\text{HP}}$) | Reliability ($\lambda$) | Phase 4 $CI_{\text{lo}}$ | Posterior Talent $\text{Post\_CI}_{\text{lo}}$ | Phase 4 Tier | Defensible Tier | Status Change |
|---|---|---|---|---|---|---|---|---|
| **1** | **Reece Topley** | +20.65 | 0.239 | +4.83 | **-0.77** | Strong evidence | **Promising but limited** | **DOWNGRADED** |
| **2** | **Tim Southee** | +18.94 | 0.376 | +2.38 | **-0.47** | Strong evidence | **Promising but limited** | **DOWNGRADED** |
| **3** | **Rashid Khan** | +18.28 | 0.570 | +8.22 | **+2.16** | Strong evidence | **Strong evidence** | **CONFIRMED (Sole Bowler)** |
| **4** | **Mayank Yadav** | +17.47 | 0.188 | +3.72 | **-4.67** | Promising but limited | **Promising but limited** | Unchanged |
| **5** | **Sikandar Raza** | +17.40 | 0.419 | +5.42 | **-1.33** | Strong evidence | **Promising but limited** | **DOWNGRADED** |
| **6** | **Wayne Parnell** | +16.32 | 0.161 | +1.16 | **-6.19** | Highly uncertain | **Promising but limited** | **CORRECTED** |
| **7** | **Abrar Ahmed** | +16.17 | 0.337 | +5.92 | **-3.84** | Strong evidence (Solid) | **Promising but limited** | **DOWNGRADED** |
| **8** | **Krunal Pandya** | +15.83 | 0.391 | +4.55 | **-3.34** | Strong evidence (Solid) | **Promising but limited** | **DOWNGRADED** |
| **9** | **Mehidy Hasan Miraz**| +14.46 | 0.155 | +3.69 | **-8.13** | Promising but limited | **Promising but limited** | Unchanged |
| **10** | **Harry Tector** | +14.06 | 0.192 | +7.23 | **-8.03** | Promising but limited | **Promising but limited** | Unchanged |
| **11** | **Mohammad Nawaz** | +13.88 | 0.368 | +0.22 | **-4.34** | Strong evidence (Solid) | **Promising but limited** | **DOWNGRADED** |

---

## 4. Summary of Evidence Label Changes

### Batters:
- **Daryl Mitchell (#10), Muhammad Waseem (#12), and Harry Brook (#13)** are downgraded from `Strong evidence (Solid Above-Average)` to `Promising but limited evidence`.
- The top 8 batters remain definitively confirmed as `Strong evidence`.

### Bowlers:
- **5 of the top 8 bowlers** (Reece Topley, Tim Southee, Sikandar Raza, Abrar Ahmed, Krunal Pandya) are downgraded from `Strong evidence` to `Promising but limited evidence`.
- **Rashid Khan (#3)** is the **ONLY bowler in the entire dataset** who qualifies as `Strong evidence` under defensible statistical standards.
- This accurately reflects cricket reality: bowling in T20 cricket is subject to severe structural over-limits (4 overs per match), making individual bowler skill much harder to separate from situation luck than top-order batting.

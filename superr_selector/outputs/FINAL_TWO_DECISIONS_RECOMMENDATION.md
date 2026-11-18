# Final Two Decisions Recommendation: SupeRR Selector Season 2

**Document:** `FINAL_TWO_DECISIONS_RECOMMENDATION.md`  
**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Context:** Targeted Methodology Decision Review  
**Supporting Reports:**
- `DECISION1_KNOCKOUT_REWARD_ANALYSIS.md`
- `DECISION2_CONSISTENCY_AND_PRESSURE_ANALYSIS.md`
- `DECISION3_JOINT_METHODOLOGY_ANALYSIS.md`
- `KNOCKOUT_WEIGHT_SENSITIVITY.csv`
- `PLAYER_CONSISTENCY_PRESSURE_DIAGNOSTICS.csv`

---

## 1. Definitive Methodology Recommendations

Based on exhaustive mathematical proofs, cross-sectional empirical evaluations across all 802 senior matches (188,761 deliveries), and joint testing across five critical player archetypes:

### Recommendation on Decision 1: Knockout Treatment
**ADOPT OPTION 1A (Separate Knockout Dimension / Dual Leaderboard).**
- **Decision**: Do **not** apply an explicit knockout weight ($w_K$) or score multiplier to the primary player rating.
- **Implementation**:
  - The primary rating $R_{HP}$ evaluates all high-pressure deliveries across the entire senior dataset (IPL and T20I), where tense moments in playoff matches naturally receive higher physical win-probability leverage ($L = |\partial \text{WP}/\partial v|$).
  - Knockout Performance is reported as an **explicit secondary leaderboard and qualification dimension** detailing:
    1. Knockout Volume ($n_{KO}$).
    2. Shrunken Knockout Expected Run Value ($\hat{R}_{KO}$).
    3. Proportion of pressure balls delivered in playoff matches.
- **Why Option 1B (Weighted Score) is Rejected**:
  Knockout deliveries comprise only **3.05% of all balls** and only **25 matches**. Over **60% of eligible batters and 75% of eligible bowlers have zero knockout deliveries**. Blending a knockout component into the primary score penalizes world-class players on non-qualifying teams (e.g. Sikandar Raza, Harry Tector, Ryan Rickelton) and allows 20-ball playoff flukes to destabilize 500-ball league careers.

---

### Recommendation on Decision 2: Consistency vs. Pressure Performance
**ADOPT OPTION 2A (High-Pressure Absolute Performance: $R_{HP}$).**
- **Decision**: The primary player estimand must measure **absolute context-adjusted performance above tactical role expectation in high-pressure match states ($PI \ge 0.800$)**.
- **Implementation**:
  $$\hat{R}_{HP, i} = \left[ \lambda_i \bar{y}_{HP, i} + (1 - \lambda_i) \mu_{\text{role}} \right] \times 100$$
  where $\lambda_i = \frac{n_{HP, i} \sigma_\mu^2}{n_{HP, i} \sigma_\mu^2 + \sigma_e^2}$ is the Empirical Bayes shrinkage factor and units represent **runs per 100 balls above role baseline**.
- **Treatment of Consistently Excellent Players**:
  - Consistently elite players (like **Phil Salt**, **Abhishek Sharma**, **Suryakumar Yadav**, and **Jasprit Bumrah**) who produce massive run value across all situations are **fully rewarded** because their world-class execution carries directly into pressure moments.
  - They are **not penalized** for possessing a flat pressure-response slope ($\Delta \approx 0$).
- **Role of the Pressure Slope ($\Delta = \bar{y}_{HP} - \bar{y}_{\text{normal}}$)**:
  - The pressure-response slope is **retained exclusively as a secondary descriptive metric** in player diagnostic profiles.
  - It is **strictly barred from modifying the primary scalar score**, preventing "Pressure Spikers" with terrible baselines (like Alishan Sharafu with $\bar{y}_{\text{norm}} = -23.12$) from leapfrogging world-class performers.

---

## 2. Exact Mathematical Formulas for the Recommended Approach

### 1. Delivery-Level Net Value
For legal delivery $k$ transitioning match state from $(u, w)$ to $(u-1, w')$:
$$v_k = \text{Runs Scored}_k + \left[ R(u-1, w') - R(u, w) \right]$$
$$v_{\text{bat}, k} = v_k, \quad v_{\text{bowl}, k} = -v_k$$
where $R(u, w)$ is the 2D isotonic monotonic expected remaining runs surface.

### 2. Match-State Leverage & Pressure Domain
$$\text{Leverage } L_k = \frac{|\text{WP}(v_k = +1) - \text{WP}(v_k = -1)|}{2}$$
$$\text{Pressure Index } PI_k = \text{Percentile}(L_k \mid \text{Format})$$
$$\text{High-Pressure Domain: } \mathcal{D}_{HP} = \{k : PI_k \ge 0.800\}$$

### 3. Primary Player Rating ($R_{HP}$)
For player $i$ with $n_{HP, i}$ high-pressure balls and sample mean $\bar{y}_{HP, i} = \frac{1}{n_{HP, i}} \sum_{k \in \mathcal{D}_{HP}} v_{ik}$:
$$\hat{R}_{HP, i} = \left[ \lambda_i \bar{y}_{HP, i} + (1 - \lambda_i) \mu_{\text{role}} \right] \times 100$$
$$\lambda_i = \frac{n_{HP, i} \sigma_\mu^2}{n_{HP, i} \sigma_\mu^2 + \sigma_e^2}$$
- Batters: $\sigma_\mu^2 = 0.0349$, $\sigma_e^2 = 8.3145$, $\sigma_\mu = 18.68$ runs/100b.
- Bowlers: $\sigma_\mu^2 = 0.0223$, $\sigma_e^2 = 8.2588$, $\sigma_\mu = 14.93$ runs/100b.

### 4. Uncertainty Estimation (Procedure A Bootstrap & Empirical Bayes Posterior)
- **Score Stability 90% Interval**: Computed via Match-Cluster Bootstrap holding $(\sigma_\mu^2, \sigma_e^2)$ fixed (Procedure A, Laird & Louis 1987):
  $$\left[ R_{HP, i}^{*(0.05)}, \quad R_{HP, i}^{*(0.95)} \right]$$
- **Latent Ability 90% Credible Interval**: Computed via Parametric Empirical Bayes Posterior:
  $$\hat{R}_{HP, i} \pm 1.645 \cdot \text{SE}_{\text{post}, i}, \quad \text{where } \text{SE}_{\text{post}, i} = 100 \times \sqrt{(1 - \lambda_i) \sigma_\mu^2}$$

### 5. Secondary Descriptive Metrics (Reported in Player Profiles)
1. **Knockout Deliveries**: $n_{KO, i}$
2. **Shrunken Knockout Rating**: $\hat{R}_{KO, i} = [\lambda_{KO, i} \bar{y}_{KO, i} + (1 - \lambda_{KO, i}) \hat{R}_{HP, i}]$
3. **Pressure Sensitivity Slope**: $\text{Slope}_i = (\bar{y}_{HP, i} - \bar{y}_{\text{normal}, i}) \times 100$

---

## 3. Concise Decision Table for Human Review & Sign-Off

| Decision Area | Evaluated Alternatives | Recommended Option | Supporting Evidence | Remaining Risk & Practical Mitigation |
|---|---|---|---|---|
| **Decision 1: Knockout Reward** | Option 1A (Separate Dimension)<br>Option 1B (Weighted Blend)<br>Option 1C (Hierarchical Model) | **Option 1A: Separate Knockout Dimension** | Only 25 KO matches (3.05% of data). Over 60% of batters and 75% of bowlers have zero KO balls. Option 1B double-counts leverage and causes severe rank instability ($w_K \ge 0.10$ collapses Abhishek Sharma from #3 to #18). | *Risk*: Media evaluators expect a "playoff hero" bonus.<br>*Mitigation*: Publish a dedicated "Knockout Clutch Leaderboard" side-by-side with the primary ranking. |
| **Decision 2: Consistency Reward** | Option 2A (Absolute HP Value)<br>Option 2B (Blended Normal + HP)<br>Option 2C (Slope Interaction) | **Option 2A: High-Pressure Absolute Value ($R_{HP}$)** | Slope models reward players with terrible baselines (Alishan Sharafu slope $+55$) while penalizing elite anchors (Phil Salt slope $-0.54$, Abhishek Sharma slope $+2.39$). Option 2A measures true output when pressure is highest. | *Risk*: High baseline players dominate both boards.<br>*Mitigation*: This is physically correct; world-class players deliver real runs. Report slope $\Delta$ as descriptive metric. |
| **Eligibility Framework** | 50b/5m Floor vs 100b/10m Strict Threshold | **Two-Tier Dual Framework** | 50 balls allows breakout stars onto shortlist (Vaibhav Sooryavanshi, Mayank Yadav), but rank intervals span 1–50. 100 balls guarantees narrow rank intervals. | *Risk*: Evaluators confuse 50-ball contenders with proven stars.<br>*Mitigation*: Formally tag players into "Confirmed Core" ($n \ge 100$) vs "Exploratory Shortlist" ($50 \le n < 100$). |

---

## 4. Strict Stop Condition Sign-Off

In compliance with instructions:
- No final player rankings have been generated or modified.
- No production model parameters or baseline CSVs have been altered.
- All sensitivity data are saved to `KNOCKOUT_WEIGHT_SENSITIVITY.csv` and `PLAYER_CONSISTENCY_PRESSURE_DIAGNOSTICS.csv`.

**Awaiting your personal review and explicit methodology approval.**

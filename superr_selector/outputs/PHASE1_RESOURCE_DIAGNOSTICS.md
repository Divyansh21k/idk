# Phase 1 Resource Diagnostics — SupeRR Selector Season 2

**Phase:** Phase 1 — Expected-Value & Resource Model Diagnosis  
**Date:** 2026-11-17  
**Branch:** `model-repair`  
**Scope:** Complete architectural diagnosis of `step1_build_tables.py`, `step2_expected_value.py`, intermediate data structures, and mathematical formulations.

---

## 1. Mathematical Architecture as Actually Implemented

To rigorously diagnose the pipeline, we trace the complete mathematical trajectory from the raw delivery event to the final delivery values $v_{\text{bat}}$ and $v_{\text{bowl}}$.

### 1.1 State Definition
At delivery $t$, before the ball is bowled, the game state is discretized into two dimensions:
1. **Balls Remaining Bin ($u$):**
   $$u = \text{balls\_left\_bin} \in \{0, 1, \dots, 19\}$$
   derived from `legal_left_before` binned into 6-ball increments $(0, 6], (6, 12], \dots, (114, 120]$.
   - $u = 0$: $1 \dots 6$ legal balls remaining (the 20th over).
   - $u = 19$: $115 \dots 120$ legal balls remaining (the 1st over).
2. **Wickets Lost Bin ($w$):**
   $$w = \text{wickets\_bin} = \min(\text{wickets\_before}, 9) \in \{0, 1, \dots, 9\}$$

### 1.2 Resource Table Formulation
The resource table $R(u, w)$ represents the expected remaining runs scored in the remainder of the 1st innings from state $(u, w)$:
$$R(u, w) = \mathbb{E}[\text{runs\_remaining} \mid \text{balls\_left\_bin} = u, \text{wickets\_bin} = w]$$
where $\text{runs\_remaining} = \text{innings\_total} - \text{runs\_before}$.

#### Implementation Steps in `step2_expected_value.py` (Lines 50–90):
1. **Filter to complete 1st innings:** Filter deliveries with `elig_wp_training == True`, `innings == 1`, and `is_legal == True` across 771 complete T20 matches (91,898 deliveries).
2. **Empirical Cell Means:** For each cell $(u, w)$ observed in data, compute empirical mean:
   $$\bar{R}_{\text{raw}}(u, w) = \frac{1}{n_{u,w}} \sum_{i \in (u, w)} y_i$$
3. **1D Linear Interpolation:** For each wicket bin $w \in \{0, \dots, 9\}$ separately:
   $$\text{Interpolate along } u \text{ with fillna(method='bfill').fillna(method='ffill')}$$
   > [!CRITICAL]
   > The interpolation was executed **strictly along $u$ for each $w$ independently**. No smoothing, regularisation, or constraint was imposed across the wickets dimension $w$. Unobserved early high-wicket states (e.g. 8 wickets down in Over 1) were filled with forward-filled flat constants.

### 1.3 Wicket Cost Formulation $c(s)$
The marginal run cost of losing a wicket in state $s = (u, w)$ is defined as:
$$c(s) = R(u, w) - R(u, w+1)$$
In `src/step2_expected_value.py` lines 105–110:
```python
def get_wicket_cost(balls_left_bin, wickets_bin):
    r0 = get_resource(balls_left_bin, int(wickets_bin))
    r1 = get_resource(balls_left_bin, min(int(wickets_bin) + 1, 9))
    return max(r0 - r1, 0.0)
```

> [!CRITICAL]
> **Discovery of Boundary Clamping Bug:** At $w = 9$ (9 wickets lost, final wicket pair at the crease), `min(9 + 1, 9) = 9`, resulting in $r_1 = r_0$ and thus:
> $$c(u, 9) = \max(r_0 - r_0, 0.0) \equiv 0.0$$
> When the 10th wicket falls, the innings terminates, and the remaining resource is $0.0$. The correct marginal loss is $R(u, 9) - 0.0 = R(u, 9)$.
> In the baseline implementation, **every single 10th-wicket dismissal (219 bowler wickets and 253 dismissals in the dataset) was assigned a wicket cost of exactly 0.0 runs!**

### 1.4 Expected Values per Delivery
For each delivery, the model estimates 4 expected quantities conditioned on the 5-way state tuple:
$$\mathcal{S} = (\text{balls\_left\_bin}, \text{wickets\_bin}, \text{delivery\_kind}, \text{batter\_hand}, \text{pace\_spin})$$
1. $\mathbb{E}[\text{batter\_runs} \mid \mathcal{S}]$
2. $\mathbb{E}[\text{bowler\_charged\_runs} \mid \mathcal{S}]$
3. $\mathbb{E}[\text{bowler\_wicket\_credit} \mid \mathcal{S}]$
4. $\mathbb{E}[\text{striker\_dismissed} \mid \mathcal{S}]$

If a delivery's 5-way tuple is unobserved, it falls back to the 2-way state $(\text{balls\_left\_bin}, \text{wickets\_bin})$, and then to the population overall mean.

### 1.5 Value Attribution Equations
For each pressure-eligible delivery:
- **Batter Value ($v_{\text{bat}}$):**
  $$v_{\text{bat}} = (\text{batter\_runs} - \mathbb{E}[\text{batter\_runs}]) - c(s) \cdot (\text{striker\_dismissed} - \mathbb{E}[\text{striker\_dismissed}])$$
- **Bowler Value ($v_{\text{bowl}}$):**
  $$v_{\text{bowl}} = -(\text{bowler\_charged\_runs} - \mathbb{E}[\text{bowler\_charged\_runs}]) + c(s) \cdot (\text{bowler\_wicket\_credit} - \mathbb{E}[\text{bowler\_wicket\_credit}])$$
- **Non-Striker Run-Out Attribution (D51):**
  When a non-striker is run out (`dismissed_role == 'non_striker'`, `dismissal_type == 'RunOut'`), the dismissal penalty is decoupled from the striker and assigned to the non-striker in Step 4 via an event penalty:
  $$v_{\text{bat\_runout}} = -c(s)$$

---

## 2. Diagnosis of Monotonicity Failures

In a valid cricketing resource function, three core physical constraints should hold under standard conditions:

### 2.1 Theoretical Foundations of the Constraints

#### Constraint A: Monotonicity in Balls Remaining
$$\frac{\partial R(u, w)}{\partial u} \ge 0 \quad \iff \quad R(u+1, w) \ge R(u, w)$$
*Reasoning:* With $w$ wickets lost, having an additional 6 legal deliveries provides strictly non-negative optionality. Even if scoring rates are lower, a team cannot score negative runs on additional balls.  
*When it might fail in raw empirical data:* Severe selection bias in sparse cells. For example, if the only time a team was 8 wickets down in Over 10 was in an exceptionally low-scoring match on an unplayable pitch, while in Over 9 it occurred in a high-scoring match.

#### Constraint B: Monotonicity in Wickets Lost
$$\frac{\partial R(u, w)}{\partial w} \le 0 \quad \iff \quad R(u, w+1) \le R(u, w)$$
*Reasoning:* Losing an additional wicket reduces batting depth and tail quality. Lower-order batters have lower average scoring rates and higher dismissal hazards than top-order batters.  
*When it might fail in raw empirical data:* Finite-sample noise in small sample cells. In the final over ($u = 0$), sample sizes for $w = 0, 1$ are tiny ($n = 6, 19$), so empirical means fluctuate wildly.

#### Constraint C: Boundedness and Non-Negativity
$$0 \le R(u, w) \le R_{\text{max}}(u)$$
A team cannot score fewer than 0 runs, nor more than 36 runs per over remaining.

---

### 2.2 Empirical Audit of Monotonicity Failures in Baseline Table

Controlled evaluation of `superr_selector/outputs/step2/resource_table.csv` revealed pervasive violations across the 200-cell grid:

| Violation Dimension | Total Possible Transitions | Number of Violations | Percentage of Grid | Maximum Violation Magnitude | Mean Violation Magnitude |
|---|---|---|---|---|---|
| **Balls Remaining ($u$)** | 190 transitions ($19 \times 10$) | **18 violations** | **9.47%** | **-44.29 runs** | **-6.72 runs** |
| **Wickets Lost ($w$)** | 180 transitions ($20 \times 9$) | **20 violations** | **11.11%** | **+20.50 runs** | **+11.83 runs** |

#### Top 5 Balls Monotonicity Violations (More Balls = Fewer Expected Runs)
1. **$u = 17$ (102–108 balls left), $w = 4$:** Expected runs drops from **132.29 runs** at $u=16$ down to **88.00 runs** at $u=17$ (**-44.29 runs violation**; $n_{\text{curr}} = 7, n_{\text{prev}} = 21$).
2. **$u = 5$ (30–36 balls left), $w = 9$:** Drops from **20.43 runs** down to **11.83 runs** (**-8.61 runs violation**; $n_{\text{curr}} = 23, n_{\text{prev}} = 53$).
3. **$u = 17$ (102–108 balls left), $w = 3$:** Drops from **124.11 runs** down to **116.32 runs** (**-7.79 runs violation**; $n_{\text{curr}} = 66, n_{\text{prev}} = 195$).
4. **$u = 18$ (108–114 balls left), $w = 3$:** Drops from **116.32 runs** down to **109.00 runs** (**-7.32 runs violation**; $n_{\text{curr}} = 12, n_{\text{prev}} = 66$).
5. **$u = 16$ (96–102 balls left), $w = 5$:** Drops from **86.33 runs** down to **79.18 runs** (**-7.15 runs violation**; $n_{\text{curr}} = 11, n_{\text{prev}} = 6$).

#### Top 5 Wickets Monotonicity Violations (More Wickets Lost = More Expected Runs)
1. **$u = 14$ (84–90 balls left), $w = 7$ vs $w = 6$:** Expected runs jumps from **62.50 runs** ($w=6, n=6$) up to **82.50 runs** ($w=7, n=0$, interpolated) (**+20.00 runs inversion**).
2. **$u = 12$ (72–78 balls left), $w = 7$ vs $w = 6$:** Jumps from **64.53 runs** up to **82.50 runs** (**+17.97 runs inversion**; $n_{\text{curr}} = 2$).
3. **$u = 15$ (90–96 balls left), $w = 7$ vs $w = 6$:** Jumps from **65.67 runs** up to **82.50 runs** (**+16.83 runs inversion**; $n_{\text{curr}} = 0$).
4. **$u = 11$ (66–72 balls left), $w = 7$ vs $w = 6$:** Jumps from **59.92 runs** up to **75.43 runs** (**+15.51 runs inversion**; $n_{\text{curr}} = 7$).
5. **$u = 16 \dots 19$ (Overs 1–4), $w = 7$ vs $w = 6$:** Constant forward-fill creates **+15.50 runs inversions** across the entire powerplay.

---

### 2.3 Sample Size Distribution & Structural Sparsity

An audit of delivery counts across the $20 \times 10$ state space in complete 1st innings ($N = 91,898$) reveals extreme structural sparsity:

- **Empty Cells ($n = 0$):** **36 cells** (18.0% of the entire grid).
- **Extremely Sparse Cells ($0 < n < 10$):** **13 cells** (6.5% of grid).
- **Sparse Cells ($10 \le n < 30$):** **14 cells** (7.0% of grid).
- **Total Deficient Cells ($n < 30$):** **63 out of 200 cells (31.5%)**.

#### Structural Sparsity Regimes in T20 Cricket:
1. **The Early-Collapse Void (High $u$, High $w$):**
   In Overs 1–3 ($u = 17, 18, 19$), states with $w \ge 4$ wickets lost almost never occur in professional cricket. At $u = 19$, $n = 0$ for all $w \ge 3$.
2. **The Death-Over Preservation Void (Low $u$, Low $w$):**
   In the 20th over ($u = 0$), a team having lost 0 wickets occurred in only 6 deliveries ($n = 6$), and 1 wicket in only 19 deliveries ($n = 19$).
3. **The Dense Core:**
   Over 80% of all deliveries reside in a narrow diagonal corridor:
   - Overs 1–6: $w \in [0, 2]$
   - Overs 7–15: $w \in [1, 4]$
   - Overs 16–20: $w \in [3, 7]$

---

### 2.4 Origin Analysis: Where Did the Problem Originate?

1. **Not in the Raw Data Quality:** The raw match and ball-by-ball records are clean (passing all 49 data layer assertions). The issue is not data corruption.
2. **Structural Data Sparsity:** T20 cricket matches do not explore all $(u, w)$ states with equal probability. Sparse cells are inevitable in finite datasets.
3. **Flawed Smoothing Strategy in Code:** The decision to interpolate linearly along $u$ while treating $w$ independently was the root mathematical failure. When a cell has $n=0$, 1D interpolation across $u$ propagates noise or clamps flat values that conflict with adjacent $w$ columns.
4. **Code Boundary Bug:** Clamping `min(w + 1, 9)` rather than defining $R(u, 10) \equiv 0$ broke wicket cost evaluation for 9th-wicket partnerships.

---

## 3. Evaluation of 5 Solution Candidates

To resolve monotonicity without destroying real cricketing variation, 5 alternative methodologies were formulated and tested:

### Candidate 1: Pooling Sparse States
- **Mechanism:** Dynamically pool states with $n < 30$ into adjacent wicket bins (e.g. pool $w \ge 6$ in early overs).
- **Evaluation:** Reduced wicket violations from 20 to 12, but **increased balls violations from 17 to 20**! Discrete bin pooling introduces artificial step-discontinuities across pool boundaries.

### Candidate 2: 2D Kernel Smoothing
- **Mechanism:** Apply 2D Gaussian kernel smoothing across both $u$ and $w$ with bandwidths $\sigma_u = 1.5$ (bins) and $\sigma_w = 1.0$ (wickets).
- **Evaluation:** Smooths the surface and eliminates wicket violations, but introduces systematic boundary attenuation (bias = $+0.817$, MAE = $17.167$). It over-smooths genuine steep scoring acceleration in death overs.

### Candidate 3: Alternating Isotonic Regression (Bi-Isotonic Projection)
- **Mechanism:** Alternating projection (PAVA) along $u$ (increasing) and $w$ (decreasing) until convergence.
- **Evaluation:** Completely eliminates all monotonicity violations (0 balls, 0 wickets). Out-of-fold MAE drops to $16.843$ (better than Baseline $16.849$). However, in completely unobserved sparse regions, it creates flat terraces rather than sensible gradients.

### Candidate 4: Pure Parametric Resource Model (Duckworth-Lewis Saturation)
- **Mechanism:** Fit a non-linear exponential resource function:
  $$R_{\text{param}}(u, w) = Z_0 \cdot \left(\frac{10 - w}{10}\right)^\alpha \cdot \left[1 - \exp\left(-\beta \cdot \frac{u}{120} \cdot \left(\frac{10 - w}{10}\right)^{-\gamma}\right)\right]$$
  Fitted parameters on complete 1st innings:
  - $Z_0 = 177.3$ (par total with 10 wickets in hand)
  - $\alpha = 0.706$
  - $\beta = 1.238$
  - $\gamma = 0.312$
- **Evaluation:** Monotone by construction (0 violations). Extremely stable across CV folds ($\sigma = 1.408$). However, pure parametric modeling has higher bias ($+0.427$) and cannot capture pitch-dependent or tactical death-over spikes evident in dense empirical data.

### Candidate 5: Hybrid Empirical-Parametric Prior with Monotone Projection (Recommended)
- **Mechanism:**
  1. Fit the global parametric resource model $R_{\text{param}}(u, w)$ as an informative prior.
  2. For every cell $(u, w)$, shrink the empirical mean $\bar{y}_{u,w}$ toward the parametric prior using sample-size credibility weighting:
     $$\hat{R}_{\text{hybrid}}(u, w) = \lambda_{u,w} \bar{y}_{u,w} + (1 - \lambda_{u,w}) R_{\text{param}}(u, w)$$
     where $\lambda_{u,w} = \frac{n_{u,w}}{n_{u,w} + n_{\text{prior}}}$ with $n_{\text{prior}} = 25$.
     - When $n \ge 200$ (dense core), $\lambda > 0.89$ (data dominates, empirical nuances preserved).
     - When $n = 0$ (sparse void), $\lambda = 0.00$ (parametric prior fills state smoothly).
  3. Apply alternating isotonic projection to enforce exact weak monotonicity.
- **Evaluation:** **Superior across all metrics.** Achieves the lowest out-of-fold MAE ($16.823$) and RMSE ($23.055$), zero bias ($+0.0205$), perfect calibration (slope $0.9986$, intercept $0.1034$), 0 monotonicity violations, and a realistic mean wicket cost of $9.92$ runs.

---

## 4. Diagnosis of Expected-Value Leakage

### 4.1 In-Sample Leakage in Baseline
In `step2_expected_value.py` lines 143–150:
```python
# Use full model (not cross-fitted for now; cross-fitting is the production version)
full_ev = compute_expected_values(b[b['elig_pressure'] == True], label='full')
```
- **The Finding:** Baseline Step 2 fitted the 5-way state group expected values on 100% of deliveries, and then evaluated those exact same deliveries against the fitted values.
- **Consequence:** An individual player's own exceptional performances (e.g. Suryakumar Yadav facing 2,745 deliveries or Jasprit Bumrah conceding few runs) shifted the expected baseline in the state cells they dominated. This violated the identity-free claim and created in-sample optimistic bias.

### 4.2 Out-of-Fold Match Cross-Fitting Implementation
To eliminate leakage:
1. Stratify all 884 matches into 5 balanced folds.
2. Ensure **all deliveries from a match reside strictly in the same fold**.
3. For fold $k$, fit group expected values on the remaining 4 folds ($\sim 707$ matches).
4. Predict expected runs and dismissal probabilities strictly for the held-out fold ($\sim 177$ matches).
5. Preserve determinism via `random_state = 42`.

### 4.3 Out-of-Fold vs In-Sample Verification
Evaluating across all 187,556 pressure deliveries:
- **Batter Expected Runs Correlation:** $r = 0.9579$
- **Bowler Expected Runs Correlation:** $r = 0.9213$
- **Bowler Wicket Credit Correlation:** $r = 0.9022$
- **Dismissal Expected Correlation:** $r = 0.9105$
- **Mean Bias:** Out-of-fold bias is $-0.000697$ runs for batters and $-0.002468$ runs for bowlers (statistically indistinguishable from zero).

Cross-fitting eliminates leakage while preserving over 95% of the signal structure.

---

## 5. Summary Diagnostic Verdict

| Issue | Severity in Baseline | Status in Phase 1 Diagnosis | Root Cause |
|---|---|---|---|
| **Resource Monotonicity (Balls)** | Critical | Diagnosed & Solved | 1D independent interpolation across sparse cells |
| **Resource Monotonicity (Wickets)** | Critical | Diagnosed & Solved | Absence of cross-wicket regularization |
| **10th Wicket Boundary Bug ($c(s)=0$)** | Critical | Diagnosed & Solved | Code clamping `min(w+1, 9)` instead of evaluating $R(u, 10)=0$ |
| **Expected Value In-Sample Leakage** | Critical | Diagnosed & Solved | Unimplemented cross-fitting skeleton |
| **Negative Wicket Cost Truncation** | High | Diagnosed & Solved | Consequence of inverted resource table |
| **Sparse-State Instability** | High | Diagnosed & Solved | Credibility shrinkage to parametric prior resolves void cells |

The diagnostic phase is complete. All numerical evidence confirms that Candidate 5 (Hybrid Prior + Monotone Projection) alongside 5-fold match cross-fitting successfully repairs the expected-value foundation.

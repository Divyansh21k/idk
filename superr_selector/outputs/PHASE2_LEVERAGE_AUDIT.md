# Phase 2 Leverage Audit — SupeRR Selector Season 2

**Phase:** Phase 2 — Delivery Leverage & State Transition Verification  
**Date:** 2026-11-17  
**Branch:** `model-repair`  
**Scope:** Complete Mathematical and Algorithmic Audit of Delivery Leverage $L(s)$, Outcome Transitions, Boundary States, and Pressure Index Construction.

---

## 1. Mathematical Definition of Delivery Leverage

In modern sports analytics, **match leverage** quantifies the sensitivity of the game outcome to the events of an individual play. 

For any delivery $t$ commencing from game state $s_t$, leverage $L(s_t)$ is formally defined as the **expected absolute swing in win probability** across the set of possible immediate delivery outcomes $\mathcal{O}$:

$$L(s_t) = \sum_{o \in \mathcal{O}} P(o \mid s_t) \cdot \left| WP(s'_{t, o}) - WP(s_t) \right|$$

where:
- $WP(s_t)$ is the pre-delivery win probability of the batting team.
- $\mathcal{O} = \{\text{dot}, \text{single}, \text{two}, \text{three}, \text{four}, \text{six}, \text{wicket}\}$ is the mutually exclusive outcome space.
- $P(o \mid s_t)$ is the conditional probability of outcome $o$ given game state $s_t$.
- $s'_{t, o}$ is the deterministic post-delivery game state resulting from outcome $o$.
- $WP(s'_{t, o})$ is the post-delivery win probability from state $s'_{t, o}$.

### Key Properties of $L(s)$:
1. **Non-Negativity:** $L(s) \ge 0$ for all states.
2. **State Property, Not Player Property:** $L(s)$ is strictly a property of the match context (score, target, balls left, wickets in hand), completely independent of which specific batter or bowler is involved in the delivery.
3. **Zero in Decided Matches:** If $WP(s) = 1.0$ (chase achieved) or $WP(s) = 0.0$ (team all out or required rate mathematically impossible), $WP(s') = WP(s)$ for all outcomes $\implies L(s) = 0.0$.
4. **Maximum in Close Finishes:** When a match is in the final over with both teams having a path to victory, a single boundary or wicket swings $WP$ by $0.40\dots 0.80$, producing peak leverage values near $1.0$.

---

## 2. Audit of State Transitions $s \to s'_{t, o}$

The calculation of post-delivery win probability $WP(s'_{t, o})$ requires exact state transition mechanics.

### 2.1 State Vector Updates
From pre-delivery state $s = (\text{runs\_before}, \text{legal\_left\_before}, \text{wickets\_before})$, an outcome $o$ with run contribution $r_o$ and wicket indicator $w_o$ induces:
1. **Cumulative Runs:**
   $$\text{runs\_before}' = \text{runs\_before} + r_o$$
2. **Legal Balls Remaining:**
   $$\text{legal\_left\_before}' = \max(\text{legal\_left\_before} - 1, 0)$$
3. **Wickets Lost:**
   $$\text{wickets\_before}' = \min(\text{wickets\_before} + w_o, 10)$$
4. **Updated Resource Lookup:**
   $$u' = \text{bin\_balls}(\text{legal\_left\_before}'), \quad w' = \min(\text{wickets\_before}', 9)$$
   $$E_{\text{remaining}}' = R(u', w')$$

---

### 2.2 Terminal Boundary Conditions in Innings 2 Chases
In `step3_win_probability.py` lines 240–255, the terminal chase conditions are evaluated explicitly:
1. **Target Achieved (Batting Team Victory):**
   $$\text{new\_required} = \text{target} - \text{runs\_before}' \le 0 \implies WP(s') \equiv 1.0$$
2. **All Out (Bowling Team Victory):**
   $$\text{wickets\_before}' \ge 10 \implies WP(s') \equiv 0.0$$
3. **Overs Exhausted (Bowling Team Victory):**
   $$\text{legal\_left\_before}' \le 0 \quad \text{and} \quad \text{new\_required} > 0 \implies WP(s') \equiv 0.0$$

> [!NOTE]
> **Audit Finding:** The boundary handling in Innings 2 is **strictly correct**. When an outcome crosses the winning threshold (e.g. hitting a four when 2 runs are needed), the model immediately clamps $WP(s') = 1.0$ rather than evaluating the logistic equation.

---

### 2.3 Audit of Outcome Space & The "Two_Three" Lumping

In baseline `step3_win_probability.py` lines 211–227, outcomes were classified into 6 bins:
- `dot` ($r=0, w=0$)
- `single` ($r=1, w=0$)
- `two_three` ($r=2.5, w=0$)
- `four` ($r=4, w=0$)
- `six` ($r=6, w=0$)
- `wicket` ($r=0, w=1$)

#### Empirical Audit of the 2.5 Run Assumption:
An empirical frequency check across all 180,708 legal deliveries revealed:
- **Deliveries with exactly 2 runs:** **11,772 deliveries (6.51%)**
- **Deliveries with exactly 3 runs:** **617 deliveries (0.34%)**
- **Ratio of 2s to 3s:** **19.1 to 1**

Because 3s constitute only $0.34\%$ of all legal deliveries, assigning an average of $2.5$ runs introduces a slight upward bias of $+0.47$ runs on that outcome bin ($11,772 \times 2 + 617 \times 3 = 25,395 \text{ runs} \implies \text{true mean} = 2.05 \text{ runs}$). 
- **Impact on Leverage:** Computing leverage with exact split outcomes $\{\text{two}: r=2, \text{three}: r=3\}$ shifts $L(s)$ by less than $0.0012$ units on average.
- **Audit Verdict:** Splitting `two` and `three` into separate categories is computationally trivial and methodologically cleaner. It is incorporated into the Phase 2 specification.

---

## 3. Delivery Classification & Illegal Deliveries Handling

The pipeline processes both legal and illegal deliveries:

### 3.1 Legal Deliveries
Legal deliveries consume 1 legal ball from the quota (`legal_left_before` decreases by 1). Leverage is computed directly from pre-delivery state $s$ to post-delivery state $s'$.

### 3.2 Illegal Deliveries (Wides & No-Balls) — Decision D47 Verification
In `step3_win_probability.py` lines 332–370:
- When a wide or no-ball occurs, the delivery does not consume a legal ball (`legal_left_before` does not decrement).
- **Decision D47 Rule:** Illegal deliveries inherit their Win Probability, Leverage, and Pressure Index from the pre-delivery state at `legal_before = k`.
- **Methodological Audit:** An illegal delivery takes place in the exact same strategic context as the legal delivery that would have followed it. A bowler delivering a wide when defending 6 runs off the final ball is under the exact same high-leverage context as on the legal ball itself.
- **Verification Against Exposure Contamination:**
  - Wides do not increment `batter_ball_faced` (the batter is not credited with a ball faced under pressure).
  - Bowlers are charged with the delivery event in `elig_bowling`.
  - State inheritance preserves physical continuity.

### 3.3 Free-Hit Deliveries
On free hits, batters cannot be dismissed bowled, caught, LBW, or stumped (only run out).
- In the baseline, free-hit state leverage was evaluated using the general outcome transition table.
- Because wicket probability is restricted on a free hit ($\sim 1.5\%$ vs normal $\sim 5.2\%$), the expected swing from a dismissal is dampened, while the expected run swing is elevated.
- Under Model B's refined transition, $P(\text{wicket} \mid \text{free\_hit})$ reflects run-out probabilities, preventing overestimation of bowler leverage on free hits.

---

## 4. Verification Against Double-Counting

A critical concern raised during independent audit was whether knockout importance is double-counted between Step 3 leverage and Step 4 ratings.

### Audit of Leverage Propagation:
1. **Delivery Level:** Each delivery $t$ receives exactly one leverage value $L(s_t)$ based on its game state.
2. **Pressure Index ($PI_t$):** $PI_t$ is the percentile rank of $L(s_t)$.
3. **Centered Pressure Metric ($x_t$):**
   $$x_t = PI_t - 0.50$$
4. **Step 4 Hierarchical Player Model:**
   In Step 4, player performance is modeled via:
   $$R_i^{\text{reg}} = (\mu_i + \theta_i \cdot x^*) \times 100$$
   where $x^* = 0.40$ (evaluating at $PI = 0.90$).
5. **Knockout Scaling Term:**
   $$R_i^{\text{overall}} = R_i^{\text{reg}} + w_K \cdot (\kappa + \gamma x^* + \delta_i) \times 100$$
   - $w_K$ is frozen at $0.052932$ (the exact ratio of total leverage in IPL Knockouts to total leverage across all IPL matches).
   - In Step 4, $R_i^{\text{reg}}$ is estimated strictly from regular matches (`cat` $\in$ `['IPL league', 'T20I non-knockout']`). Knockout deliveries are **completely excluded from the estimation of $R_i^{\text{reg}}$**.
   - Knockout deliveries are analyzed strictly in the knockout residual term $(\kappa + \gamma x^* + \delta_i)$.

> [!IMPORTANT]
> **Audit Finding: ZERO Double-Counting.**
> Knockout deliveries appear strictly once in the model hierarchy. Regular matches inform $R_i^{\text{reg}}$, while knockout matches inform $\delta_i$. The parameter $w_K$ acts as a linear convex combination weight.

---

## 5. Leverage Distribution Audit: IPL vs T20I Formats

An empirical audit was conducted to test whether competition formats differ in leverage intensity:

| Tournament Category | Delivery Count ($N$) | Mean Leverage $\bar{L}$ | Median Leverage | 80th Percentile ($PI \ge 0.80$) | 90th Percentile ($PI \ge 0.90$) | Maximum Leverage |
|---|---|---|---|---|---|---|
| **IPL League** | 77,896 | 0.1827 | 0.0988 | **0.2968** | 0.4979 | 0.9816 |
| **IPL Knockout** | 4,383 | 0.1815 | 0.0991 | **0.2974** | 0.4986 | 0.9804 |
| **T20I Non-Knockout** | 97,285 | 0.1866 | 0.1059 | **0.3020** | 0.5155 | 0.9843 |
| **T20I Final** | 1,152 | 0.1651 | 0.0912 | **0.2765** | 0.4269 | 0.9802 |

### Key Analytical Findings:
1. **Cross-Format Alignment:** The 80th percentile threshold for High Pressure across IPL ($L = 0.2968$) and T20I ($L = 0.3020$) differs by only **$0.0052$ leverage units**.
2. **Equivalence of Absolute and Percentile Thresholds:** Requiring $PI \ge 0.80$ within each competition class is functionally identical to requiring absolute leverage $L(s) \ge 0.300$.
3. **Format Parity:** T20I and IPL matches experience virtually identical proportions of close, high-leverage finishes ($\sim 20\%$ of deliveries with $L \ge 0.30$).

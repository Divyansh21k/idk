# Final Knockout Arithmetic Correction: Exact Code Trace & Score Withdrawal

**Project:** SupeRR Selector Season 2  
**Document:** `FINAL_KNOCKOUT_ARITHMETIC_CORRECTION.md`  
**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Status:** Audit of Mathematical Discrepancy & Final Score Withdrawal  
**Companion File:** [`KNOCKOUT_PLAYER_RECALCULATION.csv`](file:///Users/divyanshkharnal/Downloads/idk/superr_selector/outputs/KNOCKOUT_PLAYER_RECALCULATION.csv)

---

## Executive Summary

This document traces the exact arithmetic calculations that generated the sensitivity ratings for **Vaibhav Sooryavanshi** ($+92.63$) and **Abhishek Sharma** ($-52.28$) in `KNOCKOUT_WEIGHT_SENSITIVITY.csv`.

It explains why substituting the previously displayed numbers ($R_{KO} = 144.23$ and $R_{KO} = -305.27$) into the shrinkage formula failed to reproduce the reported results ($92.63$ and $-52.28$), provides the exact underlying code trace, and re-confirms the formal withdrawal of the knockout score.

---

## 1. Trace of the Arithmetic Discrepancy

### 1.1 The Mathematical Substitution Failure
The previous report presented the formula:
$$\hat{R}_{KO} = \lambda \cdot R_{KO} + (1 - \lambda) \cdot R_{HP}$$
and displayed:
- **Vaibhav Sooryavanshi**: $R_{HP} = 38.66$, $R_{KO} = 144.23$, $\lambda = 0.5392$, Reported Result $= \mathbf{92.63}$.
  - Direct substitution: $0.5392 \times 144.23 + (1 - 0.5392) \times 38.66 = 77.77 + 17.81 = \mathbf{95.58} \neq \mathbf{92.63}$.
- **Abhishek Sharma**: $R_{HP} = 29.38$, $R_{KO} = -305.27$, $\lambda = 0.2541$, Reported Result $= \mathbf{-52.28}$.
  - Direct substitution: $0.2541 \times (-305.27) + (1 - 0.2541) \times 29.38 = -77.57 + 21.91 = \mathbf{-55.65} \neq \mathbf{-52.28}$.

---

### 1.2 Root Cause of the Discrepancy: Delivery Rows vs Legal Balls Faced
In cricket analysis, a delivery row in `ball_by_ball.csv` can be a wide or penalty ball that does not increment `batter_ball_faced`.
When the sensitivity script computed `KNOCKOUT_WEIGHT_SENSITIVITY.csv`, it grouped `v_bat` by `striker_id` across **all delivery rows** without filtering for `batter_ball_faced == True`:

| Player | Total Delivery Rows ($n_{\text{rows}}$) | Legal Balls Faced ($n_{\text{balls}}$) | Sum of $v_{\text{bat}}$ (runs) | Rate per 100 Rows (Code Input) | Rate per 100 Balls (Displayed in Text) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Vaibhav Sooryavanshi** | **79** | 76 *(3 wides)* | $+109.612002$ | **$+138.7494$** | **$+144.2263$** |
| **Abhishek Sharma** | **23** | 22 *(1 wide)* | $-67.159237$ | **$-291.9967$** | **$-305.2693$** |

### The Exact Code Execution Trace:
1. **Vaibhav Sooryavanshi**:
   - The script used $n = 79$ and $\bar{v} \times 100 = \frac{109.612002}{79} \times 100 = \mathbf{+138.749369}$.
   - Shrinkage factor:
     $$\lambda = \frac{79 \times 0.1168}{79 \times 0.1168 + 7.8857} = \frac{9.2272}{17.1129} = \mathbf{0.53919558}$$
   - Execution:
     $$\hat{R}_{KO} = 0.53919558 \times (+138.749369) + (1 - 0.53919558) \times 38.660115$$
     $$\hat{R}_{KO} = 74.81315 + 17.81464 = \mathbf{+92.627798}\text{ runs/100b}$$
   - The previous text displayed $+144.23$ (runs per 100 balls faced) but evaluated the formula using $+138.75$ (runs per 100 delivery rows).

2. **Abhishek Sharma**:
   - The script used $n = 23$ and $\bar{v} \times 100 = \frac{-67.159237}{23} \times 100 = \mathbf{-291.996685}$.
   - Shrinkage factor:
     $$\lambda = \frac{23 \times 0.1168}{23 \times 0.1168 + 7.8857} = \frac{2.6864}{10.5721} = \mathbf{0.25410278}$$
   - Execution:
     $$\hat{R}_{KO} = 0.25410278 \times (-291.996685) + (1 - 0.25410278) \times 29.381468$$
     $$\hat{R}_{KO} = -74.19717 + 21.91555 = \mathbf{-52.281614}\text{ runs/100b}$$
   - The previous text displayed $-305.27$ (runs per 100 balls faced) but evaluated the formula using $-292.00$ (runs per 100 delivery rows).

---

## 2. Definitive Summary of Status

1. **Arithmetic Solved:** The reported results in `KNOCKOUT_WEIGHT_SENSITIVITY.csv` ($+92.63$ and $-52.28$) were the exact mathematical output of the script when evaluated against delivery rows ($n=79, \bar{v}=1.3875$ and $n=23, \bar{v}=-2.9200$).
2. **Defects in the Underlying Calculation:**
   - Evaluated raw delivery rows instead of legal balls faced.
   - Conflated all-knockout overs ($PI \in [0, 1]$) with high-pressure deliveries ($PI \ge 0.80$).
   - Omitted tactical role centering ($\mu_{\text{role}}$).
   - Vaibhav had **0 high-pressure balls in knockouts**.
   - Abhishek had **only 4 high-pressure balls in knockouts** (standard error $> 140$ runs/100b).
3. **Status of the Knockout Score:**
   The old knockout score $\hat{R}_{KO}$ is **formally withdrawn**. It is statistically indefensible and must **never be used for ranking or player selection**.

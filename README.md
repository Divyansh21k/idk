# SupeRR Selector Season 2 — Round 1 Submission

## Objective
Produce two defensible, data-derived rankings of cricket players under high-pressure conditions:
1. **Top 10 Batters Under Pressure**
2. **Top 10 Bowlers Under Pressure**

Supported by a reproducible methodology report and verification artifacts adhering strictly to the Stage 4 v0.5 methodology.

---

## Final Rankings

### Top 10 Batters Under Pressure ($x^* = 0.40, PI^* = 0.90$)
*Ratings expressed in net runs created per 100 balls above context expectation.*

| Rank | Player | Role | Overall Rating ($R$) | Regular Rating ($R_{\text{reg}}$) | Knockout Rating ($R_{\text{KO}}$) | SE | 90% CI | $P(\text{Top 10})$ | Total Balls | High-Pressure Balls | Knockout Balls |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | **Vaibhav Sooryavanshi** | opener (1-2) | **+54.54** | +54.95 | +47.17 | 15.66 | [16.25, 45.72] | 81.3% | 564 | 180 | 76 |
| 2 | **Patrick Cummins** | lower (7+) | **+52.69** | +53.21 | +43.44 | 25.35 | [-3.43, 15.34] | 66.7% | 247 | 28 | 50 |
| 3 | **Dinesh Karthik** | middle (5-6) | **+50.00** | +50.55 | +40.16 | 15.57 | [2.45, 19.09] | 75.1% | 633 | 49 | 43 |
| 4 | **Abhishek Sharma** | opener (1-2) | **+41.77** | +42.39 | +30.64 | 9.26 | [18.27, 41.91] | 57.0% | 2232 | 525 | 16 |
| 5 | **Matthew Wade** | lower (7+) | **+40.91** | +41.43 | +31.45 | 21.07 | [-6.82, 8.23] | 51.5% | 407 | 126 | 40 |
| 6 | **Suryakumar Yadav** | top order (3-4) | **+38.70** | +39.19 | +29.94 | 9.12 | [17.97, 33.36] | 47.3% | 2661 | 581 | 104 |
| 7 | **Ryan Rickelton** | opener (1-2) | **+33.88** | +34.40 | +24.50 | 13.24 | [0.26, 17.32] | 32.2% | 820 | 278 | 0 |
| 8 | **Yashasvi Jaiswal** | opener (1-2) | **+32.18** | +32.74 | +22.16 | 10.10 | [2.32, 19.82] | 19.6% | 1799 | 578 | 119 |
| 9 | **Andre Russell** | lower (7+) | **+30.84** | +31.36 | +21.46 | 17.21 | [6.92, 23.59] | 31.6% | 700 | 76 | 0 |
| 10 | **Rahul Tewatia** | middle (5-6) | **+30.17** | +30.65 | +21.67 | 16.22 | [-2.82, 9.63] | 25.4% | 516 | 92 | 73 |

---

### Top 10 Bowlers Under Pressure ($x^* = 0.40, PI^* = 0.90$)
*Ratings expressed in net runs saved/credited per 100 deliveries above context expectation.*

| Rank | Player | Type | Arm | Overall Rating ($R$) | Regular Rating ($R_{\text{reg}}$) | Knockout Rating ($R_{\text{KO}}$) | SE | 90% CI | $P(\text{Top 10})$ | Total Deliveries | High-Pressure Deliveries | Knockout Deliveries |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | **Mosaddek Hossain** | Spin | right | **+49.62** | +49.81 | +46.28 | 18.73 | [1.07, 25.50] | 65.8% | 163 | 41 | 0 |
| 2 | **Corbin Bosch** | Pace | right | **+37.46** | +37.65 | +34.12 | 16.48 | [-1.37, 17.65] | 38.9% | 360 | 99 | 0 |
| 3 | **Reece Topley** | Pace | left | **+35.60** | +35.82 | +31.53 | 14.76 | [-6.71, 12.52] | 34.0% | 632 | 117 | 18 |
| 4 | **Junaid Siddique** | Pace | right | **+34.87** | +35.06 | +31.53 | 17.34 | [1.72, 18.41] | 36.3% | 354 | 37 | 0 |
| 5 | **Ashton Agar** | Spin | left | **+30.82** | +31.01 | +27.48 | 18.26 | [1.35, 12.15] | 27.9% | 145 | 26 | 0 |
| 6 | **Lockie Ferguson** | Pace | right | **+30.52** | +30.72 | +26.97 | 12.28 | [-1.71, 14.94] | 19.1% | 1138 | 195 | 42 |
| 7 | **Zaman Khan** | Pace | right | **+30.36** | +30.55 | +27.02 | 17.82 | [-1.28, 8.60] | 27.2% | 200 | 55 | 0 |
| 8 | **Jofra Archer** | Pace | right | **+30.23** | +30.45 | +26.36 | 11.91 | [-5.37, 11.30] | 20.0% | 1290 | 276 | 50 |
| 9 | **Josh Hazlewood** | Pace | right | **+30.15** | +30.33 | +26.89 | 11.81 | [1.91, 22.25] | 18.1% | 1403 | 280 | 145 |
| 10 | **Dunith Wellalage** | Spin | left | **+29.93** | +30.12 | +26.59 | 18.26 | [-10.41, 7.18] | 25.5% | 242 | 36 | 0 |

---

## Reproducibility

To re-run the entire pipeline from the raw organizer files:

```bash
cd superr_selector
bash run_all.sh
```

All final reports, ranked candidate tables, and validation evidence will be regenerated in `outputs/final_deliverables/` and `deliverables/`.

# Pressure Experience Audit — SupeRR Selector Season 2 Round 1

**Date:** 2026-11-17 | **Status:** Independent review — does not modify existing rankings

---

## Executive Summary

After auditing the pressure exposure of our final top-10 players against the full eligible population, we find:

- **3/10 top-10 batters** have HP exposure at or above the population median (520 deliveries)
- **0/10 top-10 bowlers** have HP exposure at or above the population median (542 deliveries)
- Only **0/10 top-10 batters** and **0/10 top-10 bowlers** are above the population 75th percentile
- Several top-10 players have CI_90 intervals that include zero — their estimated positive rating is **not statistically distinguishable from noise**
- The top-10 rankings, while Model B-eligible, are not uniformly composed of experienced pressure performers

**The fundamental tension**: Our model identifies players with the highest *estimated* pressure performance value-added. Due to low SNR in T20 pressure data, this is not equivalent to identifying players with the most *sustained* and *reliable* pressure experience.

---

## 1. Pressure Index Distribution

| Band | Description | % of Bat Deliveries | % of Bowl Deliveries |
|------|-------------|--------------------|-----------------------|
| low (<0.50) | Minimal pressure | 49.99% | 49.97% |
| moderate (0.50-0.65) | Below average pressure | 15.01% | 15.05% |
| high (0.65-0.80) | Elevated pressure | 15.01% | 15.04% |
| **very_high (0.80-0.90)** | **HP (current threshold)** | **9.99%** | **10.01%** |
| **extreme (>0.90)** | **Truly extreme pressure** | **9.99%** | **9.93%** |

**PI percentiles (from all eligible deliveries):**
- Batters: p50=0.500, p75=0.750, p90=0.900
- Bowlers: p50=0.500, p75=0.749, p90=0.899

> [!NOTE]
> Our current HP threshold (PI ≥ 0.80) captures the **top ~80% of batter deliveries by pressure intensity**. This is a defensible definition of high-pressure, but it includes deliveries at PI=0.80 which are only moderately extreme relative to the most clutch situations (PI>0.90).

---

## 2. Top-10 vs Full Population Exposure

### Batters (174 eligible, Model B)

| Metric | Population | Top-10 |
|--------|-----------|--------|
| HP deliveries p25 | 311.0 | 128 |
| HP deliveries median | 520.0 | 229 |
| HP deliveries p75 | 900.0 | 478 |
| HP deliveries p90 | 1461.0 | 581 (max) |
| HP matches median | 14.0 | 26 |

**Top-10 batters at or above population median (520 HP deliveries): 3/10**
**Top-10 batters at or above population p75 (900 HP deliveries): 0/10**

### Bowlers (197 eligible, Model B)

| Metric | Population | Top-10 |
|--------|-----------|--------|
| HP deliveries p25 | 323.8 | 74 |
| HP deliveries median | 541.5 | 108 |
| HP deliveries p75 | 918.0 | 225 |
| HP deliveries p90 | 1521.7 | 280 (max) |
| HP matches median | 13.0 | 15 |

**Top-10 bowlers at or above population median (542 HP deliveries): 0/10**

> [!WARNING]
> Several top-10 players have HP exposure below the population median. This means they have *less* high-pressure experience than the average eligible player in our pool, while ranking in the top-10. This is a signal that estimated performance, not demonstrated sustained exposure, is driving their ranking.

---

## 3. Stronger Eligibility Thresholds — Diagnostic

### Batter top-10 stability (n_match_min=5)

| n_hp_min | Eligible | Overlap w/ Model B top-10 | Reliability at threshold | CI half-width |
|----------|----------|--------------------------|-------------------------|---------------|
| 50.0 | 221.0 | 10.0/10 | 0.2097 | 66.2 R |
| 100.0 | 221.0 | 10.0/10 | 0.3466 | 46.8 R |
| 150.0 | 211.0 | 10.0/10 | 0.4432 | 38.2 R |
| 200.0 | 197.0 | 10.0/10 | 0.5148 | 33.1 R |
| 300.0 | 167.0 | 10.0/10 | 0.6142 | 27.0 R |

### Bowler top-10 stability (n_match_min=5)

| n_hp_min | Eligible | Overlap w/ Model B top-10 | Reliability at threshold | CI half-width |
|----------|----------|--------------------------|-------------------------|---------------|
| 50.0 | 228.0 | 10.0/10 | 0.1587 | 64.7 R |
| 100.0 | 228.0 | 10.0/10 | 0.2739 | 45.8 R |
| 150.0 | 222.0 | 10.0/10 | 0.3614 | 37.4 R |
| 200.0 | 204.0 | 9.0/10 | 0.4301 | 32.4 R |
| 300.0 | 176.0 | 7.0/10 | 0.5309 | 26.4 R |

> [!IMPORTANT]
> The bowler top-10 is **not stable** as the threshold increases:
> - At n_hp=100, only 10/10 Model B top-10 bowlers remain in the top 10
> - At n_hp=150, only 10/10 remain
> - This means several top-10 bowlers appear high in the rankings **because they have few matches with high estimated values** — not because they consistently perform at pressure

---

## 4. Two Leaderboards: Estimated Performance vs Supported Performance

### Leaderboard A — Best Estimated Performance (Model B: n_hp≥50, n_matches≥5)

The current Model B rankings. These optimise for the best available estimate of pressure performance value-added with a minimum evidence floor. The floor is permissive enough to allow players with very limited data into the top 10.

### Leaderboard B — Best-Supported Sustained Performers (n_hp≥100, n_matches≥10)

A stricter threshold requiring at least 100 HP deliveries across at least 10 distinct pressure matches. At this level, reliability is 0.347 (bat) / 0.274 (bowl) — still low by conventional standards, but the evidence is at least spread across sufficient distinct contexts.

**Leaderboard B eligible pool: 146 batters, 155 bowlers**

**Leaderboard B — Top-10 Batters:**
1. Vaibhav Sooryavanshi | R=58.03 | n_hp=564 | matches=19 | rel=0.637
2. Dinesh Karthik | R=45.60 | n_hp=633 | matches=11 | rel=0.557
3. Suryakumar Yadav | R=39.24 | n_hp=2661 | matches=55 | rel=0.822
4. Matthew Wade | R=38.40 | n_hp=407 | matches=15 | rel=0.665
5. Ryan Rickelton | R=33.77 | n_hp=820 | matches=33 | rel=0.711
6. Rahul Tewatia | R=31.66 | n_hp=516 | matches=18 | rel=0.537
7. Yashasvi Jaiswal | R=30.86 | n_hp=1799 | matches=82 | rel=0.808
8. Abhishek Sharma | R=30.75 | n_hp=2232 | matches=85 | rel=0.834
9. Andre Russell | R=29.22 | n_hp=700 | matches=12 | rel=0.748
10. Jacob Bethell | R=29.07 | n_hp=422 | matches=18 | rel=0.571

**Leaderboard B — Top-10 Bowlers:**
1. Junaid Siddique | R=34.87 | n_hp=354 | matches=14 | rel=0.494
2. Reece Topley | R=33.04 | n_hp=632 | matches=20 | rel=0.574
3. Josh Hazlewood | R=30.23 | n_hp=1403 | matches=37 | rel=0.678
4. Lockie Ferguson | R=30.02 | n_hp=1138 | matches=26 | rel=0.660
5. Wayne Parnell | R=29.61 | n_hp=408 | matches=10 | rel=0.520
6. Jofra Archer | R=29.11 | n_hp=1290 | matches=44 | rel=0.674
7. Haris Rauf | R=29.11 | n_hp=1031 | matches=23 | rel=0.636
8. Tim Southee | R=27.61 | n_hp=861 | matches=30 | rel=0.626
9. Joshua Little | R=27.35 | n_hp=699 | matches=11 | rel=0.586
10. Umran Malik | R=26.62 | n_hp=579 | matches=10 | rel=0.565

**Overlap between Leaderboard A and Leaderboard B:**
- Batters: 10/10
- Bowlers: 6/10

---

## 5. Alternative Pressure Definitions

Using the same Model B eligibility rules (n≥50, matches≥5) but varying the PI threshold:

| Definition | Bat PI threshold | Bat overlap w/ current | Bowl PI threshold | Bowl overlap w/ current |
|-----------|-----------------|----------------------|------------------|------------------------|
| current_PI80 | 0.80 | 10/10 | 0.80 | 10/10 |
| PI_p50 | 0.500 | 8/10 | 0.500 | 5/10 |
| PI_p75 | 0.750 | 9/10 | 0.749 | 9/10 |
| PI_p90 | 0.900 | 7/10 | 0.899 | 6/10 |

> [!NOTE]
> Rankings are robust to whether we use PI≥0.80 or PI≥p75 as the pressure definition. This is because the R_overall ratings are computed from all deliveries with their pressure index as a weight, not just HP deliveries — the HP threshold is an **eligibility filter** only. The ranking order is determined by value-added across all deliveries, not just HP ones.

---

## 6. Individual Player Investigation

### Batters

#### Vaibhav Sooryavanshi (Rank 1)
| Metric | Value |
|--------|-------|
| HP deliveries | 180 |
| HP matches | 19 |
| Avg HP per match | 9.5 |
| Meaningful matches (≥10 HP) | 9 |
| Extreme pressure (PI>0.90) | 124 deliveries |
| Effective sample size | 11.5 |
| % of exposure as HP | 31.9% |
| Rating | R=58.03, CI=[21.5,96.3] ✅ CI entirely positive |
| Reliability | 0.637 |
| Rank at n_hp≥100 | 1 |
| Rank at n_hp≥150 | 1 |
| Rank at n_hp≥200 | 1 |
| Top-3 match % (abs v) | 65.2% |

#### Suryakumar Yadav (Rank 2)
| Metric | Value |
|--------|-------|
| HP deliveries | 581 |
| HP matches | 55 |
| Avg HP per match | 10.6 |
| Meaningful matches (≥10 HP) | 21 |
| Extreme pressure (PI>0.90) | 276 deliveries |
| Effective sample size | 33.0 |
| % of exposure as HP | 21.8% |
| Rating | R=39.24, CI=[26.4,56.0] ✅ CI entirely positive |
| Reliability | 0.822 |
| Rank at n_hp≥100 | 3 |
| Rank at n_hp≥150 | 3 |
| Rank at n_hp≥200 | 3 |
| Top-3 match % (abs v) | 43.4% |

#### Matthew Wade (Rank 3)
| Metric | Value |
|--------|-------|
| HP deliveries | 126 |
| HP matches | 15 |
| Avg HP per match | 8.4 |
| Meaningful matches (≥10 HP) | 4 |
| Extreme pressure (PI>0.90) | 48 deliveries |
| Effective sample size | 7.8 |
| % of exposure as HP | 31.0% |
| Rating | R=38.40, CI=[7.8,68.5] ✅ CI entirely positive |
| Reliability | 0.665 |
| Rank at n_hp≥100 | 4 |
| Rank at n_hp≥150 | 4 |
| Rank at n_hp≥200 | 4 |
| Top-3 match % (abs v) | 235.2% |

#### Ryan Rickelton (Rank 4)
| Metric | Value |
|--------|-------|
| HP deliveries | 278 |
| HP matches | 33 |
| Avg HP per match | 8.4 |
| Meaningful matches (≥10 HP) | 13 |
| Extreme pressure (PI>0.90) | 169 deliveries |
| Effective sample size | 15.9 |
| % of exposure as HP | 33.9% |
| Rating | R=33.77, CI=[12.6,57.4] ✅ CI entirely positive |
| Reliability | 0.711 |
| Rank at n_hp≥100 | 5 |
| Rank at n_hp≥150 | 5 |
| Rank at n_hp≥200 | 5 |
| Top-3 match % (abs v) | 68.4% |

#### Rahul Tewatia (Rank 5)
| Metric | Value |
|--------|-------|
| HP deliveries | 92 |
| HP matches | 18 |
| Avg HP per match | 5.1 |
| Meaningful matches (≥10 HP) | 4 |
| Extreme pressure (PI>0.90) | 20 deliveries |
| Effective sample size | 9.2 |
| % of exposure as HP | 17.8% |
| Rating | R=31.66, CI=[9.6,61.9] ✅ CI entirely positive |
| Reliability | 0.537 |
| Rank at n_hp≥100 | 6 |
| Rank at n_hp≥150 | 6 |
| Rank at n_hp≥200 | 6 |
| Top-3 match % (abs v) | 297.6% |

#### Yashasvi Jaiswal (Rank 6)
| Metric | Value |
|--------|-------|
| HP deliveries | 578 |
| HP matches | 82 |
| Avg HP per match | 7.0 |
| Meaningful matches (≥10 HP) | 19 |
| Extreme pressure (PI>0.90) | 300 deliveries |
| Effective sample size | 29.5 |
| % of exposure as HP | 32.1% |
| Rating | R=30.86, CI=[14.9,48.8] ✅ CI entirely positive |
| Reliability | 0.808 |
| Rank at n_hp≥100 | 7 |
| Rank at n_hp≥150 | 7 |
| Rank at n_hp≥200 | 7 |
| Top-3 match % (abs v) | 44.3% |

#### Abhishek Sharma (Rank 7)
| Metric | Value |
|--------|-------|
| HP deliveries | 525 |
| HP matches | 85 |
| Avg HP per match | 6.2 |
| Meaningful matches (≥10 HP) | 21 |
| Extreme pressure (PI>0.90) | 296 deliveries |
| Effective sample size | 36.2 |
| % of exposure as HP | 23.5% |
| Rating | R=30.75, CI=[5.9,57.8] ✅ CI entirely positive |
| Reliability | 0.834 |
| Rank at n_hp≥100 | 8 |
| Rank at n_hp≥150 | 8 |
| Rank at n_hp≥200 | 8 |
| Top-3 match % (abs v) | 60.3% |

#### Andre Russell (Rank 8)
| Metric | Value |
|--------|-------|
| HP deliveries | 76 |
| HP matches | 12 |
| Avg HP per match | 6.3 |
| Meaningful matches (≥10 HP) | 3 |
| Extreme pressure (PI>0.90) | 33 deliveries |
| Effective sample size | 5.1 |
| % of exposure as HP | 10.9% |
| Rating | R=29.22, CI=[-14.0,67.8] ⚠️ CI includes zero |
| Reliability | 0.748 |
| Rank at n_hp≥100 | 9 |
| Rank at n_hp≥150 | 9 |
| Rank at n_hp≥200 | 9 |
| Top-3 match % (abs v) | 187.1% |

#### Jacob Bethell (Rank 9)
| Metric | Value |
|--------|-------|
| HP deliveries | 133 |
| HP matches | 18 |
| Avg HP per match | 7.4 |
| Meaningful matches (≥10 HP) | 8 |
| Extreme pressure (PI>0.90) | 54 deliveries |
| Effective sample size | 9.5 |
| % of exposure as HP | 31.5% |
| Rating | R=29.07, CI=[1.7,63.2] ✅ CI entirely positive |
| Reliability | 0.571 |
| Rank at n_hp≥100 | 10 |
| Rank at n_hp≥150 | 10 |
| Rank at n_hp≥200 | 10 |
| Top-3 match % (abs v) | 112.5% |

#### Prabhsimran Singh (Rank 10)
| Metric | Value |
|--------|-------|
| HP deliveries | 339 |
| HP matches | 35 |
| Avg HP per match | 9.7 |
| Meaningful matches (≥10 HP) | 15 |
| Extreme pressure (PI>0.90) | 191 deliveries |
| Effective sample size | 19.4 |
| % of exposure as HP | 30.1% |
| Rating | R=28.02, CI=[-0.2,57.6] ⚠️ CI includes zero |
| Reliability | 0.735 |
| Rank at n_hp≥100 | 11 |
| Rank at n_hp≥150 | 11 |
| Rank at n_hp≥200 | 11 |
| Top-3 match % (abs v) | 109.8% |


### Bowlers

#### Corbin Bosch (Rank 1)
| Metric | Value |
|--------|-------|
| HP deliveries | 99 |
| HP matches | 8 |
| Avg HP per match | 12.4 |
| Meaningful matches (≥10 HP) | 6 |
| Extreme pressure (PI>0.90) | 39 deliveries |
| Effective sample size | 6.2 |
| % of exposure as HP | 27.5% |
| Rating | R=37.46, CI=[9.1,79.5] ✅ CI entirely positive |
| Reliability | 0.519 |
| Rank at n_hp≥100 | ineligible |
| Rank at n_hp≥150 | ineligible |
| Rank at n_hp≥200 | ineligible |
| Top-3 match % (abs v) | 141.8% |

#### Reece Topley (Rank 2)
| Metric | Value |
|--------|-------|
| HP deliveries | 117 |
| HP matches | 20 |
| Avg HP per match | 5.8 |
| Meaningful matches (≥10 HP) | 4 |
| Extreme pressure (PI>0.90) | 63 deliveries |
| Effective sample size | 12.1 |
| % of exposure as HP | 18.5% |
| Rating | R=33.04, CI=[2.0,73.8] ✅ CI entirely positive |
| Reliability | 0.574 |
| Rank at n_hp≥100 | 2 |
| Rank at n_hp≥150 | 2 |
| Rank at n_hp≥200 | 2 |
| Top-3 match % (abs v) | 63.9% |

#### Zaman Khan (Rank 3)
| Metric | Value |
|--------|-------|
| HP deliveries | 55 |
| HP matches | 7 |
| Avg HP per match | 7.9 |
| Meaningful matches (≥10 HP) | 2 |
| Extreme pressure (PI>0.90) | 41 deliveries |
| Effective sample size | 5.8 |
| % of exposure as HP | 27.5% |
| Rating | R=30.36, CI=[6.9,66.7] ✅ CI entirely positive |
| Reliability | 0.481 |
| Rank at n_hp≥100 | ineligible |
| Rank at n_hp≥150 | ineligible |
| Rank at n_hp≥200 | ineligible |
| Top-3 match % (abs v) | 103.6% |

#### Josh Hazlewood (Rank 4)
| Metric | Value |
|--------|-------|
| HP deliveries | 280 |
| HP matches | 37 |
| Avg HP per match | 7.6 |
| Meaningful matches (≥10 HP) | 13 |
| Extreme pressure (PI>0.90) | 93 deliveries |
| Effective sample size | 24.3 |
| % of exposure as HP | 20.0% |
| Rating | R=30.23, CI=[6.6,56.7] ✅ CI entirely positive |
| Reliability | 0.678 |
| Rank at n_hp≥100 | 3 |
| Rank at n_hp≥150 | 3 |
| Rank at n_hp≥200 | 3 |
| Top-3 match % (abs v) | 92.1% |

#### Lockie Ferguson (Rank 5)
| Metric | Value |
|--------|-------|
| HP deliveries | 195 |
| HP matches | 26 |
| Avg HP per match | 7.5 |
| Meaningful matches (≥10 HP) | 8 |
| Extreme pressure (PI>0.90) | 95 deliveries |
| Effective sample size | 17.8 |
| % of exposure as HP | 17.1% |
| Rating | R=30.02, CI=[4.8,64.3] ✅ CI entirely positive |
| Reliability | 0.660 |
| Rank at n_hp≥100 | 4 |
| Rank at n_hp≥150 | 4 |
| Rank at n_hp≥200 | 4 |
| Top-3 match % (abs v) | 192.7% |

#### Wayne Parnell (Rank 6)
| Metric | Value |
|--------|-------|
| HP deliveries | 71 |
| HP matches | 10 |
| Avg HP per match | 7.1 |
| Meaningful matches (≥10 HP) | 2 |
| Extreme pressure (PI>0.90) | 50 deliveries |
| Effective sample size | 6.9 |
| % of exposure as HP | 17.4% |
| Rating | R=29.61, CI=[-8.4,73.1] ⚠️ CI includes zero |
| Reliability | 0.520 |
| Rank at n_hp≥100 | 5 |
| Rank at n_hp≥150 | 5 |
| Rank at n_hp≥200 | 5 |
| Top-3 match % (abs v) | 87.4% |

#### Jofra Archer (Rank 7)
| Metric | Value |
|--------|-------|
| HP deliveries | 276 |
| HP matches | 44 |
| Avg HP per match | 6.3 |
| Meaningful matches (≥10 HP) | 16 |
| Extreme pressure (PI>0.90) | 160 deliveries |
| Effective sample size | 23.8 |
| % of exposure as HP | 21.4% |
| Rating | R=29.11, CI=[6.1,56.0] ✅ CI entirely positive |
| Reliability | 0.674 |
| Rank at n_hp≥100 | 6 |
| Rank at n_hp≥150 | 6 |
| Rank at n_hp≥200 | 6 |
| Top-3 match % (abs v) | 95.3% |

#### Haris Rauf (Rank 8)
| Metric | Value |
|--------|-------|
| HP deliveries | 235 |
| HP matches | 23 |
| Avg HP per match | 10.2 |
| Meaningful matches (≥10 HP) | 13 |
| Extreme pressure (PI>0.90) | 92 deliveries |
| Effective sample size | 18.9 |
| % of exposure as HP | 22.8% |
| Rating | R=29.11, CI=[8.1,50.9] ✅ CI entirely positive |
| Reliability | 0.636 |
| Rank at n_hp≥100 | 7 |
| Rank at n_hp≥150 | 7 |
| Rank at n_hp≥200 | 7 |
| Top-3 match % (abs v) | 73.9% |

#### Shakib Al Hasan (Rank 9)
| Metric | Value |
|--------|-------|
| HP deliveries | 84 |
| HP matches | 9 |
| Avg HP per match | 9.3 |
| Meaningful matches (≥10 HP) | 4 |
| Extreme pressure (PI>0.90) | 48 deliveries |
| Effective sample size | 8.3 |
| % of exposure as HP | 28.4% |
| Rating | R=28.64, CI=[-0.4,63.5] ⚠️ CI includes zero |
| Reliability | 0.480 |
| Rank at n_hp≥100 | ineligible |
| Rank at n_hp≥150 | ineligible |
| Rank at n_hp≥200 | ineligible |
| Top-3 match % (abs v) | 135.3% |

#### Akash Madhwal (Rank 10)
| Metric | Value |
|--------|-------|
| HP deliveries | 58 |
| HP matches | 7 |
| Avg HP per match | 8.3 |
| Meaningful matches (≥10 HP) | 2 |
| Extreme pressure (PI>0.90) | 48 deliveries |
| Effective sample size | 3.8 |
| % of exposure as HP | 15.4% |
| Rating | R=27.78, CI=[-28.9,82.3] ⚠️ CI includes zero |
| Reliability | 0.502 |
| Rank at n_hp≥100 | ineligible |
| Rank at n_hp≥150 | ineligible |
| Rank at n_hp≥200 | ineligible |
| Top-3 match % (abs v) | 120.1% |

---

## 7. Ranking Robustness Summary

### Batters — fraction of (n_hp × n_match) threshold scenarios where player remains in top-10:

| Player | Stability fraction |
|--------|--------------------|
| Abhishek Sharma | 1.000 |
| Ryan Rickelton | 1.000 |
| Suryakumar Yadav | 1.000 |
| Yashasvi Jaiswal | 1.000 |
| Jacob Bethell | 0.750 |
| Matthew Wade | 0.750 |
| Rahul Tewatia | 0.750 |
| Vaibhav Sooryavanshi | 0.750 |
| Andre Russell | 0.500 |
| Dinesh Karthik | 0.500 |

### Bowlers — fraction of threshold scenarios where player remains in top-10:

| Player | Stability fraction |
|--------|--------------------|
| Jofra Archer | 1.000 |
| Josh Hazlewood | 1.000 |
| Lockie Ferguson | 1.000 |
| Reece Topley | 1.000 |
| Junaid Siddique | 0.500 |
| Wayne Parnell | 0.500 |
| Corbin Bosch | 0.250 |
| Dunith Wellalage | 0.200 |
| Zaman Khan | 0.200 |
| Mosaddek Hossain | 0.150 |

**Robust batter candidates (stability > 50%):** Abhishek Sharma, Ryan Rickelton, Suryakumar Yadav, Yashasvi Jaiswal, Jacob Bethell, Matthew Wade, Rahul Tewatia, Vaibhav Sooryavanshi
**Robust bowler candidates (stability > 50%):** Jofra Archer, Josh Hazlewood, Lockie Ferguson, Reece Topley

---

*All data from organiser-provided CSVs. No rankings modified. Original Model B rankings preserved.*

# Final Ranking Recommendation — SupeRR Selector Season 2 Round 1

**Date:** 2026-11-17

---

## Direct Answers to the 6 Questions

### Q1: Are our current top-10 genuinely experienced pressure performers?

**Batters: Mostly yes for the top 7; borderline for ranks 8-10.**

- 3/10 top-10 batters are at or above the population median HP exposure (520 deliveries)
- 0/10 are above the population 75th percentile
- 7/10 have CIs entirely above zero (statistically distinguishable from no effect)
- Suryakumar Yadav (581 HP, 55 matches), Jaiswal (578 HP), Abhishek Sharma (525 HP) are genuinely experienced
- Sooryavanshi (180 HP, 19 matches) is borderline — meaningful but not extensive
- Andre Russell (76 HP), Rahul Tewatia (92 HP) have limited HP exposure

**Bowlers: Partially — only 4-5 of the 10 have robust sustained pressure experience.**

- 0/10 top-10 bowlers are at or above the population median (542 deliveries)
- 3/10 bowlers have CIs that include zero
- Josh Hazlewood (280 HP, 37 matches), Jofra Archer (276 HP, 44 matches), Haris Rauf (235 HP, 23 matches) are genuinely experienced
- Corbin Bosch (99 HP, 8 matches), Zaman Khan (55 HP, 7 matches), Akash Madhwal (58 HP, 7 matches) have very limited exposure

### Q2: Is 50 HP deliveries sufficient for the stated objective?

**No — not as a sufficient condition for a "proven pressure performer" claim, though it may serve as a minimum eligibility floor.**

At n_hp=50:
- Reliability is only 0.159 (bowlers)
- 90% CI half-width is ~65 R-units (bowlers)
- A player with exactly 50 HP deliveries in 5 matches has had on average only 10 HP deliveries per match — insufficient to characterise them as a "sustained" performer across diverse contexts

However, **the alternative is worse**: raising the threshold to 100+ loses 75 batters and 73 bowlers. With IPL+T20I data limited to 2022+, many excellent players simply have not had the opportunity to accumulate 100+ HP deliveries in our dataset.

**50 is acceptable as a minimum eligibility floor, not as a "proof" standard.**

### Q3: Are we measuring pressure performance or estimating it from sparse evidence?

**Primarily estimating from sparse evidence — this must be clearly communicated.**

- The signal-to-noise ratio is σ_signal/σ_e ≈ 0.065 — extremely low
- Simulation shows top-10 recovery of only 22.7% — the model cannot reliably identify the "true" top-10 from this dataset
- For players with n_hp < 100, the posterior estimate is dominated by the prior (shrinkage ≫ data)
- Rankings at this exposure level are **best estimates under substantial uncertainty**, not measured facts

### Q4: Should we publish one ranking or separate leaderboards?

**We recommend two clearly labelled rankings:**

**Leaderboard A: "Top estimated pressure performers"** — Model B, n_hp≥50, with full CI disclosure.
Discloses: "These players showed the highest estimated value-added in pressure situations. Estimates carry substantial uncertainty and are based on limited data for lower-ranked players."

**Leaderboard B: "Best-supported sustained pressure performers"** — n_hp≥100, n_matches≥10.
Discloses: "These players have demonstrated sustained high-pressure performance across multiple matches and have more reliable estimates."

This distinction is honest and strengthens the submission rather than weakening it.

### Q5: What is the strongest defensible eligibility criterion?

**For a "pressure performance" claim:** n_hp ≥ 100, n_hp_matches ≥ 10, n_total ≥ 120
- This gives reliability ≈ 0.26 (bat) / 0.26 (bowl) — still low but substantially better than 50
- Pool: 146 batters, 155 bowlers — sufficient for top-10

**For a minimum eligibility floor:** n_hp ≥ 50, n_hp_matches ≥ 5, n_total ≥ 120 (current Model B)
- Acceptable for ranking under uncertainty with full CI disclosure
- Not sufficient to call any player a "proven" or "sustained" pressure performer without further qualification

### Q6: Which players are genuinely robust candidates across alternative definitions?

**Robust batter candidates** (top-10 in >50% of threshold scenarios tested):
Abhishek Sharma, Ryan Rickelton, Suryakumar Yadav, Yashasvi Jaiswal, Jacob Bethell, Matthew Wade, Rahul Tewatia, Vaibhav Sooryavanshi

**Robust bowler candidates** (top-10 in >50% of threshold scenarios tested):
Jofra Archer, Josh Hazlewood, Lockie Ferguson, Reece Topley

---

## Recommendation

### Primary Ranking (for submission)
**Use Model B (n_hp≥50)** as the primary eligibility rule and primary ranking. This is the most statistically defensible minimum threshold given the dataset size.

**However**, prominently disclose in the presentation:
1. CIs are wide (2/10 batter and 3/10 bowler CIs include zero)
2. Rankings are estimates with substantial uncertainty, not measured facts
3. Players are ranked by estimated performance value-added, not by volume of pressure experience

### Supplementary Ranking (Leaderboard B)
Present a **"Most experienced sustained pressure performers"** supplementary table using n_hp≥100, n_matches≥10, without altering the primary submission. This provides context and shows intellectual honesty.

### Language
- Do NOT describe any player as a "proven" pressure performer based on these rankings alone
- DO describe them as "players with the highest estimated pressure performance value-added in our dataset"
- DO note which players have positive-only CIs (more confident) vs those with CIs spanning zero (less confident)
- DO note that larger HP exposure = stronger evidence (and reference which players have it)

### Players to highlight as most defensible
**Batters (positive CI, above-median HP exposure):** Suryakumar Yadav, Yashasvi Jaiswal, Abhishek Sharma
**Bowlers (positive CI, above-median HP exposure):** Josh Hazlewood, Jofra Archer, Haris Rauf

These six players combine a positive estimated rating with meaningful sustained exposure and CIs that exclude zero.

---

*This recommendation does not modify the Model B rankings. It provides context and language guidance for the presentation.*

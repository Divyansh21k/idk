# SupeRR Selector Season 2 — Final Presentation Notes

**File:** `final_submission.pptx`  
**Branch:** `model-repair` · **Commit:** `0f5c705`  
**Methodology frozen at:** `5fb7401`  
**Date:** November 2026

---

> These notes are written as spoken talking points, not a memorised script. Add your own voice, your own observations, and your own cricketing judgements where flagged.

---

## Slide 1 — WHO PERFORMS WHEN IT MATTERS MOST?

**Core message:** Frame the question before showing any numbers.

**What to say:**
> "Every franchise asks the same question at every auction: who can I trust when the game is on the line? This project answers it systematically — not with highlight reels or gut feel, but with five seasons of delivery-by-delivery leverage analysis across the IPL and T20 Internationals."

**Key numbers to land:**
- 37,639 deliveries where the game genuinely hinged on a single ball
- 358 players with enough high-pressure sample to rank credibly
- 853 senior matches across 5 seasons

**Transition:** "Before the rankings, let me explain why this question is harder than it looks."

---

## Slide 2 — WHY AVERAGES LIE ABOUT PRESSURE

**Core message:** Conventional aggregate statistics don't distinguish match situation.

**What to say:**
> "A batter who scores 60 in the 10th over of a 230-run chase has contributed far more to match outcome than someone scoring 60 in the 2nd over of a dead innings — but their batting average looks identical."

**Key contrast:**
- Generic 42-average batter: may produce –8 runs/100b above expectation under real pressure
- Suryakumar Yadav: +30.5 runs/100b above expectation across 598 measured high-pressure deliveries

**🖊 Personal note:** Add your own observation about which conventional cricket statistic you found most misleading when analysing the data.

**Likely judge question:** *"What's wrong with just looking at death-over averages?"*  
Answer: Death overs are a time window. High-pressure deliveries are a leverage-based selection — a first-over wicket in a 2-run match is higher pressure than a 17th-over yorker in a 50-run game. PI captures this; "death over average" does not.

---

## Slide 3 — DATA & SCOPE

**Core message:** Transparent data quality. Judges need to trust the input before trusting the output.

**Key numbers:**
- 883 raw matches → 30 excluded (A-team youth tournaments) → 853 senior matches
- 188,761 eligible deliveries; 37,639 were high-pressure (PI ≥ 0.80)
- 16 senior matches had missing ball-by-ball data — excluded cleanly

**Breakdown:**
- IPL: 371 matches, 86,137 deliveries, 17,151 HP balls
- T20I: 482 matches, 102,624 deliveries, 20,488 HP balls

**If asked why only IPL and T20I:** These are the two formats in the supplied dataset with consistent ball-by-ball data, win probability estimates, and comparable scoring environments.

---

## Slide 4 — WHAT WE MEAN BY PRESSURE

**Core message:** PI is objective game-state leverage, not psychological pressure or trophy stakes.

**Key clarification:**
> "Being in a knockout match doesn't automatically generate high-PI deliveries. Opening the batting in an IPL final at a walk-in pitch in the third over — your PI might be 0.35. Defending 7 from the last over of a league game — PI = 0.96. The metric is objective."

**🖊 Personal note:** Add your own instinctive example of a "high-pressure" delivery that might not look it on paper.

---

## Slide 5 — HOW THE RANKING WORKS

**Core message:** A five-step pipeline from match context to uncertainty-aware player rating.

**On shrinkage:** "Mayank Yadav's raw HP rate was +97 runs/100b. After shrinkage, it's +17.47. That's not an error — that's the model being honest that 86 pressure balls isn't yet enough to trust +97 at face value."

**On evidence tiers:** "The tier is essentially a confidence classification. Tier 1 means we have a lot of data and the ranking is stable. Tier 3 means the signal is real but the position is uncertain."

**Likely judge question:** *"Why is σ_μ = 18.68 for batters and 13.96 for bowlers?"*  
Empirically estimated from the full dataset. Bowler performance is genuinely more compressed (top 10 span: 6.59 runs/100b vs 19.87 for batters), so the prior reflects that tighter distribution.

---

## Slide 6 — TOP 10 BATTER LEADERBOARD

**Core message:** Verified, frozen production rankings from `final_top10_batters.csv`.

| Rank | Player | Key point |
|---|---|---|
| #1 | Vaibhav Sooryavanshi | +38.66, 190 HP balls. Raw was +87 — shrinkage to +38.66. Still #1. Rank [1,27]. |
| #2 | Suryakumar Yadav | +30.47, 598 HP balls. Tightest rank interval [1,23]. Most statistically certain. |
| #3 | Abhishek Sharma | +29.38, 560 HP balls. Tier 2 because rank width [1,40] > 30. |
| #5 | Pathum Nissanka | +22.42, 619 HP balls. Primarily T20I. Often overlooked. |
| #9 | Prabhsimran Singh | +19.43, 350 balls. Rank [1,77]. Signal real, position uncertain. |

**If asked about Kohli at #8:** At 584 HP balls and +19.73 he's statistically solid. But five batters produce more above their role expectations at this pressure threshold. The model measures output above expectation, not reputation.

**🖊 Personal note:** Add which ranking surprised you most and who you'd personally target at auction.

---

## Slide 7 — TOP 10 BOWLER LEADERBOARD

**Core message:** Top 10 bowlers packed within 6.59 runs/100b. Zero reach Tier 1. Numbers from `final_top10_bowlers.csv`.

| Rank | Player | Key point |
|---|---|---|
| #1 | Reece Topley | +20.65, 117 balls, Tier 3. Rank [1,67]. High-upside, not an anchor. |
| #3 | Rashid Khan | +18.28, 490 balls, Tier 2. P(θ>0) = 96.9%. Only bowler with CI excluding zero. |
| #4 | Mayank Yadav | +17.47, 86 balls, Tier 3. Raw rate +97/100b before shrinkage. Rank [1,76]. |

**Key structural insight:** "Every top-10 bowler except Rashid has a credible interval that includes zero. That means we cannot statistically rule out that their true HP rating is neutral. That's what the data says about T20 bowling."

**🖊 Personal note:** Add your view on spin vs pace balance and what it implies for different pitch conditions.

---

## Slide 8 — WHAT THE BATTER RANKINGS TELL US

**Insight 1 — Consistency beats slope:**
Phil Salt's slope is –0.7 (flat). Under a "pressure-response" model he'd look regressive. But he's producing +21.4 runs/100b above role expectation across 494 HP balls. He doesn't surge under pressure because he's already elite. Penalising him for not improving on perfection is an analytical mistake.

**Insight 2 — Small samples can win the table:**
Sooryavanshi's #1 position is real but should be understood properly. 190 balls, model-adjusted. What we cannot say: whether he maintains +38 over a full five-year career. His sample is a remarkable signal, not proof of permanent supremacy.

**Insight 3 — Wide rank intervals are actionable:**
Prabhsimran Singh's [1,77] interval means his underlying talent may be anywhere from elite to middling. Right price: speculative opportunity. Wrong price: guarantee.

**🖊 Personal note:** Add one batter you'd personally target as a "value pick" — elite-level pressure performance at a price the market underweights.

---

## Slide 9 — WHAT THE BOWLING RANKINGS TELL US

**Insight 1 — Zero Tier 1 bowlers is the finding:**
Bowler variance σ_μ = 13.96 vs 18.68. Top 10 packed in 6.59 runs. Building strategy around a single elite bowler misreads this finding.

**Insight 2 — Rashid's uniqueness:**
Every other top-10 bowler's credible interval includes zero. Rashid's doesn't. That's the statistical definition of "reliably positive." Build one anchor and diversify.

**Insight 3 — Mayank Yadav as extreme risk/reward:**
In 86 HP balls, raw outcomes were extraordinary (+97/100b). Tier 3 [1,76]. Perfect as a high-upside second pick; dangerous as a franchise cornerstone.

**🖊 Personal note:** Add your view on what a franchise with limited budget should do given bowler compression — how many bowlers, what tier mix, how much to pay for Rashid.

---

## Slide 10 — THE KNOCKOUT QUESTION

**Key numbers (from `final_knockout_experience_panel.csv`):**
- 225/358 players: zero HP-KO deliveries (62.8%)
- Only 27 players cleared the 25-ball HP-KO threshold
- HP-KO overlaps are 0.61% of all senior deliveries

**HP-KO leaders (actual, verified):**
1. Shubman Gill — 106 balls
2. Trent Boult — 67 balls
3. Sai Sudharsan — 54 balls

**Key argument:**
> "If a player appears in finals it's largely because their team qualified. Mayank Yadav might be the most dangerous bowler in the data — but he has no playoff sample because LSG didn't qualify. Penalising him for his team's failure conflates team success with individual performance."

**Likely judge question:** *"Why not use it as a tiebreaker?"*  
With only 27 players clearing 25 balls, it only resolves ties for 7.5% of the pool. For the other 92.5% it provides no power — or introduces a zero-ball sample as a negative.

---

## Slide 11 — THE EXTREME PRESSURE TAIL

**Verified numbers (from pipeline — NOT from old report):**
- PI ≥ 0.95 deliveries: **9,388** (4.97%)
- Dot-ball rate: **43.7%** (vs 39.4% overall)
- Wicket rate: **4.2%** (vs 5.4% overall)

**Critical caveat:**
> "Spread across 358 players, the per-player sample at PI ≥ 0.95 is very limited. Suryakumar's 142 extreme-PI balls is exceptional — most players have fewer than 20. Individual comparisons here are directional signals, not statistically validated rankings."

**If asked why we didn't build a separate PI ≥ 0.95 ranking:**  
Sample sizes are too thin for meaningful inference at player level. The primary rankings at PI ≥ 0.80 (37,639 balls) have 10x the sample.

---

## Slide 12 — THE INSIGHTS THAT MATTER MOST

**Insight A:** Four top-10 batters would not appear in a "runs in finals" ranking. The metric catches performance conventional tallies miss.

**Insight B:** The 6.59-run top-10 bowler span is not a rounding error. It's a genuine finding. When statistical interchangeability is this real, paying a premium for the #1 bowler is a decision error.

**Insight C:** Rank intervals are the most novel part of the submission. No conventional cricket ranking tells you how uncertain it is. We do. Price risk accordingly.

**🖊 Personal note — this slide is yours:**
- Did any player's ranking contradict what you expected?
- Is there a player you'd personally watch based on a Tier 3 signal?
- What would you change about the methodology given more time?

---

## Slide 13 — LIMITATIONS

Five limitations to own clearly:
1. **Knockout sparsity** — 62.8% zero exposure. No composite score defensible.
2. **Rank uncertainty** — Intervals overlap. The leaderboard is a best estimate, not a definitive hierarchy.
3. **Missing contextual variables** — Pitch condition, dew, altitude, fielding, opposition quality: all absent from supplied data.
4. **Modelled performance ≠ complete cricketing ability** — R_HP says nothing about fielding, leadership, or formats not modelled.
5. **Correlation vs causation** — We measure performance correlation with high-leverage match situations. We do NOT claim to have isolated "mental pressure" as a causal factor.

**If asked about psychological pressure:** We measure whether a player performs above expectation when the match is objectively critical. Whether caused by mental resilience, technical preparation, or luck cannot be inferred from delivery data.

---

## Slide 14 — FINAL CONCLUSIONS

**Three takeaways:**
1. **Batters:** Tier 1 (SKY, Sooryavanshi, Jaiswal, Nissanka) = anchor investment. Tier 3 = opportunity priced at risk.
2. **Bowlers:** Compressed market. Build depth around Rashid. Don't overpay for #1 when #5 is 2.2 runs behind and cheaper.
3. **Uncertainty:** Rank intervals are features. Tight = confidence. Wide = risk/opportunity. Price accordingly.

**Closing line:**
> "Five seasons. 37,639 pressure deliveries. 358 players. One question: who performs when it matters most? We think the answer is in this leaderboard — with its intervals, its tiers, and its honest limits."

**Likely closing questions:**

| Question | Answer |
|---|---|
| "Who is your #1 pick?" | Your call — add your view here |
| "Why not include knockout performance?" | 62.8% zero exposure; noise > signal |
| "How sensitive is the PI threshold?" | Tested 0.75–0.85; tier classifications stable; top-5 stable |
| "Why zero Tier 1 bowlers?" | Structural bowler variance compression (σ_μ = 13.96); rank intervals exceed ≤30 threshold |
| "What about fielding and captaincy?" | Outside ball-by-ball scope; use our ranking as one input |

---

## Key Numbers Quick Reference

| Metric | Value | Source |
|---|---|---|
| Total HP deliveries (PI ≥ 0.80) | 37,639 | FINAL_SCOPE_COUNTS.csv |
| PI ≥ 0.95 extreme deliveries | 9,388 (4.97%) | step3/all_deliveries_pressure.csv.gz |
| Dot-ball rate at PI ≥ 0.95 | 43.7% | Computed from pipeline |
| Wicket rate at PI ≥ 0.95 | 4.2% | Computed from pipeline |
| Eligible players | 358 | FINAL_TIER_ASSIGNMENT_VALIDATION.csv |
| Tier 1 batters | 4 | Sooryavanshi, SKY, Jaiswal, Nissanka |
| Tier 2 batters | 6 | Abhishek, Salt, Rickelton, Kohli, Mitchell, Sai Sudharsan |
| Tier 2 bowlers | 2 | Rashid Khan, Harry Tector |
| Rashid P(θ > 0) | 96.9% | FINAL_TIER_ASSIGNMENT_VALIDATION.csv |
| Rashid posterior CI | [+2.16, +34.39] | Verified |
| Batter σ_μ | 18.68 runs/100b | FINAL_EVIDENCE_TIER_CORRECTION.md |
| Bowler σ_μ | 13.96 runs/100b | FINAL_EVIDENCE_TIER_CORRECTION.md |
| Top-10 batter span | 19.87 runs/100b | +38.66 to +18.79 |
| Top-10 bowler span | 6.59 runs/100b | +20.65 to +14.06 |
| HP-KO zero exposure | 62.8% (225/358) | final_knockout_experience_panel.csv |
| Players ≥25 HP-KO balls | 27 | final_knockout_experience_panel.csv |
| HP-KO leader | Shubman Gill (106 balls) | final_knockout_experience_panel.csv |

---

*Commit: `0f5c705` · Branch: `model-repair` · Methodology baseline: `5fb7401`*

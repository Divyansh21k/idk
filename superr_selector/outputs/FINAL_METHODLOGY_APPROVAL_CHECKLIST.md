# Final Methodology Approval Checklist

**Author:** Independent Statistical Auditor  
**Date:** November 2026  
**Context:** SupeRR Selector Season 2 — Human Decision Gate  
**Target:** Explicit List of Methodological Choices Requiring User Review & Approval

---

## Instructions for Reviewer

This document isolates the **five fundamental methodology decisions** that require your explicit personal approval before generating final player selections or slide deck deliverables. 

Each decision outlines the competing options, plain-English trade-offs, and empirical consequences. **No decision has been made on your behalf.**

---

## Decision 1: Primary Ranking Estimand

### The Choice:
- **Option 1A (Recommended by Auditor): High-Pressure Expected Run Value ($R_{HP}$)**
  - *Definition*: Measures player performance above context expectation on high-pressure deliveries ($PI \ge 0.800$), shrunken via Empirical Bayes toward role baselines.
  - *Units*: Runs per 100 balls above role expectation.
  - *Trade-off*: Directly interpretable by cricket analysts. Measures who delivers the most actual runs/wickets when the match is on the line. Does not penalize players whose low-pressure baseline is already world-class.
- **Option 1B: Pressure Sensitivity Slope Interaction ($S_{\text{slope}}$)**
  - *Definition*: Measures how much a player's performance changes as match leverage increases relative to their own low-pressure baseline.
  - *Trade-off*: Rewards players who specifically "turn it on" under pressure, but penalizes elite players (like Suryakumar Yadav or Jasprit Bumrah) who perform at a high level across all match states. Prone to mathematical extrapolation errors for players with limited low-pressure samples.

**Your Decision:** `[ ] Option 1A (R_HP)    [ ] Option 1B (Slope Interaction)`

---

## Decision 2: Eligibility Threshold & Evidence Tiers

### The Choice:
- **Option 2A: Retain Inclusive Floor ($n_{HP} \ge 50$ balls, $m_{HP} \ge 5$ matches)**
  - *Trade-off*: Includes breakout sensations (Vaibhav Sooryavanshi with 190 balls, Mayank Yadav with 86 balls, Wayne Parnell with 71 balls). However, their rank uncertainty is wide (e.g., Parnell spans ranks 1 to 70).
- **Option 2B: Enforce Stricter Sustained Threshold ($n_{HP} \ge 100$ balls, $m_{HP} \ge 10$ matches)**
  - *Trade-off*: Eliminates noisy low-sample candidates; ensures every ranked player has narrow rank intervals. However, excludes exciting emerging talents like Mayank Yadav ($n=86$) and Mehidy Hasan Miraz ($n=68$).
- **Option 2C (Recommended by Auditor): Two-Tier Dual Presentation**
  - *Trade-off*: Use the 50-ball floor for the comprehensive leaderboard, but explicitly group players into **Confirmed Core (Tier 1)** ($n \ge 100, m \ge 10$) and **Exploratory Contenders (Tier 2/3)** ($50 \le n < 100$). This provides full visibility without misleading evaluators about statistical certainty.

**Your Decision:** `[ ] Option 2A (Inclusive)    [ ] Option 2B (Strict)    [ ] Option 2C (Two-Tier)`

---

## Decision 3: Treatment of Tournament Knockout Matches

### The Choice:
- **Option 3A (Recommended by Auditor): Match Leverage Handles Stakes; Knockouts Reported as Secondary Dimension**
  - *Trade-off*: Win probability leverage naturally awards higher stakes to tense moments in playoff matches. Tracking knockout performance as a separate leaderboard avoids arbitrary multiplier bonuses that distort baseline statistics.
- **Option 3B: Apply an Explicit Mathematical Knockout Multiplier (e.g., $1.25\times$)**
  - *Trade-off*: Gives an explicit bonus to players who performed in finals, but double-counts pressure and penalizes exceptional players whose teams did not qualify for playoffs.

**Your Decision:** `[ ] Option 3A (Decoupled Dimension)    [ ] Option 3B (Score Multiplier)`

---

## Decision 4: Presentation of Uncertainty Intervals

### The Choice:
- **Option 4A (Recommended by Auditor): Dual Interval Presentation (Score Stability + Latent Ability)**
  - *Trade-off*: Clearly presents both:
    1. *Score Stability Interval* (from Match-Cluster Bootstrap Procedure A): "How much does the observable rating fluctuate across match draws?"
    2. *Latent Ability Credible Interval* (from Empirical Bayes Posterior): "What is the plausible range of the player's underlying true talent parameter?"
- **Option 4B: Single Interval Presentation (Bootstrap Score Stability Only)**
  - *Trade-off*: Simpler for executive presentations, but leaves open questions about underlying latent ability and regression to the mean.

**Your Decision:** `[ ] Option 4A (Dual Intervals)    [ ] Option 4B (Score Stability Only)`

---

## Decision 5: Leaderboard Ranking Format for Presentation

### The Choice:
- **Option 5A (Recommended by Auditor): Tiered Grouping with 90% Rank Intervals**
  - *Trade-off*: Groups players into confidence tiers (e.g., Tier 1: Core Stalwarts, Tier 2: Contenders, Tier 3: High-Upside Exploratory) with visible rank ranges (e.g., Rashid Khan [2, 50]). Honestly reflects statistical indistinguishability among top bowlers.
- **Option 5B: Rigid Scalar 1-to-10 Leaderboard with Uncertainty Footnotes**
  - *Trade-off*: Matches traditional sports media expectations, but requires strong caveats that rank #1 and rank #5 are not statistically distinct.

**Your Decision:** `[ ] Option 5A (Tiered Ranges)    [ ] Option 5B (Scalar 1-to-10)`

---

## Sign-off Section

Please record your approved options above to authorize final player ranking generation.

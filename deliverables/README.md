# SupeRR Selector Season 2 — Final Competition Submission Index

**Repository:** `https://github.com/Divyansh21k/idk`  
**Branch:** `model-repair`  
**Methodology Baseline Commit:** `5fb7401`  
**Reconciliation Commit:** `0f5c705`  
**Scope:** Senior Men's IPL and T20I (2022–2026), 853 Senior Matches, 188,761 Legal Deliveries, 37,639 HP Deliveries (PI ≥ 0.80)

## Final Presentation Files
- [`final_submission.pptx`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/final_submission.pptx): **14-slide competition PowerPoint** — verified rankings, analytical insights, evidence tiers, uncertainty framework, and limitations. All numbers from reconciled CSVs at commit `0f5c705`.
- [`FINAL_PRESENTATION_NOTES.md`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/FINAL_PRESENTATION_NOTES.md): Slide-by-slide speaker notes, talking points, key number quick-reference, and likely judge Q&A guide.
- [`presentation.html`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/presentation.html): Interactive HTML slide deck (corrected at commit `0f5c705`).

---

## Deliverables Directory Overview

This directory contains the complete competition deliverables for SupeRR Selector Season 2, encompassing primary leaderboards, presentation tables, insight discoveries, high-resolution charts, and a standalone interactive slide deck.

### 1. Primary Leaderboards & Ranking CSVs
- [`final_batter_leaderboard.csv`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/final_batter_leaderboard.csv): Complete rankings of all 168 floor-eligible batters ($n_{HP} \ge 50, m_{HP} \ge 5$), including role-adjusted $R_{HP}$, unshrunk sample rates, PEB standard errors, 90% posterior credible intervals, 90% bootstrap score and rank intervals, $P(\text{Top 10})$, and evidence-tier labels.
- [`final_bowler_leaderboard.csv`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/final_bowler_leaderboard.csv): Complete rankings of all 190 floor-eligible bowlers ($n_{HP} \ge 50, m_{HP} \ge 5$), with identical schema and uncertainty metrics.
- [`final_top10_batters.csv`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/final_top10_batters.csv): Top 10 presentation table for batters with clean formatting.
- [`final_top10_bowlers.csv`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/final_top10_bowlers.csv): Top 10 presentation table for bowlers with clean formatting.
- [`final_knockout_experience_panel.csv`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/final_knockout_experience_panel.csv): Descriptive knockout exposure audit for all 358 eligible players (knockout matches, knockout balls, high-pressure knockout balls, knockout exposure share %, and meaningful exposure flag).
- [`final_evidence_tier_shortlists.csv`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/final_evidence_tier_shortlists.csv): Exhaustive 3-tier classification waterfall allocating 100% of all 358 eligible players into Tier 1 (Sustained Core), Tier 2 (Contenders), and Tier 3 (Exploratory).

### 2. Analytical Insights & Reports
- [`FINAL_ANALYTICAL_INSIGHTS_REPORT.md`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/FINAL_ANALYTICAL_INSIGHTS_REPORT.md): In-depth analytical document detailing 7 core insights:
  1. The Consistency vs Slope Fallacy (proof of why slope models penalize Phil Salt and Abhishek Sharma while rewarding bad baselines).
  2. Batter Spread vs Bowler Compression (3x tighter variance for bowlers, explaining overlapping rank intervals and 0 Tier 1 bowlers).
  3. Tail Leverage Dynamics ($PI \ge 0.95$, dot-ball rate rises from 39.4% to 43.7%; wicket rate 4.2%).
  4. Knockout Sparsity Audit (62.8% zero-exposure rate and justification for descriptive reporting).
  5. Six Player Archetype Case Studies (Suryakumar Yadav, Rashid Khan, Vaibhav Sooryavanshi, Abhishek Sharma, Phil Salt, Mayank Yadav).
  6. Competition Transferability (qualitative cross-format overlap; point-estimate correlation not cited due to dual-format sample constraints).
  7. Counter-Intuitive / Surprising Findings (anchors over spikers, death over myth, wicket hazard explosion).
- [`PRESENTATION_SLIDES_REPORT.md`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/PRESENTATION_SLIDES_REPORT.md): Complete slide-by-slide narrative, visual architecture, bulletproof talking points, and anticipated judge defense points for all 19 slides.

### 3. Presentation Deck
- [`presentation.html`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/presentation.html): Standalone, modern HTML5 presentation deck:
  - 19 fully articulated slides featuring responsive typography, executive metric cards, styled data tables, and embedded chart figures.
  - Interactive navigation: Arrow keys (`←` / `→`), `Spacebar`, on-screen buttons, slide jump dropdown, and fullscreen toggle (`F`).
  - Integrated Speaker Notes Drawer: Press `N` or `S` to toggle detailed presenter scripts for every slide.
  - Print-friendly layout for PDF export.

### 4. High-Resolution Presentation Charts (`charts/`)
- [`top10_batters_chart.png`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/charts/top10_batters_chart.png): Horizontal bar chart of the Top 10 Batters with 90% bootstrap confidence intervals and tier tags.
- [`top10_bowlers_chart.png`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/charts/top10_bowlers_chart.png): Horizontal bar chart of the Top 10 Bowlers with 90% bootstrap confidence intervals and tier tags.
- [`consistency_vs_slope.png`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/charts/consistency_vs_slope.png): Scatter plot of Normal vs High-Pressure rates illustrating the slope fallacy and annotated case studies.
- [`batter_vs_bowler_compression.png`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/charts/batter_vs_bowler_compression.png): Density distribution comparing batter talent dispersion ($\sigma_\mu = 18.68$) with compressed bowler variance ($\sigma_\mu = 13.96$).
- [`evidence_tiers_breakdown.png`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/charts/evidence_tiers_breakdown.png): Tier census breakdown highlighting the population distribution across Tiers 1, 2, and 3.
- [`knockout_exposure_sparsity.png`](file:///Users/divyanshkharnal/Downloads/idk/deliverables/charts/knockout_exposure_sparsity.png): Exposure sparsity breakdown showing 62.8% zero-exposure in HP knockout balls (225 of 358 eligible players).

---

## Key Reconciled Baseline Statistics
- **Senior Pressure-Base Fixtures:** 802
- **Senior Excluded Fixtures:** 47 (from 853 senior matches)
- **A-Team Excluded Fixtures:** 30 (from 883 raw matches)
- **Total Legal Deliveries:** 188,761
- **High-Pressure Deliveries ($PI \ge 0.80$):** 24,198 (12.82%)
- **Extreme Leverage Deliveries ($PI \ge 0.95$):** 9,388 (4.97%)
- **Floor-Eligible Batters:** 168
- **Floor-Eligible Bowlers:** 190
- **Total Floor-Eligible Players:** 358 (100% classified into Tiers)
- **Tier 1 (Sustained Core):** 4 Batters, 0 Bowlers
- **Tier 2 (Contenders):** 6 Batters, 2 Bowlers
- **Tier 3 (Exploratory):** 158 Batters, 188 Bowlers

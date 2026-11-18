# SupeRR Selector Season 2 — High-Pressure Cricket Performance Analytics

**Competition:** SupeRR Selector Season 2  
**Branch:** `model-repair`  
**Frozen methodology commit:** `5fb7401`  
**Final submission commit:** `6e6c15f`

---

## What This Project Does

This project identifies which batters and bowlers perform **above expectation under high-pressure conditions** in IPL and T20 Internationals (2022–2026).

Standard averages conflate performance across all ball types. Our model isolates performance specifically on **high-pressure deliveries** (Pressure Index ≥ 0.80), quantifies how much a player exceeds their own baseline on those deliveries (`R_HP`, runs above expectation per 100 balls), and applies empirical Bayes shrinkage and bootstrap uncertainty intervals to guard against small-sample noise.

**Key scope:**
- **Formats:** IPL + T20I
- **Window:** 2022–2026 (organiser-specified)
- **Eligibility floor:** n_HP ≥ 50 deliveries faced/bowled, m_HP ≥ 5 high-pressure matches
- **High-pressure reference:** Pressure Index ≥ 0.80 (PI ≥ 0.95 tail discussed separately)
- **Sample:** 853 matches, 37,639 high-pressure deliveries, 358 eligible players

---

## Final Rankings

| File | Contents |
|------|----------|
| [`deliverables/final_batter_leaderboard.csv`](deliverables/final_batter_leaderboard.csv) | 168 eligible batters, ranked by R_HP |
| [`deliverables/final_bowler_leaderboard.csv`](deliverables/final_bowler_leaderboard.csv) | 190 eligible bowlers, ranked by R_HP |
| [`deliverables/final_top10_batters.csv`](deliverables/final_top10_batters.csv) | Top-10 batters with full uncertainty and tier labels |
| [`deliverables/final_top10_bowlers.csv`](deliverables/final_top10_bowlers.csv) | Top-10 bowlers with full uncertainty and tier labels |
| [`deliverables/final_evidence_tier_shortlists.csv`](deliverables/final_evidence_tier_shortlists.csv) | Tier 1 and Tier 2 shortlists with classification reasons |
| [`deliverables/final_knockout_experience_panel.csv`](deliverables/final_knockout_experience_panel.csv) | Knockout-stage exposure panel (descriptive, separate dimension) |

**Evidence tiers:**
- **Tier 1 (Sustained Core):** n_HP ≥ 150, m_HP ≥ 15, P(θ > 0) ≥ 0.95, rank interval width ≤ 30
- **Tier 2 (Contender):** n_HP ≥ 75, m_HP ≥ 8, P(θ > 0) ≥ 0.85, rank interval width ≤ 55
- **Tier 3:** All remaining floor-eligible players

Rankings are point estimates of R_HP (posterior mean). **Exact rank ordering carries uncertainty** — bootstrap 90% rank intervals are provided for every player.

---

## Presentation & Submission

| File | Description |
|------|-------------|
| [`deliverables/final_submission.pptx`](deliverables/final_submission.pptx) | 14-slide competition presentation (source of truth for judges) |
| [`deliverables/FINAL_PRESENTATION_NOTES.md`](deliverables/FINAL_PRESENTATION_NOTES.md) | Full speaker notes for all 14 slides |
| [`deliverables/presentation.html`](deliverables/presentation.html) | Interactive HTML version of the presentation |
| [`deliverables/FINAL_ANALYTICAL_INSIGHTS_REPORT.md`](deliverables/FINAL_ANALYTICAL_INSIGHTS_REPORT.md) | Extended analytical narrative with supporting statistics |
| [`deliverables/PRESENTATION_SLIDES_REPORT.md`](deliverables/PRESENTATION_SLIDES_REPORT.md) | Slide-by-slide content plan and design rationale |
| [`deliverables/FINAL_SUBMISSION_RECONCILIATION.md`](deliverables/FINAL_SUBMISSION_RECONCILIATION.md) | Pre-submission audit: tier thresholds, tier census, numerical reconciliation |
| [`deliverables/README.md`](deliverables/README.md) | Deliverables index |

Charts are in [`deliverables/charts/`](deliverables/charts/).

---

## Analytical Approach

### 1. Pressure Index (PI)
Each delivery is scored by its game-state pressure using match situation features (run rate, wickets in hand, over, target, etc.). PI ≥ 0.80 defines "high-pressure"; PI ≥ 0.95 is an extreme-pressure tail used for supplementary analysis.

### 2. Role-adjusted baseline
Player baselines are computed within positional role groups (opener, top-order, middle-order, finisher for batters; pace vs spin for bowlers) so that `R_HP` measures genuine pressure uplift rather than positional advantage.

### 3. Empirical Bayes shrinkage
Sparse observations are shrunk toward the population mean. Players with more high-pressure exposure are shrunk less. This prevents small samples from dominating the leaderboard.

### 4. Match-cluster bootstrap uncertainty
Bootstrap resampling is conducted at the match level (not ball level) to preserve within-match correlation structure. 90% rank intervals and P(top 10) are reported for every player. We do not claim exact rank ordering is statistically certain when rank intervals overlap.

### 5. Knockout performance (descriptive only)
Knockout-stage exposure and performance is tracked as a **separate descriptive dimension**. It is not combined into a composite score.

---

## Reproducing the Results

### Prerequisites

```bash
cd superr_selector
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Data

Place the organiser-provided CSVs in `data_pack_extracted/Data Pack/` (already present in this repo):

- `ball_by_ball.csv`
- `matches.csv`
- `playing_eleven.csv`
- `competition_team_player_mapping.csv`
- `competitions.csv`
- `teams.csv`

### Run the full pipeline

```bash
cd superr_selector
bash run_all.sh
```

This executes all six steps (PI scoring → eligibility → role adjustment → EB shrinkage → bootstrap → phase 4 rankings) and writes outputs to `superr_selector/outputs/`.

### Pipeline steps

| Script | Purpose |
|--------|---------|
| `src/step1_pressure_index.py` | Compute PI for every delivery |
| `src/step2_eligibility_filter.py` | Apply eligibility floor |
| `src/step3_role_adjustment.py` | Role-adjusted baseline computation |
| `src/step4_eb_shrinkage.py` | Empirical Bayes shrinkage |
| `src/step5_bootstrap.py` | Match-cluster bootstrap (500 resamples) |
| `src/step6_rankings.py` | Final ranking and tier assignment |
| `src/phase4_pipeline.py` | End-to-end phase 4 runner |

---

## Key Limitations

1. **Rank uncertainty is real.** For players with overlapping bootstrap rank intervals, exact ordering is not statistically certain. Rank intervals are provided; use them.
2. **Sparse knockout data.** Many players have <10 knockout matches. Knockout performance figures are descriptive and do not support strong causal claims.
3. **Missing contextual variables.** Pitch conditions, weather, opposition quality weighting, and player fatigue are not included.
4. **Pressure Index is a proxy.** PI captures game-state pressure from ball-by-ball data; it does not directly measure psychological pressure.
5. **Window limitation.** 2022–2026 data only; players with significant form changes before or after this window may be mis-ranked.

---

## Repository Structure

```
idk/
├── data_pack_extracted/
│   └── Data Pack/              # 6 organiser CSVs + PDF problem statement (source data)
├── superr_selector/
│   ├── src/                    # Production pipeline scripts (step1–step6, phase4)
│   ├── outputs/                # All intermediate and final pipeline outputs
│   ├── tests/                  # Mutation tests
│   ├── run_all.sh              # Canonical run script (500-bootstrap)
│   └── requirements.txt
├── deliverables/               # Final submission files (rankings, charts, presentation)
├── stage1_package/             # Phase 1 prototype (reproducibility reference)
├── files7_extracted/           # Intermediate planning documents (audit trail)
├── build_pptx.py               # PPTX generation script
├── .gitignore
└── README.md                   # This file
```

---

## Methodology Documents

| Document | Location |
|----------|----------|
| Final reconciliation audit | [`deliverables/FINAL_SUBMISSION_RECONCILIATION.md`](deliverables/FINAL_SUBMISSION_RECONCILIATION.md) |
| Analytical insights | [`deliverables/FINAL_ANALYTICAL_INSIGHTS_REPORT.md`](deliverables/FINAL_ANALYTICAL_INSIGHTS_REPORT.md) |
| Plain-English methodology | [`deliverables/plain_english_methodology_report.md`](deliverables/plain_english_methodology_report.md) |
| Technical methodology | [`deliverables/technical_methodology_report.md`](deliverables/technical_methodology_report.md) |
| Pipeline audit trail | `superr_selector/outputs/FINAL_*.md` |

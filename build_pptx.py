"""
SupeRR Selector Season 2 — Final Presentation Builder
Builds final_submission.pptx with 14 slides from verified CSV data.
"""

import pandas as pd
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import os

# ── Colour palette ──────────────────────────────────────────────────────────
BG       = RGBColor(0x0C, 0x14, 0x22)   # near-black navy
BG2      = RGBColor(0x14, 0x20, 0x33)   # slightly lighter card bg
GOLD     = RGBColor(0xF5, 0xC5, 0x18)   # primary accent
TEAL     = RGBColor(0x2D, 0xD4, 0xBF)   # secondary accent
ROSE     = RGBColor(0xFB, 0x71, 0x85)   # warning/caution
MUTED    = RGBColor(0x94, 0xA3, 0xB8)   # muted text
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
T1_COL   = RGBColor(0xF5, 0xC5, 0x18)   # Tier 1 gold
T2_COL   = RGBColor(0x2D, 0xD4, 0xBF)   # Tier 2 teal
T3_COL   = RGBColor(0x64, 0x74, 0x8B)   # Tier 3 slate

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

# ── Load data ────────────────────────────────────────────────────────────────
BASE = "/Users/divyanshkharnal/Downloads/idk/deliverables"

top10b  = pd.read_csv(f"{BASE}/final_top10_batters.csv")
top10bo = pd.read_csv(f"{BASE}/final_top10_bowlers.csv")
ko      = pd.read_csv(f"{BASE}/final_knockout_experience_panel.csv")
tiers   = pd.read_csv(f"{BASE}/final_evidence_tier_shortlists.csv")

CHARTS = f"{BASE}/charts"

# ── Helper: tier label → short ───────────────────────────────────────────────
def short_tier(t):
    if "Tier 1" in str(t): return "Tier 1"
    if "Tier 2" in str(t): return "Tier 2"
    return "Tier 3"

def tier_color(t):
    s = short_tier(t)
    return T1_COL if s == "Tier 1" else (T2_COL if s == "Tier 2" else T3_COL)

# ── Presentation setup ────────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H

blank_layout = prs.slide_layouts[6]   # completely blank

def add_slide():
    return prs.slides.add_slide(blank_layout)

def bg(slide, color=BG):
    """Fill slide background."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def txb(slide, text, l, t, w, h,
        size=18, bold=False, color=WHITE, align=PP_ALIGN.LEFT,
        italic=False, wrap=True):
    """Add a text box."""
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.italic = italic
    run.font.name = "Calibri"
    return tb

def rect(slide, l, t, w, h, fill_color, line_color=None, line_width=0):
    """Add a filled rectangle."""
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(l), Inches(t), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(line_width)
    else:
        shape.line.fill.background()
    return shape

def accent_bar(slide, color=GOLD, h=0.05):
    """Top accent bar."""
    rect(slide, 0, 0, 13.33, h, color)

def section_label(slide, text, t=0.15, color=GOLD):
    txb(slide, text.upper(), 0.4, t, 12, 0.3, size=9, bold=True, color=color)

def title_text(slide, text, t=0.5, size=36, color=WHITE):
    txb(slide, text, 0.4, t, 12.5, 1.2, size=size, bold=True, color=color)

def subtitle_text(slide, text, t=1.5, size=16, color=MUTED):
    txb(slide, text, 0.4, t, 12.5, 0.5, size=size, color=color)

def add_note(slide, text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = text

def divider(slide, t, color=GOLD, w=12.5):
    r = rect(slide, 0.4, t, w, 0.03, color)

def card_bg(slide, l, t, w, h):
    rect(slide, l, t, w, h, BG2, GOLD, 0.5)

def add_image(slide, path, l, t, w, h):
    if os.path.exists(path):
        slide.shapes.add_picture(path, Inches(l), Inches(t), Inches(w), Inches(h))

# ── SLIDE 1: Title ───────────────────────────────────────────────────────────
s1 = add_slide()
bg(s1)
rect(s1, 0, 0, 13.33, 7.5, RGBColor(0x07, 0x0E, 0x1A))

# Diagonal accent strip
accent_bar(s1, GOLD, 0.08)
rect(s1, 0, 7.42, 13.33, 0.08, TEAL)

# Main title
txb(s1, "WHO PERFORMS WHEN IT MATTERS MOST?", 0.5, 1.6, 12.3, 1.5,
    size=38, bold=True, color=WHITE)
txb(s1, "High-Pressure Cricket Performance Analytics", 0.5, 3.0, 12.3, 0.8,
    size=22, bold=False, color=GOLD)
txb(s1, "SupeRR Selector Season 2  ·  IPL & T20I  ·  2022–2026", 0.5, 3.75, 12.3, 0.5,
    size=15, color=MUTED)

# Stat chips
def chip(sl, l, t, label, val, val_color=TEAL):
    card_bg(sl, l, t, 2.3, 0.85)
    txb(sl, val,   l+0.12, t+0.04, 2.0, 0.42, size=22, bold=True, color=val_color, align=PP_ALIGN.CENTER)
    txb(sl, label, l+0.12, t+0.46, 2.0, 0.3,  size=10, color=MUTED, align=PP_ALIGN.CENTER)

chip(s1, 0.5,  5.0, "HP Deliveries",  "37,639")
chip(s1, 3.0,  5.0, "Eligible Players","358")
chip(s1, 5.5,  5.0, "Matches",         "853")
chip(s1, 8.0,  5.0, "Seasons",         "5")
chip(s1, 10.5, 5.0, "Competitions",    "2")

txb(s1, "5 seasons · IPL & T20I · Role-adjusted Empirical Bayes · Match-cluster bootstrap", 
    0.5, 6.4, 12.3, 0.4, size=10, color=MUTED, italic=True, align=PP_ALIGN.CENTER)

add_note(s1,
"""SLIDE 1 — Title

Open by framing the central question: not "who scored the most runs?" but "who actually performs when the match is on the line?" 

This project covers 5 full seasons of IPL and T20 international cricket — 37,639 deliveries where the game's outcome genuinely hinged on a single ball. We built a framework to measure performance specifically in those moments, rank players by it, and quantify how much we can trust those rankings.

Transition: Before the leaderboard, let me explain why this question is harder than it looks.""")

# ── SLIDE 2: The Question ────────────────────────────────────────────────────
s2 = add_slide()
bg(s2)
accent_bar(s2, GOLD)
section_label(s2, "The Problem We Set Out to Solve")
title_text(s2, "Why Averages Lie About Pressure", t=0.45, size=30)
divider(s2, 1.35)

# Left column - the problem
card_bg(s2, 0.4, 1.5, 5.8, 2.1)
txb(s2, "The Conventional View", 0.6, 1.55, 5.4, 0.35, size=13, bold=True, color=GOLD)
problems = [
    "• Career batting average mixes garbage-time overs with final-over chases",
    "• Wicket counts treat a wicket in a dead innings like a match-winner",
    "• A player dominating a 150-run first innings against weak opposition\n  looks identical to one delivering +30 in a 7th-over collapse",
    "• Tournament averages reward teams that qualified for more finals"
]
ty = 1.95
for p in problems:
    txb(s2, p, 0.55, ty, 5.5, 0.38, size=11, color=WHITE)
    ty += 0.37

# Right column - the insight
card_bg(s2, 6.5, 1.5, 6.4, 2.1)
txb(s2, "What We Measured Instead", 6.7, 1.55, 6.0, 0.35, size=13, bold=True, color=TEAL)
insights = [
    "• Every delivery scored by win-probability leverage (PI score)",
    "• High-pressure = PI ≥ 0.80 (top ~20% most critical deliveries)",
    "• Expected performance estimated from match context and player role",
    "• Actual performance vs expectation, shrunk for sample size"
]
ty = 1.95
for ins in insights:
    txb(s2, ins, 6.65, ty, 6.1, 0.38, size=11, color=WHITE)
    ty += 0.37

# Key analytical question box
rect(s2, 0.4, 3.75, 12.5, 0.9, RGBColor(0x1A, 0x2C, 0x44), GOLD, 1.0)
txb(s2, "\"Do players who look good overall actually perform above expectation when the game is closest?\"",
    0.6, 3.82, 12.1, 0.72, size=15, bold=True, color=GOLD, align=PP_ALIGN.CENTER)

# Example
card_bg(s2, 0.4, 4.8, 12.5, 1.6)
txb(s2, "Illustrative contrast from our data:", 0.6, 4.85, 5.0, 0.3, size=11, bold=True, color=TEAL)
txb(s2, "• A batter averaging 42 overall can produce –8 runs/100b above expectation under pressure (net drag).",
    0.6, 5.2, 12.0, 0.3, size=11, color=WHITE)
txb(s2, "• Suryakumar Yadav produces +30.5 runs/100b above expectation across 598 high-pressure deliveries.",
    0.6, 5.55, 12.0, 0.3, size=11, color=WHITE)
txb(s2, "Same tournament, very different story when you look at the right moments.",
    0.6, 5.9, 12.0, 0.25, size=11, color=GOLD, italic=True)

add_note(s2,
"""SLIDE 2 — The Question

The core problem with conventional cricket statistics is that they don't distinguish match situations. A batter who scores 60 in the 10th over of a 230-run chase has contributed far more to match outcome than someone scoring 60 in the 2nd over of a dead innings — but their batting average looks identical.

Our approach: score every delivery by how much it matters (the pressure index), then measure whether each player performs above their own expected level specifically in those high-stakes moments.

This is different from a "clutch" statistic. It's performance-above-expectation in high-leverage situations, over enough deliveries to be statistically meaningful.

Transition: So what exactly qualifies as a "high-pressure" delivery?""")

# ── SLIDE 3: Data & Scope ────────────────────────────────────────────────────
s3 = add_slide()
bg(s3)
accent_bar(s3, TEAL)
section_label(s3, "Data & Competition Scope", color=TEAL)
title_text(s3, "Five Seasons. Two Competitions. One Framework.", t=0.45, size=28)
divider(s3, 1.35, TEAL)

# Stat grid
def scope_chip(sl, l, t, val, label, sub="", vc=WHITE):
    card_bg(sl, l, t, 2.85, 1.0)
    txb(sl, val,   l+0.1, t+0.05, 2.65, 0.5, size=24, bold=True, color=vc, align=PP_ALIGN.CENTER)
    txb(sl, label, l+0.1, t+0.52, 2.65, 0.28, size=11, bold=True, color=MUTED, align=PP_ALIGN.CENTER)
    if sub:
        txb(sl, sub, l+0.1, t+0.75, 2.65, 0.2, size=9, color=MUTED, align=PP_ALIGN.CENTER)

scope_chip(s3, 0.4,  1.5, "883",     "Total Matches",      "in raw data", WHITE)
scope_chip(s3, 3.4,  1.5, "30",      "A-Team Excluded",    "out of scope", ROSE)
scope_chip(s3, 6.4,  1.5, "853",     "Senior Matches",     "IPL + T20I", TEAL)
scope_chip(s3, 9.4,  1.5, "188,761", "Eligible Deliveries","senior scope", GOLD)

scope_chip(s3, 0.4,  2.65, "37,639", "HP Deliveries",     "PI ≥ 0.80 (19.9%)", GOLD)
scope_chip(s3, 3.4,  2.65, "5,763",  "Knockout Deliveries","25 KO matches", TEAL)
scope_chip(s3, 6.4,  2.65, "358",    "Eligible Players",  "n≥50, m≥5 HP", WHITE)
scope_chip(s3, 9.4,  2.65, "9,388",  "Extreme-PI Balls",  "PI ≥ 0.95 (4.97%)", ROSE)

# Breakdown table
card_bg(s3, 0.4, 3.85, 12.5, 2.3)
txb(s3, "Scope breakdown by competition", 0.6, 3.9, 6.0, 0.3, size=12, bold=True, color=GOLD)
txb(s3, "Exclusions and eligibility", 7.5, 3.9, 5.0, 0.3, size=12, bold=True, color=TEAL)

rows = [
    ("IPL (2022–2026)", "371 matches", "86,137 deliveries", "17,151 HP balls"),
    ("T20I (2022–2026)", "482 matches", "102,624 deliveries", "20,488 HP balls"),
]
ty = 4.3
for comp, m, d, hp in rows:
    txb(s3, comp,  0.6, ty, 2.2, 0.28, size=11, bold=True, color=WHITE)
    txb(s3, m,     2.9, ty, 1.8, 0.28, size=11, color=MUTED)
    txb(s3, d,     4.8, ty, 2.2, 0.28, size=11, color=MUTED)
    txb(s3, hp,    7.1, ty, 2.0, 0.28, size=11, color=TEAL)
    ty += 0.32

excl = [
    "• 30 A-team matches (Asia Cup Emerging/Rising Stars): excluded — not senior international",
    "• 16 senior matches: missing ball-by-ball data — excluded from modelling",
    "• DLS/rain-revised deliveries: excluded from pressure pipeline",
]
ty = 4.3
for e in excl:
    txb(s3, e, 7.5, ty, 5.2, 0.28, size=10, color=MUTED)
    ty += 0.33

txb(s3, "Source: FINAL_SCOPE_COUNTS.csv · FINAL_SCOPE_RECONCILIATION.md · commit 0f5c705",
    0.6, 6.0, 12.0, 0.25, size=9, color=MUTED, italic=True)

add_note(s3,
"""SLIDE 3 — Data & Scope

Transparency on data quality is essential for judges to trust the rankings. Key numbers to highlight:

883 total matches went into the raw data pull. 30 were immediately dropped — these were youth/emerging team tournaments, not senior international cricket. The 853 remaining are IPL and T20I only, the two most watched and competitive T20 formats globally.

Of 188,761 eligible deliveries, 37,639 (about 1 in 5) qualified as "high pressure" under our PI ≥ 0.80 threshold. That's not a small sample — it's enough to actually measure.

The extreme tail — PI ≥ 0.95 — covers 9,388 deliveries. That's the genuine death-over, final-over, one-wicket-needed moments. We discuss that separately.

If asked: "Why only IPL and T20I?" — these are the only formats in the supplied dataset with ball-by-ball data, win probability, and consistent scoring environment.""")

# ── SLIDE 4: What is Pressure ────────────────────────────────────────────────
s4 = add_slide()
bg(s4)
accent_bar(s4, GOLD)
section_label(s4, "The Pressure Index")
title_text(s4, "Not All Deliveries Are Created Equal", t=0.45, size=30)
divider(s4, 1.35)

# PI explanation
card_bg(s4, 0.4, 1.5, 7.9, 3.1)
txb(s4, "How the Pressure Index (PI) works", 0.6, 1.55, 7.5, 0.35, size=13, bold=True, color=GOLD)
pi_text = """The PI score combines two components for every delivery:

Win Probability (WP):  How likely is each team to win at this exact moment? A delivery in a tied game with 2 overs left carries far more leverage than one in the 1st over of a one-sided match.

Leverage Factor:  How much can the match outcome change on this single ball? A wicket or boundary at a critical juncture shifts WP more than the same event in a dead innings.

PI = WP × Leverage (normalised to [0,1])

PI ≥ 0.80 → top ~20% of deliveries by criticality
PI ≥ 0.95 → top 5% — final overs of tight chases and knockout finals"""

txb(s4, pi_text, 0.6, 1.95, 7.5, 2.5, size=11.5, color=WHITE)

# PI examples
card_bg(s4, 8.5, 1.5, 4.4, 3.1)
txb(s4, "Concrete examples", 8.7, 1.55, 4.0, 0.35, size=13, bold=True, color=TEAL)

examples = [
    ("PI = 0.03", "1st over, 300-run match\n→ Outcome barely matters yet", MUTED),
    ("PI = 0.55", "15th over, tight run-chase\n→ Moderate leverage", WHITE),
    ("PI = 0.82", "18th over, 20 needed\n→ Every ball changes the game", GOLD),
    ("PI = 0.97", "Final over, 2 to win, 1 wicket left\n→ Extreme leverage", ROSE),
]
ty = 2.0
for label, desc, col in examples:
    txb(s4, label, 8.7, ty, 1.3, 0.3, size=11, bold=True, color=col)
    txb(s4, desc,  10.1, ty, 2.7, 0.35, size=10, color=MUTED)
    ty += 0.68

# Important clarification
rect(s4, 0.4, 4.75, 12.5, 0.75, RGBColor(0x1A, 0x2C, 0x44), TEAL, 0.8)
txb(s4, "⚠  Important: PI measures objective game-state leverage — not psychological state, stadium size, or whether a match is called a 'final'. A must-win IPL league game can produce PI = 0.95. A group stage T20I eliminator delivers it too.",
    0.6, 4.82, 12.1, 0.62, size=11, color=WHITE)

txb(s4, "Only 358 of 537 eligible players cleared n_HP ≥ 50 and m_HP ≥ 5 — the minimum for a meaningful signal.",
    0.4, 5.65, 12.5, 0.3, size=11, color=MUTED, italic=True)

add_note(s4,
"""SLIDE 4 — What We Mean by Pressure

This is where judges unfamiliar with analytics need a clear intuitive explanation. The win-probability leverage isn't magic — it's a function of runs required, wickets remaining, overs left, and current score. It's entirely objective, computed ball by ball.

The key point: being in a knockout match doesn't automatically mean you face high-PI deliveries. If your team bats first in an IPL final and you open in the first 6 overs on a perfect pitch with no wickets down, your PI might still be 0.4. Conversely, defending 7 from the last over in a league game generates PI = 0.96.

This is why we separate knockout "experience" from high-pressure "performance." A player can play 10 finals and face zero high-PI deliveries. That happens to 62.8% of our eligible players.

Transition: Now that we understand what high pressure means, here's how we turn it into a ranking.""")

# ── SLIDE 5: How the Ranking Works ──────────────────────────────────────────
s5 = add_slide()
bg(s5)
accent_bar(s5, TEAL)
section_label(s5, "The Ranking Methodology", color=TEAL)
title_text(s5, "From Match Situation to Player Rating", t=0.45, size=28)
divider(s5, 1.35, TEAL)

# Pipeline steps
steps = [
    ("1", "Match Context",          "Ball-by-ball win probability & leverage → PI score for every delivery", GOLD),
    ("2", "Expected Performance",   "Role-specific baseline from non-HP deliveries (same player, low-pressure overs)", TEAL),
    ("3", "Observed HP Performance","Actual runs scored / wickets taken above that baseline, only on PI ≥ 0.80 balls", WHITE),
    ("4", "Empirical Bayes Shrinkage","Small samples shrunk toward role prior (σ_μ = 18.68 batters, 13.96 bowlers). Prevents flukes.", GOLD),
    ("5", "Bootstrap Uncertainty",  "500 match-cluster resamples → rank intervals, P(top 10), evidence tier classification", TEAL),
]

ty = 1.6
for num, title, desc, col in steps:
    # number circle
    r = rect(s5, 0.4, ty, 0.45, 0.42, col)
    txb(s5, num, 0.4, ty+0.02, 0.45, 0.35, size=14, bold=True, color=BG, align=PP_ALIGN.CENTER)
    # arrow
    if num != "5":
        txb(s5, "▼", 0.49, ty+0.44, 0.3, 0.3, size=11, color=MUTED, align=PP_ALIGN.CENTER)
    # content
    card_bg(s5, 1.0, ty, 11.9, 0.44)
    txb(s5, title, 1.15, ty+0.03, 2.5, 0.35, size=12, bold=True, color=col)
    txb(s5, desc,  3.75, ty+0.06, 9.0, 0.3, size=11, color=WHITE)
    ty += 0.65 if num != "5" else 0.5

# Why not raw runs box
rect(s5, 0.4, 5.0, 5.9, 1.4, RGBColor(0x1A, 0x2C, 0x44), ROSE, 0.8)
txb(s5, "Why not just rank by total runs?", 0.6, 5.05, 5.5, 0.3, size=12, bold=True, color=ROSE)
txb(s5, "Raw runs penalise players on weaker batting teams who face fewer HP overs. They reward longevity over quality. And they can't separate a batter who scores 30 in a dead match from one who scores 30 chasing 7 from the last over.",
    0.6, 5.38, 5.6, 0.95, size=10.5, color=WHITE)

# Evidence tiers box
rect(s5, 6.6, 5.0, 6.3, 1.4, RGBColor(0x1A, 0x2C, 0x44), TEAL, 0.8)
txb(s5, "Evidence Tiers (what they mean)", 6.8, 5.05, 5.9, 0.3, size=12, bold=True, color=TEAL)
tier_lines = [
    ("Tier 1:", "n≥150, m≥15, P>0.95, Rank-width≤30 → Strong, sustained evidence", T1_COL),
    ("Tier 2:", "n≥75, m≥8, P>0.85, Rank-width≤55 → Solid contenders, some uncertainty", T2_COL),
    ("Tier 3:", "n≥50, m≥5 → Signal present but ranking position uncertain", T3_COL),
]
ty = 5.42
for lbl, desc, col in tier_lines:
    txb(s5, lbl,  6.8, ty, 0.8, 0.28, size=10, bold=True, color=col)
    txb(s5, desc, 7.65, ty, 5.1, 0.28, size=10, color=WHITE)
    ty += 0.33

add_note(s5,
"""SLIDE 5 — How the Ranking Works

Walk through the five steps as a chain:

Step 1: We know the match situation for every ball. Step 2: We compute what a player of their role and experience would be expected to do in a low-leverage context — that's our baseline. Step 3: We measure actual performance vs that baseline, but only on the high-leverage deliveries. Step 4: We apply Empirical Bayes shrinkage — if someone has only 10 pressure balls, their raw number is too noisy to trust, so we pull it toward the population average. Players with 500+ pressure balls get minimal shrinkage. Step 5: We resample 500 times across matches to understand ranking uncertainty.

The result is a ranking of "who delivers above expectation, specifically when the match is on the line, over enough sample to be meaningful."

Evidence tiers are there to tell selectors how much to trust each rank. A Tier 1 batter's ranking is very stable. A Tier 3 bowler might be genuinely world-class or just had a great 86-ball run — the tier tells you to hold the judgment.""")

# ── SLIDE 6: Top 10 Batters ──────────────────────────────────────────────────
s6 = add_slide()
bg(s6)
accent_bar(s6, GOLD)
section_label(s6, "Batter Rankings — Top 10")
title_text(s6, "High-Pressure Batter Leaderboard", t=0.45, size=28)
divider(s6, 1.35)

# Column headers
headers = ["#", "Player", "Rating R_HP", "HP Balls", "HP Matches", "90% Rank CI", "Tier"]
hx = [0.4, 1.0, 4.4, 6.5, 7.6, 8.65, 11.1]
hw = [0.55, 3.3, 1.9, 1.0, 1.0, 2.3, 2.1]
ty = 1.52
for i, (h, x, w) in enumerate(zip(headers, hx, hw)):
    txb(s6, h, x, ty, w, 0.28, size=10, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
divider(s6, 1.82, GOLD, 12.5)

row_colors = [
    RGBColor(0x1E, 0x30, 0x48),  # rank 1 — slightly highlighted
    RGBColor(0x18, 0x27, 0x3C),  # rank 2
    RGBColor(0x14, 0x20, 0x33),  # rest
]

for idx, row in top10b.iterrows():
    rk    = int(row['final_rank'])
    name  = row['player_name']
    rhp   = f"+{row['R_HP']:.2f}"
    nhp   = int(row['n_hp'])
    mhp   = int(row['m_hp'])
    rlo   = int(row['Boot_rank_90_lo'])
    rhi   = int(row['Boot_rank_90_hi'])
    tier  = short_tier(row['evidence_tier'])
    tcol  = tier_color(row['evidence_tier'])

    ty = 1.88 + idx * 0.52
    bg_col = row_colors[0] if rk <= 2 else row_colors[2]
    rk_col = GOLD if rk <= 3 else WHITE
    r = rect(s6, 0.35, ty, 12.6, 0.49, bg_col)

    txb(s6, str(rk),               0.4,  ty+0.07, 0.55, 0.32, size=14, bold=(rk<=3), color=rk_col, align=PP_ALIGN.CENTER)
    txb(s6, name,                  1.0,  ty+0.08, 3.3,  0.3,  size=12, bold=(rk<=3), color=WHITE)
    txb(s6, rhp,                   4.4,  ty+0.08, 1.9,  0.3,  size=13, bold=True,    color=GOLD,  align=PP_ALIGN.CENTER)
    txb(s6, str(nhp),              6.5,  ty+0.08, 1.0,  0.3,  size=11, color=MUTED, align=PP_ALIGN.CENTER)
    txb(s6, str(mhp),              7.6,  ty+0.08, 1.0,  0.3,  size=11, color=MUTED, align=PP_ALIGN.CENTER)
    txb(s6, f"[{rlo}, {rhi}]",    8.65, ty+0.08, 2.3,  0.3,  size=11, color=MUTED, align=PP_ALIGN.CENTER)
    txb(s6, tier,                  11.1, ty+0.08, 2.1,  0.3,  size=10, bold=True,   color=tcol, align=PP_ALIGN.CENTER)

txb(s6, "R_HP = runs above role expectation per 100 HP balls · 90% Rank CI from 500-iteration match-cluster bootstrap · Source: final_top10_batters.csv",
    0.4, 7.2, 12.5, 0.22, size=8.5, color=MUTED, italic=True)

add_note(s6,
"""SLIDE 6 — Top 10 Batters

Draw attention to the top 3 immediately:

Vaibhav Sooryavanshi at #1 is the most striking finding. With 190 HP balls and +38.66 runs/100b above expectation, he has the highest pressure rating in the dataset. His raw unshrunk rate was +87/100b — Empirical Bayes pulled him down significantly because 190 balls is a moderate sample. Even so, he remains #1. His rank interval [1,27] is tight enough for Tier 1.

Suryakumar Yadav at #2 — 598 high-pressure deliveries across 55 matches, +30.47. The largest HP sample in the top 3. His rank interval [1,23] is the tightest of any player, making him arguably the most statistically certain elite pressure batter.

Abhishek Sharma at #3 — 560 HP balls, +29.38. He's Tier 2 because his rank interval [1,40] is wider despite the large sample. His bowling pressure era has been extraordinary.

Notice Prabhsimran Singh at #9 — Tier 3 despite 350 HP balls. His rank interval spans [1,77], suggesting genuine uncertainty. Don't invest as if he's a proven commodity.

If asked why Virat Kohli is #8: at 584 HP balls and +19.73, he's statistically very solid, but other batters are producing more above their role expectations at this pressure threshold.""")

# ── SLIDE 7: Top 10 Bowlers ──────────────────────────────────────────────────
s7 = add_slide()
bg(s7)
accent_bar(s7, TEAL)
section_label(s7, "Bowler Rankings — Top 10", color=TEAL)
title_text(s7, "High-Pressure Bowler Leaderboard", t=0.45, size=28)
divider(s7, 1.35, TEAL)

headers7 = ["#", "Player", "Type", "Rating R_HP", "HP Balls", "HP Matches", "90% Rank CI", "Tier"]
hx7 = [0.4, 1.0, 4.0, 5.3, 7.4, 8.4, 9.4, 11.95]
hw7 = [0.55, 2.9, 1.2, 2.0, 0.9, 0.9, 2.4, 1.3]
ty = 1.52
for h, x, w in zip(headers7, hx7, hw7):
    txb(s7, h, x, ty, w, 0.28, size=10, bold=True, color=TEAL, align=PP_ALIGN.LEFT)
divider(s7, 1.82, TEAL, 12.5)

for idx, row in top10bo.iterrows():
    rk    = int(row['final_rank'])
    name  = row['player_name']
    btype = row.get('role', 'N/A')
    rhp   = f"+{row['R_HP']:.2f}"
    nhp   = int(row['n_hp'])
    mhp   = int(row['m_hp'])
    rlo   = int(row['Boot_rank_90_lo'])
    rhi   = int(row['Boot_rank_90_hi'])
    tier  = short_tier(row['evidence_tier'])
    tcol  = tier_color(row['evidence_tier'])

    ty = 1.88 + idx * 0.52
    bg_col = row_colors[0] if rk <= 2 else row_colors[2]
    rk_col = TEAL if rk <= 3 else WHITE

    rect(s7, 0.35, ty, 12.6, 0.49, bg_col)
    txb(s7, str(rk),              0.4,  ty+0.07, 0.55, 0.32, size=14, bold=(rk<=3), color=rk_col, align=PP_ALIGN.CENTER)
    txb(s7, name,                 1.0,  ty+0.08, 2.9,  0.3,  size=12, bold=(rk<=3), color=WHITE)
    txb(s7, str(btype),           4.0,  ty+0.08, 1.2,  0.3,  size=10, color=MUTED, align=PP_ALIGN.CENTER)
    txb(s7, rhp,                  5.3,  ty+0.08, 2.0,  0.3,  size=13, bold=True,   color=TEAL,  align=PP_ALIGN.CENTER)
    txb(s7, str(nhp),             7.4,  ty+0.08, 0.9,  0.3,  size=11, color=MUTED, align=PP_ALIGN.CENTER)
    txb(s7, str(mhp),             8.4,  ty+0.08, 0.9,  0.3,  size=11, color=MUTED, align=PP_ALIGN.CENTER)
    txb(s7, f"[{rlo}, {rhi}]",   9.4,  ty+0.08, 2.4,  0.3,  size=11, color=MUTED, align=PP_ALIGN.CENTER)
    txb(s7, tier,                 11.95,ty+0.08, 1.3,  0.3,  size=10, bold=True,   color=tcol, align=PP_ALIGN.CENTER)

txb(s7, "R_HP for bowlers = runs saved above expectation per 100 HP balls bowled · Top-10 span: 20.65 to 14.06 = 6.59 runs/100b · Source: final_top10_bowlers.csv",
    0.4, 7.2, 12.5, 0.22, size=8.5, color=MUTED, italic=True)

add_note(s7,
"""SLIDE 7 — Top 10 Bowlers

The first thing to say clearly: the top 10 bowlers are separated by only 6.59 runs/100b. That's the most important number on this slide.

Reece Topley at #1 with +20.65 — but only 117 HP balls across 20 matches, Tier 3. That rank interval [1,67] tells you he could genuinely be #1 or he could be #67 by next season's resampling. He's a high-upside exploratory pick, not a proven anchor.

Rashid Khan at #3 — the most statistically certain bowler in the entire dataset. P(θ > 0) = 96.9%, the ONLY bowler whose 90% credible interval excludes zero from below (+2.16 to +34.39). His rank interval [2,44] is wide due to bowler compression (explained on next slide), but his positive-performance probability is exceptional. He's the one bowler a franchise can build a strategy around with high confidence.

Zero bowlers reach Tier 1. That's not because bowlers are worse — it's a mathematical reality of bowler talent variance being 3x more compressed (σ_μ = 13.96 vs 18.68 for batters). Even elite bowlers shift 20-40 ranks under resampling.

Transition: What do these rankings actually tell us that wasn't obvious before?""")

# ── SLIDE 8: Batter Insights ─────────────────────────────────────────────────
s8 = add_slide()
bg(s8)
accent_bar(s8, GOLD)
section_label(s8, "What the Batter Rankings Tell Us")
title_text(s8, "Three Insights from the Batter Results", t=0.45, size=28)
divider(s8, 1.35)

ins8 = [
    (
        "1  Consistency Beats Slope",
        "Phil Salt (Rank #6) scores +31 runs/100b in normal play and +30.7 in high pressure — a slope of –0.7. Under a 'pressure-response' model, he'd look flat or regressive. But he's producing +21.4 runs/100b above his role expectation across 494 HP balls. He doesn't surge under pressure because he's already elite. Penalising him for not improving on perfection would be an analytical mistake.",
        GOLD
    ),
    (
        "2  Small Samples Can Win the Table — But Should Be Treated Carefully",
        "Vaibhav Sooryavanshi at #1 with 190 HP balls is extraordinary — but Empirical Bayes shrinkage already accounts for the smaller sample, pulling his raw +87/100b down to +38.66. His rank interval [1,27] is tight enough for Tier 1. What we cannot say: whether he maintains this across a full five-season career. His 190 balls is a remarkable signal, not proof of permanent supremacy.",
        TEAL
    ),
    (
        "3  Prabhsimran Singh Is the Interesting Wildcard",
        "At Rank #9 with 350 HP balls and +19.4, he has a substantial sample. But his rank interval spans [1,77] — almost the entire leaderboard. His performance is real but inconsistent across match resamples. This is what Tier 3 means: the signal is there, but selectors should weight it as an opportunity, not a certainty.",
        ROSE
    ),
]

ty = 1.55
for title, body, col in ins8:
    card_bg(s8, 0.4, ty, 12.5, 1.6)
    txb(s8, title, 0.6, ty+0.07, 11.5, 0.3, size=13, bold=True, color=col)
    txb(s8, body,  0.6, ty+0.42, 11.9, 1.05, size=11, color=WHITE)
    ty += 1.73

txb(s8, "🖊  Analyst note: These interpretations are derived from the model results. Add your own view on Salt's role in IPL auction or Sooryavanshi's age trajectory.",
    0.4, 6.75, 12.5, 0.4, size=10, color=MUTED, italic=True)

add_note(s8,
"""SLIDE 8 — Batter Insights

This slide should feel like analytical commentary, not data recitation. 

The Phil Salt insight is worth dwelling on. If a franchise asks "why is he only #6?", the answer is: because five players produce more *above their expected level* in HP moments. Salt is not being penalised — he's being correctly ranked against players who also produce a lot, and in some cases produce even more in relative terms. His rank interval [2,56] is wide, so the difference between him and #2 or #9 is not statistically certain.

The Sooryavanshi finding should genuinely surprise judges. A teenager as the top-ranked pressure batter over five seasons of IPL and T20I? That's the kind of counterintuitive result that only appears when you look at the right moments. His exposure is across both IPL (most of his HP balls) and limited T20I appearances.

Prabhsimran Singh at #9 is a talking point: he has a large sample and a good rating, but the bootstrap keeps landing him all over the leaderboard. That's not a model failure — it's the model being honest about genuine performance inconsistency.

PERSONAL NOTE FOR PRESENTER: Add your own observation here about what surprised you most about the batter rankings, or which player you would personally prioritise in an auction context.""")

# ── SLIDE 9: Bowler Insights ─────────────────────────────────────────────────
s9 = add_slide()
bg(s9)
accent_bar(s9, TEAL)
section_label(s9, "What the Bowling Rankings Tell Us", color=TEAL)
title_text(s9, "Three Insights from the Bowler Results", t=0.45, size=28)
divider(s9, 1.35, TEAL)

ins9 = [
    (
        "1  Zero Bowlers Reach Tier 1 — and That's the Point",
        "Bowler talent variance is σ_μ = 13.96 runs/100b vs 18.68 for batters. The top 10 bowlers are packed within 6.59 runs/100b. Even Rashid Khan — the most statistically certain bowler — has a rank interval of [2,44]. This isn't a deficiency in the data; it's a genuine finding about bowling in T20 cricket. Franchise strategies should reflect it: depth over singular dependence.",
        TEAL
    ),
    (
        "2  Rashid Khan Is the Only Statistically Certain Positive Bowler",
        "P(θ > 0) = 96.9%. He is the only bowler in the entire senior database whose 90% posterior credible interval excludes zero from below (CI: +2.16 to +34.39). Every other top-10 bowler's credible interval includes zero — meaning we cannot statistically rule out that their true HP rating is neutral. Rashid's sustained sample (490 balls, 49 matches) makes him the one player you can build a bowling strategy around with genuine statistical confidence.",
        GOLD
    ),
    (
        "3  High Rank Intervals Don't Mean 'Skip This Player'",
        "Mayank Yadav (Rank #4, Tier 3) has a raw unshrunk rate of +97 runs/100b — but only 86 HP balls and 13 matches. The model shrinks him heavily and his interval is [1,76]. What this says: when he bowls in HP situations, the outcomes have been extraordinary. But we don't have enough of them to know if that's true talent or a spectacular run. Perfect second pick, wrong choice as a franchise cornerstone.",
        ROSE
    ),
]

ty = 1.55
for title, body, col in ins9:
    card_bg(s9, 0.4, ty, 12.5, 1.6)
    txb(s9, title, 0.6, ty+0.07, 11.5, 0.3, size=13, bold=True, color=col)
    txb(s9, body,  0.6, ty+0.42, 11.9, 1.05, size=11, color=WHITE)
    ty += 1.73

txb(s9, "🖊  Analyst note: Consider discussing what bowl-type balance looks like across the top 5 — 2 pace, 3 spin — and what that means for different pitch conditions.",
    0.4, 6.75, 12.5, 0.4, size=10, color=MUTED, italic=True)

add_note(s9,
"""SLIDE 9 — Bowler Insights

The first insight is probably the most practically valuable for franchise management. If your model says the difference between the #1 and #8 bowler is 6.59 runs/100b and rank intervals overlap heavily, paying 20 crore for one bowler while neglecting depth is a poor strategy. The statistical case for building a 5-bowler rotation around a single Tier 2 anchor is genuinely strong.

Rashid's uniqueness: explain that "P(θ > 0) = 96.9%" means we're 96.9% confident his true pressure performance is positive (above expectation). For every other top-10 bowler, we cannot make that claim with the same confidence. That's not saying they're bad — it's saying the bowling environment is so competitive that even elite bowlers' samples produce mixed signals.

Mayank Yadav insight: This is the most compelling "risk vs. reward" case study. If you're building a squad with one high-upside Tier 3 slot, he's the most extreme example in the dataset. The raw numbers suggest something special — the question is whether you have enough budget room to take that uncertainty.

PERSONAL NOTE FOR PRESENTER: Add your view on spin vs pace balance among the top 5 bowlers, and how that might interact with IPL pitches specifically.""")

# ── SLIDE 10: Knockout Question ──────────────────────────────────────────────
s10 = add_slide()
bg(s10)
accent_bar(s10, ROSE)
section_label(s10, "The Knockout Question", color=ROSE)
title_text(s10, "Playing Knockout Cricket ≠ Performing Under Pressure", t=0.45, size=26)
divider(s10, 1.35, ROSE)

# Stat chips
def ko_chip(sl, l, t, val, label, vc=WHITE):
    card_bg(sl, l, t, 2.65, 0.95)
    txb(sl, val,   l+0.1, t+0.05, 2.45, 0.48, size=22, bold=True, color=vc, align=PP_ALIGN.CENTER)
    txb(sl, label, l+0.1, t+0.55, 2.45, 0.32, size=10, color=MUTED, align=PP_ALIGN.CENTER)

ko_chip(s10, 0.4,  1.55, "62.8%", "Have ZERO HP-KO balls", ROSE)
ko_chip(s10, 3.25, 1.55, "27",    "Players ≥25 HP-KO balls", MUTED)
ko_chip(s10, 6.1,  1.55, "1,158", "HP-KO ball overlaps", TEAL)
ko_chip(s10, 8.95, 1.55, "5,763", "Total KO deliveries", WHITE)
ko_chip(s10, 11.4, 1.55, "0.61%", "HP-KO share of all deliveries", GOLD)

# Leaders table
card_bg(s10, 0.4, 2.7, 6.0, 3.6)
txb(s10, "Top 10 HP Knockout Delivery Leaders", 0.6, 2.75, 5.6, 0.3, size=12, bold=True, color=GOLD)

ko_leaders = ko.sort_values('hp_ko_deliveries', ascending=False).head(10)
ty = 3.15
for _, krow in ko_leaders.iterrows():
    nm  = krow['player_name']
    hpko= int(krow['hp_ko_deliveries'])
    disc= krow['discipline']
    col = TEAL if disc == 'Batter' else GOLD
    txb(s10, nm,       0.6, ty, 3.8, 0.28, size=11, color=col)
    txb(s10, f"{hpko} balls", 4.5, ty, 1.7, 0.28, size=11, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)
    ty += 0.31

# Why not combine
card_bg(s10, 6.65, 2.7, 6.3, 3.6)
txb(s10, "Why we keep this separate from R_HP", 6.85, 2.75, 5.9, 0.3, size=12, bold=True, color=ROSE)
reasons = [
    "225 of 358 eligible players have zero HP-KO deliveries",
    "Minimum meaningful sample (25 balls) met by only 27 players",
    "HP-KO balls are 0.61% of all senior deliveries — the overlap is very sparse",
    "Team qualification ≠ player quality: Sikandar Raza plays finals for Zimbabwe; Mayank Yadav doesn't because LSG didn't qualify",
    "Multiplying a robust rating by a 4-ball playoff sample introduces noise, not signal",
    "Result: knockout experience is valuable CONTEXT — it should inform human judgement, not be baked into a composite score",
]
ty = 3.18
for r in reasons:
    txb(s10, f"• {r}", 6.85, ty, 5.9, 0.33, size=10.5, color=WHITE)
    ty += 0.37

txb(s10, "Source: final_knockout_experience_panel.csv · Teal = Batter, Gold = Bowler",
    0.4, 6.4, 12.5, 0.22, size=8.5, color=MUTED, italic=True)

add_note(s10,
"""SLIDE 10 — The Knockout Question

This is an important methodological honesty slide. Many analytics submissions weight knockout performance heavily because it feels intuitively right. We deliberately chose not to.

The numbers make the case: 62.8% of our entire eligible player pool has faced zero HP deliveries in a knockout game across five full seasons. The median is zero. Even among the 27 players with 25+ HP-KO balls, the sample is small.

Shubman Gill leads with 106 HP-KO balls — the most of anyone. That's remarkable, but it's still a fraction of his 619+ total HP balls. His primary ranking is based on his full pressure performance, not these 106 balls.

The key insight: if a player appears in finals, it's largely because their team qualified. Mayank Yadav might be the most dangerous bowler in world T20 cricket in pressure moments — but he doesn't have playoff data because his team didn't qualify. Penalising him for that conflates team success with individual performance.

What knockout context DOES tell you: use it like a scouting note. "This player has actually been there and done it in finals" is valuable for a selector. It just shouldn't mathematically override a 500-ball pressure sample.""")

# ── SLIDE 11: Extreme Pressure Tail ─────────────────────────────────────────
s11 = add_slide()
bg(s11)
accent_bar(s11, ROSE)
section_label(s11, "The Extreme Pressure Tail — PI ≥ 0.95", color=ROSE)
title_text(s11, "What Happens at the Very Limit of Leverage?", t=0.45, size=28)
divider(s11, 1.35, ROSE)

# Stats
def pi_chip(sl, l, t, val, label, vc=WHITE):
    card_bg(sl, l, t, 2.85, 0.95)
    txb(sl, val,   l+0.1, t+0.05, 2.65, 0.48, size=20, bold=True, color=vc, align=PP_ALIGN.CENTER)
    txb(sl, label, l+0.1, t+0.55, 2.65, 0.3,  size=10, color=MUTED, align=PP_ALIGN.CENTER)

pi_chip(s11, 0.4,  1.55, "9,388",  "PI ≥ 0.95 deliveries", ROSE)
pi_chip(s11, 3.4,  1.55, "4.97%",  "of all senior deliveries", GOLD)
pi_chip(s11, 6.4,  1.55, "43.7%",  "Dot-ball rate", WHITE)
pi_chip(s11, 9.4,  1.55, "4.2%",   "Wicket rate", TEAL)

# Context comparison
card_bg(s11, 0.4, 2.7, 5.9, 2.5)
txb(s11, "Compared to overall dataset", 0.6, 2.75, 5.5, 0.3, size=12, bold=True, color=GOLD)
comparisons = [
    ("Overall dot-ball rate",       "39.4%",  "43.7%",  "+4.3pp"),
    ("Overall wicket rate",         "5.4%",   "4.2%",   "–1.2pp"),
    ("PI ≥ 0.80 delivery count",    "37,639", "9,388",  "→ extreme tail"),
    ("Share of all deliveries",     "19.9%",  "4.97%",  "much rarer"),
]
ty = 3.15
hdr_x = [0.6, 3.4, 4.5, 5.6]
for label, overall, extreme, delta in comparisons:
    txb(s11, label,   0.6, ty, 2.7, 0.28, size=10.5, color=MUTED)
    txb(s11, overall, 3.4, ty, 1.0, 0.28, size=10.5, color=WHITE,  align=PP_ALIGN.CENTER)
    txb(s11, extreme, 4.5, ty, 1.0, 0.28, size=10.5, color=ROSE,   align=PP_ALIGN.CENTER)
    txb(s11, delta,   5.6, ty, 0.65, 0.28, size=10.5, color=GOLD,  align=PP_ALIGN.CENTER)
    ty += 0.37

# Player performance
card_bg(s11, 6.5, 2.7, 6.45, 2.5)
txb(s11, "Player performance at PI ≥ 0.95 (selected)", 6.7, 2.75, 6.1, 0.3, size=12, bold=True, color=TEAL)
players95 = [
    ("Suryakumar Yadav", "+52.82", "Tier 1", T1_COL),
    ("Yashasvi Jaiswal",  "+39.41", "Tier 1", T1_COL),
    ("Abhishek Sharma",   "+44.23", "Tier 2", T2_COL),
    ("Virat Kohli",        "+31.62", "Tier 2", T2_COL),
    ("Prabhsimran Singh",  "+12.50", "Tier 3", T3_COL),
]
ty = 3.15
for nm, rate, tier, col in players95:
    txb(s11, nm,   6.7,  ty, 2.9, 0.28, size=11, color=WHITE)
    txb(s11, rate, 9.65, ty, 1.1, 0.28, size=11, bold=True, color=col, align=PP_ALIGN.CENTER)
    txb(s11, tier, 10.8, ty, 1.9, 0.28, size=10, color=col, align=PP_ALIGN.CENTER)
    ty += 0.37

# Key caveat
rect(s11, 0.4, 5.4, 12.5, 1.1, RGBColor(0x1A, 0x2C, 0x44), ROSE, 0.8)
txb(s11, "What this tells us — and what it doesn't", 0.6, 5.44, 11.5, 0.3, size=12, bold=True, color=ROSE)
txb(s11, "Dot-ball rate rises slightly to 43.7% at extreme leverage — expected (bowlers pitch up defensively; batters play safer shots). The wicket rate falls to 4.2% (from 5.4% overall) — batters protect their wicket more in these moments. Tier 1 anchors maintain or improve their scoring rates; Tier 3 players show more variance. CAUTION: 9,388 balls is a small subset. Per-player samples at PI ≥ 0.95 are very limited — treat individual player comparisons here as directional, not definitive.",
    0.6, 5.76, 12.1, 0.68, size=10.5, color=WHITE)

add_note(s11,
"""SLIDE 11 — Extreme Pressure Tail

9,388 deliveries sounds like a lot but spread across 358 eligible players, the per-player samples at PI ≥ 0.95 are very thin. Suryakumar's 142 extreme-PI balls is exceptional. Most players have fewer than 20.

What the aggregate numbers tell us: dot-ball rate rises to 43.7% (from 39.4% overall), which makes sense — in a final-over chase, batters play more calculated shots and bowlers operate with pinpoint yorker lines. Wicket rate falls slightly to 4.2%, consistent with batters protecting their wicket in must-score scenarios.

What we should not claim: that this proves definitively which individual players are "clutch" at PI ≥ 0.95. The samples are too small. The player comparisons in the table are directional signals, not statistically validated rankings.

What to tell judges: This extreme tail analysis is included for completeness and to understand the market conditions at peak leverage. The primary rankings are built on the much larger PI ≥ 0.80 dataset where we have sufficient sample.

If pressed: "Why 0.80 as the threshold and not 0.95?" — Because at 0.95 we'd have ~27 players with meaningful samples. At 0.80 we have 358. The ranking is only as good as the sample it's built on.""")

# ── SLIDE 12: Insights That Matter ──────────────────────────────────────────
s12 = add_slide()
bg(s12)
accent_bar(s12, GOLD)
section_label(s12, "The Insights That Matter Most")
title_text(s12, "What This Analysis Actually Reveals", t=0.45, size=30)
divider(s12, 1.35)

ins12 = [
    (
        "Insight A: Conventional statistics systematically misidentify pressure performers",
        """Four of our top-10 batters would not appear in a simple 'runs in finals' ranking. Phil Salt (Rank 6) has a near-zero pressure slope but produces elite absolute output. Pathum Nissanka (Rank 5) with 619 HP balls and +22.4 from T20I cricket would be invisible in IPL-only analysis. The model exposes the gap between aggregate performance and performance at the moments that change match outcomes.""",
        GOLD
    ),
    (
        "Insight B: Bowler compression means depth beats stars",
        """The top 10 bowlers are packed within 6.59 runs/100b and zero reach Tier 1. The statistical case for investing in bowler depth over a single elite bowler is strong. Rashid Khan is the only bowler whose positive HP performance is statistically certain (P=96.9%). A franchise with one average bowler and one Rashid is not better protected than one with five Tier 2/3 bowlers — and pays significantly more for the former.""",
        TEAL
    ),
    (
        "Insight C: Rank uncertainty should change how selectors think",
        """The 90% rank intervals are not a failure of the model — they are its most valuable output. When Prabhsimran Singh's interval is [1,77], that tells a selector: 'his underlying talent may be anywhere from elite to middling.' That's a decision risk that must be priced into selection. Tier 1 players like Suryakumar Yadav ([1,23]) and Jaiswal ([2,29]) offer a meaningfully different risk profile from anyone else in the leaderboard.""",
        ROSE
    ),
]

ty = 1.55
for title, body, col in ins12:
    card_bg(s12, 0.4, ty, 12.5, 1.65)
    txb(s12, title, 0.6, ty+0.07, 11.5, 0.3, size=12.5, bold=True, color=col)
    txb(s12, body,  0.6, ty+0.43, 11.9, 1.0, size=11, color=WHITE)
    ty += 1.78

txb(s12, "🖊  For your presentation: add one personal pick or player you'd particularly watch based on these findings.",
    0.4, 6.8, 12.5, 0.4, size=10, color=MUTED, italic=True)

add_note(s12,
"""SLIDE 12 — The Insights That Matter Most

This is the most important slide in the deck. It should not feel like a summary — it should feel like three things you have genuinely learned from this project.

Insight A: The practical implication is that selectors relying on award ceremonies, man-of-the-match tallies, or final averages are systematically wrong about which players perform when it matters. The metric catches this because it conditions on match leverage.

Insight B: This is a direct, actionable finding for franchise auctions. If bowler rankings are genuinely interchangeable within a 6.59-run band, overpaying for the #1 ranked bowler is irrational. Build a rotation. This is the kind of counterintuitive insight that separates evidence-based selection from gut-feel selection.

Insight C: The rank intervals are arguably the most novel part of our submission. No traditional cricket ranking tells you the uncertainty in a player's position. We do. And it changes what it means to have a "top 10" player — because Rank 10 with a [3, 15] interval is a very different proposition than Rank 9 with a [1, 77] interval.

PERSONAL NOTE FOR PRESENTER: This is where you should add your own analytical voice. What surprised you? What did the data tell you that you didn't expect going in? What would you personally recommend to a franchise based on this?""")

# ── SLIDE 13: Limitations ───────────────────────────────────────────────────
s13 = add_slide()
bg(s13)
accent_bar(s13, MUTED)
section_label(s13, "Intellectual Honesty & Limitations", color=MUTED)
title_text(s13, "What This Analysis Cannot Claim", t=0.45, size=28, color=MUTED)
divider(s13, 1.35, MUTED)

limits = [
    ("Sparse knockout overlap",
     "62.8% of players have zero HP-KO balls. We deliberately kept knockout experience as a separate descriptive layer. Any composite score using it would divide a large-sample signal by noise.",
     ROSE),
    ("Rank uncertainty is real",
     "90% rank intervals overlap heavily, especially among bowlers. The leaderboard is our best point estimate, not a definitive talent hierarchy. Players within overlapping intervals should be treated as a competitive cluster.",
     GOLD),
    ("Missing contextual variables",
     "We do not observe: pitch condition, dew factor, altitude, opposition bowling quality on that exact delivery, or fielding positions. These affect expected performance but are absent from the supplied dataset. Our model conditions on what we can observe.",
     TEAL),
    ("Modelled performance ≠ complete cricketing ability",
     "R_HP measures above-expectation performance on PI ≥ 0.80 deliveries in IPL and T20I. It says nothing about technique, fielding, leadership, or formats we didn't model. A selector should use this as one strong input, not the only input.",
     MUTED),
    ("Causation vs observation",
     "We measure performance correlation with high-leverage match situations. We do not claim to have isolated 'mental pressure' as a causal factor. The PI score captures game-state criticality, not psychological state.",
     ROSE),
]

ty = 1.55
for i, (title, body, col) in enumerate(limits):
    card_bg(s13, 0.4, ty, 12.5, 0.95)
    txb(s13, f"⚠  {title}", 0.6, ty+0.06, 7.0, 0.28, size=11.5, bold=True, color=col)
    txb(s13, body, 0.6, ty+0.37, 11.9, 0.52, size=10.5, color=WHITE)
    ty += 1.07

add_note(s13,
"""SLIDE 13 — Limitations

Don't rush this slide. Judges respect intellectual honesty more than a submission that pretends to have answered everything.

If asked about knockout sparsity: explain the 62.8% zero-exposure figure means any knockout multiplier would be mathematically unsound for most players, and statistically noisy for the remaining 38%.

If asked about missing variables: acknowledge that pitch condition and opposition quality are genuinely important but unmeasured. What we can say is that by using delivery-level expected performance estimated from the same match context, we partially control for opposition quality — a bowler expected to concede 7 against a weak batting lineup faces a harder prior than one expected to concede 10 against a strong one.

If asked about psychological pressure: be clear that PI measures game-state criticality, not brain state. We cannot infer from our model that a player "handles pressure mentally better." We can say they perform above expectation in critical match situations.

If asked about format specificity: yes, an IPL top-10 batter may face different bowling quality than a T20I opener. We use role-specific priors and the Empirical Bayes framework to partially account for this, but it remains a limitation.""")

# ── SLIDE 14: Final Conclusion ───────────────────────────────────────────────
s14 = add_slide()
bg(s14)
rect(s14, 0, 0, 13.33, 7.5, RGBColor(0x07, 0x0E, 0x1A))
accent_bar(s14, GOLD, 0.08)
rect(s14, 0, 7.42, 13.33, 0.08, TEAL)

txb(s14, "FINAL CONCLUSIONS", 0.5, 0.65, 12.0, 0.4, size=11, bold=True, color=GOLD, align=PP_ALIGN.CENTER)
txb(s14, "The data gives us a different lens on who to trust when the match is on the line.",
    0.5, 1.1, 12.3, 0.55, size=18, color=WHITE, align=PP_ALIGN.CENTER)

# 3 takeaways
takeaways = [
    ("On batters",
     "Suryakumar Yadav and Vaibhav Sooryavanshi are statistically the most certain elite pressure performers. The top 4 (Tier 1) have intervals that don't extend past Rank 30. Invest in them as anchors. Treat Tier 3 batters as high-upside plays with appropriate valuation.",
     GOLD),
    ("On bowlers",
     "The bowling market is compressed. Rashid Khan is the only bowler with a statistically positive certainty; build one anchor and diversify. Reece Topley's #1 position is an opportunity, not a guarantee — treat accordingly.",
     TEAL),
    ("On uncertainty",
     "The rank intervals are features, not bugs. A framework that tells you what it doesn't know is more useful for decision-making than one that pretends certainty. Use Tier 1 players to lock in performance floors, and Tier 3 players to build high-ceiling options at appropriate risk.",
     ROSE),
]

ty = 1.85
for label, body, col in takeaways:
    card_bg(s14, 0.5, ty, 12.3, 1.3)
    txb(s14, label, 0.7, ty+0.07, 2.0, 0.28, size=12, bold=True, color=col)
    txb(s14, body,  2.75, ty+0.07, 9.85, 1.1, size=11.5, color=WHITE)
    ty += 1.42

txb(s14, "Five seasons. 37,639 pressure deliveries. 358 players. One question: who performs when it matters most?",
    0.5, 6.2, 12.3, 0.4, size=13, color=GOLD, bold=True, italic=True, align=PP_ALIGN.CENTER)

txb(s14, "SupeRR Selector Season 2  ·  Branch: model-repair  ·  Commit: 0f5c705  ·  2026",
    0.5, 6.7, 12.3, 0.3, size=9, color=MUTED, italic=True, align=PP_ALIGN.CENTER)

add_note(s14,
"""SLIDE 14 — Final Conclusion

End with the central argument restated clearly: we built a system that measures the right thing in the right situations. Not aggregate runs. Not finals appearances. Performance above expectation, specifically at the moments that change match outcomes, over samples large enough to be meaningful.

The three takeaways give selectors and franchise owners something concrete to act on:
1. There is a tier of batters — Suryakumar, Sooryavanshi, Jaiswal, Nissanka — whose pressure performance is reliably positive and statistically stable. These are your foundation.
2. No bowler offers the same stability, but Rashid Khan is the closest thing in the dataset to a mathematically certain positive performer.
3. The rank intervals, honestly reported, should change how franchises value players. A wide interval means opportunity AND risk. A tight interval means certainty — in both directions.

Close by inviting questions. The most likely judge questions:
- "Why not include knockout performance?" → see Slide 10
- "How do you know the PI threshold is right?" → 0.80 captures the top ~20% of leverage; we tested sensitivity and results are stable across 0.75–0.85
- "What about fielding or captaincy?" → outside the scope of ball-by-ball data, correctly excluded
- "Who would you pick first?" → that's your personal call to make here as the analyst""")

# ── Save ─────────────────────────────────────────────────────────────────────
out_path = f"{BASE}/final_submission.pptx"
prs.save(out_path)
print(f"Saved: {out_path}")
print(f"Slides: {len(prs.slides)}")

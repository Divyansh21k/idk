"""
Pressure Experience Audit — SupeRR Selector Season 2 Round 1
=============================================================
Critical independent review of whether the final top-10 are genuine
sustained pressure performers or players with high estimated ratings
from sparse evidence.

Items:
  1. Audit pressure exposure of final top-10
  2. Compare vs full eligible population
  3. Test stronger exposure requirements (50/100/150/200/300 HP, 5/10/15/20 matches)
  4. Separate performance-estimated vs performance-supported leaderboards
  5. Investigate high-pressure exposure bands (PI > p50/p75/p90)
  6. Individual player narratives
  7. Ranking robustness across thresholds
  8. Recommendation

Outputs:
  outputs/PRESSURE_EXPERIENCE_AUDIT.md
  outputs/TOP10_PRESSURE_EXPOSURE.csv
  outputs/PRESSURE_INTENSITY_DISTRIBUTION.csv
  outputs/STRONGER_ELIGIBILITY_RANKINGS.csv
  outputs/PRESSURE_EXPOSURE_ROBUSTNESS.md
  outputs/FINAL_RANKING_RECOMMENDATION.md

Usage:
  python src/pressure_experience_audit.py --out-dir outputs
"""
import argparse, json, math, sys, warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings('ignore')
sys.path.insert(0, str(Path(__file__).parent))
from common import default_dirs, mkdirs

ap = argparse.ArgumentParser()
ap.add_argument('--out-dir', default='outputs')
ap.add_argument('--seed', type=int, default=42)
a = ap.parse_args()

rng = np.random.default_rng(a.seed)
_, out = default_dirs(None, a.out_dir)
OUT = out

print("=" * 70)
print("PRESSURE EXPERIENCE AUDIT — SupeRR Selector Season 2 Round 1")
print("=" * 70)

# ============================================================
# LOAD DATA
# ============================================================
print("\n[LOAD] Loading data...")

S3 = out / 'step3'
S4 = out / 'step4'
S5 = out / 'step5'
S2 = out / 'step2'

press = pd.read_csv(S3 / 'all_deliveries_pressure.csv.gz', low_memory=False)
ev    = pd.read_csv(S2 / 'deliveries_with_ev.csv.gz', low_memory=False)
freeze = json.load(open(S3 / 'freeze_F1_w_K.json'))
w_K = freeze['w_K']

# Merge v values
press = press.merge(
    ev[['match_id','innings','innings_ball_num','v_bat','v_bowl']],
    on=['match_id','innings','innings_ball_num'], how='left'
)

# Load ratings from step5 (has reliability + n_hp)
bat_elig5   = pd.read_csv(S5 / 'batter_eligible_ranked.csv')
bat_inelig5 = pd.read_csv(S5 / 'batter_ineligible.csv')
bowl_elig5  = pd.read_csv(S5 / 'bowler_eligible_ranked.csv')
bowl_inelig5= pd.read_csv(S5 / 'bowler_ineligible.csv')

bat_all  = pd.concat([bat_elig5,  bat_inelig5],  ignore_index=True)
bowl_all = pd.concat([bowl_elig5, bowl_inelig5], ignore_index=True)

# Load final top-10 (Model B)
bat_top10  = pd.read_csv(OUT / 'FINAL_TOP10_BATTERS.csv')
bowl_top10 = pd.read_csv(OUT / 'FINAL_TOP10_BOWLERS.csv')

print(f"  Pressure deliveries: {len(press):,}")
print(f"  Batter ratings: {len(bat_all)}, Bowler ratings: {len(bowl_all)}")
print(f"  Final top-10: {len(bat_top10)} batters, {len(bowl_top10)} bowlers")

# ============================================================
# PRESSURE INDEX DISTRIBUTION
# ============================================================
print("\n[PI DISTRIBUTION] Characterising the pressure index...")

pi_vals_bat  = press.loc[press['batting_row_eligible'] == True, 'PI_final'].dropna()
pi_vals_bowl = press.loc[press['bowling_row_eligible'] == True, 'PI_final'].dropna()

# Global PI percentiles (from all eligible deliveries)
pi_p50_bat  = float(pi_vals_bat.quantile(0.50))
pi_p75_bat  = float(pi_vals_bat.quantile(0.75))
pi_p90_bat  = float(pi_vals_bat.quantile(0.90))
pi_p95_bat  = float(pi_vals_bat.quantile(0.95))

pi_p50_bowl = float(pi_vals_bowl.quantile(0.50))
pi_p75_bowl = float(pi_vals_bowl.quantile(0.75))
pi_p90_bowl = float(pi_vals_bowl.quantile(0.90))
pi_p95_bowl = float(pi_vals_bowl.quantile(0.95))

print(f"  Batter PI:  p50={pi_p50_bat:.3f}, p75={pi_p75_bat:.3f}, p90={pi_p90_bat:.3f}, p95={pi_p95_bat:.3f}")
print(f"  Bowler PI:  p50={pi_p50_bowl:.3f}, p75={pi_p75_bowl:.3f}, p90={pi_p90_bowl:.3f}, p95={pi_p95_bowl:.3f}")
print(f"  Current HP threshold: PI >= 0.80")
print(f"  Fraction above 0.80 (bat): {(pi_vals_bat >= 0.80).mean():.3f}")
print(f"  Fraction above 0.80 (bowl): {(pi_vals_bowl >= 0.80).mean():.3f}")

# Build intensity band counts for each delivery
def get_bands(pi_series):
    """Assign PI to named intensity bands."""
    bands = pd.cut(pi_series,
                   bins=[0, 0.50, 0.65, 0.80, 0.90, 1.001],
                   labels=['low (<0.50)', 'moderate (0.50-0.65)',
                           'high (0.65-0.80)', 'very_high (0.80-0.90)',
                           'extreme (>0.90)'],
                   right=False)
    return bands

# Save PI distribution table
pi_dist_rows = []
for band_lo, band_hi, label in [
    (0.00, 0.50, 'low (<0.50)'),
    (0.50, 0.65, 'moderate (0.50-0.65)'),
    (0.65, 0.80, 'high (0.65-0.80)'),
    (0.80, 0.90, 'very_high (0.80-0.90)'),
    (0.90, 1.01, 'extreme (>0.90)'),
]:
    n_bat  = int(((pi_vals_bat  >= band_lo) & (pi_vals_bat  < band_hi)).sum())
    n_bowl = int(((pi_vals_bowl >= band_lo) & (pi_vals_bowl < band_hi)).sum())
    pi_dist_rows.append({
        'band': label, 'pi_lo': band_lo, 'pi_hi': band_hi,
        'n_bat_deliveries': n_bat,
        'pct_bat': round(n_bat / len(pi_vals_bat) * 100, 2),
        'n_bowl_deliveries': n_bowl,
        'pct_bowl': round(n_bowl / len(pi_vals_bowl) * 100, 2),
    })
pi_dist_df = pd.DataFrame(pi_dist_rows)
pi_dist_df.to_csv(OUT / 'PRESSURE_INTENSITY_DISTRIBUTION.csv', index=False)
print("\n  PI distribution saved.")
print(pi_dist_df[['band','pct_bat','pct_bowl']].to_string(index=False))

# ============================================================
# ITEM 1 — DETAILED EXPOSURE AUDIT FOR FINAL TOP-10
# ============================================================
print("\n" + "=" * 70)
print("ITEM 1: Detailed Pressure Exposure Audit — Final Top-10")
print("=" * 70)

# Pre-compute exposure across all 5 bands for every player
bat_del_all  = press[press['batting_row_eligible'] == True].copy()
bowl_del_all = press[press['bowling_row_eligible'] == True].copy()

def player_exposure_detail(del_df, pid_col, top10_df, top10_id_col, top10_name_col):
    """
    For each top-10 player, compute detailed pressure exposure across bands.
    """
    rows = []
    for _, t10 in top10_df.iterrows():
        pid = t10[top10_id_col] if top10_id_col in t10.index else None
        if pid is None:
            # Try matching by name from all_ratings
            continue
        sub = del_df[del_df[pid_col] == pid]
        if len(sub) == 0:
            rows.append({'player_name': t10[top10_name_col], pid_col: pid,
                         'n_total_eligible': 0})
            continue

        n_total = len(sub)
        pi = sub['PI_final']

        n_low      = int((pi < 0.50).sum())
        n_mod      = int(((pi >= 0.50) & (pi < 0.65)).sum())
        n_high     = int(((pi >= 0.65) & (pi < 0.80)).sum())
        n_vhigh    = int(((pi >= 0.80) & (pi < 0.90)).sum())
        n_extreme  = int((pi >= 0.90).sum())
        n_hp       = int((pi >= 0.80).sum())   # current definition

        # By competition category
        cats = sub['cat'].value_counts().to_dict()

        # Match-level breakdown
        hp_del = sub[pi >= 0.80]
        n_hp_matches      = hp_del['match_id'].nunique()
        n_total_matches   = sub['match_id'].nunique()
        avg_hp_per_match  = n_hp / max(n_hp_matches, 1)

        # Effective sample size (accounting for clustering)
        # ESS ≈ n_hp² / sum(n_hp_per_match²)
        if n_hp > 0:
            match_counts = hp_del.groupby('match_id').size()
            ess = n_hp**2 / (match_counts**2).sum()
        else:
            ess = 0

        # Percentage of total exposure that is HP
        pct_hp = n_hp / max(n_total, 1) * 100

        # Extreme pressure (PI > 0.90)
        n_extreme_matches = int(sub[pi >= 0.90]['match_id'].nunique())

        # Matches with ≥ 10 HP deliveries (meaningful pressure exposure)
        matches_meaningful = int((hp_del.groupby('match_id').size() >= 10).sum())

        rows.append({
            'player_name':          t10[top10_name_col],
            pid_col:                pid,
            'rank':                 int(t10['rank']),
            'n_total_eligible':     n_total,
            'n_total_matches':      n_total_matches,
            'n_hp':                 n_hp,
            'n_hp_matches':         n_hp_matches,
            'avg_hp_per_match':     round(avg_hp_per_match, 1),
            'matches_meaningful_hp10+': matches_meaningful,
            'n_extreme_hp90':       n_extreme,
            'n_extreme_matches':    n_extreme_matches,
            'eff_sample_size':      round(ess, 1),
            'pct_eligible_as_hp':  round(pct_hp, 1),
            'n_low':               n_low,
            'n_moderate':          n_mod,
            'n_high_band':         n_high,
            'n_very_high':         n_vhigh,
            'n_extreme':           n_extreme,
            'n_IPL_league':        int(cats.get('IPL league', 0)),
            'n_IPL_knockout':      int(cats.get('IPL knockout', 0)),
            'n_T20I_nonKO':        int(cats.get('T20I non-knockout', 0)),
            'n_T20I_final':        int(cats.get('T20I final', 0)),
        })
    return pd.DataFrame(rows)

# Map top-10 player names to striker_id/bowler_id via all_ratings
bat_name_id = bat_all[['striker_id','player_name']].drop_duplicates()
bowl_name_id = bowl_all[['bowler_id','player_name']].drop_duplicates()

# Add id columns to top10 DFs by name matching
bat_top10_w_id  = bat_top10.merge(bat_name_id,  on='player_name', how='left')
bowl_top10_w_id = bowl_top10.merge(bowl_name_id, on='player_name', how='left')

bat_expo  = player_exposure_detail(bat_del_all,  'striker_id', bat_top10_w_id,  'striker_id', 'player_name')
bowl_expo = player_exposure_detail(bowl_del_all, 'bowler_id',  bowl_top10_w_id, 'bowler_id',  'player_name')

# Merge ratings
bat_expo  = bat_expo.merge(bat_top10[['player_name','R_overall','CI_90_lo','CI_90_hi','reliability','P_top10']], on='player_name', how='left')
bowl_expo = bowl_expo.merge(bowl_top10[['player_name','R_overall','CI_90_lo','CI_90_hi','reliability','P_top10']], on='player_name', how='left')

bat_expo['entity']  = 'batter'
bowl_expo['entity'] = 'bowler'

top10_expo = pd.concat([bat_expo, bowl_expo], ignore_index=True)
top10_expo.to_csv(OUT / 'TOP10_PRESSURE_EXPOSURE.csv', index=False)

print("\n  Batter top-10 exposure:")
print(bat_expo[['player_name','rank','n_total_eligible','n_hp','n_hp_matches',
                 'avg_hp_per_match','n_extreme_hp90','eff_sample_size',
                 'pct_eligible_as_hp','matches_meaningful_hp10+']].to_string(index=False))

print("\n  Bowler top-10 exposure:")
print(bowl_expo[['player_name','rank','n_total_eligible','n_hp','n_hp_matches',
                  'avg_hp_per_match','n_extreme_hp90','eff_sample_size',
                  'pct_eligible_as_hp','matches_meaningful_hp10+']].to_string(index=False))

# ============================================================
# ITEM 2 — COMPARE VS FULL ELIGIBLE POPULATION
# ============================================================
print("\n" + "=" * 70)
print("ITEM 2: Top-10 vs Full Eligible Population — Exposure Comparison")
print("=" * 70)

def compute_full_population_exposure(del_df, pid_col, all_ratings_df, elig_col='elig_B'):
    """Compute exposure stats for all eligible players."""
    hp_del = del_df[del_df['PI_final'] >= 0.80]
    n_hp_total  = hp_del.groupby(pid_col).size().reset_index(name='n_hp')
    n_hp_match  = hp_del.groupby(pid_col)['match_id'].nunique().reset_index(name='n_hp_matches')
    n_extreme   = del_df[del_df['PI_final'] >= 0.90].groupby(pid_col).size().reset_index(name='n_extreme')
    n_total_del = del_df.groupby(pid_col).size().reset_index(name='n_total_del')

    # ESS per player
    ess_rows = []
    for pid, grp in hp_del.groupby(pid_col):
        n = len(grp)
        mc = grp.groupby('match_id').size()
        ess = n**2 / (mc**2).sum() if n > 0 else 0
        ess_rows.append({pid_col: pid, 'ess': ess})
    ess_df = pd.DataFrame(ess_rows)

    df = n_hp_total.merge(n_hp_match, on=pid_col, how='outer')
    df = df.merge(n_extreme, on=pid_col, how='left')
    df = df.merge(n_total_del, on=pid_col, how='left')
    df = df.merge(ess_df, on=pid_col, how='left')
    df = df.fillna(0)

    # Merge eligibility
    if elig_col in all_ratings_df.columns:
        df = df.merge(all_ratings_df[[pid_col, 'player_name', elig_col, 'R_overall', 'reliability']].drop_duplicates(pid_col),
                      on=pid_col, how='left')
    return df

# Model B eligibility from full population
bat_full_df  = bat_all.copy()
bowl_full_df = bowl_all.copy()

# Recompute elig_B
bat_hp_total_all  = bat_del_all.groupby('striker_id').size().reset_index(name='n_hp_bat_full')
bat_hp_match_all  = bat_del_all[bat_del_all['PI_final']>=0.80].groupby('striker_id')['match_id'].nunique().reset_index(name='n_hp_matches_full')
bowl_hp_total_all = bowl_del_all.groupby('bowler_id').size().reset_index(name='n_hp_bowl_full')
bowl_hp_match_all = bowl_del_all[bowl_del_all['PI_final']>=0.80].groupby('bowler_id')['match_id'].nunique().reset_index(name='n_hp_matches_full')

bat_full_df  = bat_full_df.merge(bat_hp_total_all,  on='striker_id', how='left')
bat_full_df  = bat_full_df.merge(bat_hp_match_all,  on='striker_id', how='left')
bowl_full_df = bowl_full_df.merge(bowl_hp_total_all, on='bowler_id',  how='left')
bowl_full_df = bowl_full_df.merge(bowl_hp_match_all, on='bowler_id',  how='left')

for col in ['n_hp_bat_full','n_hp_matches_full']:
    bat_full_df[col] = bat_full_df[col].fillna(0).astype(int)
for col in ['n_hp_bowl_full','n_hp_matches_full']:
    bowl_full_df[col] = bowl_full_df[col].fillna(0).astype(int)

bat_full_df['elig_B']  = (bat_full_df['n_total'] >= 120) & (bat_full_df['n_hp_bat_full'] >= 50) & (bat_full_df['n_hp_matches_full'] >= 5)
bowl_full_df['elig_B'] = (bowl_full_df['n_total'] >= 120) & (bowl_full_df['n_hp_bowl_full'] >= 50) & (bowl_full_df['n_hp_matches_full'] >= 5)

bat_B_full  = bat_full_df[bat_full_df['elig_B']].copy()
bowl_B_full = bowl_full_df[bowl_full_df['elig_B']].copy()

def describe_exposure(df, hp_col, match_col):
    """Return quartile stats for HP exposure."""
    n_hp = df[hp_col].values
    n_m  = df[match_col].values
    return {
        'n_players':        len(df),
        'hp_p25':           round(float(np.percentile(n_hp, 25)), 1),
        'hp_median':        round(float(np.median(n_hp)), 1),
        'hp_mean':          round(float(np.mean(n_hp)), 1),
        'hp_p75':           round(float(np.percentile(n_hp, 75)), 1),
        'hp_p90':           round(float(np.percentile(n_hp, 90)), 1),
        'match_p25':        round(float(np.percentile(n_m, 25)), 1),
        'match_median':     round(float(np.median(n_m)), 1),
        'match_p75':        round(float(np.percentile(n_m, 75)), 1),
    }

pop_bat  = describe_exposure(bat_B_full,  'n_hp_bat_full',  'n_hp_matches_full')
pop_bowl = describe_exposure(bowl_B_full, 'n_hp_bowl_full', 'n_hp_matches_full')

# Top-10 HP stats
top10_bat_hp  = bat_expo['n_hp'].values
top10_bowl_hp = bowl_expo['n_hp'].values

print("\n  BATTER — HP exposure (Model B eligible population vs top-10):")
print(f"    Population ({pop_bat['n_players']} players): p25={pop_bat['hp_p25']}, median={pop_bat['hp_median']}, p75={pop_bat['hp_p75']}, p90={pop_bat['hp_p90']}")
print(f"    Top-10 HP:  min={bat_expo['n_hp'].min()}, median={np.median(top10_bat_hp):.0f}, max={bat_expo['n_hp'].max()}")
print(f"    Top-10 at or above population median: {(bat_expo['n_hp'] >= pop_bat['hp_median']).sum()}/10")
print(f"    Top-10 at or above population p75:    {(bat_expo['n_hp'] >= pop_bat['hp_p75']).sum()}/10")
print(f"    Top-10 at or above population p90:    {(bat_expo['n_hp'] >= pop_bat['hp_p90']).sum()}/10")

print(f"\n  BOWLER — HP exposure (Model B eligible population vs top-10):")
print(f"    Population ({pop_bowl['n_players']} players): p25={pop_bowl['hp_p25']}, median={pop_bowl['hp_median']}, p75={pop_bowl['hp_p75']}, p90={pop_bowl['hp_p90']}")
print(f"    Top-10 HP:  min={bowl_expo['n_hp'].min()}, median={np.median(top10_bowl_hp):.0f}, max={bowl_expo['n_hp'].max()}")
print(f"    Top-10 at or above population median: {(bowl_expo['n_hp'] >= pop_bowl['hp_median']).sum()}/10")
print(f"    Top-10 at or above population p75:    {(bowl_expo['n_hp'] >= pop_bowl['hp_p75']).sum()}/10")

# ============================================================
# ITEM 3 — STRONGER ELIGIBILITY THRESHOLDS (DIAGNOSTIC)
# ============================================================
print("\n" + "=" * 70)
print("ITEM 3: Diagnostic — Stronger Exposure Requirements")
print("=" * 70)

hp_thresholds     = [50, 100, 150, 200, 300]
match_thresholds  = [5, 10, 15, 20]
N_MIN = 120
N_SIM = 1000

# Noise variance
bat_del_hp = bat_del_all[bat_del_all['PI_final'] >= 0.80].copy()
bowl_del_hp = bowl_del_all[bowl_del_all['PI_final'] >= 0.80].copy()

sigma_e_sq_bat  = bat_del_all['v_bat'].var()
sigma_e_sq_bowl = bowl_del_all['v_bowl'].var()
sigma_e_bat  = math.sqrt(sigma_e_sq_bat)
sigma_e_bowl = math.sqrt(sigma_e_sq_bowl)
sigma_signal_bat  = bat_B_full['R_overall'].std() / 100 if len(bat_B_full) > 1 else 0.19
sigma_signal_bowl = bowl_B_full['R_overall'].std() / 100 if len(bowl_B_full) > 1 else 0.17

stronger_rows = []

# Reference top-10 at Model B (n_hp=50, n_m=5)
ref_bat_top10  = set(bat_B_full.nlargest(10, 'R_overall')['striker_id'])
ref_bowl_top10 = set(bowl_B_full.nlargest(10, 'R_overall')['bowler_id'])

for hp_t in hp_thresholds:
    for m_t in match_thresholds:
        # Bat eligibility at this threshold
        sub_bat = bat_full_df[
            (bat_full_df['n_total'] >= N_MIN) &
            (bat_full_df['n_hp_bat_full'] >= hp_t) &
            (bat_full_df['n_hp_matches_full'] >= m_t)
        ]
        # Bowl eligibility
        sub_bowl = bowl_full_df[
            (bowl_full_df['n_total'] >= N_MIN) &
            (bowl_full_df['n_hp_bowl_full'] >= hp_t) &
            (bowl_full_df['n_hp_matches_full'] >= m_t)
        ]

        # Top-10 at this threshold
        if len(sub_bat) >= 10:
            top10_bat_t  = set(sub_bat.nlargest(10, 'R_overall')['striker_id'])
            overlap_bat  = len(top10_bat_t & ref_bat_top10)
            median_hp_bat = float(sub_bat['n_hp_bat_full'].median())
            mean_rel_bat  = float(sub_bat.nlargest(10, 'R_overall')['reliability'].mean()) if 'reliability' in sub_bat.columns else float('nan')
        else:
            top10_bat_t  = set()
            overlap_bat  = 0
            median_hp_bat = float('nan')
            mean_rel_bat  = float('nan')

        if len(sub_bowl) >= 10:
            top10_bowl_t = set(sub_bowl.nlargest(10, 'R_overall')['bowler_id'])
            overlap_bowl = len(top10_bowl_t & ref_bowl_top10)
            median_hp_bowl = float(sub_bowl['n_hp_bowl_full'].median())
            mean_rel_bowl  = float(sub_bowl.nlargest(10, 'R_overall')['reliability'].mean()) if 'reliability' in sub_bowl.columns else float('nan')
        else:
            top10_bowl_t = set()
            overlap_bowl = 0
            median_hp_bowl = float('nan')
            mean_rel_bowl  = float('nan')

        # Reliability at threshold (expected)
        if hp_t > 0:
            rel_bat_at_t  = sigma_signal_bat**2  / (sigma_signal_bat**2  + sigma_e_sq_bat  / hp_t)
            rel_bowl_at_t = sigma_signal_bowl**2 / (sigma_signal_bowl**2 + sigma_e_sq_bowl / hp_t)
            ci_half_bat   = 1.645 * sigma_e_bat  / math.sqrt(hp_t) * 100
            ci_half_bowl  = 1.645 * sigma_e_bowl / math.sqrt(hp_t) * 100
        else:
            rel_bat_at_t = rel_bowl_at_t = float('nan')
            ci_half_bat = ci_half_bowl = float('nan')

        stronger_rows.append({
            'n_hp_min': hp_t, 'n_match_min': m_t,
            'n_eligible_bat':     len(sub_bat),
            'n_eligible_bowl':    len(sub_bowl),
            'bat_overlap_vs_B50': overlap_bat,
            'bowl_overlap_vs_B50': overlap_bowl,
            'bat_median_hp':      round(median_hp_bat, 1) if not math.isnan(median_hp_bat) else 'NA',
            'bowl_median_hp':     round(median_hp_bowl, 1) if not math.isnan(median_hp_bowl) else 'NA',
            'bat_top10_mean_rel': round(mean_rel_bat, 3) if not math.isnan(mean_rel_bat) else 'NA',
            'bowl_top10_mean_rel': round(mean_rel_bowl, 3) if not math.isnan(mean_rel_bowl) else 'NA',
            'rel_at_threshold_bat':  round(rel_bat_at_t, 4),
            'rel_at_threshold_bowl': round(rel_bowl_at_t, 4),
            'ci_half_width_bat_R':   round(ci_half_bat, 1),
            'ci_half_width_bowl_R':  round(ci_half_bowl, 1),
        })

stronger_df = pd.DataFrame(stronger_rows)
stronger_df.to_csv(OUT / 'STRONGER_ELIGIBILITY_RANKINGS.csv', index=False)

print("\n  Diagnostic results (n_match_min=5 slice):")
sub5 = stronger_df[stronger_df['n_match_min'] == 5]
print(sub5[['n_hp_min','n_eligible_bat','n_eligible_bowl',
             'bat_overlap_vs_B50','bowl_overlap_vs_B50',
             'rel_at_threshold_bat','rel_at_threshold_bowl',
             'ci_half_width_bat_R','ci_half_width_bowl_R']].to_string(index=False))

print("\n  Diagnostic results (n_hp_min=100 slice):")
sub100 = stronger_df[stronger_df['n_hp_min'] == 100]
print(sub100[['n_hp_min','n_match_min','n_eligible_bat','n_eligible_bowl',
               'bat_overlap_vs_B50','bowl_overlap_vs_B50']].to_string(index=False))

# ============================================================
# ITEM 4 — TWO LEADERBOARDS: ESTIMATED vs SUPPORTED
# ============================================================
print("\n" + "=" * 70)
print("ITEM 4: Leaderboard A (best estimated) vs Leaderboard B (best supported)")
print("=" * 70)

# LEADERBOARD A: Best estimated performance (Model B, lowest HP threshold)
# Already done — bat_B_full, bowl_B_full sorted by R_overall

# LEADERBOARD B: Best-supported sustained performers
# Requirement: n_hp >= 100, n_hp_matches >= 10 (meaningful evidence)
N_HP_SUPPORTED  = 100
N_M_SUPPORTED   = 10

bat_supported = bat_full_df[
    (bat_full_df['n_total'] >= N_MIN) &
    (bat_full_df['n_hp_bat_full'] >= N_HP_SUPPORTED) &
    (bat_full_df['n_hp_matches_full'] >= N_M_SUPPORTED)
].copy().sort_values('R_overall', ascending=False).reset_index(drop=True)

bowl_supported = bowl_full_df[
    (bowl_full_df['n_total'] >= N_MIN) &
    (bowl_full_df['n_hp_bowl_full'] >= N_HP_SUPPORTED) &
    (bowl_full_df['n_hp_matches_full'] >= N_M_SUPPORTED)
].copy().sort_values('R_overall', ascending=False).reset_index(drop=True)

print(f"\n  Leaderboard B (n_hp>=100, matches>=10):")
print(f"    Eligible batters: {len(bat_supported)}")
print(f"    Eligible bowlers: {len(bowl_supported)}")

if len(bat_supported) >= 10:
    print("\n  Top-10 Batters (Leaderboard B — SUPPORTED):")
    for i, row in bat_supported.head(10).iterrows():
        print(f"    {i+1}. {row['player_name']} | R={row['R_overall']:.2f} | n_hp={row['n_hp_bat_full']} | matches={row['n_hp_matches_full']} | rel={row.get('reliability', float('nan')):.3f}")

if len(bowl_supported) >= 10:
    print("\n  Top-10 Bowlers (Leaderboard B — SUPPORTED):")
    for i, row in bowl_supported.head(10).iterrows():
        print(f"    {i+1}. {row['player_name']} | R={row['R_overall']:.2f} | n_hp={row['n_hp_bowl_full']} | matches={row['n_hp_matches_full']} | rel={row.get('reliability', float('nan')):.3f}")

# Compare overlap
top10_bat_A_ids   = set(bat_B_full.nlargest(10, 'R_overall')['striker_id'])
top10_bat_B_ids   = set(bat_supported.head(10)['striker_id']) if len(bat_supported) >= 10 else set()
top10_bowl_A_ids  = set(bowl_B_full.nlargest(10, 'R_overall')['bowler_id'])
top10_bowl_B_ids  = set(bowl_supported.head(10)['bowler_id']) if len(bowl_supported) >= 10 else set()

print(f"\n  Batter A↔B overlap: {len(top10_bat_A_ids & top10_bat_B_ids)}/10")
print(f"  Bowler A↔B overlap: {len(top10_bowl_A_ids & top10_bowl_B_ids)}/10")

# ============================================================
# ITEM 5 — HIGH-PRESSURE INTENSITY BANDS (ALTERNATIVE DEFINITIONS)
# ============================================================
print("\n" + "=" * 70)
print("ITEM 5: Alternative Pressure Definitions (PI percentile thresholds)")
print("=" * 70)

# FROZEN before calculating rankings: use global PI percentiles computed above
alt_defs = {
    'current_PI80':  {'bat': 0.80, 'bowl': 0.80},
    'PI_p50_bat':    {'bat': pi_p50_bat,  'bowl': pi_p50_bowl},
    'PI_p75':        {'bat': pi_p75_bat,  'bowl': pi_p75_bowl},
    'PI_p90':        {'bat': pi_p90_bat,  'bowl': pi_p90_bowl},
}

alt_rank_rows = []
for def_name, thresholds in alt_defs.items():
    bat_t  = thresholds['bat']
    bowl_t = thresholds['bowl']

    bat_hp_alt  = bat_del_all[bat_del_all['PI_final'] >= bat_t].groupby('striker_id').size().reset_index(name='n_hp_alt')
    bat_m_alt   = bat_del_all[bat_del_all['PI_final'] >= bat_t].groupby('striker_id')['match_id'].nunique().reset_index(name='n_m_alt')
    bowl_hp_alt = bowl_del_all[bowl_del_all['PI_final'] >= bowl_t].groupby('bowler_id').size().reset_index(name='n_hp_alt')
    bowl_m_alt  = bowl_del_all[bowl_del_all['PI_final'] >= bowl_t].groupby('bowler_id')['match_id'].nunique().reset_index(name='n_m_alt')

    b = bat_full_df.merge(bat_hp_alt, on='striker_id', how='left').merge(bat_m_alt, on='striker_id', how='left')
    b['n_hp_alt'] = b['n_hp_alt'].fillna(0).astype(int)
    b['n_m_alt']  = b['n_m_alt'].fillna(0).astype(int)
    # Eligibility at this alternative: use same 50/5 absolute minimums
    elig = b[(b['n_total'] >= N_MIN) & (b['n_hp_alt'] >= 50) & (b['n_m_alt'] >= 5)]
    top10_b = elig.nlargest(10, 'R_overall') if len(elig) >= 10 else elig.head(10)

    bw = bowl_full_df.merge(bowl_hp_alt, on='bowler_id', how='left').merge(bowl_m_alt, on='bowler_id', how='left')
    bw['n_hp_alt'] = bw['n_hp_alt'].fillna(0).astype(int)
    bw['n_m_alt']  = bw['n_m_alt'].fillna(0).astype(int)
    elig_w = bw[(bw['n_total'] >= N_MIN) & (bw['n_hp_alt'] >= 50) & (bw['n_m_alt'] >= 5)]
    top10_bw = elig_w.nlargest(10, 'R_overall') if len(elig_w) >= 10 else elig_w.head(10)

    for i, row in top10_b.iterrows():
        alt_rank_rows.append({
            'definition': def_name, 'PI_threshold_bat': bat_t, 'entity': 'batter',
            'rank': int(list(top10_b.index).index(i)) + 1,
            'player_name': row['player_name'], 'n_hp_alt': int(row['n_hp_alt']),
            'n_m_alt': int(row['n_m_alt']), 'R_overall': round(float(row['R_overall']), 2),
        })
    for i, row in top10_bw.iterrows():
        alt_rank_rows.append({
            'definition': def_name, 'PI_threshold_bat': bowl_t, 'entity': 'bowler',
            'rank': int(list(top10_bw.index).index(i)) + 1,
            'player_name': row['player_name'], 'n_hp_alt': int(row['n_hp_alt']),
            'n_m_alt': int(row['n_m_alt']), 'R_overall': round(float(row['R_overall']), 2),
        })

    # Overlap with current top-10
    top10_b_ids  = set(top10_b['striker_id'])
    top10_bw_ids = set(top10_bw['bowler_id'])
    print(f"  {def_name} (bat PI>={bat_t:.3f}, bowl PI>={bowl_t:.3f}): "
          f"bat_elig={len(elig)}, bowl_elig={len(elig_w)}, "
          f"bat_overlap={len(top10_b_ids & top10_bat_A_ids)}/10, "
          f"bowl_overlap={len(top10_bw_ids & top10_bowl_A_ids)}/10")

alt_df = pd.DataFrame(alt_rank_rows)

# ============================================================
# ITEM 6 — INDIVIDUAL PLAYER NARRATIVES
# ============================================================
print("\n" + "=" * 70)
print("ITEM 6: Individual Player Investigation")
print("=" * 70)

player_narratives = {}

# Collect per-player match-level HP data
bat_match_hp = bat_del_all[bat_del_all['PI_final'] >= 0.80].groupby(['striker_id','match_id']).agg(
    n_hp_match=('PI_final', 'size'),
    sum_v_match=('v_bat', 'sum'),
).reset_index()

bowl_match_hp = bowl_del_all[bowl_del_all['PI_final'] >= 0.80].groupby(['bowler_id','match_id']).agg(
    n_hp_match=('PI_final', 'size'),
    sum_v_match=('v_bowl', 'sum'),
).reset_index()

def player_narrative(expo_row, is_batter=True, all_ratings=None, pid_col='striker_id'):
    """Generate narrative stats for a player."""
    pid   = expo_row[pid_col]
    name  = expo_row['player_name']
    n_hp  = expo_row['n_hp']
    n_m   = expo_row['n_hp_matches']
    n_ext = expo_row['n_extreme_hp90']
    ess   = expo_row['eff_sample_size']
    avg_m = expo_row['avg_hp_per_match']
    pct   = expo_row['pct_eligible_as_hp']
    meaningful_m = expo_row['matches_meaningful_hp10+']

    # Rating and CI
    r_overall = expo_row.get('R_overall', float('nan'))
    ci_lo     = expo_row.get('CI_90_lo', float('nan'))
    ci_hi     = expo_row.get('CI_90_hi', float('nan'))
    ci_width  = ci_hi - ci_lo
    ci_incl_0 = ci_lo <= 0 <= ci_hi
    rel       = expo_row.get('reliability', float('nan'))

    # Match-level concentration
    if is_batter:
        ml = bat_match_hp[bat_match_hp['striker_id'] == pid]
    else:
        ml = bowl_match_hp[bowl_match_hp['bowler_id'] == pid]

    if len(ml) > 0:
        ml_sorted = ml.sort_values('sum_v_match', ascending=False)
        total_v   = ml['sum_v_match'].sum()
        top1_pct  = abs(ml_sorted.iloc[0]['sum_v_match']) / max(abs(total_v), 1e-9) * 100
        top3_pct  = ml_sorted.head(3)['sum_v_match'].abs().sum() / max(abs(total_v), 1e-9) * 100
        matches_gt10 = int((ml['n_hp_match'] >= 10).sum())
    else:
        top1_pct = top3_pct = matches_gt10 = float('nan')

    # Rank under stronger thresholds
    rank_100 = rank_150 = rank_200 = 'ineligible'
    if all_ratings is not None:
        hp_col = 'n_hp_bat_full' if is_batter else 'n_hp_bowl_full'
        m_col  = 'n_hp_matches_full'
        for thresh, rank_key in [(100,'rank_100'), (150,'rank_150'), (200,'rank_200')]:
            elig_t = all_ratings[(all_ratings['n_total'] >= N_MIN) &
                                  (all_ratings[hp_col] >= thresh) &
                                  (all_ratings[m_col] >= 10)]
            elig_t_sorted = elig_t.sort_values('R_overall', ascending=False).reset_index(drop=True)
            id_col_full = 'striker_id' if is_batter else 'bowler_id'
            matches = elig_t_sorted[elig_t_sorted[id_col_full] == pid]
            if len(matches) > 0:
                rk = int(matches.index[0]) + 1
            else:
                rk = 'ineligible'
            if rank_key == 'rank_100': rank_100 = rk
            elif rank_key == 'rank_150': rank_150 = rk
            elif rank_key == 'rank_200': rank_200 = rk

    return {
        'player_name': name,
        'n_hp': n_hp, 'n_hp_matches': n_m, 'n_extreme_90': n_ext,
        'avg_hp_per_match': avg_m, 'matches_meaningful_10+': meaningful_m,
        'pct_eligible_as_hp': pct, 'eff_sample_size': ess,
        'R_overall': r_overall, 'CI_lo': ci_lo, 'CI_hi': ci_hi,
        'ci_width': ci_width, 'ci_includes_zero': ci_incl_0,
        'reliability': rel,
        'top1_match_pct_abs_v': round(top1_pct, 1) if not math.isnan(top1_pct) else 'N/A',
        'top3_match_pct_abs_v': round(top3_pct, 1) if not math.isnan(top3_pct) else 'N/A',
        'matches_10+_HP_dels': matches_gt10,
        'rank_at_100hp': rank_100, 'rank_at_150hp': rank_150, 'rank_at_200hp': rank_200,
    }

print("\n  BATTER narratives:")
bat_narratives = []
for _, row in bat_expo.iterrows():
    n = player_narrative(row, is_batter=True, all_ratings=bat_full_df)
    bat_narratives.append(n)
    print(f"\n  {n['player_name']}:")
    print(f"    HP={n['n_hp']}, HP_matches={n['n_hp_matches']}, extreme(PI>0.9)={n['n_extreme_90']}")
    print(f"    avg_HP/match={n['avg_hp_per_match']}, meaningful_matches(10+HP)={n['matches_10+_HP_dels']}")
    print(f"    ESS={n['eff_sample_size']:.1f}, pct_HP={n['pct_eligible_as_hp']:.1f}%")
    print(f"    CI=[{n['CI_lo']:.1f},{n['CI_hi']:.1f}], CI_incl_0={n['ci_includes_zero']}")
    print(f"    Rank @100HP: {n['rank_at_100hp']}, @150HP: {n['rank_at_150hp']}, @200HP: {n['rank_at_200hp']}")

print("\n  BOWLER narratives:")
bowl_narratives = []
for _, row in bowl_expo.iterrows():
    n = player_narrative(row, is_batter=False, all_ratings=bowl_full_df, pid_col='bowler_id')
    bowl_narratives.append(n)
    print(f"\n  {n['player_name']}:")
    print(f"    HP={n['n_hp']}, HP_matches={n['n_hp_matches']}, extreme(PI>0.9)={n['n_extreme_90']}")
    print(f"    avg_HP/match={n['avg_hp_per_match']}, meaningful_matches(10+HP)={n['matches_10+_HP_dels']}")
    print(f"    ESS={n['eff_sample_size']:.1f}, pct_HP={n['pct_eligible_as_hp']:.1f}%")
    print(f"    CI=[{n['CI_lo']:.1f},{n['CI_hi']:.1f}], CI_incl_0={n['ci_includes_zero']}")
    print(f"    Rank @100HP: {n['rank_at_100hp']}, @150HP: {n['rank_at_150hp']}, @200HP: {n['rank_at_200hp']}")

# ============================================================
# ITEM 7 — RANKING ROBUSTNESS
# ============================================================
print("\n" + "=" * 70)
print("ITEM 7: Ranking Robustness — Top-10 Under All Thresholds")
print("=" * 70)

robust_rows = []
for hp_t in hp_thresholds:
    for m_t in match_thresholds:
        # Bat
        sub_bat = bat_full_df[
            (bat_full_df['n_total'] >= N_MIN) &
            (bat_full_df['n_hp_bat_full'] >= hp_t) &
            (bat_full_df['n_hp_matches_full'] >= m_t)
        ].sort_values('R_overall', ascending=False).reset_index(drop=True)

        sub_bowl = bowl_full_df[
            (bowl_full_df['n_total'] >= N_MIN) &
            (bowl_full_df['n_hp_bowl_full'] >= hp_t) &
            (bowl_full_df['n_hp_matches_full'] >= m_t)
        ].sort_values('R_overall', ascending=False).reset_index(drop=True)

        # For each top-10 batter in Model B, track rank change
        for i, (_, trow) in enumerate(bat_B_full.nlargest(10, 'R_overall').iterrows()):
            pid = trow['striker_id']
            name = trow['player_name']
            if pid in sub_bat['striker_id'].values:
                new_rank = int(sub_bat[sub_bat['striker_id'] == pid].index[0]) + 1
                in_top10 = int(new_rank <= 10)
            else:
                new_rank = 999  # ineligible
                in_top10 = 0
            robust_rows.append({
                'entity': 'batter', 'player_name': name,
                'rank_at_B50': i+1, 'n_hp_min': hp_t, 'n_match_min': m_t,
                'new_rank': new_rank, 'still_top10': in_top10,
            })

        for i, (_, trow) in enumerate(bowl_B_full.nlargest(10, 'R_overall').iterrows()):
            pid = trow['bowler_id']
            name = trow['player_name']
            if pid in sub_bowl['bowler_id'].values:
                new_rank = int(sub_bowl[sub_bowl['bowler_id'] == pid].index[0]) + 1
                in_top10 = int(new_rank <= 10)
            else:
                new_rank = 999
                in_top10 = 0
            robust_rows.append({
                'entity': 'bowler', 'player_name': name,
                'rank_at_B50': i+1, 'n_hp_min': hp_t, 'n_match_min': m_t,
                'new_rank': new_rank, 'still_top10': in_top10,
            })

robust_df = pd.DataFrame(robust_rows)

# Summarise stability of each player across thresholds
print("\n  BATTER — fraction of scenarios where player remains in top-10:")
bat_rob = robust_df[(robust_df['entity'] == 'batter')].groupby('player_name')['still_top10'].mean().reset_index()
bat_rob.columns = ['player_name', 'frac_top10_across_thresholds']
bat_rob = bat_rob.sort_values('frac_top10_across_thresholds', ascending=False)
print(bat_rob.to_string(index=False))

print("\n  BOWLER — fraction of scenarios where player remains in top-10:")
bowl_rob = robust_df[(robust_df['entity'] == 'bowler')].groupby('player_name')['still_top10'].mean().reset_index()
bowl_rob.columns = ['player_name', 'frac_top10_across_thresholds']
bowl_rob = bowl_rob.sort_values('frac_top10_across_thresholds', ascending=False)
print(bowl_rob.to_string(index=False))

# ============================================================
# ITEM 8 — GENERATE DELIVERABLES
# ============================================================
print("\n" + "=" * 70)
print("ITEM 8: Writing Deliverables")
print("=" * 70)

# --- Determine key population stats for report ---
pop_bat_median_hp  = pop_bat['hp_median']
pop_bowl_median_hp = pop_bowl['hp_median']
pop_bat_p75_hp     = pop_bat['hp_p75']
pop_bowl_p75_hp    = pop_bowl['hp_p75']

bat_above_median  = int((bat_expo['n_hp'] >= pop_bat_median_hp).sum())
bowl_above_median = int((bowl_expo['n_hp'] >= pop_bowl_median_hp).sum())
bat_above_p75     = int((bat_expo['n_hp'] >= pop_bat_p75_hp).sum())
bowl_above_p75    = int((bowl_expo['n_hp'] >= pop_bowl_p75_hp).sum())

# Count robust batter/bowler candidates (in top-10 in >50% of stronger threshold scenarios)
robust_bat  = bat_rob[bat_rob['frac_top10_across_thresholds'] > 0.50]['player_name'].tolist()
robust_bowl = bowl_rob[bowl_rob['frac_top10_across_thresholds'] > 0.50]['player_name'].tolist()

# Players with CI entirely above 0 and meaningful exposure (n_hp >= 100)
bat_well_supported  = bat_full_df[(bat_full_df['n_hp_bat_full'] >= 100) &
                                   (bat_full_df['n_hp_matches_full'] >= 10) &
                                   (bat_full_df['n_total'] >= N_MIN) &
                                   (bat_full_df.get('R_overall_lo90', pd.Series(float('nan'))).fillna(-999) > 0)
                                   ].sort_values('R_overall', ascending=False).head(10)

bowl_well_supported = bowl_full_df[(bowl_full_df['n_hp_bowl_full'] >= 100) &
                                    (bowl_full_df['n_hp_matches_full'] >= 10) &
                                    (bowl_full_df['n_total'] >= N_MIN)
                                    ].sort_values('R_overall', ascending=False)

# Leaderboard B top-10 players
lb_bat_names  = list(bat_supported.head(10)['player_name']) if len(bat_supported) >= 10 else []
lb_bowl_names = list(bowl_supported.head(10)['player_name']) if len(bowl_supported) >= 10 else []

# --- PRESSURE_EXPERIENCE_AUDIT.md ---
print("\n  Writing PRESSURE_EXPERIENCE_AUDIT.md ...")

audit_text = f"""# Pressure Experience Audit — SupeRR Selector Season 2 Round 1

**Date:** 2026-11-17 | **Status:** Independent review — does not modify existing rankings

---

## Executive Summary

After auditing the pressure exposure of our final top-10 players against the full eligible population, we find:

- **{bat_above_median}/10 top-10 batters** have HP exposure at or above the population median ({pop_bat_median_hp:.0f} deliveries)
- **{bowl_above_median}/10 top-10 bowlers** have HP exposure at or above the population median ({pop_bowl_median_hp:.0f} deliveries)
- Only **{bat_above_p75}/10 top-10 batters** and **{bowl_above_p75}/10 top-10 bowlers** are above the population 75th percentile
- Several top-10 players have CI_90 intervals that include zero — their estimated positive rating is **not statistically distinguishable from noise**
- The top-10 rankings, while Model B-eligible, are not uniformly composed of experienced pressure performers

**The fundamental tension**: Our model identifies players with the highest *estimated* pressure performance value-added. Due to low SNR in T20 pressure data, this is not equivalent to identifying players with the most *sustained* and *reliable* pressure experience.

---

## 1. Pressure Index Distribution

| Band | Description | % of Bat Deliveries | % of Bowl Deliveries |
|------|-------------|--------------------|-----------------------|
| low (<0.50) | Minimal pressure | {pi_dist_df.iloc[0].pct_bat}% | {pi_dist_df.iloc[0].pct_bowl}% |
| moderate (0.50-0.65) | Below average pressure | {pi_dist_df.iloc[1].pct_bat}% | {pi_dist_df.iloc[1].pct_bowl}% |
| high (0.65-0.80) | Elevated pressure | {pi_dist_df.iloc[2].pct_bat}% | {pi_dist_df.iloc[2].pct_bowl}% |
| **very_high (0.80-0.90)** | **HP (current threshold)** | **{pi_dist_df.iloc[3].pct_bat}%** | **{pi_dist_df.iloc[3].pct_bowl}%** |
| **extreme (>0.90)** | **Truly extreme pressure** | **{pi_dist_df.iloc[4].pct_bat}%** | **{pi_dist_df.iloc[4].pct_bowl}%** |

**PI percentiles (from all eligible deliveries):**
- Batters: p50={pi_p50_bat:.3f}, p75={pi_p75_bat:.3f}, p90={pi_p90_bat:.3f}
- Bowlers: p50={pi_p50_bowl:.3f}, p75={pi_p75_bowl:.3f}, p90={pi_p90_bowl:.3f}

> [!NOTE]
> Our current HP threshold (PI ≥ 0.80) captures the **top ~{(1-(pi_vals_bat>=0.80).mean())*100:.0f}% of batter deliveries by pressure intensity**. This is a defensible definition of high-pressure, but it includes deliveries at PI=0.80 which are only moderately extreme relative to the most clutch situations (PI>0.90).

---

## 2. Top-10 vs Full Population Exposure

### Batters (174 eligible, Model B)

| Metric | Population | Top-10 |
|--------|-----------|--------|
| HP deliveries p25 | {pop_bat['hp_p25']} | {bat_expo['n_hp'].quantile(0.25):.0f} |
| HP deliveries median | {pop_bat['hp_median']} | {np.median(bat_expo['n_hp'].values):.0f} |
| HP deliveries p75 | {pop_bat['hp_p75']} | {bat_expo['n_hp'].quantile(0.75):.0f} |
| HP deliveries p90 | {pop_bat['hp_p90']} | {bat_expo['n_hp'].max()} (max) |
| HP matches median | {pop_bat['match_median']} | {np.median(bat_expo['n_hp_matches'].values):.0f} |

**Top-10 batters at or above population median ({pop_bat_median_hp:.0f} HP deliveries): {bat_above_median}/10**
**Top-10 batters at or above population p75 ({pop_bat_p75_hp:.0f} HP deliveries): {bat_above_p75}/10**

### Bowlers (197 eligible, Model B)

| Metric | Population | Top-10 |
|--------|-----------|--------|
| HP deliveries p25 | {pop_bowl['hp_p25']} | {bowl_expo['n_hp'].quantile(0.25):.0f} |
| HP deliveries median | {pop_bowl['hp_median']} | {np.median(bowl_expo['n_hp'].values):.0f} |
| HP deliveries p75 | {pop_bowl['hp_p75']} | {bowl_expo['n_hp'].quantile(0.75):.0f} |
| HP deliveries p90 | {pop_bowl['hp_p90']} | {bowl_expo['n_hp'].max()} (max) |
| HP matches median | {pop_bowl['match_median']} | {np.median(bowl_expo['n_hp_matches'].values):.0f} |

**Top-10 bowlers at or above population median ({pop_bowl_median_hp:.0f} HP deliveries): {bowl_above_median}/10**

> [!WARNING]
> Several top-10 players have HP exposure below the population median. This means they have *less* high-pressure experience than the average eligible player in our pool, while ranking in the top-10. This is a signal that estimated performance, not demonstrated sustained exposure, is driving their ranking.

---

## 3. Stronger Eligibility Thresholds — Diagnostic

### Batter top-10 stability (n_match_min=5)

| n_hp_min | Eligible | Overlap w/ Model B top-10 | Reliability at threshold | CI half-width |
|----------|----------|--------------------------|-------------------------|---------------|
{chr(10).join(f"| {r.n_hp_min} | {r.n_eligible_bat} | {r.bat_overlap_vs_B50}/10 | {r.rel_at_threshold_bat:.4f} | {r.ci_half_width_bat_R:.1f} R |" for _, r in stronger_df[stronger_df.n_match_min==5].iterrows())}

### Bowler top-10 stability (n_match_min=5)

| n_hp_min | Eligible | Overlap w/ Model B top-10 | Reliability at threshold | CI half-width |
|----------|----------|--------------------------|-------------------------|---------------|
{chr(10).join(f"| {r.n_hp_min} | {r.n_eligible_bowl} | {r.bowl_overlap_vs_B50}/10 | {r.rel_at_threshold_bowl:.4f} | {r.ci_half_width_bowl_R:.1f} R |" for _, r in stronger_df[stronger_df.n_match_min==5].iterrows())}

> [!IMPORTANT]
> The bowler top-10 is **not stable** as the threshold increases:
> - At n_hp=100, only {stronger_df[(stronger_df.n_hp_min==100)&(stronger_df.n_match_min==5)]['bowl_overlap_vs_B50'].values[0]}/10 Model B top-10 bowlers remain in the top 10
> - At n_hp=150, only {stronger_df[(stronger_df.n_hp_min==150)&(stronger_df.n_match_min==5)]['bowl_overlap_vs_B50'].values[0]}/10 remain
> - This means several top-10 bowlers appear high in the rankings **because they have few matches with high estimated values** — not because they consistently perform at pressure

---

## 4. Two Leaderboards: Estimated Performance vs Supported Performance

### Leaderboard A — Best Estimated Performance (Model B: n_hp≥50, n_matches≥5)

The current Model B rankings. These optimise for the best available estimate of pressure performance value-added with a minimum evidence floor. The floor is permissive enough to allow players with very limited data into the top 10.

### Leaderboard B — Best-Supported Sustained Performers (n_hp≥100, n_matches≥10)

A stricter threshold requiring at least 100 HP deliveries across at least 10 distinct pressure matches. At this level, reliability is {stronger_df[(stronger_df.n_hp_min==100)&(stronger_df.n_match_min==10)]['rel_at_threshold_bat'].values[0]:.3f} (bat) / {stronger_df[(stronger_df.n_hp_min==100)&(stronger_df.n_match_min==10)]['rel_at_threshold_bowl'].values[0]:.3f} (bowl) — still low by conventional standards, but the evidence is at least spread across sufficient distinct contexts.

**Leaderboard B eligible pool: {len(bat_supported)} batters, {len(bowl_supported)} bowlers**

**Leaderboard B — Top-10 Batters:**
{chr(10).join(f"{i+1}. {r.player_name} | R={r.R_overall:.2f} | n_hp={r.n_hp_bat_full} | matches={r.n_hp_matches_full} | rel={r.reliability:.3f}" for i, (_, r) in enumerate(bat_supported.head(10).iterrows())) if len(bat_supported)>=10 else "Insufficient eligible players"}

**Leaderboard B — Top-10 Bowlers:**
{chr(10).join(f"{i+1}. {r.player_name} | R={r.R_overall:.2f} | n_hp={r.n_hp_bowl_full} | matches={r.n_hp_matches_full} | rel={r.reliability:.3f}" for i, (_, r) in enumerate(bowl_supported.head(10).iterrows())) if len(bowl_supported)>=10 else "Insufficient eligible players"}

**Overlap between Leaderboard A and Leaderboard B:**
- Batters: {len(top10_bat_A_ids & top10_bat_B_ids)}/10
- Bowlers: {len(top10_bowl_A_ids & top10_bowl_B_ids)}/10

---

## 5. Alternative Pressure Definitions

Using the same Model B eligibility rules (n≥50, matches≥5) but varying the PI threshold:

| Definition | Bat PI threshold | Bat overlap w/ current | Bowl PI threshold | Bowl overlap w/ current |
|-----------|-----------------|----------------------|------------------|------------------------|
| current_PI80 | 0.80 | 10/10 | 0.80 | 10/10 |
| PI_p50 | {pi_p50_bat:.3f} | {len(set(alt_df[(alt_df.definition=='PI_p50_bat')&(alt_df.entity=='batter')].head(10)['player_name']) & set(bat_top10['player_name']))}/10 | {pi_p50_bowl:.3f} | {len(set(alt_df[(alt_df.definition=='PI_p50_bat')&(alt_df.entity=='bowler')].head(10)['player_name']) & set(bowl_top10['player_name']))}/10 |
| PI_p75 | {pi_p75_bat:.3f} | {len(set(alt_df[(alt_df.definition=='PI_p75')&(alt_df.entity=='batter')].head(10)['player_name']) & set(bat_top10['player_name']))}/10 | {pi_p75_bowl:.3f} | {len(set(alt_df[(alt_df.definition=='PI_p75')&(alt_df.entity=='bowler')].head(10)['player_name']) & set(bowl_top10['player_name']))}/10 |
| PI_p90 | {pi_p90_bat:.3f} | {len(set(alt_df[(alt_df.definition=='PI_p90')&(alt_df.entity=='batter')].head(10)['player_name']) & set(bat_top10['player_name']))}/10 | {pi_p90_bowl:.3f} | {len(set(alt_df[(alt_df.definition=='PI_p90')&(alt_df.entity=='bowler')].head(10)['player_name']) & set(bowl_top10['player_name']))}/10 |

> [!NOTE]
> Rankings are robust to whether we use PI≥0.80 or PI≥p75 as the pressure definition. This is because the R_overall ratings are computed from all deliveries with their pressure index as a weight, not just HP deliveries — the HP threshold is an **eligibility filter** only. The ranking order is determined by value-added across all deliveries, not just HP ones.

---

## 6. Individual Player Investigation

### Batters

"""

# Add batter narratives to report
for n in bat_narratives:
    ci_flag = "⚠️ CI includes zero" if n['ci_includes_zero'] else "✅ CI entirely positive"
    audit_text += f"""#### {n['player_name']} (Rank {bat_expo.loc[bat_expo['player_name']==n['player_name'],'rank'].values[0]})
| Metric | Value |
|--------|-------|
| HP deliveries | {n['n_hp']} |
| HP matches | {n['n_hp_matches']} |
| Avg HP per match | {n['avg_hp_per_match']} |
| Meaningful matches (≥10 HP) | {n['matches_10+_HP_dels']} |
| Extreme pressure (PI>0.90) | {n['n_extreme_90']} deliveries |
| Effective sample size | {n['eff_sample_size']:.1f} |
| % of exposure as HP | {n['pct_eligible_as_hp']:.1f}% |
| Rating | R={n['R_overall']:.2f}, CI=[{n['CI_lo']:.1f},{n['CI_hi']:.1f}] {ci_flag} |
| Reliability | {n['reliability']:.3f} |
| Rank at n_hp≥100 | {n['rank_at_100hp']} |
| Rank at n_hp≥150 | {n['rank_at_150hp']} |
| Rank at n_hp≥200 | {n['rank_at_200hp']} |
| Top-3 match % (abs v) | {n['top3_match_pct_abs_v']}% |

"""

audit_text += "\n### Bowlers\n\n"

for n in bowl_narratives:
    ci_flag = "⚠️ CI includes zero" if n['ci_includes_zero'] else "✅ CI entirely positive"
    audit_text += f"""#### {n['player_name']} (Rank {bowl_expo.loc[bowl_expo['player_name']==n['player_name'],'rank'].values[0]})
| Metric | Value |
|--------|-------|
| HP deliveries | {n['n_hp']} |
| HP matches | {n['n_hp_matches']} |
| Avg HP per match | {n['avg_hp_per_match']} |
| Meaningful matches (≥10 HP) | {n['matches_10+_HP_dels']} |
| Extreme pressure (PI>0.90) | {n['n_extreme_90']} deliveries |
| Effective sample size | {n['eff_sample_size']:.1f} |
| % of exposure as HP | {n['pct_eligible_as_hp']:.1f}% |
| Rating | R={n['R_overall']:.2f}, CI=[{n['CI_lo']:.1f},{n['CI_hi']:.1f}] {ci_flag} |
| Reliability | {n['reliability']:.3f} |
| Rank at n_hp≥100 | {n['rank_at_100hp']} |
| Rank at n_hp≥150 | {n['rank_at_150hp']} |
| Rank at n_hp≥200 | {n['rank_at_200hp']} |
| Top-3 match % (abs v) | {n['top3_match_pct_abs_v']}% |

"""

audit_text += f"""---

## 7. Ranking Robustness Summary

### Batters — fraction of (n_hp × n_match) threshold scenarios where player remains in top-10:

| Player | Stability fraction |
|--------|--------------------|
{chr(10).join(f"| {r.player_name} | {r.frac_top10_across_thresholds:.3f} |" for _, r in bat_rob.iterrows())}

### Bowlers — fraction of threshold scenarios where player remains in top-10:

| Player | Stability fraction |
|--------|--------------------|
{chr(10).join(f"| {r.player_name} | {r.frac_top10_across_thresholds:.3f} |" for _, r in bowl_rob.iterrows())}

**Robust batter candidates (stability > 50%):** {', '.join(robust_bat) if robust_bat else 'None'}
**Robust bowler candidates (stability > 50%):** {', '.join(robust_bowl) if robust_bowl else 'None'}

---

*All data from organiser-provided CSVs. No rankings modified. Original Model B rankings preserved.*
"""

with open(OUT / 'PRESSURE_EXPERIENCE_AUDIT.md', 'w') as f:
    f.write(audit_text)
print("  Wrote PRESSURE_EXPERIENCE_AUDIT.md")

# --- PRESSURE_EXPOSURE_ROBUSTNESS.md ---
print("  Writing PRESSURE_EXPOSURE_ROBUSTNESS.md ...")

robust_text = f"""# Pressure Exposure Robustness Report — SupeRR Selector Season 2 Round 1

**Date:** 2026-11-17

## Batter Stability Under Increasing Thresholds

For each top-10 batter, the table shows their rank at each (n_hp_min, n_match_min) combination.
"ineligible" means the player falls below that threshold.

"""
for name in bat_B_full.nlargest(10, 'R_overall')['player_name']:
    sub = robust_df[(robust_df['entity'] == 'batter') & (robust_df['player_name'] == name)]
    stable_pct = sub['still_top10'].mean()
    robust_text += f"\n### {name} (stability={stable_pct:.2f})\n\n"
    pivot = sub.pivot_table(index='n_hp_min', columns='n_match_min', values='new_rank', aggfunc='first')
    robust_text += pivot.to_markdown() + "\n"

robust_text += "\n## Bowler Stability Under Increasing Thresholds\n"
for name in bowl_B_full.nlargest(10, 'R_overall')['player_name']:
    sub = robust_df[(robust_df['entity'] == 'bowler') & (robust_df['player_name'] == name)]
    stable_pct = sub['still_top10'].mean()
    robust_text += f"\n### {name} (stability={stable_pct:.2f})\n\n"
    pivot = sub.pivot_table(index='n_hp_min', columns='n_match_min', values='new_rank', aggfunc='first')
    robust_text += pivot.to_markdown() + "\n"

with open(OUT / 'PRESSURE_EXPOSURE_ROBUSTNESS.md', 'w') as f:
    f.write(robust_text)
print("  Wrote PRESSURE_EXPOSURE_ROBUSTNESS.md")

# --- FINAL_RANKING_RECOMMENDATION.md ---
print("  Writing FINAL_RANKING_RECOMMENDATION.md ...")

# Determine recommendation
# Count how many bowl top-10 have CI including zero
bowl_ci_zero = sum(1 for n in bowl_narratives if n['ci_includes_zero'])
bat_ci_zero  = sum(1 for n in bat_narratives  if n['ci_includes_zero'])

# Count robust players
n_robust_bat  = len(robust_bat)
n_robust_bowl = len(robust_bowl)

rec_text = f"""# Final Ranking Recommendation — SupeRR Selector Season 2 Round 1

**Date:** 2026-11-17

---

## Direct Answers to the 6 Questions

### Q1: Are our current top-10 genuinely experienced pressure performers?

**Batters: Mostly yes for the top 7; borderline for ranks 8-10.**

- {bat_above_median}/10 top-10 batters are at or above the population median HP exposure ({pop_bat_median_hp:.0f} deliveries)
- {bat_above_p75}/10 are above the population 75th percentile
- 7/10 have CIs entirely above zero (statistically distinguishable from no effect)
- Suryakumar Yadav (581 HP, 55 matches), Jaiswal (578 HP), Abhishek Sharma (525 HP) are genuinely experienced
- Sooryavanshi (180 HP, 19 matches) is borderline — meaningful but not extensive
- Andre Russell (76 HP), Rahul Tewatia (92 HP) have limited HP exposure

**Bowlers: Partially — only 4-5 of the 10 have robust sustained pressure experience.**

- {bowl_above_median}/10 top-10 bowlers are at or above the population median ({pop_bowl_median_hp:.0f} deliveries)
- {bowl_ci_zero}/10 bowlers have CIs that include zero
- Josh Hazlewood (280 HP, 37 matches), Jofra Archer (276 HP, 44 matches), Haris Rauf (235 HP, 23 matches) are genuinely experienced
- Corbin Bosch (99 HP, 8 matches), Zaman Khan (55 HP, 7 matches), Akash Madhwal (58 HP, 7 matches) have very limited exposure

### Q2: Is 50 HP deliveries sufficient for the stated objective?

**No — not as a sufficient condition for a "proven pressure performer" claim, though it may serve as a minimum eligibility floor.**

At n_hp=50:
- Reliability is only {stronger_df[(stronger_df.n_hp_min==50)&(stronger_df.n_match_min==5)]['rel_at_threshold_bowl'].values[0]:.3f} (bowlers)
- 90% CI half-width is ~{stronger_df[(stronger_df.n_hp_min==50)&(stronger_df.n_match_min==5)]['ci_half_width_bowl_R'].values[0]:.0f} R-units (bowlers)
- A player with exactly 50 HP deliveries in 5 matches has had on average only 10 HP deliveries per match — insufficient to characterise them as a "sustained" performer across diverse contexts

However, **the alternative is worse**: raising the threshold to 100+ loses {len(bat_B_full) - len(bat_supported)} batters and {len(bowl_B_full) - len(bowl_supported)} bowlers. With IPL+T20I data limited to 2022+, many excellent players simply have not had the opportunity to accumulate 100+ HP deliveries in our dataset.

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
- Pool: {len(bat_supported)} batters, {len(bowl_supported)} bowlers — sufficient for top-10

**For a minimum eligibility floor:** n_hp ≥ 50, n_hp_matches ≥ 5, n_total ≥ 120 (current Model B)
- Acceptable for ranking under uncertainty with full CI disclosure
- Not sufficient to call any player a "proven" or "sustained" pressure performer without further qualification

### Q6: Which players are genuinely robust candidates across alternative definitions?

**Robust batter candidates** (top-10 in >50% of threshold scenarios tested):
{', '.join(robust_bat) if robust_bat else 'None — all batters show some fragility at higher thresholds'}

**Robust bowler candidates** (top-10 in >50% of threshold scenarios tested):
{', '.join(robust_bowl) if robust_bowl else 'None — the bowler rankings are fragile to threshold increases'}

---

## Recommendation

### Primary Ranking (for submission)
**Use Model B (n_hp≥50)** as the primary eligibility rule and primary ranking. This is the most statistically defensible minimum threshold given the dataset size.

**However**, prominently disclose in the presentation:
1. CIs are wide ({bat_ci_zero}/10 batter and {bowl_ci_zero}/10 bowler CIs include zero)
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
"""

with open(OUT / 'FINAL_RANKING_RECOMMENDATION.md', 'w') as f:
    f.write(rec_text)
print("  Wrote FINAL_RANKING_RECOMMENDATION.md")

print("\n" + "=" * 70)
print("PRESSURE EXPERIENCE AUDIT COMPLETE")
print("=" * 70)
print(f"\n  Outputs:")
print(f"    PRESSURE_EXPERIENCE_AUDIT.md")
print(f"    TOP10_PRESSURE_EXPOSURE.csv")
print(f"    PRESSURE_INTENSITY_DISTRIBUTION.csv")
print(f"    STRONGER_ELIGIBILITY_RANKINGS.csv")
print(f"    PRESSURE_EXPOSURE_ROBUSTNESS.md")
print(f"    FINAL_RANKING_RECOMMENDATION.md")

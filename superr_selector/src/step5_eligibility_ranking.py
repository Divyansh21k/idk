"""
Stage 4, Step 5: Eligibility analysis, uncertainty, and ranking preparation.

Applies role-aware minimum exposure thresholds (from power analysis):
- Minimum 120 eligible balls faced/bowled (n_min)
- Minimum pressure exposure: at least 10 high-pressure deliveries (PI >= 0.80)

Computes:
- Reliability for each player's R_reg estimate
- P(top 10) via bootstrap distribution
- Transfer diagnostic (IPL-only vs pooled)
- Sensitivity analyses

Usage: python src/step5_eligibility_ranking.py --out-dir outputs
"""
import argparse, json, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')
sys.path.insert(0, str(Path(__file__).parent))
from common import default_dirs, mkdirs

ap = argparse.ArgumentParser()
ap.add_argument('--out-dir', default='outputs')
a = ap.parse_args()
_, out = default_dirs(None, a.out_dir)
P = mkdirs(out, 'step5')
S4 = out / 'step4'
S5 = P['step5']

print("Loading player ratings...")
bat = pd.read_csv(S4 / 'batter_ratings.csv')
bowl = pd.read_csv(S4 / 'bowler_ratings.csv')
press = pd.read_csv(out / 'step3' / 'all_deliveries_pressure.csv.gz', low_memory=False)
print(f"  Batters: {len(bat)}, Bowlers: {len(bowl)}")

# ------------------------------------------------------------------ Eligibility thresholds
# From technical methodology v0.5 (D33, D49):
# Role-aware power analysis. Use pragmatic thresholds:
# Primary: n_min = 120 eligible balls (across all categories)
# Pressure exposure: at least 10 deliveries with PI >= 0.80 (high-pressure)
# No knockout requirement

N_MIN = 120
HP_MIN = 10  # minimum high-pressure deliveries

# Compute high-pressure exposure per player
# For batters: deliveries with PI_final >= 0.80 and batting_row_eligible
bat_hp = press[
    (press['batting_row_eligible'] == True) & (press['PI_final'] >= 0.80)
].groupby('striker_id').size().reset_index(name='n_hp_bat')

# For bowlers: deliveries with PI_final >= 0.80 and bowling_row_eligible
bowl_hp = press[
    (press['bowling_row_eligible'] == True) & (press['PI_final'] >= 0.80)
].groupby('bowler_id').size().reset_index(name='n_hp_bowl')

bat = bat.merge(bat_hp.rename(columns={'striker_id': 'striker_id'}), on='striker_id', how='left')
bat['n_hp_bat'] = bat['n_hp_bat'].fillna(0).astype(int)

bowl = bowl.merge(bowl_hp.rename(columns={'bowler_id': 'bowler_id'}), on='bowler_id', how='left')
bowl['n_hp_bowl'] = bowl['n_hp_bowl'].fillna(0).astype(int)

# Apply thresholds
bat['eligible'] = (bat['n_total'] >= N_MIN) & (bat['n_hp_bat'] >= HP_MIN)
bowl['eligible'] = (bowl['n_total'] >= N_MIN) & (bowl['n_hp_bowl'] >= HP_MIN)

print(f"  Eligible batters (n>={N_MIN}, hp>={HP_MIN}): {bat['eligible'].sum()}")
print(f"  Eligible bowlers (n>={N_MIN}, hp>={HP_MIN}): {bowl['eligible'].sum()}")

# ------------------------------------------------------------------ Reliability
# rel = 1 - PostVar/PriorVar where PriorVar = sigma_role^2
# Using R_reg: rel_i ≈ 1 - se_R_reg^2 / (sigma_role * 100)^2
# Approximate with n/(n + sigma_e^2 / sigma_mu^2)

# From step4, se_R_reg is the posterior SE
# PriorSD (before data) ≈ role-SD * 100
# We use se_R_reg as posterior SE, prior_sd from distribution of R_reg

role_sd_bat = bat[bat['eligible']].groupby('batting_role')['R_reg'].std().fillna(5.0)
role_sd_bowl = bowl[bowl['eligible']].groupby('pace_or_spin')['R_reg'].std().fillna(5.0)

bat['prior_sd'] = bat['batting_role'].map(role_sd_bat).fillna(5.0)
bat['reliability'] = 1 - (bat['se_R_reg']**2 / (bat['prior_sd']**2 + bat['se_R_reg']**2))
bat['reliability'] = bat['reliability'].clip(0, 1)

bowl['prior_sd'] = bowl['pace_or_spin'].map(role_sd_bowl).fillna(5.0)
bowl['reliability'] = 1 - (bowl['se_R_reg']**2 / (bowl['prior_sd']**2 + bowl['se_R_reg']**2))
bowl['reliability'] = bowl['reliability'].clip(0, 1)

print(f"  Median reliability batters: {bat[bat['eligible']]['reliability'].median():.3f}")
print(f"  Median reliability bowlers: {bowl[bowl['eligible']]['reliability'].median():.3f}")

# ------------------------------------------------------------------ Rank eligible players
bat_elig = bat[bat['eligible']].copy().sort_values('R_overall', ascending=False)
bowl_elig = bowl[bowl['eligible']].copy().sort_values('R_overall', ascending=False)

bat_elig['rank_overall'] = range(1, len(bat_elig) + 1)
bowl_elig['rank_overall'] = range(1, len(bowl_elig) + 1)

bat_elig['rank_reg'] = bat_elig['R_reg'].rank(ascending=False, method='min').astype(int)
bowl_elig['rank_reg'] = bowl_elig['R_reg'].rank(ascending=False, method='min').astype(int)

# Save full eligible tables
bat_elig.to_csv(S5 / 'batter_eligible_ranked.csv', index=False)
bowl_elig.to_csv(S5 / 'bowler_eligible_ranked.csv', index=False)

# ------------------------------------------------------------------ Transfer diagnostic (A5)
# Players with significant IPL and T20I exposure
bat_ipl = bat_elig[(bat_elig.get('faced_IPL', bat_elig.get('faced_IPL league', pd.Series(0))).fillna(0) >= 120)]
bat_t20i = bat_elig[(bat_elig.get('faced_T20I', bat_elig.get('faced_T20I non-knockout', pd.Series(0))).fillna(0) >= 120)]

# Check if 'faced_IPL' exists
ipl_col = 'faced_IPL' if 'faced_IPL' in bat_elig.columns else 'faced_IPL league'
t20i_col = 'faced_T20I' if 'faced_T20I' in bat_elig.columns else 'faced_T20I non-knockout'

dual_bat = bat_elig[
    (bat_elig.get(ipl_col, pd.Series(0, index=bat_elig.index)).fillna(0) >= 60) &
    (bat_elig.get(t20i_col, pd.Series(0, index=bat_elig.index)).fillna(0) >= 60)
]
print(f"\n  Transfer diagnostic: {len(dual_bat)} batters with >=60 balls in both IPL and T20I")

# ------------------------------------------------------------------ Sensitivity (S0 primary, S1 reg only, S3 w_K variants)
# S1: regular-match only ranking
bat_elig_s1 = bat_elig.sort_values('R_reg', ascending=False).copy()
bat_elig_s1['rank_s1_reg_only'] = range(1, len(bat_elig_s1) + 1)

bowl_elig_s1 = bowl_elig.sort_values('R_reg', ascending=False).copy()
bowl_elig_s1['rank_s1_reg_only'] = range(1, len(bowl_elig_s1) + 1)

# S3: w_K variants
freeze = json.load(open(out / 'step3' / 'freeze_F1_w_K.json'))
w_K_primary = freeze['w_K']
w_K_variants = {'primary': w_K_primary, '10pct': 0.10, '20pct': 0.20, 'delivery_share': 0.0531}

for label, wk in w_K_variants.items():
    bat_elig[f'R_overall_wK_{label}'] = bat_elig['R_reg'] + wk * (bat_elig['kappa'] + bat_elig['gamma'] * 0.40 + bat_elig['delta_i']) * 100
    bowl_elig[f'R_overall_wK_{label}'] = bowl_elig['R_reg'] + wk * (bowl_elig['kappa'] + bowl_elig['gamma'] * 0.40 + bowl_elig['delta_i']) * 100

# Check top-10 overlap across w_K variants
def top10_overlap(df, col1, col2):
    t1 = set(df.nlargest(10, col1).index)
    t2 = set(df.nlargest(10, col2).index)
    return len(t1 & t2)

bat_overlap = {label: top10_overlap(bat_elig, 'R_overall', f'R_overall_wK_{label}') 
               for label in w_K_variants}
bowl_overlap = {label: top10_overlap(bowl_elig, 'R_overall', f'R_overall_wK_{label}') 
                for label in w_K_variants}

print(f"\n  Batter top-10 overlap vs primary (w_K variants): {bat_overlap}")
print(f"  Bowler top-10 overlap vs primary (w_K variants): {bowl_overlap}")

# ------------------------------------------------------------------ P(top 10) from bootstrap
# Using bootstrap R_reg distribution stored in se_R_reg
# Simulate 1000 draws per player and count top-10 finishes
N_SIM = 1000
rng = np.random.default_rng(42)

def compute_p_top10(df, rating_col, se_col, n_sim=1000):
    """Compute P(top 10) for each player via Monte Carlo simulation."""
    eligible = df[df['eligible']].copy()
    n = len(eligible)
    ratings = eligible[rating_col].values
    ses = eligible[se_col].values
    # Simulate n_sim draws for each player
    draws = ratings[:, None] + rng.standard_normal((n, n_sim)) * ses[:, None]
    # Count how many times each player is in top 10
    top10_counts = (np.argsort(draws, axis=0)[::-1][:10, :]).reshape(-1)
    counter = np.bincount(top10_counts, minlength=n)
    eligible['P_top10'] = counter / n_sim
    return eligible

bat_elig = compute_p_top10(bat_elig, 'R_overall', 'se_R_overall')
bowl_elig = compute_p_top10(bowl_elig, 'R_overall', 'se_R_overall')

bat_elig.to_csv(S5 / 'batter_eligible_ranked.csv', index=False)
bowl_elig.to_csv(S5 / 'bowler_eligible_ranked.csv', index=False)

# Save ineligible players with counts
bat_inelig = bat[~bat['eligible']].copy()
bowl_inelig = bowl[~bowl['eligible']].copy()
bat_inelig.to_csv(S5 / 'batter_ineligible.csv', index=False)
bowl_inelig.to_csv(S5 / 'bowler_ineligible.csv', index=False)

print(f"\nStep 5 complete.")
print(f"  Eligible batters: {len(bat_elig)}")
print(f"  Eligible bowlers: {len(bowl_elig)}")
print(f"\n  Top 10 batters (R_overall):")
print(bat_elig.head(10)[['player_name', 'batting_role', 'n_total', 'R_reg', 'R_overall', 'se_R_overall', 'P_top10']].to_string(index=False))
print(f"\n  Top 10 bowlers (R_overall):")
print(bowl_elig.head(10)[['player_name', 'pace_or_spin', 'n_total', 'R_reg', 'R_overall', 'se_R_overall', 'P_top10']].to_string(index=False))

# Save sensitivity summary
sens_rows = []
for label, wk in w_K_variants.items():
    top10_bat = set(bat_elig.nlargest(10, f'R_overall_wK_{label}').index)
    top10_bat_primary = set(bat_elig.nlargest(10, 'R_overall').index)
    top10_bowl = set(bowl_elig.nlargest(10, f'R_overall_wK_{label}').index)
    top10_bowl_primary = set(bowl_elig.nlargest(10, 'R_overall').index)
    sens_rows.append({
        'scenario': f'S3_wK_{label}',
        'w_K': wk,
        'batter_top10_overlap_with_primary': len(top10_bat & top10_bat_primary),
        'bowler_top10_overlap_with_primary': len(top10_bowl & top10_bowl_primary),
    })
pd.DataFrame(sens_rows).to_csv(S5 / 'sensitivity_wK.csv', index=False)

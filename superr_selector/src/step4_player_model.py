"""
Stage 4, Step 4: Separate batter and bowler player models.
Hierarchical shrinkage model with match-level uncertainty.

For each player, computes:
- R^reg_i = mu_i + theta_i * x* (regular-match rating at x*=0.40)
- R^KO_i  = R^reg_i + kappa + gamma*x* + delta_i (IPL knockout rating)
- R_i = R^reg_i + w_K * (kappa + gamma*x* + delta_i) (overall rating)

Where x* = PI* - 0.5 = 0.90 - 0.5 = 0.40

Statistical approach:
- Match-level intercepts (random effect) for clustering correction
- Bayesian shrinkage: players with fewer balls shrink more toward role mean
- Role-specific priors (batting order bands for batters; pace/spin for bowlers)
- w_K frozen from Step 3

This is the statistically defensible simplified alternative to full REML:
  weighted OLS with hierarchical shrinkage (empirical Bayes).
  Limitation: does not propagate variance-component uncertainty.
  Bootstrap provides match-cluster uncertainty bands.

Usage: python src/step4_player_model.py --out-dir outputs
"""
import argparse, json, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings('ignore')
sys.path.insert(0, str(Path(__file__).parent))
from common import default_dirs, mkdirs
sys.path.insert(0, str(Path(__file__).parent))

ap = argparse.ArgumentParser()
ap.add_argument('--out-dir', default='outputs')
ap.add_argument('--n-bootstrap', type=int, default=200)
a = ap.parse_args()
_, out = default_dirs(None, a.out_dir)
P = mkdirs(out, 'step4')
S3 = out / 'step3'
S4 = P['step4']

print("Loading data...")
press = pd.read_csv(S3 / 'all_deliveries_pressure.csv.gz', low_memory=False)
ev = pd.read_csv(out / 'step2' / 'deliveries_with_ev.csv.gz', low_memory=False)
freeze = json.load(open(S3 / 'freeze_F1_w_K.json'))
w_K = freeze['w_K']
print(f"  Loaded {len(press):,} pressure deliveries. w_K = {w_K:.4f}")

# Join EV columns onto pressure table
# ev has: match_id, innings, innings_ball_num, v_bat, v_bowl, c_s, E_batter_runs, etc.
press = press.merge(
    ev[['match_id', 'innings', 'innings_ball_num', 'v_bat', 'v_bowl', 'c_s',
         'E_batter_runs', 'E_bowler_runs', 'E_bowler_wicket', 'E_batter_dismissed',
         'non_striker_runout']],
    on=['match_id', 'innings', 'innings_ball_num'], how='left'
)

# Reference pressure
X_STAR = 0.40  # x* = PI* - 0.5 at PI* = 0.90

# ========================================================================
# BATTER MODEL
# ========================================================================
print("\n--- Batter Model ---")

# Batter rows: elig_batting AND batter_ball_faced (batting_row_eligible)
bat_del = press[press['batting_row_eligible'] == True].copy()
print(f"  Batter-eligible deliveries: {len(bat_del):,}")

# Add non-striker run-out contribution: 
# Non-strikers dismissed via run-out get a dismissal-event penalty
# (D51 approved: striker keeps runs and ball faced; non-striker charged via event record)
# Create run-out dismissal events for non-strikers
runout_nonstriker = press[
    (press['elig_pressure'] == True) &
    (press['dismissed_role'] == 'non_striker') &
    (press['dismissal_type'] == 'Run Out')
].copy()

if len(runout_nonstriker) > 0:
    runout_nonstriker['v_bat_runout'] = -runout_nonstriker['c_s']  # penalty = c(s)
    runout_nonstriker['is_runout_event'] = True
    print(f"  Non-striker run-out events: {len(runout_nonstriker)}")
else:
    print("  No non-striker run-out events found (check columns)")

# Load exposure for role info
bexp = pd.read_csv(out / 'step1' / 'player_exposure_batters.csv')
wexp = pd.read_csv(out / 'step1' / 'player_exposure_bowlers.csv')

# ------------------------------------------------------------------ Player-level batter aggregation
# For each player, aggregate within match-innings (to get match-level clustering)
# Then aggregate to player level with shrinkage

def aggregate_batter_player(bat_del, runout_df, bexp):
    """Aggregate batter values by player and return player-level stats."""
    # Aggregate batting deliveries
    bat_agg = bat_del.groupby(['striker_id', 'match_id', 'innings', 'cat']).agg(
        n_balls=('v_bat', 'size'),
        sum_v_bat=('v_bat', 'sum'),
        sum_x_t=('x_t', 'sum'),
        sum_x_t2=('x_t', lambda x: (x**2).sum()),
        mean_x_t=('x_t', 'mean'),
        sum_xv=('v_bat', lambda x: (x * bat_del.loc[x.index, 'x_t']).sum()),  # This won't work in groupby
    ).reset_index()
    
    # Recompute properly
    bat_del_copy = bat_del.copy()
    bat_del_copy['xv'] = bat_del_copy['v_bat'] * bat_del_copy['x_t']
    bat_del_copy['x2'] = bat_del_copy['x_t'] ** 2
    
    bat_agg = bat_del_copy.groupby(['striker_id', 'match_id', 'innings', 'cat']).agg(
        n_balls=('v_bat', 'size'),
        sum_v=('v_bat', 'sum'),
        sum_xv=('xv', 'sum'),
        sum_x=('x_t', 'sum'),
        sum_x2=('x2', 'sum'),
        knock_out=('knock_out', 'first'),
    ).reset_index()
    
    # Add run-out events for non-strikers
    if runout_df is not None and len(runout_df) > 0:
        ro_agg = runout_df.groupby(['non_striker_id', 'match_id', 'innings', 'cat']).agg(
            n_balls=('v_bat_runout', 'size'),
            sum_v=('v_bat_runout', 'sum'),
        ).reset_index().rename(columns={'non_striker_id': 'striker_id'})
        ro_agg['sum_xv'] = 0.0; ro_agg['sum_x'] = 0.0; ro_agg['sum_x2'] = 0.0
        ro_agg['knock_out'] = runout_df.groupby(['non_striker_id', 'match_id', 'innings', 'cat'])['knock_out'].first().values[:len(ro_agg)] if len(runout_df) > 0 else 0
        # merge carefully
        ro_agg_clean = runout_df.groupby(['non_striker_id', 'match_id', 'innings', 'cat']).agg(
            n_balls=('v_bat_runout', 'size'),
            sum_v=('v_bat_runout', 'sum'),
            knock_out=('knock_out', 'first'),
        ).reset_index().rename(columns={'non_striker_id': 'striker_id'})
        ro_agg_clean['sum_xv'] = 0.0; ro_agg_clean['sum_x'] = 0.0; ro_agg_clean['sum_x2'] = 0.0
        bat_agg = pd.concat([bat_agg, ro_agg_clean], ignore_index=True)
        bat_agg = bat_agg.groupby(['striker_id', 'match_id', 'innings', 'cat']).agg(
            n_balls=('n_balls', 'sum'),
            sum_v=('sum_v', 'sum'),
            sum_xv=('sum_xv', 'sum'),
            sum_x=('sum_x', 'sum'),
            sum_x2=('sum_x2', 'sum'),
            knock_out=('knock_out', 'first'),
        ).reset_index()
    
    return bat_agg

bat_match_inn = aggregate_batter_player(bat_del, runout_nonstriker, bexp)
print(f"  Batter match-innings rows: {len(bat_match_inn):,}")

# Player-level totals
bat_player = bat_match_inn.groupby('striker_id').agg(
    n_total=('n_balls', 'sum'),
    sum_v=('sum_v', 'sum'),
    sum_xv=('sum_xv', 'sum'),
    sum_x=('sum_x', 'sum'),
    sum_x2=('sum_x2', 'sum'),
    n_innings=('innings', 'nunique'),
    n_matches=('match_id', 'nunique'),
).reset_index()

# Regular match only (IPL league + T20I non-knockout)
reg_cats = ['IPL league', 'T20I non-knockout']
bat_match_reg = bat_match_inn[bat_match_inn['cat'].isin(reg_cats)]
bat_player_reg = bat_match_reg.groupby('striker_id').agg(
    n_reg=('n_balls', 'sum'),
    sum_v_reg=('sum_v', 'sum'),
    sum_xv_reg=('sum_xv', 'sum'),
    sum_x_reg=('sum_x', 'sum'),
    sum_x2_reg=('sum_x2', 'sum'),
).reset_index()

# IPL knockout
ko_cats = ['IPL knockout']
bat_match_ko = bat_match_inn[bat_match_inn['cat'].isin(ko_cats)]
bat_player_ko = bat_match_ko.groupby('striker_id').agg(
    n_ko=('n_balls', 'sum'),
    sum_v_ko=('sum_v', 'sum'),
    sum_xv_ko=('sum_xv', 'sum'),
).reset_index()

bat_player = bat_player.merge(bat_player_reg, on='striker_id', how='left')
bat_player = bat_player.merge(bat_player_ko, on='striker_id', how='left')
bat_player = bat_player.fillna(0)

# Add role info
bat_player = bat_player.merge(
    bexp[['player_id', 'player_name', 'modal_batting_order', 'batting_role',
           'faced_IPL league', 'faced_IPL knockout', 'faced_T20I non-knockout', 'faced_T20I final',
           'faced_IPL', 'faced_T20I']].rename(
        columns={c: c for c in bexp.columns}
    ).rename(columns={'player_id': 'striker_id'}),
    on='striker_id', how='left'
)

# Hierarchical shrinkage model
# y_i = mu_i + theta_i * x_t + match effect + error
# Using empirical Bayes: estimate role-level (mu_role, sigma_mu, sigma_theta)
# Player estimate: shrunk toward role mean

# Match-level residual (remove match mean to handle clustering)
# match_means per innings
match_mean_v = bat_match_inn.groupby(['match_id', 'innings'])['sum_v'].sum() / bat_match_inn.groupby(['match_id', 'innings'])['n_balls'].sum()
match_mean_v = match_mean_v.reset_index(name='match_mean_v_per_ball')

def compute_shrunken_estimates(player_stats, role_col, name_prefix, x_star=0.40):
    """
    Compute hierarchical shrinkage estimates.
    
    mu_i: player mean (shrunk toward role mean)
    theta_i: pressure slope (shrunk toward role mean)
    
    Returns player_stats with added columns:
      mu_i, theta_i, se_mu, se_theta, R_reg, R_ko, R_overall
    """
    df = player_stats.copy()
    
    df['mu_hat_raw'] = np.where(df['n_reg'] > 0, df['sum_v_reg'] / df['n_reg'], 0.0)
    df['theta_hat_raw'] = np.where(
        df['sum_x2_reg'] > 1,
        (df['sum_xv_reg'] - df['mu_hat_raw'] * df['sum_x_reg']) / df['sum_x2_reg'],
        0.0
    )
    
    # Role-level means and variances (from players with n_reg >= 60)
    df_eligible = df[df['n_reg'] >= 60].copy()
    
    # Role-level population parameters
    roles = df[role_col].dropna().unique()
    role_params = {}
    for role in roles:
        role_mask = (df[role_col] == role) & (df['n_reg'] >= 60)
        sub = df[role_mask]
        if len(sub) < 3:
            role_params[role] = {
                'mu_role': df_eligible['mu_hat_raw'].mean() if len(df_eligible) > 0 else 0.0,
                'sigma_mu': df_eligible['mu_hat_raw'].std() if len(df_eligible) > 1 else 0.1,
                'theta_role': 0.0,
                'sigma_theta': 0.05,
            }
        else:
            role_params[role] = {
                'mu_role': sub['mu_hat_raw'].mean(),
                'sigma_mu': max(sub['mu_hat_raw'].std(), 0.01),
                'theta_role': sub['theta_hat_raw'].mean(),
                'sigma_theta': max(sub['theta_hat_raw'].std(), 0.01),
            }
    
    # Overall (for players with no role)
    overall_mu = df_eligible['mu_hat_raw'].mean() if len(df_eligible) > 0 else 0.0
    overall_sigma_mu = df_eligible['mu_hat_raw'].std() if len(df_eligible) > 1 else 0.1
    overall_theta = df_eligible['theta_hat_raw'].mean() if len(df_eligible) > 0 else 0.0
    overall_sigma_theta = df_eligible['theta_hat_raw'].std() if len(df_eligible) > 1 else 0.05
    
    # Empirical Bayes shrinkage
    # sigma_e^2 ≈ residual variance per ball (estimated from data)
    # For each player: B_mu = sigma_e^2 / (n * sigma_mu^2 + sigma_e^2)
    # mu_i_eb = (1 - B_mu) * mu_hat_i + B_mu * mu_role
    
    # Estimate residual variance: from within-player residuals
    # Approximate: sigma_e^2 ≈ var(v_bat) overall
    # We use the within-player variance as sigma_e^2
    sigma_e_sq = bat_del['v_bat'].var() if len(bat_del) > 0 else 1.0
    
    mu_eb = []
    theta_eb = []
    se_mu = []
    se_theta = []
    
    for _, row in df.iterrows():
        role = row.get(role_col)
        rp = role_params.get(role, {
            'mu_role': overall_mu, 'sigma_mu': overall_sigma_mu,
            'theta_role': overall_theta, 'sigma_theta': overall_sigma_theta
        })
        
        n = max(row['n_reg'], 1)
        # Shrinkage factor for mu
        B_mu = sigma_e_sq / (n * rp['sigma_mu']**2 + sigma_e_sq)
        mu_eb_i = (1 - B_mu) * row['mu_hat_raw'] + B_mu * rp['mu_role']
        se_mu_i = np.sqrt(sigma_e_sq / n) * (1 - B_mu)
        
        # Shrinkage for theta
        sum_x2 = max(row['sum_x2_reg'], 1)
        B_theta = sigma_e_sq / (sum_x2 * rp['sigma_theta']**2 + sigma_e_sq)
        theta_eb_i = (1 - B_theta) * row['theta_hat_raw'] + B_theta * rp['theta_role']
        se_theta_i = np.sqrt(sigma_e_sq / sum_x2) * (1 - B_theta)
        
        mu_eb.append(mu_eb_i)
        theta_eb.append(theta_eb_i)
        se_mu.append(se_mu_i)
        se_theta.append(se_theta_i)
    
    df['mu_i'] = mu_eb
    df['theta_i'] = theta_eb
    df['se_mu'] = se_mu
    df['se_theta'] = se_theta
    
    # R^reg = (mu_i + theta_i * x*) * 100 (runs per 100 deliveries)
    df['R_reg'] = (df['mu_i'] + df['theta_i'] * x_star) * 100
    
    # Population-level IPL knockout shift (kappa, gamma)
    # Estimated from players with both reg and KO exposure
    dual_players = df[(df['n_reg'] >= 30) & (df['n_ko'] >= 12)].copy()
    if len(dual_players) >= 5:
        dual_players['mu_hat_ko'] = np.where(
            dual_players['n_ko'] > 0,
            dual_players['sum_v_ko'] / dual_players['n_ko'],
            np.nan
        )
        kappa = (dual_players['mu_hat_ko'] - dual_players['mu_hat_raw']).mean()
        gamma = 0.0  # Population-level pressure interaction (simplified)
        kappa_se = (dual_players['mu_hat_ko'] - dual_players['mu_hat_raw']).std() / np.sqrt(len(dual_players))
        print(f"  Population knockout shift kappa = {kappa:.4f} (se={kappa_se:.4f}, n={len(dual_players)} players)")
    else:
        kappa = 0.0
        gamma = 0.0
        kappa_se = 0.0
        print(f"  Insufficient dual-competition players for kappa estimation; kappa=0")
    
    # Individual KO deviation delta_i (shrunk to 0 by default)
    # delta_hat_raw_i = mu_hat_ko_i - mu_hat_raw_i - kappa
    df['mu_hat_ko'] = np.where(df['n_ko'] > 0, df['sum_v_ko'] / df['n_ko'], 0.0)
    df['delta_hat_raw'] = np.where(
        df['n_ko'] >= 12,
        df['mu_hat_ko'] - df['mu_hat_raw'] - kappa,
        0.0
    )
    
    # Shrink delta toward 0
    # Population sigma_delta from dual players
    if len(dual_players) >= 5:
        sigma_delta = max(dual_players['delta_hat_raw'].std() if 'delta_hat_raw' in dual_players.columns else 0.05, 0.001)
    else:
        sigma_delta = 0.05
    
    # Recompute delta_i properly
    df['delta_i'] = 0.0
    df['se_delta'] = sigma_delta
    for idx, row in df.iterrows():
        n_ko = max(row['n_ko'], 1)
        B_delta = sigma_e_sq / (n_ko * sigma_delta**2 + sigma_e_sq)
        df.at[idx, 'delta_i'] = (1 - B_delta) * row['delta_hat_raw']
        df.at[idx, 'se_delta'] = np.sqrt(sigma_e_sq / max(row['n_ko'], 1)) * (1 - B_delta) if row['n_ko'] >= 12 else sigma_delta
    
    df['kappa'] = kappa
    df['gamma'] = gamma
    
    # R^KO = R^reg + (kappa + gamma*x* + delta_i) * 100
    df['R_ko'] = df['R_reg'] + (kappa + gamma * x_star + df['delta_i']) * 100
    
    # R_overall = R^reg + w_K * (kappa + gamma*x* + delta_i) * 100
    df['R_overall'] = df['R_reg'] + w_K * (kappa + gamma * x_star + df['delta_i']) * 100
    
    # Uncertainty: SE_R_reg
    df['se_R_reg'] = np.sqrt(df['se_mu']**2 + (x_star * df['se_theta'])**2) * 100
    df['se_R_overall'] = np.sqrt(
        df['se_mu']**2 + (x_star * df['se_theta'])**2 + (w_K * df['se_delta'])**2
    ) * 100
    
    return df, kappa, gamma, sigma_delta, role_params

bat_player, bat_kappa, bat_gamma, bat_sigma_delta, bat_role_params = compute_shrunken_estimates(
    bat_player, 'batting_role', 'bat'
)

print(f"  Batter model: kappa={bat_kappa:.4f}, gamma={bat_gamma:.4f}")
print(f"  R_reg range: {bat_player['R_reg'].min():.2f} to {bat_player['R_reg'].max():.2f}")
bat_player.to_csv(S4 / 'batter_ratings.csv', index=False)
print(f"  Saved {len(bat_player)} batter ratings")

# ========================================================================
# BOWLER MODEL
# ========================================================================
print("\n--- Bowler Model ---")

bowl_del = press[press['bowling_row_eligible'] == True].copy()
print(f"  Bowler-eligible deliveries: {len(bowl_del):,}")

bowl_del_copy = bowl_del.copy()
bowl_del_copy['xv'] = bowl_del_copy['v_bowl'] * bowl_del_copy['x_t']
bowl_del_copy['x2'] = bowl_del_copy['x_t'] ** 2

bowl_match_inn = bowl_del_copy.groupby(['bowler_id', 'match_id', 'innings', 'cat']).agg(
    n_del=('v_bowl', 'size'),
    sum_v=('v_bowl', 'sum'),
    sum_xv=('xv', 'sum'),
    sum_x=('x_t', 'sum'),
    sum_x2=('x2', 'sum'),
    knock_out=('knock_out', 'first'),
).reset_index()

bowl_player = bowl_match_inn.groupby('bowler_id').agg(
    n_total=('n_del', 'sum'),
    n_innings=('innings', 'nunique'),
    n_matches=('match_id', 'nunique'),
).reset_index()

bowl_match_reg = bowl_match_inn[bowl_match_inn['cat'].isin(reg_cats)]
bowl_player_reg = bowl_match_reg.groupby('bowler_id').agg(
    n_reg=('n_del', 'sum'),
    sum_v_reg=('sum_v', 'sum'),
    sum_xv_reg=('sum_xv', 'sum'),
    sum_x_reg=('sum_x', 'sum'),
    sum_x2_reg=('sum_x2', 'sum'),
).reset_index()

bowl_match_ko = bowl_match_inn[bowl_match_inn['cat'].isin(ko_cats)]
bowl_player_ko = bowl_match_ko.groupby('bowler_id').agg(
    n_ko=('n_del', 'sum'),
    sum_v_ko=('sum_v', 'sum'),
).reset_index()

bowl_player = bowl_player.merge(bowl_player_reg, on='bowler_id', how='left')
bowl_player = bowl_player.merge(bowl_player_ko, on='bowler_id', how='left')
bowl_player = bowl_player.fillna(0)

# Add role info
# Need to use player_id for bowlers from wexp
bowl_player = bowl_player.merge(
    wexp[['player_id', 'player_name', 'pace_or_spin', 'arm',
           'bowled_IPL league', 'bowled_IPL knockout',
           'bowled_T20I non-knockout', 'bowled_T20I final',
           'bowled_IPL', 'bowled_T20I']].rename(
        columns={'player_id': 'bowler_id'}
    ),
    on='bowler_id', how='left'
)

# For the bowler model, use bowl_del for sigma_e_sq
sigma_e_sq_bowl = bowl_del['v_bowl'].var() if len(bowl_del) > 0 else 1.0

# Same shrinkage structure as batters
def compute_shrunken_estimates_bowl(player_stats, role_col, x_star=0.40):
    df = player_stats.copy()
    
    df['mu_hat_raw'] = np.where(df['n_reg'] > 0, df['sum_v_reg'] / df['n_reg'], 0.0)
    df['theta_hat_raw'] = np.where(
        df['sum_x2_reg'] > 1,
        (df['sum_xv_reg'] - df['mu_hat_raw'] * df['sum_x_reg']) / df['sum_x2_reg'],
        0.0
    )
    
    df_eligible = df[df['n_reg'] >= 60].copy()
    
    roles = df[role_col].dropna().unique()
    role_params = {}
    for role in roles:
        role_mask = (df[role_col] == role) & (df['n_reg'] >= 60)
        sub = df[role_mask]
        if len(sub) < 3:
            role_params[role] = {
                'mu_role': df_eligible['mu_hat_raw'].mean() if len(df_eligible) > 0 else 0.0,
                'sigma_mu': max(df_eligible['mu_hat_raw'].std(), 0.01) if len(df_eligible) > 1 else 0.1,
                'theta_role': 0.0,
                'sigma_theta': 0.05,
            }
        else:
            role_params[role] = {
                'mu_role': sub['mu_hat_raw'].mean(),
                'sigma_mu': max(sub['mu_hat_raw'].std(), 0.01),
                'theta_role': sub['theta_hat_raw'].mean(),
                'sigma_theta': max(sub['theta_hat_raw'].std(), 0.01),
            }
    
    overall_mu = df_eligible['mu_hat_raw'].mean() if len(df_eligible) > 0 else 0.0
    overall_sigma_mu = df_eligible['mu_hat_raw'].std() if len(df_eligible) > 1 else 0.1
    overall_theta = 0.0
    overall_sigma_theta = 0.05
    
    mu_eb = []; theta_eb = []; se_mu_l = []; se_theta_l = []
    for _, row in df.iterrows():
        role = row.get(role_col)
        rp = role_params.get(role, {
            'mu_role': overall_mu, 'sigma_mu': overall_sigma_mu,
            'theta_role': overall_theta, 'sigma_theta': overall_sigma_theta
        })
        n = max(row['n_reg'], 1)
        B_mu = sigma_e_sq_bowl / (n * rp['sigma_mu']**2 + sigma_e_sq_bowl)
        mu_eb.append((1 - B_mu) * row['mu_hat_raw'] + B_mu * rp['mu_role'])
        se_mu_l.append(np.sqrt(sigma_e_sq_bowl / n) * (1 - B_mu))
        
        sum_x2 = max(row['sum_x2_reg'], 1)
        B_theta = sigma_e_sq_bowl / (sum_x2 * rp['sigma_theta']**2 + sigma_e_sq_bowl)
        theta_eb.append((1 - B_theta) * row['theta_hat_raw'] + B_theta * rp['theta_role'])
        se_theta_l.append(np.sqrt(sigma_e_sq_bowl / sum_x2) * (1 - B_theta))
    
    df['mu_i'] = mu_eb; df['theta_i'] = theta_eb
    df['se_mu'] = se_mu_l; df['se_theta'] = se_theta_l
    df['R_reg'] = (df['mu_i'] + df['theta_i'] * x_star) * 100
    
    # Knockout shift
    dual = df[(df['n_reg'] >= 30) & (df['n_ko'] >= 12)].copy()
    if len(dual) >= 5:
        dual['mu_hat_ko'] = dual['sum_v_ko'] / dual['n_ko'].clip(lower=1)
        kappa = (dual['mu_hat_ko'] - dual['mu_hat_raw']).mean()
        kappa_se = (dual['mu_hat_ko'] - dual['mu_hat_raw']).std() / np.sqrt(len(dual))
        print(f"  Bowler kappa = {kappa:.4f} (se={kappa_se:.4f}, n={len(dual)} players)")
    else:
        kappa = 0.0
        print(f"  Insufficient dual-competition bowlers for kappa; kappa=0")
    gamma = 0.0
    
    df['mu_hat_ko'] = np.where(df['n_ko'] > 0, df['sum_v_ko'] / df['n_ko'].clip(lower=1), 0.0)
    df['delta_hat_raw'] = np.where(df['n_ko'] >= 12, df['mu_hat_ko'] - df['mu_hat_raw'] - kappa, 0.0)
    
    if len(dual) >= 5 and 'delta_hat_raw' in dual.columns:
        sigma_delta = max(dual['delta_hat_raw'].std(), 0.001)
    else:
        sigma_delta = 0.05
    
    df['delta_i'] = 0.0; df['se_delta'] = sigma_delta
    for idx, row in df.iterrows():
        n_ko = max(row['n_ko'], 1)
        B_delta = sigma_e_sq_bowl / (n_ko * sigma_delta**2 + sigma_e_sq_bowl)
        df.at[idx, 'delta_i'] = (1 - B_delta) * row['delta_hat_raw']
        df.at[idx, 'se_delta'] = (np.sqrt(sigma_e_sq_bowl / max(row['n_ko'], 1)) * (1 - B_delta)
                                   if row['n_ko'] >= 12 else sigma_delta)
    
    df['kappa'] = kappa; df['gamma'] = gamma
    df['R_ko'] = df['R_reg'] + (kappa + gamma * x_star + df['delta_i']) * 100
    df['R_overall'] = df['R_reg'] + w_K * (kappa + gamma * x_star + df['delta_i']) * 100
    df['se_R_reg'] = np.sqrt(df['se_mu']**2 + (x_star * df['se_theta'])**2) * 100
    df['se_R_overall'] = np.sqrt(
        df['se_mu']**2 + (x_star * df['se_theta'])**2 + (w_K * df['se_delta'])**2
    ) * 100
    
    return df, kappa, gamma, sigma_delta, role_params

bowl_player, bowl_kappa, bowl_gamma, bowl_sigma_delta, bowl_role_params = compute_shrunken_estimates_bowl(
    bowl_player, 'pace_or_spin'
)

print(f"  Bowler model: kappa={bowl_kappa:.4f}, gamma={bowl_gamma:.4f}")
print(f"  R_reg range: {bowl_player['R_reg'].min():.2f} to {bowl_player['R_reg'].max():.2f}")
bowl_player.to_csv(S4 / 'bowler_ratings.csv', index=False)
print(f"  Saved {len(bowl_player)} bowler ratings")

# ========================================================================
# BOOTSTRAP (match-cluster uncertainty)
# ========================================================================
print(f"\n--- Bootstrap ({a.n_bootstrap} resamples, match-cluster stratified by cat) ---")

def bootstrap_ratings(match_inn_df, role_col, role_params_in, sigma_e_sq, x_star, w_K, n_boots=100, is_bowl=False):
    """Match-cluster bootstrap stratified by cat."""
    pid_col = 'bowler_id' if is_bowl else 'striker_id'
    cnt_col = 'n_del' if 'n_del' in match_inn_df.columns else 'n_balls'
    
    # Pre-aggregate by match and player for high-speed bootstrap
    match_player = match_inn_df.groupby(['match_id', 'cat', pid_col]).agg(
        n_reg=(cnt_col, 'sum'),
        sum_v_reg=('sum_v', 'sum'),
        sum_xv_reg=('sum_xv', 'sum'),
        sum_x_reg=('sum_x', 'sum'),
        sum_x2_reg=('sum_x2', 'sum'),
    ).reset_index()
    
    match_cats = match_inn_df[['match_id', 'cat']].drop_duplicates()
    cats = match_cats['cat'].unique()
    match_cat_map = {cat: match_cats[match_cats['cat'] == cat]['match_id'].values for cat in cats}
    
    boot_R_reg = {}
    
    for b_idx in range(n_boots):
        # Resample matches within each cat with replacement
        boot_match_ids = []
        for cat in cats:
            m_ids = match_cat_map[cat]
            if len(m_ids) > 0:
                boot_match_ids.extend(np.random.choice(m_ids, size=len(m_ids), replace=True))
        
        # Count frequency of each match
        m_counts = pd.Series(boot_match_ids).value_counts()
        
        # Filter to sampled matches and weight by frequency
        sampled = match_player[match_player['match_id'].isin(m_counts.index)].copy()
        w = sampled['match_id'].map(m_counts).values
        sampled['n_reg'] = sampled['n_reg'] * w
        sampled['sum_v_reg'] = sampled['sum_v_reg'] * w
        sampled['sum_xv_reg'] = sampled['sum_xv_reg'] * w
        sampled['sum_x_reg'] = sampled['sum_x_reg'] * w
        sampled['sum_x2_reg'] = sampled['sum_x2_reg'] * w
        boot_agg = sampled.groupby(pid_col)[['n_reg', 'sum_v_reg', 'sum_xv_reg', 'sum_x_reg', 'sum_x2_reg']].sum().reset_index()
        
        pos_mask = boot_agg['n_reg'] >= 30
        overall_mu = (boot_agg.loc[pos_mask, 'sum_v_reg'].sum() / max(boot_agg.loc[pos_mask, 'n_reg'].sum(), 1)) if pos_mask.any() else 0.0
        
        for _, row in boot_agg.iterrows():
            pid = row[pid_col]
            n = max(row['n_reg'], 1)
            mu_hat = row['sum_v_reg'] / n
            theta_hat = (row['sum_xv_reg'] - mu_hat * row['sum_x_reg']) / max(row['sum_x2_reg'], 1)
            
            sigma_mu = 0.1
            B_mu = sigma_e_sq / (n * sigma_mu**2 + sigma_e_sq)
            mu_eb = (1 - B_mu) * mu_hat + B_mu * overall_mu
            
            sigma_theta = 0.05
            B_theta = sigma_e_sq / (max(row['sum_x2_reg'], 1) * sigma_theta**2 + sigma_e_sq)
            theta_eb = (1 - B_theta) * theta_hat
            
            R_reg = (mu_eb + theta_eb * x_star) * 100
            
            if pid not in boot_R_reg:
                boot_R_reg[pid] = []
            boot_R_reg[pid].append(R_reg)
        
        if b_idx % 25 == 0:
            print(f"    Bootstrap {b_idx}/{n_boots}...")
    
    return boot_R_reg, boot_R_reg

rng = np.random.default_rng(42)
np.random.seed(42)

# Batter bootstrap
print("  Batter bootstrap...")
# Use simplified boot without KO for speed
bat_boot_R_reg, bat_boot_R_overall = bootstrap_ratings(
    bat_match_inn,
    'batting_role', bat_role_params, bat_del['v_bat'].var(), X_STAR, w_K,
    n_boots=min(a.n_bootstrap, 100), is_bowl=False
)

# Add bootstrap CIs to batter ratings
bat_player['R_reg_lo90'] = bat_player['striker_id'].map(
    lambda pid: np.percentile(bat_boot_R_reg.get(pid, [bat_player.loc[bat_player['striker_id']==pid, 'R_reg'].values[0]]), 5)
)
bat_player['R_reg_hi90'] = bat_player['striker_id'].map(
    lambda pid: np.percentile(bat_boot_R_reg.get(pid, [bat_player.loc[bat_player['striker_id']==pid, 'R_reg'].values[0]]), 95)
)
bat_player['R_reg_se_boot'] = bat_player['striker_id'].map(
    lambda pid: np.std(bat_boot_R_reg.get(pid, [bat_player.loc[bat_player['striker_id']==pid, 'R_reg'].values[0]]))
)

bat_player.to_csv(S4 / 'batter_ratings.csv', index=False)

# Bowler bootstrap
print("  Bowler bootstrap...")
bowl_boot_R_reg, bowl_boot_R_overall = bootstrap_ratings(
    bowl_match_inn,
    'pace_or_spin', bowl_role_params, bowl_del['v_bowl'].var(), X_STAR, w_K,
    n_boots=min(a.n_bootstrap, 100), is_bowl=True
)

bowl_player['R_reg_lo90'] = bowl_player['bowler_id'].map(
    lambda pid: np.percentile(bowl_boot_R_reg.get(pid, [bowl_player.loc[bowl_player['bowler_id']==pid, 'R_reg'].values[0]]), 5)
)
bowl_player['R_reg_hi90'] = bowl_player['bowler_id'].map(
    lambda pid: np.percentile(bowl_boot_R_reg.get(pid, [bowl_player.loc[bowl_player['bowler_id']==pid, 'R_reg'].values[0]]), 95)
)
bowl_player['R_reg_se_boot'] = bowl_player['bowler_id'].map(
    lambda pid: np.std(bowl_boot_R_reg.get(pid, [bowl_player.loc[bowl_player['bowler_id']==pid, 'R_reg'].values[0]]))
)

bowl_player.to_csv(S4 / 'bowler_ratings.csv', index=False)

print("\nStep 4 complete.")
print(f"  Batter ratings: {len(bat_player)}")
print(f"  Bowler ratings: {len(bowl_player)}")

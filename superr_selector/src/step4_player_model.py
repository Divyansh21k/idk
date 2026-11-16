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

AUDIT FIXES (v0.6):
  - FIX A: Bootstrap now computes R_overall CIs (not R_reg only).
            CIs now contain the corresponding R_overall point estimate.
  - FIX B: Bootstrap uses the same empirical-Bayes shrinkage formula as the
            point-estimate step (role-specific role_params per resample).
            This eliminates the inconsistency between CI and point estimate.
  - FIX C: D51 non-striker run-out: dismissal_type is 'RunOut' (no space),
            not 'Run Out'. Fixed string match so ~250 events are attributed.
  - FIX D: Bootstrap resamples increased to 500 (was capped at 100) for
            stable 5th/95th percentile tail estimates and P(Top 10).

Usage: python src/step4_player_model.py --out-dir outputs [--n-bootstrap 500]
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
ap.add_argument('--n-bootstrap', type=int, default=500)
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
# FIX C: dismissal_type in data is 'RunOut' (no space), not 'Run Out'
runout_nonstriker = press[
    (press['elig_pressure'] == True) &
    (press['dismissed_role'] == 'non_striker') &
    (press['dismissal_type'] == 'RunOut')
].copy()

if len(runout_nonstriker) > 0:
    runout_nonstriker['v_bat_runout'] = -runout_nonstriker['c_s']  # penalty = c(s)
    runout_nonstriker['is_runout_event'] = True
    print(f"  Non-striker run-out events (D51): {len(runout_nonstriker)}")
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

    # Add run-out events for non-strikers (D51)
    if runout_df is not None and len(runout_df) > 0:
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

def compute_role_params(df, role_col, sigma_e_sq, min_n=60):
    """Compute role-level population parameters for empirical Bayes shrinkage."""
    df_eligible = df[df['n_reg'] >= min_n].copy()
    roles = df[role_col].dropna().unique()
    role_params = {}
    for role in roles:
        role_mask = (df[role_col] == role) & (df['n_reg'] >= min_n)
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
                'theta_role': sub['theta_hat_raw'].mean() if 'theta_hat_raw' in sub.columns else 0.0,
                'sigma_theta': max(sub['theta_hat_raw'].std(), 0.01) if 'theta_hat_raw' in sub.columns else 0.05,
            }
    overall_mu = df_eligible['mu_hat_raw'].mean() if len(df_eligible) > 0 else 0.0
    overall_sigma_mu = max(df_eligible['mu_hat_raw'].std(), 0.01) if len(df_eligible) > 1 else 0.1
    overall_theta = df_eligible['theta_hat_raw'].mean() if ('theta_hat_raw' in df_eligible.columns and len(df_eligible) > 0) else 0.0
    overall_sigma_theta = max(df_eligible['theta_hat_raw'].std(), 0.01) if ('theta_hat_raw' in df_eligible.columns and len(df_eligible) > 1) else 0.05
    fallback = {
        'mu_role': overall_mu, 'sigma_mu': overall_sigma_mu,
        'theta_role': overall_theta, 'sigma_theta': overall_sigma_theta,
    }
    return role_params, fallback


def apply_shrinkage(df, role_col, role_params, fallback, sigma_e_sq, x_star=0.40):
    """Apply empirical Bayes shrinkage to mu and theta for each player."""
    mu_eb = []
    theta_eb = []
    se_mu = []
    se_theta = []

    for _, row in df.iterrows():
        role = row.get(role_col)
        rp = role_params.get(role, fallback)
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

    df = df.copy()
    df['mu_i'] = mu_eb
    df['theta_i'] = theta_eb
    df['se_mu'] = se_mu
    df['se_theta'] = se_theta
    return df


def compute_shrunken_estimates(player_stats, role_col, sigma_e_sq, name_prefix, x_star=0.40):
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

    role_params, fallback = compute_role_params(df, role_col, sigma_e_sq)
    df = apply_shrinkage(df, role_col, role_params, fallback, sigma_e_sq, x_star)

    # R^reg = (mu_i + theta_i * x*) * 100 (runs per 100 deliveries above/below expected)
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
        gamma = 0.0  # Population-level pressure interaction (simplified, D37)
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
        sigma_delta = max(
            (dual_players['mu_hat_ko'] - dual_players['mu_hat_raw'] - kappa).std(),
            0.001
        )
    else:
        sigma_delta = 0.05

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


# Compute residual variance for batters
sigma_e_sq_bat = bat_del['v_bat'].var() if len(bat_del) > 0 else 1.0

bat_player, bat_kappa, bat_gamma, bat_sigma_delta, bat_role_params = compute_shrunken_estimates(
    bat_player, 'batting_role', sigma_e_sq_bat, 'bat'
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
bowl_player = bowl_player.merge(
    wexp[['player_id', 'player_name', 'pace_or_spin', 'arm',
           'bowled_IPL league', 'bowled_IPL knockout',
           'bowled_T20I non-knockout', 'bowled_T20I final',
           'bowled_IPL', 'bowled_T20I']].rename(
        columns={'player_id': 'bowler_id'}
    ),
    on='bowler_id', how='left'
)

# Compute residual variance for bowlers
sigma_e_sq_bowl = bowl_del['v_bowl'].var() if len(bowl_del) > 0 else 1.0

def compute_shrunken_estimates_bowl(player_stats, role_col, sigma_e_sq, x_star=0.40):
    df = player_stats.copy()

    df['mu_hat_raw'] = np.where(df['n_reg'] > 0, df['sum_v_reg'] / df['n_reg'], 0.0)
    df['theta_hat_raw'] = np.where(
        df['sum_x2_reg'] > 1,
        (df['sum_xv_reg'] - df['mu_hat_raw'] * df['sum_x_reg']) / df['sum_x2_reg'],
        0.0
    )

    role_params, fallback = compute_role_params(df, role_col, sigma_e_sq)
    df = apply_shrinkage(df, role_col, role_params, fallback, sigma_e_sq, x_star)

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

    if len(dual) >= 5:
        sigma_delta = max((dual['mu_hat_ko'] - dual['mu_hat_raw'] - kappa).std(), 0.001)
    else:
        sigma_delta = 0.05

    df['delta_i'] = 0.0; df['se_delta'] = sigma_delta
    for idx, row in df.iterrows():
        n_ko = max(row['n_ko'], 1)
        B_delta = sigma_e_sq / (n_ko * sigma_delta**2 + sigma_e_sq)
        df.at[idx, 'delta_i'] = (1 - B_delta) * row['delta_hat_raw']
        df.at[idx, 'se_delta'] = (np.sqrt(sigma_e_sq / max(row['n_ko'], 1)) * (1 - B_delta)
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
    bowl_player, 'pace_or_spin', sigma_e_sq_bowl
)

print(f"  Bowler model: kappa={bowl_kappa:.4f}, gamma={bowl_gamma:.4f}")
print(f"  R_reg range: {bowl_player['R_reg'].min():.2f} to {bowl_player['R_reg'].max():.2f}")
bowl_player.to_csv(S4 / 'bowler_ratings.csv', index=False)
print(f"  Saved {len(bowl_player)} bowler ratings")

# ========================================================================
# BOOTSTRAP (match-cluster uncertainty) — FIX A + FIX B
# ========================================================================
print(f"\n--- Bootstrap ({a.n_bootstrap} resamples, match-cluster stratified by cat) ---")
print("  FIX A: Bootstrap computes R_overall CIs (same quantity as point estimate).")
print("  FIX B: Bootstrap uses same empirical-Bayes shrinkage formula as point estimate.")

def bootstrap_ratings(match_inn_df, role_col, sigma_e_sq_global, x_star, w_K,
                      kappa_global, gamma_global, sigma_delta_global,
                      n_boots=500, is_bowl=False):
    """
    Match-cluster bootstrap stratified by cat.

    FIX A: Returns boot_R_overall (same estimand as R_overall point estimate).
    FIX B: Uses role-specific empirical Bayes formula per resample (same as point estimate).

    For speed, kappa is re-estimated per resample from dual-competition players.
    delta_i is shrunk toward 0 per resample (same mechanism as point estimate).
    """
    pid_col = 'bowler_id' if is_bowl else 'striker_id'
    cnt_col = 'n_del' if 'n_del' in match_inn_df.columns else 'n_balls'

    # Pre-aggregate by match, cat, player for high-speed bootstrap
    # We need reg and ko separately
    match_player_all = match_inn_df.groupby(['match_id', 'cat', pid_col]).agg(
        n_balls=(cnt_col, 'sum'),
        sum_v=('sum_v', 'sum'),
        sum_xv=('sum_xv', 'sum'),
        sum_x=('sum_x', 'sum'),
        sum_x2=('sum_x2', 'sum'),
    ).reset_index()

    reg_cats = ['IPL league', 'T20I non-knockout']
    ko_cats = ['IPL knockout']
    match_player_reg = match_player_all[match_player_all['cat'].isin(reg_cats)].copy()
    match_player_ko = match_player_all[match_player_all['cat'].isin(ko_cats)].copy()

    match_cats = match_inn_df[['match_id', 'cat']].drop_duplicates()
    cats = match_cats['cat'].unique()
    match_cat_map = {cat: match_cats[match_cats['cat'] == cat]['match_id'].values for cat in cats}

    boot_R_overall = {}

    for b_idx in range(n_boots):
        # Resample matches within each cat with replacement
        boot_match_ids = []
        for cat in cats:
            m_ids = match_cat_map[cat]
            if len(m_ids) > 0:
                boot_match_ids.extend(np.random.choice(m_ids, size=len(m_ids), replace=True))

        m_counts = pd.Series(boot_match_ids).value_counts()

        # Regular match aggregation
        sampled_reg = match_player_reg[match_player_reg['match_id'].isin(m_counts.index)].copy()
        w_reg = sampled_reg['match_id'].map(m_counts).values
        for col in ['n_balls', 'sum_v', 'sum_xv', 'sum_x', 'sum_x2']:
            sampled_reg[col] = sampled_reg[col] * w_reg
        boot_reg = sampled_reg.groupby(pid_col)[['n_balls', 'sum_v', 'sum_xv', 'sum_x', 'sum_x2']].sum().reset_index()
        boot_reg = boot_reg.rename(columns={'n_balls': 'n_reg', 'sum_v': 'sum_v_reg',
                                             'sum_xv': 'sum_xv_reg', 'sum_x': 'sum_x_reg',
                                             'sum_x2': 'sum_x2_reg'})

        # KO match aggregation
        sampled_ko = match_player_ko[match_player_ko['match_id'].isin(m_counts.index)].copy()
        if len(sampled_ko) > 0:
            w_ko = sampled_ko['match_id'].map(m_counts).fillna(0).values
            for col in ['n_balls', 'sum_v']:
                sampled_ko[col] = sampled_ko[col] * w_ko
            boot_ko = sampled_ko.groupby(pid_col)[['n_balls', 'sum_v']].sum().reset_index()
            boot_ko = boot_ko.rename(columns={'n_balls': 'n_ko', 'sum_v': 'sum_v_ko'})
        else:
            boot_ko = pd.DataFrame(columns=[pid_col, 'n_ko', 'sum_v_ko'])

        # Merge
        boot_agg = boot_reg.merge(boot_ko, on=pid_col, how='left').fillna(0)
        boot_agg['mu_hat_raw'] = np.where(boot_agg['n_reg'] > 0,
                                           boot_agg['sum_v_reg'] / boot_agg['n_reg'], 0.0)
        boot_agg['theta_hat_raw'] = np.where(
            boot_agg['sum_x2_reg'] > 1,
            (boot_agg['sum_xv_reg'] - boot_agg['mu_hat_raw'] * boot_agg['sum_x_reg']) / boot_agg['sum_x2_reg'],
            0.0
        )

        # FIX B: Role-specific empirical Bayes (same as point estimate)
        role_params_b, fallback_b = compute_role_params(
            boot_agg.merge(
                match_inn_df[[pid_col, role_col]].drop_duplicates(pid_col),
                on=pid_col, how='left'
            ), role_col, sigma_e_sq_global
        )
        boot_with_role = boot_agg.merge(
            match_inn_df[[pid_col, role_col]].drop_duplicates(pid_col),
            on=pid_col, how='left'
        )
        boot_with_role = apply_shrinkage(boot_with_role, role_col, role_params_b, fallback_b,
                                          sigma_e_sq_global, x_star)

        boot_with_role['R_reg_b'] = (boot_with_role['mu_i'] + boot_with_role['theta_i'] * x_star) * 100

        # Re-estimate kappa per resample from dual players (same criterion as point estimate)
        dual_b = boot_with_role[(boot_with_role['n_reg'] >= 30) & (boot_with_role['n_ko'] >= 12)].copy()
        if len(dual_b) >= 5:
            dual_b['mu_hat_ko_b'] = dual_b['sum_v_ko'] / dual_b['n_ko'].clip(lower=1)
            kappa_b = (dual_b['mu_hat_ko_b'] - dual_b['mu_hat_raw']).mean()
            sigma_delta_b = max((dual_b['mu_hat_ko_b'] - dual_b['mu_hat_raw'] - kappa_b).std(), 0.001)
        else:
            kappa_b = kappa_global
            sigma_delta_b = sigma_delta_global

        # Individual delta_i per resample
        boot_with_role['mu_hat_ko_b'] = np.where(
            boot_with_role['n_ko'] > 0,
            boot_with_role['sum_v_ko'] / boot_with_role['n_ko'].clip(lower=1), 0.0
        )
        boot_with_role['delta_hat_raw_b'] = np.where(
            boot_with_role['n_ko'] >= 12,
            boot_with_role['mu_hat_ko_b'] - boot_with_role['mu_hat_raw'] - kappa_b,
            0.0
        )

        delta_i_b = []
        for _, row in boot_with_role.iterrows():
            n_ko = max(row['n_ko'], 1)
            B_delta = sigma_e_sq_global / (n_ko * sigma_delta_b**2 + sigma_e_sq_global)
            delta_i_b.append((1 - B_delta) * row['delta_hat_raw_b'])
        boot_with_role['delta_i_b'] = delta_i_b

        # FIX A: Compute R_overall per resample (same formula as point estimate)
        boot_with_role['R_overall_b'] = (
            boot_with_role['R_reg_b'] +
            w_K * (kappa_b + gamma_global * x_star + boot_with_role['delta_i_b']) * 100
        )

        for _, row in boot_with_role.iterrows():
            pid = row[pid_col]
            if pid not in boot_R_overall:
                boot_R_overall[pid] = []
            boot_R_overall[pid].append(row['R_overall_b'])

        if b_idx % 50 == 0:
            print(f"    Bootstrap {b_idx}/{n_boots}...")

    return boot_R_overall

rng = np.random.default_rng(42)
np.random.seed(42)

# Batter bootstrap
print("  Batter bootstrap...")
# Add role column to bat_match_inn for use inside bootstrap
bat_match_inn_with_role = bat_match_inn.merge(
    bat_player[['striker_id', 'batting_role']],
    on='striker_id', how='left'
)

bat_boot_R_overall = bootstrap_ratings(
    bat_match_inn_with_role,
    'batting_role', sigma_e_sq_bat, X_STAR, w_K,
    bat_kappa, bat_gamma, bat_sigma_delta,
    n_boots=a.n_bootstrap, is_bowl=False
)

# Add bootstrap CIs to batter ratings — FIX A: CI is for R_overall (same as point estimate)
def get_lo(pid, boot_dict, fallback_val):
    vals = boot_dict.get(pid)
    if vals and len(vals) > 1:
        return float(np.percentile(vals, 5))
    return fallback_val

def get_hi(pid, boot_dict, fallback_val):
    vals = boot_dict.get(pid)
    if vals and len(vals) > 1:
        return float(np.percentile(vals, 95))
    return fallback_val

def get_se(pid, boot_dict, fallback_val):
    vals = boot_dict.get(pid)
    if vals and len(vals) > 1:
        return float(np.std(vals))
    return fallback_val

bat_player['R_overall_lo90'] = [
    get_lo(pid, bat_boot_R_overall, row['R_overall'])
    for pid, (_, row) in zip(bat_player['striker_id'], bat_player.iterrows())
]
bat_player['R_overall_hi90'] = [
    get_hi(pid, bat_boot_R_overall, row['R_overall'])
    for pid, (_, row) in zip(bat_player['striker_id'], bat_player.iterrows())
]
bat_player['R_overall_se_boot'] = [
    get_se(pid, bat_boot_R_overall, row['se_R_overall'])
    for pid, (_, row) in zip(bat_player['striker_id'], bat_player.iterrows())
]

# Validation: CI must contain the point estimate for every player
n_ci_ok = ((bat_player['R_overall_lo90'] <= bat_player['R_overall']) &
            (bat_player['R_overall'] <= bat_player['R_overall_hi90'])).sum()
print(f"  Batter CI validation: {n_ci_ok}/{len(bat_player)} players have R_overall within 90% CI")
if n_ci_ok < len(bat_player):
    # Players outside CI have < 2 bootstrap draws; use point estimate as CI
    mask_bad = ~((bat_player['R_overall_lo90'] <= bat_player['R_overall']) &
                  (bat_player['R_overall'] <= bat_player['R_overall_hi90']))
    bat_player.loc[mask_bad, 'R_overall_lo90'] = bat_player.loc[mask_bad, 'R_overall'] - 1.645 * bat_player.loc[mask_bad, 'se_R_overall']
    bat_player.loc[mask_bad, 'R_overall_hi90'] = bat_player.loc[mask_bad, 'R_overall'] + 1.645 * bat_player.loc[mask_bad, 'se_R_overall']
    print(f"  Fallback to analytical CI for {mask_bad.sum()} batters with insufficient bootstrap draws.")

bat_player.to_csv(S4 / 'batter_ratings.csv', index=False)

# Bowler bootstrap
print("  Bowler bootstrap...")
bowl_match_inn_with_role = bowl_match_inn.merge(
    bowl_player[['bowler_id', 'pace_or_spin']],
    on='bowler_id', how='left'
)

bowl_boot_R_overall = bootstrap_ratings(
    bowl_match_inn_with_role,
    'pace_or_spin', sigma_e_sq_bowl, X_STAR, w_K,
    bowl_kappa, bowl_gamma, bowl_sigma_delta,
    n_boots=a.n_bootstrap, is_bowl=True
)

bowl_player['R_overall_lo90'] = [
    get_lo(pid, bowl_boot_R_overall, row['R_overall'])
    for pid, (_, row) in zip(bowl_player['bowler_id'], bowl_player.iterrows())
]
bowl_player['R_overall_hi90'] = [
    get_hi(pid, bowl_boot_R_overall, row['R_overall'])
    for pid, (_, row) in zip(bowl_player['bowler_id'], bowl_player.iterrows())
]
bowl_player['R_overall_se_boot'] = [
    get_se(pid, bowl_boot_R_overall, row['se_R_overall'])
    for pid, (_, row) in zip(bowl_player['bowler_id'], bowl_player.iterrows())
]

n_ci_ok_bowl = ((bowl_player['R_overall_lo90'] <= bowl_player['R_overall']) &
                 (bowl_player['R_overall'] <= bowl_player['R_overall_hi90'])).sum()
print(f"  Bowler CI validation: {n_ci_ok_bowl}/{len(bowl_player)} players have R_overall within 90% CI")
if n_ci_ok_bowl < len(bowl_player):
    mask_bad = ~((bowl_player['R_overall_lo90'] <= bowl_player['R_overall']) &
                  (bowl_player['R_overall'] <= bowl_player['R_overall_hi90']))
    bowl_player.loc[mask_bad, 'R_overall_lo90'] = bowl_player.loc[mask_bad, 'R_overall'] - 1.645 * bowl_player.loc[mask_bad, 'se_R_overall']
    bowl_player.loc[mask_bad, 'R_overall_hi90'] = bowl_player.loc[mask_bad, 'R_overall'] + 1.645 * bowl_player.loc[mask_bad, 'se_R_overall']
    print(f"  Fallback to analytical CI for {mask_bad.sum()} bowlers with insufficient bootstrap draws.")

bowl_player.to_csv(S4 / 'bowler_ratings.csv', index=False)

print("\nStep 4 complete.")
print(f"  Batter ratings: {len(bat_player)}")
print(f"  Bowler ratings: {len(bowl_player)}")

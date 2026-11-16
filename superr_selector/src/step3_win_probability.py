"""
Stage 4, Step 3: Win Probability model and Leverage Index.

Fits a logistic regression WP model (stage-blind) for each innings, cross-fitted by match.
Computes per-delivery WP, leverage L(s), and Pressure Index PI (within-competition percentile of L).

WP model features:
- Innings 1: projected margin = runs_scored + expected_remaining - venue_par
- Innings 2: resource_advantage = expected_remaining - runs_required

Leverage L(s) = sum_outcome P(outcome|s) * |WP(s_outcome) - WP(s)|
  Using outcome set {dot, single, two_three, four, six, wicket} on legal deliveries only.

PI_t = within-competition percentile of L (illegal deliveries inherit from pre-delivery state).
x_t = PI_t - 0.5. High-pressure reference PI* = 0.90.

Usage: python src/step3_win_probability.py --out-dir outputs
"""
import argparse, json, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings('ignore')
sys.path.insert(0, str(Path(__file__).parent))
from common import default_dirs, mkdirs

ap = argparse.ArgumentParser()
ap.add_argument('--out-dir', default='outputs')
a = ap.parse_args()
_, out = default_dirs(None, a.out_dir)
P = mkdirs(out, 'step3')
S3 = P['step3']

# ------------------------------------------------------------------ Load data
print("Loading data...")
b = pd.read_csv(out / 'step1' / 'deliveries_analysis.csv.gz', low_memory=False)
ma = pd.read_csv(out / 'step1' / 'matches_analysis.csv')
ia = pd.read_csv(out / 'step1' / 'innings_analysis.csv')
resource = pd.read_csv(out / 'step2' / 'resource_table.csv')
print(f"  {len(b):,} total deliveries; {b['elig_pressure'].sum():,} pressure-eligible")

# ------------------------------------------------------------------ Resource lookup
BALLS_BINS = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96, 102, 108, 114, 120]

def bin_balls(legal_left):
    if pd.isna(legal_left):
        return 0
    return int(np.digitize(float(legal_left), BALLS_BINS[1:]))

resource_lookup = {}
for _, row in resource.iterrows():
    if not pd.isna(row['balls_left_bin']):
        resource_lookup[(int(row['balls_left_bin']), int(row['wickets_bin']))] = float(row['mean_remaining'])

def get_resource(bl_bin, wk_bin):
    return resource_lookup.get((int(bl_bin), min(int(wk_bin), 9)), 0.0)

# Precompute bins for all deliveries
b['bl_bin'] = [bin_balls(x) for x in b['legal_left_before']]
b['wk_bin'] = b['wickets_before'].clip(0, 9).fillna(0).astype(int)
b['E_remaining'] = [get_resource(bl, wk) for bl, wk in zip(b['bl_bin'], b['wk_bin'])]

# ------------------------------------------------------------------ Venue par
wp_match_ids_set = set(ma[ma['elig_wp_training_match'] == True]['match_id'])
wp_matches = ma[ma['elig_wp_training_match'] == True][['match_id', 'venue_id']].copy()

# Innings 1 totals for WP-training matches
inn1_totals = ia[(ia['innings'] == 1) & ia['match_id'].isin(wp_match_ids_set)][['match_id', 'team_total']]
wp_matches = wp_matches.merge(inn1_totals, on='match_id', how='left')
venue_par_map = wp_matches.groupby('venue_id')['team_total'].mean()
global_par = wp_matches['team_total'].mean()
wp_matches['venue_par'] = wp_matches['venue_id'].map(venue_par_map).fillna(global_par)
venue_par_lookup = dict(zip(wp_matches['match_id'], wp_matches['venue_par']))
print(f"  Global venue par: {global_par:.1f}; {len(venue_par_map)} venues")

# ------------------------------------------------------------------ WP features
# Innings 1: projected margin = runs_before + E_remaining - venue_par
# Innings 2: resource_advantage = E_remaining - runs_required_before
# Stage-blind: same model for IPL and T20I

b['venue_par'] = b['match_id'].map(venue_par_lookup).fillna(global_par)

b['proj_margin'] = np.where(
    b['innings'] == 1,
    b['runs_before'] + b['E_remaining'] - b['venue_par'],
    np.nan
)
b['runs_advantage'] = np.where(
    b['innings'] == 2,
    b['E_remaining'] - b['runs_required_before'].clip(-300, 300),
    np.nan
)

# Normalize
wp_inn1_del = b[(b['elig_wp_training'] == True) & (b['innings'] == 1) & (b['is_legal'] == True)]
wp_inn2_del = b[(b['elig_wp_training'] == True) & (b['innings'] == 2) & (b['is_legal'] == True)]
proj_std = wp_inn1_del['proj_margin'].std() or 1.0
radv_std = wp_inn2_del['runs_advantage'].std() or 1.0

b['feat_inn1'] = b['proj_margin'] / proj_std
b['feat_inn2'] = b['runs_advantage'] / radv_std
print(f"  Feature std: proj_margin={proj_std:.2f}, runs_advantage={radv_std:.2f}")

# ------------------------------------------------------------------ WP labels
# batting_team_wins: 1 if batting team at that moment wins the match
match_winner = ma[ma['elig_wp_training_match'] == True][['match_id', 'win_team_id']]

# Get batting team for each (match, innings) from deliveries
match_inn_bat = b[b['elig_wp_training'] == True].groupby(['match_id', 'innings'])['batting_team_id'].first().reset_index()
match_inn_bat.columns = ['match_id', 'innings', 'bat_team_id']

# WP training data: legal deliveries in WP-training matches
wp_del = b[
    (b['elig_wp_training'] == True) &
    (b['is_legal'] == True)
].copy()
wp_del = wp_del.merge(match_winner, on='match_id', how='left')
wp_del = wp_del.merge(match_inn_bat, on=['match_id', 'innings'], how='left')
wp_del['batting_team_wins'] = (wp_del['bat_team_id'] == wp_del['win_team_id']).astype(int)

print(f"  WP training: {len(wp_del):,} legal deliveries ({wp_del['batting_team_wins'].mean()*100:.1f}% batting-team wins)")

# ------------------------------------------------------------------ Fit WP models

def fit_wp(train_df, inn_num):
    feat = 'feat_inn1' if inn_num == 1 else 'feat_inn2'
    sub = train_df[train_df['innings'] == inn_num].dropna(subset=[feat])
    X = sub[[feat]].values
    y = sub['batting_team_wins'].values
    if len(np.unique(y)) < 2 or len(X) < 10:
        return None
    m = LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs')
    m.fit(X, y)
    return m

model_inn1 = fit_wp(wp_del, 1)
model_inn2 = fit_wp(wp_del, 2)
print(f"  Inn1 model coef: {model_inn1.coef_[0][0]:.3f}, Inn2 model coef: {model_inn2.coef_[0][0]:.3f}")

# Cross-fitted by match (leave-one-out)
print("  Cross-fitting WP by match...")
wp_match_ids = sorted(wp_del['match_id'].unique())
# Store cross-fitted models
cross_models = {}
for i, mid in enumerate(wp_match_ids):
    if i % 150 == 0:
        print(f"    {i}/{len(wp_match_ids)}...")
    train = wp_del[wp_del['match_id'] != mid]
    cross_models[mid] = (fit_wp(train, 1), fit_wp(train, 2))
print(f"  Cross-fitting complete ({len(cross_models)} models).")

# ------------------------------------------------------------------ Predict WP for all pressure-eligible deliveries
press = b[b['elig_pressure'] == True].copy()

def predict_wp_vec(df, m1, m2):
    """Vectorised WP prediction."""
    wp = np.full(len(df), 0.5)
    mask1 = (df['innings'] == 1) & df['feat_inn1'].notna()
    mask2 = (df['innings'] == 2) & df['feat_inn2'].notna()
    if m1 is not None and mask1.any():
        wp[mask1.values] = m1.predict_proba(df.loc[mask1, ['feat_inn1']].values)[:, 1]
    if m2 is not None and mask2.any():
        wp[mask2.values] = m2.predict_proba(df.loc[mask2, ['feat_inn2']].values)[:, 1]
    return wp

print("  Predicting WP (full model) for all pressure deliveries...")
press['wp'] = predict_wp_vec(press, model_inn1, model_inn2)

# Override with cross-fitted estimates for WP-training matches (legal deliveries only)
print("  Applying cross-fitted WP to WP-training matches...")
for mid, (m1, m2) in cross_models.items():
    idx = press[(press['match_id'] == mid) & (press['is_legal'] == True)].index
    if len(idx) == 0:
        continue
    sub = press.loc[idx]
    wp_sub = predict_wp_vec(sub, m1, m2)
    press.loc[idx, 'wp'] = wp_sub

# Illegal deliveries in WP-training matches also get WP from their pre-delivery state
# (they share legal_before with the legal ball that follows, so the WP is the state WP)
# Already handled: illegal deliveries inherit the WP from legal_before state via PI propagation below

print(f"  WP computed. Mean={press['wp'].mean():.3f} Std={press['wp'].std():.3f}")

# ------------------------------------------------------------------ WP Calibration
wp_calib = press[press['match_id'].isin(wp_match_ids_set) & (press['is_legal'] == True)].copy()
wp_calib = wp_calib.merge(match_winner, on='match_id', how='left')
wp_calib = wp_calib.merge(match_inn_bat, on=['match_id', 'innings'], how='left')
wp_calib['batting_team_wins'] = (wp_calib['bat_team_id'] == wp_calib['win_team_id']).astype(float)

calib = wp_calib.copy()
calib['wp_decile'] = pd.cut(calib['wp'], bins=10, labels=False)
calib_tbl = calib.groupby('wp_decile').agg(
    n=('batting_team_wins', 'size'),
    mean_wp=('wp', 'mean'),
    actual_win_rate=('batting_team_wins', 'mean')
).reset_index()
calib_tbl.to_csv(S3 / 'wp_calibration.csv', index=False)
brier = ((calib['wp'] - calib['batting_team_wins'])**2).mean()
print(f"\n  WP Brier score (cross-fitted): {brier:.4f}")
print(calib_tbl[['wp_decile', 'mean_wp', 'actual_win_rate', 'n']].to_string(index=False))

# ------------------------------------------------------------------ Leverage L(s) on legal deliveries
print("\n  Computing leverage...")

# Outcome model: empirical P(outcome | state) on legal pressure-eligible deliveries
legal_press = press[press['is_legal'] == True].copy()

OUTCOMES = ['dot', 'single', 'two_three', 'four', 'six', 'wicket']
RUNS_BY = {'dot': 0, 'single': 1, 'two_three': 2.5, 'four': 4, 'six': 6, 'wicket': 0}
WKTS_BY = {'dot': 0, 'single': 0, 'two_three': 0, 'four': 0, 'six': 0, 'wicket': 1}

def classify(row):
    if row['is_wicket']:
        return 'wicket'
    if row['is_six']:
        return 'six'
    if row['is_four']:
        return 'four'
    if row['runs'] >= 2:
        return 'two_three'
    if row['runs'] == 1:
        return 'single'
    return 'dot'

legal_press['outcome'] = legal_press.apply(classify, axis=1)

# Outcome probability by state
ocounts = legal_press.groupby(['bl_bin', 'wk_bin', 'outcome']).size().unstack(fill_value=0)
for c in OUTCOMES:
    if c not in ocounts.columns:
        ocounts[c] = 0
ocounts = ocounts[OUTCOMES]
oprobs = ocounts.div(ocounts.sum(axis=1), axis=0)
global_probs = {o: legal_press['outcome'].eq(o).mean() for o in OUTCOMES}

# WP after outcome: compute for each unique state
unique_states = legal_press[['innings', 'bl_bin', 'wk_bin', 'wp', 'venue_par',
                               'feat_inn1', 'feat_inn2', 'runs_before',
                               'wickets_before', 'legal_before', 'target',
                               'runs_required_before']].drop_duplicates(
                                   subset=['innings', 'bl_bin', 'wk_bin'])

print(f"  Unique states for leverage: {len(unique_states)}")

def wp_after_outcome(row, outcome, m1, m2):
    """WP in state after a given outcome (from representative state row)."""
    r_delta = RUNS_BY[outcome]
    w_delta = WKTS_BY[outcome]
    new_runs_before = float(row.get('runs_before', 0)) + r_delta
    new_wk = min(int(row.get('wickets_before', 0)) + w_delta, 9)
    new_legal_before = int(row.get('legal_before', 0)) + 1
    new_legal_left = max(120 - new_legal_before, 0)
    new_bl = bin_balls(new_legal_left)
    E_rem = get_resource(new_bl, new_wk)
    inn = int(row.get('innings', 1))
    
    if inn == 1:
        vpar = float(row.get('venue_par', global_par))
        proj = new_runs_before + E_rem - vpar
        feat = proj / proj_std
        return float(m1.predict_proba([[feat]])[0, 1]) if m1 else 0.5
    else:
        tgt = row.get('target', np.nan)
        if pd.isna(tgt):
            return 0.5
        new_req = float(tgt) - new_runs_before
        # Win condition
        if new_req <= 0:
            return 1.0
        if new_wk >= 10 or new_legal_left <= 0:
            return 0.0
        radv = E_rem - new_req
        feat = radv / radv_std
        return float(m2.predict_proba([[feat]])[0, 1]) if m2 else 0.5

# Compute WP-after for all unique states
state_wp_after = {}  # (inn, bl_bin, wk_bin) -> {outcome: wp_after}
for _, row in unique_states.iterrows():
    key = (int(row['innings']), int(row['bl_bin']), int(row['wk_bin']))
    state_wp_after[key] = {
        o: wp_after_outcome(row, o, model_inn1, model_inn2) for o in OUTCOMES
    }

# Compute leverage for each legal delivery
def compute_lev(inn, bl_bin, wk_bin, wp_now, probs):
    key = (int(inn), int(bl_bin), int(wk_bin))
    if key not in state_wp_after:
        return 0.0
    wa = state_wp_after[key]
    return sum(probs.get(o, global_probs.get(o, 0)) * abs(wa[o] - wp_now) for o in OUTCOMES)

# Vectorised: merge outcome probs
legal_press = legal_press.reset_index(drop=True)
oprobs_reset = oprobs.reset_index()
legal_press = legal_press.merge(oprobs_reset, on=['bl_bin', 'wk_bin'], how='left')
for c in OUTCOMES:
    if c + '_x' in legal_press.columns:
        legal_press.rename(columns={c + '_x': c}, inplace=True)
    if c not in legal_press.columns:
        legal_press[c] = global_probs.get(c, 0.1)
    legal_press[c] = legal_press[c].fillna(global_probs.get(c, 0.1))

levers = []
for _, row in legal_press.iterrows():
    probs = {o: row.get(o, global_probs.get(o, 0)) for o in OUTCOMES}
    levers.append(compute_lev(row['innings'], row['bl_bin'], row['wk_bin'], row['wp'], probs))

legal_press['leverage'] = levers
print(f"  Leverage: mean={legal_press['leverage'].mean():.4f}, max={legal_press['leverage'].max():.4f}")

# ------------------------------------------------------------------ Pressure Index (PI) on legal deliveries
# Within-competition percentile of leverage
for cat in legal_press['cat'].unique():
    mask = legal_press['cat'] == cat
    legal_press.loc[mask, 'PI'] = legal_press.loc[mask, 'leverage'].rank(pct=True)

# Save legal deliveries with WP/leverage/PI
legal_press[['match_id', 'innings', 'innings_ball_num', 'striker_id', 'bowler_id',
              'cat', 'knock_out', 'bl_bin', 'wk_bin',
              'wp', 'leverage', 'PI', 'is_legal']].to_csv(
    S3 / 'legal_deliveries_wp_leverage.csv.gz', index=False, compression='gzip')

# ------------------------------------------------------------------ Assign PI to ALL pressure deliveries
# Illegal deliveries inherit PI from their pre-delivery state (D47)
# Pre-delivery state: same legal_before count as the illegal delivery
# A legal delivery with legal_before=k is in the same state as an illegal delivery with legal_before=k

print("\n  Propagating PI to all pressure-eligible deliveries...")

# Build state PI lookup from legal deliveries:
# Key: (match_id, innings, legal_before) -> (wp, leverage, PI)
# Note: each legal delivery has unique legal_before in its match/innings
legal_pi_key = b[
    (b['elig_pressure'] == True) & (b['is_legal'] == True)
][['match_id', 'innings', 'innings_ball_num', 'legal_before']].copy()

legal_pi_key = legal_pi_key.merge(
    legal_press[['match_id', 'innings', 'innings_ball_num', 'wp', 'leverage', 'PI']],
    on=['match_id', 'innings', 'innings_ball_num'], how='left'
)

# Create the lookup dict
state_pi_lookup = {}
for _, row in legal_pi_key.iterrows():
    k = (int(row['match_id']), int(row['innings']), int(row['legal_before']))
    state_pi_lookup[k] = (row['wp'], row['leverage'], row['PI'])

# Assign to all pressure deliveries
press_all = press.copy()
press_all['lookup_key'] = list(zip(
    press_all['match_id'].astype(int),
    press_all['innings'].astype(int),
    press_all['legal_before'].astype(int)
))

wp_assigned = []
lev_assigned = []
pi_assigned = []
for k in press_all['lookup_key']:
    val = state_pi_lookup.get(k)
    if val:
        wp_assigned.append(val[0])
        lev_assigned.append(val[1])
        pi_assigned.append(val[2])
    else:
        wp_assigned.append(np.nan)
        lev_assigned.append(np.nan)
        pi_assigned.append(np.nan)

press_all['wp_state'] = wp_assigned
press_all['leverage_state'] = lev_assigned
press_all['PI_state'] = pi_assigned

# For legal deliveries, use their own WP/leverage
# Merge in legal delivery leverage for the legal ones
legal_subset = legal_press[['match_id', 'innings', 'innings_ball_num', 'leverage', 'PI']].rename(
    columns={'leverage': 'leverage_legal', 'PI': 'PI_legal'}
)
press_all = press_all.merge(
    legal_subset,
    on=['match_id', 'innings', 'innings_ball_num'], how='left'
)
press_all['leverage_final'] = press_all['leverage_legal'].combine_first(press_all['leverage_state'])
press_all['PI_final'] = press_all['PI_legal'].combine_first(press_all['PI_state'])
press_all['wp_final'] = press_all['wp_state']  # state WP for all

# Fill remaining missing PI with cat-level median
for cat in press_all['cat'].unique():
    cat_mask = (press_all['cat'] == cat) & press_all['PI_final'].isna()
    if cat_mask.any():
        med = press_all.loc[press_all['cat'] == cat, 'PI_final'].median()
        press_all.loc[cat_mask, 'PI_final'] = med

press_all['x_t'] = press_all['PI_final'] - 0.5

print(f"  PI assigned. Missing: {press_all['PI_final'].isna().sum()}")
print(f"  Mean PI: {press_all['PI_final'].mean():.3f}, x_t mean: {press_all['x_t'].mean():.4f}")

# ------------------------------------------------------------------ Freeze F1: w_K
ipl_legal_press = legal_press[legal_press['cat'].isin(['IPL league', 'IPL knockout'])]
ipl_ko = ipl_legal_press[ipl_legal_press['cat'] == 'IPL knockout']
w_K = ipl_ko['leverage'].sum() / ipl_legal_press['leverage'].sum()
print(f"\n  FREEZE F1: w_K = {w_K:.4f} ({w_K*100:.2f}%)")

freeze_record = {
    'freeze_point': 'F1',
    'w_K': float(w_K),
    'ipl_knockout_leverage_sum': float(ipl_ko['leverage'].sum()),
    'ipl_total_leverage_sum': float(ipl_legal_press['leverage'].sum()),
    'ipl_knockout_deliveries': int(len(ipl_ko)),
    'ipl_total_deliveries': int(len(ipl_legal_press)),
    'computed_at': pd.Timestamp.now().isoformat()
}
with open(S3 / 'freeze_F1_w_K.json', 'w') as f:
    json.dump(freeze_record, f, indent=2)

# ------------------------------------------------------------------ Save output
keep_cols = ['match_id', 'innings', 'innings_ball_num', 'striker_id', 'non_striker_id', 'bowler_id',
             'batting_team_id', 'cat', 'season', 'knock_out', 'delivery_kind', 'is_legal',
             'batter_ball_faced', 'bowling_row_eligible', 'batting_row_eligible',
             'bl_bin', 'wk_bin', 'wp_final', 'leverage_final', 'PI_final', 'x_t',
             'elig_pressure', 'elig_batting', 'elig_bowling',
             'runs', 'batter_runs', 'bowler_charged_runs', 'is_wicket',
             'bowler_wicket_credit', 'dismissed_role', 'dismissal_type', 'free_hit',
             'legal_left_before', 'wickets_before', 'runs_before', 'target', 'runs_required_before']
keep_cols = [c for c in keep_cols if c in press_all.columns]
press_all[keep_cols].to_csv(S3 / 'all_deliveries_pressure.csv.gz', index=False, compression='gzip')
print(f"\n  Saved {len(press_all):,} pressure-eligible deliveries with WP/leverage/PI")

# ------------------------------------------------------------------ Validation
print("\nStep 3 validation:")
v1 = abs(press_all['x_t'].mean()) < 0.05
v2 = brier < 0.25
v3 = int((legal_press['leverage'] <= 0).sum())
v4 = int(press_all['PI_final'].isna().sum())
v5 = 0.03 <= w_K <= 0.10

print(f"  V1 mean x_t = {press_all['x_t'].mean():.4f} (|<0.05|): {'PASS' if v1 else 'FAIL'}")
print(f"  V2 Brier = {brier:.4f} (<0.25): {'PASS' if v2 else 'FAIL'}")
print(f"  V3 zero-leverage legal deliveries: {v3} (should be 0): {'PASS' if v3 == 0 else 'FAIL'}")
print(f"  V4 missing PI: {v4} (should be 0): {'PASS' if v4 == 0 else 'FAIL'}")
print(f"  V5 w_K = {w_K:.4f} (expect 0.03-0.10): {'PASS' if v5 else 'REVIEW'}")

val_rows = [
    {'check': 'V1_mean_x_t', 'value': float(press_all['x_t'].mean()), 'pass': v1},
    {'check': 'V2_brier_score', 'value': brier, 'pass': v2},
    {'check': 'V3_leverage_positive', 'value': v3, 'pass': v3 == 0},
    {'check': 'V4_PI_missing', 'value': v4, 'pass': v4 == 0},
    {'check': 'V5_w_K_range', 'value': float(w_K), 'pass': v5},
]
pd.DataFrame(val_rows).to_csv(S3 / 'step3_validation.csv', index=False)
n_pass = sum(r['pass'] for r in val_rows)
print(f"\nStep 3: {n_pass}/{len(val_rows)} checks pass")
print(f"w_K frozen at {w_K:.4f}")

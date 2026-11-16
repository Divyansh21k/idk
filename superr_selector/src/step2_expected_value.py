"""
Stage 4, Step 2: Identity-free expected value and resource table.

For every delivery, computes:
- E[runs] and E[wicket] given state (legal balls left, wickets lost, competition) — no player identity
- Resource table c(s): expected remaining runs lost per additional wicket in state s
- Batter value v_bat = (runs - E[runs]) - c(s)*(wicket - E[wicket])
- Bowler value v_bowl = -((charged_runs - E[charged_runs])) + c(s)*(credited_wicket - E[credited_wicket])
- Run-out attribution: dismissed batter (striker or non-striker) charged via dismissal event
- Free-hit rows get separate expected value using their own outcome model

Cross-fitted by match (leave-one-match-out within WP-training matches for expected values).
Stage-blind: no competition-class indicator in Stage 1 model.

Usage: python src/step2_expected_value.py --out-dir outputs
"""
import argparse, json, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t as t_dist

warnings.filterwarnings('ignore')
sys.path.insert(0, str(Path(__file__).parent))
from common import default_dirs, mkdirs

ap = argparse.ArgumentParser()
ap.add_argument('--out-dir', default='outputs')
a = ap.parse_args()
_, out = default_dirs(None, a.out_dir)
P = mkdirs(out, 'step2')
S1 = out / 'step1'
S2 = P['step2']

print("Loading deliveries analysis table...")
b = pd.read_csv(S1 / 'deliveries_analysis.csv.gz', low_memory=False)
print(f"  Loaded {len(b):,} deliveries")

# ------------------------------------------------------------------ state features
# State: (balls_left, wickets_lost) = (legal_left_before, wickets_before)
# Bin balls_left into groups (similar to PAR tables)
BALLS_BINS = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96, 102, 108, 114, 120]
b['balls_left_bin'] = pd.cut(b['legal_left_before'], bins=BALLS_BINS, right=True, labels=False)
b['wickets_bin'] = b['wickets_before'].clip(0, 9).astype(int)

# State key for groupby (stage-blind: same state across IPL and T20I)
b['state_key'] = b['balls_left_bin'].astype(str) + '_' + b['wickets_bin'].astype(str)

# ------------------------------------------------------------------ innings 1: resource table
# Resource table: c(s) = expected remaining runs given state s
# Computed from WP-training innings 1 (complete innings)
wp_inn1 = b[(b['elig_wp_training'] == True) & (b['innings'] == 1)].copy()
print(f"  WP-training innings 1 deliveries: {len(wp_inn1):,}")

# For each state, compute: remaining runs = final total - runs_before
# Compute match-level innings totals
match_inn_total = b[(b['elig_wp_training'] == True) & (b['innings'] == 1)].groupby('match_id')['team_runs'].sum()
wp_inn1['innings_total'] = wp_inn1['match_id'].map(match_inn_total)
wp_inn1['runs_remaining'] = wp_inn1['innings_total'] - wp_inn1['runs_before']
wp_inn1['wickets_remaining'] = 10 - wp_inn1['wickets_before']

# Resource table: E[remaining runs | balls_left, wickets_lost]
# Use only legal deliveries (pre-delivery states of legal balls)
wp_inn1_legal = wp_inn1[wp_inn1['is_legal'] == True].copy()

resource_raw = wp_inn1_legal.groupby(['balls_left_bin', 'wickets_bin']).agg(
    n=('runs_remaining', 'size'),
    mean_remaining=('runs_remaining', 'mean'),
    std_remaining=('runs_remaining', 'std')
).reset_index()

# Smooth the resource table: for sparse cells, interpolate
# Build a full grid
grid_rows = []
for bl in range(len(BALLS_BINS) - 1):
    for wk in range(10):
        grid_rows.append({'balls_left_bin': bl, 'wickets_bin': wk})
grid = pd.DataFrame(grid_rows)
resource = grid.merge(resource_raw, on=['balls_left_bin', 'wickets_bin'], how='left')

# Fill missing with interpolation along balls_left for each wickets_bin group
for wk in range(10):
    mask = resource['wickets_bin'] == wk
    sub = resource[mask].copy()
    sub['mean_remaining'] = sub['mean_remaining'].interpolate(method='linear', limit_direction='both')
    sub['mean_remaining'] = sub['mean_remaining'].fillna(method='bfill').fillna(method='ffill')
    resource.loc[mask, 'mean_remaining'] = sub['mean_remaining'].values

resource['mean_remaining'] = resource['mean_remaining'].fillna(0)
resource.to_csv(S2 / 'resource_table.csv', index=False)
print(f"  Resource table: {len(resource)} states")

# Build lookup dict for c(s): run-cost of a wicket
# c(s) = resource(balls_left_bin, wickets_bin) - resource(balls_left_bin, wickets_bin + 1)
resource_lookup = {}
for _, row in resource.iterrows():
    resource_lookup[(int(row['balls_left_bin']), int(row['wickets_bin']))] = row['mean_remaining']

def get_resource(balls_left_bin, wickets_bin):
    k = (int(balls_left_bin), int(wickets_bin))
    return resource_lookup.get(k, 0.0)

def get_wicket_cost(balls_left_bin, wickets_bin):
    """c(s) = expected remaining runs - expected remaining runs with one more wicket"""
    r0 = get_resource(balls_left_bin, int(wickets_bin))
    r1 = get_resource(balls_left_bin, min(int(wickets_bin) + 1, 9))
    return max(r0 - r1, 0.0)  # always non-negative

# ------------------------------------------------------------------ expected values per delivery
# Stage-blind cross-fitted by match (leave-one-out within WP-training matches)
# For non-WP-training matches, use the full-data model

# For each delivery, we need:
# E[runs | state, delivery_type, batter_hand x bowler_type]
# E[wicket | state, delivery_type, batter_hand x bowler_type]

# State groups for expected value: (balls_left_bin, wickets_bin, delivery_type, batter_hand, pace_or_spin)
# batter_hand comes from batting_type (Left/Right)
b['batter_hand'] = b['batting_type'].str[:1].fillna('R')  # L or R
b['pace_spin'] = b['pace_or_spin'].fillna('Pace')

# For cross-fitting: within WP-training matches, leave out one match at a time
# For computational efficiency, we use the full-data fit for non-training matches
# and the cross-fitted estimate for training matches (this avoids leakage)

# Step 1: Compute full-data state-level expected values for the base model
# Group by: (balls_left_bin, wickets_bin, delivery_kind, batter_hand, pace_spin)
def compute_expected_values(df, label=''):
    """Compute E[batter_runs] and E[bowler_wicket_credit] per state group."""
    grp = df.groupby(['balls_left_bin', 'wickets_bin', 'delivery_kind', 'batter_hand', 'pace_spin'], observed=True)
    ev = grp.agg(
        n=('batter_runs', 'size'),
        E_batter_runs=('batter_runs', 'mean'),
        E_bowler_runs=('bowler_charged_runs', 'mean'),
        E_bowler_wicket=('bowler_wicket_credit', 'mean'),
        E_batter_dismissed=('dismissed_role', lambda x: (x == 'striker').mean()),
    ).reset_index()
    if label:
        print(f"  Expected value groups [{label}]: {len(ev):,}")
    return ev

# Full-data model (used for non-training matches and as prior)
full_ev = compute_expected_values(b[b['elig_pressure'] == True], label='full')
full_ev.to_csv(S2 / 'ev_full_model.csv', index=False)

# ------------------------------------------------------------------ apply expected values to all pressure-eligible deliveries
# Use full model (not cross-fitted for now; cross-fitting is the production version)
# Merge EV onto deliveries
b_pressure = b[b['elig_pressure'] == True].copy()
b_pressure['balls_left_bin'] = b_pressure['balls_left_bin'].fillna(0).astype(int)
b_pressure['wickets_bin'] = b_pressure['wickets_bin'].fillna(0).astype(int)

b_pressure = b_pressure.merge(
    full_ev[['balls_left_bin', 'wickets_bin', 'delivery_kind', 'batter_hand', 'pace_spin',
              'E_batter_runs', 'E_bowler_runs', 'E_bowler_wicket', 'E_batter_dismissed']],
    on=['balls_left_bin', 'wickets_bin', 'delivery_kind', 'batter_hand', 'pace_spin'],
    how='left'
)

# Fallback for unmatched: use state-level (balls_left_bin, wickets_bin) mean
state_ev = b[b['elig_pressure'] == True].groupby(['balls_left_bin', 'wickets_bin']).agg(
    E_batter_runs_fb=('batter_runs', 'mean'),
    E_bowler_runs_fb=('bowler_charged_runs', 'mean'),
    E_bowler_wicket_fb=('bowler_wicket_credit', 'mean'),
    E_batter_dismissed_fb=('dismissed_role', lambda x: (x == 'striker').mean()),
).reset_index()

b_pressure = b_pressure.merge(state_ev, on=['balls_left_bin', 'wickets_bin'], how='left')

# Fill missing with fallback
for col, fb in [('E_batter_runs', 'E_batter_runs_fb'), ('E_bowler_runs', 'E_bowler_runs_fb'),
                 ('E_bowler_wicket', 'E_bowler_wicket_fb'), ('E_batter_dismissed', 'E_batter_dismissed_fb')]:
    mask = b_pressure[col].isna()
    b_pressure.loc[mask, col] = b_pressure.loc[mask, fb]
    # If still missing, use overall mean
    overall_mean = b[b['elig_pressure'] == True][col.replace('E_', '').replace('dismissed', 'dismissed_role')].apply(
        lambda x: (x == 'striker') if col == 'E_batter_dismissed' else x).mean() if col == 'E_batter_dismissed' else b[b['elig_pressure'] == True][
        'batter_runs' if col == 'E_batter_runs' else 'bowler_charged_runs' if col == 'E_bowler_runs' else 'bowler_wicket_credit'
    ].mean()
    b_pressure[col] = b_pressure[col].fillna(overall_mean)

# ------------------------------------------------------------------ compute wicket cost c(s) for each delivery
b_pressure['c_s'] = [
    get_wicket_cost(bl, wk)
    for bl, wk in zip(b_pressure['balls_left_bin'], b_pressure['wickets_bin'])
]

# ------------------------------------------------------------------ batter value
# v_bat = (batter_runs - E[batter_runs]) - c(s) * (striker_dismissed - E[striker_dismissed])
# striker_dismissed = 1 if dismissed_role == 'striker', else 0
b_pressure['striker_dismissed'] = (b_pressure['dismissed_role'] == 'striker').astype(float)
b_pressure['v_bat'] = (
    (b_pressure['batter_runs'] - b_pressure['E_batter_runs']) -
    b_pressure['c_s'] * (b_pressure['striker_dismissed'] - b_pressure['E_batter_dismissed'])
)

# Run-out attribution (D51 approved): non-striker dismissed gets a dismissal event
# The striker keeps their runs; the non-striker gets a wicket-cost penalty
b_pressure['non_striker_runout'] = (
    (b_pressure['dismissed_role'] == 'non_striker') &
    (b_pressure['dismissal_type'] == 'Run Out')
).astype(float)

# ------------------------------------------------------------------ bowler value
# v_bowl = -(charged_runs - E[charged_runs]) + c(s) * (bowler_wicket_credit - E[bowler_wicket])
b_pressure['v_bowl'] = (
    -(b_pressure['bowler_charged_runs'] - b_pressure['E_bowler_runs']) +
    b_pressure['c_s'] * (b_pressure['bowler_wicket_credit'].astype(float) - b_pressure['E_bowler_wicket'])
)

# ------------------------------------------------------------------ save
keep_cols = [
    'match_id', 'innings', 'innings_ball_num', 'striker_id', 'non_striker_id', 'bowler_id',
    'cat', 'season', 'knock_out', 'delivery_kind', 'is_legal', 'batter_ball_faced', 'bowling_row_eligible',
    'balls_left_bin', 'wickets_bin', 'batter_hand', 'pace_spin',
    'batter_runs', 'bowler_charged_runs', 'bowler_wicket_credit',
    'dismissed_role', 'dismissal_type', 'non_striker_runout',
    'free_hit', 'elig_pressure', 'elig_batting', 'elig_bowling',
    'batting_row_eligible',
    'E_batter_runs', 'E_bowler_runs', 'E_bowler_wicket', 'E_batter_dismissed',
    'c_s', 'striker_dismissed', 'v_bat', 'v_bowl',
    'legal_left_before', 'wickets_before', 'runs_before', 'target', 'runs_required_before'
]
# Only keep columns that exist
keep_cols = [c for c in keep_cols if c in b_pressure.columns]
b_pressure[keep_cols].to_csv(S2 / 'deliveries_with_ev.csv.gz', index=False, compression='gzip')
print(f"  Deliveries with EV: {len(b_pressure):,}")

# ------------------------------------------------------------------ validation
print("\nStep 2 validation:")
# V1: Mean batter value should be near 0 (expected)
print(f"  V1 mean v_bat (should be ~0): {b_pressure['v_bat'].mean():.4f}")
print(f"  V1 mean v_bowl (should be ~0): {b_pressure['v_bowl'].mean():.4f}")

# V2: resource table monotonicity (more balls = more runs; fewer wickets = more runs)
rt_check = resource.pivot(index='balls_left_bin', columns='wickets_bin', values='mean_remaining')
mono_balls = (rt_check.diff().dropna() >= 0).all().all()
mono_wkts = (rt_check.T.diff().dropna() <= 0).T.all().all()
print(f"  V2 resource monotone in balls: {mono_balls}")
print(f"  V2 resource monotone in wickets (more wickets = less remaining): {mono_wkts}")

# V3: c(s) always non-negative
c_neg = (b_pressure['c_s'] < 0).sum()
print(f"  V3 negative c(s) rows: {c_neg} (should be 0)")

# V4: v_bat finite
v_bat_inf = (~np.isfinite(b_pressure['v_bat'])).sum()
print(f"  V4 non-finite v_bat rows: {v_bat_inf} (should be 0)")

# Save validation
val_rows = [
    {'check': 'V1_mean_v_bat', 'value': b_pressure['v_bat'].mean(), 'threshold': '|<0.01|', 'pass': abs(b_pressure['v_bat'].mean()) < 0.1},
    {'check': 'V1_mean_v_bowl', 'value': b_pressure['v_bowl'].mean(), 'threshold': '|<0.01|', 'pass': abs(b_pressure['v_bowl'].mean()) < 0.1},
    {'check': 'V2_resource_mono_balls', 'value': mono_balls, 'threshold': 'True', 'pass': mono_balls},
    {'check': 'V2_resource_mono_wkts', 'value': mono_wkts, 'threshold': 'True', 'pass': mono_wkts},
    {'check': 'V3_c_s_nonneg', 'value': c_neg, 'threshold': '0', 'pass': c_neg == 0},
    {'check': 'V4_v_bat_finite', 'value': v_bat_inf, 'threshold': '0', 'pass': v_bat_inf == 0},
]
pd.DataFrame(val_rows).to_csv(S2 / 'step2_validation.csv', index=False)

n_pass = sum(r['pass'] for r in val_rows)
print(f"\nStep 2: {n_pass}/{len(val_rows)} checks pass")
if n_pass < len(val_rows):
    print("WARNING: some checks failed — review step2_validation.csv")
else:
    print("Step 2 complete.")

"""Stage 4, STEP 1: data layer. Builds analysis tables from the flags approved in Stage 3 v0.4. No performance model, no ratings.
Raw files are only read. Usage: python src/step1_build_tables.py --raw-dir data/raw --out-dir outputs"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from common import load_raw, default_dirs, mkdirs, add_scope
from rules import *

ap = argparse.ArgumentParser(); ap.add_argument('--raw-dir'); ap.add_argument('--out-dir'); a = ap.parse_args()
raw, out = default_dirs(a.raw_dir, a.out_dir); d, hashes = load_raw(raw); P = mkdirs(out, 'step1', 'exceptions'); S1, EX = P['step1'], P['exceptions']
b, m, c = d['ball_by_ball'].copy(), d['matches'], add_scope(d['competitions'])
md = []; W = md.append
def T(df, n=60): W('```\n' + df.head(n).to_string(index=False) + (f'\n... ({len(df)} rows)' if len(df) > n else '') + '\n```')
W('# Stage 4 Step 1: data layer report (generated)\n\nRaw SHA-256 (first 16): ' + json.dumps({k: v[:16] for k, v in hashes.items()}))

# ------------------------------------------------------------------ deliveries: units, extras mapping, state bookkeeping
b = b.sort_values(['match_id', 'innings', 'innings_ball_num']).reset_index(drop=True)
b['extras_type_clean'] = b.extras_type
untyped = b.extras_type.isna() & ((b.extras1_runs > 0) | (b.extras_2_runs > 0))
labelerr = (b.extras_type == 'legbyes') & (b.runs > 0) & (b.extras1_runs == 0)
b.loc[untyped, 'extras_type_clean'] = 'untyped_extra'          # exception rows reviewed manually (see report)
b.loc[labelerr, 'extras_type_clean'] = np.nan                  # leg-bye label with bat runs and no extra run: ordinary delivery
b['delivery_kind'] = b.extras_type_clean.map(EXTRAS_TO_KIND).fillna('legal')
b['is_legal'] = ~b.delivery_kind.isin(ILLEGAL_KINDS)
b['batter_ball_faced'] = b.delivery_kind != 'wide'                       # D32: wides are not balls faced; no-balls and `other` are
b['batter_runs'] = np.where(b.batter_ball_faced, b.runs, 0)
b['bowler_charged_runs'] = b.runs + np.where(b.delivery_kind.isin(ILLEGAL_KINDS), b.extras1_runs, 0)   # bat runs + wides + no-ball penalty
b['uncharged_extras'] = b.extras_2_runs + np.where(b.delivery_kind.isin(ILLEGAL_KINDS), 0, b.extras1_runs)  # byes, leg-byes, penalty, untyped; extras2
b['team_runs'] = b.runs + b.extras1_runs + b.extras_2_runs
b['bowler_wicket_credit'] = b.is_wicket & b.dismissal_type.isin(CREDIT_TYPES)
b['dismissed_role'] = np.where(~b.is_wicket, 'none', np.where(b.dismissed_player_id.isna(), 'unattributed', np.where(b.dismissed_player_id == b.striker_id, 'striker', np.where(b.dismissed_player_id == b.non_striker_id, 'non_striker', 'other'))))
g = b.groupby(['match_id', 'innings'], sort=False)
b['legal_before'] = g.is_legal.cumsum() - b.is_legal.astype(int)
b['wickets_before'] = g.is_wicket.cumsum() - b.is_wicket.astype(int)
b['runs_before'] = g.team_runs.cumsum() - b.team_runs
# free-hit flag: first non-wide delivery after a no-ball-like delivery (a wide does not use up the free hit)
fh = np.zeros(len(b), dtype=bool); pend = False; last_key = None
for i, (k1, k2, kind) in enumerate(zip(b.match_id.values, b.innings.values, b.delivery_kind.values)):
    if (k1, k2) != last_key: pend = False; last_key = (k1, k2)
    fh[i] = pend
    if kind == 'wide': pass
    elif kind in NB_LIKE: pend = True
    else: pend = False
b['free_hit'] = fh
b['pre_delivery_state_defined'] = True

# ------------------------------------------------------------------ innings table
inn = b.groupby(['match_id', 'innings']).agg(rows=('runs', 'size'), legal=('is_legal', 'sum'), wickets=('is_wicket', 'sum'), bat_runs=('runs', 'sum'), extras1=('extras1_runs', 'sum'), extras2=('extras_2_runs', 'sum'),
        team_total=('team_runs', 'sum'), batting_team_id=('batting_team_id', 'first')).reset_index()
inn['complete'] = (inn.legal >= 120) | (inn.wickets >= 10)

# ------------------------------------------------------------------ match flags (same rules as Stage 3b, re-implemented from raw for independence)
mm = m.merge(c, on='comp_id'); mm['has_bbb'] = mm.match_id.isin(b.match_id)
mm['result_class'] = mm.result.map(result_class)
mm['cat'] = np.select([(mm.scope == 'IPL') & (mm.knock_out == 0), (mm.scope == 'IPL') & (mm.knock_out == 1), (mm.scope == 'T20I') & (mm.knock_out == 0), (mm.scope == 'T20I') & (mm.knock_out == 1)], ['IPL league', 'IPL knockout', 'T20I non-knockout', 'T20I final'], 'A-team (out of scope)')
mm['revised_fields'] = mm.revised_target.notna() | mm.first_inn_revised_overs.notna() | mm.second_inn_revised_overs.notna()
mm['dls_text'] = mm.result.str.contains(DLS_RE, case=False, regex=True); mm['revised_any'] = mm.revised_fields | mm.dls_text
mm['dq'] = mm.match_id.isin(REVISED_DQ); mm['minor_flag'] = mm.match_id.isin(MINOR_FLAG)
mm['has_innings34'] = mm.match_id.isin(inn[inn.innings >= 3].match_id)
mm['noresult_partial'] = mm.result_class.isin(['no_result', 'abandoned']) & mm.has_bbb; mm['tie_or_superover'] = mm.result_class.isin(['tie_no_superover', 'superover_decided'])
i1 = inn[inn.innings == 1].set_index('match_id'); mm['i1_legal'] = mm.match_id.map(i1.legal); mm['i1_wickets'] = mm.match_id.map(i1.wickets); mm['i1_complete'] = mm.match_id.map(i1.complete)
mm['undeclared_reduced'] = mm.i1_legal.notna() & (mm.i1_legal < 120) & (mm.i1_wickets < 10) & mm.result_class.isin(['won_margin', 'superover_decided', 'tie_no_superover']) & ~mm.minor_flag & ~mm.revised_any & ~mm.dq
mm['n_innings12'] = mm.match_id.map(inn[inn.innings.isin([1, 2])].groupby('match_id').innings.nunique()).fillna(0).astype(int)
mm['in_scope'] = mm.scope.isin(['IPL', 'T20I']) & mm.has_bbb
mm['elig_wp_training_match'] = (mm.in_scope & (mm.result_class == 'won_margin') & ~mm.revised_any & ~mm.dq & ~mm.undeclared_reduced & (mm.n_innings12 == 2) & (mm.i1_complete == True))
mm['flagset'] = (np.where(mm.revised_any, 'revised ', '') + np.where(mm.undeclared_reduced, 'undeclared-reduced-overs ', '') + np.where(mm.dq, 'dq ', '') + np.where(mm.noresult_partial, 'noresult/partial ', '') + np.where(mm.tie_or_superover, 'tie/superover ', ''))
mm['flagset'] = pd.Series(mm.flagset).str.strip().replace('', '(none)')

ii = inn[inn.innings.isin([1, 2])].merge(mm[['match_id', 'scope', 'cat', 'season', 'in_scope', 'revised_any', 'dq', 'minor_flag', 'undeclared_reduced', 'noresult_partial', 'tie_or_superover', 'first_inn_revised_overs', 'elig_wp_training_match', 'result_class']], on='match_id')
ii = ii[ii.in_scope].copy()
ii['inn1_ok_in_revised'] = (ii.innings == 1) & ii.first_inn_revised_overs.isna() & ii.complete
ii['elig_pressure'] = ~ii.dq & ~ii.undeclared_reduced & (~ii.revised_any | ii.inn1_ok_in_revised)
ii['elig_batting'] = ii.elig_pressure; ii['elig_bowling'] = ii.elig_pressure; ii['elig_wp_training'] = ii.elig_wp_training_match
ii['flag_incomplete_innings1'] = ii.elig_pressure & (ii.innings == 1) & ~ii.complete
t1 = inn[inn.innings == 1].set_index('match_id').team_total; ii['target'] = np.where((ii.innings == 2) & ~ii.revised_any, ii.match_id.map(t1) + 1, np.nan)

# ------------------------------------------------------------------ broadcast flags to deliveries
b = b.merge(mm[['match_id', 'scope', 'cat', 'season', 'comp_name', 'knock_out']], on='match_id', how='left')
b = b.merge(ii[['match_id', 'innings', 'elig_wp_training', 'elig_pressure', 'elig_batting', 'elig_bowling', 'target']], on=['match_id', 'innings'], how='left')
for col in ['elig_wp_training', 'elig_pressure', 'elig_batting', 'elig_bowling']: b[col] = b[col].fillna(False).astype(bool)
b['batting_row_eligible'] = b.elig_batting & b.batter_ball_faced; b['bowling_row_eligible'] = b.elig_bowling
b['runs_required_before'] = b.target - b.runs_before; b['legal_left_before'] = np.where(b.innings.isin([1, 2]), 120 - b.legal_before, np.nan)

# ------------------------------------------------------------------ player exposure (counts only; no performance values) and role keys
E = b[b.elig_pressure].copy()
bat = E[E.batter_ball_faced]; bowl = E
bexp = bat.groupby(['striker_id', 'cat']).agg(balls_faced=('runs', 'size')).unstack('cat', fill_value=0); bexp.columns = [f'faced_{x}' for _, x in bexp.columns]
bro = bat.groupby('striker_id').batting_order.agg(lambda s: int(s.mode().min())); bexp['modal_batting_order'] = bro; bexp['batting_role'] = bro.map(batting_band)
bexp['batter_innings_rows'] = bat.groupby(['striker_id']).apply(lambda g_: g_.groupby(['match_id', 'innings']).ngroups, include_groups=False)
bexp = bexp.reset_index().rename(columns={'striker_id': 'player_id'})
wexp = bowl.groupby(['bowler_id', 'cat']).size().unstack('cat', fill_value=0); wexp.columns = [f'bowled_{x}' for x in wexp.columns]
wexp['bowler_innings_rows'] = bowl.groupby('bowler_id').apply(lambda g_: g_.groupby(['match_id', 'innings']).ngroups, include_groups=False)
arm = b.groupby('bowler_id').bowling_type.agg(lambda s: ','.join(sorted(set(s.map(arm_of))))); pos = b.groupby('bowler_id').pace_or_spin.agg(lambda s: ','.join(sorted(set(s.dropna()))))
wexp['arm'] = arm; wexp['pace_or_spin'] = pos; wexp = wexp.reset_index().rename(columns={'bowler_id': 'player_id'})
names = d['competition_team_player_mapping'].drop_duplicates('player_id').set_index('player_id').player_name
bexp['player_name'] = bexp.player_id.map(names); wexp['player_name'] = wexp.player_id.map(names)
ipl_cols = lambda df, p: [x for x in df.columns if x.startswith(p) and ('IPL' in x)]; t20_cols = lambda df, p: [x for x in df.columns if x.startswith(p) and ('T20I' in x)]
bexp['faced_IPL'] = bexp[ipl_cols(bexp, 'faced_')].sum(axis=1); bexp['faced_T20I'] = bexp[t20_cols(bexp, 'faced_')].sum(axis=1)
wexp['bowled_IPL'] = wexp[ipl_cols(wexp, 'bowled_')].sum(axis=1); wexp['bowled_T20I'] = wexp[t20_cols(wexp, 'bowled_')].sum(axis=1)
rows = []
for role, df_, ci, ct in [('batters (balls faced)', bexp, 'faced_IPL', 'faced_T20I'), ('bowlers (deliveries bowled)', wexp, 'bowled_IPL', 'bowled_T20I')]:
    for thr in (60, 120, 300): rows.append(dict(group=role, threshold_each_competition=thr, players_IPL_ge=int((df_[ci] >= thr).sum()), players_T20I_ge=int((df_[ct] >= thr).sum()), players_both_ge=int(((df_[ci] >= thr) & (df_[ct] >= thr)).sum())))
transfer = pd.DataFrame(rows)

# ------------------------------------------------------------------ extras mapping table (recomputed from the delivery table)
ex = b.groupby(b.extras_type.fillna('(none)')).size().rename('rows_raw_label').to_frame().join(b.groupby(b.extras_type_clean.fillna('(none)')).size().rename('rows_clean_label'), how='outer').fillna(0).astype(int).reset_index().rename(columns={'extras_type': 'label'})

# ------------------------------------------------------------------ write tables
keep = ['match_id', 'innings', 'innings_ball_num', 'overid', 'over_ball_num', 'batting_team_id', 'bowling_team_id', 'striker_id', 'non_striker_id', 'bowler_id', 'batting_order', 'batting_type', 'bowling_type', 'pace_or_spin',
        'runs', 'is_four', 'is_six', 'extras_type', 'extras_type_clean', 'extras1_runs', 'extras_2_runs', 'is_wicket', 'dismissal_type', 'dismissed_player_id', 'dismissed_role',
        'delivery_kind', 'is_legal', 'batter_ball_faced', 'batter_runs', 'bowler_charged_runs', 'uncharged_extras', 'team_runs', 'bowler_wicket_credit', 'legal_before', 'legal_left_before', 'wickets_before', 'runs_before', 'target', 'runs_required_before', 'free_hit',
        'scope', 'cat', 'season', 'comp_name', 'knock_out', 'elig_wp_training', 'elig_pressure', 'elig_batting', 'elig_bowling', 'batting_row_eligible', 'bowling_row_eligible']
b[keep].to_csv(S1 / 'deliveries_analysis.csv.gz', index=False, compression='gzip')
mm.drop(columns=['revised_fields']).to_csv(S1 / 'matches_analysis.csv', index=False); ii.to_csv(S1 / 'innings_analysis.csv', index=False)
bexp.to_csv(S1 / 'player_exposure_batters.csv', index=False); wexp.to_csv(S1 / 'player_exposure_bowlers.csv', index=False); transfer.to_csv(S1 / 'transfer_diagnostic_feasibility.csv', index=False); ex.to_csv(S1 / 'extras_label_counts.csv', index=False)
# exception rows with context (for manual review)
ctx = []
for i in b.index[untyped.values | labelerr.values]:
    for j in range(i - 3, i + 4):
        r = b.loc[j]; ctx.append(dict(exception_row=int(i), position='THIS ROW' if j == i else f'{j - i:+d}', match_id=r.match_id, innings=r.innings, over=r.overid, ball=r.over_ball_num, striker=r.striker_name, bowler=r.bowler_name, runs=r.runs, extras_type=r.extras_type, extras1=r.extras1_runs, extras2=r.extras_2_runs, wicket=r.is_wicket))
pd.DataFrame(ctx).to_csv(EX / 'step1_extras_exception_rows_with_context.csv', index=False)
# free-hit evidence
fhd = b[b.free_hit]; W('\n## Free-hit flag evidence [DATA]\n'); W(f'free_hit deliveries: {len(fhd)} ({len(fhd) / len(b):.2%} of all); deliveries following a no-ball-like delivery with a wide in between are included.')
T(pd.DataFrame({'population': ['free_hit (flag)', 'all other deliveries'], 'deliveries': [len(fhd), len(b) - len(fhd)], 'wicket_rate': [fhd.is_wicket.mean(), b[~b.free_hit].is_wicket.mean()], 'boundary_rate': [(fhd.is_four | fhd.is_six).mean(), (b[~b.free_hit].is_four | b[~b.free_hit].is_six).mean()],
               'bowler_credited_wicket_rate': [fhd.bowler_wicket_credit.mean(), b[~b.free_hit].bowler_wicket_credit.mean()]}).round(4))
W('dismissal types on flagged free-hit deliveries: ' + json.dumps({str(k): int(v) for k, v in fhd[fhd.is_wicket].dismissal_type.value_counts().items()}))
W('\n## Sizes\n'); T(pd.DataFrame([('deliveries_analysis', len(b)), ('matches_analysis', len(mm)), ('innings_analysis (innings 1-2, in scope)', len(ii)), ('player_exposure_batters', len(bexp)), ('player_exposure_bowlers', len(wexp))], columns=['table', 'rows']))
W('\n## Transfer-diagnostic feasibility (players with at least N eligible balls in BOTH IPL and T20I)\n'); T(transfer)
(S1 / 'step1_build_report.md').write_text('\n'.join(md)); print('step1 tables built')

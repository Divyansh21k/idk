"""Stage 3b: task-specific eligibility flags, exact exclusion intersections, extras mapping, role-specific knockout reliability.
Computes FLAGS AND COUNTS ONLY: no data is deleted and no performance model is fitted.
Needs outputs/stage2/s2_innings_summary.csv (run stage2 first).
Usage: python src/stage3b_eligibility.py --raw-dir data/raw --out-dir outputs"""
import argparse, json, re, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from common import load_raw, default_dirs, mkdirs, add_scope
ap = argparse.ArgumentParser(); ap.add_argument('--raw-dir'); ap.add_argument('--out-dir'); a = ap.parse_args()
raw, out = default_dirs(a.raw_dir, a.out_dir); d, _ = load_raw(raw); P = mkdirs(out, 'stage3b')['stage3b']
b, m, c = d['ball_by_ball'], d['matches'], add_scope(d['competitions'])
mm = m.merge(c, on='comp_id'); mm['has_bbb'] = mm.match_id.isin(b.match_id)
inn = pd.read_csv(out / 'stage2' / 's2_innings_summary.csv')
md = []; W = md.append
def H(s): W(f'\n## {s}\n')
def T(df, n=80): W('```\n' + df.head(n).to_string(index=False) + (f'\n... ({len(df)} rows)' if len(df) > n else '') + '\n```')
W('# Stage 3b eligibility and extras audit (generated; flags and counts only)')

# ------------------------------------------------------------ A. extras mapping
H('A. Extras-treatment mapping')
g = b.groupby(b.extras_type.fillna('(none)')).agg(rows=('runs', 'size'), bat_runs=('runs', 'sum'), extras1_sum=('extras1_runs', 'sum'), extras2_sum=('extras_2_runs', 'sum'),
        rows_bat_runs_gt0=('runs', lambda s: int((s > 0).sum())), extras1_values=('extras1_runs', lambda s: json.dumps({int(k): int(v) for k, v in s.value_counts().sort_index().items()})),
        extras2_values=('extras_2_runs', lambda s: json.dumps({int(k): int(v) for k, v in s.value_counts().sort_index().items()}))).reset_index().rename(columns={'extras_type': 'extras_type'})
rule = {  # type: (legal, batter runs, batter ball faced, bowler runs charged, bowler delivery counted, basis)
 '(none)':   ('yes', 'runs', 'yes', 'runs', 'yes', 'DATA: ordinary delivery (1 row has extras1=1 and extras2=1 but no type: exception)'),
 'wide':     ('no', '0 (runs=0 in all 7,714 rows)', 'NO', 'extras1 (wide + any runs run or boundary)', 'yes (not legal)', 'DATA: runs=0, extras2=0; KNOW: wides are not balls faced and are charged to the bowler'),
 'Overstep': ('no', 'runs (0-6)', 'yes', 'runs + extras1 (1 penalty run); extras2 NOT charged', 'yes (not legal)', 'DATA: extras1=1 always; KNOW: no-balls count as balls faced; ASSUME extras2 = byes/leg-byes off the no-ball'),
 'other':    ('no', 'runs (0-6)', 'ASSUME yes (sensitivity: no)', 'runs + extras1 (1); extras2 NOT charged', 'yes (not legal)', 'DATA: identical value pattern to Overstep and consumes no legal ball; label undocumented [OPEN]'),
 'byes':     ('yes', '0', 'yes', '0 (extras1 = byes, not charged)', 'yes', 'DATA: runs=0 in all rows; KNOW: byes are not charged to the bowler'),
 'legbyes':  ('yes', '0 (1 row has bat runs=1: exception)', 'yes', '0 (extras1 = leg-byes, not charged)', 'yes', 'DATA: runs=0 except 1 row; KNOW: leg-byes are not charged'),
 'Penalty':  ('yes (row occupies ball 4 of a complete 6-row over)', '0', 'yes', '0 (5 penalty runs not charged to the bowler)', 'yes', 'DATA: 1 row, runs=0, extras1=5, over has exactly 6 rows; KNOW: penalty runs go to the batting side only'),
}
mp = g.merge(pd.DataFrame([(k, *v) for k, v in rule.items()], columns=['extras_type','legal_ball','batter_runs_credited','batter_ball_faced','bowler_runs_charged','bowler_delivery_counted','basis']), on='extras_type')
mp.to_csv(P / 's3b_extras_mapping.csv', index=False); T(mp[['extras_type','rows','legal_ball','batter_runs_credited','batter_ball_faced','bowler_runs_charged','bowler_delivery_counted']]); W('\nEvidence columns:'); T(mp[['extras_type','rows','bat_runs','extras1_sum','extras2_sum','rows_bat_runs_gt0','extras1_values','extras2_values','basis']])
W('[OPEN] The files do not state who is charged for extras; the charging column follows standard convention [KNOW] and is an assumption. Team totals are unaffected (total = runs + extras1 + extras2, reconciled in Stage 2).')
unt = b[b.extras_type.isna() & ((b.extras1_runs > 0) | (b.extras_2_runs > 0))]; lb = b[(b.extras_type == 'legbyes') & (b.runs > 0)]
pd.concat([unt.assign(issue='extras present but extras_type null'), lb.assign(issue='legbyes with bat runs')])[['issue','match_id','innings','overid','over_ball_num','striker_name','bowler_name','runs','extras_type','extras1_runs','extras_2_runs']].to_csv(out / 'exceptions' / 's3b_extras_exception_rows.csv', index=False)
W('[DATA] extras exception rows (2): '); T(pd.concat([unt.assign(issue='extras present but extras_type null'), lb.assign(issue='legbyes with bat runs')])[['issue','match_id','innings','overid','over_ball_num','runs','extras_type','extras1_runs','extras_2_runs']])

# ------------------------------------------------------------ B. match flags
H('B. Match-level flags and exact intersections')
def result_class(r):
    t = str(r).lower()
    if 'abandon' in t: return 'abandoned'
    if 'no result' in t: return 'no_result'
    if re.search(r'super\s*over|one over|eliminator', t): return 'superover_decided'
    if re.search(r'\btied?\b', t): return 'tie_no_superover'
    if re.search(r'\bwon\b', t) and re.search(r'\d+\s*(runs?|wickets?|wkts?)', t): return 'won_margin'
    return 'other'
mm['result_class'] = mm.result.map(result_class)
mm['cat'] = np.select([(mm.scope == 'IPL') & (mm.knock_out == 0), (mm.scope == 'IPL') & (mm.knock_out == 1), (mm.scope == 'T20I') & (mm.knock_out == 0), (mm.scope == 'T20I') & (mm.knock_out == 1)], ['IPL league','IPL knockout','T20I non-knockout','T20I final'], 'A-team (out of scope)')
mm['revised_fields'] = mm.revised_target.notna() | mm.first_inn_revised_overs.notna() | mm.second_inn_revised_overs.notna()
mm['dls_text'] = mm.result.str.contains(r'D/?L|DLS', case=False, regex=True)
mm['revised_any'] = mm.revised_fields | mm.dls_text; mm['dq'] = mm.match_id.isin([14130, 20190]); mm['minor_flag'] = mm.match_id.isin([14164, 41509])
mm['has_innings34'] = mm.match_id.isin(inn[inn.innings >= 3].match_id)
mm['noresult_partial'] = mm.result_class.isin(['no_result', 'abandoned']) & mm.has_bbb
mm['tie_or_superover'] = mm.result_class.isin(['tie_no_superover', 'superover_decided'])
W('[DATA] result classes (all 883): ' + json.dumps(mm.result_class.value_counts().to_dict()))
wf = [('All matches', len(mm)), ('minus A-team tournaments (out of scope)', -int((mm.scope == 'OTHER').sum())), ('= IPL + T20I', int(mm.scope.isin(['IPL','T20I']).sum())),
      ('minus matches without ball-by-ball (all abandoned)', -int((mm.scope.isin(['IPL','T20I']) & ~mm.has_bbb).sum())), ('= IPL + T20I with ball-by-ball', int((mm.scope.isin(['IPL','T20I']) & mm.has_bbb).sum()))]
W('[DATA] waterfall:'); T(pd.DataFrame(wf, columns=['step', 'matches']))
S = mm[mm.scope.isin(['IPL','T20I']) & mm.has_bbb].copy()
_i1 = inn[inn.innings == 1][['match_id', 'legal', 'wkts']].rename(columns={'legal': 'i1_legal', 'wkts': 'i1_wkts'})
S = S.merge(_i1, on='match_id', how='left')
S['undeclared_reduced'] = (S.i1_legal.notna() & (S.i1_legal < 120) & (S.i1_wkts < 10) & S.result_class.isin(['won_margin', 'superover_decided', 'tie_no_superover']) & ~S.minor_flag & ~S.revised_any & ~S.dq)
S['flagset'] = np.where(S.revised_any, 'revised ', '') + np.where(S.undeclared_reduced, 'undeclared-reduced-overs ', '') + np.where(S.dq, 'dq ', '') + np.where(S.noresult_partial, 'noresult/partial ', '') + np.where(S.tie_or_superover, 'tie/superover ', '')
S['flagset'] = S['flagset'].replace('', '(none)').str.strip()
W('[DATA] exact (mutually exclusive) flag combinations among the 837 in-scope matches with ball-by-ball:'); T(S.groupby('flagset').size().rename('matches').reset_index().sort_values('matches', ascending=False))
W('[DATA] flag totals among the 837: ' + json.dumps({k: int(S[k].sum()) for k in ['revised_any', 'undeclared_reduced', 'dq', 'noresult_partial', 'tie_or_superover', 'has_innings34', 'minor_flag']}) + f'; revised via fields {int(S.revised_fields.sum())}, via result text only {int((S.dls_text & ~S.revised_fields).sum())}')
W('[DATA] undeclared reduced-overs matches (innings 1 shorter than 120 legal balls without all-out, normal result, no revised field or D/L text): ' + json.dumps(S[S.undeclared_reduced].match_id.tolist()))
prelim = S[~S.revised_any & ~S.dq]
W(f'[DATA] earlier "preliminary base" = 837 - (revised or dq) = {len(prelim)} matches; of those, {int(prelim.noresult_partial.sum())} are no-result/partial matches (C3) and {int(prelim.tie_or_superover.sum())} are ties/super-over decided. Under the earlier C3 these {int(prelim.noresult_partial.sum())} would also have been removed (-> {len(prelim) - int(prelim.noresult_partial.sum())}); under the revised rules they are not removed wholesale (see section C).')
S.to_csv(P / 's3b_match_flags.csv', index=False)

# ------------------------------------------------------------ C. innings-level task eligibility
H('C. Task-specific eligibility (innings level)')
ii = inn[inn.innings.isin([1, 2])].merge(S[['match_id','cat','scope','revised_any','dq','minor_flag','result_class','first_inn_revised_overs','noresult_partial','tie_or_superover','undeclared_reduced']], on='match_id', how='inner')
ii['complete'] = (ii.legal >= 120) | (ii.wkts >= 10)
ii['inn1_ok_in_revised'] = (ii.innings == 1) & ii.first_inn_revised_overs.isna() & ii.complete
ii['elig_pressure'] = ~ii.dq & ~ii.undeclared_reduced & (~ii.revised_any | ii.inn1_ok_in_revised)
ii['elig_batting'] = ii.elig_pressure; ii['elig_bowling'] = ii.elig_pressure
ii['flag_incomplete_innings1'] = ii.elig_pressure & (ii.innings == 1) & ~ii.complete
both = ii.groupby('match_id').complete.transform(lambda s: bool(s.all())) & (ii.groupby('match_id').innings.transform('nunique') == 2)
okmatch = S.set_index('match_id')
wp = (ii.result_class == 'won_margin') & ~ii.revised_any & ~ii.dq & ~ii.undeclared_reduced & (ii.groupby('match_id').innings.transform('nunique') == 2) & ii.groupby('match_id').apply(lambda g: pd.Series(bool(g[g.innings == 1].complete.all()), index=g.index), include_groups=False).reset_index(level=0, drop=True)
ii['elig_wp_training'] = wp.reindex(ii.index).fillna(False)
ii.to_csv(P / 's3b_innings_eligibility.csv', index=False)
rule_tbl = pd.DataFrame([
 ('WP training', 'Match decided by a margin (not tie/super over/no result), not revised/D-L, not data-quality excluded, both innings present, innings 1 complete', 'match-level label needs an outcome'),
 ('Pressure calculation', 'IPL/T20I, ball-by-ball present, innings 1-2, not data-quality excluded, not an undeclared reduced-overs match; revised matches: innings 1 only if first_inn_revised_overs is null and the innings is complete; no-result/abandoned/tie/super-over matches ARE eligible (win probability needs only the state)', 'WP of a state does not need the match result; revised innings 2 has a different target/overs'),
 ('Batting performance', 'Same innings as pressure calculation (separate flag; may diverge on delivery-level exceptions)', 'needs pressure index and stage-1 expectation'),
 ('Bowling performance', 'Same innings as pressure calculation plus the extras mapping (separate flag)', 'needs pressure index, stage-1 expectation and charging rules')], columns=['task', 'innings/match rule', 'reason'])
W('[DATA/PROPOSED] rules:'); T(rule_tbl); rule_tbl.to_csv(P / 's3b_task_rules.csv', index=False)
def cnt(df, label):
    x = df.groupby('cat').agg(matches=('match_id', 'nunique'), innings=('match_id', 'size')).reindex(['IPL league','IPL knockout','T20I non-knockout','T20I final']).fillna(0).astype(int)
    x.loc['TOTAL'] = [df.match_id.nunique(), len(df)]; x.insert(0, 'task', label); return x.reset_index()
tabs = [cnt(ii[ii.elig_wp_training], 'WP training'), cnt(ii[ii.elig_pressure], 'Pressure calculation'), cnt(ii[ii.elig_batting], 'Batting performance'), cnt(ii[ii.elig_bowling], 'Bowling performance'), cnt(ii, 'All innings 1-2 in the 837')]
et = pd.concat(tabs); et.to_csv(P / 's3b_task_sample_sizes_matches_innings.csv', index=False); W('[DATA] task-specific matches and innings by category:'); T(et, 40)
# delivery-level
bd = b[b.innings.isin([1, 2])].merge(ii[['match_id','innings','cat','elig_pressure','elig_wp_training']], on=['match_id','innings'], how='inner')
bd['legal'] = ~bd.extras_type.isin(['wide','Overstep','other']); bd['faced'] = bd.extras_type != 'wide'
rows = []
for cat in ['IPL league','IPL knockout','T20I non-knockout','T20I final']:
    x = bd[bd.cat == cat]; e = x[x.elig_pressure]; w_ = x[x.elig_wp_training]
    rows.append(dict(category=cat, wp_train_deliveries=len(w_), pressure_deliveries=len(e), pressure_legal=int(e.legal.sum()), batting_balls_faced=int(e.faced.sum()), batter_innings_rows=e[e.faced].groupby(['match_id','innings','striker_id']).ngroups, distinct_batters=e[e.faced].striker_id.nunique(),
                     bowling_deliveries=len(e), bowler_innings_rows=e.groupby(['match_id','innings','bowler_id']).ngroups, distinct_bowlers=e.bowler_id.nunique()))
dl = pd.DataFrame(rows); dl.loc[len(dl)] = ['TOTAL'] + [int(dl[c_].sum()) if c_ not in ('distinct_batters','distinct_bowlers') else int(bd[bd.elig_pressure].striker_id.nunique() if c_ == 'distinct_batters' else bd[bd.elig_pressure].bowler_id.nunique()) for c_ in dl.columns[1:]]
dl.to_csv(P / 's3b_task_sample_sizes_deliveries.csv', index=False); W('[DATA] task-specific delivery and player exposure by category:'); T(dl)
W('[DATA] reconciliation: 837 in-scope matches with ball-by-ball -> innings-level: ' + f"pressure-eligible matches {ii[ii.elig_pressure].match_id.nunique()}, of which revised matches retained for innings 1 only: {ii[ii.elig_pressure & ii.revised_any].match_id.nunique()} (innings {int((ii.elig_pressure & ii.revised_any).sum())}); matches with NO eligible innings: {837 - ii[ii.elig_pressure].match_id.nunique()}; no-result/partial matches retained: {ii[ii.elig_pressure & ii.noresult_partial].match_id.nunique()}; tie/super-over matches retained: {ii[ii.elig_pressure & ii.tie_or_superover].match_id.nunique()}; eligible innings 1 that are incomplete (flagged): {int(ii.flag_incomplete_innings1.sum())}")
W('[DATA] IPL knockouts: pressure-eligible innings ' + str(int(ii[ii.elig_pressure & (ii.cat == 'IPL knockout')].shape[0])) + ' of ' + str(int(ii[ii.cat == 'IPL knockout'].shape[0])) + ' (the DLS 2023 Final contributes innings 1 only if its first innings was uncurtailed).')
W('Revised matches by innings retained:'); T(ii[ii.revised_any].groupby(['innings','elig_pressure']).size().rename('n_innings').reset_index())

# ------------------------------------------------------------ D. role-specific knockout reliability
H('D. Role-specific knockout reliability (IPL, unadjusted; replaces the single pooled figure)')
ip = bd[bd.elig_pressure & bd.cat.isin(['IPL league', 'IPL knockout'])].copy(); ip['ko'] = ip.cat == 'IPL knockout'
ip['charge'] = ip.runs + np.where(ip.extras_type.isin(['wide','Overstep','other']), ip.extras1_runs, 0)
def role_rel(df, pid, val, role_col, minn=120):
    rows = []
    for role, g in df.groupby(role_col):
        lg = g[~g.ko]; pl = lg.groupby(pid)[val].agg(['mean', 'count']); pl = pl[pl['count'] >= minn]
        s2 = lg[val].var(ddof=1); tau2 = max(pl['mean'].var(ddof=1) - (s2 / pl['count']).mean(), 0) if len(pl) > 2 else np.nan
        ko = g[g.ko].groupby(pid)[val].count(); n_med = ko.median() if len(ko) else np.nan
        rows.append(dict(role=role, players_league_ge120=len(pl), players_with_KO_balls=len(ko), players_KO_ge30=int((ko >= 30).sum()), median_KO_balls=n_med, sigma_per_ball=np.sqrt(s2), tau_between_player=np.sqrt(tau2) if tau2 == tau2 else np.nan,
                         reliability_at_median_KO=(tau2 / (tau2 + s2 / n_med)) if tau2 == tau2 and n_med == n_med else np.nan, reliability_at_median_league_n=(tau2 / (tau2 + s2 / pl['count'].median())) if tau2 == tau2 else np.nan,
                         KO_balls_needed_for_rel_0p5=(s2 / tau2) if tau2 and tau2 == tau2 else np.nan))
    return pd.DataFrame(rows)
bf = ip[ip.extras_type != 'wide'].copy(); bo = bf.groupby('striker_id').batting_order.agg(lambda s: s.mode().iloc[0]); bf['role'] = bf.striker_id.map(bo).map(lambda o: 'opener (1-2)' if o <= 2 else 'top order (3-4)' if o <= 4 else 'middle (5-6)' if o <= 6 else 'lower (7+)')
rb = role_rel(bf, 'striker_id', 'runs', 'role'); rb.insert(0, 'group', 'batters (runs per ball faced)')
rb_all = role_rel(bf.assign(role='ALL batters'), 'striker_id', 'runs', 'role'); rb_all.insert(0, 'group', 'batters (runs per ball faced)')
bw = ip.copy(); bw['role'] = bw.bowler_id.map(bw.groupby('bowler_id').pace_or_spin.first())
rw = role_rel(bw, 'bowler_id', 'charge', 'role'); rw.insert(0, 'group', 'bowlers (charged runs per delivery bowled)')
rw_all = role_rel(bw.assign(role='ALL bowlers'), 'bowler_id', 'charge', 'role'); rw_all.insert(0, 'group', 'bowlers (charged runs per delivery bowled)')
rr_ = pd.concat([rb_all, rb, rw_all, rw]); rr_.to_csv(P / 's3b_role_specific_knockout_reliability.csv', index=False); T(rr_.round(3), 20)
W('[DATA/METHOD] same method-of-moments estimator as Stage 3 (tau = between-player SD of true per-ball means from IPL non-knockout data; reliability = tau^2/(tau^2 + sigma^2/n)); values are runs only (no wicket cost), unadjusted for state, so they are upper bounds. Role = modal batting-order band (batters) or pace/spin (bowlers). Units follow the proposed definitions (balls faced exclude wides; bowlers charged runs + wide/no-ball extras, not byes/leg-byes/penalty).')

# ------------------------------------------------------------ E. reasons for non-retained revised innings, population knockout deviation, weight proxies (new unit/eligibility)
H('E. Revised-match innings 1 retention, population knockout deviation and reference-weight proxies (current rules)')
r1 = ii[ii.revised_any & (ii.innings == 1)].copy()
r1['reason'] = np.where(r1.inn1_ok_in_revised, 'retained (first_inn_revised_overs null, innings complete)', np.where(r1.first_inn_revised_overs.notna(), 'excluded: first innings overs revised (timing of revision unknown)', 'excluded: innings 1 incomplete with no revised field'))
W('[DATA] innings 1 of the 38 revised/D-L matches:'); T(r1.groupby('reason').size().rename('matches').reset_index())
rows_ = []
for role, pid, col, dfx in [('batters (runs per ball faced)', 'striker_id', 'runs', bf), ('bowlers (charged runs per delivery bowled)', 'bowler_id', 'charge', ip)]:
    g_ = dfx.groupby([pid, 'ko'])[col].agg(['mean', 'count']).unstack('ko'); g_.columns = ['lg_mean', 'ko_mean', 'lg_n', 'ko_n']
    both_ = g_[(g_.lg_n >= 120) & (g_.ko_n >= 12)].dropna().copy(); s2_ = dfx[col].var(ddof=1)
    both_['d'] = both_.ko_mean - both_.lg_mean; both_['sv'] = s2_ * (1 / both_.ko_n + 1 / both_.lg_n)
    est = lambda df: (df.d.mean(), max(df.d.var(ddof=1) - df.sv.mean(), 0))
    kh, p2 = est(both_); bs_ = [est(both_.sample(len(both_), replace=True, random_state=i)) for i in range(2000)]
    kb = np.array([x[0] for x in bs_]); pb = np.sqrt([x[1] for x in bs_]); nmed = both_.ko_n.median()
    rows_.append(dict(group=role, players=len(both_), kappa_hat=kh, kappa_ci_low=np.percentile(kb, 2.5), kappa_ci_high=np.percentile(kb, 97.5), psi_hat=np.sqrt(p2), psi_ci_low=np.percentile(pb, 2.5), psi_ci_high=np.percentile(pb, 97.5), median_KO_balls=nmed,
                      weight_on_own_KO_deviation_at_median=p2 / (p2 + s2_ / nmed), share_boot_psi_zero=float((pb == 0).mean())))
pk = pd.DataFrame(rows_); pk.to_csv(P / 's3b_population_knockout_deviation.csv', index=False); T(pk.round(4))
W('[DATA/METHOD] unadjusted for match state; IPL knockouts vs IPL league only (T20I finals excluded); players with >=120 league and >=12 knockout balls; kappa_hat = mean of (knockout mean - league mean); psi^2 = Var(difference) minus mean sampling variance, floored at 0; bootstrap over players. A rough guide only: the adjusted joint model replaces it.')
ipl_all = bd[bd.cat.isin(['IPL league', 'IPL knockout'])]
pe = ipl_all[ipl_all.elig_pressure]
prox = {'IPL knockout share of all IPL matches (20/371)': 20 / 371, 'IPL knockout share of pressure-eligible IPL matches': ii[(ii.cat == 'IPL knockout') & ii.elig_pressure].match_id.nunique() / ii[ii.cat.isin(['IPL league', 'IPL knockout']) & ii.elig_pressure].match_id.nunique(),
        'IPL knockout share of pressure-eligible IPL deliveries': float((pe.cat == 'IPL knockout').mean()), 'IPL knockout share of pressure-eligible IPL overs 16-20 deliveries': float((pe[pe.overid >= 16].cat == 'IPL knockout').mean()),
        'IPL knockout share of pressure-eligible IPL innings-2 overs 16-20 deliveries': float((pe[(pe.overid >= 16) & (pe.innings == 2)].cat == 'IPL knockout').mean())}
W('[DATA] reference-weight PROXIES (the primary w_K, a leverage share, cannot be computed until the validated pressure model exists): ' + json.dumps({k: round(v, 4) for k, v in prox.items()}))
pd.DataFrame(list(prox.items()), columns=['proxy', 'ik_share']).to_csv(P / 's3b_weight_proxies.csv', index=False)

(P / 's3b_eligibility_report.md').write_text('\n'.join(md)); print('stage3b done')

"""Stage 2: record-level investigation of anomalies. Read-only on raw data; nothing is cleaned or dropped.
Usage: python src/stage2_investigate.py --raw-dir data/raw --out-dir outputs"""
import argparse, itertools, json, re, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from common import load_raw, default_dirs, mkdirs, add_scope

ap = argparse.ArgumentParser(); ap.add_argument('--raw-dir'); ap.add_argument('--out-dir'); a = ap.parse_args()
raw, out = default_dirs(a.raw_dir, a.out_dir); d, hashes = load_raw(raw)
PD = mkdirs(out, 'stage2', 'exceptions'); S2, E = PD['stage2'], PD['exceptions']
b, m, c, p, t, cm = (d[k] for k in ['ball_by_ball','matches','competitions','playing_eleven','teams','competition_team_player_mapping'])
c2 = add_scope(c); mm = m.merge(c2, on='comp_id', how='left'); scope_of = mm.set_index('match_id').scope
md = []; W = md.append
def H(s): W(f'\n## {s}\n')
def T(df, n=60): W('```\n' + df.head(n).to_string(index=False) + (f'\n... ({len(df)} rows total)' if len(df) > n else '') + '\n```')
pname = cm.drop_duplicates('player_id').set_index('player_id').player_name
W('# Stage 2 investigation (generated). Labels: [DATA] derived from supplied files; [KNOW] general cricket convention (not verifiable from the files); [OPEN] unresolved.')

# ------------------------------------------------------------------ 1. innings table + result parsing
bi = b.copy(); bi['scope'] = bi.match_id.map(scope_of)
inn = bi.groupby(['match_id','innings']).agg(scope=('scope','first'), team=('batting_team_id','first'), rows=('runs','size'), bat=('runs','sum'), e1=('extras1_runs','sum'), e2=('extras_2_runs','sum'),
        wkts=('is_wicket','sum'), maxover=('overid','max')).reset_index()
def parse_result(x):
    # permissive: the organiser text is inconsistent ("Won by 6 Wkts", "Won 36  Runs", "13Runs", "Won By", ...)
    r = re.match(r'^(.*?)\s+won\s+(?:by\s+)?(\d+)\s*(runs?|wickets?|wkts?)\b(.*)$', str(x), flags=re.I)
    if not r: return (None, None, None, None)
    return (r.group(1).strip(), int(r.group(2)), 'run' if r.group(3).lower().startswith('run') else 'wicket', r.group(4).strip())
mm[['res_team','res_n','res_unit','res_tail']] = mm.result.apply(lambda x: pd.Series(parse_result(x)))
H('1. Result-text formats (digits masked)')
fmt = mm.result.str.replace(r'\d+', '#', regex=True).str.replace(r'^.*?( [Ww]on by)', r'<team>\1', regex=True)
W('```\n' + fmt.value_counts().to_string() + '\n```')
W('\n[DATA] results that are not "<team> won by N runs/wickets" (tail text after margin, if any):')
T(mm[mm.res_team.isna()].result.value_counts().rename_axis('result').reset_index(name='n'))
T(mm[mm.res_tail.fillna('') != ''].groupby('res_tail').size().rename('n').reset_index())

# ------------------------------------------------------------------ 2. legal-ball semantics (empirical test)
H('2. Legal-delivery semantics: which extras types consume a legal ball? (empirical over-structure test)')
x = bi[bi.innings.isin([1, 2])].copy()
cats = ['wide','Overstep','other','Penalty','byes','legbyes']
for k in cats: x['c_' + k] = (x.extras_type == k).astype(int)
x['c_RetireOut'] = (x.dismissal_type == 'Retire Out').astype(int); cols = ['c_' + k for k in cats] + ['c_RetireOut']
ov = x.groupby(['match_id','innings','overid']).agg(n=('runs','size'), **{k: (k, 'sum') for k in cols}).reset_index()
ov['complete'] = ov.overid < ov.groupby(['match_id','innings']).overid.transform('max')
M = ov[cols].values; n = ov.n.values; comp = ov.complete.values
res = []
for r in range(len(cols) + 1):
    for idx in itertools.combinations(range(len(cols)), r):
        legal = n - (M[:, list(idx)].sum(1) if idx else 0)
        res.append(dict(illegal_set='{' + ','.join(cols[i][2:] for i in idx) + '}', complete_overs_not_6_legal=int(((legal != 6) & comp).sum()), any_over_gt6_legal=int((legal > 6).sum())))
sem = pd.DataFrame(res).sort_values(['complete_overs_not_6_legal','any_over_gt6_legal']).reset_index(drop=True)
sem.to_csv(S2 / 's2_legal_ball_subset_test.csv', index=False)
W(f'[DATA] {int(comp.sum())} complete overs (an over followed by a later over in the same innings, innings 1-2). A correct illegal-delivery set should leave exactly 6 legal balls in each. Best 8 of {len(sem)} candidate sets:')
T(sem, 8)
base = sem[sem.illegal_set == '{wide,Overstep}'].iloc[0]; oth = sem[sem.illegal_set == '{wide,Overstep,other}'].iloc[0]
W(f'\n[DATA] {{wide,Overstep}}: {base.complete_overs_not_6_legal} bad complete overs; adding `other`: {oth.complete_overs_not_6_legal}.')
best_set = sem.iloc[0].illegal_set.strip('{}').split(',')
W(f'[DATA] Best-fitting illegal set in this file: {best_set}')
xs = x.sort_values(['match_id','innings','innings_ball_num']); xs['seq'] = xs.groupby(['match_id','innings','overid']).cumcount() + 1
W(f'[DATA] deliveries where over_ball_num != position within the over (by innings_ball_num order): {int((xs.seq != xs.over_ball_num).sum())}')
ILL = set(best_set)

H('3. The `other` extras category - actual records, no assumption')
o = bi[bi.extras_type == 'other']; ov_ = bi[bi.extras_type == 'Overstep']; wd = bi[bi.extras_type == 'wide']
for nm, df in [('other', o), ('Overstep', ov_)]:
    W(f'\n[DATA] value pattern of `{nm}` (n={len(df)}): (runs, extras1_runs, extras_2_runs, is_wicket)')
    T(df.groupby(['runs','extras1_runs','extras_2_runs','is_wicket']).size().rename('n').reset_index())
W('[DATA] `other` by scope / season (compare share of all deliveries):')
tmp = bi.assign(season=bi.match_id.map(mm.set_index('match_id').season), is_other=bi.extras_type == 'other', is_over=bi.extras_type == 'Overstep')
T(tmp.groupby(['scope','season']).agg(deliveries=('runs','size'), other=('is_other','sum'), overstep=('is_over','sum')).reset_index())
W('[DATA] matches / bowlers with `other`: ' + f"{o.match_id.nunique()} matches, {o.bowler_id.nunique()} bowlers; top matches by count:")
T(o.groupby('match_id').size().rename('n_other').reset_index().sort_values('n_other', ascending=False).head(8))
ctx = []
bs = bi.sort_values(['match_id','innings','innings_ball_num']).reset_index(drop=True)
for i in bs.index[bs.extras_type == 'other'][:12]:
    for j in (i - 1, i, i + 1):
        r = bs.loc[j]; ctx.append(dict(case=i, pos='prev' if j < i else 'THIS' if j == i else 'next', match_id=r.match_id, inn=r.innings, over=r.overid, ob=r.over_ball_num, ib=r.innings_ball_num, bowler=r.bowler_name, runs=r.runs, ext=r.extras_type, e1=r.extras1_runs, e2=r.extras_2_runs, wkt=r.is_wicket, dism=r.dismissal_type))
W('[DATA] 12 sample `other` deliveries with the previous and next delivery:'); T(pd.DataFrame(ctx), 40)
W('[OPEN] The files give no label definition for `other`. What the data supports: its value pattern matches `Overstep` (1 penalty run in extras1, bat runs allowed), and the over-structure test above shows whether treating it as a non-legal delivery makes overs complete. The *name/meaning* (e.g. which kind of no-ball) cannot be resolved from the supplied data.')
W('\n[DATA] extras_2_runs > 0 by extras_type:'); T(bi[bi.extras_2_runs > 0].groupby('extras_type').extras_2_runs.agg(['size','sum','max']).reset_index())
W('[DATA] `Penalty` record(s):'); T(bi[bi.extras_type == 'Penalty'][['match_id','innings','overid','over_ball_num','innings_ball_num','runs','extras1_runs','extras_2_runs']])

# ------------------------------------------------------------------ 4. innings reconciliation
H('4. Innings reconciliation (totals, extras, legal balls, wickets)')
bi['legal'] = ~bi.extras_type.isin([e for e in ILL if e in cats]) & ~((bi.dismissal_type == 'Retire Out') & ('RetireOut' in ILL))
inn = inn.merge(bi.groupby(['match_id','innings']).legal.sum().rename('legal').reset_index(), on=['match_id','innings'])
inn['T_bat_e1_e2'] = inn.bat + inn.e1 + inn.e2; inn['T_bat_e1'] = inn.bat + inn.e1
inn['overs_by_legal'] = np.ceil(inn.legal / 6)
inn.to_csv(S2 / 's2_innings_summary.csv', index=False)
W(f'[DATA] innings rows: {len(inn)} (innings 1: {(inn.innings==1).sum()}, 2: {(inn.innings==2).sum()}, 3: {(inn.innings==3).sum()}, 4: {(inn.innings==4).sum()}). Legal balls/innings (innings 1-2): max {inn[inn.innings<=2].legal.max()}, median {inn[inn.innings<=2].legal.median()}.')
W(f'[DATA] innings with >120 legal balls: {int((inn.legal>120).sum())}; with wickets >10: {int((inn.wkts>10).sum())}; innings where max(overid) != ceil(legal/6): {int((inn.maxover != inn.overs_by_legal).sum())}')
T(inn[(inn.legal > 120) | (inn.wkts > 10) | (inn.maxover != inn.overs_by_legal)].head(30))
rev_ids = set(mm[mm.revised_target.notna() | mm.first_inn_revised_overs.notna() | mm.second_inn_revised_overs.notna()].match_id)
i1 = inn[inn.innings == 1].set_index('match_id'); i2 = inn[inn.innings == 2].set_index('match_id')
recs = []
for _, r in mm[mm.res_team.notna() & mm.match_id.isin(b.match_id)].iterrows():
    mid = r.match_id
    if mid not in i1.index or mid not in i2.index: recs.append(dict(match_id=mid, status='missing_innings', result=r.result)); continue
    a1, a2 = i1.loc[mid], i2.loc[mid]
    wid = r.home_team_id if r.res_team == r.home_team else r.away_team_id if r.res_team == r.away_team else None
    row = dict(match_id=mid, scope=r.scope, revised=mid in rev_ids, result=r.result, res_unit=r.res_unit, res_n=r.res_n, winner_name_in_result_matches_a_team=wid is not None, win_team_id_agrees=(wid == r.win_team_id) if wid is not None else None,
               T1_a=a1.T_bat_e1_e2, T2_a=a2.T_bat_e1_e2, T1_b=a1.T_bat_e1, T2_b=a2.T_bat_e1, wk1=a1.wkts, wk2=a2.wkts, legal1=a1.legal, legal2=a2.legal, team1=a1.team, team2=a2.team, winner_id=wid)
    if r.res_unit == 'run':
        row['winner_batted_first'] = wid == a1.team
        row['margin_ok_a'] = (a1.T_bat_e1_e2 - a2.T_bat_e1_e2) == r.res_n; row['margin_ok_b'] = (a1.T_bat_e1 - a2.T_bat_e1) == r.res_n
    else:
        row['winner_batted_first'] = wid == a1.team
        row['margin_ok_a'] = (a2.wkts == 10 - r.res_n) and (a2.T_bat_e1_e2 > a1.T_bat_e1_e2); row['margin_ok_b'] = (a2.wkts == 10 - r.res_n) and (a2.T_bat_e1 > a1.T_bat_e1)
    recs.append(row)
rc = pd.DataFrame(recs); rc.to_csv(S2 / 's2_result_reconciliation_all.csv', index=False)
ok = rc[rc.status.isna() if 'status' in rc else rc.margin_ok_a.notna()] if False else rc[rc.get('margin_ok_a').notna()]
W(f'\n[DATA] "won by N runs/wickets" matches with both innings in ball-by-ball: {len(ok)}  (non-revised: {int((~ok.revised).sum())}, revised: {int(ok.revised.sum())})')
for lab, df in [('non-revised', ok[~ok.revised]), ('revised (D/L-type)', ok[ok.revised])]:
    W(f'- {lab}: n={len(df)}; margin reconciles with total=bat+extras1+extras2: {int(df.margin_ok_a.sum())}; with total=bat+extras1 only: {int(df.margin_ok_b.sum())}; winner team named in result is a match team: {int(df.winner_name_in_result_matches_a_team.sum())}; win_team_id agrees with result text: {int((df.win_team_id_agrees==True).sum())}')
W('- by unit (non-revised): ' + json.dumps({u: [int(len(g)), int(g.margin_ok_a.sum())] for u, g in ok[~ok.revised].groupby('res_unit')}) + '  [n, reconciled]')
fail = ok[(~ok.margin_ok_a)]
fail.to_csv(E / 's2_result_reconciliation_failures.csv', index=False)
W(f'\n[DATA] Reconciliation failures (total=bat+e1+e2), all {len(fail)} records (exception file s2_result_reconciliation_failures.csv):')
T(fail[['match_id','scope','revised','result','T1_a','T2_a','wk1','wk2','legal1','legal2','winner_batted_first','win_team_id_agrees']], 60)
oth_res = mm[(mm.res_team.isna()) & mm.match_id.isin(b.match_id)][['match_id','scope','result']]
W('\n[DATA] matches with ball-by-ball whose result text is not a plain margin (tie / no result / abandoned / other), innings present:')
ni = inn.groupby('match_id').innings.apply(lambda s: ','.join(map(str, sorted(s.unique())))).rename('innings_present')
T(oth_res.merge(ni, on='match_id').merge(mm[['match_id','win_team_id']], on='match_id'), 70)

# ------------------------------------------------------------------ 5. truncated / short innings
H('5. Innings that do not look like complete 20-over or all-out innings (innings 1-2)')
short = inn[(inn.innings <= 2) & (inn.legal < 120) & (inn.wkts < 10)].copy()
short['revised_match'] = short.match_id.isin(rev_ids)
short = short.merge(mm[['match_id','result','rtype' if 'rtype' in mm else 'result']].drop_duplicates('match_id')[['match_id','result']].rename(columns={'result':'match_result'}), on='match_id')
chase_done = short[(short.innings == 2) & short.match_id.map(lambda k: k in i1.index and k in i2.index and i2.loc[k].T_bat_e1_e2 > i1.loc[k].T_bat_e1_e2)]
short['explained_by_chase_completed'] = short.index.isin(chase_done.index)
short.to_csv(E / 's2_short_innings.csv', index=False)
W(f'[DATA] {len(short)} innings with <120 legal balls and <10 wickets: explained by successful chase {int(short.explained_by_chase_completed.sum())}; in revised-target matches {int(short.revised_match.sum())}; unexplained remainder:')
T(short[~short.explained_by_chase_completed & ~short.revised_match][['match_id','scope','innings','legal','wkts','T_bat_e1_e2','match_result']], 60)

# ------------------------------------------------------------------ 6. innings 3 & 4
H('6. Innings 3 and 4 matches')
i34 = inn[inn.innings >= 3]
rows = []
for mid, g in inn[inn.match_id.isin(i34.match_id)].groupby('match_id'):
    r = mm[mm.match_id == mid].iloc[0]
    rows.append(dict(match_id=mid, scope=r.scope, comp=r.comp_name, date=r.match_date, home=r.home_team, away=r.away_team, result=r.result, win_team_id=r.win_team_id, rev=mid in rev_ids,
                     **{f'inn{k}': f"{int(g[g.innings==k].T_bat_e1_e2.iloc[0])}/{int(g[g.innings==k].wkts.iloc[0])} ({int(g[g.innings==k].legal.iloc[0])}b, team {int(g[g.innings==k].team.iloc[0])})" if (g.innings == k).any() else '-' for k in (1, 2, 3, 4)}))
s34 = pd.DataFrame(rows); s34.to_csv(E / 's2_innings3_4_matches.csv', index=False); T(s34)
W(f'[DATA] matches with innings 3/4: {len(s34)}; result types in ties: tie-results in file = {int((mm.result.str.contains("tie", case=False)).sum())}; tie-result matches that have innings 3/4: {int(mm[mm.result.str.contains("tie", case=False)].match_id.isin(s34.match_id).sum())}')
W('[DATA] all tie-result matches:'); T(mm[mm.result.str.contains('tie', case=False)][['match_id','scope','match_date','home_team','away_team','result','win_team_id']].assign(has_innings34=lambda df: df.match_id.isin(s34.match_id)))

# ------------------------------------------------------------------ 7. revised matches
H('7. Revised-target matches (any of first_inn_revised_overs / second_inn_revised_overs / revised_target non-null)')
rv = mm[mm.match_id.isin(rev_ids)][['match_id','scope','match_date','home_team','away_team','first_inn_revised_overs','second_inn_revised_overs','revised_target','result']].copy()
rv = rv.merge(i1[['T_bat_e1_e2','legal','wkts']].add_suffix('_1').reset_index(), on='match_id', how='left').merge(i2[['T_bat_e1_e2','legal','wkts']].add_suffix('_2').reset_index(), on='match_id', how='left')
rv['T1_plus1_eq_target'] = rv.T_bat_e1_e2_1 + 1 == rv.revised_target
rv['has_bbb'] = rv.match_id.isin(b.match_id); rv.to_csv(E / 's2_revised_target_matches_detail.csv', index=False)
W(f'[DATA] {len(rv)} matches; revised_target non-null {int(rv.revised_target.notna().sum())}; first-inn overs revised {int(rv.first_inn_revised_overs.notna().sum())}; second-inn {int(rv.second_inn_revised_overs.notna().sum())}; with ball-by-ball {int(rv.has_bbb.sum())}; revised_target == innings-1 total + 1: {int(rv.T1_plus1_eq_target.sum())}')
T(rv[['match_id','scope','first_inn_revised_overs','second_inn_revised_overs','revised_target','T_bat_e1_e2_1','legal_1','T_bat_e1_e2_2','legal_2','wkts_2','result']], 40)
W('[DATA] combinations of (first_inn_revised_overs, second_inn_revised_overs) present: ' + json.dumps({str(k): int(v) for k, v in rv.groupby([rv.first_inn_revised_overs.fillna(-1), rv.second_inn_revised_overs.fillna(-1)]).size().items()}))
W('[OPEN] The file has no DLS par-score or interruption timeline, so ball-level pressure inside these matches cannot be modelled from the supplied data. Treatment decision belongs to Stage 3.')

# ------------------------------------------------------------------ 8. timestamps
H('8. Timestamp discrepancies')
bi['ts'] = pd.to_datetime(bi.delivery_ist_time.str.replace(' UTC', ''), errors='coerce')
mt = bi.groupby('match_id').agg(first_ts=('ts','min'), last_ts=('ts','max')).join(mm.set_index('match_id')[['match_date','scope','comp_name']])
mt['md'] = pd.to_datetime(mt.match_date); mt['first_day_diff'] = (mt.first_ts.dt.normalize() - mt.md).dt.days; mt['last_day_diff'] = (mt.last_ts.dt.normalize() - mt.md).dt.days
mt['span_h'] = (mt.last_ts - mt.first_ts).dt.total_seconds() / 3600
W('[DATA] first-ball date minus match_date (days): ' + json.dumps(mt.first_day_diff.value_counts().sort_index().to_dict()) + '; last-ball date minus match_date: ' + json.dumps(mt.last_day_diff.value_counts().sort_index().to_dict()))
W(f'[DATA] match duration (last-first ts, hours): median {mt.span_h.median():.2f}, p95 {mt.span_h.quantile(.95):.2f}, max {mt.span_h.max():.2f}; matches with span >8h: {int((mt.span_h > 8).sum())}')
bad = mt[(mt.first_day_diff != 0) | (mt.last_day_diff != 0)].reset_index(); bad.drop(columns='md').to_csv(E / 's2_timestamp_date_discrepancies.csv', index=False)
W(f'[DATA] matches where first or last ball date != match_date: {len(bad)} ({bad.scope.value_counts().to_dict()}). Records:'); T(bad[['match_id','scope','match_date','first_ts','last_ts','first_day_diff','last_day_diff','span_h']], 70)
first_i1 = bi[bi.innings == 1].groupby('match_id').ts.min()
hr = first_i1.dt.hour.groupby(first_i1.index.map(scope_of)).value_counts().unstack(0).fillna(0).astype(int)
W('[DATA] hour-of-day (clock value in the timestamp) of each match\'s first innings-1 ball, by scope:'); W('```\n' + hr.to_string() + '\n```')
bi = bi.sort_values(['match_id','innings','innings_ball_num']); dts = bi.groupby(['match_id','innings']).ts.diff().dt.total_seconds()
W(f'[DATA] within-innings timestamp decreases vs innings_ball_num order: {int((dts < 0).sum())}; zero gaps: {int((dts == 0).sum())}; gaps >30 min: {int((dts > 1800).sum())}')
W('[OPEN] Column is named `delivery_ist_time` but values carry a "UTC" suffix; the files do not say which is correct. Use `innings_ball_num` for ordering, never the timestamp. If the clock hours above look like UTC-converted IST that is an inference, not a documented fact.')

# ------------------------------------------------------------------ 9. dismissals
H('9. Dismissal and bowler-credit logic')
wk = bi[bi.is_wicket].copy()
W('[DATA] dismissal_type_id <-> dismissal_type:'); T(bi[bi.dismissal_type.notna()].groupby(['dismissal_type_id','dismissal_type']).size().rename('n').reset_index())
wk['who'] = np.where(wk.dismissed_player_id.isna(), 'null', np.where(wk.dismissed_player_id == wk.striker_id, 'striker', np.where(wk.dismissed_player_id == wk.non_striker_id, 'non_striker', 'other')))
W('[DATA] who was dismissed, by type:'); T(pd.crosstab(wk.dismissal_type, wk.who).reset_index())
W('[DATA] dismissal type x delivery type (extras_type):'); T(pd.crosstab(wk.dismissal_type, wk.extras_type.fillna('(legal/none)')).reset_index())
sus = wk[wk.dismissal_type.isin(['Bowled','Caught','LBW']) & wk.extras_type.isin(['wide','Overstep','other'])]
sus[['match_id','innings','overid','over_ball_num','bowler_name','striker_name','extras_type','runs','dismissal_type']].to_csv(E / 's2_dismissal_on_nonlegal_ball.csv', index=False)
W(f'[DATA/KNOW] Bowled/Caught/LBW recorded on a wide/Overstep/other delivery: {len(sus)} (not possible under standard laws [KNOW]; would indicate mis-labelled extras or dismissal): '); T(sus[['match_id','overid','over_ball_num','bowler_name','extras_type','dismissal_type']], 20)
CRED = ['Bowled','Caught','LBW','Stump','Hit Wicket']
W('[KNOW] Proposed rule (standard convention; not stated in the files): bowler-credited = Bowled, Caught, LBW, Stump, Hit Wicket; not credited = RunOut, Retire Out, Obstructing the field (both spellings in the file).')
wk['credited'] = wk.dismissal_type.isin(CRED)
W(f'[DATA] naive is_wicket={len(wk)}; bowler-credited by rule={int(wk.credited.sum())}; over-credit if is_wicket used: {len(wk) - int(wk.credited.sum())}; bowlers with a different count: {int((wk.groupby("bowler_id").size() != wk[wk.credited].groupby("bowler_id").size().reindex(wk.bowler_id.unique()).fillna(0).reindex(wk.groupby("bowler_id").size().index)).sum())} of {wk.bowler_id.nunique()} with any wicket-flag delivery')
W('[DATA] all Retire Out / Obstructing records:'); T(wk[wk.dismissal_type.isin(['Retire Out','Obstracting the field','Obstructing the field'])][['match_id','innings','overid','over_ball_num','innings_ball_num','bowler_name','striker_name','non_striker_name','dismissed_player_id','who','runs','extras_type','dismissal_type']])
an = bi[(bi.is_wicket & (bi.dismissed_player_id.isna() | bi.dismissal_type.isna())) | (~bi.is_wicket & (bi.dismissal_type.notna() | bi.dismissed_player_id.notna()))].copy()
an['dismissed_name'] = an.dismissed_player_id.map(pname); an['scope'] = an.match_id.map(scope_of)
an[['scope','match_id','innings','overid','over_ball_num','innings_ball_num','bowler_name','striker_name','non_striker_name','is_wicket','dismissal_type','dismissed_player_id','dismissed_name','runs','extras_type']].to_csv(E / 's2_wicket_flag_anomaly_records.csv', index=False)
W('[DATA] the 13 wicket-flag/dismissed-id anomaly records (actual rows):'); T(an[['scope','match_id','innings','overid','over_ball_num','bowler_name','striker_name','non_striker_name','is_wicket','dismissal_type','dismissed_player_id','dismissed_name','runs','extras_type']])
W('[DATA] wickets per innings: ' + json.dumps(inn[inn.innings <= 2].wkts.value_counts().sort_index().to_dict()))
sr = bi[bi.striker_id == bi.non_striker_id]; W('[DATA] striker==non_striker record(s):'); T(sr[['match_id','innings','overid','over_ball_num','striker_id','striker_name','non_striker_name','bowler_name','runs','is_wicket']])

# ------------------------------------------------------------------ 10. playing XI
H('10. Playing-XI issues')
pl = p[p.is_played == True]
tm = pl.groupby(['match_id','team_id']).agg(n_played=('player_id','size'), n_impact=('is_impact','sum'), n_impact_off=('is_impact_off','sum'), n_dup_keys=('player_id', lambda s: int(s.duplicated().sum()))).reset_index()
tm['scope'] = tm.match_id.map(scope_of)
W('[DATA] played rows per team-match vs impact flags, by scope:'); T(tm.groupby(['scope','n_played','n_impact']).size().rename('team_matches').reset_index())
unusual = tm[~(((tm.n_played == 11) & (tm.n_impact == 0)) | ((tm.n_played == 12) & (tm.n_impact == 1)))]
unusual = unusual.merge(mm[['match_id','comp_name','match_date','home_team','away_team']], on='match_id'); unusual.to_csv(E / 's2_xi_unusual_team_matches.csv', index=False)
W(f'[DATA] team-matches that are NOT (11 played, 0 impact) or (12 played, 1 impact): {len(unusual)} - actual records:'); T(unusual, 40)
bo = bi[bi.innings <= 2].groupby(['match_id','striker_id']).batting_order.agg(lambda s: s.mode().iloc[0]).rename('bbb_order').reset_index().rename(columns={'striker_id':'player_id'})
pj = pl.merge(bo, on=['match_id','player_id'], how='inner'); dupm = set(p[p.duplicated(['match_id','team_id','player_id'], keep=False)].match_id)
pj['agree'] = pj.batting_order == pj.bbb_order
W(f'[DATA] XI batting_order vs bbb striker batting_order (mode) for batters present in both: agree {int(pj.agree.sum())} of {len(pj)}; disagreements outside the 3 duplicate-XI matches: {int((~pj.agree & ~pj.match_id.isin(dupm)).sum())}; inside: {int((~pj.agree & pj.match_id.isin(dupm)).sum())}')
dk = p[p.duplicated(['match_id','team_id','player_id'], keep=False)].merge(bo, on=['match_id','player_id'], how='left')
dk['option_matches_bbb'] = dk.batting_order == dk.bbb_order
g = dk.groupby(['match_id','team_id','player_id']).agg(options=('batting_order', lambda s: sorted(s.tolist())), bbb_order=('bbb_order','first'), n_options=('batting_order','size'), n_matching=('option_matches_bbb','sum')).reset_index()
g['player'] = g.player_id.map(pname); g.to_csv(E / 's2_xi_duplicates_vs_bbb.csv', index=False)
W(f'[DATA] duplicate-XI keys: {len(g)}; keys where exactly one duplicate option equals the ball-by-ball batting order: {int((g.n_matching == 1).sum())}; zero options equal: {int((g.n_matching == 0).sum())}; more than one: {int((g.n_matching > 1).sum())}')
T(g.head(40))
W('[DATA] innings present in the three duplicate-XI matches (to test the "extra batting innings" explanation):'); T(inn[inn.match_id.isin(dupm)].groupby('match_id').innings.apply(lambda s: sorted(s.unique())).rename('innings').reset_index())
for fn, lab in [('assert_R19.csv', 'ball-by-ball participants absent from XI for their team/match')]:
    z = pd.read_csv(E / fn); z['player'] = z.player_id.map(pname); z['scope'] = z.match_id.map(scope_of); z['xi_rows_for_team_match'] = [int(((p.match_id == r.match_id) & (p.team_id == r.team_id)).sum()) for r in z.itertuples()]
    W(f'[DATA] {lab} ({len(z)} participant-role rows):'); T(z[['match_id','scope','team_id','player_id','player','role','xi_rows_for_team_match']])
    W('[DATA] these participant-match pairs: ' + str(z[['match_id','player_id']].drop_duplicates().shape[0]) + '; scopes ' + json.dumps(z.scope.value_counts().to_dict()))
z23 = pd.read_csv(E / 'assert_R23.csv'); W(f'[DATA] XI rows absent from the (comp,team) squad but present in mapping under another team/competition: players {z23.player_id.unique().tolist()} ({[pname.get(i) for i in z23.player_id.unique()]}), team {z23.team_id.unique().tolist()}, comp {z23.comp_id.unique().tolist()}, is_played {z23.is_played.unique().tolist()}')
nev = pl[pl.match_id.isin(b.match_id)].merge(pd.concat([bi[['match_id','striker_id']].rename(columns={'striker_id':'player_id'}), bi[['match_id','non_striker_id']].rename(columns={'non_striker_id':'player_id'}), bi[['match_id','bowler_id']].rename(columns={'bowler_id':'player_id'})]).drop_duplicates().assign(seen=1), on=['match_id','player_id'], how='left')
nev = nev[nev.seen.isna()].copy(); nev['scope'] = nev.match_id.map(scope_of); nev['has_batting_order'] = nev.batting_order.notna()
W('[DATA] is_played=True players who never appear as striker/non-striker/bowler in their match ("did not bat or bowl" - not an error):')
T(nev.groupby(['scope','is_impact','has_batting_order']).size().rename('n').reset_index())
W('[DATA] is_played=True rows with null batting_order:'); T(pl[pl.batting_order.isna()].assign(scope=lambda df: df.match_id.map(scope_of), player=lambda df: df.player_id.map(pname))[['match_id','scope','team_id','player_id','player','is_impact','is_impact_off']])
W('[DATA] matches with no XI rows: ' + json.dumps(mm[~mm.match_id.isin(p.match_id)][['match_id','result','scope']].to_dict('records')))

# ------------------------------------------------------------------ 11. supplementary checks
H('11. Supplementary record-level checks')
# 12a DLS text vs revised fields; unit of revised-overs fields
mm['dls_text'] = mm.result.str.contains(r'D/?L|DLS', case=False, regex=True); mm['rev_flag'] = mm.match_id.isin(rev_ids)
W('[DATA] result text mentions D/L or DLS vs revised_* fields populated:'); T(pd.crosstab(mm.dls_text, mm.rev_flag).reset_index())
dl = mm[mm.dls_text & ~mm.rev_flag][['match_id','scope','match_date','home_team','away_team','result']]; dl.to_csv(E / 's2_dls_text_without_revised_fields.csv', index=False)
W(f'[DATA] matches whose result text says D/L-DLS but have NO revised_* field: {len(dl)}'); T(dl)
vals = pd.concat([mm.first_inn_revised_overs.dropna(), mm.second_inn_revised_overs.dropna()])
W(f'[DATA] revised_*_overs values: n={len(vals)}, min {vals.min()}, max {vals.max()}, divisible by 6: {int((vals % 6 == 0).sum())}, > 20: {int((vals > 20).sum())}  -> values behave like BALLS (e.g. 114 = 19 overs), not overs, despite the column name')
rvm = mm[mm.match_id.isin(rev_ids) & mm.first_inn_revised_overs.notna()].merge(i1[['legal']], left_on='match_id', right_index=True)
W(f'[DATA] first_inn_revised_overs == legal balls actually bowled in innings 1: {int((rvm.first_inn_revised_overs == rvm.legal).sum())} of {len(rvm)}')
rvm2 = mm[mm.match_id.isin(rev_ids) & mm.second_inn_revised_overs.notna()].merge(i2[['legal','wkts']], left_on='match_id', right_index=True)
W(f'[DATA] second_inn_revised_overs == legal balls bowled in innings 2: {int((rvm2.second_inn_revised_overs == rvm2.legal).sum())} of {len(rvm2)} (chases that ended early on success/all-out are expected to be lower)')
# 12b timestamp clock by IPL season
ipl_first = bi[(bi.innings == 1) & (bi.scope == 'IPL')].groupby('match_id').ts.min()
ipl_first = ipl_first.to_frame().assign(season=lambda df: df.index.map(mm.set_index('match_id').season), hour=lambda df: df.ts.dt.hour)
W('[DATA] IPL first-ball clock hour by season (a consistent time zone would give the same hours every season):'); T(pd.crosstab(ipl_first.hour, ipl_first.season).reset_index())
W('[OPEN] IPL first-ball hours cluster at 14 and 19 across seasons: both are plausible start-clock values (14 = a 19:30 IST start expressed in UTC; 19 = a 19:30 start expressed in IST). The organiser files do not say which rows use which zone; whether the zone changes by season is shown above. Ordering/phase logic must not rely on timestamps.')
# 12c non-wicket rows carrying a dismissed_player_id
rows = []
bsrt = bi.sort_values(['match_id','innings','innings_ball_num'])
cand = bsrt[(~bsrt.is_wicket & bsrt.dismissed_player_id.notna()) | (bsrt.is_wicket & bsrt.dismissed_player_id.isna())]
for _, r in cand.iterrows():
    later = bsrt[(bsrt.match_id == r.match_id) & (bsrt.innings == r.innings) & (bsrt.innings_ball_num > r.innings_ball_num)]
    cands = [r.dismissed_player_id] if pd.notna(r.dismissed_player_id) else [r.striker_id, r.non_striker_id]
    for pid in cands:
        rows.append(dict(match_id=r.match_id, innings=r.innings, ball=r.innings_ball_num, is_wicket=r.is_wicket, dism_type=r.dismissal_type, player=pname.get(pid), role_on_ball='striker' if pid == r.striker_id else 'non_striker' if pid == r.non_striker_id else 'other',
                         appears_after_in_innings=bool(((later.striker_id == pid) | (later.non_striker_id == pid)).any())))
cc = pd.DataFrame(rows); cc.to_csv(E / 's2_wicket_flag_anomaly_continuation_test.csv', index=False)
W('[DATA] For each of the 13 anomalous rows: does the player named in dismissed_player_id (or, if null, each batter at the crease) still bat later in that innings? (a player who bats on cannot have been dismissed on that ball):'); T(cc)
# 12d residual over-structure exceptions under the best set
ov['legal_best'] = ov.n - ov[[('c_' + e) for e in ILL if ('c_' + e) in cols]].sum(axis=1)
badov = ov[((ov.legal_best != 6) & ov.complete) | (ov.legal_best > 6)]; badov.to_csv(E / 's2_over_structure_exceptions.csv', index=False)
W(f'[DATA] overs still not consistent with 6 legal balls under {sorted(ILL)} ({len(badov)} records):'); T(badov[['match_id','innings','overid','n','legal_best','complete'] + cols])
# 12e deep-dive on non-revised reconciliation failures
nf = fail[~fail.revised]
W('[DATA] non-revised reconciliation failures - innings components:')
rows = []
for mid in nf.match_id:
    for k in (1, 2):
        r_ = inn[(inn.match_id == mid) & (inn.innings == k)].iloc[0]; rows.append(dict(match_id=mid, innings=k, bat=r_.bat, e1=r_.e1, e2=r_.e2, total=r_.T_bat_e1_e2, wkts=r_.wkts, legal=r_.legal, result=mm[mm.match_id == mid].result.iloc[0]))
T(pd.DataFrame(rows))
for mid in [20190]:
    x_ = bi[(bi.match_id == mid) & (bi.innings == 2) & bi.is_wicket][['overid','over_ball_num','bowler_name','striker_name','dismissal_type','dismissed_player_id']]
    W(f'[DATA] all wicket records, match {mid} innings 2 (result says 6 wickets, ball-by-ball has {len(x_)} wicket rows):'); T(x_)
# 12f batting-order disagreements outside duplicate matches
dis = pj[~pj.agree & ~pj.match_id.isin(dupm)].assign(player=lambda df: df.player_id.map(pname))[['match_id','team_id','player_id','player','batting_order','bbb_order','is_impact']]
dis.to_csv(E / 's2_xi_vs_bbb_batting_order_disagreements.csv', index=False)
W('[DATA] XI batting_order vs ball-by-ball batting order disagreements outside the three duplicate-XI matches:'); T(dis)


# ------------------------------------------------------------------ 12. bowler metadata
H('12. Bowler metadata: multiple bowling_type labels, pace_or_spin, bowl_speed')
bt = bi.assign(season=bi.match_id.map(mm.set_index('match_id').season)).groupby(['bowler_id','bowling_type','pace_or_spin'], dropna=False).agg(n=('runs','size'), matches=('match_id','nunique'), first_match=('match_id','min'), last_match=('match_id','max')).reset_index()
multi = bt.groupby('bowler_id').bowling_type.nunique(); multi = multi[multi > 1].index
mb = bt[bt.bowler_id.isin(multi)].copy(); mb['bowler'] = mb.bowler_id.map(pname); mb.to_csv(E / 's2_bowlers_multiple_bowling_type.csv', index=False)
W(f'[DATA] bowlers with >1 bowling_type label: {len(multi)} of {bi.bowler_id.nunique()}; with >1 pace_or_spin value: {int((bt.groupby("bowler_id").pace_or_spin.nunique() > 1).sum())}')
pairs = mb.sort_values('n', ascending=False).groupby('bowler_id').bowling_type.apply(lambda s: ' | '.join(s)).value_counts().rename_axis('label_set').reset_index(name='bowlers')
W('[DATA] which label sets co-occur (most common):'); T(pairs, 15)
W('[DATA] share of each multi-label bowler\'s deliveries carried by the minority label(s):')
mb['share'] = mb.n / mb.groupby('bowler_id').n.transform('sum')
T(mb.sort_values(['bowler_id','share'], ascending=[True, False]).groupby('bowler_id').agg(bowler=('bowler','first'), labels=('bowling_type', lambda s: ' | '.join(s.astype(str))), shares=('share', lambda s: ' | '.join(f'{v:.2f}' for v in s)), matches_by_label=('matches', lambda s: ' | '.join(map(str, s)))).reset_index().head(50), 50)
mbm = bi[bi.bowler_id.isin(multi)].groupby(['bowler_id','match_id']).bowling_type.nunique()
W(f'[DATA] (bowler,match) pairs where the label changes WITHIN a match: {int((mbm > 1).sum())}; label sets by match_date order - bowlers whose label changes over time in one direction vs flips back and forth is in the CSV (s2_bowlers_multiple_bowling_type.csv)')
seq = bi[bi.bowler_id.isin(multi)].sort_values(['bowler_id','match_id','innings_ball_num']).groupby(['bowler_id','match_id']).bowling_type.first().reset_index()
flips = seq.groupby('bowler_id').bowling_type.apply(lambda s: int((s != s.shift()).sum() - 1))
W('[DATA] number of label changes between consecutive matches per multi-label bowler (1 = clean one-time change; >1 = flip-flopping): ' + json.dumps(flips.value_counts().sort_index().to_dict()))
W('[DATA] bowling_type x pace_or_spin:'); T(bi.groupby(['bowling_type','pace_or_spin'], dropna=False).size().rename('n').reset_index())
W('[OPEN] The files carry no definition for bowling_type. Whether multi-label bowlers are real changes of style or labelling noise cannot be established from the supplied data alone; the one-time vs flip-flop evidence above is the only discriminating information available.')

(S2 / 'stage2_investigation_report.md').write_text('\n'.join(md)); print('stage2 done:', len(md), 'blocks')

"""Step 1 validation: checks the analysis tables against (a) the numbers in the approved Stage 3 v0.4 proposal and (b) internal invariants computed independently from the raw files.
Usage: python src/step1_validate.py --raw-dir data/raw --out-dir outputs   (exit code 1 if any check fails)"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from common import load_raw, default_dirs

ap = argparse.ArgumentParser(); ap.add_argument('--raw-dir'); ap.add_argument('--out-dir'); a = ap.parse_args()
raw, out = default_dirs(a.raw_dir, a.out_dir); d, _ = load_raw(raw); S1 = out / 'step1'
dl = pd.read_csv(S1 / 'deliveries_analysis.csv.gz', low_memory=False); mm = pd.read_csv(S1 / 'matches_analysis.csv'); ii = pd.read_csv(S1 / 'innings_analysis.csv')
bx = pd.read_csv(S1 / 'player_exposure_batters.csv'); wx = pd.read_csv(S1 / 'player_exposure_bowlers.csv'); raw_b = d['ball_by_ball']
R = []
def chk(cid, desc, expected, actual, hard=True):
    ok = (expected == actual) if not isinstance(expected, float) else abs(expected - actual) < 1e-9
    R.append(dict(id=cid, description=desc, expected=json.dumps(expected, default=str), actual=json.dumps(actual, default=str), status='PASS' if ok else 'FAIL', hard=hard))
CATS = ['IPL league', 'IPL knockout', 'T20I non-knockout', 'T20I final']
# ---- A. approved document numbers (Stage 3 v0.4, section 3)
chk('A01', 'all matches', 883, len(mm)); chk('A02', 'IPL + T20I', 853, int(mm.scope.isin(['IPL', 'T20I']).sum())); chk('A03', 'IPL + T20I with ball-by-ball', 837, int(mm.in_scope.sum()))
S = mm[mm.in_scope]
chk('A04', 'exclusive flag combinations', {'(none)': 772, 'revised': 28, 'revised noresult/partial': 10, 'noresult/partial': 14, 'tie/superover': 8, 'undeclared-reduced-overs': 3, 'dq': 2}, S.flagset.value_counts().to_dict())
chk('A05', 'flag totals', {'revised': 38, 'revised_by_fields': 34, 'revised_text_only': 4, 'noresult_partial': 24, 'tie_or_superover': 8, 'undeclared_reduced': 3, 'dq': 2, 'innings34_in_scope': 4, 'minor_flag': 2},
    {'revised': int(S.revised_any.sum()), 'revised_by_fields': int(S.revised_fields.sum()) if 'revised_fields' in S else int((S.revised_any & ~(S.dls_text & S.first_inn_revised_overs.isna() & S.second_inn_revised_overs.isna() & S.revised_target.isna())).sum()),
     'revised_text_only': int((S.dls_text & S.first_inn_revised_overs.isna() & S.second_inn_revised_overs.isna() & S.revised_target.isna()).sum()), 'noresult_partial': int(S.noresult_partial.sum()), 'tie_or_superover': int(S.tie_or_superover.sum()),
     'undeclared_reduced': int(S.undeclared_reduced.sum()), 'dq': int(S.dq.sum()), 'innings34_in_scope': int(S.has_innings34.sum()), 'minor_flag': int(S.minor_flag.sum())})
chk('A06', 'earlier preliminary base 837 - 38 - 2', 797, int((S.in_scope & ~S.revised_any & ~S.dq).sum()))
def size(df): return {c: [int(df[df.cat == c].match_id.nunique()), int((df.cat == c).sum())] for c in CATS} | {'TOTAL': [int(df.match_id.nunique()), len(df)]}
chk('A07', 'WP training matches [matches, innings]', {'IPL league': [331, 662], 'IPL knockout': [19, 38], 'T20I non-knockout': [416, 832], 'T20I final': [5, 10], 'TOTAL': [771, 1542]}, size(ii[ii.elig_wp_training]))
for t in ['elig_pressure', 'elig_batting', 'elig_bowling']:
    chk('A08' + t[5], f'{t} [matches, innings]', {'IPL league': [341, 676], 'IPL knockout': [20, 39], 'T20I non-knockout': [436, 858], 'T20I final': [5, 10], 'TOTAL': [802, 1583]}, size(ii[ii[t]]))
chk('A09', 'matches with no eligible innings', 35, int(837 - ii[ii.elig_pressure].match_id.nunique()))
chk('A10', 'revised matches with innings 1 retained', 8, int(ii[ii.elig_pressure & ii.revised_any].match_id.nunique())); chk('A11', 'no-result/partial matches retained', 14, int(ii[ii.elig_pressure & ii.noresult_partial].match_id.nunique()))
chk('A12', 'tie/super-over matches retained', 8, int(ii[ii.elig_pressure & ii.tie_or_superover].match_id.nunique())); chk('A13', 'incomplete innings 1 retained with flag', 10, int(ii.flag_incomplete_innings1.sum()))
E = dl[dl.elig_pressure]; Bt = dl[dl.batting_row_eligible]
def per(cat, f): return int(f(cat))
exp = {'deliveries': {'IPL league': 81564, 'IPL knockout': 4573, 'T20I non-knockout': 101434, 'T20I final': 1190, 'TOTAL': 188761},
       'legal': {'IPL league': 77896, 'IPL knockout': 4383, 'T20I non-knockout': 97285, 'T20I final': 1152, 'TOTAL': 180716},
       'balls_faced': {'IPL league': 78248, 'IPL knockout': 4403, 'T20I non-knockout': 97712, 'T20I final': 1154, 'TOTAL': 181517},
       'batter_innings_rows': {'IPL league': 5259, 'IPL knockout': 313, 'T20I non-knockout': 7086, 'T20I final': 91, 'TOTAL': 12749},
       'distinct_batters': {'IPL league': 334, 'IPL knockout': 128, 'T20I non-knockout': 658, 'T20I final': 66, 'TOTAL': 816},
       'bowler_innings_rows': {'IPL league': 4022, 'IPL knockout': 223, 'T20I non-knockout': 5073, 'T20I final': 58, 'TOTAL': 9376},
       'distinct_bowlers': {'IPL league': 259, 'IPL knockout': 92, 'T20I non-knockout': 470, 'T20I final': 41, 'TOTAL': 589},
       'wp_training_deliveries': {'IPL league': 80141, 'IPL knockout': 4451, 'T20I non-knockout': 98595, 'T20I final': 1190, 'TOTAL': 184377}}
act = {k: {} for k in exp}
for c_ in CATS + ['TOTAL']:
    e_ = E if c_ == 'TOTAL' else E[E.cat == c_]; b_ = Bt if c_ == 'TOTAL' else Bt[Bt.cat == c_]; w_ = dl[dl.elig_wp_training] if c_ == 'TOTAL' else dl[dl.elig_wp_training & (dl.cat == c_)]
    act['deliveries'][c_] = len(e_); act['legal'][c_] = int(e_.is_legal.sum()); act['balls_faced'][c_] = len(b_); act['batter_innings_rows'][c_] = b_.groupby(['match_id', 'innings', 'striker_id']).ngroups
    act['distinct_batters'][c_] = int(b_.striker_id.nunique()); act['bowler_innings_rows'][c_] = e_.groupby(['match_id', 'innings', 'bowler_id']).ngroups; act['distinct_bowlers'][c_] = int(e_.bowler_id.nunique()); act['wp_training_deliveries'][c_] = len(w_)
for k in exp: chk('A14_' + k, f'exposure: {k}', exp[k], act[k])
chk('A15', 'player exposure tables: batters / bowlers', [816, 589], [len(bx), len(wx)])
chk('A16', 'extras raw label counts', {'(none)': 189167, 'Overstep': 576, 'Penalty': 1, 'byes': 529, 'legbyes': 2748, 'other': 264, 'wide': 7714}, dl.extras_type.fillna('(none)').value_counts().to_dict())
chk('A17', 'extras clean labels: untyped_extra / relabelled leg-bye / (none)', [2, 2747, 189166], [int((dl.extras_type_clean == 'untyped_extra').sum()), int((dl.extras_type_clean == 'legbyes').sum()), int(dl.extras_type_clean.isna().sum())])
# ---- B. internal invariants (independent of the tables' own derived columns)
chk('B01', 'delivery rows', 200999, len(dl)); chk('B02', 'delivery key unique', 0, int(dl.duplicated(['match_id', 'innings', 'innings_ball_num']).sum()))
rb = raw_b.assign(t=raw_b.runs + raw_b.extras1_runs + raw_b.extras_2_runs).groupby(['match_id', 'innings']).t.sum()
tb = dl.groupby(['match_id', 'innings']).agg(total=('team_runs', 'sum'), charged=('bowler_charged_runs', 'sum'), unch=('uncharged_extras', 'sum'))
chk('B03', 'team total per innings equals raw runs+extras1+extras2 (all innings)', 0, int((tb.total != rb.reindex(tb.index)).sum()))
chk('B04', 'bowler-charged + uncharged extras = team total (every innings): no category lost or double counted', 0, int(((tb.charged + tb.unch) != tb.total).sum()))
chk('B05', 'batter runs on balls faced = bat runs (wides carry none)', int(raw_b.runs.sum()), int(dl.loc[dl.batter_ball_faced, 'batter_runs'].sum()))
legal_raw = (~raw_b.extras_type.isin(['wide', 'Overstep', 'other'])).groupby([raw_b.match_id, raw_b.innings]).sum(); lg = dl.groupby(['match_id', 'innings']).is_legal.sum()
chk('B06', 'legal balls per innings equal independent count from raw labels', 0, int((lg != legal_raw.reindex(lg.index)).sum())); chk('B07', 'no innings 1-2 above 120 legal balls', 0, int((lg.reset_index().query('innings<=2').is_legal > 120).sum()))
last = dl.sort_values(['match_id', 'innings', 'innings_ball_num']).groupby(['match_id', 'innings']).tail(1).set_index(['match_id', 'innings'])
chk('B08', 'runs_before + last delivery runs = innings total (state bookkeeping)', 0, int(((last.runs_before + last.team_runs) != tb.total.reindex(last.index)).sum()))
wk = dl.groupby(['match_id', 'innings']).is_wicket.sum(); chk('B09', 'wickets_before + last = innings wickets', 0, int(((last.wickets_before + last.is_wicket.astype(int)) != wk.reindex(last.index)).sum()))
el = dl[dl.elig_pressure & dl.innings.isin([1, 2])]; chk('B10', 'legal balls left before each eligible delivery within 0..120', 0, int(((el.legal_left_before < 0) | (el.legal_left_before > 120)).sum()))
chk('B11', 'WP-training innings are a subset of pressure-eligible innings', 0, int((ii.elig_wp_training & ~ii.elig_pressure).sum())); chk('B12', 'batting rows eligible imply innings eligible and ball faced', 0, int((dl.batting_row_eligible & ~(dl.elig_batting & dl.batter_ball_faced)).sum()))
e2 = ii[(ii.innings == 2) & ii.elig_pressure & ~ii.revised_any]; t1 = ii.merge(d['ball_by_ball'].groupby(['match_id', 'innings']).apply(lambda g: int((g.runs + g.extras1_runs + g.extras_2_runs).sum()), include_groups=False).rename('tot').reset_index(), on=['match_id', 'innings'])
t1 = t1[t1.innings == 1].set_index('match_id').tot; chk('B13', 'innings-2 target = innings-1 total + 1 (eligible non-revised)', 0, int((e2.target.values != (e2.match_id.map(t1) + 1).values).sum()))
fhd = dl[dl.free_hit]; viol = fhd[fhd.bowler_wicket_credit]
chk('B14', 'free-hit deliveries with a bowler-credited dismissal (not possible under the free-hit rule [KNOW])', 0, len(viol)); chk('B15', 'free-hit flag only follows no-ball-like deliveries: first innings delivery never flagged', 0, int(dl[(dl.legal_before == 0) & (dl.runs_before == 0) & (dl.wickets_before == 0) & (dl.over_ball_num == 1) & (dl.overid == 1) & dl.free_hit].shape[0]))
chk('B16', 'bowlers with more than one arm / pace-spin value', [0, 0], [int(wx.arm.str.contains(',').sum()), int(wx.pace_or_spin.str.contains(',').sum())])
chk('B17', 'batters with one role; modal order within 1..13', [0, True], [int(bx.batting_role.isna().sum()), bool(bx.modal_batting_order.between(1, 13).all())])
chk('B18', 'wickets with unattributed dismissed player (Retire Out, match 40709)', 1, int((dl.dismissed_role == 'unattributed').sum()))
chk('B19', 'null player ids on eligible rows', 0, int(E[['striker_id', 'non_striker_id', 'bowler_id']].isna().sum().sum()))
raw_kind = raw_b.extras_type.map({'wide': 'wide', 'Overstep': 'overstep', 'other': 'other'}).fillna('legal')
dls = dl.sort_values(['match_id', 'innings', 'innings_ball_num']).reset_index(drop=True); rs = raw_b.sort_values(['match_id', 'innings', 'innings_ball_num']).reset_index(drop=True); rk = raw_kind.loc[rs.index] if False else rs.extras_type.map({'wide': 'wide', 'Overstep': 'overstep', 'other': 'other'}).fillna('legal')
chk('B20', 'batter_ball_faced equals independent rule (not a wide) on every delivery', 0, int((dls.batter_ball_faced != (rs.extras_type != 'wide')).sum()))
chk('B21', 'batting_row_eligible = innings eligible AND ball faced', 0, int((dl.batting_row_eligible != (dl.elig_batting & dl.batter_ball_faced)).sum()))
ind_charge = rs.runs + rs.extras1_runs.where(rk.isin(['wide', 'overstep', 'other']), 0)
chk('B22', 'bowler_charged_runs equals independent recomputation from raw columns', 0, int((dls.bowler_charged_runs != ind_charge).sum()))
chk('B23', 'delivery_kind equals independent mapping from raw extras_type', 0, int((dls.delivery_kind != rk).sum()))
# ---- C. cross-check against Stage 3b audit outputs (independent implementation)
s3b = out / 'stage3b' / 's3b_innings_eligibility.csv'
if s3b.exists():
    x = pd.read_csv(s3b)[['match_id', 'innings', 'elig_pressure', 'elig_wp_training']].merge(ii[['match_id', 'innings', 'elig_pressure', 'elig_wp_training']], on=['match_id', 'innings'], suffixes=('_3b', '_s1'), how='outer')
    chk('C01', 'Step 1 innings flags equal Stage 3b audit flags', 0, int(((x.elig_pressure_3b != x.elig_pressure_s1) | (x.elig_wp_training_3b != x.elig_wp_training_s1)).sum()))
res = pd.DataFrame(R); res.to_csv(S1 / 'step1_validation.csv', index=False)
print(res[['id', 'status', 'description']].to_string(index=False)); nf = int(((res.status == 'FAIL') & res.hard).sum()); print(f'\n{(res.status == "PASS").sum()} PASS, {(res.status == "FAIL").sum()} FAIL')
sys.exit(1 if nf else 0)

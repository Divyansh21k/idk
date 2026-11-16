"""Stage 3 (pre-cleaning): audit of `stage` / `knock_out`, sample sizes by category, descriptive league-vs-knockout comparison.
Nothing is cleaned or dropped from data; preliminary exclusion flags are applied only inside this analysis and are listed.
Usage: python src/stage3_stage_audit.py --raw-dir data/raw --out-dir outputs"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
def jd(x): return json.dumps({str(k): int(v) for k, v in dict(x).items()})
sys.path.insert(0, str(Path(__file__).parent))
from common import load_raw, default_dirs, mkdirs, add_scope
ap = argparse.ArgumentParser(); ap.add_argument('--raw-dir'); ap.add_argument('--out-dir'); ap.add_argument('--reps', type=int, default=2000); a = ap.parse_args()
raw, out = default_dirs(a.raw_dir, a.out_dir); d, _ = load_raw(raw); P3 = mkdirs(out, 'stage3')['stage3']
b, m, c, p, t, cm = (d[k] for k in ['ball_by_ball','matches','competitions','playing_eleven','teams','competition_team_player_mapping'])
c2 = add_scope(c); mm = m.merge(c2, on='comp_id'); mm['has_bbb'] = mm.match_id.isin(b.match_id); mm['date'] = pd.to_datetime(mm.match_date)
md = []; W = md.append
def H(s): W(f'\n## {s}\n')
def T(df, n=80): W('```\n' + df.head(n).to_string(index=False) + (f'\n... ({len(df)} rows)' if len(df) > n else '') + '\n```')
W('# Stage 3 pre-cleaning audit: stage / knock_out (generated)')

# ---------------------------------------------------------------- A. field audit
H('A. Field audit')
W(f'[DATA] `stage` dtype {m.stage.dtype}, nulls {int(m.stage.isna().sum())}; `knock_out` dtype {m.knock_out.dtype}, nulls {int(m.knock_out.isna().sum())}, values {sorted(m.knock_out.unique().tolist())}')
W('[DATA] stage x knock_out by scope:'); T(pd.crosstab([mm.scope, mm.stage], mm.knock_out).reset_index())
KO_STAGES = {'Final','Qualifier','Eliminator','Semi Final'}
incons = mm[(mm.knock_out == 1) != mm.stage.isin(KO_STAGES)]
W(f'[DATA] matches where knock_out=1 disagrees with stage in {sorted(KO_STAGES)}: {len(incons)}')
W('[DATA] knockout matches by competition:'); T(mm[mm.knock_out == 1].groupby(['scope','comp_name','stage']).size().rename('matches').reset_index())
# IPL structure checks
ipl = mm[mm.scope == 'IPL'].sort_values(['comp_name','match_number'])
rows = []
for comp, g in ipl.groupby('comp_name'):
    ko = g[g.knock_out == 1]; lg = g[g.knock_out == 0]
    rows.append(dict(comp=comp, n=len(g), league=len(lg), knockouts=len(ko), ko_match_numbers=list(ko.match_number), last_league_number=lg.match_number.max(),
                     ko_all_after_league_by_number=bool(ko.match_number.min() > lg.match_number.max()), ko_all_after_league_by_date=bool(ko.date.min() >= lg.date.max()),
                     order_by_number=' > '.join(ko.sort_values('match_number').stage), has_bbb_all=bool(g.has_bbb.all())))
ik = pd.DataFrame(rows); W('[DATA] IPL structure: do the 4 knockouts sit after all league matches (by match_number and by date), and in what stage order?'); T(ik)
ik.to_csv(P3 / 's3_ipl_knockout_structure.csv', index=False)
# T20I stage semantics
t20 = mm[mm.scope == 'T20I']
tg = t20.groupby('comp_name').agg(n=('match_id', 'size'), ko=('knock_out', 'sum'), first=('match_date', 'min'), last=('match_date', 'max'), stages=('stage', lambda s: jd(s.value_counts()))).reset_index()
W(f'[DATA] T20I competitions: {len(tg)}; with >= 8 matches (tournament-like): {int((tg.n >= 8).sum())}; with any knock_out: {int((tg.ko > 0).sum())}; names containing "World": {int(tg.comp_name.str.contains("World", case=False).sum())}')
W('[DATA] T20I competitions with >= 8 matches, and every competition with a knockout:'); T(tg[(tg.n >= 8) | (tg.ko > 0)].sort_values('first'))
W('[DATA] T20I stage value counts: ' + jd(t20.stage.value_counts()) + ' -> "Others" = ' + str(int((t20.stage == 'Others').sum())) + ' matches; the label never appears in IPL.')
W('[INFERENCE, [KNOW]-assisted] Asia Cup 2022 has 12 "League" matches + Final = 13, while Asia Cup 2025 has 12 League + 6 "Super 4" + Final = 19: the 2022 Super-Four matches are most likely labelled "League". The files cannot confirm this.')
W('[OPEN] `stage` has different semantics in IPL (League = round robin) and T20I (League = group/tournament OR series match; Others = series match). Only `knock_out` (Final/Qualifier/Eliminator/Semi Final) is comparable across competitions, and in T20I it flags only 5 finals.')
tg.to_csv(P3 / 's3_t20i_competition_stage_summary.csv', index=False)
# Playoff sub-type inference within IPL (order within season)
ko_ipl = ipl[ipl.knock_out == 1].copy()
ko_ipl['ord'] = ko_ipl.groupby('comp_name').cumcount() + 1
sub = {1: 'Qualifier-1 (by order)', 2: 'Eliminator (by order)', 3: 'Qualifier-2 (by order)', 4: 'Final'}
ko_ipl['playoff_role_inferred'] = ko_ipl.ord.map(sub); ko_ipl['stage_label_agrees'] = ko_ipl.apply(lambda r: r.stage in r.playoff_role_inferred, axis=1)
W(f'[DATA/KNOW] IPL playoff role inferred from chronological order within season (Q1, Eliminator, Q2, Final): stage label agrees for {int(ko_ipl.stage_label_agrees.sum())} of {len(ko_ipl)} matches')
T(ko_ipl[['comp_name','match_number','match_date','stage','playoff_role_inferred','stage_label_agrees','has_bbb','result']])
ko_ipl.to_csv(P3 / 's3_ipl_playoff_matches.csv', index=False)

# ---------------------------------------------------------------- B. analysis base (preliminary flags only)
H('B. Preliminary analysis base (flags, nothing deleted)')
inn = pd.read_csv(out / 'stage2' / 's2_innings_summary.csv')
rv = mm[mm.revised_target.notna() | mm.first_inn_revised_overs.notna() | mm.second_inn_revised_overs.notna() | mm.result.str.contains(r'D/?L|DLS', case=False, regex=True)].match_id
dq = [14130, 20190]
bs = b[b.innings.isin([1, 2])].merge(mm[['match_id','scope','season','stage','knock_out','comp_name']], on='match_id')
bs = bs[bs.scope.isin(['IPL','T20I']) & ~bs.match_id.isin(rv) & ~bs.match_id.isin(dq)].copy()
bs['legal'] = ~bs.extras_type.isin(['wide','Overstep','other'])
bs['cat'] = np.where(bs.scope == 'IPL', np.where(bs.knock_out == 1, 'IPL knockout', 'IPL league'), np.where(bs.knock_out == 1, 'T20I knockout (final)', 'T20I non-knockout'))
bs['dot'] = (bs.runs == 0) & bs.legal & bs.extras_type.isna(); bs['bound'] = bs.is_four | bs.is_six
bs['late'] = bs.overid >= 16
W(f'[DATA] preliminary flags: scope IPL+T20I only; excluded matches: revised/D-L {len(set(rv))}, data-quality {dq}; innings 1-2 only (super-over innings and OTHER competitions excluded); legal = not wide/Overstep/other. Deliveries kept: {len(bs):,} of {len(b):,}')
# match counts by category
mc = mm[mm.scope.isin(['IPL','T20I']) & mm.has_bbb & ~mm.match_id.isin(rv) & ~mm.match_id.isin(dq)].assign(cat=lambda df: np.where(df.scope == 'IPL', np.where(df.knock_out == 1, 'IPL knockout', 'IPL league'), np.where(df.knock_out == 1, 'T20I knockout (final)', 'T20I non-knockout')))
W('[DATA] matches by category (with ball-by-ball, after preliminary flags):'); T(mc.groupby('cat').size().rename('matches').reset_index())
W('[DATA] IPL knockouts by season and stage (all 20 have ball-by-ball and none is revised): ' + jd(ko_ipl.groupby('comp_name').size()) + '; any IPL knockout excluded by flags: ' + str(int(ko_ipl.match_id.isin(rv).sum() + ko_ipl.match_id.isin(dq).sum())))

pa = p[p.is_played == True].merge(mc[['match_id','cat']], on='match_id')
pa_t = pa.groupby('cat').agg(player_appearances=('player_id','size'), distinct_players=('player_id','nunique')).reset_index()
W('[DATA] player appearances (playing_eleven is_played=True) in the same preliminary base, by category:'); T(pa_t)
pa_t.to_csv(P3 / 's3_appearances_by_category.csv', index=False)
# ---------------------------------------------------------------- C. exposure counts by category
H('C. Exposure by category')
leg = bs[bs.legal]
exp = leg.groupby('cat').agg(deliveries=('runs', 'size'), batter_match_pairs=('striker_id', lambda s: 0), late_overs_16_20=('late', 'sum'), chase_late=('late', lambda s: 0)).reset_index()
bp = leg.groupby(['cat','match_id','striker_id']).size().reset_index().groupby('cat').size().rename('batter_innings_rows')
wp = leg.groupby(['cat','match_id','bowler_id']).size().reset_index().groupby('cat').size().rename('bowler_match_rows')
ch = leg[(leg.innings == 2) & leg.late].groupby('cat').size().rename('innings2_overs16_20_deliveries')
sx = leg.groupby('cat').agg(deliveries=('runs', 'size'), late_16_20=('late', 'sum'), distinct_batters=('striker_id', 'nunique'), distinct_bowlers=('bowler_id', 'nunique')).join([bp, wp, ch]).reset_index()
W('[DATA] legal deliveries, batter-match rows, bowler-match rows, distinct players, and a crude proxy of late-innings deliveries (overs 16-20; NOT the leverage-based pressure measure, which does not exist yet):'); T(sx)
sx.to_csv(P3 / 's3_exposure_by_category.csv', index=False)

# eligibility proxy
bat = leg.groupby('striker_id').size().rename('bat_total'); bow = leg.groupby('bowler_id').size().rename('bowl_total')
batk = leg.groupby(['striker_id','cat']).size().unstack(fill_value=0); bowk = leg.groupby(['bowler_id','cat']).size().unstack(fill_value=0)
for cc in ['IPL league','IPL knockout','T20I non-knockout','T20I knockout (final)']:
    for df in (batk, bowk):
        if cc not in df: df[cc] = 0
batk['KO'] = batk['IPL knockout'] + batk['T20I knockout (final)']; bowk['KO'] = bowk['IPL knockout'] + bowk['T20I knockout (final)']
rows = []
for role, tot, k in [('batter', bat, batk), ('bowler', bow, bowk)]:
    for thr in (300, 500):
        el = k.loc[tot[tot >= thr].index]
        row = dict(role=role, eligible_min_legal_balls=thr, eligible_players=len(el), with_any_KO_balls=int((el.KO > 0).sum()))
        for kk in (12, 30, 60, 120): row[f'KO_balls>={kk}'] = int((el.KO >= kk).sum())
        row['median_KO_balls_among_eligible'] = float(el.KO.median()); row['p75_KO_balls'] = float(el.KO.quantile(.75)); row['max_KO_balls'] = int(el.KO.max())
        row['median_league_IPL_balls'] = float(el['IPL league'].median())
        rows.append(row)
es = pd.DataFrame(rows); es.to_csv(P3 / 's3_eligibility_vs_knockout_exposure.csv', index=False)
W('[DATA] eligibility proxy (minimum legal balls in the preliminary base) vs knockout exposure of those players:'); T(es.T.reset_index().rename(columns={'index': 'metric'}), 20)

# ---------------------------------------------------------------- D. descriptive league vs knockout (IPL), unadjusted, match-cluster bootstrap
H('D. Descriptive league vs knockout comparison (IPL only, UNADJUSTED; EARLIER preliminary base and legal-ball unit; the current eligibility rules and units are in stage3b)')
ip = leg[leg.scope == 'IPL'].copy(); ip['ko'] = ip.knock_out == 1
ip['wk_bat'] = ip.is_wicket & ip.dismissal_type.isin(['Bowled','Caught','LBW','Stump','Hit Wicket','RunOut'])
ip['conc'] = ip.runs + np.where(ip.extras_type.isin(['wide','Overstep','other']), ip.extras1_runs, 0)
agg = ip.groupby(['match_id','innings','ko']).agg(n=('runs', 'size'), runs=('runs', 'sum'), dots=('dot', 'sum'), bnd=('bound', 'sum'), wk=('is_wicket', 'sum')).reset_index()
rng = np.random.default_rng(20260514)
def stat(df): n = df.n.sum(); return np.array([df.runs.sum() / n, df.dots.sum() / n, df.bnd.sum() / n, df.wk.sum() / n])
names = ['runs_per_legal_ball','dot_share','boundary_share','wicket_per_ball']
out_rows = []
for lab, sub in [('both innings', agg), ('innings 1', agg[agg.innings == 1]), ('innings 2', agg[agg.innings == 2])]:
    byk = {k: g.groupby('match_id') for k, g in sub.groupby('ko')}
    mids = {k: np.array(list(v.groups.keys())) for k, v in byk.items()}
    pm = {k: sub[sub.ko == k].groupby('match_id')[['n','runs','dots','bnd','wk']].sum() for k in (False, True)}
    obs = stat(sub[sub.ko]) - stat(sub[~sub.ko]); boots = []
    for _ in range(a.reps):
        ds = []
        for k in (True, False):
            ids = rng.choice(pm[k].index.values, size=len(pm[k]), replace=True); q = pm[k].loc[ids]
            ds.append(np.array([q.runs.sum(), q.dots.sum(), q.bnd.sum(), q.wk.sum()]) / q.n.sum())
        boots.append(ds[0] - ds[1])
    boots = np.array(boots)
    for i, nm in enumerate(names):
        out_rows.append(dict(subset=lab, metric=nm, league=stat(sub[~sub.ko])[i], knockout=stat(sub[sub.ko])[i], diff_KO_minus_league=obs[i], ci95_low=np.percentile(boots[:, i], 2.5), ci95_high=np.percentile(boots[:, i], 97.5),
                             ko_matches=int(sub[sub.ko].match_id.nunique()), ko_deliveries=int(sub[sub.ko].n.sum())))
cmp_ = pd.DataFrame(out_rows); cmp_.to_csv(P3 / 's3_ipl_league_vs_knockout_descriptive.csv', index=False)
T(cmp_.round(4), 20)
W(f'[DATA] bootstrap: {a.reps} resamples of whole matches within each group (seeded). These are population-level, state-UNADJUSTED differences: they mix who plays, innings state and opposition quality, so they show size/uncertainty, not a causal knockout effect.')

# ---------------------------------------------------------------- E. player-level reliability of knockout samples (unadjusted)
H('E. (earlier base; superseded by stage3b section D) How much of a player\'s knockout sample is signal? (method-of-moments reliability, unadjusted per-ball values)')
def reliability(df, pid, valcol, minn_league=120):
    g = df.groupby([pid, 'ko'])[valcol].agg(['mean', 'count', 'var']).reset_index()
    lg = g[(~g.ko) & (g['count'] >= minn_league)]
    sigma2 = df[~df.ko][valcol].var(ddof=1)
    tau2 = max(lg['mean'].var(ddof=1) - (sigma2 / lg['count']).mean(), 0)
    kg = g[g.ko]
    return dict(players_league_ge=len(lg), sigma_per_ball=np.sqrt(sigma2), tau_between_player=np.sqrt(tau2), median_KO_balls_all_KO_players=float(kg['count'].median()), KO_players=len(kg),
                reliability_at_median_KO_n=tau2 / (tau2 + sigma2 / max(kg['count'].median(), 1)), reliability_at_league_median_n=tau2 / (tau2 + sigma2 / lg['count'].median()), n_for_reliability_0p5=sigma2 / tau2 if tau2 > 0 else np.nan)
rb = reliability(ip.assign(v=ip.runs), 'striker_id', 'v'); rw = reliability(ip.assign(v=ip.conc), 'bowler_id', 'v')
rel = pd.DataFrame([dict(role='batter (bat runs per legal ball)', **rb), dict(role='bowler (runs conceded per legal ball)', **rw)]); rel.to_csv(P3 / 's3_knockout_reliability.csv', index=False); T(rel.round(3))
W('[DATA/METHOD] tau = estimated between-player SD of true per-ball means (league sample, players with >=120 legal IPL league balls); sigma = per-ball SD; reliability = tau^2/(tau^2 + sigma^2/n). Unadjusted for state, so tau is inflated by role and exposure differences; adjusted tau is smaller and reliabilities lower. Treat these as an UPPER bound.')
# paired league/KO per player
for role, pid, col in [('batters', 'striker_id', 'runs'), ('bowlers', 'bowler_id', 'conc')]:
    g = ip.groupby([pid, 'ko'])[col].agg(['mean', 'count']).unstack('ko'); g.columns = ['lg_mean','ko_mean','lg_n','ko_n']
    both = g[(g.lg_n >= 120) & (g.ko_n >= 12)].dropna()
    W(f'[DATA] {role} with >=120 league and >=12 knockout IPL legal balls: {len(both)}; mean (KO - league) per-ball value {float((both.ko_mean - both.lg_mean).mean()):.3f} (SE {float((both.ko_mean - both.lg_mean).std(ddof=1) / np.sqrt(len(both))):.3f}); correlation league vs knockout per-ball means: {float(both.lg_mean.corr(both.ko_mean)):.2f}; median KO balls in this group {float(both.ko_n.median()):.0f}')

# ---------------------------------------------------------------- F. population-level knockout deviation (no player-level output)
H('F. (earlier base; superseded by stage3b section E) Population-level knockout deviation')
res_f = []
for role, pid, col in [('batters', 'striker_id', 'runs'), ('bowlers', 'bowler_id', 'conc')]:
    g = ip.groupby([pid, 'ko'])[col].agg(['mean', 'count']).unstack('ko'); g.columns = ['lg_mean','ko_mean','lg_n','ko_n']
    both = g[(g.lg_n >= 120) & (g.ko_n >= 12)].dropna().copy()
    sig2 = ip[col].var(ddof=1); both['d'] = both.ko_mean - both.lg_mean; both['sv'] = sig2 * (1 / both.ko_n + 1 / both.lg_n)
    def est(df): return df.d.mean(), max(df.d.var(ddof=1) - df.sv.mean(), 0)
    k_hat, psi2 = est(both); bs_ = [est(both.sample(len(both), replace=True, random_state=int(i))) for i in range(a.reps)]
    kb = np.array([x[0] for x in bs_]); pb = np.sqrt(np.array([x[1] for x in bs_]))
    n_med = both.ko_n.median(); B = psi2 / (psi2 + sig2 / n_med)
    res_f.append(dict(role=role, players=len(both), kappa_hat=k_hat, kappa_ci_low=np.percentile(kb, 2.5), kappa_ci_high=np.percentile(kb, 97.5), psi_hat=np.sqrt(psi2), psi_ci_low=np.percentile(pb, 2.5), psi_ci_high=np.percentile(pb, 97.5),
                      sigma_per_ball=np.sqrt(sig2), median_KO_balls=n_med, shrink_weight_on_own_KO_deviation_at_median=B, share_of_players_psi_boot_is_zero=float((pb == 0).mean())))
rf = pd.DataFrame(res_f); rf.to_csv(P3 / 's3_population_knockout_deviation.csv', index=False); T(rf.round(4))
W('[DATA/METHOD] d_i = knockout mean minus league mean per ball (players with >=120 league and >=12 knockout IPL legal balls); psi^2 = Var(d) minus average sampling variance, floored at 0; bootstrap over players. UNADJUSTED for match state, so this is a rough guide; the adjusted model replaces it in Stage 4. A shrink weight near 0 means a player\'s own knockout sample barely moves his estimate away from "league estimate + population shift".')
shares = {'IPL knockout share of IPL legal deliveries': 4263 / (4263 + 77848), 'IPL knockout share of IPL overs 16-20 deliveries': 913 / (913 + 17518), 'IPL knockout share of IPL matches (all, incl. excluded)': 20 / 371,
          'IPL knockout share of all IPL+T20I legal deliveries in base': 4263 / (4263 + 77848 + 96961 + 1152)}
W('[DATA] reference-weight candidates (preliminary proxies; the final value is computed once from the leverage model before any player result is viewed): ' + json.dumps({k: round(v, 4) for k, v in shares.items()}))

# ---------------------------------------------------------------- G. can the supplied fields measure league-match importance?
H('G. League-match importance: what the supplied fields do and do not support')
lg_ipl = mm[(mm.scope == 'IPL') & (mm.knock_out == 0)]
tm_ = pd.concat([lg_ipl[['comp_name','match_id','home_team_id']].rename(columns={'home_team_id':'team'}), lg_ipl[['comp_name','match_id','away_team_id']].rename(columns={'away_team_id':'team'})])
pt = tm_.groupby(['comp_name','team']).size().groupby('comp_name').agg(['count','min','max']).rename(columns={'count':'teams'})
ordr = lg_ipl.sort_values(['comp_name','match_number']).groupby('comp_name').apply(lambda g: pd.Series(dict(date_monotonic_by_match_number=bool(g.date.is_monotonic_increasing), match_numbers_contiguous=bool((g.match_number.diff().dropna() == 1).all()), league_matches=len(g), no_winner=int(g.win_team_id.isna().sum()), matches_per_date_max=int(g.groupby('date').size().max()))), include_groups=False)
W('[DATA] IPL league matches per team per season, ordering and result availability:'); T(pt.join(ordr).reset_index())
t20n = mm[mm.scope == 'T20I'].groupby('comp_name').size()
W(f'[DATA] T20I: {len(t20n)} competitions; matches per competition: ' + json.dumps({str(k): int(v) for k, v in t20n.value_counts().sort_index().items()}) + ' (key = matches in the competition)')
W('[DATA] Fields available for league-match importance: competition, season, `stage` (all IPL league matches carry the single value "League"), `match_number`, `match_date`, `win_team_id`, `result`. There is no points table, no qualification rule, no tie-break rule and no remaining-fixture/qualification information in the files.')
W('[DATA/OPEN] Cumulative win-loss records could be computed from `win_team_id` (supported by the data), but converting a record into "how important was this league match" needs qualification rules (how many teams qualify, points for no-result, tie-breaks) that the supplied files do not contain. Therefore league-match tournament importance is NOT measurable here and no numerical importance score will be built.')

(P3 / 's3_stage_audit_report.md').write_text('\n'.join(md)); print('stage3 audit done')

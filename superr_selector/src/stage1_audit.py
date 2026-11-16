"""Stage 1: read-only raw-data audit.
Usage: python src/stage1_audit.py --raw-dir data/raw --out-dir outputs [--strict]
--strict: exit code 1 if any hard assertion fails (useful for CI; known anomalies WILL fail it)."""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from common import load_raw, default_dirs, mkdirs, add_scope, KEYS
from crossfile import run_assertions

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--raw-dir'); ap.add_argument('--out-dir'); ap.add_argument('--strict', action='store_true')
    a = ap.parse_args(); raw, out = default_dirs(a.raw_dir, a.out_dir)
    d, hashes = load_raw(raw)
    P = mkdirs(out, 'stage1', 'exceptions'); S, E = P['stage1'], P['exceptions']
    b, m, c, p, t, cm = (d[k] for k in ['ball_by_ball','matches','competitions','playing_eleven','teams','competition_team_player_mapping'])
    md = []; w = md.append
    w('# Stage 1 raw audit (generated)\n'); w('SHA-256 of raw files:\n```\n' + json.dumps(hashes, indent=1) + '\n```')
    # ---- column profile
    rows = []
    for f, df in d.items():
        w(f'\n## {f}.csv  shape={df.shape}')
        k = KEYS[f]; w(f'- full-row duplicates: {int(df.duplicated().sum())}; duplicate-key extra rows {k}: {int(df.duplicated(k).sum())}')
        for col in df.columns:
            s = df[col]; nn = int(s.isna().sum())
            r = dict(file=f, column=col, dtype=str(s.dtype), n_null=nn, pct_null=round(100 * nn / len(df), 3), nunique=int(s.nunique()))
            if pd.api.types.is_numeric_dtype(s) and s.dtype != bool: r['min'] = s.min(); r['max'] = s.max()
            elif s.nunique() <= 15: r['top'] = json.dumps(s.value_counts(dropna=False).head(15).to_dict(), default=str)
            rows.append(r)
    pd.DataFrame(rows).to_csv(S / 'column_profile.csv', index=False)
    # ---- scope
    c2 = add_scope(c); mm = m.merge(c2, on='comp_id', how='left', validate='m:1'); mm['has_bbb'] = mm.match_id.isin(b.match_id)
    w('\n## A. Scope'); w(c2.groupby(['scope','match_format']).size().to_string())
    w('\nMatches by scope x season x has_bbb:\n' + mm.groupby(['scope','season','has_bbb']).size().unstack(fill_value=0).to_string())
    def rtype(x):
        x = str(x).lower()
        return 'abandoned' if 'abandon' in x else 'no_result' if 'no result' in x else 'tie' if 'tie' in x else 'won' if 'won' in x else 'other'
    mm['rtype'] = mm.result.map(rtype); w('\nResult types: ' + json.dumps(mm.rtype.value_counts().to_dict()))
    mm[~mm.has_bbb][['match_id','comp_name','scope','season','match_date','result','rtype']].to_csv(E / 'matches_without_bbb.csv', index=False)
    mm[mm.revised_target.notna() | mm.first_inn_revised_overs.notna() | mm.second_inn_revised_overs.notna()][['match_id','comp_name','scope','result','first_inn_revised_overs','second_inn_revised_overs','revised_target']].to_csv(E / 'revised_target_matches.csv', index=False)
    # ---- cross-file assertions
    res = run_assertions(d, E)
    sc = c2.set_index('comp_id').scope; m_scope = m.set_index('match_id').comp_id.map(sc)
    def scope_counts(fn):
        if not fn: return ''
        x = pd.read_csv(E / fn)
        s_ = x.match_id.map(m_scope) if 'match_id' in x else x.comp_id.map(sc) if 'comp_id' in x else None
        return '' if s_ is None else json.dumps(s_.value_counts(dropna=False).to_dict())
    res['violations_by_scope'] = res.exception_file.map(scope_counts)
    res.to_csv(S.parent / 'cross_file_assertions.csv', index=False)
    w('\n## B. Cross-file assertions (competition/team/match-specific)\n' + res.drop(columns=['exception_file']).to_string(index=False))
    # ---- XI duplicates precise
    key = ['match_id','team_id','player_id']
    dup = p[p.duplicated(key, keep=False)].copy()
    dup['dup_group'] = dup.groupby(key).ngroup() + 1; dup['copies_in_group'] = dup.groupby('dup_group').dup_group.transform('size')
    valcols = [x for x in p.columns if x not in key]
    def differing(g): return ','.join([x for x in valcols if g[x].astype(str).nunique() > 1])
    diff = dup.groupby('dup_group').apply(differing, include_groups=False).rename('conflicting_columns')
    dup = dup.merge(diff, on='dup_group')
    names = cm[['player_id','player_name']].drop_duplicates('player_id')
    dup = dup.merge(names, on='player_id', how='left').merge(m[['match_id','comp_id','match_date','home_team','away_team']], on='match_id', how='left')
    dup = dup.sort_values(['match_id','team_id','player_id']).reset_index(drop=True)
    dup.to_csv(E / 'playing_eleven_duplicates_detail.csv', index=False)
    grp = dup.drop_duplicates('dup_group')
    w('\n## C. playing_eleven duplicate keys: precise accounting')
    w(f'- rows in duplicated keys: {len(dup)}; distinct duplicated keys: {dup.dup_group.nunique()}; extra rows (rows - keys): {len(dup) - dup.dup_group.nunique()}')
    w('- copies per key: ' + json.dumps(grp.copies_in_group.value_counts().sort_index().to_dict()) + '  -> 75 = (30 keys x 2) + (5 keys x 3 copies); extra rows = 30x1 + 5x2 = 40')
    w('- by match:\n' + dup.groupby(['match_id','home_team','away_team','match_date']).agg(rows=('dup_group','size'), keys=('dup_group','nunique')).to_string())
    w('- conflicting columns across groups: ' + json.dumps(grp.conflicting_columns.replace('', '(none: exact duplicate)').value_counts().to_dict()))
    exact = int(p.duplicated().sum()); w(f'- exact full-row duplicate rows in file: {exact}')
    w('\nActual records (all 75):\n' + dup[['dup_group','match_id','team_id','player_id','player_name','batting_order','is_played','is_captain','is_wk','is_impact','is_impact_off','conflicting_columns']].to_string(index=False))
    # ---- other value domains (kept from first pass)
    w('\n## D. ball_by_ball value domains')
    for col in ['innings','runs','extras_type','dismissal_type','pace_or_spin','batting_type']: w(f'- {col}: {json.dumps(b[col].value_counts(dropna=False).to_dict(), default=str)}')
    ts = pd.to_datetime(b.delivery_ist_time.str.replace(' UTC', ''), errors='coerce')
    w(f'- unparseable timestamps: {int(ts.isna().sum())}; bowl_speed zero {round((b.bowl_speed == 0).mean() * 100, 2)}%, negative {int((b.bowl_speed < 0).sum())}, >170: {int((b.bowl_speed > 170).sum())}')
    w(f'- runs==4 & not is_four: {int(((b.runs == 4) & ~b.is_four).sum())}; runs==6 & not is_six: {int(((b.runs == 6) & ~b.is_six).sum())}; is_four with runs!=4: {int((b.is_four & (b.runs != 4)).sum())}; is_six with runs!=6: {int((b.is_six & (b.runs != 6)).sum())}')
    pl = p[p.is_played == True]; g = pl.groupby(['match_id','team_id']).size()
    w(f'- played rows per (match,team): {json.dumps(g.value_counts().sort_index().to_dict())}')
    (S / 'stage1_audit_report.md').write_text('\n'.join(md))
    failed = res[(res.status == 'FAIL') & (res.severity == 'hard')]
    print(res[res.status=='FAIL'][['id','violations','violations_if_only_global_id_lookup','severity','violations_by_scope']].to_string(index=False))
    print(f'{(res.status=="PASS").sum()} assertions PASS, {(res.status=="FAIL").sum()} FAIL')
    print(f'\nStage 1 complete. Outputs in {Path(out).resolve()}. Hard failures: {len(failed)} (known anomalies are expected; see report).')
    if a.strict and len(failed): sys.exit(1)

if __name__ == '__main__': main()

"""Shared loading/validation helpers. Raw files are only ever read."""
import hashlib, os, sys
from pathlib import Path
import numpy as np, pandas as pd

REQUIRED = {
 'ball_by_ball': ['match_id','innings','overid','over_ball_num','innings_ball_num','batting_team_id','bowling_team_id','striker_id','striker_name','non_striker_id','non_striker_name','bowler_id','bowler_name','batting_type','bowling_type','batting_order','runs','is_four','is_six','is_wicket','dismissal_type_id','dismissal_type','dismissed_player_id','extras_type','extras1_runs','extras_2_runs','pace_or_spin','bowl_speed','stroke','delivery_style','over_or_around','on_or_off','delivery_ist_time'],
 'matches': ['match_id','comp_id','match_number','match_date','stage','venue_id','venue_country','home_team_id','home_team','away_team_id','away_team','home_team_captain_id','away_team_captain_id','toss_win_team_id','toss_opted','man_of_the_match','first_inn_revised_overs','second_inn_revised_overs','revised_target','knock_out','win_team_id','result'],
 'competitions': ['comp_id','comp_name','match_format','season'],
 'playing_eleven': ['match_id','team_id','player_id','batting_order','is_played','is_captain','is_wk','is_impact','is_impact_off'],
 'teams': ['comp_id','team_id','team_name'],
 'competition_team_player_mapping': ['comp_id','comp_name','team_id','team_name','player_id','player_name'],
}
KEYS = {'ball_by_ball':['match_id','innings','innings_ball_num'],'matches':['match_id'],'competitions':['comp_id'],
        'playing_eleven':['match_id','team_id','player_id'],'teams':['comp_id','team_id'],
        'competition_team_player_mapping':['comp_id','team_id','player_id']}

def default_dirs(argv_raw=None, argv_out=None):
    raw = argv_raw or os.environ.get('SUPERR_RAW_DIR') or 'data/raw'
    out = argv_out or os.environ.get('SUPERR_OUT_DIR') or 'outputs'
    return Path(raw), Path(out)

def load_raw(raw_dir):
    raw = Path(raw_dir)
    problems = []
    for f, cols in REQUIRED.items():
        p = raw / f'{f}.csv'
        if not p.is_file(): problems.append(f'MISSING FILE: {p}'); continue
        head = pd.read_csv(p, nrows=0).columns.tolist()
        miss = [c for c in cols if c not in head]
        if miss: problems.append(f'{f}.csv missing columns: {miss}')
    if problems:
        sys.exit('Input validation failed:\n  ' + '\n  '.join(problems))
    d, hashes = {}, {}
    for f in REQUIRED:
        p = raw / f'{f}.csv'
        hashes[f] = hashlib.sha256(p.read_bytes()).hexdigest()
        d[f] = pd.read_csv(p, low_memory=False)
    return d, hashes

def add_scope(comp):
    c = comp.copy()
    c['scope'] = np.where(c.comp_name.str.startswith('IPL'), 'IPL', np.where(c.match_format == 'T20I', 'T20I', 'OTHER'))
    return c

def mkdirs(out, *names):
    paths = {}
    for n in names:
        p = Path(out) / n; p.mkdir(parents=True, exist_ok=True); paths[n] = p
    return paths

def anti(left, right, lk, rk=None):
    """Rows of `left` whose key tuple `lk` is absent from `right[rk]`. Rows with null keys are excluded."""
    rk = rk or lk
    l = left[left[lk].notna().all(axis=1)]
    r = right[rk].dropna().drop_duplicates(); r.columns = lk
    m = l[lk].merge(r, how='left', on=lk, indicator=True)
    return l[(m['_merge'] == 'left_only').values]

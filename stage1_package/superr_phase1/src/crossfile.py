"""Competition-/team-/match-specific cross-file assertions. Each assertion writes its violating records."""
import pandas as pd, numpy as np
from common import anti

def run_assertions(d, exc_dir):
    b, m, c, p, t, cm = (d[k] for k in ['ball_by_ball','matches','competitions','playing_eleven','teams','competition_team_player_mapping'])
    rec = []
    def A(aid, rel, desc, checked, viol, severity='hard', global_viol=None):
        fn = ''
        if len(viol):
            fn = f'assert_{aid}.csv'; viol.to_csv(exc_dir / fn, index=False)
        rec.append(dict(id=aid, relationship=rel, description=desc, rows_checked=int(checked), violations=int(len(viol)),
                        status='PASS' if len(viol) == 0 else 'FAIL', severity=severity,
                        violations_if_only_global_id_lookup=global_viol if global_viol is not None else '', exception_file=fn))
    mt = m[['match_id','comp_id','home_team_id','away_team_id','home_team','away_team','toss_win_team_id','win_team_id']]
    # ---- uniqueness
    for aid, f in [('U1','ball_by_ball'),('U2','matches'),('U3','competitions'),('U4','playing_eleven'),('U5','teams'),('U6','competition_team_player_mapping')]:
        df = d[f]; k = {'ball_by_ball':['match_id','innings','innings_ball_num'],'matches':['match_id'],'competitions':['comp_id'],
                        'playing_eleven':['match_id','team_id','player_id'],'teams':['comp_id','team_id'],'competition_team_player_mapping':['comp_id','team_id','player_id']}[f]
        A(aid, f'{f}: unique key {k}', 'No duplicate keys', len(df), df[df.duplicated(k, keep=False)])
    # ---- competition / team membership  (comp_id, team_id)
    A('R1','matches.comp_id -> competitions.comp_id','Every match belongs to a listed competition', len(m), anti(m, c, ['comp_id']))
    A('R2','teams.comp_id -> competitions.comp_id','Every team row belongs to a listed competition', len(t), anti(t, c, ['comp_id']))
    A('R3','mapping.comp_id -> competitions.comp_id','Every mapping row belongs to a listed competition', len(cm), anti(cm, c, ['comp_id']))
    A('R4','mapping (comp_id,team_id) -> teams (comp_id,team_id)','Squad rows only for teams registered in that competition', len(cm), anti(cm, t, ['comp_id','team_id']),
      global_viol=len(anti(cm, t, ['team_id'])))
    A('R5','matches (comp_id,home_team_id) -> teams (comp_id,team_id)','Home team registered in the match competition', len(m), anti(m, t, ['comp_id','home_team_id'], ['comp_id','team_id']),
      global_viol=len(anti(m, t, ['home_team_id'], ['team_id'])))
    A('R6','matches (comp_id,away_team_id) -> teams (comp_id,team_id)','Away team registered in the match competition', len(m), anti(m, t, ['comp_id','away_team_id'], ['comp_id','team_id']),
      global_viol=len(anti(m, t, ['away_team_id'], ['team_id'])))
    nm = m.merge(t.rename(columns={'team_id':'home_team_id','team_name':'_hn'}), on=['comp_id','home_team_id'], how='left').merge(t.rename(columns={'team_id':'away_team_id','team_name':'_an'}), on=['comp_id','away_team_id'], how='left')
    A('R7','matches.home/away_team (name) == teams.team_name for (comp_id,team_id)','Team names agree between files', len(m), nm[(nm.home_team != nm._hn) | (nm.away_team != nm._an)][['match_id','comp_id','home_team_id','home_team','_hn','away_team_id','away_team','_an']])
    A('R8','matches: home_team_id != away_team_id','Teams distinct', len(m), m[m.home_team_id == m.away_team_id])
    A('R9','matches.toss_win_team_id (non-null) in {home,away}','Toss winner is a match team', int(m.toss_win_team_id.notna().sum()), mt[mt.toss_win_team_id.notna() & ~((mt.toss_win_team_id == mt.home_team_id) | (mt.toss_win_team_id == mt.away_team_id))])
    A('R10','matches.win_team_id (non-null) in {home,away}','Winner is a match team', int(m.win_team_id.notna().sum()), mt[mt.win_team_id.notna() & ~((mt.win_team_id == mt.home_team_id) | (mt.win_team_id == mt.away_team_id))])
    cap = pd.concat([m[['match_id','comp_id','home_team_id','home_team_captain_id']].set_axis(['match_id','comp_id','team_id','player_id'], axis=1),
                     m[['match_id','comp_id','away_team_id','away_team_captain_id']].set_axis(['match_id','comp_id','team_id','player_id'], axis=1)]).dropna(subset=['player_id'])
    cap['player_id'] = cap.player_id.astype(int)
    A('R11','matches captain ids: (comp_id,team_id,player_id) -> mapping','Captain belongs to that team squad in that competition', len(cap),
      anti(cap, cm, ['comp_id','team_id','player_id']), global_viol=len(anti(cap, cm, ['player_id'])))
    mom = m[m.man_of_the_match != 0][['match_id','comp_id','man_of_the_match']].copy()
    mm2 = mom.merge(pd.concat([mt[['match_id','home_team_id']].rename(columns={'home_team_id':'team_id'}), mt[['match_id','away_team_id']].rename(columns={'away_team_id':'team_id'})]), on='match_id')
    mm2 = mm2.rename(columns={'man_of_the_match':'player_id'})
    ok = mm2.merge(cm[['comp_id','team_id','player_id']].drop_duplicates().assign(_h=1), on=['comp_id','team_id','player_id'], how='left').groupby('match_id')._h.max()
    bad_ids = ok[ok.isna()].index
    A('R12','matches.man_of_the_match (non-zero): (comp_id, either match team, player_id) -> mapping','MoM id (semantics undocumented) is a squad player of one of the two teams', len(mom), m[m.match_id.isin(bad_ids)][['match_id','comp_id','home_team','away_team','man_of_the_match']], severity='soft')
    # ---- ball-by-ball structure
    A('R13','ball_by_ball.match_id -> matches','Every delivery belongs to a listed match', len(b), anti(b, m, ['match_id']))
    bb = b.merge(mt[['match_id','comp_id','home_team_id','away_team_id']], on='match_id', how='left')
    okpair = ((bb.batting_team_id == bb.home_team_id) & (bb.bowling_team_id == bb.away_team_id)) | ((bb.batting_team_id == bb.away_team_id) & (bb.bowling_team_id == bb.home_team_id))
    A('R14','ball_by_ball (batting_team_id,bowling_team_id) == matches {home,away}','Delivery teams are the two teams of that match, opposite sides', len(bb), bb[~okpair][['match_id','innings','innings_ball_num','batting_team_id','bowling_team_id','home_team_id','away_team_id']])
    A('R15','ball_by_ball (comp_id,batting_team_id) and (comp_id,bowling_team_id) -> teams','Delivery teams registered in the match competition', len(bb),
      pd.concat([anti(bb, t, ['comp_id','batting_team_id'], ['comp_id','team_id']), anti(bb, t, ['comp_id','bowling_team_id'], ['comp_id','team_id'])]).drop_duplicates()[['match_id','comp_id','batting_team_id','bowling_team_id']].drop_duplicates())
    inn = b[b.innings.isin([1, 2])].groupby(['match_id','innings']).batting_team_id.agg(lambda s: s.nunique()).reset_index()
    inn_multi = inn[inn.batting_team_id > 1]
    A('R16','ball_by_ball: one batting team per (match,innings)','Batting team constant within an innings', len(inn), inn_multi)
    t12 = b[b.innings.isin([1, 2])].groupby(['match_id','innings']).batting_team_id.first().unstack()
    t12 = t12.dropna()
    A('R17','ball_by_ball: innings 1 and 2 batting teams differ','Opposite teams bat in innings 1 and 2', len(t12), t12[t12[1] == t12[2]].reset_index())
    # ---- participants
    part = pd.concat([
        b[['match_id','batting_team_id','striker_id']].set_axis(['match_id','team_id','player_id'], axis=1).assign(role='striker'),
        b[['match_id','batting_team_id','non_striker_id']].set_axis(['match_id','team_id','player_id'], axis=1).assign(role='non_striker'),
        b[['match_id','bowling_team_id','bowler_id']].set_axis(['match_id','team_id','player_id'], axis=1).assign(role='bowler')]).drop_duplicates()
    part = part.merge(mt[['match_id','comp_id']], on='match_id', how='left')
    A('R18','ball_by_ball participants: (comp_id,team_id,player_id) -> mapping','Striker/non-striker (batting team) and bowler (bowling team) are squad members of that team in that competition', len(part),
      anti(part, cm, ['comp_id','team_id','player_id']), global_viol=len(anti(part, cm, ['player_id'])))
    pl = p[p.is_played == True]
    A('R19','ball_by_ball participants: (match_id,team_id,player_id) -> playing_eleven[is_played=True]','Participants listed as playing for that team in that match', len(part),
      anti(part, pl, ['match_id','team_id','player_id']), global_viol=len(anti(part, pl, ['match_id','player_id'])))
    A('R20','ball_by_ball participants: (match_id,team_id,player_id) -> playing_eleven (any row)','Participants appear in the XI table for that team at all', len(part),
      anti(part, p, ['match_id','team_id','player_id']), global_viol=len(anti(part, p, ['match_id','player_id'])))
    # ---- playing eleven
    A('R21','playing_eleven.match_id -> matches','XI rows belong to a listed match', len(p), anti(p, m, ['match_id']))
    px = p.merge(mt[['match_id','comp_id','home_team_id','away_team_id']], on='match_id', how='left')
    A('R22','playing_eleven.team_id in {home,away} of its match','XI row team is a team in that match', len(px), px[~((px.team_id == px.home_team_id) | (px.team_id == px.away_team_id))])
    A('R23','playing_eleven (comp_id,team_id,player_id) -> mapping','XI player is in the competition squad of that team', len(px), anti(px, cm, ['comp_id','team_id','player_id']),
      global_viol=len(anti(px, cm, ['player_id'])))
    both = pl.groupby(['match_id','player_id']).team_id.nunique().reset_index()
    A('R24','playing_eleven: a played player is on only one team per match','No player plays for both sides of one match', len(both), both[both.team_id > 1])
    cnt = p.groupby('match_id').team_id.nunique().reset_index()
    A('R25','playing_eleven: both match teams present for each XI match','Both teams have XI rows', len(cnt), cnt[cnt.team_id != 2])
    nx = m[~m.match_id.isin(p.match_id)][['match_id','comp_id','home_team','away_team','result']]
    A('R26','matches -> playing_eleven coverage','Each match has XI rows', len(m), nx, severity='soft')
    caps = pl.assign(cap=pl.is_captain.astype(str).str.lower() == 'true').groupby(['match_id','team_id']).cap.sum().reset_index()
    A('R27','playing_eleven: <=1 captain among played players per team-match','At most one captain flagged', len(caps), caps[caps.cap > 1], severity='soft')
    # ---- dismissals vs participants
    w = bb[bb.is_wicket & bb.dismissed_player_id.notna()]
    A('R28','ball_by_ball: dismissed_player_id in {striker_id, non_striker_id} of that delivery','Dismissed player was at the crease', len(w),
      w[(w.dismissed_player_id != w.striker_id) & (w.dismissed_player_id != w.non_striker_id)][['match_id','innings','innings_ball_num','striker_id','non_striker_id','dismissed_player_id','dismissal_type']])
    dd = w[['match_id','batting_team_id','dismissed_player_id']].drop_duplicates().rename(columns={'batting_team_id':'team_id','dismissed_player_id':'player_id'})
    A('R29','ball_by_ball dismissed player: (match_id,batting team,player_id) -> playing_eleven[is_played=True]','Dismissed batter is in that team XI for that match', len(dd), anti(dd.assign(player_id=dd.player_id.astype(int)), pl, ['match_id','team_id','player_id']))
    A('R30','ball_by_ball: striker_id != non_striker_id','Two different batters at the crease', len(b), b[b.striker_id == b.non_striker_id][['match_id','innings','overid','over_ball_num','innings_ball_num','striker_id','striker_name','non_striker_id','bowler_name','runs','is_wicket','dismissal_type']])
    A('R31','ball_by_ball: wicket flag <-> dismissal fields','is_wicket iff dismissal_type and dismissed_player_id present', len(b),
      b[(b.is_wicket & (b.dismissed_player_id.isna() | b.dismissal_type.isna())) | (~b.is_wicket & (b.dismissal_type.notna() | b.dismissed_player_id.notna()))])
    df = pd.DataFrame(rec); df.to_csv(exc_dir.parent / 'cross_file_assertions.csv', index=False)
    return df

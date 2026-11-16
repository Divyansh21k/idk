"""Negative controls: deliberately corrupt copies of the Step 1 tables and confirm the validation suite catches each corruption.
Usage: python tests/mutation_test_step1.py --raw-dir data/raw --out-dir outputs"""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path
import pandas as pd
ap = argparse.ArgumentParser(); ap.add_argument('--raw-dir', default='data/raw'); ap.add_argument('--out-dir', default='outputs'); a = ap.parse_args()
root = Path(__file__).resolve().parent.parent; out = Path(a.out_dir)
def run(mut_name, mutate, expect_ids):
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp) / 'out'; shutil.copytree(out / 'step1', t / 'step1'); (t / 'stage3b').mkdir(parents=True)
        if (out / 'stage3b' / 's3b_innings_eligibility.csv').exists(): shutil.copy(out / 'stage3b' / 's3b_innings_eligibility.csv', t / 'stage3b')
        mutate(t / 'step1')
        r = subprocess.run([sys.executable, str(root / 'src' / 'step1_validate.py'), '--raw-dir', a.raw_dir, '--out-dir', str(t)], capture_output=True, text=True)
        res = pd.read_csv(t / 'step1' / 'step1_validation.csv'); failed = set(res[res.status == 'FAIL'].id)
        ok = r.returncode != 0 and set(expect_ids) <= failed
        print(f"{'PASS' if ok else 'FAIL'}: mutation '{mut_name}' -> validator exit {r.returncode}, failed checks {sorted(failed)} (expected to include {expect_ids})"); return ok
def m_other_legal(p):
    d = pd.read_csv(p / 'deliveries_analysis.csv.gz', low_memory=False); d.loc[d.delivery_kind == 'other', 'is_legal'] = True; d.to_csv(p / 'deliveries_analysis.csv.gz', index=False, compression='gzip')
def m_drop_innings(p):
    i = pd.read_csv(p / 'innings_analysis.csv'); i.loc[i.index[(i.elig_pressure)][:1], 'elig_pressure'] = False; i.to_csv(p / 'innings_analysis.csv', index=False)
def m_wide_faced(p):
    d = pd.read_csv(p / 'deliveries_analysis.csv.gz', low_memory=False); d.loc[d.delivery_kind == 'wide', 'batter_ball_faced'] = True; d.to_csv(p / 'deliveries_analysis.csv.gz', index=False, compression='gzip')
def m_charge_byes(p):
    d = pd.read_csv(p / 'deliveries_analysis.csv.gz', low_memory=False); d.loc[d.extras_type == 'byes', 'bowler_charged_runs'] += d.loc[d.extras_type == 'byes', 'extras1_runs']; d.to_csv(p / 'deliveries_analysis.csv.gz', index=False, compression='gzip')
def m_freehit(p):
    d = pd.read_csv(p / 'deliveries_analysis.csv.gz', low_memory=False); i = d.index[d.bowler_wicket_credit & ~d.free_hit][:3]; d.loc[i, 'free_hit'] = True; d.to_csv(p / 'deliveries_analysis.csv.gz', index=False, compression='gzip')
def m_charge_noball(p):
    d = pd.read_csv(p / 'deliveries_analysis.csv.gz', low_memory=False); d.loc[d.delivery_kind == 'overstep', 'bowler_charged_runs'] -= 1; d.loc[d.delivery_kind == 'overstep', 'uncharged_extras'] += 1; d.to_csv(p / 'deliveries_analysis.csv.gz', index=False, compression='gzip')
res = [run('do not charge the no-ball penalty to the bowler', m_charge_noball, ['B22']), run('treat `other` as a legal ball', m_other_legal, ['B06']), run('drop one eligible innings', m_drop_innings, ['A08p']), run('count wides as balls faced', m_wide_faced, ['B20']),
       run('charge byes to the bowler', m_charge_byes, ['B04']), run('mis-flag free hits on credited wickets', m_freehit, ['B14'])]
print(f'\n{sum(res)} of {len(res)} negative controls detected'); sys.exit(0 if all(res) else 1)

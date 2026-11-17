"""
Targeted Statistical Verification Pipeline:
1. Re-estimate variance components within 500 match-cluster bootstrap resamples.
2. Compare fixed vs re-estimated bootstrap interval widths, rank intervals, and P(Top 10).
3. Compute exact empirical Bayes posterior intervals, P(mu > 0), and P(Top 10).
4. Export TARGETED_AUDIT_PLAYER_PROBABILITIES.csv.
"""
import sys, os, time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

def run_targeted_verification():
    print("=== Targeted Statistical Verification Pipeline ===")
    np.random.seed(42)

    base_dir = Path("superr_selector")
    out_dir = base_dir / "outputs"
    step1_dir = out_dir / "step1"
    step2_dir = out_dir / "step2"
    step3_dir = out_dir / "step3"

    print("1. Loading datasets...")
    ev = pd.read_csv(step2_dir / "deliveries_with_ev.csv.gz", low_memory=False)
    press = pd.read_csv(step3_dir / "all_deliveries_pressure.csv.gz", low_memory=False)
    bexp = pd.read_csv(step1_dir / "player_exposure_batters.csv")
    wexp = pd.read_csv(step1_dir / "player_exposure_bowlers.csv")

    bat_final = pd.read_csv(out_dir / "FINAL_REPAIRED_BATTER_RANKINGS.csv")
    bowl_final = pd.read_csv(out_dir / "FINAL_REPAIRED_BOWLER_RANKINGS.csv")

    df = press[[
        'match_id', 'innings', 'innings_ball_num', 'striker_id', 'bowler_id',
        'cat', 'season', 'PI_final', 'leverage_final', 'elig_batting', 'elig_bowling'
    ]].merge(
        ev[['match_id', 'innings', 'innings_ball_num', 'v_bat', 'v_bowl']],
        on=['match_id', 'innings', 'innings_ball_num'],
        how='inner'
    )
    df['is_hp'] = df['PI_final'] >= 0.800

    matches_df = df[['match_id', 'cat']].drop_duplicates()
    cats = matches_df['cat'].unique()
    match_cats = {c: matches_df[matches_df['cat'] == c]['match_id'].values for c in cats}

    # -----------------------------------------------------------------
    # A. BATTERS: FIXED vs RE-ESTIMATED VARIANCE-COMPONENT BOOTSTRAP
    # -----------------------------------------------------------------
    print("\n2. Running Batters Bootstrap Comparison (Fixed vs Re-estimated Variance Components)...")
    hp_bat = df[(df['elig_batting'] == 1) & (df['is_hp'])].copy()
    hp_bat = hp_bat.merge(bexp[['player_id', 'batting_role']], left_on='striker_id', right_on='player_id', how='left')

    # Full sample estimates
    sigma_e2_bat_full = hp_bat['v_bat'].var()
    role_means_bat_full = hp_bat.groupby('batting_role')['v_bat'].mean().to_dict()
    global_mean_bat_full = hp_bat['v_bat'].mean()
    bat_player_hp = hp_bat.groupby('striker_id').agg(n=('v_bat', 'count'), mean_v=('v_bat', 'mean'))
    sample_bat = bat_player_hp[bat_player_hp['n'] >= 20]
    sigma_mu2_bat_full = max(sample_bat['mean_v'].var() - sigma_e2_bat_full * (1.0 / sample_bat['n']).mean(), 0.005)

    eligible_bat_ids = set(bat_final['player_id'])
    bat_role_lookup = bat_final.set_index('player_id')['role'].to_dict()

    # Pre-aggregate match records for fast bootstrap
    bat_match_records = {}
    for m, g in hp_bat.groupby('match_id'):
        bat_match_records[m] = {
            'strikers': g['striker_id'].values,
            'roles': g['batting_role'].values,
            'v': g['v_bat'].values
        }

    n_boots = 500
    # Fixed bootstrap storage
    bat_ratings_fixed = {pid: [] for pid in eligible_bat_ids}
    bat_ranks_fixed = {pid: [] for pid in eligible_bat_ids}
    # Re-estimated bootstrap storage
    bat_ratings_reest = {pid: [] for pid in eligible_bat_ids}
    bat_ranks_reest = {pid: [] for pid in eligible_bat_ids}
    bat_sigma_e2_dist = []
    bat_sigma_mu2_dist = []

    np.random.seed(42)
    for b in range(n_boots):
        sampled_matches = []
        for c in cats:
            m_list = match_cats[c]
            sampled_matches.extend(np.random.choice(m_list, size=len(m_list), replace=True))

        # Re-aggregate data in resample b
        all_v = []
        role_v = {}
        player_counts = {}
        player_sums = {}

        for m in sampled_matches:
            if m in bat_match_records:
                rec = bat_match_records[m]
                all_v.extend(rec['v'])
                for pid, r, v in zip(rec['strikers'], rec['roles'], rec['v']):
                    role_v.setdefault(r, []).append(v)
                    player_counts[pid] = player_counts.get(pid, 0) + 1
                    player_sums[pid] = player_sums.get(pid, 0.0) + v

        # 1. Re-estimated parameters
        all_v_arr = np.array(all_v)
        sigma_e2_b = np.var(all_v_arr, ddof=1) if len(all_v_arr) > 1 else sigma_e2_bat_full
        bat_sigma_e2_dist.append(sigma_e2_b)

        role_means_b = {r: np.mean(v_list) for r, v_list in role_v.items()}
        global_mean_b = np.mean(all_v_arr) if len(all_v_arr) > 0 else global_mean_bat_full

        means_20 = []
        inv_n_20 = []
        for pid, n in player_counts.items():
            if n >= 20:
                means_20.append(player_sums[pid] / n)
                inv_n_20.append(1.0 / n)
        if len(means_20) >= 5:
            sigma_mu2_b = max(np.var(means_20, ddof=1) - sigma_e2_b * np.mean(inv_n_20), 0.005)
        else:
            sigma_mu2_b = sigma_mu2_bat_full
        bat_sigma_mu2_dist.append(sigma_mu2_b)

        # 2. Score players under FIXED vs RE-ESTIMATED
        scores_fixed = {}
        scores_reest = {}

        for pid in eligible_bat_ids:
            n_b = player_counts.get(pid, 0)
            s_b = player_sums.get(pid, 0.0)
            p_role = bat_role_lookup.get(pid, 'opener (1-2)')

            # Fixed
            p_mean_fix = role_means_bat_full.get(p_role, global_mean_bat_full)
            if n_b > 0:
                lam_fix = (n_b * sigma_mu2_bat_full) / (n_b * sigma_mu2_bat_full + sigma_e2_bat_full)
                r_fix = (lam_fix * (s_b / n_b) + (1 - lam_fix) * p_mean_fix) * 100
            else:
                r_fix = p_mean_fix * 100
            bat_ratings_fixed[pid].append(r_fix)
            scores_fixed[pid] = r_fix

            # Re-estimated
            p_mean_re = role_means_b.get(p_role, global_mean_b)
            if n_b > 0:
                lam_re = (n_b * sigma_mu2_b) / (n_b * sigma_mu2_b + sigma_e2_b)
                r_re = (lam_re * (s_b / n_b) + (1 - lam_re) * p_mean_re) * 100
            else:
                r_re = p_mean_re * 100
            bat_ratings_reest[pid].append(r_re)
            scores_reest[pid] = r_re

        # Ranks under fixed
        sorted_fix = sorted(scores_fixed.items(), key=lambda x: x[1], reverse=True)
        for rk, (pid, _) in enumerate(sorted_fix, 1):
            bat_ranks_fixed[pid].append(rk)

        # Ranks under re-estimated
        sorted_re = sorted(scores_reest.items(), key=lambda x: x[1], reverse=True)
        for rk, (pid, _) in enumerate(sorted_re, 1):
            bat_ranks_reest[pid].append(rk)

    # -----------------------------------------------------------------
    # B. BOWLERS: FIXED vs RE-ESTIMATED VARIANCE-COMPONENT BOOTSTRAP
    # -----------------------------------------------------------------
    print("\n3. Running Bowlers Bootstrap Comparison (Fixed vs Re-estimated Variance Components)...")
    hp_bowl = df[(df['elig_bowling'] == 1) & (df['is_hp'])].copy()
    hp_bowl = hp_bowl.merge(wexp[['player_id', 'pace_or_spin']], left_on='bowler_id', right_on='player_id', how='left')

    sigma_e2_bowl_full = hp_bowl['v_bowl'].var()
    role_means_bowl_full = hp_bowl.groupby('pace_or_spin')['v_bowl'].mean().to_dict()
    global_mean_bowl_full = hp_bowl['v_bowl'].mean()
    bowl_player_hp = hp_bowl.groupby('bowler_id').agg(n=('v_bowl', 'count'), mean_v=('v_bowl', 'mean'))
    sample_bowl = bowl_player_hp[bowl_player_hp['n'] >= 20]
    sigma_mu2_bowl_full = max(sample_bowl['mean_v'].var() - sigma_e2_bowl_full * (1.0 / sample_bowl['n']).mean(), 0.005)

    eligible_bowl_ids = set(bowl_final['player_id'])
    bowl_role_lookup = bowl_final.set_index('player_id')['role'].to_dict()

    bowl_match_records = {}
    for m, g in hp_bowl.groupby('match_id'):
        bowl_match_records[m] = {
            'bowlers': g['bowler_id'].values,
            'roles': g['pace_or_spin'].values,
            'v': g['v_bowl'].values
        }

    bowl_ratings_fixed = {pid: [] for pid in eligible_bowl_ids}
    bowl_ranks_fixed = {pid: [] for pid in eligible_bowl_ids}
    bowl_ratings_reest = {pid: [] for pid in eligible_bowl_ids}
    bowl_ranks_reest = {pid: [] for pid in eligible_bowl_ids}
    bowl_sigma_e2_dist = []
    bowl_sigma_mu2_dist = []

    np.random.seed(42)
    for b in range(n_boots):
        sampled_matches = []
        for c in cats:
            m_list = match_cats[c]
            sampled_matches.extend(np.random.choice(m_list, size=len(m_list), replace=True))

        all_v = []
        role_v = {}
        player_counts = {}
        player_sums = {}

        for m in sampled_matches:
            if m in bowl_match_records:
                rec = bowl_match_records[m]
                all_v.extend(rec['v'])
                for pid, r, v in zip(rec['bowlers'], rec['roles'], rec['v']):
                    role_v.setdefault(r, []).append(v)
                    player_counts[pid] = player_counts.get(pid, 0) + 1
                    player_sums[pid] = player_sums.get(pid, 0.0) + v

        all_v_arr = np.array(all_v)
        sigma_e2_b = np.var(all_v_arr, ddof=1) if len(all_v_arr) > 1 else sigma_e2_bowl_full
        bowl_sigma_e2_dist.append(sigma_e2_b)

        role_means_b = {r: np.mean(v_list) for r, v_list in role_v.items()}
        global_mean_b = np.mean(all_v_arr) if len(all_v_arr) > 0 else global_mean_bowl_full

        means_20 = []
        inv_n_20 = []
        for pid, n in player_counts.items():
            if n >= 20:
                means_20.append(player_sums[pid] / n)
                inv_n_20.append(1.0 / n)
        if len(means_20) >= 5:
            sigma_mu2_b = max(np.var(means_20, ddof=1) - sigma_e2_b * np.mean(inv_n_20), 0.005)
        else:
            sigma_mu2_b = sigma_mu2_bowl_full
        bowl_sigma_mu2_dist.append(sigma_mu2_b)

        scores_fixed = {}
        scores_reest = {}

        for pid in eligible_bowl_ids:
            n_b = player_counts.get(pid, 0)
            s_b = player_sums.get(pid, 0.0)
            p_role = bowl_role_lookup.get(pid, 'Pace')

            # Fixed
            p_mean_fix = role_means_bowl_full.get(p_role, global_mean_bowl_full)
            if n_b > 0:
                lam_fix = (n_b * sigma_mu2_bowl_full) / (n_b * sigma_mu2_bowl_full + sigma_e2_bowl_full)
                r_fix = (lam_fix * (s_b / n_b) + (1 - lam_fix) * p_mean_fix) * 100
            else:
                r_fix = p_mean_fix * 100
            bowl_ratings_fixed[pid].append(r_fix)
            scores_fixed[pid] = r_fix

            # Re-estimated
            p_mean_re = role_means_b.get(p_role, global_mean_b)
            if n_b > 0:
                lam_re = (n_b * sigma_mu2_b) / (n_b * sigma_mu2_b + sigma_e2_b)
                r_re = (lam_re * (s_b / n_b) + (1 - lam_re) * p_mean_re) * 100
            else:
                r_re = p_mean_re * 100
            bowl_ratings_reest[pid].append(r_re)
            scores_reest[pid] = r_re

        sorted_fix = sorted(scores_fixed.items(), key=lambda x: x[1], reverse=True)
        for rk, (pid, _) in enumerate(sorted_fix, 1):
            bowl_ranks_fixed[pid].append(rk)

        sorted_re = sorted(scores_reest.items(), key=lambda x: x[1], reverse=True)
        for rk, (pid, _) in enumerate(sorted_re, 1):
            bowl_ranks_reest[pid].append(rk)

    # -----------------------------------------------------------------
    # C. BUILD TARGETED_AUDIT_PLAYER_PROBABILITIES.csv
    # -----------------------------------------------------------------
    print("\n4. Generating TARGETED_AUDIT_PLAYER_PROBABILITIES.csv...")
    sigma_mu_bat = np.sqrt(sigma_mu2_bat_full) * 100 # 18.68 runs/100b
    sigma_mu_bowl = np.sqrt(sigma_mu2_bowl_full) * 100 # 14.94 runs/100b

    records = []

    # Process Batters
    for _, r in bat_final.iterrows():
        pid = r['player_id']
        lam = r['reliability']
        r_hp = r['R_HP']
        
        # Empirical Bayes Posterior standard deviation
        sd_post = np.sqrt(max(1.0 - lam, 0.001)) * sigma_mu_bat
        post_lo = r_hp - 1.645 * sd_post
        post_hi = r_hp + 1.645 * sd_post
        p_pos = stats.norm.cdf(r_hp / max(sd_post, 1e-4))
        
        # Re-estimated bootstrap stats
        re_arr = np.array(bat_ratings_reest[pid])
        re_rk = np.array(bat_ranks_reest[pid])
        ci_lo_re = np.percentile(re_arr, 5)
        ci_hi_re = np.percentile(re_arr, 95)
        width_fixed = r['CI_90_hi'] - r['CI_90_lo']
        width_reest = ci_hi_re - ci_lo_re
        p_top10_re = (re_rk <= 10).mean()
        
        # Classification separating A (positive talent) and B (top 10 contender)
        if p_pos >= 0.95 and r['P_top10'] >= 0.50:
            classification = "Elite Proven Clutch Anchor"
        elif p_pos >= 0.95 and r['P_top10'] >= 0.35:
            classification = "Proven Above-Average Contender"
        elif p_pos >= 0.90 and r['P_top10'] >= 0.35:
            classification = "Probable Positive Clutch Contender"
        elif p_pos >= 0.90:
            classification = "Probable Positive (Lower Top-10 Probability)"
        elif r_hp > 0:
            classification = "Promising but Statistically Indistinguishable from Zero"
        else:
            classification = "Below Replacement Level Under Pressure"

        records.append({
            'discipline': 'Batter',
            'rank': r['final_rank'],
            'player_id': pid,
            'player_name': r['player_name'],
            'role': r['role'],
            'R_HP': r_hp,
            'reliability_lambda': lam,
            'posterior_sd': sd_post,
            'posterior_CI_90_lo': post_lo,
            'posterior_CI_90_hi': post_hi,
            'P_positive_latent_ability': p_pos,
            'P_top10_fixed_boot': r['P_top10'],
            'P_top10_reestimated_boot': p_top10_re,
            'fixed_CI_width': width_fixed,
            'reestimated_CI_width': width_reest,
            'width_change_pct': ((width_reest - width_fixed) / max(width_fixed, 1e-4)) * 100,
            'fixed_rank_90_lo': r['rank_90_lo'],
            'fixed_rank_90_hi': r['rank_90_hi'],
            'reestimated_rank_90_lo': int(np.percentile(re_rk, 5)),
            'reestimated_rank_90_hi': int(np.percentile(re_rk, 95)),
            'n_hp': r['n_hp'],
            'm_hp': r['m_hp'],
            'n_total': r['n_total'],
            'IPL_share': (r['IPL_league'] + r['IPL_knockout']) / max(r['n_total'], 1),
            'classification': classification
        })

    # Process Bowlers
    for _, r in bowl_final.iterrows():
        pid = r['player_id']
        lam = r['reliability']
        r_hp = r['R_HP']
        
        sd_post = np.sqrt(max(1.0 - lam, 0.001)) * sigma_mu_bowl
        post_lo = r_hp - 1.645 * sd_post
        post_hi = r_hp + 1.645 * sd_post
        p_pos = stats.norm.cdf(r_hp / max(sd_post, 1e-4))
        
        re_arr = np.array(bowl_ratings_reest[pid])
        re_rk = np.array(bowl_ranks_reest[pid])
        ci_lo_re = np.percentile(re_arr, 5)
        ci_hi_re = np.percentile(re_arr, 95)
        width_fixed = r['CI_90_hi'] - r['CI_90_lo']
        width_reest = ci_hi_re - ci_lo_re
        p_top10_re = (re_rk <= 10).mean()
        
        if p_pos >= 0.95 and r['P_top10'] >= 0.50:
            classification = "Elite Proven Clutch Anchor"
        elif p_pos >= 0.95 and r['P_top10'] >= 0.35:
            classification = "Proven Above-Average Contender"
        elif p_pos >= 0.90 and r['P_top10'] >= 0.35:
            classification = "Probable Positive Clutch Contender"
        elif p_pos >= 0.90:
            classification = "Probable Positive (Lower Top-10 Probability)"
        elif r_hp > 0:
            classification = "Promising but Statistically Indistinguishable from Zero"
        else:
            classification = "Below Replacement Level Under Pressure"

        records.append({
            'discipline': 'Bowler',
            'rank': r['final_rank'],
            'player_id': pid,
            'player_name': r['player_name'],
            'role': r['role'],
            'R_HP': r_hp,
            'reliability_lambda': lam,
            'posterior_sd': sd_post,
            'posterior_CI_90_lo': post_lo,
            'posterior_CI_90_hi': post_hi,
            'P_positive_latent_ability': p_pos,
            'P_top10_fixed_boot': r['P_top10'],
            'P_top10_reestimated_boot': p_top10_re,
            'fixed_CI_width': width_fixed,
            'reestimated_CI_width': width_reest,
            'width_change_pct': ((width_reest - width_fixed) / max(width_fixed, 1e-4)) * 100,
            'fixed_rank_90_lo': r['rank_90_lo'],
            'fixed_rank_90_hi': r['rank_90_hi'],
            'reestimated_rank_90_lo': int(np.percentile(re_rk, 5)),
            'reestimated_rank_90_hi': int(np.percentile(re_rk, 95)),
            'n_hp': r['n_hp'],
            'm_hp': r['m_hp'],
            'n_total': r['n_total'],
            'IPL_share': (r['IPL_league'] + r['IPL_knockout']) / max(r['n_total'], 1),
            'classification': classification
        })

    df_out = pd.DataFrame(records)
    csv_path = out_dir / "TARGETED_AUDIT_PLAYER_PROBABILITIES.csv"
    df_out.to_csv(csv_path, index=False)
    print(f"   Saved {len(df_out)} player records to {csv_path}")

    # Print summary diagnostics
    print("\n5. Bootstrap Variance Component Stability:")
    print(f"   Batters sigma_e2: Full={sigma_e2_bat_full:.4f}, Boot Mean={np.mean(bat_sigma_e2_dist):.4f}, Boot SD={np.std(bat_sigma_e2_dist):.4f}")
    print(f"   Batters sigma_mu2: Full={sigma_mu2_bat_full:.4f}, Boot Mean={np.mean(bat_sigma_mu2_dist):.4f}, Boot SD={np.std(bat_sigma_mu2_dist):.4f}")
    print(f"   Bowlers sigma_e2: Full={sigma_e2_bowl_full:.4f}, Boot Mean={np.mean(bowl_sigma_e2_dist):.4f}, Boot SD={np.std(bowl_sigma_e2_dist):.4f}")
    print(f"   Bowlers sigma_mu2: Full={sigma_mu2_bowl_full:.4f}, Boot Mean={np.mean(bowl_sigma_mu2_dist):.4f}, Boot SD={np.std(bowl_sigma_mu2_dist):.4f}")

    print("\n=== TOP 10 BATTERS TARGETED AUDIT ===")
    print(df_out[df_out['discipline'] == 'Batter'].head(10)[['rank', 'player_name', 'R_HP', 'P_positive_latent_ability', 'P_top10_fixed_boot', 'P_top10_reestimated_boot', 'fixed_CI_width', 'reestimated_CI_width', 'classification']])

    print("\n=== TOP 10 BOWLERS TARGETED AUDIT ===")
    print(df_out[df_out['discipline'] == 'Bowler'].head(10)[['rank', 'player_name', 'R_HP', 'P_positive_latent_ability', 'P_top10_fixed_boot', 'P_top10_reestimated_boot', 'fixed_CI_width', 'reestimated_CI_width', 'classification']])

if __name__ == '__main__':
    run_targeted_verification()

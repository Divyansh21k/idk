"""
Independent Verification Pipeline for Match-Cluster Bootstrap and Empirical Bayes Posterior.

Audit Targets:
1. Independently verify the mathematics of the Double Sampling Noise Theorem and Procedure B bias.
2. Compare i.i.d. Empirical Bayes posterior vs Clustered Empirical Bayes posterior on synthetic data with known talent.
3. Run 100 synthetic datasets under a realistic cricket Data Generating Process (skewed delivery values, variable balls/match, discrete outcomes).
4. Run full-field ranking (all eligible players, not truncated to top 25) on real 802-match IPL/T20I data for Procedures A, B, and C.
5. Export results to superr_selector/outputs/BOOTSTRAP_VERIFICATION_RESULTS.csv.
"""

import sys, os, time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

def run_verification():
    print("=== SupeRR Selector: Independent Bootstrap & Posterior Verification ===")
    np.random.seed(12345)

    base_dir = Path("superr_selector")
    out_dir = base_dir / "outputs"
    step1_dir = out_dir / "step1"
    step2_dir = out_dir / "step2"
    step3_dir = out_dir / "step3"

    # -------------------------------------------------------------
    # 1. REALISTIC CRICKET SYNTHETIC DGP (100 independent datasets)
    # -------------------------------------------------------------
    print("\n1. Running 100 Realistic Cricket Synthetic Datasets...")
    # Cricket DGP parameters:
    # Match random effect: sigma_match = 0.2831 runs/ball (variance = 0.0801)
    # Player latent ability: sigma_mu = 0.1868 runs/ball (variance = 0.0349)
    # Delivery residual noise: sigma_e = 2.8835 runs/ball (variance = 8.3145)
    
    sigma_mu_true = 0.1868
    sigma_match_true = 0.2831
    sigma_e_true = 2.8835
    
    n_players = 80
    n_matches = 150
    n_sim_datasets = 100
    n_boot_inner = 80
    
    records_synth = []
    
    for sim_id in range(n_sim_datasets):
        # Latent talent (normal)
        alpha = np.random.normal(0, sigma_mu_true, size=n_players)
        # Match effects (normal)
        gamma = np.random.normal(0, sigma_match_true, size=n_matches)
        
        # Exposure tiers:
        # Low: 3-6 matches; Med: 8-15 matches; High: 18-32 matches
        # Balls per match: skewed (Poisson/Gamma-like, min 3, max 35)
        sim_data = []
        player_meta = {}
        for p in range(n_players):
            if p < 25:
                n_m = np.random.randint(3, 7)
                grp = 'Low (50-100 balls)'
            elif p < 55:
                n_m = np.random.randint(8, 16)
                grp = 'Medium (100-250 balls)'
            else:
                n_m = np.random.randint(18, 33)
                grp = 'High (250+ balls)'
                
            p_matches = np.random.choice(n_matches, size=n_m, replace=False)
            tot_b = 0
            for m in p_matches:
                # Skewed balls per match
                b_m = int(np.clip(np.random.negative_binomial(5, 0.3), 4, 35))
                tot_b += b_m
                
                # Cricket delivery values: mixture of dots (negative), singles (around 0), boundaries (positive), wickets
                # We simulate delivery residual with mean 0 and variance sigma_e^2 = 8.3145
                # Using a 4-component mixture matching T20 high-pressure empirical distribution:
                # 45% dots (-0.4), 35% singles (+0.1), 15% boundaries (+2.5), 5% wickets (-2.0) + jitter
                u = np.random.uniform(0, 1, size=b_m)
                resid = np.where(u < 0.45, -0.65 + np.random.normal(0, 0.3, b_m),
                        np.where(u < 0.80, 0.15 + np.random.normal(0, 0.4, b_m),
                        np.where(u < 0.95, 2.60 + np.random.normal(0, 0.6, b_m),
                                           -2.40 + np.random.normal(0, 0.8, b_m))))
                # Center and scale residuals to exact sigma_e_true
                resid = (resid - resid.mean()) / (resid.std() + 1e-6) * sigma_e_true
                
                v_del = alpha[p] + gamma[m] + resid
                for v in v_del:
                    sim_data.append({'player': p, 'match': m, 'v': v})
                    
            player_meta[p] = {'exposure_grp': grp, 'n_balls': tot_b, 'n_matches': n_m, 'true_talent': alpha[p] * 100}
            
        df_sim = pd.DataFrame(sim_data)
        
        # Talent tiers
        for p in range(n_players):
            if alpha[p] > 1.28 * sigma_mu_true:
                t_grp = 'Top 10% Talent'
            elif alpha[p] < -1.28 * sigma_mu_true:
                t_grp = 'Bottom 10% Talent'
            else:
                t_grp = 'Middle 80% Talent'
            player_meta[p]['talent_grp'] = t_grp
            
        # Full-sample variance estimates
        sigma_e2_full = np.var(df_sim['v'], ddof=1)
        p_stats_full = df_sim.groupby('player').agg(n=('v', 'count'), mean_v=('v', 'mean')).reset_index()
        mean_inv_n_full = np.mean(1.0 / p_stats_full['n'])
        
        # Two-way corrected full-sample sigma_mu2
        m_means = df_sim.groupby('match')['v'].transform('mean')
        v_adj = df_sim['v'] - m_means
        p_stats_adj = df_sim.assign(v_adj=v_adj).groupby('player').agg(n=('v_adj', 'count'), mean_adj=('v_adj', 'mean')).reset_index()
        sigma_mu2_full = max(np.var(p_stats_adj['mean_adj'], ddof=1) - np.var(v_adj, ddof=1) * mean_inv_n_full, 0.005)
        
        # Match lookup
        sim_match_dict = {m: {'p': g['player'].values, 'v': g['v'].values} for m, g in df_sim.groupby('match')}
        sim_matches = np.unique(df_sim['match'])
        
        # Run inner bootstrap
        boot_scores_A = {p: [] for p in range(n_players)}
        boot_scores_B = {p: [] for p in range(n_players)}
        boot_scores_C = {p: [] for p in range(n_players)}
        
        for b in range(n_boot_inner):
            sampled_m = np.random.choice(sim_matches, size=len(sim_matches), replace=True)
            
            p_counts = {}
            p_sums = {}
            all_v_b = []
            m_v_map = {}
            
            for m in sampled_m:
                rec = sim_match_dict[m]
                all_v_b.extend(rec['v'])
                m_v_map.setdefault(m, []).extend(rec['v'])
                for p, v in zip(rec['p'], rec['v']):
                    p_counts[p] = p_counts.get(p, 0) + 1
                    p_sums[p] = p_sums.get(p, 0.0) + v
                    
            sigma_e2_b = np.var(all_v_b, ddof=1)
            means_b = [p_sums[p] / p_counts[p] for p in p_counts]
            inv_n_b = [1.0 / p_counts[p] for p in p_counts]
            
            # Procedure B Naive sigma_mu2
            sigma_mu2_B = max(np.var(means_b, ddof=1) - sigma_e2_b * np.mean(inv_n_b), 0.005)
            
            # Procedure C Corrected Two-Way sigma_mu2
            m_means_b = {m: np.mean(vs) for m, vs in m_v_map.items()}
            p_adj_sums = {}
            for m in sampled_m:
                rec = sim_match_dict[m]
                m_bar = m_means_b[m]
                for p, v in zip(rec['p'], rec['v']):
                    p_adj_sums[p] = p_adj_sums.get(p, 0.0) + (v - m_bar)
            adj_means_b = [p_adj_sums[p] / p_counts[p] for p in p_counts]
            sigma_mu2_C = max(np.var(adj_means_b, ddof=1) - sigma_e2_b * np.mean(inv_n_b), 0.005)
            
            for p in range(n_players):
                n_b = p_counts.get(p, 0)
                y_b = p_sums.get(p, 0.0) / max(n_b, 1) if n_b > 0 else 0.0
                
                # A: Fixed
                lam_A = (n_b * sigma_mu2_full) / (n_b * sigma_mu2_full + sigma_e2_full) if n_b > 0 else 0
                boot_scores_A[p].append(lam_A * y_b * 100)
                
                # B: Naive Re-estimated
                lam_B = (n_b * sigma_mu2_B) / (n_b * sigma_mu2_B + sigma_e2_b) if n_b > 0 else 0
                boot_scores_B[p].append(lam_B * y_b * 100)
                
                # C: Corrected Two-Way
                lam_C = (n_b * sigma_mu2_C) / (n_b * sigma_mu2_C + sigma_e2_b) if n_b > 0 else 0
                boot_scores_C[p].append(lam_C * y_b * 100)
                
        # Evaluate for all players in dataset sim_id
        for p in range(n_players):
            meta = player_meta[p]
            theta_true = meta['true_talent']
            
            # Full-sample analytical EB posterior
            p_row = p_stats_full[p_stats_full['player'] == p].iloc[0]
            n_p = p_row['n']
            y_bar_p = p_row['mean_v']
            m_p = meta['n_matches']
            
            # 1. Standard i.i.d. Empirical Bayes posterior
            lam_iid = (n_p * sigma_mu2_full) / (n_p * sigma_mu2_full + sigma_e2_full)
            r_hp_iid = lam_iid * y_bar_p * 100
            sd_post_iid = np.sqrt(max(1.0 - lam_iid, 0.001)) * np.sqrt(sigma_mu2_full) * 100
            cov_post_iid = (r_hp_iid - 1.645 * sd_post_iid <= theta_true <= r_hp_iid + 1.645 * sd_post_iid)
            width_post_iid = 2 * 1.645 * sd_post_iid
            
            # 2. Clustered Empirical Bayes posterior (accounting for match variance sigma_match^2/M_i)
            # V_p = sigma_match^2 / M_p + sigma_e^2 / n_p
            v_p_cluster = (sigma_match_true**2) / max(m_p, 1) + sigma_e2_full / max(n_p, 1)
            lam_cluster = sigma_mu2_full / (sigma_mu2_full + v_p_cluster)
            r_hp_cluster = lam_cluster * y_bar_p * 100
            sd_post_cluster = np.sqrt(max(1.0 - lam_cluster, 0.001)) * np.sqrt(sigma_mu2_full) * 100
            cov_post_cluster = (r_hp_cluster - 1.645 * sd_post_cluster <= theta_true <= r_hp_cluster + 1.645 * sd_post_cluster)
            width_post_cluster = 2 * 1.645 * sd_post_cluster
            
            # Bootstrap intervals
            cov_A = (np.percentile(boot_scores_A[p], 5) <= theta_true <= np.percentile(boot_scores_A[p], 95))
            width_A = np.percentile(boot_scores_A[p], 95) - np.percentile(boot_scores_A[p], 5)
            
            cov_B = (np.percentile(boot_scores_B[p], 5) <= theta_true <= np.percentile(boot_scores_B[p], 95))
            width_B = np.percentile(boot_scores_B[p], 95) - np.percentile(boot_scores_B[p], 5)
            
            cov_C = (np.percentile(boot_scores_C[p], 5) <= theta_true <= np.percentile(boot_scores_C[p], 95))
            width_C = np.percentile(boot_scores_C[p], 95) - np.percentile(boot_scores_C[p], 5)
            
            records_synth.append({
                'sim_id': sim_id,
                'player_id': p,
                'exposure_group': meta['exposure_grp'],
                'talent_group': meta['talent_grp'],
                'n_balls': n_p,
                'n_matches': m_p,
                'true_talent': theta_true,
                'cov_A': cov_A, 'width_A': width_A,
                'cov_B': cov_B, 'width_B': width_B,
                'cov_C': cov_C, 'width_C': width_C,
                'cov_post_iid': cov_post_iid, 'width_post_iid': width_post_iid,
                'cov_post_cluster': cov_post_cluster, 'width_post_cluster': width_post_cluster,
            })
            
        if (sim_id + 1) % 25 == 0:
            print(f"   Completed {sim_id + 1}/{n_sim_datasets} synthetic datasets...")
            
    df_res_synth = pd.DataFrame(records_synth)

    # -------------------------------------------------------------
    # 2. FULL-FIELD REAL DATA BOOTSTRAP (ALL ELIGIBLE PLAYERS)
    # -------------------------------------------------------------
    print("\n2. Running Full-Field Real Data Bootstrap on 802 matches (All Eligible Players)...")
    ev = pd.read_csv(step2_dir / "deliveries_with_ev.csv.gz", low_memory=False)
    press = pd.read_csv(step3_dir / "all_deliveries_pressure.csv.gz", low_memory=False)
    bexp = pd.read_csv(step1_dir / "player_exposure_batters.csv")
    wexp = pd.read_csv(step1_dir / "player_exposure_bowlers.csv")
    bat_final = pd.read_csv(out_dir / "FINAL_REPAIRED_BATTER_RANKINGS.csv")
    bowl_final = pd.read_csv(out_dir / "FINAL_REPAIRED_BOWLER_RANKINGS.csv")

    df = press[[
        'match_id', 'innings', 'innings_ball_num', 'striker_id', 'bowler_id',
        'cat', 'season', 'PI_final', 'elig_batting', 'elig_bowling'
    ]].merge(
        ev[['match_id', 'innings', 'innings_ball_num', 'v_bat', 'v_bowl']],
        on=['match_id', 'innings', 'innings_ball_num'],
        how='inner'
    )
    df['is_hp'] = df['PI_final'] >= 0.800

    matches_df = df[['match_id', 'cat']].drop_duplicates()
    cats = matches_df['cat'].unique()
    match_cats = {c: matches_df[matches_df['cat'] == c]['match_id'].values for c in cats}

    # All eligible players
    hp_bat = df[(df['elig_batting'] == 1) & (df['is_hp'])].copy()
    hp_bat = hp_bat.merge(bexp[['player_id', 'batting_role']], left_on='striker_id', right_on='player_id', how='left')
    all_bat_ids = set(bat_final['player_id'])

    hp_bowl = df[(df['elig_bowling'] == 1) & (df['is_hp'])].copy()
    hp_bowl = hp_bowl.merge(wexp[['player_id', 'pace_or_spin']], left_on='bowler_id', right_on='player_id', how='left')
    all_bowl_ids = set(bowl_final['player_id'])

    bat_match_records = {}
    for m, g in hp_bat.groupby('match_id'):
        bat_match_records[m] = {
            'strikers': g['striker_id'].values,
            'roles': g['batting_role'].values,
            'v': g['v_bat'].values
        }

    bowl_match_records = {}
    for m, g in hp_bowl.groupby('match_id'):
        bowl_match_records[m] = {
            'bowlers': g['bowler_id'].values,
            'roles': g['pace_or_spin'].values,
            'v': g['v_bowl'].values
        }

    # Fixed parameters from full sample
    sigma_e2_bat_full = hp_bat['v_bat'].var()
    sigma_mu2_bat_full = 0.0349
    role_means_bat_full = hp_bat.groupby('batting_role')['v_bat'].mean().to_dict()

    sigma_e2_bowl_full = hp_bowl['v_bowl'].var()
    sigma_mu2_bowl_full = 0.0223
    role_means_bowl_full = hp_bowl.groupby('pace_or_spin')['v_bowl'].mean().to_dict()

    n_real_boots = 300
    bat_res_A = {pid: [] for pid in all_bat_ids}
    bat_res_B = {pid: [] for pid in all_bat_ids}
    bat_res_C = {pid: [] for pid in all_bat_ids}
    bat_rk_A = {pid: [] for pid in all_bat_ids}
    bat_rk_B = {pid: [] for pid in all_bat_ids}
    bat_rk_C = {pid: [] for pid in all_bat_ids}

    bowl_res_A = {pid: [] for pid in all_bowl_ids}
    bowl_res_B = {pid: [] for pid in all_bowl_ids}
    bowl_res_C = {pid: [] for pid in all_bowl_ids}
    bowl_rk_A = {pid: [] for pid in all_bowl_ids}
    bowl_rk_B = {pid: [] for pid in all_bowl_ids}
    bowl_rk_C = {pid: [] for pid in all_bowl_ids}

    for b in range(n_real_boots):
        sampled_matches = []
        for c in cats:
            m_list = match_cats[c]
            sampled_matches.extend(np.random.choice(m_list, size=len(m_list), replace=True))

        # Batters
        all_v_bat = []
        p_counts_bat = {}
        p_sums_bat = {}
        m_v_map_bat = {}
        for m in sampled_matches:
            if m in bat_match_records:
                rec = bat_match_records[m]
                all_v_bat.extend(rec['v'])
                m_v_map_bat.setdefault(m, []).extend(rec['v'])
                for p, v in zip(rec['strikers'], rec['v']):
                    p_counts_bat[p] = p_counts_bat.get(p, 0) + 1
                    p_sums_bat[p] = p_sums_bat.get(p, 0.0) + v

        sigma_e2_bat_b = np.var(all_v_bat, ddof=1)
        means_20 = [p_sums_bat[p]/p_counts_bat[p] for p in p_counts_bat if p_counts_bat[p] >= 20]
        inv_20 = [1.0/p_counts_bat[p] for p in p_counts_bat if p_counts_bat[p] >= 20]
        sigma_mu2_bat_B = max(np.var(means_20, ddof=1) - sigma_e2_bat_b * np.mean(inv_20), 0.005)

        m_means_bat = {m: np.mean(vs) for m, vs in m_v_map_bat.items()}
        p_adj_sums_bat = {}
        for m in sampled_matches:
            if m in bat_match_records:
                rec = bat_match_records[m]
                m_bar = m_means_bat[m]
                for p, v in zip(rec['strikers'], rec['v']):
                    p_adj_sums_bat[p] = p_adj_sums_bat.get(p, 0.0) + (v - m_bar)
        adj_means_20 = [p_adj_sums_bat[p]/p_counts_bat[p] for p in p_counts_bat if p_counts_bat[p] >= 20]
        sigma_mu2_bat_C = max(np.var(adj_means_20, ddof=1) - sigma_e2_bat_b * np.mean(inv_20), 0.005)

        scores_A, scores_B, scores_C = {}, {}, {}
        for pid in all_bat_ids:
            n_b = p_counts_bat.get(pid, 0)
            y_b = p_sums_bat.get(pid, 0.0) / max(n_b, 1) if n_b > 0 else 0.0
            r_prior = role_means_bat_full.get(bat_final.loc[bat_final['player_id']==pid, 'role'].values[0], 0.0)

            lam_A = (n_b * sigma_mu2_bat_full) / (n_b * sigma_mu2_bat_full + sigma_e2_bat_full) if n_b > 0 else 0
            sc_A = (lam_A * y_b + (1 - lam_A) * r_prior) * 100
            bat_res_A[pid].append(sc_A)
            scores_A[pid] = sc_A

            lam_B = (n_b * sigma_mu2_bat_B) / (n_b * sigma_mu2_bat_B + sigma_e2_bat_b) if n_b > 0 else 0
            sc_B = (lam_B * y_b + (1 - lam_B) * r_prior) * 100
            bat_res_B[pid].append(sc_B)
            scores_B[pid] = sc_B

            lam_C = (n_b * sigma_mu2_bat_C) / (n_b * sigma_mu2_bat_C + sigma_e2_bat_b) if n_b > 0 else 0
            sc_C = (lam_C * y_b + (1 - lam_C) * r_prior) * 100
            bat_res_C[pid].append(sc_C)
            scores_C[pid] = sc_C

        # Full field rank across ALL eligible batters
        for rk, (pid, _) in enumerate(sorted(scores_A.items(), key=lambda x: x[1], reverse=True), 1):
            bat_rk_A[pid].append(rk)
        for rk, (pid, _) in enumerate(sorted(scores_B.items(), key=lambda x: x[1], reverse=True), 1):
            bat_rk_B[pid].append(rk)
        for rk, (pid, _) in enumerate(sorted(scores_C.items(), key=lambda x: x[1], reverse=True), 1):
            bat_rk_C[pid].append(rk)

        # Bowlers
        all_v_bowl = []
        p_counts_bowl = {}
        p_sums_bowl = {}
        m_v_map_bowl = {}
        for m in sampled_matches:
            if m in bowl_match_records:
                rec = bowl_match_records[m]
                all_v_bowl.extend(rec['v'])
                m_v_map_bowl.setdefault(m, []).extend(rec['v'])
                for p, v in zip(rec['bowlers'], rec['v']):
                    p_counts_bowl[p] = p_counts_bowl.get(p, 0) + 1
                    p_sums_bowl[p] = p_sums_bowl.get(p, 0.0) + v

        sigma_e2_bowl_b = np.var(all_v_bowl, ddof=1)
        means_20_bowl = [p_sums_bowl[p]/p_counts_bowl[p] for p in p_counts_bowl if p_counts_bowl[p] >= 20]
        inv_20_bowl = [1.0/p_counts_bowl[p] for p in p_counts_bowl if p_counts_bowl[p] >= 20]
        sigma_mu2_bowl_B = max(np.var(means_20_bowl, ddof=1) - sigma_e2_bowl_b * np.mean(inv_20_bowl), 0.005)

        m_means_bowl = {m: np.mean(vs) for m, vs in m_v_map_bowl.items()}
        p_adj_sums_bowl = {}
        for m in sampled_matches:
            if m in bowl_match_records:
                rec = bowl_match_records[m]
                m_bar = m_means_bowl[m]
                for p, v in zip(rec['bowlers'], rec['v']):
                    p_adj_sums_bowl[p] = p_adj_sums_bowl.get(p, 0.0) + (v - m_bar)
        adj_means_20_bowl = [p_adj_sums_bowl[p]/p_counts_bowl[p] for p in p_counts_bowl if p_counts_bowl[p] >= 20]
        sigma_mu2_bowl_C = max(np.var(adj_means_20_bowl, ddof=1) - sigma_e2_bowl_b * np.mean(inv_20_bowl), 0.005)

        scores_A_bw, scores_B_bw, scores_C_bw = {}, {}, {}
        for pid in all_bowl_ids:
            n_b = p_counts_bowl.get(pid, 0)
            y_b = p_sums_bowl.get(pid, 0.0) / max(n_b, 1) if n_b > 0 else 0.0
            r_prior = role_means_bowl_full.get(bowl_final.loc[bowl_final['player_id']==pid, 'role'].values[0], 0.0)

            lam_A = (n_b * sigma_mu2_bowl_full) / (n_b * sigma_mu2_bowl_full + sigma_e2_bowl_full) if n_b > 0 else 0
            sc_A = (lam_A * y_b + (1 - lam_A) * r_prior) * 100
            bowl_res_A[pid].append(sc_A)
            scores_A_bw[pid] = sc_A

            lam_B = (n_b * sigma_mu2_bowl_B) / (n_b * sigma_mu2_bowl_B + sigma_e2_bowl_b) if n_b > 0 else 0
            sc_B = (lam_B * y_b + (1 - lam_B) * r_prior) * 100
            bowl_res_B[pid].append(sc_B)
            scores_B_bw[pid] = sc_B

            lam_C = (n_b * sigma_mu2_bowl_C) / (n_b * sigma_mu2_bowl_C + sigma_e2_bowl_b) if n_b > 0 else 0
            sc_C = (lam_C * y_b + (1 - lam_C) * r_prior) * 100
            bowl_res_C[pid].append(sc_C)
            scores_C_bw[pid] = sc_C

        # Full field rank across ALL eligible bowlers
        for rk, (pid, _) in enumerate(sorted(scores_A_bw.items(), key=lambda x: x[1], reverse=True), 1):
            bowl_rk_A[pid].append(rk)
        for rk, (pid, _) in enumerate(sorted(scores_B_bw.items(), key=lambda x: x[1], reverse=True), 1):
            bowl_rk_B[pid].append(rk)
        for rk, (pid, _) in enumerate(sorted(scores_C_bw.items(), key=lambda x: x[1], reverse=True), 1):
            bowl_rk_C[pid].append(rk)

    # Compile Verification Results table
    final_records = []
    # Add Batters Top 20
    for _, r in bat_final.head(20).iterrows():
        pid = r['player_id']
        final_records.append({
            'discipline': 'Batter',
            'rank': r['final_rank'],
            'player_name': r['player_name'],
            'n_hp': r['n_hp'],
            'R_HP': r['R_HP'],
            'A_CI_width': np.percentile(bat_res_A[pid], 95) - np.percentile(bat_res_A[pid], 5),
            'B_CI_width': np.percentile(bat_res_B[pid], 95) - np.percentile(bat_res_B[pid], 5),
            'C_CI_width': np.percentile(bat_res_C[pid], 95) - np.percentile(bat_res_C[pid], 5),
            'A_P_top10': np.mean(np.array(bat_rk_A[pid]) <= 10),
            'B_P_top10': np.mean(np.array(bat_rk_B[pid]) <= 10),
            'C_P_top10': np.mean(np.array(bat_rk_C[pid]) <= 10),
            'A_rank_90_lo': int(np.percentile(bat_rk_A[pid], 5)),
            'A_rank_90_hi': int(np.percentile(bat_rk_A[pid], 95)),
            'B_rank_90_lo': int(np.percentile(bat_rk_B[pid], 5)),
            'B_rank_90_hi': int(np.percentile(bat_rk_B[pid], 95)),
            'C_rank_90_lo': int(np.percentile(bat_rk_C[pid], 5)),
            'C_rank_90_hi': int(np.percentile(bat_rk_C[pid], 95)),
        })
    # Add Bowlers Top 20
    for _, r in bowl_final.head(20).iterrows():
        pid = r['player_id']
        final_records.append({
            'discipline': 'Bowler',
            'rank': r['final_rank'],
            'player_name': r['player_name'],
            'n_hp': r['n_hp'],
            'R_HP': r['R_HP'],
            'A_CI_width': np.percentile(bowl_res_A[pid], 95) - np.percentile(bowl_res_A[pid], 5),
            'B_CI_width': np.percentile(bowl_res_B[pid], 95) - np.percentile(bowl_res_B[pid], 5),
            'C_CI_width': np.percentile(bowl_res_C[pid], 95) - np.percentile(bowl_res_C[pid], 5),
            'A_P_top10': np.mean(np.array(bowl_rk_A[pid]) <= 10),
            'B_P_top10': np.mean(np.array(bowl_rk_B[pid]) <= 10),
            'C_P_top10': np.mean(np.array(bowl_rk_C[pid]) <= 10),
            'A_rank_90_lo': int(np.percentile(bowl_rk_A[pid], 5)),
            'A_rank_90_hi': int(np.percentile(bowl_rk_A[pid], 95)),
            'B_rank_90_lo': int(np.percentile(bowl_rk_B[pid], 5)),
            'B_rank_90_hi': int(np.percentile(bowl_rk_B[pid], 95)),
            'C_rank_90_lo': int(np.percentile(bowl_rk_C[pid], 5)),
            'C_rank_90_hi': int(np.percentile(bowl_rk_C[pid], 95)),
        })

    df_results = pd.DataFrame(final_records)
    csv_out = out_dir / "BOOTSTRAP_VERIFICATION_RESULTS.csv"
    df_results.to_csv(csv_out, index=False)
    print(f"\n   Saved verification results to {csv_out}")

    # Print Synthetic Summary
    print("\n=== SYNTHETIC VERIFICATION SUMMARY BY EXPOSURE ===")
    print(df_res_synth.groupby('exposure_group')[[
        'cov_A', 'cov_B', 'cov_C', 'cov_post_iid', 'cov_post_cluster',
        'width_A', 'width_B', 'width_C', 'width_post_iid', 'width_post_cluster'
    ]].mean().to_string())

    print("\n=== SYNTHETIC VERIFICATION SUMMARY BY TALENT TIER ===")
    print(df_res_synth.groupby('talent_group')[[
        'cov_A', 'cov_B', 'cov_C', 'cov_post_iid', 'cov_post_cluster',
        'width_A', 'width_B', 'width_C', 'width_post_iid', 'width_post_cluster'
    ]].mean().to_string())

    print("\n=== FULL FIELD REAL DATA SUMMARY (TOP 5 BATTERS) ===")
    print(df_results[df_results['discipline']=='Batter'].head(5)[[
        'rank', 'player_name', 'n_hp', 'A_CI_width', 'B_CI_width', 'A_P_top10', 'B_P_top10', 'A_rank_90_lo', 'A_rank_90_hi', 'B_rank_90_lo', 'B_rank_90_hi'
    ]].to_string())

    print("\n=== FULL FIELD REAL DATA SUMMARY (TOP 5 BOWLERS) ===")
    print(df_results[df_results['discipline']=='Bowler'].head(5)[[
        'rank', 'player_name', 'n_hp', 'A_CI_width', 'B_CI_width', 'A_P_top10', 'B_P_top10', 'A_rank_90_lo', 'A_rank_90_hi', 'B_rank_90_lo', 'B_rank_90_hi'
    ]].to_string())

if __name__ == '__main__':
    run_verification()

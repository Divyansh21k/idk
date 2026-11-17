"""
Critical Bootstrap Investigation Pipeline:
1. Diagnose the 5.5x and 8.0x variance inflation root cause.
2. Implement Procedure A (Fixed), Procedure B (Naive Re-estimation), and Procedure C (Corrected Two-Way Re-estimation).
3. Run synthetic validation across 100 independent datasets with known parameters.
4. Run real-data sensitivity on all 802 matches.
5. Export:
   - BOOTSTRAP_SYNTHETIC_VALIDATION.csv
   - BOOTSTRAP_REAL_DATA_SENSITIVITY.csv
"""
import sys, os, time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

def run_investigation():
    print("=== SupeRR Selector: Critical Bootstrap Investigation ===")
    np.random.seed(42)

    base_dir = Path("superr_selector")
    out_dir = base_dir / "outputs"
    step1_dir = out_dir / "step1"
    step2_dir = out_dir / "step2"
    step3_dir = out_dir / "step3"

    print("\n1. Running Synthetic Validation across 100 independent datasets...")
    # Parameters for realistic cricket-like synthetic data:
    # 100 players, 200 matches, 2 competition classes (IPL: 80 matches, T20I: 120 matches)
    # True latent talent sigma_mu = 0.1868 (runs/ball)
    # Match random effect sigma_match = 0.2831 (runs/ball)
    # Delivery residual sigma_e = 2.8835 (runs/ball)
    
    sigma_mu_true = 0.1868
    sigma_match_true = 0.2831
    sigma_e_true = 2.8835
    
    n_players_sim = 80
    n_matches_sim = 150
    n_sim_datasets = 100
    n_boot_inner = 100 # inner bootstrap resamples per dataset
    
    synth_records = []
    
    for sim_id in range(n_sim_datasets):
        # 1. Generate ground truth
        mu_true = np.random.normal(0, sigma_mu_true, size=n_players_sim)
        gamma_match = np.random.normal(0, sigma_match_true, size=n_matches_sim)
        
        # Exposure volumes: unequal matches per player
        # Low exposure (3-6 matches), Med exposure (7-15 matches), High exposure (16-30 matches)
        player_exposures = []
        rows = []
        for p in range(n_players_sim):
            if p < 25:
                n_m = np.random.randint(3, 7) # Low
                exp_grp = 'Low (50-100 balls)'
            elif p < 55:
                n_m = np.random.randint(8, 16) # Med
                exp_grp = 'Medium (100-250 balls)'
            else:
                n_m = np.random.randint(18, 31) # High
                exp_grp = 'High (250+ balls)'
                
            p_matches = np.random.choice(n_matches_sim, size=n_m, replace=False)
            total_b = 0
            for m in p_matches:
                b_count = np.random.randint(8, 15)
                total_b += b_count
                v = mu_true[p] + gamma_match[m] + np.random.normal(0, sigma_e_true, size=b_count)
                for val in v:
                    rows.append({'player': p, 'match': m, 'v': val})
                    
            player_exposures.append((p, total_b, len(p_matches), exp_grp))
            
        df_sim = pd.DataFrame(rows)
        
        # Talent groups
        talent_grps = []
        for p in range(n_players_sim):
            if mu_true[p] > 1.28 * sigma_mu_true:
                t_grp = 'Top 10% Talent'
            elif mu_true[p] < -1.28 * sigma_mu_true:
                t_grp = 'Bottom 10% Talent'
            else:
                t_grp = 'Middle 80% Talent'
            talent_grps.append(t_grp)
            
        # Full-sample estimates on df_sim
        sigma_e2_full = np.var(df_sim['v'], ddof=1)
        p_stats_full = df_sim.groupby('player').agg(n=('v', 'count'), mean_v=('v', 'mean')).reset_index()
        var_means_full = np.var(p_stats_full['mean_v'], ddof=1)
        mean_inv_n_full = np.mean(1.0 / p_stats_full['n'])
        # Two-way crossed ANOVA for full sample sigma_mu2
        m_means = df_sim.groupby('match')['v'].transform('mean')
        v_adj = df_sim['v'] - m_means
        p_stats_adj = df_sim.assign(v_adj=v_adj).groupby('player').agg(n=('v_adj', 'count'), mean_adj=('v_adj', 'mean')).reset_index()
        sigma_mu2_full_corrected = max(np.var(p_stats_adj['mean_adj'], ddof=1) - np.var(v_adj, ddof=1) * np.mean(1.0 / p_stats_adj['n']), 0.005)
        sigma_mu2_full_naive = max(var_means_full - sigma_e2_full * mean_inv_n_full, 0.005)
        
        # Pre-group matches
        sim_match_records = {m: {'p': g['player'].values, 'v': g['v'].values} for m, g in df_sim.groupby('match')}
        sim_matches = np.unique(df_sim['match'])
        
        # Run 3 procedures for 100 inner bootstrap resamples
        boot_scores_A = {p: [] for p in range(n_players_sim)}
        boot_scores_B = {p: [] for p in range(n_players_sim)}
        boot_scores_C = {p: [] for p in range(n_players_sim)}
        
        for b in range(n_boot_inner):
            sampled_m = np.random.choice(sim_matches, size=len(sim_matches), replace=True)
            
            p_counts = {}
            p_sums = {}
            all_v_b = []
            m_v_map = {}
            
            for m in sampled_m:
                rec = sim_match_records[m]
                all_v_b.extend(rec['v'])
                m_v_map.setdefault(m, []).extend(rec['v'])
                for p, v in zip(rec['p'], rec['v']):
                    p_counts[p] = p_counts.get(p, 0) + 1
                    p_sums[p] = p_sums.get(p, 0.0) + v
                    
            sigma_e2_b = np.var(all_v_b, ddof=1)
            
            # Procedure B Naive sigma_mu2
            means_b = [p_sums[p] / p_counts[p] for p in p_counts]
            inv_n_b = [1.0 / p_counts[p] for p in p_counts]
            sigma_mu2_b_naive = max(np.var(means_b, ddof=1) - sigma_e2_b * np.mean(inv_n_b), 0.005)
            
            # Procedure C Corrected Two-Way sigma_mu2
            # Subtract match means
            m_means_b = {m: np.mean(vs) for m, vs in m_v_map.items()}
            p_adj_sums = {}
            for m in sampled_m:
                rec = sim_match_records[m]
                m_bar = m_means_b[m]
                for p, v in zip(rec['p'], rec['v']):
                    p_adj_sums[p] = p_adj_sums.get(p, 0.0) + (v - m_bar)
            adj_means_b = [p_adj_sums[p] / p_counts[p] for p in p_counts]
            var_adj_b = np.var(adj_means_b, ddof=1)
            sigma_mu2_b_corrected = max(var_adj_b - sigma_e2_b * np.mean(inv_n_b), 0.005)
            
            for p in range(n_players_sim):
                n_b = p_counts.get(p, 0)
                y_b = p_sums.get(p, 0.0) / max(n_b, 1) if n_b > 0 else 0.0
                
                # A: Fixed
                lam_A = (n_b * sigma_mu2_full_corrected) / (n_b * sigma_mu2_full_corrected + sigma_e2_full) if n_b > 0 else 0
                r_A = (lam_A * y_b) * 100
                boot_scores_A[p].append(r_A)
                
                # B: Naive Re-estimated
                lam_B = (n_b * sigma_mu2_b_naive) / (n_b * sigma_mu2_b_naive + sigma_e2_b) if n_b > 0 else 0
                r_B = (lam_B * y_b) * 100
                boot_scores_B[p].append(r_B)
                
                # C: Corrected Re-estimated
                lam_C = (n_b * sigma_mu2_b_corrected) / (n_b * sigma_mu2_b_corrected + sigma_e2_b) if n_b > 0 else 0
                r_C = (lam_C * y_b) * 100
                boot_scores_C[p].append(r_C)
                
        # Evaluate coverage and metrics across players in dataset sim_id
        for p in range(n_players_sim):
            target_mu = mu_true[p] * 100 # runs/100b
            exp_grp = player_exposures[p][3]
            t_grp = talent_grps[p]
            
            # Proc A
            ci_A_lo = np.percentile(boot_scores_A[p], 5)
            ci_A_hi = np.percentile(boot_scores_A[p], 95)
            cov_A = (ci_A_lo <= target_mu <= ci_A_hi)
            width_A = ci_A_hi - ci_A_lo
            
            # Proc B
            ci_B_lo = np.percentile(boot_scores_B[p], 5)
            ci_B_hi = np.percentile(boot_scores_B[p], 95)
            cov_B = (ci_B_lo <= target_mu <= ci_B_hi)
            width_B = ci_B_hi - ci_B_lo
            
            # Proc C
            ci_C_lo = np.percentile(boot_scores_C[p], 5)
            ci_C_hi = np.percentile(boot_scores_C[p], 95)
            cov_C = (ci_C_lo <= target_mu <= ci_C_hi)
            width_C = ci_C_hi - ci_C_lo
            
            synth_records.append({
                'sim_id': sim_id,
                'player_id': p,
                'exposure_group': exp_grp,
                'talent_group': t_grp,
                'true_talent': target_mu,
                'cov_A': cov_A, 'width_A': width_A,
                'cov_B': cov_B, 'width_B': width_B,
                'cov_C': cov_C, 'width_C': width_C,
            })
            
        if (sim_id + 1) % 25 == 0:
            print(f"   Completed {sim_id + 1}/{n_sim_datasets} synthetic datasets...")
            
    df_synth = pd.DataFrame(synth_records)
    synth_csv_path = out_dir / "BOOTSTRAP_SYNTHETIC_VALIDATION.csv"
    
    # Summary of synthetic results
    synth_summary = df_synth.groupby('exposure_group').agg(
        Coverage_A=('cov_A', 'mean'), Width_A=('width_A', 'mean'),
        Coverage_B=('cov_B', 'mean'), Width_B=('width_B', 'mean'),
        Coverage_C=('cov_C', 'mean'), Width_C=('width_C', 'mean'),
    ).reset_index()
    
    synth_summary_talent = df_synth.groupby('talent_group').agg(
        Coverage_A=('cov_A', 'mean'), Width_A=('width_A', 'mean'),
        Coverage_B=('cov_B', 'mean'), Width_B=('width_B', 'mean'),
        Coverage_C=('cov_C', 'mean'), Width_C=('width_C', 'mean'),
    ).reset_index()
    
    df_synth.to_csv(synth_csv_path, index=False)
    print(f"   Saved synthetic validation results to {synth_csv_path}")

    # -----------------------------------------------------------------
    # REAL-DATA SENSITIVITY PIPELINE (Procedure A vs B vs C)
    # -----------------------------------------------------------------
    print("\n2. Running Real-Data Sensitivity Analysis (Procedures A, B, C on 802 matches)...")
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

    # Focus on Top 25 Batters and Top 25 Bowlers for detailed comparison
    test_bat = bat_final.head(25)
    test_bowl = bowl_final.head(25)
    test_bat_ids = set(test_bat['player_id'])
    test_bowl_ids = set(test_bowl['player_id'])

    hp_bat = df[(df['elig_batting'] == 1) & (df['is_hp'])].copy()
    hp_bat = hp_bat.merge(bexp[['player_id', 'batting_role']], left_on='striker_id', right_on='player_id', how='left')
    bat_match_records = {}
    for m, g in hp_bat.groupby('match_id'):
        bat_match_records[m] = {
            'strikers': g['striker_id'].values,
            'roles': g['batting_role'].values,
            'v': g['v_bat'].values
        }

    hp_bowl = df[(df['elig_bowling'] == 1) & (df['is_hp'])].copy()
    hp_bowl = hp_bowl.merge(wexp[['player_id', 'pace_or_spin']], left_on='bowler_id', right_on='player_id', how='left')
    bowl_match_records = {}
    for m, g in hp_bowl.groupby('match_id'):
        bowl_match_records[m] = {
            'bowlers': g['bowler_id'].values,
            'roles': g['pace_or_spin'].values,
            'v': g['v_bowl'].values
        }

    # Full sample fixed parameters
    sigma_e2_bat_full = hp_bat['v_bat'].var()
    sigma_mu2_bat_full = 0.0349
    role_means_bat_full = hp_bat.groupby('batting_role')['v_bat'].mean().to_dict()

    sigma_e2_bowl_full = hp_bowl['v_bowl'].var()
    sigma_mu2_bowl_full = 0.0223
    role_means_bowl_full = hp_bowl.groupby('pace_or_spin')['v_bowl'].mean().to_dict()

    # Storage for real comparison (500 resamples)
    n_real_boots = 500
    bat_res_A = {pid: [] for pid in test_bat_ids}
    bat_res_B = {pid: [] for pid in test_bat_ids}
    bat_res_C = {pid: [] for pid in test_bat_ids}

    bat_rk_A = {pid: [] for pid in test_bat_ids}
    bat_rk_B = {pid: [] for pid in test_bat_ids}
    bat_rk_C = {pid: [] for pid in test_bat_ids}

    bowl_res_A = {pid: [] for pid in test_bowl_ids}
    bowl_res_B = {pid: [] for pid in test_bowl_ids}
    bowl_res_C = {pid: [] for pid in test_bowl_ids}

    bowl_rk_A = {pid: [] for pid in test_bowl_ids}
    bowl_rk_B = {pid: [] for pid in test_bowl_ids}
    bowl_rk_C = {pid: [] for pid in test_bowl_ids}

    np.random.seed(42)
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
        # Proc B Naive
        means_20 = [p_sums_bat[p]/p_counts_bat[p] for p in p_counts_bat if p_counts_bat[p] >= 20]
        inv_20 = [1.0/p_counts_bat[p] for p in p_counts_bat if p_counts_bat[p] >= 20]
        sigma_mu2_bat_B = max(np.var(means_20, ddof=1) - sigma_e2_bat_b * np.mean(inv_20), 0.005)

        # Proc C Corrected Two-Way
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
        for pid in test_bat_ids:
            n_b = p_counts_bat.get(pid, 0)
            y_b = p_sums_bat.get(pid, 0.0) / max(n_b, 1) if n_b > 0 else 0.0
            r_prior = role_means_bat_full.get(bat_final.loc[bat_final['player_id']==pid, 'role'].values[0], 0.0)

            # A: Fixed
            lam_A = (n_b * sigma_mu2_bat_full) / (n_b * sigma_mu2_bat_full + sigma_e2_bat_full) if n_b > 0 else 0
            sc_A = (lam_A * y_b + (1 - lam_A) * r_prior) * 100
            bat_res_A[pid].append(sc_A)
            scores_A[pid] = sc_A

            # B: Naive Re-estimated
            lam_B = (n_b * sigma_mu2_bat_B) / (n_b * sigma_mu2_bat_B + sigma_e2_bat_b) if n_b > 0 else 0
            sc_B = (lam_B * y_b + (1 - lam_B) * r_prior) * 100
            bat_res_B[pid].append(sc_B)
            scores_B[pid] = sc_B

            # C: Corrected Re-estimated
            lam_C = (n_b * sigma_mu2_bat_C) / (n_b * sigma_mu2_bat_C + sigma_e2_bat_b) if n_b > 0 else 0
            sc_C = (lam_C * y_b + (1 - lam_C) * r_prior) * 100
            bat_res_C[pid].append(sc_C)
            scores_C[pid] = sc_C

        # Rank within top 25
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
        for pid in test_bowl_ids:
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

        for rk, (pid, _) in enumerate(sorted(scores_A_bw.items(), key=lambda x: x[1], reverse=True), 1):
            bowl_rk_A[pid].append(rk)
        for rk, (pid, _) in enumerate(sorted(scores_B_bw.items(), key=lambda x: x[1], reverse=True), 1):
            bowl_rk_B[pid].append(rk)
        for rk, (pid, _) in enumerate(sorted(scores_C_bw.items(), key=lambda x: x[1], reverse=True), 1):
            bowl_rk_C[pid].append(rk)

    # Build real-data sensitivity dataframe
    real_records = []
    # Batters
    for _, r in test_bat.iterrows():
        pid = r['player_id']
        arr_A = np.array(bat_res_A[pid])
        arr_B = np.array(bat_res_B[pid])
        arr_C = np.array(bat_res_C[pid])

        rk_A = np.array(bat_rk_A[pid])
        rk_B = np.array(bat_rk_B[pid])
        rk_C = np.array(bat_rk_C[pid])

        real_records.append({
            'discipline': 'Batter',
            'rank': r['final_rank'],
            'player_id': pid,
            'player_name': r['player_name'],
            'role': r['role'],
            'R_HP': r['R_HP'],
            'n_hp': r['n_hp'],
            'IPL_share': (r['IPL_league'] + r['IPL_knockout']) / max(r['n_total'], 1),
            'exposure_class': 'High (>=250 balls)' if r['n_hp'] >= 250 else ('Medium (100-250)' if r['n_hp'] >= 100 else 'Low (50-100)'),
            # Procedure A
            'A_CI_width': np.percentile(arr_A, 95) - np.percentile(arr_A, 5),
            'A_P_top10': (rk_A <= 10).mean(),
            'A_rank_90_lo': int(np.percentile(rk_A, 5)),
            'A_rank_90_hi': int(np.percentile(rk_A, 95)),
            # Procedure B
            'B_CI_width': np.percentile(arr_B, 95) - np.percentile(arr_B, 5),
            'B_P_top10': (rk_B <= 10).mean(),
            'B_rank_90_lo': int(np.percentile(rk_B, 5)),
            'B_rank_90_hi': int(np.percentile(rk_B, 95)),
            # Procedure C
            'C_CI_width': np.percentile(arr_C, 95) - np.percentile(arr_C, 5),
            'C_P_top10': (rk_C <= 10).mean(),
            'C_rank_90_lo': int(np.percentile(rk_C, 5)),
            'C_rank_90_hi': int(np.percentile(rk_C, 95)),
        })

    # Bowlers
    for _, r in test_bowl.iterrows():
        pid = r['player_id']
        arr_A = np.array(bowl_res_A[pid])
        arr_B = np.array(bowl_res_B[pid])
        arr_C = np.array(bowl_res_C[pid])

        rk_A = np.array(bowl_rk_A[pid])
        rk_B = np.array(bowl_rk_B[pid])
        rk_C = np.array(bowl_rk_C[pid])

        real_records.append({
            'discipline': 'Bowler',
            'rank': r['final_rank'],
            'player_id': pid,
            'player_name': r['player_name'],
            'role': r['role'],
            'R_HP': r['R_HP'],
            'n_hp': r['n_hp'],
            'IPL_share': (r['bowled_IPL league'] + r['bowled_IPL knockout']) / max(r['n_total'], 1) if 'bowled_IPL league' in r else 0.5,
            'exposure_class': 'High (>=250 balls)' if r['n_hp'] >= 250 else ('Medium (100-250)' if r['n_hp'] >= 100 else 'Low (50-100)'),
            # Procedure A
            'A_CI_width': np.percentile(arr_A, 95) - np.percentile(arr_A, 5),
            'A_P_top10': (rk_A <= 10).mean(),
            'A_rank_90_lo': int(np.percentile(rk_A, 5)),
            'A_rank_90_hi': int(np.percentile(rk_A, 95)),
            # Procedure B
            'B_CI_width': np.percentile(arr_B, 95) - np.percentile(arr_B, 5),
            'B_P_top10': (rk_B <= 10).mean(),
            'B_rank_90_lo': int(np.percentile(rk_B, 5)),
            'B_rank_90_hi': int(np.percentile(rk_B, 95)),
            # Procedure C
            'C_CI_width': np.percentile(arr_C, 95) - np.percentile(arr_C, 5),
            'C_P_top10': (rk_C <= 10).mean(),
            'C_rank_90_lo': int(np.percentile(rk_C, 5)),
            'C_rank_90_hi': int(np.percentile(rk_C, 95)),
        })

    df_real = pd.DataFrame(real_records)
    real_csv_path = out_dir / "BOOTSTRAP_REAL_DATA_SENSITIVITY.csv"
    df_real.to_csv(real_csv_path, index=False)
    print(f"   Saved real-data sensitivity results to {real_csv_path}")

    print("\n=== SYNTHETIC VALIDATION SUMMARY (Coverage of True Talent) ===")
    print(synth_summary.to_string())
    print("\n=== SYNTHETIC VALIDATION SUMMARY BY TALENT TIER ===")
    print(synth_summary_talent.to_string())

    print("\n=== REAL-DATA SENSITIVITY SUMMARY (TOP 10 BATTERS) ===")
    print(df_real[df_real['discipline']=='Batter'].head(10)[['rank', 'player_name', 'n_hp', 'A_CI_width', 'B_CI_width', 'C_CI_width', 'A_P_top10', 'B_P_top10', 'C_P_top10']])

    print("\n=== REAL-DATA SENSITIVITY SUMMARY (TOP 10 BOWLERS) ===")
    print(df_real[df_real['discipline']=='Bowler'].head(10)[['rank', 'player_name', 'n_hp', 'A_CI_width', 'B_CI_width', 'C_CI_width', 'A_P_top10', 'B_P_top10', 'C_P_top10']])

if __name__ == '__main__':
    run_investigation()

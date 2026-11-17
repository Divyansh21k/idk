"""
Phase 4 Pipeline: Compute Repaired Player Ratings, Empirical Bayes Shrinkage,
Match-Cluster Stratified Bootstrap, Rank Intervals, and Evidence Classification.
"""
import sys, os, json
from pathlib import Path
import numpy as np
import pandas as pd

def run_phase4():
    print("=== SupeRR Selector Phase 4 Pipeline ===")
    np.random.seed(42)

    base_dir = Path("superr_selector")
    out_dir = base_dir / "outputs"
    step1_dir = out_dir / "step1"
    step2_dir = out_dir / "step2"
    step3_dir = out_dir / "step3"
    baseline_dir = out_dir / "baseline"

    print("1. Loading delivery and pressure datasets...")
    ev = pd.read_csv(step2_dir / "deliveries_with_ev.csv.gz", low_memory=False)
    press = pd.read_csv(step3_dir / "all_deliveries_pressure.csv.gz", low_memory=False)
    bexp = pd.read_csv(step1_dir / "player_exposure_batters.csv")
    wexp = pd.read_csv(step1_dir / "player_exposure_bowlers.csv")

    # Baseline rankings for comparison
    base_bat = pd.read_csv(baseline_dir / "BASELINE_RANKINGS_BATTERS.csv")
    base_bowl = pd.read_csv(baseline_dir / "BASELINE_RANKINGS_BOWLERS.csv")

    df = press[[
        'match_id', 'innings', 'innings_ball_num', 'striker_id', 'bowler_id',
        'cat', 'season', 'PI_final', 'leverage_final', 'elig_batting', 'elig_bowling'
    ]].merge(
        ev[['match_id', 'innings', 'innings_ball_num', 'v_bat', 'v_bowl', 'c_s']],
        on=['match_id', 'innings', 'innings_ball_num'],
        how='inner'
    )
    print(f"   Loaded {len(df):,} merged deliveries across {df['match_id'].nunique()} matches.")

    # High-pressure subset (PI >= 0.80)
    df['is_hp'] = df['PI_final'] >= 0.800

    # -------------------------------------------------------------
    # BATTERS PIPELINE
    # -------------------------------------------------------------
    print("\n2. Processing Batters...")
    bat_df = df[df['elig_batting'] == 1].copy()
    bat_df = bat_df.merge(
        bexp[['player_id', 'player_name', 'batting_role', 'faced_IPL league',
              'faced_IPL knockout', 'faced_T20I non-knockout', 'faced_T20I final']],
        left_on='striker_id', right_on='player_id', how='left'
    )

    # HP delivery variance and role means
    hp_bat = bat_df[bat_df['is_hp']].copy()
    sigma_e2_bat = hp_bat['v_bat'].var()
    role_means_bat = hp_bat.groupby('batting_role')['v_bat'].mean().to_dict()
    global_mean_bat = hp_bat['v_bat'].mean()

    # Estimate between-player talent variance sigma_mu2
    bat_player_hp = hp_bat.groupby('striker_id').agg(
        n=('v_bat', 'count'),
        mean_v=('v_bat', 'mean')
    )
    sample_bat = bat_player_hp[bat_player_hp['n'] >= 20]
    sigma_mu2_bat = max(sample_bat['mean_v'].var() - sigma_e2_bat * (1.0 / sample_bat['n']).mean(), 0.005)

    print(f"   Batters HP: sigma_e2={sigma_e2_bat:.4f}, sigma_mu2={sigma_mu2_bat:.4f} (SD={np.sqrt(sigma_mu2_bat)*100:.2f} runs/100b)")
    print(f"   Batting Role Means (runs/ball): {role_means_bat}")

    # Aggregates across all balls and HP balls
    bat_agg_all = bat_df.groupby('striker_id').agg(
        n_total=('v_bat', 'count'),
        sum_L=('leverage_final', 'sum'),
        sum_L2=('leverage_final', lambda x: (x**2).sum()),
        sum_Lv=('leverage_final', lambda x: (x * bat_df.loc[x.index, 'v_bat']).sum())
    ).reset_index()
    bat_agg_all['N_eff'] = (bat_agg_all['sum_L']**2) / np.maximum(bat_agg_all['sum_L2'], 1e-6)
    bat_agg_all['mean_v_LW'] = bat_agg_all['sum_Lv'] / np.maximum(bat_agg_all['sum_L'], 1e-6)

    bat_agg_hp = hp_bat.groupby('striker_id').agg(
        n_hp=('v_bat', 'count'),
        m_hp=('match_id', 'nunique'),
        sum_v_hp=('v_bat', 'sum'),
        mean_v_hp=('v_bat', 'mean')
    ).reset_index()

    bat_summary = bat_agg_all.merge(bat_agg_hp, on='striker_id', how='left').fillna({'n_hp': 0, 'm_hp': 0, 'sum_v_hp': 0.0, 'mean_v_hp': 0.0})
    bat_summary = bat_summary.merge(
        bexp[['player_id', 'player_name', 'batting_role', 'faced_IPL league',
              'faced_IPL knockout', 'faced_T20I non-knockout', 'faced_T20I final']],
        left_on='striker_id', right_on='player_id', how='left'
    )

    # Compute Empirical Bayes shrinkage
    bat_summary['prior_mean'] = bat_summary['batting_role'].map(role_means_bat).fillna(global_mean_bat)
    bat_summary['lambda_i'] = (bat_summary['n_hp'] * sigma_mu2_bat) / (bat_summary['n_hp'] * sigma_mu2_bat + sigma_e2_bat)
    bat_summary['R_HP'] = (bat_summary['lambda_i'] * bat_summary['mean_v_hp'] + (1 - bat_summary['lambda_i']) * bat_summary['prior_mean']) * 100
    bat_summary['se_analytical'] = bat_summary['lambda_i'] * (np.sqrt(sigma_e2_bat) / np.maximum(np.sqrt(bat_summary['n_hp']), 1.0)) * 100

    # Leverage-weighted rating
    bat_summary['lambda_eff'] = (bat_summary['N_eff'] * sigma_mu2_bat) / (bat_summary['N_eff'] * sigma_mu2_bat + sigma_e2_bat)
    bat_summary['R_LW'] = (bat_summary['lambda_eff'] * bat_summary['mean_v_LW'] + (1 - bat_summary['lambda_eff']) * bat_summary['prior_mean']) * 100

    # Eligibility flags
    bat_summary['elig_floor'] = (bat_summary['n_hp'] >= 50) & (bat_summary['m_hp'] >= 5) & (bat_summary['n_total'] >= 200)
    bat_summary['elig_sustained'] = (bat_summary['n_hp'] >= 100) & (bat_summary['m_hp'] >= 10) & (bat_summary['n_total'] >= 300)

    # -------------------------------------------------------------
    # BOWLERS PIPELINE
    # -------------------------------------------------------------
    print("\n3. Processing Bowlers...")
    bowl_df = df[df['elig_bowling'] == 1].copy()
    bowl_df = bowl_df.merge(
        wexp[['player_id', 'player_name', 'pace_or_spin', 'bowled_IPL league',
              'bowled_IPL knockout', 'bowled_T20I non-knockout', 'bowled_T20I final']],
        left_on='bowler_id', right_on='player_id', how='left'
    )

    # HP delivery variance and role means
    hp_bowl = bowl_df[bowl_df['is_hp']].copy()
    sigma_e2_bowl = hp_bowl['v_bowl'].var()
    role_means_bowl = hp_bowl.groupby('pace_or_spin')['v_bowl'].mean().to_dict()
    global_mean_bowl = hp_bowl['v_bowl'].mean()

    # Estimate between-player talent variance sigma_mu2
    bowl_player_hp = hp_bowl.groupby('bowler_id').agg(
        n=('v_bowl', 'count'),
        mean_v=('v_bowl', 'mean')
    )
    sample_bowl = bowl_player_hp[bowl_player_hp['n'] >= 20]
    sigma_mu2_bowl = max(sample_bowl['mean_v'].var() - sigma_e2_bowl * (1.0 / sample_bowl['n']).mean(), 0.005)

    print(f"   Bowlers HP: sigma_e2={sigma_e2_bowl:.4f}, sigma_mu2={sigma_mu2_bowl:.4f} (SD={np.sqrt(sigma_mu2_bowl)*100:.2f} runs/100b)")
    print(f"   Bowling Role Means (runs/ball): {role_means_bowl}")

    # Aggregates across all balls and HP balls
    bowl_agg_all = bowl_df.groupby('bowler_id').agg(
        n_total=('v_bowl', 'count'),
        sum_L=('leverage_final', 'sum'),
        sum_L2=('leverage_final', lambda x: (x**2).sum()),
        sum_Lv=('leverage_final', lambda x: (x * bowl_df.loc[x.index, 'v_bowl']).sum())
    ).reset_index()
    bowl_agg_all['N_eff'] = (bowl_agg_all['sum_L']**2) / np.maximum(bowl_agg_all['sum_L2'], 1e-6)
    bowl_agg_all['mean_v_LW'] = bowl_agg_all['sum_Lv'] / np.maximum(bowl_agg_all['sum_L'], 1e-6)

    bowl_agg_hp = hp_bowl.groupby('bowler_id').agg(
        n_hp=('v_bowl', 'count'),
        m_hp=('match_id', 'nunique'),
        sum_v_hp=('v_bowl', 'sum'),
        mean_v_hp=('v_bowl', 'mean')
    ).reset_index()

    bowl_summary = bowl_agg_all.merge(bowl_agg_hp, on='bowler_id', how='left').fillna({'n_hp': 0, 'm_hp': 0, 'sum_v_hp': 0.0, 'mean_v_hp': 0.0})
    bowl_summary = bowl_summary.merge(
        wexp[['player_id', 'player_name', 'pace_or_spin', 'bowled_IPL league',
              'bowled_IPL knockout', 'bowled_T20I non-knockout', 'bowled_T20I final']],
        left_on='bowler_id', right_on='player_id', how='left'
    )

    # Compute Empirical Bayes shrinkage
    bowl_summary['prior_mean'] = bowl_summary['pace_or_spin'].map(role_means_bowl).fillna(global_mean_bowl)
    bowl_summary['lambda_i'] = (bowl_summary['n_hp'] * sigma_mu2_bowl) / (bowl_summary['n_hp'] * sigma_mu2_bowl + sigma_e2_bowl)
    bowl_summary['R_HP'] = (bowl_summary['lambda_i'] * bowl_summary['mean_v_hp'] + (1 - bowl_summary['lambda_i']) * bowl_summary['prior_mean']) * 100
    bowl_summary['se_analytical'] = bowl_summary['lambda_i'] * (np.sqrt(sigma_e2_bowl) / np.maximum(np.sqrt(bowl_summary['n_hp']), 1.0)) * 100

    # Leverage-weighted rating
    bowl_summary['lambda_eff'] = (bowl_summary['N_eff'] * sigma_mu2_bowl) / (bowl_summary['N_eff'] * sigma_mu2_bowl + sigma_e2_bowl)
    bowl_summary['R_LW'] = (bowl_summary['lambda_eff'] * bowl_summary['mean_v_LW'] + (1 - bowl_summary['lambda_eff']) * bowl_summary['prior_mean']) * 100

    # Eligibility flags
    bowl_summary['elig_floor'] = (bowl_summary['n_hp'] >= 50) & (bowl_summary['m_hp'] >= 5) & (bowl_summary['n_total'] >= 200)
    bowl_summary['elig_sustained'] = (bowl_summary['n_hp'] >= 100) & (bowl_summary['m_hp'] >= 10) & (bowl_summary['n_total'] >= 300)

    # -------------------------------------------------------------
    # MATCH-CLUSTER STRATIFIED BOOTSTRAP (500 iterations)
    # -------------------------------------------------------------
    print("\n4. Running Match-Cluster Stratified Bootstrap (500 resamples)...")
    matches_df = df[['match_id', 'cat']].drop_duplicates()
    cats = matches_df['cat'].unique()
    match_cats = {c: matches_df[matches_df['cat'] == c]['match_id'].values for c in cats}

    # Pre-aggregate match-player statistics for HP deliveries
    bat_match_hp = hp_bat.groupby(['match_id', 'striker_id']).agg(
        n_m=('v_bat', 'count'),
        sum_v_m=('v_bat', 'sum')
    ).reset_index()

    bowl_match_hp = hp_bowl.groupby(['match_id', 'bowler_id']).agg(
        n_m=('v_bowl', 'count'),
        sum_v_m=('v_bowl', 'sum')
    ).reset_index()

    # Pre-build lookup tables
    eligible_bat_ids = set(bat_summary[bat_summary['elig_floor']]['striker_id'])
    eligible_bowl_ids = set(bowl_summary[bowl_summary['elig_floor']]['bowler_id'])

    bat_role_lookup = bat_summary.set_index('striker_id')['prior_mean'].to_dict()
    bowl_role_lookup = bowl_summary.set_index('bowler_id')['prior_mean'].to_dict()

    # Map match_id to records
    bat_match_dict = {}
    for r in bat_match_hp.itertuples():
        bat_match_dict.setdefault(r.match_id, []).append((r.striker_id, r.n_m, r.sum_v_m))

    bowl_match_dict = {}
    for r in bowl_match_hp.itertuples():
        bowl_match_dict.setdefault(r.match_id, []).append((r.bowler_id, r.n_m, r.sum_v_m))

    n_boots = 500
    bat_boot_ratings = {pid: [] for pid in eligible_bat_ids}
    bowl_boot_ratings = {pid: [] for pid in eligible_bowl_ids}
    bat_boot_ranks = {pid: [] for pid in eligible_bat_ids}
    bowl_boot_ranks = {pid: [] for pid in eligible_bowl_ids}

    for b in range(n_boots):
        sampled_matches = []
        for c in cats:
            m_list = match_cats[c]
            sampled_matches.extend(np.random.choice(m_list, size=len(m_list), replace=True))

        # Batters aggregation
        b_bat_n = {pid: 0 for pid in eligible_bat_ids}
        b_bat_sum = {pid: 0.0 for pid in eligible_bat_ids}
        for m in sampled_matches:
            if m in bat_match_dict:
                for pid, n, s in bat_match_dict[m]:
                    if pid in b_bat_n:
                        b_bat_n[pid] += n
                        b_bat_sum[pid] += s

        b_bat_scores = {}
        for pid in eligible_bat_ids:
            n_b = b_bat_n[pid]
            s_b = b_bat_sum[pid]
            p_mean = bat_role_lookup[pid]
            if n_b > 0:
                mean_b = s_b / n_b
                lam_b = (n_b * sigma_mu2_bat) / (n_b * sigma_mu2_bat + sigma_e2_bat)
                r_b = (lam_b * mean_b + (1 - lam_b) * p_mean) * 100
            else:
                r_b = p_mean * 100
            bat_boot_ratings[pid].append(r_b)
            b_bat_scores[pid] = r_b

        # Rank batters in resample b
        sorted_bat = sorted(b_bat_scores.items(), key=lambda x: x[1], reverse=True)
        for rank_idx, (pid, _) in enumerate(sorted_bat, 1):
            bat_boot_ranks[pid].append(rank_idx)

        # Bowlers aggregation
        b_bowl_n = {pid: 0 for pid in eligible_bowl_ids}
        b_bowl_sum = {pid: 0.0 for pid in eligible_bowl_ids}
        for m in sampled_matches:
            if m in bowl_match_dict:
                for pid, n, s in bowl_match_dict[m]:
                    if pid in b_bowl_n:
                        b_bowl_n[pid] += n
                        b_bowl_sum[pid] += s

        b_bowl_scores = {}
        for pid in eligible_bowl_ids:
            n_b = b_bowl_n[pid]
            s_b = b_bowl_sum[pid]
            p_mean = bowl_role_lookup[pid]
            if n_b > 0:
                mean_b = s_b / n_b
                lam_b = (n_b * sigma_mu2_bowl) / (n_b * sigma_mu2_bowl + sigma_e2_bowl)
                r_b = (lam_b * mean_b + (1 - lam_b) * p_mean) * 100
            else:
                r_b = p_mean * 100
            bowl_boot_ratings[pid].append(r_b)
            b_bowl_scores[pid] = r_b

        # Rank bowlers in resample b
        sorted_bowl = sorted(b_bowl_scores.items(), key=lambda x: x[1], reverse=True)
        for rank_idx, (pid, _) in enumerate(sorted_bowl, 1):
            bowl_boot_ranks[pid].append(rank_idx)

        if (b + 1) % 100 == 0:
            print(f"   Completed {b + 1}/{n_boots} bootstrap iterations...")

    # Compute bootstrap summary statistics for Batters
    bat_summary['CI_90_lo'] = np.nan
    bat_summary['CI_90_hi'] = np.nan
    bat_summary['se_boot'] = np.nan
    bat_summary['rank_90_lo'] = np.nan
    bat_summary['rank_90_hi'] = np.nan
    bat_summary['P_top10'] = np.nan

    for pid in eligible_bat_ids:
        r_arr = np.array(bat_boot_ratings[pid])
        rk_arr = np.array(bat_boot_ranks[pid])
        idx = bat_summary[bat_summary['striker_id'] == pid].index[0]
        bat_summary.at[idx, 'CI_90_lo'] = np.percentile(r_arr, 5)
        bat_summary.at[idx, 'CI_90_hi'] = np.percentile(r_arr, 95)
        bat_summary.at[idx, 'se_boot'] = np.std(r_arr, ddof=1)
        bat_summary.at[idx, 'rank_90_lo'] = int(np.percentile(rk_arr, 5))
        bat_summary.at[idx, 'rank_90_hi'] = int(np.percentile(rk_arr, 95))
        bat_summary.at[idx, 'P_top10'] = (rk_arr <= 10).mean()

    # Compute bootstrap summary statistics for Bowlers
    bowl_summary['CI_90_lo'] = np.nan
    bowl_summary['CI_90_hi'] = np.nan
    bowl_summary['se_boot'] = np.nan
    bowl_summary['rank_90_lo'] = np.nan
    bowl_summary['rank_90_hi'] = np.nan
    bowl_summary['P_top10'] = np.nan

    for pid in eligible_bowl_ids:
        r_arr = np.array(bowl_boot_ratings[pid])
        rk_arr = np.array(bowl_boot_ranks[pid])
        idx = bowl_summary[bowl_summary['bowler_id'] == pid].index[0]
        bowl_summary.at[idx, 'CI_90_lo'] = np.percentile(r_arr, 5)
        bowl_summary.at[idx, 'CI_90_hi'] = np.percentile(r_arr, 95)
        bowl_summary.at[idx, 'se_boot'] = np.std(r_arr, ddof=1)
        bowl_summary.at[idx, 'rank_90_lo'] = int(np.percentile(rk_arr, 5))
        bowl_summary.at[idx, 'rank_90_hi'] = int(np.percentile(rk_arr, 95))
        bowl_summary.at[idx, 'P_top10'] = (rk_arr <= 10).mean()

    # -------------------------------------------------------------
    # EVIDENCE CLASSIFICATION
    # -------------------------------------------------------------
    print("\n5. Classifying Evidence Tiers...")
    def classify_evidence(row):
        if not row['elig_floor']:
            return "Ineligible"
        # Strong evidence: Sustained tier, CI lower bound > 0, and substantial Top 10 probability or clear positive significance
        if row['elig_sustained'] and row['CI_90_lo'] > 0 and row['P_top10'] >= 0.35:
            return "Strong evidence"
        # If sustained and CI_lo > 0 but P_top10 < 0.35 (solid above-average performer)
        elif row['elig_sustained'] and row['CI_90_lo'] > 0:
            return "Strong evidence (Solid Above-Average)"
        # Promising but limited evidence: meets floor, positive point estimate, but narrower sample or CI crosses zero
        elif row['R_HP'] > 0 and (row['CI_90_hi'] - row['CI_90_lo']) <= 30.0:
            return "Promising but limited evidence"
        else:
            return "Highly uncertain"

    bat_summary['evidence_tier'] = bat_summary.apply(classify_evidence, axis=1)
    bowl_summary['evidence_tier'] = bowl_summary.apply(classify_evidence, axis=1)

    # -------------------------------------------------------------
    # MERGE BASELINE MODEL B RANKS FOR COMPARISON
    # -------------------------------------------------------------
    bat_summary = bat_summary.merge(
        base_bat[['player_name', 'rank', 'R_overall']].rename(columns={'rank': 'baseline_rank', 'R_overall': 'baseline_rating'}),
        on='player_name', how='left'
    )
    bowl_summary = bowl_summary.merge(
        base_bowl[['player_name', 'rank', 'R_overall']].rename(columns={'rank': 'baseline_rank', 'R_overall': 'baseline_rating'}),
        on='player_name', how='left'
    )

    # Filter and Rank eligible players
    bat_eligible = bat_summary[bat_summary['elig_floor']].copy()
    bat_eligible = bat_eligible.sort_values(by='R_HP', ascending=False).reset_index(drop=True)
    bat_eligible['final_rank'] = bat_eligible.index + 1

    bowl_eligible = bowl_summary[bowl_summary['elig_floor']].copy()
    bowl_eligible = bowl_eligible.sort_values(by='R_HP', ascending=False).reset_index(drop=True)
    bowl_eligible['final_rank'] = bowl_eligible.index + 1

    # Select and order final columns
    final_cols = [
        'final_rank', 'player_id', 'player_name', 'role',
        'R_HP', 'CI_90_lo', 'CI_90_hi', 'se_analytical', 'se_boot', 'reliability',
        'rank_90_lo', 'rank_90_hi', 'P_top10',
        'n_total', 'n_hp', 'm_hp', 'N_eff', 'R_LW',
        'IPL_league', 'IPL_knockout', 'T20I_nonKO', 'T20I_final',
        'eligibility_status', 'evidence_tier',
        'baseline_rank', 'baseline_rating'
    ]

    # Format Batters
    if 'player_id' in bat_eligible.columns and 'striker_id' in bat_eligible.columns:
        bat_eligible = bat_eligible.drop(columns=['player_id'])
    bat_export = bat_eligible.rename(columns={
        'striker_id': 'player_id',
        'batting_role': 'role',
        'lambda_i': 'reliability',
        'faced_IPL league': 'IPL_league',
        'faced_IPL knockout': 'IPL_knockout',
        'faced_T20I non-knockout': 'T20I_nonKO',
        'faced_T20I final': 'T20I_final',
    }).copy()
    bat_export['eligibility_status'] = np.where(bat_export['elig_sustained'], "Sustained (>=100 balls, >=10 matches)", "Floor (>=50 balls, >=5 matches)")
    bat_export = bat_export[final_cols]

    # Format Bowlers
    if 'player_id' in bowl_eligible.columns and 'bowler_id' in bowl_eligible.columns:
        bowl_eligible = bowl_eligible.drop(columns=['player_id'])
    bowl_export = bowl_eligible.rename(columns={
        'bowler_id': 'player_id',
        'pace_or_spin': 'role',
        'lambda_i': 'reliability',
        'bowled_IPL league': 'IPL_league',
        'bowled_IPL knockout': 'IPL_knockout',
        'bowled_T20I non-knockout': 'T20I_nonKO',
        'bowled_T20I final': 'T20I_final',
    }).copy()
    bowl_export['eligibility_status'] = np.where(bowl_export['elig_sustained'], "Sustained (>=100 balls, >=10 matches)", "Floor (>=50 balls, >=5 matches)")
    bowl_export = bowl_export[final_cols]

    # Save final ranking CSVs
    bat_csv_path = out_dir / "FINAL_REPAIRED_BATTER_RANKINGS.csv"
    bowl_csv_path = out_dir / "FINAL_REPAIRED_BOWLERS_RANKINGS.csv"
    bat_export.to_csv(bat_csv_path, index=False)
    bowl_export.to_csv(out_dir / "FINAL_REPAIRED_BOWLER_RANKINGS.csv", index=False)

    print(f"\n6. Successfully generated final rankings:")
    print(f"   Batters: {len(bat_export)} eligible players saved to {bat_csv_path}")
    print(f"   Bowlers: {len(bowl_export)} eligible players saved to {out_dir / 'FINAL_REPAIRED_BOWLER_RANKINGS.csv'}")

    # Print Top 10 for inspection
    print("\n=== TOP 10 REPAIRED BATTERS UNDER PRESSURE ===")
    print(bat_export.head(10)[['final_rank', 'player_name', 'role', 'R_HP', 'CI_90_lo', 'CI_90_hi', 'P_top10', 'n_hp', 'm_hp', 'evidence_tier']])

    print("\n=== TOP 10 REPAIRED BOWLERS UNDER PRESSURE ===")
    print(bowl_export.head(10)[['final_rank', 'player_name', 'role', 'R_HP', 'CI_90_lo', 'CI_90_hi', 'P_top10', 'n_hp', 'm_hp', 'evidence_tier']])

if __name__ == '__main__':
    run_phase4()

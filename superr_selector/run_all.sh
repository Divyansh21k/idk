#!/usr/bin/env bash
set -euo pipefail

# SupeRR Selector Season 2 — Round 1: End-to-End Pipeline
# Runs entire audited data layer, expected value, win probability, leverage,
# player models, eligibility/ranking, and report generation.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RAW_DIR="${1:-data/raw}"
OUT_DIR="${2:-outputs}"

echo "=========================================================="
echo "SupeRR Selector Season 2: Round 1 End-to-End Execution"
echo "  Raw data dir: $RAW_DIR"
echo "  Output dir:   $OUT_DIR"
echo "=========================================================="

echo ""
echo "[Step 1/6] Building analysis tables from raw CSVs..."
python3 src/step1_build_tables.py --raw-dir "$RAW_DIR" --out-dir "$OUT_DIR"

echo ""
echo "[Step 1b] Running 49 validation checks on Step 1 tables..."
python3 src/step1_validate.py --raw-dir "$RAW_DIR" --out-dir "$OUT_DIR"

echo ""
echo "[Step 2/6] Identity-free expected performance & resource table..."
python3 src/step2_expected_value.py --out-dir "$OUT_DIR"

echo ""
echo "[Step 3/6] Win probability, leverage & pressure index (PI)..."
python3 src/step3_win_probability.py --out-dir "$OUT_DIR"

echo ""
echo "[Step 4/6] Hierarchical player models & match-cluster bootstrap (500 resamples)..."
python3 src/step4_player_model.py --out-dir "$OUT_DIR" --n-bootstrap 500

echo ""
echo "[Step 5/6] Eligibility filtering & uncertainty analysis..."
python3 src/step5_eligibility_ranking.py --out-dir "$OUT_DIR"

echo ""
echo "[Step 6/6] Generating deliverables, rankings, and reports..."
python3 src/step6_reports_and_deliverables.py --out-dir "$OUT_DIR"

echo ""
echo "=========================================================="
echo "Pipeline execution finished successfully!"
echo "Final deliverables available in: $OUT_DIR/final_deliverables/"
echo "=========================================================="

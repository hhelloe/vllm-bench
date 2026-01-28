#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./plot.sh results/summary/vllm_summary.json results/plots

SUMMARY="${1:-results/summary/vllm_summary.json}"
OUTDIR="${2:-results/plots}"

python bench/plot.py \
  --summary "$SUMMARY" \
  --outdir "$OUTDIR"

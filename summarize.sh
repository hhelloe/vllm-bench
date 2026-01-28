#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/summary.sh results/raw/vllm_raw.jsonl results/summary/vllm_summary.json
INP="${1:-results/raw/vllm_raw.jsonl}"
OUT="${2:-results/summary/vllm_summary.json}"

python bench/summarize.py --inp "$INP" --out "$OUT"

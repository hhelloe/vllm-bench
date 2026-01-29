#!/usr/bin/env bash
set -euo pipefail

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate vllm

python scripts/gen_workload_sort.py \
  --out workloads/test_sort.jsonl \
  --n 50

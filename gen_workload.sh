#!/usr/bin/env bash
set -euo pipefail

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate vllm

python scripts/gen_workload.py \
  --out workloads/workload_3mix.jsonl \
  --n 300

#!/usr/bin/env bash
set -euo pipefail

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate vllm

python bench/run_bench_vllm.py \
  --base-url http://127.0.0.1:8000 \
  --model /home/aus/data/models/Qwen/Qwen2.5-7B-Instruct \
  --workload workloads/test.jsonl \
  --concurrency 1 4 8 16 \
  --out results/raw/vllm_raw.jsonl

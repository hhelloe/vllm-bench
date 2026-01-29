#!/usr/bin/env bash
set -e

############################
# 可配置参数（你以后常改的）
############################

MODEL_PATH="/home/aus/data/models/Qwen/Qwen2.5-7B-Instruct"
OUT_PREFIX="$HOME/nsys_reports/vllm_server_hot"
DELAY=60
DURATION=60

############################
# 环境准备
############################

mkdir -p "$(dirname "$OUT_PREFIX")"

echo "==> Using model: $MODEL_PATH"
echo "==> Nsight output prefix: $OUT_PREFIX"
echo "==> Delay: ${DELAY}s, Duration: ${DURATION}s"
echo

############################
# 启动 vLLM Server + nsys
############################

nsys profile \
  -o "$OUT_PREFIX" \
  --force-overwrite=true \
  --trace=cuda,osrt,nvtx \
  --sample=cpu \
  --cpuctxsw=process-tree \
  --wait=all \
  --delay="$DELAY" \
  --duration="$DURATION" \
  python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_PATH"

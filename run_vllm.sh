conda activate vllm

export MODEL="/home/aus/data/models/Qwen/Qwen2.5-7B-Instruct"

python -m vllm.entrypoints.openai.api_server \
  --model "$MODEL" \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype float16 \
  --max-model-len 4096
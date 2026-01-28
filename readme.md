# vLLM 推理压测实验记录

本仓库用于记录基于 **vLLM OpenAI API Server** 的大模型推理压测实验流程、配置与结果，
目标是理解并分析 **并发、调度、prefill / decode 行为** 对推理性能（TTFT / latency）的影响。

---

## 1. 实验环境

### 硬件
- GPU：NVIDIA RTX 4090
- 显存：24 GB
- CPU / 内存：本地开发机
- 运行环境：WSL2（Ubuntu）

### 软件
- OS：Ubuntu (WSL2)
- Python：3.12（conda）
- vLLM：0.14.1
- CUDA / Driver：本地可用（4090）
- Benchmark client：Python + httpx + asyncio

---

## 2. 模型信息

- 模型名称：Qwen/Qwen2.5-7B-Instruct
- 模型加载方式：本地路径
- 最大上下文长度：4096
- 精度：float16

---

## 3. vLLM Server 启动方式
> ⚠️ **已废弃（Deprecated）**
>
>下列方式已被打包为脚本使用，根据环境、模型、路径等不同请自行修改

```bash
conda activate vllm

export MODEL="/home/aus/data/models/Qwen/Qwen2.5-7B-Instruct"

python -m vllm.entrypoints.openai.api_server \
  --model "$MODEL" \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype float16 \
  --max-model-len 4096

```

## 4.run_bench_vllm
调用./run_bench_vllm/sh
参数请自行进入脚本内修改

结果以JSONL形式写入，示例：
{
  "id": "req_000001",
  "profile": "short_short",
  "ttft_s": 0.038,
  "total_s": 0.56,
  "concurrency": 16
}

## 结果与分析见analysis.md
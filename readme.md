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

## 5.summarize

## 6.plot

## 下面是笔者自己的步骤
### 脑测的核心假设
H1：TTFT 主要由 prefill 决定，prompt 越长 TTFT 越高（近似线性或次线性，取决于批与实现）
H2：TPOT 主要由 decode 决定，输出越长、并发越高，TPOT 趋于稳定但可能因调度/碎片化恶化
H3：当并发升高时，瓶颈会从 GEMM-heavy（prefill）转向 memory-bound（decode/KV 带宽 + step 粒度）
H4：nsys 上“长块/短块”的比例会随 workload 改变：prefill-heavy → 长块占比上升；decode-heavy → 短碎块密度上升

### 程序运行前的修改
加了如下4种情况的请求，并且添加程序让它们按顺序生成，以便于在nsys里观察
SS（short prompt, short output）：prompt_rep=40, max_tokens=8
SL（short prompt, long output）：prompt_rep=40, max_tokens=512
LS（long prompt, short output）：prompt_rep=400, max_tokens=8
LL（long prompt, long output）：prompt_rep=400, max_tokens=512
这一组被我命名为tiny

SS（short prompt, short output）：prompt_rep=40, max_tokens=1
SL（short prompt, long output）：prompt_rep=40, max_tokens=512
LS（long prompt, short output）：prompt_rep=1000, max_tokens=1
LL（long prompt, long output）：prompt_rep=1000， max_tokens=512
这一组被我命名为huge

控制的变量如上
### 结果
**所有的plot结果都在results/plots里**
#### total
latency随max_tokens显著增长，说明decode贡献了主要的可变部分，prefill 更像固定成本

#### ttft
低并发：长 prompt TTFT 更高 → prefill 主导
并发升高：趋同 → 排队/调度主导
c=32：短 prompt + 长输出 TTFT 最大 → decode/调度压力影响首 token

#### tpot
huge：在max_tokens很短的场景下，TPOT 被固定开销主导（TTFT、调度、kernel launch/同步等难以摊薄），因此平均 TPOT 反而偏大
tiny：低token规模下，常数项（调度、框架、网络）占比高，导致TPOT对工作负载差异不敏感
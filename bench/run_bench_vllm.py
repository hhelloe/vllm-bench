import argparse
import asyncio
import time
import orjson
from pathlib import Path

import httpx


async def send_one(client, sem, req, model):
    """
    发送单个请求，测 TTFT / total time
    """
    async with sem:
        t0 = time.perf_counter()
        ttft = None

        async with client.stream(
            "POST",
            "/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": req["prompt"]}],
                "max_tokens": req["max_tokens"],
                "temperature": req["temperature"],
                "top_p": req["top_p"],
                "stream": True,
            },
        ) as resp:
            async for line in resp.aiter_lines():
                if not line:
                    continue
                if ttft is None:
                    ttft = time.perf_counter() - t0

        total = time.perf_counter() - t0

    return {
        "id": req["id"],
        "profile": req["profile"],
        "ttft_s": ttft,
        "total_s": total,
    }


async def run_once(base_url, model, workload, concurrency):
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(base_url=base_url, timeout=None) as client:
        tasks = [
            send_one(client, sem, req, model)
            for req in workload
        ]
        return await asyncio.gather(*tasks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--workload", required=True)
    ap.add_argument("--concurrency", type=int, nargs="+", required=True)
    ap.add_argument("--out", required=True)

    # NEW: warmup rounds per concurrency
    ap.add_argument(
        "--warmup",
        type=int,
        default=0,
        help="number of warmup rounds per concurrency (results are discarded)",
    )
    args = ap.parse_args()
    workload = []
    with open(args.workload, "rb") as f:
        for line in f:
            workload.append(orjson.loads(line))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("wb") as f:
        for c in args.concurrency:
            print(f"Running concurrency = {c}")
             # NEW: warmup (discard results)
            for i in range(args.warmup):
                print(f"  Warmup {i + 1}/{args.warmup}")
                asyncio.run(run_once(args.base_url, args.model, workload, c))

            # measure
            results = asyncio.run(run_once(args.base_url, args.model, workload, c))
            for r in results:
                r["concurrency"] = c
                f.write(orjson.dumps(r))
                f.write(b"\n")


if __name__ == "__main__":
    main()

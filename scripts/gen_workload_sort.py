import argparse
import random
import orjson
from pathlib import Path
'''
生成工作请求，根据需求修改
'''

def make_prompt(n_tokens: int) -> str:
    return ("请总结以下内容：" + ("猫在盒子里。 " * n_tokens)).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    mixes = [
        {"name": "short_short", "prompt_rep": 400,  "max_tokens": 1, "weight": 0.4},
        {"name": "long_short",  "prompt_rep": 400, "max_tokens": 1, "weight": 0.4},
        {"name": "long_long",   "prompt_rep": 400, "max_tokens": 1, "weight": 0.2},
    ]

    # 按顺序生成：先 short_short，再 long_short，最后 long_long
    with out.open("wb") as f:
        req_idx = 0
        for m in mixes:
            count = int(args.n * m["weight"])
            # 最后一个类型补齐剩余数量
            if req_idx + count > args.n:
                count = args.n - req_idx
            for _ in range(count):
                item = {
                    "id": f"req_{req_idx:06d}",
                    "profile": m["name"],
                    "prompt": make_prompt(m["prompt_rep"]),
                    "max_tokens": m["max_tokens"],
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "stream": True,
                }
                f.write(orjson.dumps(item))
                f.write(b"\n")
                req_idx += 1

    print(f"Wrote {args.n} requests to {out}")

if __name__ == "__main__":
    main()

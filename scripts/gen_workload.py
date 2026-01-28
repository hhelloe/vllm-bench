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
        {"name": "short_short", "prompt_rep": 40,  "max_tokens": 128, "weight": 0.4},
        {"name": "long_short",  "prompt_rep": 600, "max_tokens": 128, "weight": 0.4},
        {"name": "long_long",   "prompt_rep": 600, "max_tokens": 512, "weight": 0.2},
    ]

    weights = [m["weight"] for m in mixes]

    with out.open("wb") as f:
        for i in range(args.n):
            m = random.choices(mixes, weights=weights, k=1)[0]
            item = {
                "id": f"req_{i:06d}",
                "profile": m["name"],
                "prompt": make_prompt(m["prompt_rep"]),
                "max_tokens": m["max_tokens"],
                "temperature": 0.2,
                "top_p": 0.9,
                "stream": True,
            }
            f.write(orjson.dumps(item))
            f.write(b"\n")

    print(f"Wrote {args.n} requests to {out}")

if __name__ == "__main__":
    main()

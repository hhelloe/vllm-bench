# bench/summarize.py
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


def percentile(sorted_xs, p: float) -> float:
    """线性插值分位数。sorted_xs 必须已排序。p in [0,1]."""
    if not sorted_xs:
        return float("nan")
    if p <= 0:
        return float(sorted_xs[0])
    if p >= 1:
        return float(sorted_xs[-1])
    i = (len(sorted_xs) - 1) * p
    lo = math.floor(i)
    hi = math.ceil(i)
    if lo == hi:
        return float(sorted_xs[lo])
    a = sorted_xs[lo]
    b = sorted_xs[hi]
    return float(a * (hi - i) + b * (i - lo))


def summarize_values(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    xs.sort()
    n = len(xs)
    if n == 0:
        return {
            "n": 0,
            "mean": None,
            "min": None,
            "max": None,
            "p50": None,
            "p90": None,
            "p95": None,
            "p99": None,
        }
    mean = sum(xs) / n
    return {
        "n": n,
        "mean": mean,
        "min": xs[0],
        "max": xs[-1],
        "p50": percentile(xs, 0.50),
        "p90": percentile(xs, 0.90),
        "p95": percentile(xs, 0.95),
        "p99": percentile(xs, 0.99),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", required=True, help="input jsonl, e.g. results/raw/vllm_raw.jsonl")
    ap.add_argument("--out", required=True, help="output summary json")
    args = ap.parse_args()

    inp = Path(args.inp)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    # groups[(profile, concurrency)] = {"ttft": [...], "total": [...], "tpot": [...]}
    groups = defaultdict(lambda: {"ttft": [], "total": [], "tpot": []})

    with inp.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            key = (r["profile"], int(r["concurrency"]))
            groups[key]["ttft"].append(r.get("ttft_s"))
            groups[key]["total"].append(r.get("total_s"))
            groups[key]["tpot"].append(r.get("tpot_s"))

    profiles = sorted({k[0] for k in groups.keys()})
    concurrencies = sorted({k[1] for k in groups.keys()})

    summary = {
        "input": str(inp),
        "profiles": profiles,
        "concurrencies": concurrencies,
        "by_profile": {},
    }

    for profile in profiles:
        summary["by_profile"][profile] = {}
        for c in concurrencies:
            vals = groups.get((profile, c))
            if vals is None:
                continue
            summary["by_profile"][profile][str(c)] = {
                "ttft_s": summarize_values(vals["ttft"]),
                "total_s": summarize_values(vals["total"]),
                "tpot_s": summarize_values(vals["tpot"]),
            }

    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote summary: {out}")


if __name__ == "__main__":
    main()

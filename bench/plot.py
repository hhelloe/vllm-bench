# bench/plot.py
import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True, help="summary json from summarize.py")
    ap.add_argument("--outdir", required=True, help="directory to write png plots")
    args = ap.parse_args()

    summary_path = Path(args.summary)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    profiles = summary["profiles"]
    concurrencies = [int(x) for x in summary["concurrencies"]]
    by_profile = summary["by_profile"]

    # 我们画三类图：TTFT / TOTAL / TPOT
    # 每张图画两条线：p50 与 p95
    for profile in profiles:
        for metric in ("ttft_s", "total_s", "tpot_s"):
            xs = []
            p50s = []
            p95s = []
            ns = []

            for c in concurrencies:
                bucket = by_profile.get(profile, {}).get(str(c))
                if not bucket:
                    continue
                stat = bucket[metric]
                xs.append(c)
                p50s.append(stat["p50"])
                p95s.append(stat["p95"])
                ns.append(stat["n"])

            if not xs:
                continue

            plt.figure()
            plt.plot(xs, p50s, marker="o", label="p50")
            plt.plot(xs, p95s, marker="o", label="p95")
            plt.xlabel("concurrency")
            plt.ylabel(metric)
            plt.title(f"{profile} - {metric} (p50/p95)")
            plt.legend()
            plt.grid(True, which="both", linestyle="--", linewidth=0.5)

            outpath = outdir / f"{profile}__{metric}.png"
            plt.savefig(outpath, dpi=160, bbox_inches="tight")
            plt.close()
            print(f"Wrote plot: {outpath}")

    # 额外再输出一个“样本量”图，避免误读（n 太小 p95 会很飘）
    for profile in profiles:
        xs = []
        ns = []
        for c in concurrencies:
            bucket = by_profile.get(profile, {}).get(str(c))
            if not bucket:
                continue
            n = bucket["ttft_s"]["n"]
            xs.append(c)
            ns.append(n)

        if not xs:
            continue

        plt.figure()
        plt.plot(xs, ns, marker="o")
        plt.xlabel("concurrency")
        plt.ylabel("n (samples)")
        plt.title(f"{profile} - sample count")
        plt.grid(True, which="both", linestyle="--", linewidth=0.5)

        outpath = outdir / f"{profile}__n.png"
        plt.savefig(outpath, dpi=160, bbox_inches="tight")
        plt.close()
        print(f"Wrote plot: {outpath}")


if __name__ == "__main__":
    main()

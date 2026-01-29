# bench/plot.py
import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def plot_combined_metric(by_profile, profiles, concurrencies, metric, outdir):
    """Plot combined p50 and p95 values for all profiles on separate graphs."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    colors = {'LL': '#1f77b4', 'LS': '#ff7f0e', 'SL': '#2ca02c', 'SS': '#d62728'}
    markers = {'LL': 'o', 'LS': 's', 'SL': '^', 'SS': 'D'}

    # 生成p50组合图
    plt.figure()
    for profile in profiles:
        xs = []
        p50s = []
        for c in concurrencies:
            bucket = by_profile.get(profile, {}).get(str(c))
            if not bucket:
                continue
            stat = bucket[metric]
            xs.append(c)
            p50s.append(stat["p50"])

        if xs:
            plt.plot(xs, p50s, marker=markers[profile],
                     color=colors[profile], label=profile, linewidth=2)

    plt.xlabel("concurrency")
    plt.ylabel(metric + " (seconds)")
    plt.title(f"{metric} p50 - All Profiles")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    outpath = outdir / f"combined_p50.png"
    plt.savefig(outpath, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Wrote plot: {outpath}")

    # 生成p95组合图
    plt.figure()
    for profile in profiles:
        xs = []
        p95s = []
        for c in concurrencies:
            bucket = by_profile.get(profile, {}).get(str(c))
            if not bucket:
                continue
            stat = bucket[metric]
            xs.append(c)
            p95s.append(stat["p95"])

        if xs:
            plt.plot(xs, p95s, marker=markers[profile],
                     color=colors[profile], label=profile, linewidth=2)

    plt.xlabel("concurrency")
    plt.ylabel(metric + " (seconds)")
    plt.title(f"{metric} p95 - All Profiles")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    outpath = outdir / f"combined_p95.png"
    plt.savefig(outpath, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Wrote plot: {outpath}")


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
    # 并按metric分类到子目录
    metric_dirs = {
        "ttft_s": outdir / "ttft",
        "total_s": outdir / "total",
        "tpot_s": outdir / "tpot"
    }

    for profile in profiles:
        for metric in ("ttft_s", "total_s", "tpot_s"):
            xs = []
            p50s = []
            p95s = []

            for c in concurrencies:
                bucket = by_profile.get(profile, {}).get(str(c))
                if not bucket:
                    continue
                stat = bucket[metric]
                xs.append(c)
                p50s.append(stat["p50"])
                p95s.append(stat["p95"])

            if not xs:
                continue

            metric_outdir = metric_dirs[metric]
            metric_outdir.mkdir(parents=True, exist_ok=True)

            plt.figure()
            plt.plot(xs, p50s, marker="o", label="p50")
            plt.plot(xs, p95s, marker="o", label="p95")
            plt.xlabel("concurrency")
            plt.ylabel(metric + " (seconds)")
            plt.title(f"{profile} - {metric} (p50/p95)")
            plt.legend()
            plt.grid(True, which="both", linestyle="--", linewidth=0.5)

            outpath = metric_outdir / f"{profile}__{metric}.png"
            plt.savefig(outpath, dpi=160, bbox_inches="tight")
            plt.close()
            print(f"Wrote plot: {outpath}")

    # 生成组合图：所有profile的TTFT p50和p95画在一起
    plot_combined_metric(by_profile, profiles, concurrencies, "ttft_s", metric_dirs["ttft_s"])
    # 生成组合图：所有profile的TPOT p50和p95画在一起
    plot_combined_metric(by_profile, profiles, concurrencies, "tpot_s", metric_dirs["tpot_s"])
    # 生成组合图：所有profile的TOTAL p50和p95画在一起
    plot_combined_metric(by_profile, profiles, concurrencies, "total_s", metric_dirs["total_s"])


if __name__ == "__main__":
    main()

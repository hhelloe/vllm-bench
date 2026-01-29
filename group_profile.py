import json
from collections import defaultdict

groups = defaultdict(list)

with open("results/raw/vllm_raw.jsonl", "r") as f:
    for line in f:
        r = json.loads(line)
        groups[r["profile"]].append(r)

# 看有哪些 profile
print(groups.keys())

# 取出某一个 profile
ss = groups["SS"]
sl = groups["SL"]
ls = groups["LS"]
ll = groups["LL"]


filtered = [
    {
        "ttft_s": r["ttft_s"],
    }
    for r in ss
]

print(filtered)
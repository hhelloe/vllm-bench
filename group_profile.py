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
short_short = groups["short_short"]
long_short  = groups["long_short"]
long_long   = groups["long_long"]

print(len(short_short), len(long_short))

filtered = [
    {
        "ttft_s": r["ttft_s"],
    }
    for r in short_short
]

print(filtered)
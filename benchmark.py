"""Run python benchmark.py --repeat 5 --output results/benchmark.json.

Time and memory are measured in separate runs so tracemalloc does not inflate
reported solve times. Peak traced Python allocation is NOT process RSS.
"""
import argparse
import json
import platform
from pathlib import Path
import statistics

from logic_lab.levels import LEVELS
from logic_lab.games.pipes import Pipes
from logic_lab.games.lightup import LightUp
from logic_lab.search import search


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--output", default="results/benchmark.json")
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")
    records = []
    for level in LEVELS:
        for algorithm in ("dfs", "greedy"):
            make = lambda: Pipes(level) if level["game"] == "pipes" else LightUp(level)
            search(make(), algorithm)  # warm-up
            runs = [search(make(), algorithm) for _ in range(args.repeat)]
            measured = search(make(), algorithm, measure_memory=True)
            records.append({"level": level["id"], "algorithm": algorithm,
                            "statuses": [r["status"] for r in runs],
                            "median_ms": statistics.median(r["metrics"]["elapsed_ms"] for r in runs),
                            "runs_ms": [r["metrics"]["elapsed_ms"] for r in runs],
                            "expanded": runs[0]["metrics"]["expanded"],
                            "frontier_peak": runs[0]["metrics"]["frontier_peak"],
                            "memory_status": measured["status"],
                            "peak_python_kib": measured["metrics"]["peak_kib"]})
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"python": platform.python_version(), "platform": platform.platform(),
                                 "repeat": args.repeat, "scope": "search only, no UI/HTTP/trace; peak Python allocations, not RSS",
                                 "results": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(records)} results to {output}")


if __name__ == "__main__":
    main()

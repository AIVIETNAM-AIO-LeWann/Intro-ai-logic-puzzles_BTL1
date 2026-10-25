"""Reproducible DFS/Greedy comparison; standard-library only.

Time and traced Python allocations use separate runs. Puzzle construction,
UI, HTTP and trace storage are outside the measured search scope.
"""
import argparse
import csv
from datetime import datetime, timezone
import gc
import hashlib
import json
import math
import platform
from pathlib import Path
import statistics
import subprocess

from logic_lab.inputs import load_levels, make_problem, suite_levels
from logic_lab.search import search


def verify(problem, result):
    if result["status"] != "solved":
        return None
    solution = result["solution"]
    checked = (problem.check(solution["tiles"]) if "tiles" in solution
               else problem.check(solution["bulbs"]))
    if not checked["solved"]:
        raise RuntimeError("Benchmark stopped: invalid solver solution.")
    return True


def run_case(level, algorithm, repeat, timeout, max_nodes, memory_timeout):
    def run(*, memory=False):
        problem = make_problem(level)
        if memory:
            gc.collect()  # Outside the measured search and isolated memory trace.
        result = search(problem, algorithm, timeout=memory_timeout if memory else timeout,
                        max_nodes=max_nodes, measure_memory=memory)
        return result, verify(problem, result)

    run()  # warm-up, excluded from the samples
    samples = [run() for _ in range(repeat)]
    measured, memory_verified = run(memory=True)
    runs = [r for r, _ in samples]
    durations = [r["metrics"]["elapsed_ms"] for r in runs]
    first = runs[0]["metrics"]
    return {"level": level["id"], "game": level["game"],
            "rows": level["rows"], "cols": level["cols"],
            "algorithm": algorithm, "statuses": [r["status"] for r in runs],
            "solved_runs": sum(r["status"] == "solved" for r in runs),
            "solutions_verified": all(valid for r, valid in samples if r["status"] == "solved")
                                  if any(r["status"] == "solved" for r in runs) else None,
            "median_ms": statistics.median(durations), "min_ms": min(durations),
            "max_ms": max(durations), "runs_ms": durations,
            "expanded": first["expanded"], "generated": first["generated"],
            "pruned": first["pruned"], "frontier_peak": first["frontier_peak"],
            "runs_metrics": [r["metrics"] for r in runs],
            "memory_status": measured["status"], "memory_solution_verified": memory_verified,
            "memory_expanded": measured["metrics"]["expanded"],
            "peak_python_kib": measured["metrics"]["peak_kib"]}


def revision():
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                text=True, timeout=5, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                                    text=True, timeout=5, check=True).stdout.strip())
        return {"commit": commit, "dirty": dirty}
    except (OSError, subprocess.SubprocessError):
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=5)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--suite", choices=("playable", "extended"), default="playable")
    source.add_argument("--input", help="JSON input set; same format as python -m logic_lab --input.")
    parser.add_argument("--timeout", type=float, default=4.0)
    parser.add_argument("--memory-timeout", type=float, default=30.0,
                        help="Separate budget because tracemalloc slows execution.")
    parser.add_argument("--max-nodes", type=int, default=100000)
    parser.add_argument("--output", default="results/benchmark.json")
    args = parser.parse_args(argv)
    if args.repeat < 1 or args.max_nodes < 1:
        parser.error("--repeat and --max-nodes must be at least 1")
    if any(not math.isfinite(v) or v <= 0 for v in (args.timeout, args.memory_timeout)):
        parser.error("Timeouts must be finite and positive")
    try:
        levels = load_levels(args.input) if args.input else suite_levels(args.suite)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    records = []
    for level in levels:
        for algorithm in ("dfs", "greedy"):
            record = run_case(level, algorithm, args.repeat, args.timeout,
                              args.max_nodes, args.memory_timeout)
            records.append(record)
            print(f"{level['id']:<25} {algorithm:<6} {record['solved_runs']}/{args.repeat} solved; "
                  f"{record['median_ms']:.3f} ms; {record['peak_python_kib']:.2f} KiB", flush=True)
    manifest = json.dumps(levels, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    code_files = [Path(__file__).resolve(), *sorted(Path(__file__).resolve().parent.joinpath("logic_lab").rglob("*.py"))]
    code_hash = hashlib.sha256()
    for file in code_files:
        code_hash.update(file.name.encode())
        code_hash.update(file.read_bytes())
    payload = {"schema_version": 2, "created_utc": datetime.now(timezone.utc).isoformat(),
               "python": platform.python_version(), "platform": platform.platform(),
               "processor": platform.processor(), "git": revision(),
               "source_sha256": code_hash.hexdigest(), "repeat": args.repeat,
               "suite": "custom" if args.input else args.suite,
               "limits": {"timeout_seconds": args.timeout, "max_nodes": args.max_nodes,
                          "memory_timeout_seconds": args.memory_timeout},
               "scope": "search only, no construction/UI/HTTP/trace; isolated peak Python allocations, not RSS",
               "inputs_sha256": hashlib.sha256(manifest.encode("utf-8")).hexdigest(),
               "inputs": levels, "results": records}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    columns = ["level", "game", "rows", "cols", "algorithm", "solved_runs", "median_ms", "min_ms",
               "max_ms", "expanded", "generated", "pruned", "frontier_peak", "memory_status", "peak_python_kib"]
    with output.with_suffix(".csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print(f"Saved {len(records)} records: {output} and {output.with_suffix('.csv')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

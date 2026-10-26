"""Solve a bundled or custom input without a running web server."""
import argparse
import json
from pathlib import Path

from .inputs import load_levels, make_problem
from .levels import BY_ID, public_levels
from .search import search


def main(argv=None):
    parser = argparse.ArgumentParser(description="Giải Pipes / Light Up bằng Python 3.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--level", choices=tuple(BY_ID))
    source.add_argument("--input", help="Tệp JSON chứa một bài toán hoặc danh sách bài toán.")
    source.add_argument("--list", action="store_true", help="Xuất các màn gốc dưới dạng JSON.")
    parser.add_argument("--algorithm", choices=("dfs", "greedy"), default="greedy")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--max-nodes", type=int, default=100000)
    parser.add_argument("--trace", type=int, default=0, metavar="COUNT")
    parser.add_argument("--output", help="Ghi JSON kết quả ra tệp.")
    args = parser.parse_args(argv)
    try:
        if args.list:
            result, exit_code = public_levels(), 0
        else:
            levels = load_levels(args.input) if args.input else [BY_ID[args.level]]
            result = []
            for level in levels:
                problem = make_problem(level)
                answer = search(problem, args.algorithm, timeout=args.timeout,
                                max_nodes=args.max_nodes, trace_limit=args.trace)
                if answer["status"] == "solved":
                    solution = answer["solution"]
                    checked = (problem.check(solution["tiles"]) if level["game"] == "pipes"
                               else problem.check(solution["bulbs"]))
                    if not checked["solved"]:
                        raise RuntimeError("Solver trả về lời giải không hợp lệ.")
                result.append({"level": level["id"], "algorithm": args.algorithm, **answer})
            exit_code = 2 if any(r["status"] == "limit" for r in result) else 0
        raw = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            target = Path(args.output)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(raw, encoding="utf-8")
        else:
            print(raw, end="")
        return exit_code
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())

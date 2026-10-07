"""Shared DFS / Greedy Best-First engine. No third-party dependencies."""
from dataclasses import dataclass, asdict
import heapq
import itertools
import time
import tracemalloc


@dataclass
class Metrics:
    expanded: int = 0
    generated: int = 1
    pruned: int = 0
    frontier_peak: int = 1
    elapsed_ms: float = 0
    peak_kib: float | None = None


def search(problem, algorithm="greedy", timeout=4.0, max_nodes=100000,
           trace_limit=0, measure_memory=False):
    """Only EXHAUSTED proves UNSAT; a budget limit is always UNKNOWN.

    Both algorithms share successor order and feasibility pruning. DFS uses
    a stack, never the heuristic to select its next state. Greedy uses h only.
    Fixed-order variable assignment makes the search space a tree.
    Memory measurement is opt-in for single-process benchmarks, not HTTP.
    """
    if algorithm not in ("dfs", "greedy"):
        raise ValueError("Thuật toán phải là dfs hoặc greedy.")
    started = time.perf_counter()
    if measure_memory:
        tracemalloc.start()
    metrics = Metrics()
    trace = []
    sequence = itertools.count()
    frontier = []
    status, solution = "unsat", None

    def push(state, domains):
        if algorithm == "dfs":
            frontier.append((state, domains))
        else:
            heapq.heappush(frontier, (problem.heuristic(state, domains),
                                     next(sequence), state, domains))

    try:
        root = problem.initial
        domains = problem.analyze(root)
        if domains is not None:
            push(root, domains)
        else:
            metrics.pruned += 1
        while frontier:
            if metrics.expanded >= max_nodes or time.perf_counter() - started >= timeout:
                status = "limit"
                break
            if algorithm == "dfs":
                state, domains = frontier.pop()
            else:
                _, _, state, domains = heapq.heappop(frontier)
            metrics.expanded += 1
            if len(trace) < trace_limit:
                trace.append({"state": problem.present(state),
                              "h": round(problem.heuristic(state, domains), 2),
                              "expanded": metrics.expanded,
                              "frontier": len(frontier)})
            if problem.goal(state):
                status, solution = "solved", problem.present_solution(state)
                break
            children = list(problem.successors(state, domains))
            # Preserve the same logical child order under LIFO.
            if algorithm == "dfs":
                children.reverse()
            for child in children:
                metrics.generated += 1
                child_domains = problem.analyze(child)
                if child_domains is None:
                    metrics.pruned += 1
                else:
                    push(child, child_domains)
            metrics.frontier_peak = max(metrics.frontier_peak, len(frontier))
    finally:
        metrics.elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        if measure_memory:
            _, peak = tracemalloc.get_traced_memory()
            metrics.peak_kib = round(peak / 1024, 2)
            tracemalloc.stop()
    return {"status": status, "solution": solution, "metrics": asdict(metrics),
            "trace": trace, "trace_truncated": metrics.expanded > len(trace) if trace_limit else False}

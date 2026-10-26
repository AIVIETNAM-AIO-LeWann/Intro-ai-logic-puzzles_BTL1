"""Search policy, resource budgets and metrics, independent of game heuristics."""
import math
import tracemalloc
import unittest

from logic_lab.search import search


class Tree:
    initial = "root"
    branches = {"root": ("a", "b"), "a": ("dead", "answer"), "b": ("answer-b",)}

    def analyze(self, state):
        return None if state == "dead" else ()

    def goal(self, state):
        return state.startswith("answer")

    def successors(self, state, _domains):
        return iter(self.branches.get(state, ()))

    def heuristic(self, state, _domains):
        return {"root": 3, "a": 10, "b": 1}.get(state, 0)

    def present(self, state):
        return state

    present_solution = present


class SearchContractTests(unittest.TestCase):
    def test_dfs_uses_child_order_and_never_calls_heuristic_without_trace(self):
        problem = Tree()
        problem.heuristic = lambda *_: self.fail("DFS must not use h to select states")
        result = search(problem, "dfs")
        self.assertEqual(result["solution"], "answer")
        self.assertEqual(result["metrics"]["expanded"], 3)
        self.assertEqual(result["metrics"]["generated"], 5)
        self.assertEqual(result["metrics"]["pruned"], 1)
        self.assertEqual(result["metrics"]["frontier_peak"], 2)

    def test_greedy_uses_h_and_trace_is_expansion_order(self):
        result = search(Tree(), "greedy", trace_limit=10)
        self.assertEqual([row["state"] for row in result["trace"]], ["root", "b", "answer-b"])
        self.assertFalse(result["trace_truncated"])

    def test_equal_greedy_scores_keep_insertion_order(self):
        problem = Tree()
        problem.heuristic = lambda *_: 0
        result = search(problem, "greedy", trace_limit=10)
        self.assertEqual([row["state"] for row in result["trace"]], ["root", "a", "b", "answer"])

    def test_trace_cap_keeps_final_solution_separate(self):
        result = search(Tree(), "dfs", trace_limit=1)
        self.assertEqual(len(result["trace"]), 1)
        self.assertTrue(result["trace_truncated"])
        self.assertEqual(result["solution"], "answer")

    def test_infeasible_root_has_no_frontier(self):
        problem = Tree()
        problem.analyze = lambda _: None
        result = search(problem)
        self.assertEqual(result["status"], "unsat")
        self.assertEqual(result["metrics"]["frontier_peak"], 0)
        self.assertEqual(result["metrics"]["pruned"], 1)
        self.assertEqual(result["metrics"]["expanded"], 0)

    def test_exhaustion_and_budget_limits_are_distinct(self):
        problem = Tree()
        problem.goal = lambda _: False
        for algorithm in ("dfs", "greedy"):
            self.assertEqual(search(problem, algorithm)["status"], "unsat")
            for limits in ({"max_nodes": 1}, {"timeout": 0}):
                result = search(problem, algorithm, **limits)
                self.assertEqual(result["status"], "limit")
                self.assertIsNone(result["solution"])

    def test_invalid_budgets_fail_before_search(self):
        for args in ({"timeout": math.nan}, {"timeout": math.inf}, {"timeout": -1},
                     {"max_nodes": True}, {"max_nodes": -1}, {"trace_limit": 1.5}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                search(Tree(), **args)

    def test_memory_trace_is_cleaned_up_even_on_exception(self):
        problem = Tree()
        def broken(_):
            raise RuntimeError("failure")
        problem.analyze = broken
        with self.assertRaises(RuntimeError):
            search(problem, measure_memory=True)
        self.assertFalse(tracemalloc.is_tracing())

    def test_memory_measurement_preserves_an_existing_profiler(self):
        tracemalloc.start()
        try:
            with self.assertRaises(ValueError):
                search(Tree(), measure_memory=True)
            self.assertTrue(tracemalloc.is_tracing())
        finally:
            tracemalloc.stop()

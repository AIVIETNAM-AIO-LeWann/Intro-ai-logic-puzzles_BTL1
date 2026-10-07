"""Rule and search regression tests, including independent exhaustive oracles."""
import itertools
import random
import unittest
from unittest.mock import patch

from logic_lab.levels import LEVELS, BY_ID, make_pipes
from logic_lab.games.pipes import Pipes, orientations, rotate
from logic_lab.games.lightup import LightUp
from logic_lab.search import search
from logic_lab import service


def valid_pipes(level, tiles):
    """Independent complete-board oracle: reciprocal edges + spanning tree."""
    rows, cols = level["rows"], level["cols"]
    edges = set()
    for i, mask in enumerate(tiles):
        r, c = divmod(i, cols)
        for dr, dc, bit, back in ((-1, 0, 1, 4), (0, 1, 2, 8), (1, 0, 4, 1), (0, -1, 8, 2)):
            if not mask & bit:
                continue
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                return False
            j = nr * cols + nc
            if not tiles[j] & back:
                return False
            edges.add(tuple(sorted((i, j))))
    reached = {0}
    for _ in tiles:
        for a, b in edges:
            if a in reached or b in reached:
                reached.update((a, b))
    return len(reached) == len(tiles) and len(edges) == len(tiles) - 1


def valid_akari(board, bulbs):
    rows, cols = len(board), len(board[0])
    lit = set(bulbs)
    for i in bulbs:
        r, c = divmod(i, cols)
        if board[r][c] != ".":
            return False
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            while 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == ".":
                j = nr * cols + nc
                if j in bulbs:
                    return False
                lit.add(j)
                nr += dr
                nc += dc
    for r in range(rows):
        for c in range(cols):
            value = board[r][c]
            if value == "." and r * cols + c not in lit:
                return False
            if value.isdigit():
                count = sum((r + dr) * cols + c + dc in bulbs
                            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
                            if 0 <= r + dr < rows and 0 <= c + dc < cols)
                if count != int(value):
                    return False
    return True


class RuleTests(unittest.TestCase):
    def test_rotations_preserve_shape(self):
        for mask in range(1, 16):
            value = mask
            for _ in range(4):
                value = rotate(value)
            self.assertEqual(mask, value)
        self.assertEqual(len(orientations(5)), 2)

    def test_pipes_cycle_and_disconnected_are_not_wins(self):
        for tiles in ([6, 12, 3, 9], [2, 8, 2, 8]):
            level = {"rows": 2, "cols": 2, "tiles": tiles}
            self.assertFalse(Pipes(level).check(tiles)["solved"])
        tree = {"rows": 2, "cols": 2, "tiles": [2, 12, 2, 9]}
        self.assertTrue(Pipes(tree).check(tree["tiles"])["solved"])

    def test_lightup_accepts_multiple_solutions(self):
        p = LightUp(BY_ID["lightup-3"])
        self.assertTrue(p.check([0, 8])["solved"])
        self.assertTrue(p.check([2, 6])["solved"])
        self.assertFalse(p.check([0, 2])["solved"])
        self.assertFalse(p.check([1, 8])["solved"])

    def test_black_wall_blocks_light(self):
        p = LightUp({"board": [".#."]})
        self.assertTrue(p.check([0, 2])["solved"])
        self.assertEqual(p.check([0])["lit"], [0])

    def test_zero_wall_and_crosses_can_make_unsat(self):
        self.assertEqual(search(LightUp(BY_ID["lightup-3"], bulbs=[1]))["status"], "unsat")
        self.assertEqual(search(LightUp(BY_ID["lightup-3"], crosses=[0, 2, 6, 8]))["status"], "unsat")


class SearchTests(unittest.TestCase):
    def test_all_levels_both_algorithms_have_valid_solutions(self):
        for level in LEVELS:
            for algorithm in ("dfs", "greedy"):
                with self.subTest(level=level["id"], algorithm=algorithm):
                    problem = Pipes(level) if level["game"] == "pipes" else LightUp(level)
                    result = search(problem, algorithm, timeout=2, trace_limit=5)
                    self.assertEqual(result["status"], "solved")
                    answer = result["solution"]
                    valid = valid_pipes(level, answer["tiles"]) if level["game"] == "pipes" else valid_akari(level["board"], set(answer["bulbs"]))
                    self.assertTrue(valid)
                    self.assertLessEqual(len(result["trace"]), 5)

    def test_limits_never_claim_unsat(self):
        for algorithm in ("dfs", "greedy"):
            result = search(LightUp(BY_ID["lightup-3"]), algorithm, max_nodes=0)
            self.assertEqual(result["status"], "limit")
            self.assertIsNone(result["solution"])

    def test_pipes_against_exhaustive_oracle(self):
        rng = random.Random(99)
        for seed in range(5):
            level = make_pipes(2, seed, "", "", "")
            all_boards = list(itertools.product(*(orientations(v) for v in level["tiles"])))
            solutions = [t for t in all_boards if valid_pipes(level, t)]
            for _ in range(20):
                current = rng.choice(all_boards)
                fixed = [i for i in range(4) if rng.random() < .6]
                expected = any(all(t[i] == current[i] for i in fixed) for t in solutions)
                for algorithm in ("dfs", "greedy"):
                    actual = search(Pipes(level, current, fixed), algorithm)
                    self.assertEqual(actual["status"] == "solved", expected)

    def test_akari_against_exhaustive_oracle(self):
        rng = random.Random(73)
        for board in (["...", ".0.", "..."], ["...", ".2.", "..."], [".#.", "...", ".#."]):
            cells = [r * 3 + c for r, row in enumerate(board) for c, value in enumerate(row) if value == "."]
            solutions = []
            for bits in itertools.product((0, 1), repeat=len(cells)):
                bulbs = {c for c, bit in zip(cells, bits) if bit}
                if valid_akari(board, bulbs):
                    solutions.append(bulbs)
            for _ in range(60):
                choices = [rng.choice((-1, -1, 0, 1)) for _ in cells]
                lamps = {c for c, value in zip(cells, choices) if value == 1}
                crosses = {c for c, value in zip(cells, choices) if value == 0}
                expected = any(lamps <= answer and not crosses & answer for answer in solutions)
                for algorithm in ("dfs", "greedy"):
                    result = search(LightUp({"board": board}, lamps, crosses), algorithm)
                    self.assertEqual(result["status"] == "solved", expected)


class HintTests(unittest.TestCase):
    def test_hint_preserves_player_bulb(self):
        result = service.hint({"level": "lightup-3", "state": {"bulbs": [0], "crosses": []}})
        self.assertEqual(result["status"], "hint")
        self.assertEqual(result["action"], {"kind": "add_bulb", "cell": 8})

    def test_hint_preserves_alternative_solution(self):
        result = service.hint({"level": "lightup-3", "state": {"bulbs": [2]}})
        self.assertEqual(result["action"], {"kind": "add_bulb", "cell": 6})

    def test_wrong_bulb_gets_explicit_repair(self):
        result = service.hint({"level": "lightup-3", "state": {"bulbs": [1]}})
        self.assertEqual(result["status"], "repair")
        self.assertEqual(result["action"], {"kind": "remove_bulb", "cell": 1})

    def test_wrong_crosses_get_repair(self):
        result = service.hint({"level": "lightup-3", "state": {"crosses": [0, 2, 6, 8]}})
        self.assertEqual(result["status"], "repair")
        self.assertEqual(result["action"]["kind"], "remove_cross")

    def test_pipes_fixed_wrong_orientation_gets_repair(self):
        level = BY_ID["pipes-3"]
        current = level["_witness"]["tiles"][:]
        current[0] = next(v for v in orientations(current[0]) if v not in Pipes(level).options[0])
        result = service.hint({"level": level["id"], "state": {"tiles": current, "fixed": [0]}})
        self.assertEqual(result["status"], "repair")
        self.assertEqual(result["action"]["cell"], 0)

    def test_hint_limit_is_not_misrepresented(self):
        with patch("logic_lab.service.search", return_value={"status": "limit", "metrics": {}}):
            result = service.hint({"level": "lightup-3", "state": {}})
            self.assertEqual(result["status"], "limit")
            self.assertNotIn("action", result)

    def test_complete_board_needs_no_hint(self):
        self.assertEqual(service.hint({"level": "lightup-3", "state": {"bulbs": [2, 6]}})["status"], "complete")

    def test_hint_actions_eventually_solve_every_level(self):
        for level in LEVELS:
            state = {"tiles": level.get("tiles", [])[:], "fixed": []} if level["game"] == "pipes" else {"bulbs": [], "crosses": []}
            for _ in range(level["rows"] * level["cols"] + 1):
                data = {"level": level["id"], "state": state}
                if service.check(data)["solved"]:
                    break
                result = service.hint(data)
                self.assertEqual(result["status"], "hint")
                action = result["action"]
                if level["game"] == "pipes":
                    state["tiles"][action["cell"]] = action["value"]
                    state["fixed"].append(action["cell"])
                else:
                    state["bulbs"].append(action["cell"])
            self.assertTrue(service.check({"level": level["id"], "state": state})["solved"])


if __name__ == "__main__":
    unittest.main()

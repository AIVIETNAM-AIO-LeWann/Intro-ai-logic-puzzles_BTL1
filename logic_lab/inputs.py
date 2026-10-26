"""Validated, portable puzzle inputs for the CLI and reproducible experiments."""
import json
from pathlib import Path

from .games.pipes import Pipes
from .games.lightup import LightUp
from .levels import make_pipes, make_lightup, public_levels


def validate_level(value):
    """Accept JSON puzzle data, without requiring a stored solution or seed.

    Contradictory clues/shapes are valid inputs: the solver must prove UNSAT.
    Structural errors are rejected before constructing a problem.
    """
    if not isinstance(value, dict) or value.get("game") not in ("pipes", "lightup"):
        raise ValueError("game phải là pipes hoặc lightup.")
    rows, cols = value.get("rows"), value.get("cols")
    if any(type(n) is not int or not 1 <= n <= 20 for n in (rows, cols)):
        raise ValueError("rows và cols phải là số nguyên từ 1 đến 20.")
    level = {"game": value["game"], "rows": rows, "cols": cols}
    identifier = value.get("id", "custom")
    if not isinstance(identifier, str) or not identifier.strip() or len(identifier) > 100:
        raise ValueError("id phải là chuỗi không trống, tối đa 100 ký tự.")
    level["id"] = identifier
    if level["game"] == "pipes":
        tiles = value.get("tiles")
        if (not isinstance(tiles, list) or len(tiles) != rows * cols
                or any(type(v) is not int or not 1 <= v <= 15 for v in tiles)):
            raise ValueError("tiles phải có rows × cols số nguyên từ 1 đến 15.")
        level["tiles"] = tiles[:]
    else:
        board = value.get("board")
        if (not isinstance(board, list) or len(board) != rows
                or any(not isinstance(row, str) or len(row) != cols
                       or any(c not in ".#01234" for c in row) for row in board)):
            raise ValueError("board phải có rows dòng, mỗi dòng cols ký tự thuộc .#01234.")
        level["board"] = board[:]
    for key in ("seed", "title", "difficulty", "description"):
        if key in value:
            level[key] = value[key]
    return level


def load_levels(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    values = raw if isinstance(raw, list) else [raw]
    if not values:
        raise ValueError("Tệp input phải chứa ít nhất một bài toán.")
    levels = [validate_level(v) for v in values]
    if len({level["id"] for level in levels}) != len(levels):
        raise ValueError("Các input phải có id khác nhau.")
    return levels


def make_problem(level):
    return Pipes(level) if level["game"] == "pipes" else LightUp(level)


def suite_levels(suite="playable"):
    if suite not in ("playable", "extended"):
        raise ValueError("suite phải là playable hoặc extended.")
    levels = public_levels()
    if suite == "extended":
        # Consecutive seeds and fixed sizes, not selected for a winning algorithm.
        for game, generate in (("pipes", make_pipes), ("lightup", make_lightup)):
            for size in (4, 6, 8):
                for seed in (101, 102, 103):
                    level = generate(size, seed, "Benchmark", "Thực nghiệm", "Input có seed cố định.")
                    level["id"] = f"{game}-{size}-seed-{seed}"
                    levels.append({k: v for k, v in level.items() if not k.startswith("_")})
    return levels

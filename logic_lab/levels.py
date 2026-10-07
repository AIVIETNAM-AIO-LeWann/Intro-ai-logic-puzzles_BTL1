"""Reproducible original inputs, inspired by the official puzzle rules.

Each generated level has a constructive witness. Multiple solutions are
allowed; a player's board is always checked against rules, not a saved answer.
"""
import random
from .games.pipes import DIRS, rotate
from .games.lightup import LightUp


def make_pipes(size, seed, title, difficulty, description):
    rng = random.Random(seed)
    tiles = [0] * (size * size)
    seen, stack = {0}, [0]
    while stack:
        i = stack[-1]
        r, c = divmod(i, size)
        choices = [( (r + dr) * size + c + dc, bit, opposite)
                   for dr, dc, bit, opposite in DIRS
                   if 0 <= r + dr < size and 0 <= c + dc < size
                   and (r + dr) * size + c + dc not in seen]
        if not choices:
            stack.pop()
            continue
        j, bit, opposite = rng.choice(choices)
        tiles[i] |= bit
        tiles[j] |= opposite
        seen.add(j)
        stack.append(j)
    witness = tiles[:]
    for i in range(len(tiles)):
        for _ in range(rng.randrange(4)):
            tiles[i] = rotate(tiles[i])
    if tiles == witness:
        tiles[0] = rotate(tiles[0])
    return {"id": f"pipes-{size}", "game": "pipes", "rows": size, "cols": size,
            "title": title, "difficulty": difficulty, "description": description,
            "tiles": tiles, "seed": seed, "_witness": {"tiles": witness}}


def make_lightup(size, seed, title, difficulty, description):
    rng = random.Random(seed)
    board = [["#" if rng.random() < .24 else "." for _ in range(size)] for _ in range(size)]
    blank = {"board": ["".join(row) for row in board]}
    puzzle = LightUp(blank)
    unlit = set(range(len(puzzle.cells)))
    lamps = set()
    while unlit:
        i = rng.choice(sorted(unlit))
        lamps.add(puzzle.cells[i])
        unlit.difference_update(puzzle.visibility[i])
    for r in range(size):
        for c in range(size):
            if board[r][c] == "#" and rng.random() < .78:
                count = sum((r + dr) * size + c + dc in lamps
                            for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1))
                            if 0 <= r + dr < size and 0 <= c + dc < size)
                board[r][c] = str(count)
    return {"id": f"lightup-{size}", "game": "lightup", "rows": size, "cols": size,
            "title": title, "difficulty": difficulty, "description": description,
            "board": ["".join(row) for row in board], "seed": seed,
            "_witness": {"bulbs": sorted(lamps)}}


LEVELS = [
    make_pipes(3, 11, "Mạch đầu tiên", "Làm quen", "Một bảng nhỏ để làm quen với các góc nối."),
    make_pipes(4, 27, "Những ngã rẽ", "Cơ bản", "Theo dấu đường ống qua những khúc quanh."),
    make_pipes(5, 43, "Mạng lưới xanh", "Thử thách", "Quan sát cả mạng, đừng chỉ nhìn một ô."),
    make_pipes(6, 71, "Kết nối cuối cùng", "Mở rộng", "Một mạng lớn hơn cho buổi thực hành tìm kiếm."),
    {"id": "lightup-3", "game": "lightup", "rows": 3, "cols": 3,
     "title": "Hai đốm sáng", "difficulty": "Làm quen",
     "description": "Bắt đầu từ ví dụ quen thuộc: một ô đen mang số 0.",
     "board": ["...", ".0.", "..."], "_witness": {"bulbs": [0, 8]}},
    make_lightup(5, 19, "Góc nắng", "Cơ bản", "Ô đen chặn sáng, những con số chỉ đường."),
    make_lightup(6, 31, "Ánh sáng giao nhau", "Thử thách", "Hai tia sáng được giao nhau, hai đèn thì không."),
    make_lightup(7, 57, "Thắp sáng khu vườn", "Mở rộng", "Kết hợp vùng sáng và các ràng buộc quanh ô đen."),
]
BY_ID = {level["id"]: level for level in LEVELS}


def public_levels():
    return [{k: v for k, v in level.items() if not k.startswith("_")} for level in LEVELS]

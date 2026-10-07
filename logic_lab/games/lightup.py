"""Akari with numbered walls, player bulbs and explicit no-bulb marks."""


class LightUp:
    def __init__(self, level, bulbs=None, crosses=None):
        self.board = level["board"]
        self.rows, self.cols = len(self.board), len(self.board[0])
        self.cells = tuple(r * self.cols + c for r, row in enumerate(self.board)
                           for c, value in enumerate(row) if value == ".")
        self.index = {cell: i for i, cell in enumerate(self.cells)}
        self.visibility = []
        for cell in self.cells:
            r, c = divmod(cell, self.cols)
            visible = {self.index[cell]}
            for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                nr, nc = r + dr, c + dc
                while 0 <= nr < self.rows and 0 <= nc < self.cols and self.board[nr][nc] == ".":
                    visible.add(self.index[nr * self.cols + nc])
                    nr, nc = nr + dr, nc + dc
            self.visibility.append(frozenset(visible))
        self.clues = []
        for r, row in enumerate(self.board):
            for c, value in enumerate(row):
                if value.isdigit():
                    adjacent = []
                    for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and nr * self.cols + nc in self.index:
                            adjacent.append(self.index[nr * self.cols + nc])
                    self.clues.append((r * self.cols + c, int(value), tuple(adjacent)))
        bulbs, crosses = set(bulbs or []), set(crosses or [])
        if bulbs & crosses or any(type(c) is not int or c not in self.index for c in bulbs | crosses):
            raise ValueError("Đèn và dấu X phải nằm ở ô trắng và không trùng nhau.")
        self.initial = tuple(1 if c in bulbs else 0 if c in crosses else -1 for c in self.cells)

    def info(self, state):
        bulbs = {i for i, v in enumerate(state) if v == 1}
        lit = set().union(*(self.visibility[i] for i in bulbs)) if bulbs else set()
        return bulbs, lit

    def analyze(self, state):
        bulbs, lit = self.info(state)
        if any((self.visibility[i] - {i}) & bulbs for i in bulbs):
            return None
        candidates = {i for i, v in enumerate(state) if v == -1 and i not in lit}
        # A satisfied numbered wall forbids any additional adjacent bulb.
        for _, target, adjacent in self.clues:
            count = sum(i in bulbs for i in adjacent)
            if count > target:
                return None
            if count == target:
                candidates.difference_update(adjacent)
        for _, target, adjacent in self.clues:
            count = sum(i in bulbs for i in adjacent)
            if count + sum(i in candidates for i in adjacent) < target:
                return None
        for i in range(len(state)):
            if i not in lit and not self.visibility[i] & candidates:
                return None
        return candidates

    def goal(self, state):
        bulbs, lit = self.info(state)
        return len(lit) == len(state) and all(sum(i in bulbs for i in adj) == k for _, k, adj in self.clues)

    def successors(self, state, candidates):
        i = state.index(-1)
        # Fixed order shared by both algorithms; no MRV in the DFS baseline.
        for value in ((0, 1) if i in candidates else (0,)):
            yield state[:i] + (value,) + state[i + 1:]

    def heuristic(self, state, candidates):
        bulbs, lit = self.info(state)
        deficit = sum(k - sum(i in bulbs for i in adj) for _, k, adj in self.clues)
        return len(state) - len(lit) + deficit

    def present(self, state):
        return {"bulbs": [self.cells[i] for i, v in enumerate(state) if v == 1],
                "crosses": [self.cells[i] for i, v in enumerate(state) if v == 0]}

    def present_solution(self, state):
        return {"bulbs": [self.cells[i] for i, v in enumerate(state) if v == 1]}

    def check(self, bulbs, crosses=None):
        chosen = {self.index[c] for c in bulbs}
        lit = set().union(*(self.visibility[i] for i in chosen)) if chosen else set()
        conflicts = set()
        for i in chosen:
            if (self.visibility[i] - {i}) & chosen:
                conflicts.update(self.cells[j] for j in self.visibility[i] & chosen)
        clues = []
        for cell, target, adjacent in self.clues:
            count = sum(i in chosen for i in adjacent)
            clues.append({"cell": cell, "target": target, "count": count,
                          "status": "over" if count > target else "met" if count == target else "open"})
            if count > target:
                conflicts.update(self.cells[i] for i in adjacent if i in chosen)
        return {"solved": len(lit) == len(self.cells) and not conflicts and all(c["status"] == "met" for c in clues),
                "lit": sorted(self.cells[i] for i in lit), "errors": sorted(conflicts),
                "clues": clues, "lit_count": len(lit), "white_count": len(self.cells)}

"""Non-wrapping Pipes. N/E/S/W are the bits 1/2/4/8.

Search assigns final orientations in row-major order, with sound constraint
pruning shared by DFS and Greedy. Player-edited cells become fixed inputs.
"""
DIRS = ((-1, 0, 1, 4), (0, 1, 2, 8), (1, 0, 4, 1), (0, -1, 8, 2))


def rotate(mask):
    return ((mask << 1) & 15) | (mask >> 3)


def orientations(mask):
    values = []
    for _ in range(4):
        if mask not in values:
            values.append(mask)
        mask = rotate(mask)
    return tuple(values)


class Pipes:
    def __init__(self, level, current=None, fixed=None):
        self.rows, self.cols = level["rows"], level["cols"]
        self.tiles = tuple(level["tiles"])
        self.count = self.rows * self.cols
        current = self.tiles if current is None else tuple(current)
        if len(current) != self.count:
            raise ValueError("Số ô Pipes không đúng.")
        self.neighbors = []
        self.options = []
        for i, mask in enumerate(self.tiles):
            if type(current[i]) is not int or current[i] not in orientations(mask):
                raise ValueError("Loại ống không khớp với màn chơi.")
            r, c = divmod(i, self.cols)
            neighbors, forbidden = [], 0
            for dr, dc, bit, opposite in DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    neighbors.append((nr * self.cols + nc, bit, opposite))
                else:
                    forbidden |= bit
            self.neighbors.append(neighbors)
            self.options.append(tuple(v for v in orientations(mask) if not v & forbidden))
        fixed = set() if fixed is None else set(fixed)
        if any(type(i) is not int or i < 0 or i >= self.count for i in fixed):
            raise ValueError("Vị trí ô đã chỉnh không hợp lệ.")
        self.initial = tuple(current[i] if i in fixed else 0 for i in range(self.count))

    def analyze(self, state):
        domains = [(v,) if v else self.options[i] for i, v in enumerate(state)]
        if any(v and v not in self.options[i] for i, v in enumerate(state)):
            return None
        # Forward checking against assigned neighbors, shared by both
        # algorithms. Do not pre-solve the board with full arc consistency.
        for i in range(self.count):
            allowed = tuple(v for v in domains[i] if all(
                bool(v & bit) == bool(state[j] & opposite)
                for j, bit, opposite in self.neighbors[i] if state[j]))
            if not allowed:
                return None
            domains[i] = allowed
        # Reject a cycle among already assigned, mutually matched edges.
        parents = list(range(self.count))
        def find(i):
            while i != parents[i]:
                parents[i] = parents[parents[i]]
                i = parents[i]
            return i
        for i, v in enumerate(state):
            if not v:
                continue
            for j, bit, opposite in self.neighbors[i]:
                if j > i and state[j] and v & bit and state[j] & opposite:
                    a, b = find(i), find(j)
                    if a == b:
                        return None
                    parents[a] = b
        # The graph of all still possible edges must be connected.
        seen, stack = {0}, [0]
        while stack:
            i = stack.pop()
            for j, bit, opposite in self.neighbors[i]:
                if j not in seen and any(v & bit for v in domains[i]) and any(v & opposite for v in domains[j]):
                    seen.add(j)
                    stack.append(j)
        return domains if len(seen) == self.count else None

    def goal(self, state):
        return all(state) and self.check(state)["solved"]

    def successors(self, state, domains):
        i = state.index(0)
        for value in domains[i]:
            yield state[:i] + (value,) + state[i + 1:]

    def heuristic(self, state, domains):
        # Greedy uncertainty score, not an admissible A* cost bound.
        return sum(1 + .25 * (len(domains[i]) - 1) for i, v in enumerate(state) if not v)

    def present(self, state):
        return {"tiles": list(state)}

    present_solution = present

    def check(self, tiles):
        errors = set()
        links = [[] for _ in tiles]
        edge_count = 0
        for i, value in enumerate(tiles):
            if value not in self.options[i]:
                errors.add(i)
            for j, bit, opposite in self.neighbors[i]:
                if bool(value & bit) != bool(tiles[j] & opposite):
                    errors.update((i, j))
                elif value & bit:
                    links[i].append(j)
                    if j > i:
                        edge_count += 1
        seen, components = set(), 0
        for root in range(self.count):
            if root in seen:
                continue
            components += 1
            stack = [root]
            seen.add(root)
            while stack:
                for j in links[stack.pop()]:
                    if j not in seen:
                        seen.add(j)
                        stack.append(j)
        cycles = edge_count - self.count + components
        return {"solved": not errors and components == 1 and cycles == 0,
                "errors": sorted(errors), "components": components,
                "cycles": cycles, "connected_edges": edge_count,
                "total_edges": self.count - 1}

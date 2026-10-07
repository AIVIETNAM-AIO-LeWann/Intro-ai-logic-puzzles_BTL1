"""Emit deterministic cases to compare JavaScript feedback with Python rules."""
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from logic_lab.levels import public_levels
from logic_lab.games.pipes import Pipes, orientations
from logic_lab.games.lightup import LightUp

rng = random.Random(28)
cases = []
for level in public_levels():
    for _ in range(100):
        if level["game"] == "pipes":
            state = {"tiles": [rng.choice(orientations(t)) for t in level["tiles"]], "fixed": []}
            result = Pipes(level).check(state["tiles"])
        else:
            puzzle = LightUp(level)
            bulbs = [c for c in puzzle.cells if rng.random() < .2]
            state = {"bulbs": bulbs, "crosses": []}
            result = puzzle.check(bulbs)
        cases.append({"level": level, "state": state, "result": result})
print(json.dumps(cases))

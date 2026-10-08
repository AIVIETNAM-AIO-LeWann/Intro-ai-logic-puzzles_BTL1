"""Player journeys: arbitrary mistakes, hints, repair and real HTTP transport."""
import copy
import json
import random
import re
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

from app import Handler
from logic_lab import service
from logic_lab.levels import LEVELS
from logic_lab.games.pipes import orientations


class GameplayTests(unittest.TestCase):
    def test_hints_recover_from_random_player_mistakes(self):
        rng = random.Random(20261008)
        for level in LEVELS:
            for algorithm in ('dfs', 'greedy'):
                for sample in range(3):
                    with self.subTest(level=level['id'], algorithm=algorithm, sample=sample):
                        if level['game'] == 'pipes':
                            state = {'tiles': [rng.choice(orientations(v)) for v in level['tiles']],
                                     'fixed': [i for i in range(len(level['tiles'])) if rng.random() < .6]}
                        else:
                            whites = [r * level['cols'] + c for r, row in enumerate(level['board'])
                                      for c, value in enumerate(row) if value == '.']
                            bulbs = [i for i in whites if rng.random() < .3]
                            state = {'bulbs': bulbs, 'crosses': [i for i in whites if i not in bulbs and rng.random() < .3]}
                        data = {'level': level['id'], 'state': state, 'algorithm': algorithm}
                        original = copy.deepcopy(data)
                        demo = service.solve({**data, 'scope': 'flexible'}, trace=True)
                        self.assertEqual(data, original, 'Viewing a demo must not change player state')
                        self.assertEqual(demo['status'], 'solved')
                        self.assertTrue(service.check({'level': level['id'], 'state': demo['solution']})['solved'])
                        for _ in range(level['rows'] * level['cols'] * 2 + 1):
                            if service.check(data)['solved']:
                                break
                            before_hint = copy.deepcopy(state)
                            hint = service.hint(data)
                            self.assertEqual(state, before_hint)
                            self.assertIn(hint['status'], ('hint', 'repair'))
                            action = hint['action']
                            cell = action['cell']
                            if action['kind'] == 'rotate':
                                state['tiles'][cell] = action['value']
                                if cell not in state['fixed']:
                                    state['fixed'].append(cell)
                            elif action['kind'] == 'add_bulb':
                                state['bulbs'].append(cell)
                            elif action['kind'] == 'remove_bulb':
                                state['bulbs'].remove(cell)
                            else:
                                state['crosses'].remove(cell)
                        self.assertTrue(service.check(data)['solved'], 'Repeated accepted hints must finish the level')


class QuietHandler(Handler):
    def log_message(self, *_args):
        pass


class HttpJourneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def fetch(self, path, data=None):
        raw = json.dumps(data).encode() if data is not None else None
        headers = {'Content-Type': 'application/json', 'Origin': self.base} if raw else {}
        with urlopen(Request(self.base + path, raw, headers), timeout=15) as response:
            self.assertEqual(response.status, 200)
            return response.read()

    def test_page_assets_and_gameplay_over_http(self):
        html = self.fetch('/').decode('utf-8')
        for asset in re.findall(r'(?:href|src)="(/[^\"]+)"', html):
            self.assertTrue(self.fetch(asset), asset)
        levels = json.loads(self.fetch('/api/levels'))
        self.assertEqual(len(levels), 8)
        for level in levels:
            for algorithm in ('dfs', 'greedy'):
                with self.subTest(level=level['id'], algorithm=algorithm):
                    data = {'level': level['id'], 'algorithm': algorithm, 'scope': 'flexible'}
                    result = json.loads(self.fetch('/api/solve', data))
                    self.assertEqual(result['status'], 'solved')
                    solved = {'level': level['id'], 'state': result['solution']}
                    self.assertTrue(json.loads(self.fetch('/api/check', solved))['solved'])
                    self.assertEqual(json.loads(self.fetch('/api/hint', solved))['status'], 'complete')

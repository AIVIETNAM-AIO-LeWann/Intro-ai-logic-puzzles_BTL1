// Optional Node.js check. It tests syntax and rules, not browser layout/events.
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import assert from 'node:assert/strict';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
for (const file of ['api.js', 'board.js', 'app.js', 'pipe-hint.js']) {
  const source = fs.readFileSync(path.join(root, 'web', file), 'utf8');
  new vm.Script(source.replace(/^import .*;\s*$/gm, '').replace(/\bexport\s+(?=(?:async\s+)?function|const|let)/g, ''), { filename: file });
}
const generated = spawnSync('python', ['tests/frontend_cases.py'], { cwd: root, encoding: 'utf8' });
assert.equal(generated.status, 0, generated.stderr || generated.error?.message);
const cases = JSON.parse(generated.stdout);
const source = fs.readFileSync(path.join(root, 'web/board.js'), 'utf8');
const { inspect } = vm.runInNewContext(source.replace(/\bexport\s+/g, '') + '\n({inspect})');
const canonical = value => JSON.stringify(Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, v]) => [key, Array.isArray(v) && v.every(x => typeof x === 'number') ? [...v].sort((a, b) => a - b) : v])));
for (const [i, sample] of cases.entries()) {
  assert.equal(canonical(inspect(sample.level, sample.state)), canonical(sample.result), `Frontend rule mismatch in case ${i}`);
}
console.log(`JavaScript syntax OK; ${cases.length} rule comparisons passed.`);

// Verify demo rotation keyframes for every pipe shape/orientation, without
// requiring a browser. Actual visual rendering still needs manual review.
let reduceMotion = false;
const animationSource = fs.readFileSync(path.join(root, 'web/pipe-hint.js'), 'utf8');
const animationEngine = vm.runInNewContext(
  source.replace(/\bexport\s+/g, '') + '\n' +
  animationSource.replace(/^import .*;\s*$/gm, '').replace(/\bexport\s+/g, '') +
  '\n({animateDemoPipes, rotate})',
  { window: { matchMedia: () => ({ matches: reduceMotion }) } },
);
let animations = [];
const container = { querySelector: () => ({ animate: (frames, options) => animations.push({ frames, options }) }) };
for (let from = 1; from < 16; from++) {
  let to = from;
  for (let step = 1; step <= 3; step++) {
    to = animationEngine.rotate(to);
    animations = [];
    animationEngine.animateDemoPipes(container, [from], [to]);
    if (from === to) { assert.equal(animations.length, 0); continue; }
    assert.equal(animations.length, 1);
    let turns = 0, rotated = from;
    while (rotated !== to) { rotated = animationEngine.rotate(rotated); turns++; }
    assert.equal(animations[0].frames[0].transform, `rotate(${-turns * 90}deg)`);
    assert.equal(animations[0].frames[1].transform, 'rotate(0deg)');
    assert.ok(animations[0].options.duration < 950);
  }
}
reduceMotion = true;
animations = [];
animationEngine.animateDemoPipes(container, [1], [2]);
assert.equal(animations.length, 0);
console.log('Demo rotations and reduced-motion checks passed.');

// Exercise the actual reset/history functions with UI side effects stubbed.
const appSource = fs.readFileSync(path.join(root, 'web/app.js'), 'utf8')
  .replace(/^import .*;\s*$/gm, '').replace(/^init\(\);\s*$/m, '');
const historyContext = vm.createContext({
  document: { getElementById: () => ({ close() {} }) },
});
vm.runInContext(appSource + `
  render = () => {}; renderLevels = () => {}; clearHint = () => {};
  notify = () => {}; save = () => {};
  level = { id: 'lightup-3', game: 'lightup' };
  state = { bulbs: [0, 8], crosses: [] }; moveCount = 2; elapsed = 12;
  completed = new Set(['lightup-3', 'pipes-3']);
`, historyContext);
const historyState = () => JSON.parse(vm.runInContext(
  "JSON.stringify({state, moveCount, elapsed, done: [...completed]})", historyContext));
vm.runInContext('resetPuzzle()', historyContext);
assert.deepEqual(historyState(), { state: { bulbs: [], crosses: [] }, moveCount: 0, elapsed: 0, done: ['pipes-3'] });
vm.runInContext('travel(true)', historyContext);
assert.deepEqual(historyState(), { state: { bulbs: [0, 8], crosses: [] }, moveCount: 2, elapsed: 12, done: ['pipes-3', 'lightup-3'] });
vm.runInContext('travel(false)', historyContext);
assert.deepEqual(historyState(), { state: { bulbs: [], crosses: [] }, moveCount: 0, elapsed: 0, done: ['pipes-3'] });
console.log('Reset, undo and redo completion-state checks passed.');

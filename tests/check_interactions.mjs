// Exercise actual app functions with a minimal DOM double, not a browser.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const read = file => fs.readFileSync(new URL(`../web/${file}`, import.meta.url), 'utf8');
const app = read('app.js').replace(/^import .*;\s*$/gm, '').replace(/^init\(\);\s*$/m, '');
const rules = vm.runInNewContext(read('board.js').replace(/\bexport\s+/g, '') + '\n({inspect,rotate})');
const level = {id: 'lightup-3', game: 'lightup', rows: 3, cols: 3, board: ['...', '.0.', '...'], title: 'Test', difficulty: 'Test'};
function harness() {
  const elements = new Map(), pending = [], messages = [];
  const element = id => {
    if (!elements.has(id)) elements.set(id, {
      textContent: '', innerHTML: '', value: id === 'algorithm' ? 'greedy' : '', open: false,
      style: {}, dataset: {}, listeners: {}, attributes: {},
      classList: {add() {}, remove() {}, toggle() {}},
      setAttribute(name, value) { this.attributes[name] = value; },
      addEventListener(name, fn) { this.listeners[name] = fn; },
      showModal() { this.open = true; },
      close() { this.open = false; this.listeners.close?.(); },
      replaceChildren() {}, querySelector() { return null; },
    });
    return elements.get(id);
  };
  const document = {
    hidden: false, getElementById: element,
    querySelector: selector => selector === 'dialog[open]'
      ? [...elements.values()].find(e => e.open) || null : element(selector),
    querySelectorAll: () => [], addEventListener() {},
  };
  const context = vm.createContext({document, AbortController, ...rules,
    window: {addEventListener() {}}, clearInterval, setInterval: () => 1,
    setTimeout, clearTimeout, clearPipePreview() {}, showPipePreview() {},
    animateAppliedPipe() {}, animateDemoPipes() {},
    drawBoard: (_node, target, state) => rules.inspect(target, state),
    request: (...args) => new Promise((resolve, reject) => pending.push({args, resolve, reject})),
    testLevel: level, report: message => messages.push(message),
  });
  const run = code => vm.runInContext(code, context);
  const json = code => JSON.parse(run(`JSON.stringify(${code})`));
  run(app + `
    renderLevels = () => {}; save = () => {}; notify = report;
    level = testLevel; levels = [testLevel]; state = fresh(level);
    events(); render();
  `);
  return {run, json, element, document, pending, messages};
}

// Clock counts active play only; undo is not a time machine.
{
  const h = harness();
  h.run('tickClock()'); assert.equal(h.run('elapsed'), 0);
  h.run('playCell(0); elapsed = 10; playCell(8)');
  h.run('travel(true); tickClock()'); assert.equal(h.run('elapsed'), 11);
  h.run('travel(false); tickClock()'); assert.equal(h.run('elapsed'), 11); // solved
  h.run('travel(true); resetPuzzle(); tickClock()');
  assert.deepEqual(h.json('[elapsed, started, moveCount]'), [0, false, 0]);
  h.run('travel(true)'); assert.equal(h.run('elapsed'), 11);
  h.document.hidden = true; h.run('tickClock()'); assert.equal(h.run('elapsed'), 11);
  h.document.hidden = false; h.element('rules-dialog').open = true;
  h.run('tickClock()'); assert.equal(h.run('elapsed'), 11);
  h.element('rules-dialog').open = false; h.run('tickClock()'); assert.equal(h.run('elapsed'), 12);
  h.run('selectLevel(level.id)'); assert.equal(h.run('history.length'), 1);
}

// A stale hint success or failure cannot replace a newer hint or release its lock.
for (const rejectOld of [false, true]) {
  const h = harness();
  const first = h.run('getHint()');
  h.run('playCell(0)');
  assert.equal(h.pending[0].args[2].signal.aborted, true);
  assert.equal(h.run('busy'), false);
  const second = h.run('getHint()');
  if (rejectOld) h.pending[0].reject(new Error('old request failed'));
  else h.pending[0].resolve({status: 'hint', message: 'stale', action: {kind: 'add_bulb', cell: 2}});
  await first;
  assert.equal(h.run('busy'), true);
  assert.equal(h.run('currentHint'), null);
  h.pending[1].resolve({status: 'hint', message: 'new', action: {kind: 'add_bulb', cell: 8}});
  await second;
  assert.equal(h.element('coach-message').textContent, 'new');
  assert.equal(h.run('busy'), false);
  h.run('applyHint()'); assert.deepEqual(h.json('state.bulbs'), [0, 8]);
}

// Changing algorithms cancels a pending hint, leaving controls available.
{
  const h = harness(); const job = h.run('getHint()');
  h.element('algorithm').value = 'dfs'; h.element('algorithm').listeners.change();
  assert.equal(h.pending[0].args[2].signal.aborted, true);
  assert.equal(h.run('busy'), false);
  h.pending[0].reject(new Error('cancelled')); await job;
  assert.notEqual(h.element('coach-title').textContent, 'Chưa kết nối được.');
}

// Close/reopen during a solve must not leak the old response into the new demo.
{
  const h = harness(); const before = h.json('state');
  const first = h.run('openDemo()');
  h.element('demo-dialog').close();
  assert.equal(h.pending[0].args[2].signal.aborted, true);
  const second = h.run("openDemo('current')");
  h.pending[0].resolve({status: 'solved'}); await first;
  assert.equal(h.run('demoResult'), null); assert.equal(h.run('busy'), true);
  h.pending[1].resolve({status: 'unsat', trace: [], metrics: {expanded: 0, frontier_peak: 0, elapsed_ms: 1}});
  await second;
  assert.equal(h.run('demoResult.status'), 'unsat');
  assert.equal(h.element('demo-flexible').disabled, false);
  assert.deepEqual(h.json('state'), before);
  assert.equal(h.element('demo-play').disabled, true);
}

// A victory check from before a reset cannot award completion to a new attempt,
// even when the new board happens to have the same solution.
{
  const h = harness();
  h.run('playCell(0); playCell(8)'); assert.equal(h.pending.length, 1);
  h.run('resetPuzzle(); playCell(0); playCell(8)'); assert.equal(h.pending.length, 2);
  h.pending[0].resolve({solved: true}); await new Promise(setImmediate);
  assert.equal(h.run('completed.size'), 0);
  h.pending[1].resolve({solved: true}); await new Promise(setImmediate);
  assert.equal(h.run('completed.has(level.id)'), true);
  assert.equal(h.element('victory-dialog').open, true);
  h.element('victory-dialog').close(); h.run('render()');
  assert.equal(h.pending.length, 2); // No repeated announcement for same board.
}

// A failed victory validation offers a retry without changing the solved board.
{
  const h = harness();
  h.run('playCell(0); playCell(8)');
  h.pending[0].reject(new Error('offline')); await new Promise(setImmediate);
  assert.equal(h.element('retry-win').hidden, false);
  assert.equal(h.run('completed.size'), 0);
  h.element('retry-win').listeners.click();
  assert.equal(h.pending.length, 2);
  assert.equal(h.element('retry-win').hidden, true);
  h.pending[1].resolve({solved: true}); await new Promise(setImmediate);
  assert.equal(h.run('completed.has(level.id)'), true);
  assert.equal(h.element('victory-dialog').open, true);
}

// Victory skips finished levels and stops offering a next level when all are done.
{
  const h = harness();
  h.run(`levels = [level, {...level, id:'second'}, {...level, id:'third'}];
    completed = new Set([level.id, 'second']); showVictory();`);
  let chosen;
  h.run('selectLevel = id => { selectedForTest = id; }');
  h.element('victory-next').onclick(); chosen = h.run('selectedForTest');
  assert.equal(chosen, 'third');
  h.run("completed.add('third'); showVictory()"); assert.equal(h.element('victory-next').hidden, true);
}

// Corrupt stored counters/state recover without negative/NaN clocks.
{
  const h = harness();
  h.run(`level = null; saved = {'lightup-3': {state: {bulbs: [0], crosses: []}, moves: -4, elapsed: 'oops', started: true}};
    selectLevel('lightup-3');`);
  assert.deepEqual(h.json('[state.bulbs, moveCount, elapsed]'), [[0], 0, 0]);
  h.run(`level = null; saved['lightup-3'].state = {bulbs: [4], crosses: []}; selectLevel('lightup-3');`);
  assert.deepEqual(h.json('state'), {bulbs: [], crosses: []});
}

// Transport tests: successful JSON, useful network errors, timeout, caller abort.
const apiSource = read('api.js').replace(/\bexport\s+/g, '') + '\nrequest';
const makeRequest = fetch => vm.runInNewContext(apiSource, {fetch, AbortController, setTimeout, clearTimeout, TypeError});
const ok = makeRequest(async () => ({ok: true, json: async () => ({ok: 1})}));
assert.deepEqual(await ok('/api/levels'), {ok: 1});
await assert.rejects(makeRequest(async () => {throw new TypeError('offline');})('/'), /Không kết nối/);
await assert.rejects(makeRequest(async () => ({ok: false, json: async () => ({error: 'busy'})}))('/'), /busy/);
await assert.rejects(makeRequest(async () => ({ok: true, json: async () => {throw new Error('invalid');}}))('/'), /dữ liệu không hợp lệ/);
const stalled = makeRequest((_path, {signal}) => new Promise((_resolve, reject) => {
  if (signal.aborted) reject(new Error('aborted'));
  signal.addEventListener('abort', () => reject(new Error('aborted')), {once: true});
}));
await assert.rejects(stalled('/', {}, {timeoutMs: 5}), /phản hồi quá lâu/);
const cancel = new AbortController(); const job = stalled('/', {}, {signal: cancel.signal}); cancel.abort();
await assert.rejects(job, /aborted/);
console.log('Gameplay history, clock, stale requests, victory, saved-state and API failure checks passed (DOM doubles; no visual browser coverage).');

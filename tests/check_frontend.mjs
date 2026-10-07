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

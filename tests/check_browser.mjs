// Optional real Chromium coverage. Install Playwright or set PLAYWRIGHT_MODULE.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {spawn} from 'node:child_process';

const require = createRequire(import.meta.url);
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const output = path.resolve(root, process.env.BROWSER_OUTPUT || 'tmp/browser');
await fs.mkdir(output, {recursive: true});
const server = spawn(process.env.PYTHON || 'python', ['-u', 'app.py', '--port', '0'], {
  cwd: root, env: {...process.env, PYTHONUTF8: '1'}, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'],
});
let browser;
try {
  const base = await new Promise((resolve, reject) => {
    let text = '';
    const timer = setTimeout(() => reject(new Error('Local server did not start')), 10000);
    server.once('error', error => {clearTimeout(timer); reject(error);});
    server.once('exit', code => {clearTimeout(timer); reject(new Error(`Server exited: ${code}`));});
    server.stdout.on('data', data => {
      text += data;
      const match = text.match(/http:\/\/127\.0\.0\.1:\d+/);
      if (match) {clearTimeout(timer); resolve(match[0]);}
    });
    server.stderr.on('data', () => {}); // Drain normal HTTP logs.
  });
  browser = await chromium.launch({headless: true,
    ...(process.env.CHROMIUM_EXECUTABLE ? {executablePath: process.env.CHROMIUM_EXECUTABLE} : {})});
  const page = await browser.newPage({viewport: {width: 1440, height: 1000}, reducedMotion: 'reduce'});
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {if (message.type() === 'error') errors.push(message.text());});
  await page.goto(base);
  await page.locator('#board .cell').first().waitFor();
  const levels = await page.evaluate(async () => (await fetch('/api/levels')).json());
  const state = () => page.evaluate(() => {
    const store = JSON.parse(localStorage.getItem('mach.logic-lab.v1'));
    return store.saved[store.selected].state;
  });

  // Native keyboard focus survives rendering; reverse rotation is accessible.
  const initial = await state();
  await page.locator('#board .cell').first().focus();
  await page.keyboard.press('ArrowRight');
  assert.equal(await page.evaluate(() => document.activeElement.dataset.cell), '1');
  await page.keyboard.press('Enter');
  await page.keyboard.press('Shift+Enter');
  assert.deepEqual((await state()).tiles, initial.tiles);
  assert.equal(await page.evaluate(() => document.activeElement.dataset.cell), '1');

  // Both policies run through the real UI, with solution separate from play.
  for (const level of levels) {
    await page.locator(`[data-game="${level.game}"]`).click();
    const index = levels.filter(item => item.game === level.game).findIndex(item => item.id === level.id);
    await page.locator('#level-list button').nth(index).click();
    for (const algorithm of ['dfs', 'greedy']) {
      await page.locator('#algorithm').selectOption(algorithm);
      const before = await state();
      await page.locator('#demo-open').click();
      await page.locator('#demo-solution').waitFor({state: 'visible'});
      await page.locator('#demo-next').click();
      assert.match(await page.locator('#demo-step-label').textContent(), /Trạng thái 2/);
      await page.locator('#demo-prev').click();
      await page.locator('#demo-solution').click();
      assert.equal(await page.locator('#demo-board.solved').count(), 1, `${level.id}/${algorithm}`);
      assert.deepEqual(await state(), before);
      if (level.id === 'pipes-5' && algorithm === 'greedy') {
        await page.screenshot({path: path.join(output, 'demo-desktop.png'), fullPage: true});
        await page.locator('#demo-dialog').screenshot({path: path.join(output, 'demo-panel.png')});
      }
      await page.locator('#demo-dialog .dialog-close').click();
    }
  }

  // Real hints recover a deliberately forbidden Light Up bulb, then finish.
  await page.locator('[data-game="lightup"]').click();
  await page.locator('#level-list button').first().click();
  await page.locator('#board [data-cell="1"]').click();
  await page.locator('#hint-button').click();
  await page.locator('#apply-hint').waitFor({state: 'visible'});
  assert.match(await page.locator('#coach-title').textContent(), /sửa/);
  await page.locator('#apply-hint').click();
  assert.deepEqual((await state()).bulbs, []);
  for (let i = 0; i < 2; i++) {
    await page.locator('#hint-button').click();
    await page.locator('#apply-hint').waitFor({state: 'visible'});
    await page.locator('#apply-hint').click();
  }
  await page.locator('#victory-dialog[open]').waitFor();
  await page.screenshot({path: path.join(output, 'victory-desktop.png'), fullPage: true});
  await page.locator('#victory-stay').click();
  const solvedState = await state();
  await page.reload();
  await page.waitForFunction(() => document.querySelector('#progress-label').textContent.includes('Đã giải đúng'));
  assert.deepEqual(await state(), solvedState);
  assert.equal(await page.locator('#victory-dialog[open]').count(), 0);
  await page.locator('#undo').isDisabled().then(value => assert.equal(value, true));

  // Responsive sizing and native dialogs at narrow and tablet viewports.
  for (const width of [1440, 768, 390, 320]) {
    await page.setViewportSize({width, height: width > 1000 ? 1000 : 844});
    for (const game of ['pipes', 'lightup']) {
      await page.locator(`[data-game="${game}"]`).click();
      await page.locator('#level-list button').last().click();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
      assert.equal(overflow, false, `${game} horizontal overflow at ${width}`);
      await page.screenshot({path: path.join(output, `${game}-${width}.png`), fullPage: true});
      if (width === 1440) await page.locator('.play-card').screenshot({path: path.join(output, `${game}-board.png`)});
      await page.locator('#rules-open').click();
      assert.equal(await page.locator('#rules-dialog[open]').count(), 1);
      await page.keyboard.press('Escape');
      await page.locator('#demo-open').click();
      await page.locator('#demo-solution').waitFor({state: 'visible'});
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
      await page.screenshot({path: path.join(output, `demo-${game}-${width}.png`), fullPage: true});
      await page.locator('#demo-solution').scrollIntoViewIfNeeded();
      const control = await page.locator('#demo-solution').boundingBox();
      assert.ok(control.y >= 0 && control.y + control.height <= page.viewportSize().height,
        `Dialog controls must be reachable at ${width}`);
      await page.keyboard.press('Escape');
    }
  }
  assert.deepEqual(errors, [], 'Browser console / uncaught errors');
  console.log('Chromium passed: 16 demos, keyboard, repair/hints/victory, persistence, 4 viewport sizes; no console errors.');
  console.log(`Screenshots: ${output}`);
} finally {
  await browser?.close();
  server.kill();
}

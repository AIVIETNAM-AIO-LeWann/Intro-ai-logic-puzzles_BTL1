import { request } from './api.js';
import { drawBoard, inspect, rotate } from './board.js';
import { clearPipePreview, showPipePreview, animateAppliedPipe, animateDemoPipes } from './pipe-hint.js';

const $ = id => document.getElementById(id);
const clone = value => JSON.parse(JSON.stringify(value));
const STORE = 'mach.logic-lab.v1';
let levels = [], level, state, history = [], future = [], moveCount = 0, elapsed = 0, started = false;
let currentHint = null, revision = 0, busy = false, tool = 'bulb', completed = new Set(), saved = {};
let demoResult = null, demoIndex = 0, demoTimer = null, toastTimer = null, solved = false;
let announcedWin = null, pendingWin = null;
let demoVisibleTiles = null;

function winningBoardKey() { return JSON.stringify([level.id, state]); }

function showVictory() {
  let dialog = $('victory-dialog');
  if (!dialog) {
    dialog = document.createElement('dialog');
    dialog.id = 'victory-dialog';
    dialog.className = 'victory-dialog';
    dialog.setAttribute('aria-labelledby', 'victory-title');
    dialog.setAttribute('aria-describedby', 'victory-message');
    dialog.innerHTML = `<div class="victory-emblem" aria-hidden="true">✓</div>
      <div class="eyebrow">GIẢI ĐÚNG RỒI</div><h2 id="victory-title">Hoàn thành!</h2>
      <p id="victory-message"></p>
      <div class="victory-stats"><div><strong id="victory-moves"></strong><span>NƯỚC ĐI</span></div><div><strong id="victory-time"></strong><span>THỜI GIAN CHƠI</span></div></div>
      <button id="victory-next" class="primary-button" autofocus></button>
      <button id="victory-stay" class="text-button">Ở lại xem bảng đã giải</button>`;
    document.body.append(dialog);
    $('victory-stay').addEventListener('click', () => dialog.close());
  }
  $('victory-message').textContent = `Bạn đã giải đúng “${level.title}”. ${level.game === 'pipes' ? 'Tất cả ống đã nối thành một mạng, không có đầu hở hay vòng kín.' : 'Mọi ô trắng đã sáng, các ô số đều đúng và không có đèn chiếu vào nhau.'}`;
  $('victory-moves').textContent = moveCount;
  $('victory-time').textContent = $('timer').textContent;
  const sameGame = levels.filter(item => item.game === level.game);
  const index = sameGame.findIndex(item => item.id === level.id);
  const next = sameGame[index + 1] || sameGame.find(item => !completed.has(item.id))
    || levels.find(item => item.game !== level.game && !completed.has(item.id));
  $('victory-next').hidden = !next;
  if (next) {
    $('victory-next').textContent = next.game === level.game ? 'Chơi màn tiếp theo →' : `Khám phá ${next.game === 'pipes' ? 'Pipes' : 'Light Up'} →`;
    $('victory-next').onclick = () => { dialog.close(); selectLevel(next.id); };
  } else {
    $('victory-message').textContent += ' Bạn đã hoàn thành tất cả các màn hiện có!';
  }
  if (!dialog.open) dialog.showModal();
}

function notify(message) {
  $('toast').textContent = message; $('toast').classList.add('show');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => $('toast').classList.remove('show'), 3500);
}
function save() {
  if (!level) return;
  saved[level.id] = { state: clone(state), moves: moveCount, elapsed, started };
  try { localStorage.setItem(STORE, JSON.stringify({ saved, completed: [...completed], selected: level.id })); }
  catch { /* The app remains fully usable with storage disabled. */ }
}
function fresh(target) {
  return target.game === 'pipes' ? { tiles: [...target.tiles], fixed: [] } : { bulbs: [], crosses: [] };
}
function validSaved(target, value) {
  if (!value || typeof value !== 'object') return false;
  const indices = a => Array.isArray(a) && a.every(i => Number.isInteger(i) && i >= 0 && i < target.rows * target.cols);
  if (target.game === 'pipes') return Array.isArray(value.tiles) && value.tiles.length === target.tiles.length && value.tiles.every((v, i) => {
    let mask = target.tiles[i]; for (let k = 0; k < 4; k++, mask = rotate(mask)) if (mask === v) return true; return false;
  }) && indices(value.fixed);
  return indices(value.bulbs) && indices(value.crosses) && [...value.bulbs, ...value.crosses].every(i => target.board[Math.floor(i / target.cols)][i % target.cols] === '.') && !value.bulbs.some(i => value.crosses.includes(i));
}
function clearHint() {
  clearPipePreview();
  currentHint = null; $('apply-hint').hidden = true; $('coach-detail').hidden = true;
  document.querySelector('.coach-card').classList.remove('repair');
  $('coach-title').textContent = 'Một chút gợi mở?';
  $('coach-message').textContent = 'Cứ thử ý tưởng của bạn. Khi cần, mình sẽ tìm một nước đi tiếp từ chính bảng bạn đang chơi.';
}
function snapshot() { return { state: clone(state), moves: moveCount, elapsed, started }; }
function commit(change) {
  history.push(snapshot()); if (history.length > 500) history.shift(); future = [];
  change(); moveCount++; started = true; revision++; clearHint(); render(); save();
}
function selectLevel(id) {
  $('victory-dialog')?.close();
  announcedWin = null;
  if (level) save();
  level = levels.find(item => item.id === id) || levels[0];
  const previous = saved[level.id];
  state = validSaved(level, previous?.state) ? clone(previous.state) : fresh(level);
  moveCount = Number.isFinite(previous?.moves) ? Math.max(0, previous.moves) : 0;
  elapsed = Number.isFinite(previous?.elapsed) ? Math.max(0, previous.elapsed) : 0;
  started = Boolean(previous?.started); history = []; future = []; revision++; clearHint();
  const pipes = level.game === 'pipes';
  $('game-title').innerHTML = pipes ? 'Pipes<span>.</span>' : 'Light Up<span>.</span>';
  $('game-eyebrow').textContent = pipes ? '01 / KẾT NỐI' : '02 / THẮP SÁNG';
  $('game-description').textContent = pipes ? 'Xoay từng mảnh ống. Nối thành một mạng duy nhất.' : 'Đặt những đốm sáng. Tìm lời giải trong từng ô trắng.';
  $('level-title').textContent = level.title;
  $('level-size').textContent = `${level.rows} × ${level.cols}`;
  const number = levels.filter(l => l.game === level.game).findIndex(l => l.id === level.id) + 1;
  $('level-kicker').textContent = `MÀN ${String(number).padStart(2, '0')} / ${level.difficulty.toLocaleUpperCase('vi')}`;
  $('board-caption').innerHTML = `<span class="caption-dot"></span>${pipes ? 'Nhấn một ô để xoay 90° · Chuột phải để xoay ngược' : 'Nhấn để đặt / bỏ đèn · Chuột phải để đánh dấu ×'}`;
  $('hint-policy').textContent = pipes ? 'Gợi ý giữ hướng các ô bạn đã chỉnh. Ô có chấm nhỏ là ô đã chỉnh.' : 'Gợi ý giữ cả đèn và dấu × bạn đã đặt. Dấu × nghĩa là không đặt đèn ở ô đó.';
  $('light-tools').hidden = pipes;
  document.querySelector('.heading-art').style.opacity = pipes ? '.55' : '.28';
  document.querySelectorAll('[data-game]').forEach(button => button.classList.toggle('active', button.dataset.game === level.game));
  renderLevels(); render(); save();
}
function renderLevels() {
  const gameLevels = levels.filter(l => l.game === level.game);
  $('completion-count').textContent = `${gameLevels.filter(l => completed.has(l.id)).length} / ${gameLevels.length}`;
  $('level-list').replaceChildren(...gameLevels.map((item, i) => {
    const button = document.createElement('button'); button.type = 'button';
    button.className = `level-choice ${item.id === level.id ? 'active' : ''} ${completed.has(item.id) ? 'completed' : ''}`;
    button.innerHTML = `<span class="level-number">${completed.has(item.id) ? '✓' : String(i + 1).padStart(2, '0')}</span><span class="level-info"><strong>${item.title}</strong><small>${item.rows} × ${item.cols} · ${item.difficulty}</small></span>`;
    button.setAttribute('aria-label', `${item.title}, ${item.rows} nhân ${item.cols}, ${item.difficulty}${completed.has(item.id) ? ', đã hoàn thành' : ''}`);
    if (item.id === level.id) button.setAttribute('aria-current', 'true');
    button.addEventListener('click', () => selectLevel(item.id)); return button;
  }));
}
function render() {
  const focusCell = document.activeElement?.closest('#board .cell')?.dataset.cell;
  const status = drawBoard($('board'), level, state, { hintCell: currentHint?.action?.cell });
  if (focusCell !== undefined) $('board').querySelector(`[data-cell="${focusCell}"]`)?.focus({ preventScroll: true });
  solved = status.solved;
  if (!solved) announcedWin = null;
  const pipes = level.game === 'pipes';
  const percent = pipes ? Math.round(status.connected_edges / status.total_edges * 100) : Math.round(status.lit_count / status.white_count * 100);
  $('progress-number').textContent = pipes ? `${status.connected_edges} / ${status.total_edges}` : `${Math.min(percent, 100)}%`;
  $('progress-description').textContent = pipes ? 'kết nối đã khớp' : 'ô trắng đã sáng';
  document.querySelector('.progress-track').hidden = pipes;
  $('progress-bar').style.width = `${Math.min(percent, 100)}%`;
  $('status-message').className = 'status-message';
  if (solved) {
    $('status-message').textContent = 'Hoàn thành! Bảng của bạn thỏa tất cả quy tắc.';
    $('status-message').classList.add('success'); $('progress-label').textContent = '✓ Đã giải đúng';
    if (announcedWin !== winningBoardKey() && pendingWin !== winningBoardKey()) validateWin();
  } else if (!pipes && status.errors.length) {
    $('status-message').textContent = 'Có đèn chiếu vào nhau hoặc vượt số đèn cạnh ô đen. Các ô liên quan được tô đỏ.';
    $('status-message').classList.add('warning'); $('progress-label').textContent = 'Cần xem lại';
  } else {
    $('status-message').textContent = pipes
      ? `${status.components > 1 ? `Còn ${status.components} nhóm ống chưa nối thành một mạng.` : 'Các ống đã cùng một mạng; hãy kiểm tra các đầu còn hở.'}${status.cycles ? ' Có vòng kín cần mở ra.' : ''} Kết nối đang khớp vẫn có thể cần xoay lại.`
      : `${status.lit_count} / ${status.white_count} ô trắng đã sáng. ${status.clues.filter(c => c.status === 'met').length} / ${status.clues.length} ô số đã đủ đèn.`;
    $('progress-label').textContent = 'Đang khám phá';
  }
  $('move-count').textContent = moveCount; renderTimer();
  $('undo').disabled = !history.length; $('redo').disabled = !future.length;
  $('hint-button').disabled = busy || solved; $('demo-open').disabled = busy;
}
async function validateWin() {
  const key = winningBoardKey(), id = level.id;
  pendingWin = key;
  try {
    const result = await request('/api/check', payload());
    if (key !== winningBoardKey() || !result.solved || announcedWin === key) return;
    completed.add(id); renderLevels(); save();
    announcedWin = key;
    showVictory();
  } catch (error) { notify(error.message); }
  finally { if (pendingWin === key) pendingWin = null; }
}
function renderTimer() { $('timer').textContent = `${String(Math.floor(elapsed / 60)).padStart(2, '0')}:${String(elapsed % 60).padStart(2, '0')}`; }
function payload() { return { level: level.id, state: clone(state), algorithm: $('algorithm').value }; }
function setBusy(value) {
  busy = value; $('hint-button').classList.toggle('loading-pulse', value);
  $('hint-button').innerHTML = value ? '<span>✧</span> Đang tìm…' : '<span>✧</span> Gợi ý một bước';
  $('hint-button').disabled = value || solved; $('demo-open').disabled = value;
}
function metricsText(metrics) {
  return `${metrics.expanded.toLocaleString('vi')} trạng thái xét · ${Number(metrics.elapsed_ms).toLocaleString('vi', { maximumFractionDigits: 2 })} ms`;
}
async function getHint() {
  if (busy || solved) return;
  setBusy(true); clearHint(); const rev = revision;
  $('coach-title').textContent = 'Đang nối các ý tưởng…'; $('coach-message').textContent = 'Máy đang tìm lời giải có giữ những lựa chọn hiện tại của bạn.';
  try {
    const result = await request('/api/hint', payload());
    if (rev !== revision) { notify('Bảng đã thay đổi. Hãy xin gợi ý lại từ trạng thái mới.'); return; }
    currentHint = result;
    $('coach-title').textContent = ({ hint: 'Thử ô được đánh dấu.', repair: 'Cần sửa một lựa chọn.', limit: 'Cần thêm thời gian.', repair_limit: 'Nhánh này chưa có lối ra.', complete: 'Bạn đã làm được!' })[result.status] || 'Kết quả tìm kiếm';
    $('coach-message').textContent = result.message;
    if (result.action?.kind === 'rotate') {
      $('coach-message').textContent = 'Xoay ô được đánh dấu theo hình bên dưới.';
      showPipePreview(state.tiles[result.action.cell], result.action, level.cols);
    }
    $('coach-detail').textContent = result.explanation || ''; $('coach-detail').hidden = !result.explanation;
    $('apply-hint').hidden = !result.action;
    $('apply-hint').textContent = result.status === 'repair' ? 'Áp dụng bước sửa này ↗' : 'Áp dụng bước này ↗';
    document.querySelector('.coach-card').classList.toggle('repair', result.status.startsWith('repair'));
    if (result.metrics) $('last-metrics').textContent = metricsText(result.metrics);
    render();
  } catch (error) { $('coach-title').textContent = 'Chưa kết nối được.'; $('coach-message').textContent = error.message; }
  finally { setBusy(false); }
}
function applyHint() {
  const action = currentHint?.action; if (!action) return;
  commit(() => {
    const cell = action.cell;
    if (action.kind === 'rotate') { state.tiles[cell] = action.value; if (!state.fixed.includes(cell)) state.fixed.push(cell); }
    else if (action.kind === 'add_bulb') { state.crosses = state.crosses.filter(i => i !== cell); if (!state.bulbs.includes(cell)) state.bulbs.push(cell); }
    else if (action.kind === 'remove_bulb') state.bulbs = state.bulbs.filter(i => i !== cell);
    else if (action.kind === 'remove_cross') state.crosses = state.crosses.filter(i => i !== cell);
  });
  notify('Đã áp dụng. Bạn có thể hoàn tác bất cứ lúc nào.');
  if (action.kind === 'rotate') animateAppliedPipe(action.cell, action.turns);
}
function playCell(cell, right = false) {
  if (!level) return;
  if (level.game === 'lightup' && level.board[Math.floor(cell / level.cols)][cell % level.cols] !== '.') return;
  commit(() => {
    if (level.game === 'pipes') {
      const turns = right ? 3 : 1;
      for (let i = 0; i < turns; i++) state.tiles[cell] = rotate(state.tiles[cell]);
      if (!state.fixed.includes(cell)) state.fixed.push(cell);
    } else {
      const key = right || tool === 'cross' ? 'crosses' : 'bulbs';
      const other = key === 'crosses' ? 'bulbs' : 'crosses';
      state[other] = state[other].filter(i => i !== cell);
      state[key] = state[key].includes(cell) ? state[key].filter(i => i !== cell) : [...state[key], cell];
    }
  });
}
function travel(back) {
  const source = back ? history : future, destination = back ? future : history;
  if (!source.length) return;
  destination.push(snapshot()); const entry = source.pop(); state = entry.state; moveCount = entry.moves;
  elapsed = entry.elapsed; started = entry.started;
  revision++; clearHint(); render(); save();
}
function showRules() {
  const pipes = level.game === 'pipes'; $('rules-title').textContent = pipes ? 'Cách chơi Pipes' : 'Cách chơi Light Up';
  $('rules-content').innerHTML = pipes
    ? '<ol><li>Nhấn một ô để xoay ống 90° theo chiều kim đồng hồ. Chuột phải để xoay ngược.</li><li>Mọi đầu ống phải khớp với ô bên cạnh và không chĩa ra ngoài bảng.</li><li>Tất cả ống phải nối thành <strong>một mạng duy nhất, không có vòng kín</strong>.</li></ol><div class="rule-note">Gợi ý giữ hướng các ô bạn đã chỉnh (có chấm nhỏ). Nếu những lựa chọn này mâu thuẫn, máy đề xuất một bước sửa và chờ bạn áp dụng. Hoàn tác sẽ khôi phục cả hướng ống lẫn dấu đã chỉnh.</div><p>Nguồn luật: <a href="https://www.puzzle-pipes.com/" target="_blank" rel="noreferrer">puzzle-pipes.com</a>. Các màn trong ứng dụng được tạo riêng, không nối xuyên biên.</p>'
    : '<ol><li>Nhấn ô trắng để đặt hoặc bỏ đèn. Đèn chiếu theo hàng và cột, dừng ở ô đen.</li><li>Chiếu sáng <strong>tất cả ô trắng</strong>. Hai bóng đèn không được chiếu trực tiếp vào nhau.</li><li>Ô đen mang số cần đúng bấy nhiêu đèn kề cạnh (không tính đường chéo). Số 0 nghĩa là không có đèn kề cạnh.</li><li>Chuột phải hoặc chọn “Đánh dấu” để đặt dấu ×: bạn quyết định không đặt đèn ở ô đó. Ô × vẫn có thể được chiếu sáng.</li></ol><div class="rule-note">Các tia sáng được giao nhau. Gợi ý giữ nguyên cả đèn và dấu × của bạn. Nếu cần sửa, máy giải thích trước và không tự thay đổi bảng.</div><p>Nguồn luật: <a href="https://www.puzzle-light-up.com/" target="_blank" rel="noreferrer">puzzle-light-up.com</a>. Các màn trong ứng dụng được tạo riêng.</p>';
  $('rules-dialog').showModal();
}
function stopDemo() { clearInterval(demoTimer); demoTimer = null; $('demo-play').textContent = 'Tự chạy'; }
function renderDemo(solution = false) {
  if (!demoResult) return;
  const trace = demoResult.trace || [], entry = trace[demoIndex];
  const shown = solution ? demoResult.solution : entry?.state;
  if (shown) {
    const visibleTiles = level.game === 'pipes'
      ? shown.tiles.map((mask, i) => mask || state.tiles[i] || level.tiles[i]) : null;
    drawBoard($('demo-board'), level, shown, { demo: true, fallback: state });
    if (visibleTiles) animateDemoPipes($('demo-board'), demoVisibleTiles || state.tiles, visibleTiles);
    demoVisibleTiles = visibleTiles;
  }
  const metrics = demoResult.metrics;
  const stats = [[metrics.expanded, 'TRẠNG THÁI ĐÃ XÉT'], [metrics.frontier_peak, 'FRONTIER LỚN NHẤT'], [metrics.elapsed_ms + ' ms', 'THỜI GIAN TÌM'], [solution ? '0' : entry?.h ?? '—', 'HEURISTIC h']];
  $('demo-stats').innerHTML = stats.map(([v, label]) => `<div class="demo-stat"><small>${label}</small><strong>${v}</strong></div>`).join('');
  $('demo-slider').max = Math.max(0, trace.length - 1); $('demo-slider').value = demoIndex;
  $('demo-step-label').textContent = solution ? 'Bảng lời giải · bảng chơi của bạn được giữ nguyên' : `Trạng thái ${trace.length ? demoIndex + 1 : 0} / ${trace.length}${demoResult.trace_truncated ? ' · chỉ lưu 350 trạng thái đầu' : ''}`;
  $('demo-prev').disabled = !trace.length || demoIndex === 0;
  $('demo-next').disabled = !trace.length || demoIndex >= trace.length - 1;
  $('demo-play').disabled = trace.length < 2; $('demo-slider').disabled = !trace.length;
  $('demo-solution').hidden = !demoResult.solution;
}
async function openDemo() {
  if (busy) return;
  setBusy(true); stopDemo(); demoResult = null; demoVisibleTiles = null;
  $('demo-title').textContent = $('algorithm').value === 'dfs' ? 'Theo dấu DFS' : 'Theo dấu Greedy';
  $('demo-message').textContent = 'Đang tìm kiếm từ các lựa chọn hiện tại. Các ô ống mờ là những ô máy chưa gán hướng.';
  $('demo-board').replaceChildren(); $('demo-stats').replaceChildren(); $('demo-step-label').textContent = '';
  for (const id of ['demo-prev', 'demo-next', 'demo-play', 'demo-slider']) $(id).disabled = true;
  $('demo-solution').hidden = true; $('demo-dialog').showModal(); const rev = revision;
  try {
    const result = await request('/api/solve', payload());
    if (rev !== revision) return;
    demoResult = result; demoIndex = 0;
    $('demo-message').textContent = result.status === 'solved'
      ? 'Đã tìm được lời giải. Xem từng trạng thái được xét; việc xem demo không thay đổi bảng bạn đang chơi.'
      : result.status === 'unsat' ? 'Không có lời giải giữ nguyên các lựa chọn hiện tại. Đóng demo và bấm Gợi ý để xem một phương án sửa.'
      : 'Đã chạm giới hạn tìm kiếm. Các trạng thái dưới đây là phần máy đã xét; chưa thể kết luận vô nghiệm.';
    if (result.trace_truncated) $('demo-message').textContent += ' Bản xem chỉ lưu 350 trạng thái đầu.';
    renderDemo(); $('last-metrics').textContent = metricsText(result.metrics);
  } catch (error) { $('demo-message').textContent = error.message; }
  finally { setBusy(false); }
}

function events() {
  document.querySelectorAll('[data-game]').forEach(button => button.addEventListener('click', () => selectLevel(levels.find(l => l.game === button.dataset.game).id)));
  $('board').addEventListener('click', event => { const cell = event.target.closest('[data-cell]'); if (cell) playCell(Number(cell.dataset.cell)); });
  $('board').addEventListener('contextmenu', event => { const cell = event.target.closest('[data-cell]'); if (cell) { event.preventDefault(); playCell(Number(cell.dataset.cell), true); } });
  $('undo').addEventListener('click', () => travel(true)); $('redo').addEventListener('click', () => travel(false));
  $('reset').addEventListener('click', () => $('reset-dialog').showModal());
  $('confirm-reset').addEventListener('click', () => { commit(() => { state = fresh(level); moveCount = -1; elapsed = 0; }); $('reset-dialog').close(); notify('Bảng đã được đặt lại. Bạn vẫn có thể hoàn tác.'); });
  $('hint-button').addEventListener('click', getHint); $('apply-hint').addEventListener('click', applyHint);
  $('rules-open').addEventListener('click', showRules); $('demo-open').addEventListener('click', openDemo);
  document.querySelectorAll('.dialog-close').forEach(button => button.addEventListener('click', () => button.closest('dialog').close()));
  $('demo-dialog').addEventListener('close', stopDemo);
  $('algorithm').addEventListener('change', () => { revision++; $('algorithm-summary').textContent = $('algorithm').value === 'dfs' ? 'Đi sâu theo một nhánh, quay lại khi gặp bế tắc.' : 'Ưu tiên trạng thái có điểm heuristic thấp hơn.'; clearHint(); render(); });
  document.querySelectorAll('[data-tool]').forEach(button => button.addEventListener('click', () => { tool = button.dataset.tool; document.querySelectorAll('[data-tool]').forEach(b => b.classList.toggle('active', b === button)); }));
  $('demo-prev').addEventListener('click', () => { stopDemo(); demoIndex = Math.max(0, demoIndex - 1); renderDemo(); });
  $('demo-next').addEventListener('click', () => { stopDemo(); demoIndex = Math.min(demoResult.trace.length - 1, demoIndex + 1); renderDemo(); });
  $('demo-slider').addEventListener('input', event => { stopDemo(); demoIndex = Number(event.target.value); renderDemo(); });
  $('demo-play').addEventListener('click', () => {
    if (demoTimer) { stopDemo(); return; }
    if (demoIndex >= demoResult.trace.length - 1) demoIndex = 0;
    $('demo-play').textContent = 'Tạm dừng'; renderDemo();
    demoTimer = setInterval(() => { if (demoIndex >= demoResult.trace.length - 1) { stopDemo(); return; } demoIndex++; renderDemo(); }, level.game === 'pipes' ? 950 : 650);
  });
  $('demo-solution').addEventListener('click', () => { stopDemo(); renderDemo(true); });
  document.addEventListener('keydown', event => {
    if (document.querySelector('dialog[open]') || ['INPUT', 'SELECT', 'TEXTAREA'].includes(event.target.tagName)) return;
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') { event.preventDefault(); travel(!event.shiftKey); }
    else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'y') { event.preventDefault(); travel(false); }
    else if (!event.ctrlKey && !event.metaKey && level.game === 'lightup' && ['b', 'x'].includes(event.key.toLowerCase())) document.querySelector(`[data-tool="${event.key.toLowerCase() === 'b' ? 'bulb' : 'cross'}"]`).click();
  });
  window.addEventListener('beforeunload', save);
  setInterval(() => { if (started && !solved && !document.hidden) { elapsed++; renderTimer(); if (elapsed % 5 === 0) save(); } }, 1000);
}

async function init() {
  try {
    let selected;
    try { const stored = JSON.parse(localStorage.getItem(STORE) || '{}'); saved = stored.saved && typeof stored.saved === 'object' ? stored.saved : {}; completed = new Set(Array.isArray(stored.completed) ? stored.completed : []); selected = stored.selected; } catch { saved = {}; }
    levels = await request('/api/levels'); events(); selectLevel(selected || levels[0].id);
  } catch (error) { $('coach-title').textContent = 'Cần mở máy giải Python'; $('coach-message').textContent = 'Chạy python app.py rồi mở http://127.0.0.1:8765. ' + error.message; notify('Không thể tải màn chơi. Kiểm tra cửa sổ chạy Python.'); }
}
init();

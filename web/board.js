// Rendering and immediate feedback only. Python validates completed boards.
const directions = [[-1, 0, 1, 4], [0, 1, 2, 8], [1, 0, 4, 1], [0, -1, 8, 2]];
export const rotate = mask => ((mask << 1) & 15) | (mask >> 3);
const bulb = `<svg class="bulb-icon" viewBox="0 0 40 48" aria-hidden="true"><path d="M13 31C13 26 7 23 7 16a13 13 0 0 1 26 0c0 7-6 10-6 15" fill="#f5c957" stroke="currentColor" stroke-width="2.1"/><path d="M14 33h12m-12 5h12m-9 5h6" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><path d="M20 29V18m-4-2 4 3 4-3" fill="none" stroke="#b98922" stroke-width="1.7" stroke-linecap="round"/></svg>`;

export function pipeSvg(mask) {
  const ends = [[1, 50, 0], [2, 100, 50], [4, 50, 100], [8, 0, 50]].filter(([bit]) => mask & bit);
  const path = ends.map(([, x, y]) => `M50 50L${x} ${y}`).join('');
  return `<svg viewBox="0 0 100 100" aria-hidden="true"><path class="pipe-shadow" d="${path}"/><path class="pipe-path" d="${path}"/><path class="pipe-inner" d="${path}"/>${ends.length === 1 ? '<circle cx="50" cy="50" r="10" fill="#e9f0df" stroke="#789768" stroke-width="4"/><circle cx="50" cy="50" r="3" fill="#789768"/>' : ''}</svg>`;
}

export function inspect(level, state) {
  const n = level.rows * level.cols;
  if (level.game === 'pipes') {
    const errors = new Set(), edges = Array.from({ length: n }, () => []);
    let connected = 0;
    for (let i = 0; i < n; i++) {
      const r = Math.floor(i / level.cols), c = i % level.cols, value = state.tiles[i];
      for (const [dr, dc, bit, opposite] of directions) {
        const nr = r + dr, nc = c + dc;
        if (nr < 0 || nr >= level.rows || nc < 0 || nc >= level.cols) {
          if (value & bit) errors.add(i);
          continue;
        }
        const j = nr * level.cols + nc;
        if (Boolean(value & bit) !== Boolean(state.tiles[j] & opposite)) { errors.add(i); errors.add(j); }
        else if (value & bit) { edges[i].push(j); if (j > i) connected++; }
      }
    }
    const seen = new Set(); let components = 0;
    for (let root = 0; root < n; root++) {
      if (seen.has(root)) continue;
      components++; const stack = [root]; seen.add(root);
      while (stack.length) for (const j of edges[stack.pop()]) if (!seen.has(j)) { seen.add(j); stack.push(j); }
    }
    const cycles = connected - n + components;
    return { solved: !errors.size && components === 1 && cycles === 0,
      errors: [...errors], connected_edges: connected, total_edges: n - 1, components, cycles };
  }
  const lamps = new Set(state.bulbs), lit = new Set(), errors = new Set(), clues = [];
  let white = 0;
  for (const row of level.board) for (const value of row) if (value === '.') white++;
  for (const i of lamps) {
    lit.add(i); const r = Math.floor(i / level.cols), c = i % level.cols;
    for (const [dr, dc] of directions) {
      let nr = r + dr, nc = c + dc;
      while (nr >= 0 && nr < level.rows && nc >= 0 && nc < level.cols && level.board[nr][nc] === '.') {
        const j = nr * level.cols + nc; lit.add(j);
        if (lamps.has(j)) { errors.add(i); errors.add(j); }
        nr += dr; nc += dc;
      }
    }
  }
  for (let r = 0; r < level.rows; r++) for (let c = 0; c < level.cols; c++) {
    const value = level.board[r][c];
    if (!/^[0-4]$/.test(value)) continue;
    const adjacent = directions.map(([dr, dc]) => [r + dr, c + dc]).filter(([nr, nc]) => nr >= 0 && nr < level.rows && nc >= 0 && nc < level.cols).map(([nr, nc]) => nr * level.cols + nc);
    const count = adjacent.filter(i => lamps.has(i)).length, target = Number(value);
    const status = count > target ? 'over' : count === target ? 'met' : 'open';
    clues.push({ cell: r * level.cols + c, target, count, status });
    if (status === 'over') adjacent.filter(i => lamps.has(i)).forEach(i => errors.add(i));
  }
  return { solved: lit.size === white && !errors.size && clues.every(c => c.status === 'met'), lit: [...lit], errors: [...errors], clues, lit_count: lit.size, white_count: white };
}

export function drawBoard(container, level, state, { hintCell = -1, demo = false, fallback = null } = {}) {
  const status = inspect(level, state), fixed = new Set(state.fixed || []), lit = new Set(status.lit || []), lamps = new Set(state.bulbs || []), crosses = new Set(state.crosses || []);
  const errors = new Set(status.errors), clueMap = new Map((status.clues || []).map(c => [c.cell, c]));
  container.className = `board ${demo ? 'demo-board' : ''} ${level.game === 'lightup' ? 'lightup-board' : ''} ${status.solved ? 'solved' : ''}`;
  container.style.setProperty('--cols', level.cols);
  const cells = [];
  for (let i = 0; i < level.rows * level.cols; i++) {
    const cell = document.createElement('button'); cell.type = 'button'; cell.className = 'cell'; cell.dataset.cell = i;
    const r = Math.floor(i / level.cols), c = i % level.cols;
    let label = `Hàng ${r + 1}, cột ${c + 1}`;
    if (level.game === 'pipes') {
      const value = state.tiles[i]; cell.innerHTML = pipeSvg(value || fallback?.tiles[i] || level.tiles[i]);
      if (fixed.has(i)) cell.classList.add('touched');
      if (demo && !value) cell.classList.add('trace-empty');
      const names = [[1, 'trên'], [2, 'phải'], [4, 'dưới'], [8, 'trái']].filter(([bit]) => value & bit).map(([, name]) => name);
      label += `: ống nối ${names.join(', ')}${fixed.has(i) ? ', đã chỉnh' : ''}. Nhấn để xoay.`;
    } else {
      const value = level.board[r][c];
      if (value !== '.') {
        cell.classList.add('wall'); cell.textContent = value === '#' ? '' : value;
        const clue = clueMap.get(i); if (clue) cell.classList.add(clue.status);
        cell.disabled = true; label += value === '#' ? ': ô đen' : `: ô đen số ${value}`;
      } else {
        if (lit.has(i)) cell.classList.add('lit');
        if (lamps.has(i)) { cell.classList.add('lamp'); cell.innerHTML = bulb; }
        if (crosses.has(i)) cell.classList.add('cross');
        if (errors.has(i)) cell.classList.add('error');
        label += lamps.has(i) ? ': có đèn' : crosses.has(i) ? ': dấu không đặt đèn' : lit.has(i) ? ': đang sáng' : ': chưa sáng';
      }
    }
    if (i === hintCell) cell.classList.add('hinted');
    cell.setAttribute('aria-label', label); cell.title = label;
    if (demo) cell.tabIndex = -1;
    cells.push(cell);
  }
  container.replaceChildren(...cells);
  return status;
}

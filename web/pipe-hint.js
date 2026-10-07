import { pipeSvg } from './board.js';

let previewAnimation = null;
const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function previewElement() {
  let element = document.getElementById('pipe-hint-preview');
  if (!element) {
    element = document.createElement('div');
    element.id = 'pipe-hint-preview';
    element.className = 'pipe-hint-preview';
    document.getElementById('coach-message').after(element);
  }
  return element;
}

export function clearPipePreview() {
  previewAnimation?.cancel();
  previewAnimation = null;
  const element = document.getElementById('pipe-hint-preview');
  if (element) { element.hidden = true; element.replaceChildren(); }
}

export function showPipePreview(from, action, cols) {
  clearPipePreview();
  const element = previewElement();
  element.hidden = false;
  const location = `Hàng ${Math.floor(action.cell / cols) + 1} · Cột ${action.cell % cols + 1}`;
  element.innerHTML = `<div class="pipe-preview-location"></div>
    <div class="pipe-preview-comparison">
      <div class="pipe-preview-state"><div class="pipe-preview-tile">${pipeSvg(from)}</div><span>Hiện tại</span></div>
      <span class="pipe-preview-arrow" aria-hidden="true">→</span>
      <div class="pipe-preview-state"><div class="pipe-preview-tile pipe-preview-target">${pipeSvg(action.value)}</div><span>Hướng cần nối</span></div>
    </div>
    <button type="button" class="pipe-preview-replay">↻ Xem lại cách xoay</button>`;
  element.querySelector('.pipe-preview-location').textContent = location;
  element.setAttribute('role', 'group');
  element.setAttribute('aria-label', `${location}. Xem hướng ống hiện tại và hướng được gợi ý.`);
  const target = element.querySelector('.pipe-preview-target svg');
  const replay = () => {
    previewAnimation?.cancel();
    if (reducedMotion() || !target.animate) return;
    // SVG already represents the final mask: rotate back to the start,
    // then move clockwise to its natural orientation. No state mutation.
    previewAnimation = target.animate([
      { transform: `rotate(${-action.turns * 90}deg)`, offset: 0 },
      { transform: `rotate(${-action.turns * 90}deg)`, offset: .22 },
      { transform: 'rotate(0deg)', offset: 1 },
    ], { duration: 950 + action.turns * 180, easing: 'cubic-bezier(.22,.7,.25,1)' });
  };
  element.querySelector('button').addEventListener('click', replay);
  replay();
}

export function animateAppliedPipe(cell, turns) {
  const svg = document.querySelector(`#board [data-cell="${cell}"] svg`);
  if (!svg?.animate || reducedMotion()) return;
  svg.animate([{ transform: `rotate(${-turns * 90}deg)` }, { transform: 'rotate(0deg)' }],
    { duration: 420 + turns * 150, easing: 'cubic-bezier(.22,.7,.25,1)' });
}

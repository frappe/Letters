import { ref } from "vue";

const MIN_PANEL = 160;
const MAX_PANEL = 480;

// Drag-to-resize widths for the left (layers) and right (inspector) panels.
// Self-contained: owns both widths and wires window mouse listeners for the
// duration of a drag. The left handle grows the panel as the cursor moves
// right; the right handle grows it as the cursor moves left.
export function usePanelResize({ left = 208, right = 288 } = {}) {
  const leftPanelWidth = ref(left);
  const rightPanelWidth = ref(right);

  function beginDrag(widthRef, sign, e) {
    e.preventDefault();
    const startX = e.clientX;
    const startW = widthRef.value;
    function onMove(ev) {
      widthRef.value = Math.min(MAX_PANEL, Math.max(MIN_PANEL, startW + sign * (ev.clientX - startX)));
    }
    function onUp() {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    }
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }

  const startLeftResize = (e) => beginDrag(leftPanelWidth, 1, e);
  const startRightResize = (e) => beginDrag(rightPanelWidth, -1, e);

  return { leftPanelWidth, rightPanelWidth, startLeftResize, startRightResize };
}

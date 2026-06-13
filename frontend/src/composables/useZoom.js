import { ref, watch } from "vue";

const ZOOM_LEVELS = [0.5, 0.67, 0.75, 0.9, 1, 1.1, 1.25, 1.5];

// Canvas zoom level plus the auto-hiding zoom pill. The pill is hidden by
// default; it appears whenever the zoom changes (shortcut, trackpad, or its own
// buttons) and fades out 2.5s after the last change so it never permanently
// covers the canvas.
export function useZoom() {
  const canvasZoom = ref(1);
  const zoomVisible = ref(false);
  let hideTimer = null;

  function flashZoom() {
    zoomVisible.value = true;
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => { zoomVisible.value = false; }, 2500);
  }
  watch(canvasZoom, flashZoom);

  function resetZoom() {
    canvasZoom.value = 1;
  }

  function stepZoom(dir) {
    const idx = ZOOM_LEVELS.findIndex(z => z >= canvasZoom.value - 0.01);
    const next = dir > 0
      ? ZOOM_LEVELS[Math.min(idx + 1, ZOOM_LEVELS.length - 1)]
      : ZOOM_LEVELS[Math.max(idx - 1, 0)];
    canvasZoom.value = next ?? canvasZoom.value;
  }

  return { canvasZoom, zoomVisible, resetZoom, stepZoom };
}

<template>
  <div class="space-y-1.5">
    <div
      v-if="imageUrl"
      ref="frame"
      class="relative w-full overflow-hidden rounded border border-outline-gray-2 cursor-crosshair select-none bg-surface-gray-2"
      style="aspect-ratio: 4 / 3;"
      @pointerdown="onPointerDown"
    >
      <!-- whole image shown so the user can see what they're aiming at -->
      <img
        :src="imageUrl"
        alt=""
        class="absolute inset-0 w-full h-full object-contain pointer-events-none"
        draggable="false"
      />
      <!-- draggable focus handle -->
      <div
        class="absolute w-4 h-4 -ml-2 -mt-2 rounded-full border-2 border-white shadow ring-1 ring-black/30 bg-blue-500 pointer-events-none"
        :style="{ left: pct.x + '%', top: pct.y + '%' }"
      />
    </div>
    <p v-else class="text-xs text-ink-gray-4">Add an image to set its focus point.</p>
    <div class="flex items-center justify-between">
      <p class="text-[11px] text-ink-gray-4">Drag to set the crop focus.</p>
      <span class="text-[11px] font-medium text-ink-gray-6 tabular-nums">{{ pct.x }}% {{ pct.y }}%</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  value:      { default: "center" },
  blockProps: { type: Object, default: () => ({}) },
});
const emit = defineEmits(["change"]);

const frame = ref(null);
const imageUrl = computed(() => props.blockProps.image_url || "");

// Keyword positions → percentage pairs (x y), where 0%=left/top, 100%=right/bottom.
const KEYWORDS = {
  center: [50, 50],
  "center top": [50, 0],
  "center bottom": [50, 100],
  "left center": [0, 50],
  "right center": [100, 50],
  "left top": [0, 0],
  "right top": [100, 0],
  "left bottom": [0, 100],
  "right bottom": [100, 100],
};

const pct = computed(() => {
  const v = (props.value || "center").trim();
  if (KEYWORDS[v]) return { x: KEYWORDS[v][0], y: KEYWORDS[v][1] };
  const m = v.match(/^(\d+(?:\.\d+)?)%\s+(\d+(?:\.\d+)?)%$/);
  if (m) return { x: clamp(+m[1]), y: clamp(+m[2]) };
  return { x: 50, y: 50 };
});

function clamp(n) { return Math.max(0, Math.min(100, n)); }

function setFromEvent(e) {
  const el = frame.value;
  if (!el) return;
  const r = el.getBoundingClientRect();
  const x = clamp(Math.round(((e.clientX - r.left) / r.width) * 100));
  const y = clamp(Math.round(((e.clientY - r.top) / r.height) * 100));
  emit("change", `${x}% ${y}%`);
}

function onPointerDown(e) {
  setFromEvent(e);
  const move = (ev) => setFromEvent(ev);
  const up = () => {
    window.removeEventListener("pointermove", move);
    window.removeEventListener("pointerup", up);
  };
  window.addEventListener("pointermove", move);
  window.addEventListener("pointerup", up);
}
</script>

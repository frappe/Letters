<template>
  <!-- width/minHeight live here so they apply to the full wrapper, not double-counted -->
  <BlockWrapper :block="block" :index="index" :extra-style="wrapperStyle">
    <div
      :style="{
        backgroundColor: block.props.background_color || undefined,
        display: 'flex',
        flexDirection: block.props.layout === 'row' ? 'row' : 'column',
        alignItems:     block.props.layout === 'row' ? (block.props.vertical_align || 'stretch') : undefined,
        justifyContent: block.props.layout !== 'row' ? (block.props.vertical_align || 'flex-start') : undefined,
        gap: `${block.props.gap ?? 12}px`,
        height: '100%',
        ...paddingStyle,
      }"
    >
      <!-- Children -->
      <template v-if="block.children?.length">
        <div
          v-for="(child, childIndex) in block.children"
          :key="child.id"
          class="relative group/child rounded transition-colors"
          :class="childDragOver === childIndex ? 'ring-2 ring-blue-400' : ''"
          :style="childFlexStyle(child)"
          draggable="true"
          @click.stop="store.selectBlock(child.id)"
          @dragstart.stop="onChildDragStart(childIndex, $event)"
          @dragover.stop.prevent="onChildDragOver(childIndex, $event)"
          @dragleave.stop="childDragOver = null"
          @drop.stop.prevent="onChildDrop(childIndex)"
          @dragend.stop="childDragFrom = null; childDragOver = null"
        >
          <!-- Drop indicator -->
          <div v-if="childDragOver === childIndex && childDragFrom !== null && childDragFrom !== childIndex"
            class="absolute inset-x-0 -top-px h-0.5 bg-blue-500 rounded-full pointer-events-none z-20" />
          <!-- Drag grip -->
          <div
            class="absolute top-1/2 -translate-y-1/2 -left-5 w-4 h-6 flex items-center justify-center
                   cursor-grab active:cursor-grabbing select-none rounded
                   text-ink-gray-3 hover:text-ink-gray-5 hover:bg-surface-gray-2 transition-all z-20
                   opacity-0 group-hover/child:opacity-100"
            @click.stop
          >
            <svg width="8" height="12" viewBox="0 0 8 12" fill="currentColor">
              <circle cx="2" cy="2"  r="1.2"/><circle cx="6" cy="2"  r="1.2"/>
              <circle cx="2" cy="6"  r="1.2"/><circle cx="6" cy="6"  r="1.2"/>
              <circle cx="2" cy="10" r="1.2"/><circle cx="6" cy="10" r="1.2"/>
            </svg>
          </div>
          <!-- Remove child button -->
          <button
            type="button"
            class="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-surface-base border border-outline-gray-2
                   shadow-sm text-ink-gray-4 hover:text-red-500 hover:border-red-200
                   text-xs leading-none z-20
                   opacity-0 group-hover/child:opacity-100 transition-opacity
                   flex items-center justify-center"
            title="Remove block"
            aria-label="Remove block"
            @click.stop="store.removeBlock(child.id)"
          ><FeatherIcon name="x" class="w-3 h-3" /></button>
          <!-- Render the child block -->
          <BlockRenderer :block="child" :index="childIndex" />
        </div>
      </template>

      <!-- Empty state -->
      <div
        v-else
        class="flex items-center justify-center py-6 select-none"
      >
        <button
          type="button"
          class="w-7 h-7 flex items-center justify-center text-ink-gray-3 hover:text-ink-gray-6 transition-colors"
          title="Add block inside"
          @click.stop="openPicker({ mode: 'child', parentId: block.id, afterIndex: -1 })"
        >
          <FeatherIcon name="plus" class="w-4 h-4" />
        </button>
      </div>
    </div>
  </BlockWrapper>
</template>

<script setup>
import { computed, ref, inject } from "vue";
import BlockWrapper from "../BlockWrapper.vue";
import BlockRenderer from "../BlockRenderer.vue";
import { FeatherIcon } from "frappe-ui";
import { useEditorStore } from "../../stores/editor";
import { usePadding } from "../../composables/usePadding";

const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();
const openPicker = inject("openPicker", () => {});

const blockProps = computed(() => props.block.props);
const paddingStyle = usePadding(blockProps, { top: 16, right: 16, bottom: 16, left: 16 });

// width + minHeight go on the BlockWrapper so they aren't applied twice
// (the parent's childFlexStyle also reads width, so the inner div must NOT repeat it)
// Width is NOT set here — it's applied by the parent's childFlexStyle on the
// child-wrapper div. Setting it here too would cause double-application (% of %).
// backgroundColor is duplicated here so the area between content-bottom and
// minHeight shows the container color instead of the canvas/parent background.
const wrapperStyle = computed(() => {
  const h  = props.block.props.height;
  const bg = props.block.props.background_color;
  return {
    ...(h && h !== "auto" && h !== "0px" ? { minHeight: h } : {}),
    ...(bg && bg !== "transparent" ? { backgroundColor: bg } : {}),
  };
});

// ── Child sizing (row flex + column width) ───────────────────────────────────
// Width is always applied HERE on the child-wrapper div, never on BlockWrapper,
// to avoid double-application (% of % bug).
// block_width / block_height are Inspector-settable overrides for a child's
// slot size inside this container (independent of the block's own content props).
function childFlexStyle(child) {
  const bw = child.props?.block_width;
  const bh = child.props?.block_height;
  const heightStyle = bh && bh !== "auto" ? { minHeight: bh } : {};

  if (props.block.props.layout === "row") {
    if (bw && bw !== "auto") return { flex: `0 0 ${bw}`, minWidth: 0, alignSelf: "stretch", ...heightStyle };
    // flex_width: legacy prop kept for presets that still use it
    const fw = child.props?.flex_width;
    if (fw && fw !== "auto") return { flex: `0 0 ${fw}`, minWidth: 0, alignSelf: "stretch", ...heightStyle };
    if (fw === "auto")       return { flex: "0 0 auto",  minWidth: 0, alignSelf: "stretch", ...heightStyle };
    // Vertical dividers shrink to padding width rather than sharing equal flex space
    if (child.type === "divider" && child.props?.orientation === "vertical") {
      return { flex: "0 0 auto", minWidth: 0, alignSelf: "stretch", ...heightStyle };
    }
    const w = child.props?.width;
    const hasWidth = w && w !== "auto" && w !== "100%" && w !== "0px";
    if (hasWidth) return { flex: `0 0 ${w}`, minWidth: 0, alignSelf: alignSelfMap[child.props?.align] || "stretch", ...heightStyle };
    return { flex: "1 1 0", minWidth: 0, ...heightStyle };
  } else {
    const w = bw || child.props?.width;
    const hasWidth = w && w !== "auto" && w !== "100%" && w !== "0px";
    if (hasWidth) return { width: w, alignSelf: alignSelfMap[child.props?.align] || "stretch", ...heightStyle };
    return { ...heightStyle };
  }
}

const alignSelfMap = { left: "flex-start", center: "center", right: "flex-end" };

// ── Child drag-to-reorder ────────────────────────────────────────────────────
const childDragFrom = ref(null);
const childDragOver = ref(null);

function onChildDragStart(index, e) {
  childDragFrom.value = index;
  e.dataTransfer.effectAllowed = "move";
}
function onChildDragOver(index) {
  if (childDragFrom.value === null) return;
  childDragOver.value = index;
}
function onChildDrop(toIndex) {
  const from = childDragFrom.value;
  childDragFrom.value = null;
  childDragOver.value = null;
  if (from === null || from === toIndex) return;
  store.moveChildBlock(props.block.id, from, toIndex);
}
</script>

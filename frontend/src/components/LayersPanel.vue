<template>
  <div class="flex flex-col h-full">
    <!-- Empty state -->
    <div
      v-if="!store.blocks.length"
      class="flex-1 flex flex-col items-center justify-center px-4 text-center gap-2"
    >
      <p class="text-xs text-ink-gray-4 leading-relaxed">
        No blocks yet. Use <strong>+ Add block</strong> below.
      </p>
    </div>

    <!-- Layer tree -->
    <div
      v-else
      class="flex-1 overflow-y-auto py-1 flex flex-col"
      @dragover.prevent
      @drop.prevent="onDropAtEnd"
    >
      <LayerNode
        v-for="block in store.blocks"
        :key="block.id"
        :block="block"
        :depth="0"
        :is-last="block === store.blocks[store.blocks.length - 1]"
      />
    </div>

    <!-- Reorder hint -->
    <div v-if="store.blocks.length > 1" class="px-3 py-2 border-t border-gray-100">
      <p class="text-xs text-ink-gray-3 text-center">Drag to reorder · double-click to rename</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted, onUnmounted, defineComponent, h } from "vue";
import { FeatherIcon } from "frappe-ui";
import { useEditorStore } from "../stores/editor";
import { BLOCK_SCHEMA } from "../blockSchema";

const store = useEditorStore();
const openPicker = inject("openPicker", () => {});

const vFocus = { mounted: (el) => el.focus() };

const STRUCTURAL = new Set(["container", "columns"]);
const blockIcon  = (type) => BLOCK_SCHEMA[type]?.icon || "box";
const blockLabel = (type) => BLOCK_SCHEMA[type]?.label || type;

function rowClass(node) {
  if (store.selectedBlockId === node.id) return "bg-surface-elevation-3 shadow-sm";
  return "hover:bg-surface-gray-2";
}

// ── Block metadata ────────────────────────────────────────────────────────────
const blockMeta = computed(() => {
  const map = new Map();
  function walk(list, parentId) {
    list.forEach((block, index) => {
      const colChildren = block.columns?.flatMap((col) => col.blocks || []) ?? [];
      map.set(block.id, {
        parentId,
        index,
        childrenCount: (block.children?.length ?? 0) + colChildren.length,
        isContainer: block.type === "container",
      });
      if (block.children?.length) walk(block.children, block.id);
      if (colChildren.length) walk(colChildren, block.id);
    });
  }
  walk(store.blocks, null);
  return map;
});

function topLevelIndex(id) {
  const m = blockMeta.value.get(id);
  return m && m.parentId === null ? m.index : null;
}

// ── Inline rename ─────────────────────────────────────────────────────────────
const editingId = ref(null);
const startRename  = (id) => { editingId.value = id; };
function finishRename(id, value) {
  store.setBlockLabel(id, value);
  editingId.value = null;
}

// ── Drag-to-reorder ───────────────────────────────────────────────────────────
const dragId    = ref(null);
const dropState = ref(null);

function onDragStart(id, e) {
  dragId.value = id;
  e.dataTransfer.effectAllowed = "move";
}

function getZone(e, isContainer) {
  const rect = e.currentTarget.getBoundingClientRect();
  const ratio = (e.clientY - rect.top) / rect.height;
  if (!isContainer) return ratio < 0.5 ? "before" : "after";
  if (ratio < 0.3) return "before";
  if (ratio < 0.7) return "inside";
  return "after";
}

function isDescendant(ancestorId, nodeId) {
  let cur = blockMeta.value.get(nodeId);
  while (cur && cur.parentId != null) {
    if (cur.parentId === ancestorId) return true;
    cur = blockMeta.value.get(cur.parentId);
  }
  return false;
}

function onDragOver(id, e) {
  if (dragId.value == null || dragId.value === id || isDescendant(dragId.value, id)) {
    dropState.value = null;
    return;
  }
  const meta = blockMeta.value.get(id);
  dropState.value = { targetId: id, zone: getZone(e, meta?.isContainer) };
}

function onDrop(id) {
  const from  = dragId.value;
  const state = dropState.value;
  clearDrag();
  if (from == null || from === id || !state || isDescendant(from, id)) return;

  const meta = blockMeta.value.get(id);
  if (!meta) return;
  const { zone } = state;

  if (zone === "inside" && meta.isContainer) {
    store.moveBlockTo(from, id, meta.childrenCount);
  } else if (zone === "before") {
    store.moveBlockTo(from, meta.parentId, meta.index);
  } else {
    store.moveBlockTo(from, meta.parentId, meta.index + 1);
  }
}

function onDropAtEnd() {
  const from = dragId.value;
  clearDrag();
  if (from == null) return;
  store.moveBlockTo(from, null, store.blocks.length);
}

function clearDrag() {
  dragId.value    = null;
  dropState.value = null;
}

// ── Keyboard shortcuts ────────────────────────────────────────────────────────
function onKeyDown(e) {
  const tag = document.activeElement?.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || document.activeElement?.isContentEditable) return;

  const isMac = navigator.platform.startsWith("Mac");
  const mod = isMac ? e.metaKey : e.ctrlKey;
  if (!store.selectedBlockId) return;

  if (e.key === "Delete" || e.key === "Backspace") {
    e.preventDefault();
    store.removeBlock(store.selectedBlockId);
    return;
  }
  if (mod && e.key === "c") { e.preventDefault(); store.copyBlock(store.selectedBlockId); return; }
  if (mod && e.key === "v") { e.preventDefault(); store.pasteBlock(); return; }
}

onMounted(() => window.addEventListener("keydown", onKeyDown));
onUnmounted(() => window.removeEventListener("keydown", onKeyDown));

// ── LayerNode: recursive component ───────────────────────────────────────────
// Gets children from block.children (containers) OR block.columns[].blocks (columns).
function getChildren(block) {
  if (block.children?.length) return block.children;
  if (block.columns?.length) return block.columns.flatMap((col) => col.blocks || []);
  return [];
}

const collapsed = ref(new Set());
function toggleCollapse(id) {
  if (collapsed.value.has(id)) collapsed.value.delete(id);
  else collapsed.value.add(id);
  collapsed.value = new Set(collapsed.value); // trigger reactivity
}

const LayerNode = defineComponent({
  name: "LayerNode",
  props: {
    block:  { type: Object, required: true },
    depth:  { type: Number, default: 0 },
    isLast: { type: Boolean, default: false },
  },
  setup(props) {
    return () => {
      const b        = props.block;
      const children = getChildren(b);
      const hasKids  = children.length > 0;
      const isOpen   = !collapsed.value.has(b.id);
      const idx      = topLevelIndex(b.id);
      const dState   = dropState.value;

      // ── Row ──
      const row = h("div", {
        class: [
          "group relative flex items-center gap-1.5 px-2 py-1 mx-1 rounded-md cursor-pointer select-none transition-colors",
          rowClass(b),
        ].join(" "),
        draggable: true,
        onClick: (e) => { e.stopPropagation(); store.selectBlock(b.id); },
        onDblclick: (e) => { e.stopPropagation(); startRename(b.id); },
        onDragstart: (e) => { e.stopPropagation(); onDragStart(b.id, e); },
        onDragover:  (e) => { e.stopPropagation(); e.preventDefault(); onDragOver(b.id, e); },
        onDrop:      (e) => { e.stopPropagation(); e.preventDefault(); onDrop(b.id); },
        onDragend:   () => clearDrag(),
      }, [
        // Drop: line above
        dState?.targetId === b.id && dState.zone === "before"
          ? h("div", { class: "absolute inset-x-1 -top-px h-0.5 bg-blue-500 rounded-full pointer-events-none z-10" })
          : null,
        // Drop: ring inside
        dState?.targetId === b.id && dState.zone === "inside"
          ? h("div", { class: "absolute inset-0 rounded-md ring-2 ring-blue-400 bg-blue-50/40 pointer-events-none z-10" })
          : null,
        // Drop: line below
        dState?.targetId === b.id && dState.zone === "after"
          ? h("div", { class: "absolute inset-x-1 -bottom-px h-0.5 bg-blue-500 rounded-full pointer-events-none z-10" })
          : null,

        // Chevron or spacer
        hasKids
          ? h("button", {
              type: "button",
              class: "flex-shrink-0 w-4 h-4 flex items-center justify-center text-ink-gray-6 hover:text-ink-gray-8",
              onClick: (e) => { e.stopPropagation(); toggleCollapse(b.id); },
            }, [h(FeatherIcon, { name: isOpen ? "chevron-down" : "chevron-right", class: "w-3.5 h-3.5" })])
          : h("span", { class: "flex-shrink-0 w-4" }),

        // Icon
        h(FeatherIcon, { name: blockIcon(b.type), class: "w-3.5 h-3.5 flex-shrink-0 text-ink-gray-6" }),

        // Label (editable on dblclick)
        editingId.value === b.id
          ? h("input", {
              class: "flex-1 text-sm bg-transparent border-b border-blue-400 outline-none min-w-0 py-0.5",
              value: b.label || blockLabel(b.type),
              onBlur:    (e) => finishRename(b.id, e.target.value),
              onKeydown: (e) => {
                if (e.key === "Enter") { e.preventDefault(); finishRename(b.id, e.target.value); }
                if (e.key === "Escape") { e.preventDefault(); editingId.value = null; }
              },
              onClick:    (e) => e.stopPropagation(),
              onDblclick: (e) => e.stopPropagation(),
              onDragstart:(e) => { e.stopPropagation(); e.preventDefault(); },
              ref: (el) => el?.focus(),
            })
          : h("span", { class: "flex-1 text-sm text-ink-gray-6 truncate" }, b.label || blockLabel(b.type)),

        // Top-level index badge
        idx !== null
          ? h("span", { class: "text-xs text-ink-gray-4 flex-shrink-0 tabular-nums px-0.5" }, idx + 1)
          : null,

        // Add inside (containers only)
        b.type === "container"
          ? h("button", {
              type: "button",
              class: "opacity-0 group-hover:opacity-100 text-ink-gray-5 hover:text-blue-600 transition flex-shrink-0 w-4 h-4 flex items-center justify-center rounded hover:bg-blue-50",
              title: "Add block inside",
              onClick: (e) => { e.stopPropagation(); openPicker({ mode: "child", parentId: b.id, afterIndex: (b.children?.length ?? 1) - 1 }); },
            }, [h(FeatherIcon, { name: "plus", class: "w-3 h-3" })])
          : null,

        // Remove
        h("button", {
          type: "button",
          class: "opacity-0 group-hover:opacity-100 text-ink-gray-4 hover:text-red-500 transition flex-shrink-0 w-4 h-4 flex items-center justify-center rounded",
          title: "Remove",
          onClick: (e) => { e.stopPropagation(); store.removeBlock(b.id); },
        }, [h(FeatherIcon, { name: "x", class: "w-3 h-3" })]),
      ]);

      if (!hasKids || !isOpen) return row;

      // ── Children with guide line ──
      const childNodes = children.map((child, i) =>
        h(LayerNode, {
          key: child.id,
          block: child,
          depth: props.depth + 1,
          isLast: i === children.length - 1,
        })
      );

      const guide = h("div", {
        class: "flex",
        style: { paddingLeft: (props.depth * 16 + 20) + "px" },
      }, [
        // Vertical guide line
        h("div", { class: "w-px bg-gray-200 flex-shrink-0 mx-1 my-0.5" }),
        h("div", { class: "flex flex-col flex-1 min-w-0" }, childNodes),
      ]);

      return h("div", {}, [row, guide]);
    };
  },
});
</script>

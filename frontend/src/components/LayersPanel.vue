<template>
  <div class="flex flex-col h-full">
    <!-- Right-click context menu -->
    <Teleport to="body">
      <div
        v-if="contextMenu"
        class="fixed inset-0 z-[100]"
        @click="closeContextMenu"
        @contextmenu.prevent="closeContextMenu"
      >
        <div
          class="fixed z-[101] bg-surface-base border border-outline-gray-2 rounded-lg shadow-xl py-1 w-44"
          :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
          @click.stop
        >
          <button class="w-full text-left px-3 py-1.5 text-sm text-ink-gray-7 hover:bg-surface-gray-1 flex items-center gap-2 transition-colors" @click="menuRename">
            <FeatherIcon name="edit-2" class="w-3.5 h-3.5 shrink-0" /> Rename
          </button>
          <button class="w-full text-left px-3 py-1.5 text-sm text-ink-gray-7 hover:bg-surface-gray-1 flex items-center gap-2 transition-colors" @click="menuDuplicate">
            <FeatherIcon name="copy" class="w-3.5 h-3.5 shrink-0" /> Duplicate
          </button>
          <template v-if="store.selectedBlock?.type !== 'container'">
            <div class="h-px bg-outline-gray-1 my-0.5 mx-2" />
            <button class="w-full text-left px-3 py-1.5 text-sm text-ink-gray-7 hover:bg-surface-gray-1 flex items-center gap-2 transition-colors" @click="menuCopyStyle">
              <FeatherIcon name="droplet" class="w-3.5 h-3.5 shrink-0" /> Copy style
            </button>
            <button
              class="w-full text-left px-3 py-1.5 text-sm flex items-center gap-2 transition-colors"
              :class="store.styleClipboard ? 'text-ink-gray-7 hover:bg-surface-gray-1 cursor-pointer' : 'text-ink-gray-3 cursor-not-allowed'"
              @click="menuPasteStyle"
            >
              <FeatherIcon name="clipboard" class="w-3.5 h-3.5 shrink-0" /> Paste style
            </button>
          </template>
          <div class="h-px bg-outline-gray-1 my-0.5 mx-2" />
          <button class="w-full text-left px-3 py-1.5 text-sm text-red-500 hover:bg-red-50 flex items-center gap-2 transition-colors" @click="menuRemove">
            <FeatherIcon name="trash-2" class="w-3.5 h-3.5 shrink-0" /> Remove
          </button>
        </div>
      </div>
    </Teleport>

    <div
      v-if="!store.blocks.length"
      class="flex-1 flex flex-col items-center justify-center px-4 text-center gap-2"
    >
      <p class="text-xs text-ink-gray-4 leading-relaxed">
        No blocks yet. Use the <strong>+</strong> button in the toolbar to add your first block.
      </p>
    </div>

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
      />
    </div>

    <div v-if="store.blocks.length > 1" class="px-3 py-2 border-t border-outline-gray-1">
      <p class="text-xs text-ink-gray-3 text-center">Drag to reorder · double-click to rename</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, defineComponent, h } from "vue";
import { FeatherIcon } from "frappe-ui";
import { useEditorStore } from "../stores/editor";
import { BLOCK_SCHEMA } from "../blockSchema";

const store      = useEditorStore();
const openPicker = inject("openPicker", () => {});

// ── Right-click context menu ──────────────────────────────────────────────────
const contextMenu = ref(null);

function openContextMenu(blockId, e) {
  e.preventDefault();
  e.stopPropagation();
  store.selectBlock(blockId);
  const x = Math.min(e.clientX, window.innerWidth  - 184);
  const y = Math.min(e.clientY, window.innerHeight - 224);
  contextMenu.value = { x, y, blockId };
}
function closeContextMenu() { contextMenu.value = null; }
function menuRename()     { startRename(contextMenu.value.blockId); closeContextMenu(); }
function menuDuplicate()  { store.duplicateBlock(contextMenu.value.blockId); closeContextMenu(); }
function menuCopyStyle()  { store.copyStyle(contextMenu.value.blockId); closeContextMenu(); }
function menuPasteStyle() { if (store.styleClipboard) store.pasteStyle(contextMenu.value.blockId); closeContextMenu(); }
function menuRemove()     { store.removeBlock(contextMenu.value.blockId); closeContextMenu(); }

// INDENT_W: px per depth level. Chevron is 16px wide, so line sits at depth*INDENT_W + 8 + INDENT_W/2
const INDENT_W = 16;
const BASE_PAD = 8; // px-2 equivalent

const blockIcon  = (type) => BLOCK_SCHEMA[type]?.icon  || "box";
const blockLabel = (type) => BLOCK_SCHEMA[type]?.label || type;

function rowClass(node) {
  if (store.selectedBlockIds.has(node.id)) {
    return store.selectedBlockId === node.id
      ? "ring-1 ring-blue-400 bg-surface-gray-1"
      : "ring-1 ring-blue-200 bg-surface-gray-1";
  }
  return "hover:ring-1 hover:ring-blue-100";
}

function getChildren(block) {
  if (block.children?.length) return block.children;
  if (block.columns?.length)  return block.columns.flatMap((col) => col.blocks || []);
  return [];
}

// ── Block metadata ────────────────────────────────────────────────────────────
const blockMeta = computed(() => {
  const map = new Map();
  function walk(list, parentId, colIndex = null) {
    list.forEach((block, index) => {
      const colChildCount = block.columns?.reduce((n, col) => n + (col.blocks?.length ?? 0), 0) ?? 0;
      map.set(block.id, {
        parentId,
        index,
        colIndex,   // which column this block lives in (null = not a column child)
        childrenCount: (block.children?.length ?? 0) + colChildCount,
        isContainer: block.type === "container",
      });
      if (block.children?.length) walk(block.children, block.id, null);
      if (block.columns?.length) {
        block.columns.forEach((col, ci) => walk(col.blocks || [], block.id, ci));
      }
    });
  }
  walk(store.blocks, null, null);
  return map;
});

function topLevelIndex(id) {
  const m = blockMeta.value.get(id);
  return m && m.parentId === null ? m.index : null;
}

// ── Inline rename ─────────────────────────────────────────────────────────────
const editingId = ref(null);
function startRename(id)  { editingId.value = id; }
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
  const rect  = e.currentTarget.getBoundingClientRect();
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
    dropState.value = null; return;
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

  if (state.zone === "inside" && meta.isContainer) {
    store.moveBlockTo(from, id, meta.childrenCount);
    return;
  }

  const insertOffset = state.zone === "before" ? 0 : 1;

  // If the target block lives inside a column, use the column-aware move so the
  // dragged block lands in the correct column rather than vanishing into .children.
  if (meta.colIndex !== null) {
    store.moveBlockToColumn(from, meta.parentId, meta.colIndex, meta.index + insertOffset);
  } else {
    store.moveBlockTo(from, meta.parentId, meta.index + insertOffset);
  }
}

function onDropAtEnd() {
  const from = dragId.value;
  clearDrag();
  if (from == null) return;
  store.moveBlockTo(from, null, store.blocks.length);
}

function clearDrag() { dragId.value = null; dropState.value = null; }

// ── Flat ordered block IDs for Shift+Click range-select ───────────────────────
const flatBlockIds = computed(() => {
  const ids = [];
  function walk(list) {
    list.forEach((block) => {
      ids.push(block.id);
      if (!collapsed.value.has(block.id)) {
        const children = getChildren(block);
        if (children.length) walk(children);
      }
    });
  }
  walk(store.blocks);
  return ids;
});

// ── Multi-select click handler ────────────────────────────────────────────────
function handleLayerClick(id, e) {
  e.stopPropagation();
  const mod = e.metaKey || e.ctrlKey;
  if (e.shiftKey && store.selectedBlockId != null) {
    const from = flatBlockIds.value.indexOf(store.selectedBlockId);
    const to   = flatBlockIds.value.indexOf(id);
    if (from !== -1 && to !== -1) {
      store.addRangeToSelection(
        flatBlockIds.value.slice(Math.min(from, to), Math.max(from, to) + 1)
      );
      return;
    }
  }
  if (mod) {
    store.toggleInSelection(id);
    return;
  }
  store.selectBlock(id);
}

// ── Collapse state ────────────────────────────────────────────────────────────
const collapsed = ref(new Set());
function toggleCollapse(id) {
  const next = new Set(collapsed.value);
  next.has(id) ? next.delete(id) : next.add(id);
  collapsed.value = next;
}

// ── LayerNode ─────────────────────────────────────────────────────────────────
// All indentation is driven by `depth` on each row's paddingLeft.
// A single absolute-positioned vertical line is drawn for each expanded parent,
// placed at the horizontal center of the parent's chevron.
const LayerNode = defineComponent({
  name: "LayerNode",
  props: {
    block: { type: Object, required: true },
    depth: { type: Number, default: 0 },
  },
  setup(props) {
    return () => {
      const b          = props.block;
      const children   = getChildren(b);
      const schema     = BLOCK_SCHEMA[b.type];
      const subLayers  = (!children.length && schema?.sub_layers) ? schema.sub_layers : [];
      const hasKids    = children.length > 0 || subLayers.length > 0;
      const isOpen     = !collapsed.value.has(b.id);
      const dState   = dropState.value;
      const idx      = topLevelIndex(b.id);

      // Row left padding grows with depth
      const rowPaddingLeft = BASE_PAD + props.depth * INDENT_W;

      const row = h("div", {
        class: "group relative flex items-center gap-1.5 pr-2 py-1.5 mx-1 rounded cursor-pointer select-none transition-colors " + rowClass(b),
        style: { paddingLeft: rowPaddingLeft + "px" },
        draggable: true,
        onClick:        (e) => handleLayerClick(b.id, e),
        onDblclick:     (e) => { e.stopPropagation(); startRename(b.id); },
        onContextmenu:  (e) => openContextMenu(b.id, e),
        onDragstart:    (e) => { e.stopPropagation(); onDragStart(b.id, e); },
        onDragover:     (e) => { e.stopPropagation(); e.preventDefault(); onDragOver(b.id, e); },
        onDrop:         (e) => { e.stopPropagation(); e.preventDefault(); onDrop(b.id); },
        onDragend:      ()  => clearDrag(),
      }, [
        dState?.targetId === b.id && dState.zone === "before"
          ? h("div", { class: "absolute inset-x-1 -top-px h-0.5 bg-blue-500 rounded-full pointer-events-none z-10" }) : null,
        dState?.targetId === b.id && dState.zone === "inside"
          ? h("div", { class: "absolute inset-0 rounded-md ring-2 ring-blue-400 bg-blue-50/40 pointer-events-none z-10" }) : null,
        dState?.targetId === b.id && dState.zone === "after"
          ? h("div", { class: "absolute inset-x-1 -bottom-px h-0.5 bg-blue-500 rounded-full pointer-events-none z-10" }) : null,

        hasKids
          ? h("button", {
              type: "button",
              class: "flex-shrink-0 w-4 h-4 flex items-center justify-center text-ink-gray-6 hover:text-ink-gray-8",
              onClick: (e) => { e.stopPropagation(); toggleCollapse(b.id); },
            }, [h(FeatherIcon, { name: isOpen ? "chevron-down" : "chevron-right", class: "w-3.5 h-3.5" })])
          : h("span", { class: "flex-shrink-0 w-4" }),

        h(FeatherIcon, { name: blockIcon(b.type), class: "w-3.5 h-3.5 flex-shrink-0 text-ink-gray-6" }),

        editingId.value === b.id
          ? h("input", {
              class: "flex-1 text-sm bg-transparent border-b border-blue-400 outline-none min-w-0 py-0.5",
              value: b.label || blockLabel(b.type),
              onBlur:    (e) => finishRename(b.id, e.target.value),
              onKeydown: (e) => {
                if (e.key === "Enter")  { e.preventDefault(); finishRename(b.id, e.target.value); }
                if (e.key === "Escape") { e.preventDefault(); editingId.value = null; }
              },
              onClick:    (e) => e.stopPropagation(),
              onDblclick: (e) => e.stopPropagation(),
              onDragstart:(e) => { e.stopPropagation(); e.preventDefault(); },
              onVnodeMounted: ({ el }) => { el?.focus(); el?.select(); },
            })
          : h("span", { class: "flex-1 text-sm text-ink-gray-6 truncate" }, b.label || blockLabel(b.type)),

        idx !== null
          ? h("span", { class: "text-xs text-ink-gray-4 flex-shrink-0 tabular-nums px-0.5" }, idx + 1)
          : null,

        b.type === "container"
          ? h("button", {
              type: "button",
              class: "opacity-0 group-hover:opacity-100 text-ink-gray-5 hover:text-blue-600 transition flex-shrink-0 w-4 h-4 flex items-center justify-center rounded hover:bg-blue-50",
              title: "Add block inside",
              onClick: (e) => { e.stopPropagation(); openPicker({ mode: "child", parentId: b.id, afterIndex: (b.children?.length ?? 1) - 1 }); },
            }, [h(FeatherIcon, { name: "plus", class: "w-3 h-3" })])
          : null,

        h("button", {
          type: "button",
          class: (store.selectedBlockId === b.id
            ? "opacity-100 pointer-events-auto"
            : "opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto")
            + " text-ink-gray-4 hover:text-red-500 transition flex-shrink-0 w-4 h-4 flex items-center justify-center rounded",
          title: "Remove",
          onClick: (e) => { e.stopPropagation(); store.removeBlock(b.id); },
        }, [h(FeatherIcon, { name: "x", class: "w-3 h-3" })]),
      ]);

      if (!hasKids || !isOpen) return row;

      // Guide line: absolute, left = mx-1(4px) + paddingLeft + half chevron(8px)
      const lineLeft = 4 + rowPaddingLeft + 8;
      const subLayerPad = rowPaddingLeft + INDENT_W;

      const subLayerRows = subLayers.map((sl) =>
        h("div", {
          class: "flex items-center gap-1.5 pr-2 py-1 mx-1 rounded cursor-pointer transition-colors hover:bg-surface-gray-1",
          style: { paddingLeft: subLayerPad + "px" },
          onClick: (e) => { e.stopPropagation(); store.selectBlock(b.id); },
        }, [
          h("span", { class: "flex-shrink-0 w-4" }),
          h(FeatherIcon, { name: sl.icon, class: "w-3 h-3 flex-shrink-0 text-ink-gray-3" }),
          h("span", { class: "text-xs text-ink-gray-3 truncate" }, sl.label),
        ])
      );

      const childrenSection = h("div", { class: "relative" }, [
        h("div", {
          class: "absolute top-0 bottom-0 w-px bg-outline-gray-2",
          style: { left: lineLeft + "px" },
        }),
        ...children.map((child) =>
          h(LayerNode, { key: child.id, block: child, depth: props.depth + 1 })
        ),
        ...subLayerRows,
      ]);

      return h("div", [row, childrenSection]);
    };
  },
});
</script>

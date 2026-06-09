import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { BLOCK_SCHEMA } from "../blockSchema";

export const useEditorStore = defineStore("editor", () => {
  const blocks         = ref([]);
  const renderedHtml   = ref("");
  const campaignName   = ref("");
  const campaignDoc    = ref(null);
  const selectedBlockId = ref(null);
  const isDirty        = ref(false);

  // ID counter lives inside the store so it resets correctly with the store
  // and is not shared as a stale module-level variable across HMR reloads.
  const _idCounter = ref(0);
  function nextId() { return ++_idCounter.value; }

  function markDirty() { isDirty.value = true; }
  function clearDirty() { isDirty.value = false; }

  // ── Recursive helpers ────────────────────────────────────────────────────────
  function findBlock(id, list = blocks.value) {
    for (const b of list) {
      if (b.id === id) return b;
      if (b.children?.length) {
        const found = findBlock(id, b.children);
        if (found) return found;
      }
    }
    return null;
  }

  const selectedBlock = computed(() => findBlock(selectedBlockId.value));

  // ── Top-level block operations ───────────────────────────────────────────────
  function addBlock(type, afterIndex = null) {
    const newBlock = _createBlock(type, nextId());
    if (afterIndex === null || afterIndex === undefined) {
      blocks.value.push(newBlock);
    } else if (afterIndex < 0) {
      blocks.value.unshift(newBlock);
    } else {
      blocks.value.splice(afterIndex + 1, 0, newBlock);
    }
    selectedBlockId.value = newBlock.id;
    markDirty();
  }

  function removeBlock(id) {
    function removeFrom(list) {
      const idx = list.findIndex((b) => b.id === id);
      if (idx !== -1) { list.splice(idx, 1); return true; }
      for (const b of list) {
        if (b.children && removeFrom(b.children)) return true;
      }
      return false;
    }
    removeFrom(blocks.value);
    if (selectedBlockId.value === id) selectedBlockId.value = null;
    markDirty();
  }

  function moveBlock(fromIndex, toIndex) {
    const item = blocks.value.splice(fromIndex, 1)[0];
    blocks.value.splice(toIndex, 0, item);
    markDirty();
  }

  function selectBlock(id) {
    selectedBlockId.value = id;
  }

  function updateBlockProps(id, props) {
    const block = findBlock(id);
    if (block) { Object.assign(block.props, props); markDirty(); }
  }

  // ── Child block operations (for containers) ──────────────────────────────────
  function addChildBlock(parentId, type, afterIndex = null) {
    const parent = findBlock(parentId);
    if (!parent) return;
    if (!parent.children) parent.children = [];
    const newBlock = _createBlock(type, nextId());
    if (afterIndex === null || afterIndex === undefined) {
      parent.children.push(newBlock);
    } else if (afterIndex < 0) {
      parent.children.unshift(newBlock);
    } else {
      parent.children.splice(afterIndex + 1, 0, newBlock);
    }
    selectedBlockId.value = newBlock.id;
    markDirty();
  }

  function moveChildBlock(parentId, fromIndex, toIndex) {
    const parent = findBlock(parentId);
    if (!parent?.children) return;
    const item = parent.children.splice(fromIndex, 1)[0];
    parent.children.splice(toIndex, 0, item);
    markDirty();
  }

  // Move any block to any location (cross-level drag from the layers panel)
  function moveBlockTo(blockId, targetParentId, targetIndex) {
    if (targetParentId !== null && _isDescendant(blockId, targetParentId)) return;

    let moved = null;
    function detach(list) {
      const idx = list.findIndex((b) => b.id === blockId);
      if (idx !== -1) { moved = list.splice(idx, 1)[0]; return true; }
      for (const b of list) {
        if (b.children && detach(b.children)) return true;
      }
      return false;
    }
    detach(blocks.value);
    if (!moved) return;

    if (targetParentId === null) {
      const idx = Math.min(targetIndex, blocks.value.length);
      blocks.value.splice(idx, 0, moved);
    } else {
      const parent = findBlock(targetParentId);
      if (parent) {
        if (!parent.children) parent.children = [];
        const idx = Math.min(targetIndex, parent.children.length);
        parent.children.splice(idx, 0, moved);
      }
    }
    markDirty();
  }

  function _isDescendant(blockId, ofId) {
    const ancestor = findBlock(ofId);
    if (!ancestor?.children) return false;
    function check(list) {
      for (const b of list) {
        if (b.id === blockId) return true;
        if (b.children && check(b.children)) return true;
      }
      return false;
    }
    return check(ancestor.children);
  }

  function duplicateBlock(id) {
    // Deep-clone the block, assign fresh IDs to it and all descendants
    function cloneWithNewIds(b) {
      const clone = JSON.parse(JSON.stringify(b));
      clone.id = nextId();
      if (clone.children) clone.children = clone.children.map(cloneWithNewIds);
      return clone;
    }

    // Try top-level first
    const topIdx = blocks.value.findIndex((b) => b.id === id);
    if (topIdx !== -1) {
      const clone = cloneWithNewIds(blocks.value[topIdx]);
      blocks.value.splice(topIdx + 1, 0, clone);
      selectedBlockId.value = clone.id;
      markDirty();
      return;
    }

    // Try inside containers
    function duplicateIn(list) {
      for (let i = 0; i < list.length; i++) {
        if (list[i].id === id) {
          const clone = cloneWithNewIds(list[i]);
          list.splice(i + 1, 0, clone);
          selectedBlockId.value = clone.id;
          markDirty();
          return true;
        }
        if (list[i].children && duplicateIn(list[i].children)) return true;
      }
      return false;
    }
    duplicateIn(blocks.value);
  }

  function setBlockLabel(id, label) {
    const block = findBlock(id);
    if (!block) return;
    const trimmed = label?.trim();
    if (trimmed) block.label = trimmed;
    else delete block.label;
    markDirty();
  }

  // ── Persistence ──────────────────────────────────────────────────────────────
  function setRenderedHtml(html) {
    renderedHtml.value = html;
  }

  function _assignIds(list) {
    return (list || []).map((b) => ({
      ...b,
      id: nextId(),
      children: b.children
        ? _assignIds(b.children)
        : (b.type === "container" ? [] : undefined),
    }));
  }

  function loadFromDoc(doc) {
    campaignDoc.value  = doc;
    campaignName.value = doc.title;
    _idCounter.value   = 0;
    selectedBlockId.value = null;
    blocks.value = _assignIds(doc.blocks || []);
    clearDirty();
  }

  return {
    blocks,
    renderedHtml,
    campaignName,
    campaignDoc,
    selectedBlockId,
    selectedBlock,
    isDirty,
    addBlock,
    removeBlock,
    moveBlock,
    selectBlock,
    updateBlockProps,
    addChildBlock,
    moveChildBlock,
    moveBlockTo,
    duplicateBlock,
    setBlockLabel,
    setRenderedHtml,
    loadFromDoc,
    findBlock,
    markDirty,
    clearDirty,
  };
});

// ── Block factory ─────────────────────────────────────────────────────────────
// Defaults come from BLOCK_SCHEMA[type].defaults — single source of truth.
// No separate defaultProps() function needed.
function _createBlock(type, id) {
  const defaults = BLOCK_SCHEMA[type]?.defaults ?? {};
  return {
    id,
    type,
    // Spread a deep copy of defaults so mutations on one block don't affect others
    // (only relevant for object/array props like `columns` in the columns block).
    props: JSON.parse(JSON.stringify(defaults)),
    ...(type === "container" ? { children: [] } : {}),
  };
}

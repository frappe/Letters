<template>
  <div class="flex flex-col h-full">
    <!-- Empty state -->
    <div
      v-if="!store.blocks.length"
      class="flex-1 flex flex-col items-center justify-center px-4 text-center gap-2"
    >
      <p class="text-xs text-gray-400 leading-relaxed">
        No blocks yet. Switch to <strong>Blocks</strong> to add some.
      </p>
    </div>

    <!-- Layer rows -->
    <ul v-else class="flex-1 overflow-y-auto py-1.5">
      <li
        v-for="(block, index) in store.blocks"
        :key="block.id"
        class="flex items-center gap-2 mx-2 my-0.5 px-2 py-2 rounded-lg cursor-pointer transition-colors select-none group"
        :class="store.selectedBlockId === block.id
          ? 'bg-blue-50 text-blue-700'
          : 'text-gray-600 hover:bg-gray-100'"
        draggable="true"
        @dragstart="onDragStart(index)"
        @dragover.prevent="onDragOver(index)"
        @drop.prevent="onDrop(index)"
        @dragend="onDragEnd"
        @click="store.selectBlock(block.id)"
      >
        <!-- Drag handle -->
        <span
          class="text-gray-300 group-hover:text-gray-400 cursor-grab active:cursor-grabbing text-sm leading-none flex-shrink-0"
          title="Drag to reorder"
        >⠿</span>

        <!-- Block icon + label -->
        <span class="text-sm leading-none flex-shrink-0">{{ blockIcon(block.type) }}</span>
        <span class="flex-1 text-xs font-medium truncate capitalize">
          {{ blockLabel(block.type) }}
        </span>
        <span class="text-xs text-gray-300 flex-shrink-0 tabular-nums">{{ index + 1 }}</span>

        <!-- Delete -->
        <button
          type="button"
          class="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-500 transition-all text-xs leading-none flex-shrink-0 w-4 h-4 flex items-center justify-center rounded"
          title="Remove"
          @click.stop="store.removeBlock(block.id)"
        >✕</button>
      </li>
    </ul>

    <!-- Reorder hint -->
    <div v-if="store.blocks.length > 1" class="px-3 py-2 border-t border-gray-100">
      <p class="text-xs text-gray-300 text-center">Drag rows to reorder</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useEditorStore } from "../stores/editor";
import { BLOCK_SCHEMA } from "../blockSchema";

const store = useEditorStore();

function blockIcon(type) {
  return BLOCK_SCHEMA[type]?.icon || "□";
}
function blockLabel(type) {
  return BLOCK_SCHEMA[type]?.label || type;
}

// Drag-to-reorder within the layers list
const dragFrom = ref(null);

function onDragStart(index) {
  dragFrom.value = index;
}
function onDragOver(index) {
  // visual hint handled by browser
}
function onDrop(toIndex) {
  if (dragFrom.value !== null && dragFrom.value !== toIndex) {
    store.moveBlock(dragFrom.value, toIndex);
  }
}
function onDragEnd() {
  dragFrom.value = null;
}
</script>

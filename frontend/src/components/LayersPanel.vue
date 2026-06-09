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
      <template v-for="(block, index) in store.blocks" :key="block.id">
        <li
          class="relative flex items-center gap-2 mx-2 my-0.5 px-2 py-2 rounded-lg cursor-pointer transition-colors select-none group"
          :class="store.selectedBlockId === block.id
            ? 'bg-blue-50 text-blue-700'
            : 'text-gray-600 hover:bg-gray-100'"
          draggable="true"
          @dragstart="onDragStart(index, $event)"
          @dragover.prevent="onDragOver(index, $event)"
          @drop.prevent="onDrop(index)"
          @dragend="onDragEnd"
          @click="store.selectBlock(block.id)"
        >
          <!-- Drop indicator lines -->
          <div
            v-if="dropIndicator === index"
            class="absolute inset-x-0 -top-px h-0.5 bg-blue-500 rounded-full pointer-events-none z-10"
          />
          <div
            v-if="dropIndicator === index + 0.5"
            class="absolute inset-x-0 -bottom-px h-0.5 bg-blue-500 rounded-full pointer-events-none z-10"
          />
          <!-- Drag handle -->
          <span
            class="text-gray-300 group-hover:text-gray-400 cursor-grab active:cursor-grabbing text-sm leading-none flex-shrink-0"
            title="Drag to reorder"
          >⠿</span>
          <!-- Block icon + label -->
          <FeatherIcon :name="blockIcon(block.type)" class="w-3 h-3 flex-shrink-0" />
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

        <!-- Children of container blocks (indented) -->
        <template v-if="block.type === 'container' && block.children?.length">
          <li
            v-for="(child, ci) in block.children"
            :key="child.id"
            class="relative flex items-center gap-2 ml-6 mr-2 my-0.5 px-2 py-1.5 rounded-lg cursor-pointer transition-colors select-none group"
            :class="store.selectedBlockId === child.id
              ? 'bg-blue-50 text-blue-700'
              : 'text-gray-500 hover:bg-gray-100'"
            @click="store.selectBlock(child.id)"
          >
            <!-- Tree line -->
            <div class="absolute left-0 top-0 bottom-0 w-px bg-gray-200 -translate-x-2" />
            <div class="w-2 h-px bg-gray-200 flex-shrink-0 -ml-1" />
            <FeatherIcon :name="blockIcon(child.type)" class="w-3 h-3 flex-shrink-0 opacity-70" />
            <span class="flex-1 text-xs truncate capitalize opacity-80">
              {{ blockLabel(child.type) }}
            </span>
            <button
              type="button"
              class="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-500 transition-all text-xs leading-none flex-shrink-0 w-4 h-4 flex items-center justify-center rounded"
              title="Remove"
              @click.stop="store.removeBlock(child.id)"
            >✕</button>
          </li>
        </template>
      </template>
    </ul>

    <!-- Reorder hint -->
    <div v-if="store.blocks.length > 1" class="px-3 py-2 border-t border-gray-100">
      <p class="text-xs text-gray-300 text-center">Drag rows to reorder</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { FeatherIcon } from "frappe-ui";
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
// dropIndicator: integer = before that row, n+0.5 = after last row
const dropIndicator = ref(null);

function onDragStart(index, e) {
  dragFrom.value = index;
  e.dataTransfer.effectAllowed = "move";
}

function onDragOver(index, e) {
  if (dragFrom.value === null) return;
  const rect = e.currentTarget.getBoundingClientRect();
  const after = e.clientY > rect.top + rect.height / 2;
  // Show line above or below this row
  dropIndicator.value = after ? index + 0.5 : index;
}

function onDrop(toIndex) {
  const from = dragFrom.value;
  if (from === null) return;
  // Determine whether we dropped in the upper or lower half
  const insertAfter = dropIndicator.value !== null && dropIndicator.value > toIndex;
  let dest = insertAfter ? toIndex + 1 : toIndex;
  if (from < dest) dest--;
  dragFrom.value = null;
  dropIndicator.value = null;
  if (from !== dest) store.moveBlock(from, dest);
}

function onDragEnd() {
  dragFrom.value = null;
  dropIndicator.value = null;
}
</script>

<template>
  <aside class="w-72 flex-shrink-0 bg-white border-l border-gray-200 flex flex-col overflow-hidden">
    <div class="px-4 py-3 border-b border-gray-200">
      <span class="text-xs font-semibold text-gray-500 uppercase tracking-widest">
        {{ schema ? schema.label + " settings" : "Properties" }}
      </span>
    </div>

    <!-- No selection -->
    <div
      v-if="!block"
      class="flex-1 flex items-center justify-center px-6 text-center"
    >
      <p class="text-sm text-gray-400 leading-relaxed">
        Select a block on the canvas to edit its colors, alignment, and other properties.
      </p>
    </div>

    <!-- Selected block controls -->
    <div v-else class="flex-1 overflow-y-auto px-4 py-4 space-y-4">
      <div v-for="field in schema.fields" :key="field.key">
        <label class="block text-xs font-medium text-gray-600 mb-1.5">{{ field.label }}</label>

        <!-- Color -->
        <div v-if="field.type === 'color'" class="flex items-center gap-2">
          <input
            type="color"
            :value="value(field.key)"
            @input="set(field.key, $event.target.value)"
            class="w-9 h-9 rounded cursor-pointer border border-gray-200 p-0.5 bg-white"
          />
          <input
            type="text"
            :value="value(field.key)"
            @change="set(field.key, $event.target.value)"
            class="flex-1 border border-gray-200 rounded-lg px-2.5 py-1.5 text-sm text-gray-700 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <!-- Select -->
        <select
          v-else-if="field.type === 'select'"
          :value="value(field.key)"
          @change="set(field.key, coerce(field, $event.target.value))"
          class="w-full border border-gray-200 rounded-lg px-2.5 py-1.5 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option v-for="opt in field.options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>

        <!-- Alignment segmented control -->
        <div v-else-if="field.type === 'align'" class="flex rounded-lg border border-gray-200 overflow-hidden">
          <button
            v-for="opt in alignOptions"
            :key="opt.value"
            type="button"
            class="flex-1 py-1.5 text-sm transition-colors"
            :class="value(field.key) === opt.value
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-500 hover:bg-gray-50'"
            @click="set(field.key, opt.value)"
          >{{ opt.icon }}</button>
        </div>

        <!-- Number -->
        <input
          v-else-if="field.type === 'number'"
          type="number"
          :min="field.min"
          :max="field.max"
          :value="value(field.key)"
          @input="set(field.key, Number($event.target.value))"
          class="w-full border border-gray-200 rounded-lg px-2.5 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <!-- Text (default) -->
        <input
          v-else
          type="text"
          :placeholder="field.placeholder || ''"
          :value="value(field.key)"
          @change="set(field.key, $event.target.value)"
          class="w-full border border-gray-200 rounded-lg px-2.5 py-1.5 text-sm text-gray-700 placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <!-- Block actions -->
      <div class="pt-3 mt-2 border-t border-gray-100">
        <button
          type="button"
          class="w-full text-sm text-red-500 hover:text-red-600 hover:bg-red-50 rounded-lg py-2 transition-colors"
          @click="store.removeBlock(block.id)"
        >
          Delete block
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from "vue";
import { useEditorStore } from "../stores/editor";
import { BLOCK_SCHEMA } from "../blockSchema";

const store = useEditorStore();

const block = computed(() => store.selectedBlock);
const schema = computed(() => (block.value ? BLOCK_SCHEMA[block.value.type] : null));

const alignOptions = [
  { value: "left", icon: "⇤" },
  { value: "center", icon: "⇆" },
  { value: "right", icon: "⇥" },
];

function value(key) {
  return block.value?.props?.[key];
}

function set(key, val) {
  if (block.value) store.updateBlockProps(block.value.id, { [key]: val });
}

// Select options can carry non-string values (e.g. thickness numbers).
function coerce(field, raw) {
  const opt = field.options?.find((o) => String(o.value) === String(raw));
  return opt ? opt.value : raw;
}
</script>

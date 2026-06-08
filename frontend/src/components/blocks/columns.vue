<template>
  <BlockWrapper :block="block" :index="index">
    <div
      class="px-6 py-5 flex gap-4"
      :style="{ backgroundColor: block.props.background_color }"
    >
      <div
        v-for="(col, i) in columns"
        :key="i"
        class="flex-1 flex flex-col gap-2 min-w-0"
      >
        <!-- Heading -->
        <div
          class="font-semibold text-base outline-none leading-tight text-gray-900"
          :style="{ color: block.props.heading_color || '#111827' }"
          contenteditable="true"
          @blur="updateCol(i, 'heading', $event.target.innerText)"
          @click.stop="store.selectBlock(block.id)"
        >{{ col.heading }}</div>

        <!-- Body text -->
        <div
          class="text-sm outline-none leading-relaxed text-gray-600"
          :style="{ color: block.props.text_color || '#6b7280' }"
          contenteditable="true"
          @blur="updateCol(i, 'text', $event.target.innerText)"
          @click.stop="store.selectBlock(block.id)"
        >{{ col.text }}</div>

        <!-- Optional button -->
        <div v-if="col.button_label" class="mt-1">
          <a
            :href="col.button_url || '#'"
            class="inline-block text-xs font-semibold px-4 py-1.5 rounded"
            :style="{ backgroundColor: block.props.button_color || '#111827', color: '#ffffff' }"
            @click.prevent
          >{{ col.button_label }}</a>
        </div>
      </div>
    </div>
  </BlockWrapper>
</template>

<script setup>
import { computed, watch } from "vue";
import BlockWrapper from "../BlockWrapper.vue";
import { useEditorStore } from "../../stores/editor";

const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();

// Computed columns array from props.columns (always kept in sync with column_count)
const columns = computed(() => props.block.props.columns || []);

// When column_count changes in the Inspector, resize the columns array
watch(
  () => props.block.props.column_count,
  (count) => {
    const n = parseInt(count) || 2;
    const current = [...(props.block.props.columns || [])];
    while (current.length < n) {
      current.push({
        heading: `Column ${current.length + 1}`,
        text: "Add your description here.",
        button_label: "",
        button_url: "",
      });
    }
    const trimmed = current.slice(0, n);
    store.updateBlockProps(props.block.id, { columns: trimmed });
  }
);

function updateCol(index, key, value) {
  const updated = props.block.props.columns.map((col, i) =>
    i === index ? { ...col, [key]: value } : col
  );
  store.updateBlockProps(props.block.id, { columns: updated });
}
</script>

<template>
  <BlockWrapper :block="block" :index="index">
    <div
      :style="{
        backgroundColor: block.props.background_color || '#f8fafc',
        border: `1px solid ${block.props.border_color || '#e2e8f0'}`,
        borderRadius: block.props.border_radius || '12px',
        ...paddingStyle,
      }"
      class="transition-all"
    >
      <!-- Optional heading -->
      <div
        v-if="block.props.heading !== undefined"
        class="font-semibold text-base outline-none mb-1.5 leading-snug text-gray-800"
        contenteditable="true"
        :data-placeholder="!block.props.heading ? 'Heading (optional)…' : ''"
        @blur="update('heading', $event.target.innerText)"
        @click.stop="store.selectBlock(block.id)"
      >{{ block.props.heading }}</div>

      <!-- Optional body text -->
      <div
        v-if="block.props.text !== undefined"
        class="text-sm outline-none leading-relaxed text-gray-500"
        contenteditable="true"
        :data-placeholder="!block.props.text ? 'Body text (optional)…' : ''"
        @blur="update('text', $event.target.innerText)"
        @click.stop="store.selectBlock(block.id)"
      >{{ block.props.text }}</div>

      <!-- Placeholder when both heading & text are empty -->
      <div
        v-if="!block.props.heading && !block.props.text"
        class="text-xs text-gray-300 text-center py-2 select-none pointer-events-none"
      >Container — add a heading or text in the Inspector</div>
    </div>
  </BlockWrapper>
</template>

<script setup>
import { computed } from "vue";
import BlockWrapper from "../BlockWrapper.vue";
import { useEditorStore } from "../../stores/editor";
import { usePadding } from "../../composables/usePadding";

const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();
function update(key, val) { store.updateBlockProps(props.block.id, { [key]: val }); }

const blockProps = computed(() => props.block.props);
const paddingStyle = usePadding(blockProps, { top: 24, right: 24, bottom: 24, left: 24 });
</script>

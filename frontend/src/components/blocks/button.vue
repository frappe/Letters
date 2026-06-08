<template>
  <BlockWrapper :block="block" :index="index">
    <div class="px-8 py-5">
      <div :class="alignClass">
        <span
          class="inline-block rounded px-6 py-2.5 font-semibold cursor-text outline-none"
          :style="{ backgroundColor: block.props.color, color: block.props.text_color }"
          contenteditable="true"
          @blur="update('label', $event.target.innerText)"
          @click.stop="store.selectBlock(block.id)"
        >{{ block.props.label }}</span>
      </div>
    </div>
  </BlockWrapper>
</template>

<script setup>
import BlockWrapper from "../BlockWrapper.vue";
import { computed } from "vue";
import { useEditorStore } from "../../stores/editor";
const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();
function update(key, val) { store.updateBlockProps(props.block.id, { [key]: val }); }
const alignClass = computed(() => ({
  'text-left': props.block.props.align === 'left',
  'text-center': props.block.props.align === 'center',
  'text-right': props.block.props.align === 'right',
}));
</script>

<template>
  <BlockWrapper :block="block" :index="index">
    <div
      class="text-center"
      :style="{ backgroundColor: block.props.background_color, ...paddingStyle }"
    >
      <div
        class="text-xs leading-relaxed outline-none"
        :style="{ color: block.props.text_color }"
        contenteditable="true"
        @blur="update('text', $event.target.innerText)"
        @click.stop="store.selectBlock(block.id)"
      >{{ block.props.text }}</div>
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
const paddingStyle = usePadding(blockProps);
</script>

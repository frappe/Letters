<template>
  <BlockWrapper :block="block" :index="index">
    <div
      class="px-8 py-5 text-center"
      :style="{ backgroundColor: block.props.background_color }"
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
import BlockWrapper from "../BlockWrapper.vue";
import { useEditorStore } from "../../stores/editor";
const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();
function update(key, val) { store.updateBlockProps(props.block.id, { [key]: val }); }
</script>

<template>
  <BlockWrapper :block="block" :index="index">
    <div class="px-8 py-5">
      <div
        class="outline-none min-h-10 leading-relaxed text-gray-700"
        :style="{ textAlign: block.props.align, fontSize: block.props.font_size }"
        contenteditable="true"
        @blur="update('content', $event.target.innerText)"
        @click.stop="store.selectBlock(block.id)"
      >{{ block.props.content }}</div>
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

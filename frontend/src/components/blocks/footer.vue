<template>
  <BlockWrapper :block="block" :index="index">
    <div
      class="text-center"
      :style="{ backgroundColor: block.props.background_color, ...paddingStyle }"
    >
      <div
        ref="textRef"
        class="text-xs leading-relaxed outline-none"
        :style="{ color: block.props.text_color }"
        contenteditable="true"
        @focus="onFocus"
        @blur="onBlur"
        @paste.prevent="onPaste"
        @keydown="onKeydown"
        @click.stop="store.selectBlock(block.id)"
      />
    </div>
  </BlockWrapper>
</template>

<script setup>
import { computed } from "vue";
import BlockWrapper from "../BlockWrapper.vue";
import { useEditorStore } from "../../stores/editor";
import { usePadding } from "../../composables/usePadding";
import { useContentEditable } from "../../composables/useContentEditable";

const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();
function update(key, val) { store.updateBlockProps(props.block.id, { [key]: val }); }

const blockProps = computed(() => props.block.props);
const paddingStyle = usePadding(blockProps);

const { elRef: textRef, onFocus, onBlur, onPaste, onKeydown } = useContentEditable(
  () => props.block.props.text,
  (val) => update("text", val)
);
</script>

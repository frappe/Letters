<template>
  <BlockWrapper :block="block" :index="index">
    <div
      :style="{
        backgroundColor: block.props.background_color,
        padding: paddingValue,
      }"
      :class="textAlignClass"
    >
      <div
        class="font-bold outline-none mb-2 leading-tight"
        :style="{ color: block.props.heading_color, fontSize: block.props.heading_size || '30px' }"
        contenteditable="true"
        @blur="update('heading', $event.target.innerText)"
        @click.stop="store.selectBlock(block.id)"
      >{{ block.props.heading }}</div>
      <div
        class="text-base outline-none leading-relaxed"
        :style="{ color: block.props.subheading_color }"
        contenteditable="true"
        @blur="update('subheading', $event.target.innerText)"
        @click.stop="store.selectBlock(block.id)"
      >{{ block.props.subheading }}</div>
    </div>
  </BlockWrapper>
</template>

<script setup>
import { computed } from "vue";
import BlockWrapper from "../BlockWrapper.vue";
import { useEditorStore } from "../../stores/editor";
const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();
function update(key, val) { store.updateBlockProps(props.block.id, { [key]: val }); }

const paddingValue = computed(() => {
  const map = { compact: "24px 32px", normal: "40px 32px", spacious: "64px 32px" };
  return map[props.block.props.padding] || "40px 32px";
});

const textAlignClass = computed(() => ({
  "text-left":   props.block.props.text_align === "left",
  "text-center": props.block.props.text_align === "center" || !props.block.props.text_align,
  "text-right":  props.block.props.text_align === "right",
}));
</script>

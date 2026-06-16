<template>
  <BlockWrapper :block="block" :index="index">
    <!-- Horizontal -->
    <div v-if="!vertical" :style="paddingStyle" class="flex" :class="alignClass">
      <div :style="lineStyleH" />
    </div>

    <!-- Vertical: fixed height, centered -->
    <div
      v-else
      :style="{ ...paddingStyle, display: 'flex', flexDirection: 'column', alignItems: 'center' }"
    >
      <div :style="lineStyleV" />
    </div>
  </BlockWrapper>
</template>

<script setup>
import { computed } from "vue";
import BlockWrapper from "../BlockWrapper.vue";
import { usePadding } from "../../composables/usePadding";

const props = defineProps({ block: Object, index: Number });

const blockProps = computed(() => props.block.props);
const paddingStyle = usePadding(blockProps, { top: 16, right: 16, bottom: 16, left: 16 });

const vertical  = computed(() => props.block.props.orientation === "vertical");
const color     = computed(() => props.block.props.border_color || "#e5e7eb");
const thick     = computed(() => props.block.props.thickness ?? 1);
const lineStyle = computed(() => props.block.props.style || "solid");
const lineH     = computed(() => (props.block.props.height ?? 80));

const lineStyleH = computed(() => ({
  width:           props.block.props.width || "100%",
  height:          thick.value + "px",
  backgroundColor: lineStyle.value === "solid" ? color.value : "transparent",
  borderTop:       lineStyle.value !== "solid"
    ? `${thick.value}px ${lineStyle.value} ${color.value}`
    : "none",
}));

const lineStyleV = computed(() => ({
  width:           thick.value + "px",
  height:          lineH.value + "px",
  backgroundColor: lineStyle.value === "solid" ? color.value : "transparent",
  borderLeft:      lineStyle.value !== "solid"
    ? `${thick.value}px ${lineStyle.value} ${color.value}`
    : "none",
}));

const alignClass = computed(() => {
  const a = props.block.props.align || "center";
  return a === "left" ? "justify-start" : a === "right" ? "justify-end" : "justify-center";
});
</script>

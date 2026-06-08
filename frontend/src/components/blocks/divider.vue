<template>
  <BlockWrapper :block="block" :index="index">
    <div :style="paddingStyle">
      <div
        :style="{
          height: block.props.thickness + 'px',
          backgroundColor: block.props.style === 'solid' ? block.props.border_color : 'transparent',
          borderTop: block.props.style !== 'solid'
            ? `${block.props.thickness}px ${block.props.style} ${block.props.border_color}`
            : 'none',
        }"
      />
    </div>
  </BlockWrapper>
</template>

<script setup>
import { computed } from "vue";
import BlockWrapper from "../BlockWrapper.vue";
import { usePadding } from "../../composables/usePadding";
const props = defineProps({ block: Object, index: Number });

const blockProps = computed(() => props.block.props);
const paddingStyle = usePadding(blockProps, { top: 16, right: 32, bottom: 16, left: 32 });
</script>

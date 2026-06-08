<template>
  <BlockWrapper :block="block" :index="index">
    <div class="px-8 py-4">
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
import BlockWrapper from "../BlockWrapper.vue";
const props = defineProps({ block: Object, index: Number });
</script>

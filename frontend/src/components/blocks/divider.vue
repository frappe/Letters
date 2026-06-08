<template>
  <BlockWrapper :block="block" :index="index">
    <div class="px-8 py-4">
      <hr
        :style="{
          borderColor: block.props.border_color,
          borderTopWidth: block.props.thickness + 'px',
          borderTopStyle: block.props.style,
        }"
        class="border-0"
      />
    </div>
  </BlockWrapper>
</template>

<script setup>
import BlockWrapper from "../BlockWrapper.vue";
const props = defineProps({ block: Object, index: Number });
</script>

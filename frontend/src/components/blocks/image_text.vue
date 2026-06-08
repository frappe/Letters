<template>
  <div class="block-wrapper" :data-type="block.type">
    <pre>{{ block }}</pre>
  </div>
</template>
<script setup>
defineProps({ block: Object, index: Number });
</script>

<template>
  <component :is="resolvedComp" :block="block" :index="index" />
</template>

<script setup>
import { computed, defineAsyncComponent } from "vue";
import ContainerBlock from "./blocks/container.vue";

const props = defineProps({
  block: { type: Object, required: true },
  index: { type: Number, default: 0 },
});

// Module-level cache so async components are only created once
const _cache = {};

function getComp(type) {
  if (type === "container") return ContainerBlock;
  if (!_cache[type]) {
    _cache[type] = defineAsyncComponent(() => import(`./blocks/${type}.vue`));
  }
  return _cache[type];
}

const resolvedComp = computed(() => getComp(props.block.type));
</script>

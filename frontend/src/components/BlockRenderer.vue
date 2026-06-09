<template>
  <component :is="resolvedComp" :block="block" :index="index" />
</template>

<script setup>
import { computed, defineAsyncComponent, h } from "vue";
import ContainerBlock from "./blocks/container.vue";

const props = defineProps({
  block: { type: Object, required: true },
  index: { type: Number, default: 0 },
});

// Lightweight inline components for async states — avoids extra file dependencies
const BlockLoadingPlaceholder = {
  name: "BlockLoadingPlaceholder",
  render() {
    return h("div", {
      class: "h-10 bg-gray-100 animate-pulse rounded mx-4 my-1",
      "aria-hidden": "true",
    });
  },
};

const BlockErrorFallback = {
  name: "BlockErrorFallback",
  props: ["error"],
  render() {
    return h(
      "div",
      {
        class:
          "mx-4 my-1 px-3 py-2 text-xs text-red-600 bg-red-50 border border-red-200 rounded flex items-center gap-2",
        role: "alert",
      },
      [
        h("span", { class: "font-medium" }, "Block failed to load"),
        h(
          "span",
          { class: "text-red-400" },
          this.error?.message ? `(${this.error.message})` : ""
        ),
      ]
    );
  },
};

// Module-level cache so async components are only created once
const _cache = {};

function getComp(type) {
  if (type === "container") return ContainerBlock;
  if (!_cache[type]) {
    _cache[type] = defineAsyncComponent({
      loader: () => import(`./blocks/${type}.vue`),
      loadingComponent: BlockLoadingPlaceholder,
      errorComponent: BlockErrorFallback,
      // Give each block component 8 s to load before showing the error state
      timeout: 8000,
    });
  }
  return _cache[type];
}

const resolvedComp = computed(() => getComp(props.block.type));
</script>

<template>
  <BlockWrapper :block="block" :index="index">
    <div v-if="!block.props.html?.trim()" class="min-h-16 flex items-center justify-center text-xs text-ink-gray-3 select-none pointer-events-none border border-dashed border-outline-gray-2 rounded-md m-2">
      Custom HTML — add code in the Inspector
    </div>
    <!-- Sandboxed, script-free preview so arbitrary markup can't touch the builder page itself.
         Auto-resized to its own content height on every load. -->
    <iframe
      v-else
      ref="frame"
      :srcdoc="block.props.html"
      class="w-full border-none block"
      sandbox="allow-same-origin"
      scrolling="no"
      @load="resize"
    />
  </BlockWrapper>
</template>

<script setup>
import { ref, watch, nextTick } from "vue";
import BlockWrapper from "../BlockWrapper.vue";

const props = defineProps({ block: Object, index: Number });
const frame = ref(null);

function resize() {
  const doc = frame.value?.contentDocument;
  if (doc) frame.value.style.height = doc.documentElement.scrollHeight + "px";
}

// srcdoc changes trigger a fresh @load, but only after the DOM updates.
watch(() => props.block.props.html, () => nextTick(resize));
</script>

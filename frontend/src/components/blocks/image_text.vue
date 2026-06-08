<template>
  <BlockWrapper :block="block" :index="index">
    <div
      class="flex gap-5 px-8 py-5 items-center"
      :class="{ 'flex-row-reverse': block.props.image_position === 'right' }"
      :style="{ backgroundColor: block.props.background_color }"
    >
      <!-- Image slot -->
      <div class="flex-shrink-0 w-44">
        <img v-if="block.props.image_url" :src="block.props.image_url" class="w-full rounded" />
        <div
          v-else
          class="w-full h-28 border-2 border-dashed border-gray-300 rounded flex items-center justify-center bg-gray-50"
        >
          <span class="text-xs text-gray-400">Set image URL →</span>
        </div>
      </div>

      <!-- Text -->
      <div class="flex-1">
        <div
          class="outline-none min-h-10 leading-relaxed text-gray-700"
          contenteditable="true"
          @blur="update('text', $event.target.innerText)"
          @click.stop="store.selectBlock(block.id)"
        >{{ block.props.text }}</div>
      </div>
    </div>
  </BlockWrapper>
</template>

<script setup>
import BlockWrapper from "../BlockWrapper.vue";
import { useEditorStore } from "../../stores/editor";
const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();
function update(key, val) { store.updateBlockProps(props.block.id, { [key]: val }); }
</script>

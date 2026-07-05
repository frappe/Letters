<template>
  <BlockWrapper :block="block" :index="index">
    <div :style="paddingStyle">
      <div
        class="relative overflow-hidden"
        :style="{ borderRadius: block.props.border_radius || '8px' }"
      >
        <!-- Thumbnail — ImageUploader handles click-to-upload and Replace on hover -->
        <ImageUploader
          :url="block.props.thumbnail_url"
          height-class="h-52"
          @uploaded="update('thumbnail_url', $event)"
        >
          <template #default="{ url }">
            <img
              v-if="url"
              :src="url"
              class="w-full object-cover block"
              :style="{ height: thumbnailHeight }"
            />
          </template>
        </ImageUploader>

        <!-- Play button overlay — pointer-events-none so ImageUploader stays clickable -->
        <div
          class="absolute inset-0 flex items-center justify-center pointer-events-none"
          :style="{ backgroundColor: block.props.overlay_color || 'rgba(0,0,0,0.3)', borderRadius: block.props.border_radius || '8px' }"
        >
          <div
            class="w-16 h-16 rounded-full flex items-center justify-center shadow-lg"
            :style="{ backgroundColor: block.props.play_button_color || '#ffffff' }"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <polygon points="8,5 19,12 8,19" :fill="block.props.play_icon_color || '#111827'" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Caption -->
      <EditableDiv
        v-if="block.props.caption"
        class="mt-2 text-center text-xs text-ink-gray-5 outline-none"
        :model-value="block.props.caption"
        @update:model-value="update('caption', $event)"
        @click.stop="store.selectBlock(block.id)"
      />
    </div>
  </BlockWrapper>
</template>

<script setup>
import { computed } from "vue";
import BlockWrapper from "../BlockWrapper.vue";
import ImageUploader from "../ImageUploader.vue";
import EditableDiv from "../EditableDiv.vue";
import { useEditorStore } from "../../stores/editor";
import { usePadding } from "../../composables/usePadding";

const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();
function update(key, val) { store.updateBlockProps(props.block.id, { [key]: val }); }

const blockProps = computed(() => props.block.props);
const paddingStyle = usePadding(blockProps);

// The "Height" field in the Size panel sets block_height (BlockWrapper applies
// it as minHeight on the outer wrapper); mirror it onto the thumbnail image
// itself so the image actually grows instead of just leaving empty space.
const thumbnailHeight = computed(() => {
  const h = props.block.props.block_height;
  return h && h !== "auto" ? h : "208px";
});
</script>

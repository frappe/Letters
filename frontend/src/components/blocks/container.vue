<template>
  <BlockWrapper :block="block" :index="index">
    <div
      :style="{
        backgroundColor: block.props.background_color || '#f8fafc',
        border: `1px solid ${block.props.border_color || '#e2e8f0'}`,
        borderRadius: block.props.border_radius || '12px',
        display: 'flex',
        flexDirection: block.props.layout === 'row' ? 'row' : 'column',
        gap: `${block.props.gap ?? 12}px`,
        ...paddingStyle,
      }"
    >
      <!-- Children -->
      <template v-if="block.children?.length">
        <div
          v-for="(child, childIndex) in block.children"
          :key="child.id"
          class="relative group/child rounded"
          :class="block.props.layout === 'row' ? 'flex-1 min-w-0' : ''"
          @click.stop="store.selectBlock(child.id)"
        >
          <!-- Selection ring (pointer-events-none so clicks pass through to block) -->
          <div
            class="absolute inset-0 rounded pointer-events-none z-10 transition-all"
            :class="store.selectedBlockId === child.id
              ? 'ring-2 ring-blue-400 ring-offset-1'
              : 'group-hover/child:ring-1 group-hover/child:ring-blue-200'"
          />
          <!-- Remove child button -->
          <button
            type="button"
            class="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-white border border-gray-200
                   shadow-sm text-gray-400 hover:text-red-500 hover:border-red-200
                   text-xs leading-none z-20
                   opacity-0 group-hover/child:opacity-100 transition-opacity
                   flex items-center justify-center"
            title="Remove block"
            @click.stop="store.removeBlock(child.id)"
          >✕</button>
          <!-- Render the child block (recursive via BlockRenderer) -->
          <BlockRenderer :block="child" :index="childIndex" />
        </div>
      </template>

      <!-- Empty state -->
      <div
        v-else
        class="flex flex-col items-center justify-center gap-2 py-8 select-none pointer-events-none"
      >
        <div class="text-2xl opacity-20">⬚</div>
        <p class="text-xs text-gray-400 text-center leading-relaxed">
          Container is empty<br/>
          <span class="text-gray-300">Click <strong>+ Add inside</strong> below</span>
        </p>
      </div>

      <!-- Add block inside button -->
      <button
        type="button"
        class="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg
               border border-dashed border-gray-300 text-xs text-gray-400
               hover:border-blue-400 hover:text-blue-500 hover:bg-blue-50
               transition-colors cursor-pointer w-full mt-1"
        @click.stop="openPicker({ parentId: block.id, afterIndex: (block.children?.length ?? 1) - 1 })"
      >
        <span class="font-medium">+</span>
        Add block inside
      </button>
    </div>
  </BlockWrapper>
</template>

<script setup>
import { computed, inject } from "vue";
import BlockWrapper from "../BlockWrapper.vue";
import BlockRenderer from "../BlockRenderer.vue";
import { useEditorStore } from "../../stores/editor";
import { usePadding } from "../../composables/usePadding";

const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();
const openPicker = inject("openPicker", () => {});

const blockProps = computed(() => props.block.props);
const paddingStyle = usePadding(blockProps, { top: 16, right: 16, bottom: 16, left: 16 });
</script>

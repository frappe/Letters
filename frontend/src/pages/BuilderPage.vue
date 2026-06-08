<template>
  <div class="builder-layout">
    <aside class="block-palette">
      <h3>Blocks</h3>
      <div
        v-for="block in availableBlocks"
        :key="block.type"
        class="palette-item"
        draggable="true"
        @dragstart="onDragStart(block)"
      >
        {{ block.label }}
      </div>
    </aside>

    <main
      class="canvas"
      @dragover.prevent
      @drop="onDrop"
    >
      <div v-if="!editorStore.blocks.length" class="canvas-empty">
        Drag blocks here to start designing
      </div>
      <component
        v-for="(block, index) in editorStore.blocks"
        :key="block.id"
        :is="blockComponent(block.type)"
        :block="block"
        :index="index"
      />
    </main>

    <aside class="preview-pane">
      <h3>Preview</h3>
      <button @click="previewMode = 'desktop'">Desktop</button>
      <button @click="previewMode = 'mobile'">Mobile</button>
      <div
        class="preview-frame"
        :class="previewMode"
        v-html="editorStore.renderedHtml"
      />
    </aside>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useEditorStore } from "../stores/editor";

const editorStore = useEditorStore();
const previewMode = ref("desktop");

const availableBlocks = [
  { type: "hero", label: "Hero" },
  { type: "text", label: "Text" },
  { type: "image_text", label: "Image + Text" },
  { type: "button", label: "Button" },
  { type: "divider", label: "Divider" },
  { type: "footer", label: "Footer" },
];

let dragging = null;

function onDragStart(block) {
  dragging = block;
}

function onDrop() {
  if (dragging) {
    editorStore.addBlock(dragging.type);
    dragging = null;
  }
}

function blockComponent(type) {
  return () => import(`../components/blocks/${type}.vue`);
}
</script>

<template>
  <BlockWrapper :block="block" :index="index">
    <div
      class="flex gap-5 px-8 py-5 items-center"
      :class="{ 'flex-row-reverse': block.props.image_position === 'right' }"
      :style="{ backgroundColor: block.props.background_color }"
    >
      <!-- Image slot -->
      <div class="flex-shrink-0 w-44">
        <img
          v-if="block.props.image_url"
          :src="block.props.image_url"
          class="w-full rounded"
        />
        <!-- Upload zone -->
        <div
          v-else
          class="w-full h-32 border-2 border-dashed rounded-lg flex flex-col items-center justify-center gap-2 cursor-pointer transition-colors"
          :class="isDragging
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400 hover:bg-gray-100'"
          @click="triggerFileInput"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop.prevent="onFileDrop"
        >
          <span v-if="uploading" class="text-xs text-gray-400">Uploading…</span>
          <template v-else>
            <span class="text-xl">🖼</span>
            <span class="text-xs text-gray-500 font-medium">Click or drop image</span>
            <span class="text-xs text-gray-400">PNG, JPG, GIF, WebP</span>
          </template>
        </div>
        <!-- Replace image button (shown when image exists) -->
        <button
          v-if="block.props.image_url"
          type="button"
          class="mt-1 w-full text-xs text-gray-400 hover:text-gray-600 text-center py-0.5 transition-colors"
          @click="triggerFileInput"
        >Replace image</button>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          class="hidden"
          @change="onFileSelect"
        />
        <p v-if="uploadError" class="mt-1 text-xs text-red-500">{{ uploadError }}</p>
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
import { ref } from "vue";
import BlockWrapper from "../BlockWrapper.vue";
import { useEditorStore } from "../../stores/editor";

const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();
function update(key, val) { store.updateBlockProps(props.block.id, { [key]: val }); }

const fileInput = ref(null);
const uploading = ref(false);
const uploadError = ref("");
const isDragging = ref(false);

function triggerFileInput() {
  fileInput.value?.click();
}

function onFileSelect(e) {
  const file = e.target.files?.[0];
  if (file) uploadFile(file);
}

function onFileDrop(e) {
  isDragging.value = false;
  const file = e.dataTransfer?.files?.[0];
  if (file && file.type.startsWith("image/")) uploadFile(file);
}

async function uploadFile(file) {
  uploading.value = true;
  uploadError.value = "";
  try {
    const fd = new FormData();
    fd.append("file", file, file.name);
    fd.append("is_private", "0");
    fd.append("doctype", "Email Campaign");

    const csrfToken =
      (typeof window !== "undefined" && window.frappe?.csrf_token) || "";

    const res = await fetch("/api/method/upload_file", {
      method: "POST",
      headers: { "X-Frappe-CSRF-Token": csrfToken },
      body: fd,
    });

    if (!res.ok) throw new Error(`Upload failed (${res.status})`);

    const data = await res.json();
    const url = data?.message?.file_url;
    if (!url) throw new Error("No file URL returned");

    update("image_url", url);
  } catch (err) {
    uploadError.value = err.message || "Upload failed";
  } finally {
    uploading.value = false;
    if (fileInput.value) fileInput.value.value = "";
  }
}
</script>

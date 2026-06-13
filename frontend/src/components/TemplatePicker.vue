<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
    <div class="bg-white rounded-2xl shadow-2xl w-[900px] max-h-[85vh] flex flex-col overflow-hidden">

      <!-- Header -->
      <div class="flex-shrink-0 px-8 pt-7 pb-5 border-b border-gray-100">
        <h2 class="text-xl font-semibold text-gray-900">New Campaign</h2>
        <p class="text-sm text-gray-500 mt-1">Start from a template or begin with a blank canvas.</p>
      </div>

      <!-- Grid -->
      <div class="flex-1 overflow-y-auto px-8 py-6">
        <div v-if="loading" class="grid grid-cols-3 gap-5">
          <div v-for="i in 6" :key="i" class="rounded-xl border border-gray-100 overflow-hidden animate-pulse">
            <div class="bg-gray-100 h-48" />
            <div class="p-4 space-y-2">
              <div class="h-3.5 bg-gray-200 rounded w-1/2" />
              <div class="h-2.5 bg-gray-100 rounded w-3/4" />
            </div>
          </div>
        </div>

        <div v-else class="grid grid-cols-3 gap-5">
          <!-- Blank tile -->
          <button
            type="button"
            class="group text-left rounded-xl border-2 border-dashed border-gray-200 hover:border-gray-900 transition-all overflow-hidden focus:outline-none focus:border-gray-900"
            :disabled="creating"
            @click="selectBlank"
          >
            <div class="h-48 bg-gray-50 flex flex-col items-center justify-center gap-2 group-hover:bg-gray-100 transition-colors">
              <div class="w-10 h-10 rounded-full bg-white border-2 border-gray-200 flex items-center justify-center group-hover:border-gray-400 transition-colors">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <span class="text-xs text-gray-400 group-hover:text-gray-600 transition-colors">Blank canvas</span>
            </div>
            <div class="px-4 py-3 border-t border-gray-100">
              <p class="text-sm font-semibold text-gray-800">Blank</p>
              <p class="text-xs text-gray-400 mt-0.5">Header and footer only</p>
            </div>
          </button>

          <!-- Template tiles -->
          <button
            v-for="tpl in templates"
            :key="tpl.name"
            type="button"
            class="group text-left rounded-xl border-2 border-gray-100 hover:border-gray-900 transition-all overflow-hidden focus:outline-none focus:border-gray-900"
            :disabled="creating"
            @click="selectTemplate(tpl)"
          >
            <!-- Preview: iframe of actual rendered email HTML -->
            <div class="h-48 bg-gray-50 overflow-hidden relative">
              <iframe
                v-if="tpl.preview_html"
                :srcdoc="tpl.preview_html"
                class="absolute top-0 left-0 w-full border-none pointer-events-none"
                sandbox="allow-same-origin"
                :style="{ height: '600px', transform: 'scale(0.32)', transformOrigin: 'top left', width: '312.5%' }"
              />
              <!-- Fallback while preview loads -->
              <div v-else class="w-full h-full bg-gradient-to-b from-gray-100 to-gray-50 flex items-center justify-center">
                <span class="text-xs text-gray-300">Preview unavailable</span>
              </div>
              <!-- Hover overlay -->
              <div class="absolute inset-0 bg-gray-900/0 group-hover:bg-gray-900/5 transition-colors" />
            </div>
            <div class="px-4 py-3 border-t border-gray-100">
              <p class="text-sm font-semibold text-gray-800 group-hover:text-gray-900">{{ tpl.title }}</p>
            </div>
          </button>
        </div>
      </div>

      <!-- Footer -->
      <div v-if="creating" class="flex-shrink-0 px-8 py-4 border-t border-gray-100 flex items-center gap-3">
        <div class="w-4 h-4 border-2 border-gray-300 border-t-gray-700 rounded-full animate-spin" />
        <span class="text-sm text-gray-500">Creating campaign…</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const emit = defineEmits(["created"]);

const loading = ref(true);
const creating = ref(false);
const templates = ref([]);

onMounted(async () => {
  try {
    const res = await frappe.call({ method: "letters.letters.api.get_templates" });
    templates.value = res.message || [];
  } catch (e) {
    console.error("Failed to load templates", e);
  } finally {
    loading.value = false;
  }
});

async function createCampaign(blocks) {
  creating.value = true;
  try {
    const res = await frappe.call({
      method: "letters.letters.api.save_campaign",
      args: {
        name: null,
        title: "Untitled Campaign",
        subject: "",
        preview_text: "",
        email_width: 600,
        blocks: JSON.stringify(blocks),
        recipient_config: null,
      },
    });
    emit("created", res.message.name);
  } catch (e) {
    frappe.msgprint("Could not create campaign. Please try again.");
    creating.value = false;
  }
}

function selectBlank() {
  createCampaign([{ type: "header" }, { type: "footer" }]);
}

function selectTemplate(tpl) {
  const blocks = JSON.parse(tpl.blocks_json || "[]");
  createCampaign(blocks);
}
</script>

<template>
  <Teleport to="body">
    <transition
      enter-active-class="transition-opacity duration-150"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 font-sans"
      >
        <!-- Overlay -->
        <div class="absolute inset-0 bg-black/40" @click="close" />

        <!-- Panel: left nav + right content, mirroring Frappe Builder's settings -->
        <div class="relative flex w-full max-w-3xl h-[560px] max-h-[90vh] bg-white rounded-xl shadow-2xl overflow-hidden">

          <!-- Left nav -->
          <aside class="w-52 flex-shrink-0 bg-gray-50 border-r border-gray-100 p-3 flex flex-col">
            <p class="px-2.5 py-2 text-base font-semibold text-ink-gray-9">Settings</p>
            <p class="px-2.5 pt-2 pb-1 text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Campaign</p>
            <nav class="space-y-0.5">
              <button
                v-for="s in sections"
                :key="s.id"
                type="button"
                class="w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-sm text-left transition-colors"
                :class="activeTab === s.id
                  ? 'bg-white text-ink-gray-9 shadow-sm font-medium'
                  : 'text-ink-gray-6 hover:text-ink-gray-9 hover:bg-gray-100'"
                @click="activeTab = s.id"
              >
                <FeatherIcon :name="s.icon" class="w-4 h-4 flex-shrink-0" />
                {{ s.label }}
              </button>
            </nav>
          </aside>

          <!-- Right content -->
          <div class="flex-1 flex flex-col min-w-0">
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
              <h2 class="text-base font-semibold text-ink-gray-9">{{ activeSection.label }}</h2>
              <button
                type="button"
                class="w-7 h-7 flex items-center justify-center rounded-md text-ink-gray-5 hover:text-ink-gray-9 hover:bg-gray-100 transition-colors"
                aria-label="Close settings"
                @click="close"
              ><FeatherIcon name="x" class="w-4 h-4" /></button>
            </div>

            <div class="flex-1 overflow-y-auto px-6 py-5">

              <!-- ── Details ── -->
              <div v-if="activeTab === 'details'" class="space-y-4">
                <div>
                  <label class="block text-xs font-semibold text-ink-gray-6 uppercase tracking-wide mb-1.5">Campaign Name</label>
                  <TextInput
                    :model-value="campaignName"
                    placeholder="Untitled Campaign"
                    @update:model-value="(v) => emit('update:campaignName', v)"
                  />
                </div>
                <div>
                  <label class="block text-xs font-semibold text-ink-gray-6 uppercase tracking-wide mb-1.5">Subject Line</label>
                  <TextInput
                    :model-value="subject"
                    placeholder="What recipients see in their inbox"
                    @update:model-value="(v) => emit('update:subject', v)"
                  />
                </div>
                <div>
                  <label class="block text-xs font-semibold text-ink-gray-6 uppercase tracking-wide mb-1.5">Preview Text</label>
                  <TextInput
                    :model-value="previewText"
                    placeholder="The short line shown after the subject in the inbox"
                    @update:model-value="(v) => emit('update:previewText', v)"
                  />
                  <p class="text-xs text-ink-gray-5 mt-1.5">Appears next to the subject in most inboxes. Keep it under ~90 characters.</p>
                </div>
              </div>

              <!-- ── Recipients ── -->
              <div v-else-if="activeTab === 'recipients'">
                <RecipientsPicker
                  :model-value="recipientConfig"
                  @update:model-value="(v) => emit('update:recipientConfig', v)"
                />
              </div>

              <!-- ── Analytics ── -->
              <div v-else-if="activeTab === 'analytics'" class="space-y-4">
                <div v-if="loadingAnalytics" class="text-xs text-ink-gray-5 py-6 text-center">Loading analytics…</div>

                <div v-else-if="!analytics || !analytics.sent_status" class="rounded-lg border border-dashed border-gray-200 px-4 py-10 text-center">
                  <FeatherIcon name="bar-chart-2" class="w-6 h-6 text-ink-gray-4 mx-auto mb-2" />
                  <p class="text-sm text-ink-gray-6 font-medium">No sends yet</p>
                  <p class="text-xs text-ink-gray-5 mt-1">Open analytics appear here once this campaign has been sent.</p>
                </div>

                <div v-else class="space-y-4">
                  <div class="grid grid-cols-3 gap-3">
                    <div class="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3">
                      <p class="text-2xl font-semibold text-ink-gray-9 tabular-nums">{{ analytics.sent }}</p>
                      <p class="text-xs text-ink-gray-5 mt-0.5">Sent</p>
                    </div>
                    <div class="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3">
                      <p class="text-2xl font-semibold text-ink-gray-9 tabular-nums">{{ analytics.opened }}</p>
                      <p class="text-xs text-ink-gray-5 mt-0.5">Opened</p>
                    </div>
                    <div class="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3">
                      <p class="text-2xl font-semibold text-ink-gray-9 tabular-nums">{{ analytics.open_rate }}%</p>
                      <p class="text-xs text-ink-gray-5 mt-0.5">Open rate</p>
                    </div>
                  </div>

                  <div class="text-xs text-ink-gray-5 space-y-1">
                    <p v-if="analytics.last_opened">Last opened: {{ formatDate(analytics.last_opened) }}</p>
                    <p v-if="analytics.last_sent">Sent: {{ formatDate(analytics.last_sent) }}</p>
                  </div>

                  <p class="text-xs text-ink-gray-5 border-t border-gray-100 pt-3">
                    Open tracking uses a pixel, so it only counts opens where images load. It can undercount (image blocking) or overcount (inbox image proxies), and registers nothing while the site is on localhost.
                  </p>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { TextInput, FeatherIcon } from "frappe-ui";
import RecipientsPicker from "./RecipientsPicker.vue";

const props = defineProps({
  modelValue:      { type: Boolean, default: false },
  campaignName:    { type: String, default: "" },
  subject:         { type: String, default: "" },
  previewText:     { type: String, default: "" },
  recipientConfig: { type: Object, default: null },
  campaignDoc:     { type: Object, default: null },
});
const emit = defineEmits([
  "update:modelValue", "update:campaignName", "update:subject",
  "update:previewText", "update:recipientConfig",
]);

const sections = [
  { id: "details",    label: "Details",    icon: "settings" },
  { id: "recipients", label: "Recipients", icon: "users" },
  { id: "analytics",  label: "Analytics",  icon: "bar-chart-2" },
];
const activeTab = ref("details");
const activeSection = computed(() => sections.find(s => s.id === activeTab.value) || sections[0]);

function close() {
  emit("update:modelValue", false);
}

// ── Analytics (lazy: load when the tab is opened) ─────────────────────────────
const analytics        = ref(null);
const loadingAnalytics = ref(false);

async function loadAnalytics() {
  if (!props.campaignDoc?.name) {
    analytics.value = null;
    return;
  }
  loadingAnalytics.value = true;
  try {
    const res = await frappe.call({
      method: "letters.letters.api.get_campaign_analytics",
      args: { name: props.campaignDoc.name },
    });
    analytics.value = res.message || null;
  } catch {
    analytics.value = null;
  } finally {
    loadingAnalytics.value = false;
  }
}

watch(
  () => [props.modelValue, activeTab.value],
  ([open, tab]) => {
    if (open && tab === "analytics") loadAnalytics();
  }
);

function onKeydown(e) {
  if (e.key === "Escape" && props.modelValue) close();
}
onMounted(() => document.addEventListener("keydown", onKeydown));
onUnmounted(() => document.removeEventListener("keydown", onKeydown));

function formatDate(s) {
  try {
    return new Date(s.replace(" ", "T")).toLocaleString();
  } catch {
    return s;
  }
}
</script>

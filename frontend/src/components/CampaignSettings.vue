<template>
  <Dialog
    :model-value="modelValue"
    title="Campaign Settings"
    size="2xl"
    @update:model-value="(v) => emit('update:modelValue', v)"
  >
    <template #default>
      <TabButtons
        class="mb-5"
        :buttons="tabs"
        v-model="activeTab"
      />

      <!-- ── Details ── -->
      <div v-if="activeTab === 'details'" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1.5">Campaign Name</label>
          <TextInput
            :model-value="campaignName"
            placeholder="Untitled Campaign"
            @update:model-value="(v) => emit('update:campaignName', v)"
          />
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1.5">Subject Line</label>
          <TextInput
            :model-value="subject"
            placeholder="What recipients see in their inbox"
            @update:model-value="(v) => emit('update:subject', v)"
          />
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1.5">Preview Text</label>
          <TextInput
            :model-value="previewText"
            placeholder="The short line shown after the subject in the inbox"
            @update:model-value="(v) => emit('update:previewText', v)"
          />
          <p class="text-xs text-gray-400 mt-1.5">Appears next to the subject in most inboxes. Keep it under ~90 characters.</p>
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
        <div v-if="loadingAnalytics" class="text-xs text-gray-400 py-6 text-center">Loading analytics…</div>

        <div v-else-if="!analytics || !analytics.sent_status" class="rounded-lg border border-dashed border-gray-200 px-4 py-8 text-center">
          <FeatherIcon name="bar-chart-2" class="w-6 h-6 text-gray-300 mx-auto mb-2" />
          <p class="text-sm text-gray-500 font-medium">No sends yet</p>
          <p class="text-xs text-gray-400 mt-1">Open analytics appear here once this campaign has been sent.</p>
        </div>

        <div v-else class="space-y-4">
          <div class="grid grid-cols-3 gap-3">
            <div class="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3">
              <p class="text-2xl font-semibold text-gray-800 tabular-nums">{{ analytics.sent }}</p>
              <p class="text-xs text-gray-400 mt-0.5">Sent</p>
            </div>
            <div class="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3">
              <p class="text-2xl font-semibold text-gray-800 tabular-nums">{{ analytics.opened }}</p>
              <p class="text-xs text-gray-400 mt-0.5">Opened</p>
            </div>
            <div class="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3">
              <p class="text-2xl font-semibold text-gray-800 tabular-nums">{{ analytics.open_rate }}%</p>
              <p class="text-xs text-gray-400 mt-0.5">Open rate</p>
            </div>
          </div>

          <div class="text-xs text-gray-400 space-y-1">
            <p v-if="analytics.last_opened">Last opened: {{ formatDate(analytics.last_opened) }}</p>
            <p v-if="analytics.last_sent">Sent: {{ formatDate(analytics.last_sent) }}</p>
          </div>

          <p class="text-xs text-ink-gray-5 border-t border-gray-100 pt-3">
            Open tracking uses a pixel, so it only counts opens where images load. It can undercount (image blocking) or overcount (inbox image proxies), and registers nothing while the site is on localhost.
          </p>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex items-center justify-end gap-2 w-full">
        <Button @click="emit('update:modelValue', false)">Done</Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from "vue";
import { Dialog, TabButtons, TextInput, Button, FeatherIcon } from "frappe-ui";
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

const tabs = [
  { label: "Details",    value: "details" },
  { label: "Recipients", value: "recipients" },
  { label: "Analytics",  value: "analytics" },
];
const activeTab = ref("details");

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

function formatDate(s) {
  try {
    return new Date(s.replace(" ", "T")).toLocaleString();
  } catch {
    return s;
  }
}
</script>

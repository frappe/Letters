<template>
  <div class="space-y-4">
    <div v-if="loading" class="text-xs text-ink-gray-5 py-6 text-center">Loading…</div>

    <div v-else-if="notification" class="space-y-3">
      <div class="rounded-lg border border-outline-gray-1 p-4 space-y-2.5">
        <div class="flex items-start justify-between gap-3">
          <p class="text-sm font-medium text-ink-gray-8 leading-snug">{{ notification.name }}</p>
          <span
            class="flex-shrink-0 text-xs px-2 py-0.5 rounded-full font-medium"
            :class="notification.enabled ? 'bg-green-50 text-green-700' : 'bg-surface-gray-2 text-ink-gray-4'"
          >{{ notification.enabled ? "Enabled" : "Disabled" }}</span>
        </div>
        <div class="text-xs text-ink-gray-5 space-y-0.5">
          <p v-if="notification.document_type">
            Trigger: <span class="text-ink-gray-7">{{ notification.event }}</span> on
            <span class="text-ink-gray-7">{{ notification.document_type }}</span>
          </p>
          <p v-if="notification.subject" class="truncate">
            Subject: <span class="text-ink-gray-7">{{ notification.subject }}</span>
          </p>
        </div>
        <Button
          variant="subtle"
          size="sm"
          label="Open in Desk"
          iconLeft="lucide-external-link"
          @click="openInDesk"
        />
      </div>

      <p class="text-xs text-ink-gray-4 leading-relaxed">
        Configure trigger conditions, recipients, and other settings from the Desk form.
        Use <code class="font-mono bg-surface-gray-2 px-1 rounded text-ink-gray-6">{{ jinjaSyntaxHint }}</code>
        in your letter's text blocks to insert values from the triggering document.
      </p>
    </div>

    <div v-else class="rounded border border-dashed border-outline-gray-2 px-4 py-10 text-center">
      <span class="lucide-bell size-6 text-ink-gray-4 mx-auto mb-2 block" aria-hidden="true" />
      <p class="text-sm text-ink-gray-6 font-medium">No notification linked</p>
      <p class="text-xs text-ink-gray-5 mt-1 mb-4 leading-relaxed">
        Create a Frappe Notification that uses this Letter as its email body.
        Configure the trigger, conditions, and recipients there.
      </p>
      <Button
        size="sm"
        label="Create Notification"
        :loading="creating"
        @click="createNotification"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { Button, toast } from "frappe-ui";

const jinjaSyntaxHint = "{{ doc.field_name }}";

const props = defineProps({
  letterDoc: { type: Object, default: null },
});

const loading = ref(false);
const creating = ref(false);
const notification = ref(null);

async function load() {
  if (!props.letterDoc?.name) return;
  loading.value = true;
  try {
    const res = await frappe.call({
      method: "letters.letters.api.notifications.get_notification_for_letter",
      args: { letter: props.letterDoc.name },
    });
    notification.value = res.message || null;
  } catch {
    notification.value = null;
  } finally {
    loading.value = false;
  }
}

async function createNotification() {
  creating.value = true;
  try {
    const res = await frappe.call({
      method: "letters.letters.api.notifications.create_notification_for_letter",
      args: { letter: props.letterDoc.name },
    });
    await load();
    window.open(`/app/notification/${encodeURIComponent(res.message.name)}`, "_blank");
  } catch {
    toast.error("Couldn't create notification.");
  } finally {
    creating.value = false;
  }
}

function openInDesk() {
  if (notification.value?.name) {
    window.open(`/app/notification/${encodeURIComponent(notification.value.name)}`, "_blank");
  }
}

onMounted(load);
watch(() => props.letterDoc?.name, load);
</script>

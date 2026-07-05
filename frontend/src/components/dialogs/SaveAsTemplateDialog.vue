<template>
  <Dialog
    :model-value="modelValue"
    title="Save as Template"
    size="sm"
    @update:model-value="(v) => { if (!v) emit('update:modelValue', false) }"
  >
    <template #default>
      <div class="flex flex-col gap-3">
        <p class="text-sm text-ink-gray-6">
          Save this letter's design as a reusable template. It'll show up in the template picker for new letters.
        </p>
        <TextInput
          size="sm"
          placeholder="Template title"
          :model-value="title"
          autofocus
          @update:model-value="emit('update:title', $event)"
          @keydown.enter.prevent="title && !saving && emit('save')"
        />
      </div>
    </template>
    <template #actions>
      <div class="flex items-center justify-end gap-2 w-full">
        <Button @click="emit('update:modelValue', false)">Cancel</Button>
        <Button
          variant="solid"
          :loading="saving"
          :disabled="!title || saving"
          @click="emit('save')"
        >Save template</Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { Dialog, Button, TextInput } from "frappe-ui";

defineProps({
  modelValue: Boolean,
  title: { type: String, default: "" },
  saving: Boolean,
});
const emit = defineEmits(["update:modelValue", "update:title", "save"]);
</script>

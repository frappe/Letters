<template>
  <div class="space-y-4">
    <div>
      <label class="block text-xs font-semibold text-ink-gray-6 uppercase tracking-wide mb-1.5">DocType</label>
      <Select
        v-model="selectedDoctype"
        :options="doctypes"
        placeholder="Select DocType"
        size="sm"
        @update:modelValue="onDoctypeChange"
      />
    </div>

    <div v-if="emailFields.length > 1">
      <label class="block text-xs font-semibold text-ink-gray-6 uppercase tracking-wide mb-1.5">Email Field</label>
      <Select
        v-model="selectedField"
        :options="emailFields.map(f => ({ label: `${f.label} (${f.fieldname})`, value: f.fieldname }))"
        placeholder="Select field"
        size="sm"
        @update:modelValue="onFieldChange"
      />
    </div>

    <div v-if="selectedDoctype && selectedField && filterFields.length" class="space-y-3">
      <p class="text-xs font-semibold text-ink-gray-6 uppercase tracking-wide">
        Filters <span class="font-normal normal-case text-ink-gray-4">(optional, leave blank to include all)</span>
      </p>

      <div v-for="ff in filterFields" :key="ff.fieldname" class="flex items-center gap-3">
        <label class="w-32 flex-shrink-0 text-xs text-ink-gray-6 font-medium truncate" :title="ff.label">{{ ff.label }}</label>

        <Select
          v-if="ff.fieldtype === 'Select'"
          class="flex-1"
          size="sm"
          :model-value="activeFilters[ff.fieldname] || ''"
          :options="[{ label: 'Any', value: '' }, ...ff.options.map(o => ({ label: o, value: o }))]"
          @update:model-value="setFilter(ff.fieldname, $event)"
        />
        <DatePicker
          v-else-if="ff.fieldtype === 'Date' || ff.fieldtype === 'Datetime'"
          class="flex-1"
          size="sm"
          placeholder="On or after…"
          :model-value="activeFilters[ff.fieldname] ? activeFilters[ff.fieldname][1] : ''"
          @update:model-value="setDateFilter(ff.fieldname, $event)"
        />
        <TextInput
          v-else
          class="flex-1"
          size="sm"
          type="text"
          :placeholder="`Filter by ${ff.label}…`"
          :model-value="activeFilters[ff.fieldname] || ''"
          @update:model-value="setFilter(ff.fieldname, $event)"
        />

        <Button
          v-if="activeFilters[ff.fieldname] !== undefined && activeFilters[ff.fieldname] !== ''"
          variant="ghost"
          icon="x"
          size="sm"
          class="!text-ink-gray-3 hover:!text-ink-red-3"
          @click="clearFilter(ff.fieldname)"
        />
      </div>

      <div class="flex items-center gap-2 pt-1">
        <Button
          variant="ghost"
          size="sm"
          :label="countLoading ? 'Counting…' : 'Preview recipient count'"
          :disabled="countLoading"
          @click="previewCount"
        />
        <span v-if="recipientCount !== null" class="text-xs text-ink-gray-6 font-medium">
          → {{ recipientCount }} recipient{{ recipientCount === 1 ? "" : "s" }}
        </span>
      </div>
    </div>

    <p v-if="selectedDoctype && selectedField && !filterFields.length && !loadingFilters" class="text-xs text-ink-gray-4">
      No filterable fields found for this DocType.
    </p>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { Select, DatePicker, TextInput, Button } from "frappe-ui";

const props = defineProps({
  modelValue: { type: Object, default: null },
});
const emit = defineEmits(["update:modelValue"]);

const doctypes        = ref([]);
const selectedDoctype = ref("");
const emailFields     = ref([]);
const selectedField   = ref("");
const filterFields    = ref([]);
const activeFilters   = ref({});
const loadingFilters  = ref(false);
const recipientCount  = ref(null);
const countLoading    = ref(false);

async function loadDoctypes() {
  try {
    const res = await frappe.call({ method: "letters.letters.api.get_doctypes_with_email_fields" });
    doctypes.value = (res.message || []).map(d => ({ label: d, value: d }));
  } catch { /* paste tab still works */ }
}

async function onDoctypeChange() {
  selectedField.value  = "";
  filterFields.value   = [];
  activeFilters.value  = {};
  recipientCount.value = null;
  emailFields.value    = [];
  if (!selectedDoctype.value) return;
  try {
    const res = await frappe.call({
      method: "letters.letters.api.get_email_fields",
      args: { doctype: selectedDoctype.value },
    });
    emailFields.value = res.message || [];
    if (emailFields.value.length === 1) {
      selectedField.value = emailFields.value[0].fieldname;
      await loadFilterFields();
    }
  } catch { emailFields.value = []; }
  emitConfig();
}

async function onFieldChange() {
  filterFields.value   = [];
  activeFilters.value  = {};
  recipientCount.value = null;
  await loadFilterFields();
  emitConfig();
}

async function loadFilterFields() {
  if (!selectedDoctype.value) return;
  loadingFilters.value = true;
  try {
    const res = await frappe.call({
      method: "letters.letters.api.get_doctype_filter_fields",
      args: { doctype: selectedDoctype.value },
    });
    filterFields.value = res.message || [];
  } catch {
    filterFields.value = [];
  } finally {
    loadingFilters.value = false;
  }
}

function setFilter(fieldname, value) {
  const f = { ...activeFilters.value };
  if (!value) delete f[fieldname];
  else f[fieldname] = value;
  activeFilters.value  = f;
  recipientCount.value = null;
  emitConfig();
}

function setDateFilter(fieldname, value) {
  if (!value) { clearFilter(fieldname); return; }
  activeFilters.value  = { ...activeFilters.value, [fieldname]: [">=", value] };
  recipientCount.value = null;
  emitConfig();
}

function clearFilter(fieldname) {
  const f = { ...activeFilters.value };
  delete f[fieldname];
  activeFilters.value  = f;
  recipientCount.value = null;
  emitConfig();
}

async function previewCount() {
  if (!selectedDoctype.value || !selectedField.value) return;
  countLoading.value = true;
  try {
    const res = await frappe.call({
      method: "letters.letters.api.count_doctype_recipients",
      args: {
        doctype:     selectedDoctype.value,
        email_field: selectedField.value,
        filters:     JSON.stringify(activeFilters.value),
      },
    });
    recipientCount.value = res.message?.count ?? 0;
  } catch {
    recipientCount.value = null;
  } finally {
    countLoading.value = false;
  }
}

function emitConfig() {
  if (selectedDoctype.value && selectedField.value) {
    emit("update:modelValue", {
      type: "doctype",
      doctype:     selectedDoctype.value,
      email_field: selectedField.value,
      filters:     activeFilters.value,
    });
  } else {
    emit("update:modelValue", null);
  }
}

// Hydrate from saved config when opened
watch(() => props.modelValue, (cfg) => {
  if (cfg?.type !== "doctype") return;
  selectedDoctype.value = cfg.doctype || "";
  selectedField.value   = cfg.email_field || "";
  activeFilters.value   = cfg.filters || {};
}, { immediate: true });

onMounted(loadDoctypes);
</script>

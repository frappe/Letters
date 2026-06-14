<template>
  <!-- color -->
  <ColorPicker
    v-if="field.type === 'color'"
    :model-value="value"
    @update:model-value="emit('change', $event)"
  />

  <!-- boolean select → Switch -->
  <Switch
    v-else-if="field.type === 'select' && hasBooleanOptions"
    :model-value="!!value"
    @update:model-value="emit('change', $event)"
  />

  <!-- select -->
  <Select
    v-else-if="field.type === 'select'"
    :model-value="value"
    :options="resolvedOptions"
    size="sm"
    class="w-full"
    @update:model-value="emit('change', $event)"
  />

  <!-- alignment -->
  <TabButtons
    v-else-if="field.type === 'align'"
    :buttons="alignOptions"
    :model-value="value"
    @update:model-value="emit('change', $event)"
  />

  <!-- vertical alignment -->
  <TabButtons
    v-else-if="field.type === 'valign'"
    :buttons="valignOptions"
    :model-value="value"
    @update:model-value="emit('change', $event)"
  />

  <!-- direction -->
  <TabButtons
    v-else-if="field.type === 'direction'"
    :buttons="directionOptions"
    :model-value="value"
    @update:model-value="emit('change', $event)"
  />

  <!-- slider -->
  <div v-else-if="field.type === 'slider'" class="flex items-center gap-2">
    <Slider
      :model-value="[value ?? field.min ?? 0]"
      :min="field.min ?? 0"
      :max="field.max ?? 100"
      :step="field.step ?? 1"
      size="sm"
      @update:model-value="emit('change', $event[0])"
    />
    <span class="text-xs text-ink-gray-5 w-8 text-right flex-shrink-0 tabular-nums">
      {{ value ?? field.min ?? 0 }}{{ field.unit ?? "" }}
    </span>
  </div>

  <!-- number -->
  <div v-else-if="field.type === 'number'" class="flex items-center gap-1.5">
    <TextInput
      type="number"
      :min="field.min"
      :max="field.max"
      size="sm"
      :model-value="value"
      @update:model-value="emit('change', Number($event))"
    />
    <span v-if="field.unit" class="text-xs text-ink-gray-4 flex-shrink-0">{{ field.unit }}</span>
  </div>

  <!-- dimension -->
  <div v-else-if="field.type === 'dimension'" class="flex items-center gap-1">
    <TextInput
      type="number"
      :min="0"
      size="sm"
      class="flex-1 min-w-0"
      :model-value="parsedDim.num"
      @update:model-value="emit('change', $event + parsedDim.unit)"
    />
    <TabButtons
      :buttons="[{ value: 'px', label: 'px' }, { value: '%', label: '%' }]"
      :model-value="parsedDim.unit"
      @update:model-value="emit('change', parsedDim.num + $event)"
    />
    <button
      type="button"
      :style="value === 'auto' ? autoActiveStyle : autoInactiveStyle"
      @click="emit('change', 'auto')"
    >auto</button>
  </div>

  <!-- default: text -->
  <TextInput
    v-else
    type="text"
    :placeholder="field.placeholder || ''"
    size="sm"
    :model-value="value"
    @update:model-value="emit('change', $event)"
  />
</template>

<script setup>
import { computed } from "vue";
import { TextInput, Select, Switch, TabButtons, Slider } from "frappe-ui";
import ColorPicker from "./ColorPicker.vue";

const props = defineProps({
  field:      { type: Object, required: true },
  value:      { default: undefined },
  blockProps: { type: Object, default: () => ({}) },
});
const emit = defineEmits(["change"]);

const resolvedOptions = computed(() =>
  typeof props.field.options === "function"
    ? props.field.options(props.blockProps)
    : props.field.options
);

const hasBooleanOptions = computed(() =>
  resolvedOptions.value?.some((o) => typeof o.value === "boolean") ?? false
);

function parseDimension(val) {
  if (!val || val === "auto") return { num: 0, unit: "px" };
  const m = String(val).match(/^(\d*\.?\d+)(px|%)$/);
  if (m) return { num: parseFloat(m[1]), unit: m[2] };
  const n = parseFloat(val);
  return { num: isNaN(n) ? 0 : n, unit: val.includes("px") ? "px" : "%" };
}
const parsedDim = computed(() => parseDimension(props.value));

const alignOptions = [
  { value: "left",    icon: "align-left",    label: "Left",    hideLabel: true },
  { value: "center",  icon: "align-center",  label: "Center",  hideLabel: true },
  { value: "right",   icon: "align-right",   label: "Right",   hideLabel: true },
  { value: "justify", icon: "align-justify", label: "Justify", hideLabel: true },
];
const valignOptions = [
  { value: "flex-start", icon: "chevron-up",   label: "Top",    hideLabel: true },
  { value: "center",     icon: "minus",         label: "Middle", hideLabel: true },
  { value: "flex-end",   icon: "chevron-down",  label: "Bottom", hideLabel: true },
];
const directionOptions = [
  { value: "row",    icon: "arrow-right", label: "Row",    hideLabel: true },
  { value: "column", icon: "arrow-down",  label: "Column", hideLabel: true },
];

const autoActiveStyle   = "font-size:11px;font-weight:500;padding:2px 6px;border-radius:4px;border:1px solid var(--surface-gray-7);background:var(--surface-gray-7);color:var(--text-ink-white);flex-shrink:0;cursor:pointer;";
const autoInactiveStyle = "font-size:11px;font-weight:500;padding:2px 6px;border-radius:4px;border:1px solid var(--outline-gray-2);background:transparent;color:var(--text-ink-gray-5);flex-shrink:0;cursor:pointer;";
</script>

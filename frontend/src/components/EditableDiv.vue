<template>
  <!--
    Thin contenteditable wrapper that prevents Vue's reactive re-renders from
    resetting the cursor or dropping keystrokes while the user is editing.

    Usage:
      <EditableDiv
        :model-value="block.props.title"
        class="text-lg font-bold"
        :style="{ color: block.props.title_color }"
        @update:model-value="update('title', $event)"
        @click.stop="store.selectBlock(block.id)"
      />

    All non-prop attributes (class, style, @click, etc.) fall through to the
    root <div> via Vue's attribute inheritance.
  -->
  <div
    ref="divEl"
    contenteditable="true"
    @focus="onFocus"
    @blur="onBlur"
  />
</template>

<script setup>
import { useContentEditable } from "../composables/useContentEditable";

const props = defineProps({
  modelValue: { type: String, default: "" },
});
const emit = defineEmits(["update:modelValue"]);

const { elRef: divEl, onFocus, onBlur } = useContentEditable(
  () => props.modelValue,
  (val) => emit("update:modelValue", val)
);
</script>

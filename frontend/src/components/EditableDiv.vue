<template>
  <!--
    Thin contenteditable wrapper that prevents Vue's reactive re-renders from
    resetting the cursor or dropping keystrokes while the user is editing.
    Enforces plain-text-only input: paste is stripped of HTML, and formatting
    shortcuts (Cmd+B/I/U) + Enter are suppressed.

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
    @paste.prevent="onPaste"
    @keydown="onKeydown"
  />
</template>

<script setup>
import { useContentEditable } from "../composables/useContentEditable";

const props = defineProps({
  modelValue: { type: String, default: "" },
});
const emit = defineEmits(["update:modelValue"]);

const { elRef: divEl, onFocus, onBlur, onPaste, onKeydown } = useContentEditable(
  () => props.modelValue,
  (val) => emit("update:modelValue", val)
);
</script>

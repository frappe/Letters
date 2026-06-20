<template>
  <!--
    Zero-height by default so it consumes no visible space between blocks.
    On hover it expands to show a faint line + centred + button.
  -->
  <div
    class="relative flex items-center justify-center overflow-visible select-none
           h-0 hover:h-6 transition-all duration-150 group"
    style="z-index:10"
    @click.stop
  >
    <!-- faint line -->
    <div class="absolute inset-x-0 top-1/2 -translate-y-1/2 h-px bg-outline-gray-2
                opacity-0 group-hover:opacity-100 transition-opacity" />

    <!-- + button -->
    <Button
      variant="ghost"
      icon="lucide-plus"
      size="sm"
      aria-label="Add block here"
      title="Add block here"
      class="relative z-10 !w-6 !h-6 !rounded-full opacity-0 group-hover:opacity-100 transition-all
             bg-surface-base border border-outline-gray-3 text-ink-gray-4
             hover:bg-surface-gray-7 hover:text-ink-white hover:border-surface-gray-7 hover:scale-110
             shadow-sm"
      @click.stop="$emit('open', afterIndex)"
    />
  </div>
</template>

<script setup>
import { Button } from "frappe-ui";
defineProps({ afterIndex: { type: Number, required: true } });
defineEmits(["open"]);
</script>

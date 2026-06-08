<template>
  <!-- Hover zone between blocks — shows a centered + button -->
  <div class="relative flex items-center justify-center h-7 group select-none" @click.stop>
    <!-- faint line -->
    <div class="absolute inset-x-0 top-1/2 -translate-y-1/2 h-px bg-gray-200 opacity-0 group-hover:opacity-100 transition-opacity"></div>

    <!-- + button -->
    <button
      type="button"
      title="Add block here"
      class="relative z-10 w-6 h-6 rounded-full flex items-center justify-center text-sm font-semibold leading-none
             opacity-0 group-hover:opacity-100 transition-all
             bg-white border border-gray-300 text-gray-400
             hover:bg-gray-900 hover:text-white hover:border-gray-900 hover:scale-110
             shadow-sm"
      @click.stop="$emit('open', afterIndex)"
    >+</button>
  </div>
</template>

<script setup>
defineProps({ afterIndex: { type: Number, required: true } });
defineEmits(["open"]);
</script>

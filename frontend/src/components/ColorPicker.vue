<template>
  <Popover placement="bottom-start" transition="default">
    <template #target="{ togglePopover }">
      <div class="flex items-center gap-1.5">
        <button
          type="button"
          class="w-6 h-6 rounded flex-shrink-0 border border-gray-200 cursor-pointer hover:scale-105 transition-transform"
          :style="{ backgroundColor: modelValue || '#ffffff' }"
          :title="modelValue || 'Pick a color'"
          @click="togglePopover"
        />
        <TextInput
          size="sm"
          type="text"
          class="flex-1 min-w-0"
          :modelValue="modelValue"
          placeholder="—"
          @update:modelValue="$emit('update:modelValue', $event)"
        />
      </div>
    </template>

    <template #body-main="{ close }">
      <div class="p-2.5 flex flex-col gap-2" style="width: 222px">
        <!-- Palette grid: neutrals row + hue rows -->
        <div class="flex flex-col gap-0.5">
          <div v-for="(row, ri) in PALETTE" :key="ri" class="flex gap-0.5">
            <button
              v-for="color in row"
              :key="color"
              type="button"
              class="w-[18px] h-[18px] rounded-sm flex-shrink-0 cursor-pointer border border-black/10 hover:scale-110 transition-transform"
              :style="{ backgroundColor: color }"
              :title="color"
              @click="pick(color, close)"
            />
          </div>
        </div>

        <!-- Custom hex input -->
        <div class="flex items-center gap-1.5 pt-1.5 border-t border-gray-100">
          <div
            class="w-5 h-5 rounded flex-shrink-0 border border-gray-200"
            :style="{ backgroundColor: modelValue || '#ffffff' }"
          />
          <TextInput
            size="sm"
            type="text"
            class="flex-1"
            :modelValue="modelValue"
            placeholder="Custom hex"
            @update:modelValue="$emit('update:modelValue', $event)"
          />
        </div>
      </div>
    </template>
  </Popover>
</template>

<script setup>
import { Popover, TextInput } from "frappe-ui";

defineProps({ modelValue: { type: String, default: "" } });
const emit = defineEmits(["update:modelValue"]);

function pick(color, close) {
  emit("update:modelValue", color);
  close();
}

// 10 columns × 9 rows (1 neutral + 8 hue families)
const PALETTE = [
  // Neutrals
  ["#ffffff","#f8f8f8","#ededed","#c7c7c7","#999999","#7c7c7c","#525252","#383838","#171717","#0f0f0f"],
  // Red
  ["#fff5f5","#ffe7e7","#ffd8d8","#f79596","#e03434","#ce2c2c","#b41d1d","#941f1f","#6b1515","#4c0d0d"],
  // Orange
  ["#fff4ed","#ffefe4","#ffdec5","#f4b07f","#e86c13","#d35a09","#bd3e0c","#9e3513","#6b2711","#491605"],
  // Yellow
  ["#fcfbe8","#fff7d3","#f7e9a8","#f5e171","#edba13","#9a6304","#8c5600","#6b4210","#733f12","#542e0d"],
  // Green
  ["#f0faf3","#e4faeb","#bdefcc","#7edaa1","#43ac79","#268c5c","#14804d","#075e35","#173b2c","#0a3020"],
  // Teal
  ["#eefbf8","#e6f7f4","#bae8e1","#73d1c4","#36baad","#0a857b","#0f736b","#115c57","#114541","#053734"],
  // Blue
  ["#f1f8fe","#e6f4ff","#d1eaff","#61afef","#0d8ef8","#077ddf","#0375d3","#005cad","#004880","#032e63"],
  // Purple
  ["#f8f3fb","#f6e9ff","#ecd3ff","#bf78fa","#9c45e3","#8e49ca","#6e399d","#5c2f83","#401863","#2d084e"],
  // Pink
  ["#fff7fc","#fde8f5","#ffd5f0","#f77cc6","#e34aa6","#cf3a96","#9c2671","#801458","#570f3e","#40062c"],
];
</script>

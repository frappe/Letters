<template>
  <BlockWrapper :block="block" :index="index">
    <div
      :style="{ backgroundColor: block.props.background_color, ...paddingStyle }"
    >
      <!-- Column grid -->
      <div class="flex">
        <div
          v-for="(col, i) in columns"
          :key="i"
          class="flex-1 flex flex-col min-w-0"
          :style="colStyle(i)"
        >
          <!-- ── Heading (optional) ──────────────────────────────────────── -->
          <EditableDiv
            class="font-semibold text-base outline-none leading-tight transition-opacity"
            :class="col.heading ? 'mb-1.5 opacity-100' : 'opacity-30'"
            :style="{ color: block.props.heading_color || '#111827' }"
            :model-value="col.heading"
            @update:model-value="updateCol(i, 'heading', $event.trim())"
            @click.stop="store.selectBlock(block.id)"
          />

          <!-- ── Body text ───────────────────────────────────────────────── -->
          <EditableDiv
            class="text-sm outline-none leading-relaxed flex-1"
            :style="{ color: block.props.text_color || '#6b7280' }"
            :model-value="col.text"
            @update:model-value="updateCol(i, 'text', $event)"
            @click.stop="store.selectBlock(block.id)"
          />

          <!-- ── CTA ────────────────────────────────────────────────────── -->
          <div class="mt-2.5">
            <!-- Active / editing button -->
            <template v-if="col.button_label || editingCtaCol === i">
              <EditableDiv
                class="inline-block text-xs font-semibold px-3 py-1.5 rounded outline-none cursor-text"
                :style="{ backgroundColor: block.props.button_color || '#111827', color: '#fff' }"
                :model-value="col.button_label || 'Button text'"
                @update:model-value="onCtaLabelBlur(i, $event)"
                @focus.native="editingCtaCol = i"
                @click.stop="editingCtaCol = i; store.selectBlock(block.id)"
              />

              <!-- URL row (shows while editing this CTA) -->
              <div v-if="editingCtaCol === i" class="mt-1 flex items-center gap-1">
                <FeatherIcon name="external-link" class="w-3 h-3 text-gray-400 flex-shrink-0" />
                <input
                  type="text"
                  :value="col.button_url"
                  placeholder="https://…"
                  class="flex-1 min-w-0 text-xs border border-gray-200 rounded px-2 py-0.5
                         outline-none focus:border-gray-400 bg-white"
                  @input="updateCol(i, 'button_url', $event.target.value)"
                  @click.stop
                  @keydown.enter.prevent="editingCtaCol = null"
                />
                <button
                  type="button"
                  class="text-gray-300 hover:text-red-400 transition-colors flex-shrink-0 w-4 h-4 flex items-center justify-center"
                  title="Remove button"
                  @click.stop="removeCtaCol(i)"
                >
                  <FeatherIcon name="x" class="w-3 h-3" />
                </button>
              </div>
            </template>

            <!-- Add button affordance -->
            <button
              v-else
              type="button"
              class="text-xs text-gray-300 hover:text-gray-500 transition-colors flex items-center gap-1"
              @click.stop="addCta(i)"
            >
              <FeatherIcon name="plus" class="w-3 h-3" />
              Add button
            </button>
          </div>
        </div>
      </div>
    </div>
  </BlockWrapper>
</template>

<script setup>
import { ref, computed, watch, nextTick } from "vue";
import BlockWrapper from "../BlockWrapper.vue";
import EditableDiv from "../EditableDiv.vue";
import { FeatherIcon } from "frappe-ui";
import { useEditorStore } from "../../stores/editor";
import { usePadding } from "../../composables/usePadding";

const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();

const blockProps = computed(() => props.block.props);
const paddingStyle = usePadding(blockProps, { top: 20, right: 20, bottom: 20, left: 20 });

const columns = computed(() => props.block.props.columns || []);

const showDividers = computed(() => !!props.block.props.show_dividers);
const dividerColor = computed(() => props.block.props.divider_color || "#e5e7eb");
const colGap       = computed(() => props.block.props.col_gap ?? 16);

function colStyle(i) {
  const isLast = i === columns.value.length - 1;
  const half   = Math.round(colGap.value / 2);
  return {
    paddingLeft:  i === 0 ? "0" : `${half}px`,
    paddingRight: isLast ? "0" : `${half}px`,
    ...(showDividers.value && !isLast
      ? { borderRight: `1px solid ${dividerColor.value}` }
      : {}),
  };
}

// Resize columns array when column_count changes.
// Guard prevents the revert call from re-triggering this watcher.
let _watchGuard = false;
watch(
  () => props.block.props.column_count,
  (newCount, oldCount) => {
    if (_watchGuard) return;
    const n   = parseInt(newCount) || 2;
    const old = parseInt(oldCount) || 2;
    const current = [...(props.block.props.columns || [])];

    // H-02: warn before silently destroying column content
    if (n < current.length) {
      const removedCols = current.slice(n);
      const hasContent  = removedCols.some(
        (col) => col.heading || col.text || col.button_label
      );
      if (hasContent) {
        const label = removedCols.length === 1 ? "column" : "columns";
        const confirmed = window.confirm(
          `Reducing to ${n} ${n === 1 ? "column" : "columns"} will permanently delete the content in the removed ${label}. Continue?`
        );
        if (!confirmed) {
          // Revert the column_count change without re-triggering this watcher
          _watchGuard = true;
          store.updateBlockProps(props.block.id, { column_count: String(old) });
          nextTick(() => { _watchGuard = false; });
          return;
        }
      }
    }

    while (current.length < n) {
      current.push({ heading: "", text: "Add your text here.", button_label: "", button_url: "" });
    }
    store.updateBlockProps(props.block.id, { columns: current.slice(0, n) });
  }
);

function updateCol(idx, key, value) {
  const updated = props.block.props.columns.map((col, i) =>
    i === idx ? { ...col, [key]: value } : col
  );
  store.updateBlockProps(props.block.id, { columns: updated });
}

// ── CTA editing ──────────────────────────────────────────────────────────────
const editingCtaCol = ref(null);

function addCta(i) {
  store.selectBlock(props.block.id);
  updateCol(i, "button_label", "Learn more");
  updateCol(i, "button_url",   "#");
  editingCtaCol.value = i;
}

function onCtaLabelBlur(i, label) {
  const trimmed = (label || "").trim();
  if (!trimmed || trimmed === "Button text") {
    removeCtaCol(i);
  } else {
    updateCol(i, "button_label", trimmed);
  }
}

function removeCtaCol(i) {
  updateCol(i, "button_label", "");
  updateCol(i, "button_url",   "");
  editingCtaCol.value = null;
}
</script>

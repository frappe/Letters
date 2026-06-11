<template>
  <BlockWrapper :block="block" :index="index">
    <div :style="{ backgroundColor: block.props.background_color, ...paddingStyle }">

      <!-- Left-border style -->
      <template v-if="block.props.style !== 'centered'">
        <div :style="leftBorderStyle" class="pl-5">
          <div
            ref="quoteRef"
            class="outline-none text-base italic leading-relaxed mb-3"
            :style="{ color: block.props.quote_color, fontFamily: quoteFont }"
            contenteditable="true"
            @focus="onQuoteFocus"
            @blur="onQuoteBlur"
            @paste.prevent="onQuotePaste"
            @keydown="onQuoteKeydown"
            @click.stop="store.selectBlock(block.id)"
          />
          <div
            ref="authorRef"
            class="text-sm font-semibold outline-none"
            :style="{ color: block.props.author_color, fontFamily: metaFont }"
            contenteditable="true"
            @focus="onAuthorFocus"
            @blur="onAuthorBlur"
            @paste.prevent="onAuthorPaste"
            @keydown="onAuthorKeydown"
            @click.stop="store.selectBlock(block.id)"
          />
          <div
            ref="roleRef"
            class="text-xs outline-none mt-0.5"
            :style="{ color: block.props.author_color, fontFamily: metaFont }"
            contenteditable="true"
            @focus="onRoleFocus"
            @blur="onRoleBlur"
            @paste.prevent="onRolePaste"
            @keydown="onRoleKeydown"
            @click.stop="store.selectBlock(block.id)"
          />
        </div>
      </template>

      <!-- Centered / big-quote style -->
      <template v-else>
        <div class="text-center">
          <div class="text-5xl leading-none mb-2 select-none" :style="{ color: block.props.border_color }">&#8220;</div>
          <div
            ref="quoteRef"
            class="outline-none text-base italic leading-relaxed mb-4 max-w-lg mx-auto"
            :style="{ color: block.props.quote_color, fontFamily: quoteFont }"
            contenteditable="true"
            @focus="onQuoteFocus"
            @blur="onQuoteBlur"
            @paste.prevent="onQuotePaste"
            @keydown="onQuoteKeydown"
            @click.stop="store.selectBlock(block.id)"
          />
          <div
            ref="authorRef"
            class="text-sm font-semibold outline-none"
            :style="{ color: block.props.author_color, fontFamily: metaFont }"
            contenteditable="true"
            @focus="onAuthorFocus"
            @blur="onAuthorBlur"
            @paste.prevent="onAuthorPaste"
            @keydown="onAuthorKeydown"
            @click.stop="store.selectBlock(block.id)"
          />
          <div
            ref="roleRef"
            class="text-xs outline-none mt-0.5"
            :style="{ color: block.props.author_color, fontFamily: metaFont }"
            contenteditable="true"
            @focus="onRoleFocus"
            @blur="onRoleBlur"
            @paste.prevent="onRolePaste"
            @keydown="onRoleKeydown"
            @click.stop="store.selectBlock(block.id)"
          />
        </div>
      </template>

    </div>
  </BlockWrapper>
</template>

<script setup>
import { computed } from "vue";
import BlockWrapper from "../BlockWrapper.vue";
import { useEditorStore } from "../../stores/editor";
import { usePadding } from "../../composables/usePadding";
import { useContentEditable } from "../../composables/useContentEditable";
import { fontStack } from "../../fonts";

const props = defineProps({ block: Object, index: Number });
const store = useEditorStore();
function update(key, val) { store.updateBlockProps(props.block.id, { [key]: val }); }

const blockProps = computed(() => props.block.props);
const paddingStyle = usePadding(blockProps);

// The quote uses the chosen font (serif by default); author/role stay sans by
// default. A single picked font applies to all three, matching the renderer.
const quoteFont = computed(() => fontStack(props.block.props.font_family, "Georgia, 'Times New Roman', serif"));
const metaFont  = computed(() => fontStack(props.block.props.font_family, "Arial, Helvetica, sans-serif"));

// Each field gets its own composable instance.
// Both template branches use the same ref names — Vue assigns the currently
// mounted element, so only one branch's element is active at a time.
const {
  elRef: quoteRef,
  onFocus: onQuoteFocus, onBlur: onQuoteBlur,
  onPaste: onQuotePaste, onKeydown: onQuoteKeydown,
} = useContentEditable(() => props.block.props.quote, (val) => update("quote", val));

const {
  elRef: authorRef,
  onFocus: onAuthorFocus, onBlur: onAuthorBlur,
  onPaste: onAuthorPaste, onKeydown: onAuthorKeydown,
} = useContentEditable(() => props.block.props.author, (val) => update("author", val));

const {
  elRef: roleRef,
  onFocus: onRoleFocus, onBlur: onRoleBlur,
  onPaste: onRolePaste, onKeydown: onRoleKeydown,
} = useContentEditable(() => props.block.props.role, (val) => update("role", val));

const leftBorderStyle = computed(() => ({
  borderLeft: `4px solid ${props.block.props.border_color || "#e5e7eb"}`,
}));
</script>

import { ref, watchEffect } from "vue";

/**
 * Safe contenteditable binding that decouples Vue's reactivity from the DOM
 * during editing, preventing cursor resets and dropped keystrokes.
 *
 * Usage:
 *   const { elRef, onFocus, onBlur } = useContentEditable(
 *     () => props.block.props.content,
 *     (val) => update("content", val)
 *   );
 *
 *   <div ref="elRef" contenteditable="true" @focus="onFocus" @blur="onBlur" />
 *
 * How it works:
 *   - The DOM is only updated from props when the element is NOT focused.
 *   - While the user types, Vue's reactive re-renders do NOT touch the element.
 *   - On blur, the value is committed back to the store once.
 *   - watchEffect re-runs when elRef.value changes (v-if/v-else remounts)
 *     so initial content is always set correctly.
 */
export function useContentEditable(getValue, onCommit) {
  const elRef = ref(null);
  const _focused = ref(false);

  watchEffect(() => {
    const el = elRef.value;
    // Access getValue() so watchEffect tracks it as a dependency.
    const val = getValue();
    if (!_focused.value && el) {
      // Only sync from store to DOM when not editing.
      el.textContent = val ?? "";
    }
  });

  function onFocus() {
    _focused.value = true;
  }

  function onBlur(e) {
    _focused.value = false;
    onCommit(e.target.innerText);
  }

  return { elRef, onFocus, onBlur };
}

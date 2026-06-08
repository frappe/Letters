import { defineStore } from "pinia";
import { ref, computed } from "vue";

let _idCounter = 0;

export const useEditorStore = defineStore("editor", () => {
  const blocks = ref([]);
  const renderedHtml = ref("");
  const campaignName = ref("");
  const campaignDoc = ref(null); // { name, title, subject, preview_text }
  const selectedBlockId = ref(null);

  const selectedBlock = computed(
    () => blocks.value.find((b) => b.id === selectedBlockId.value) || null
  );

  function addBlock(type) {
    const id = ++_idCounter;
    blocks.value.push({ id, type, props: defaultProps(type) });
    selectedBlockId.value = id; // select the block we just added
  }

  function removeBlock(id) {
    blocks.value = blocks.value.filter((b) => b.id !== id);
    if (selectedBlockId.value === id) selectedBlockId.value = null;
  }

  function moveBlock(fromIndex, toIndex) {
    const item = blocks.value.splice(fromIndex, 1)[0];
    blocks.value.splice(toIndex, 0, item);
  }

  function selectBlock(id) {
    selectedBlockId.value = id;
  }

  function updateBlockProps(id, props) {
    const block = blocks.value.find((b) => b.id === id);
    if (block) Object.assign(block.props, props);
  }

  function setRenderedHtml(html) {
    renderedHtml.value = html;
  }

  function loadFromDoc(doc) {
    campaignDoc.value = doc;
    campaignName.value = doc.title;
    _idCounter = 0;
    selectedBlockId.value = null;
    blocks.value = (doc.blocks || []).map((b) => ({ ...b, id: ++_idCounter }));
  }

  return {
    blocks,
    renderedHtml,
    campaignName,
    campaignDoc,
    selectedBlockId,
    selectedBlock,
    addBlock,
    removeBlock,
    moveBlock,
    selectBlock,
    updateBlockProps,
    setRenderedHtml,
    loadFromDoc,
  };
});

function defaultProps(type) {
  const defaults = {
    hero: { heading: "Your heading", subheading: "Your subheading", background_color: "#ffffff" },
    text: { content: "Start typing your message...", align: "left", font_size: "16px" },
    image_text: { image_url: "", text: "Describe the image", image_position: "left" },
    button: { label: "Click here", url: "#", color: "#6366f1", text_color: "#ffffff", align: "center" },
    divider: { border_color: "#e0e0e0", thickness: 1, style: "solid" },
    footer: { text: "You received this email because you signed up.", background_color: "#f9fafb", text_color: "#6b7280" },
  };
  return defaults[type] ?? {};
}

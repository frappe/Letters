import { defineStore } from "pinia";
import { ref } from "vue";

let _idCounter = 0;

export const useEditorStore = defineStore("editor", () => {
  const blocks = ref([]);
  const renderedHtml = ref("");
  const campaignName = ref("");

  function addBlock(type) {
    blocks.value.push({ id: ++_idCounter, type, props: defaultProps(type) });
  }

  function removeBlock(id) {
    blocks.value = blocks.value.filter((b) => b.id !== id);
  }

  function moveBlock(fromIndex, toIndex) {
    const item = blocks.value.splice(fromIndex, 1)[0];
    blocks.value.splice(toIndex, 0, item);
  }

  function updateBlockProps(id, props) {
    const block = blocks.value.find((b) => b.id === id);
    if (block) Object.assign(block.props, props);
  }

  function setRenderedHtml(html) {
    renderedHtml.value = html;
  }

  return {
    blocks,
    renderedHtml,
    campaignName,
    addBlock,
    removeBlock,
    moveBlock,
    updateBlockProps,
    setRenderedHtml,
  };
});

function defaultProps(type) {
  const defaults = {
    hero: { heading: "Your heading", subheading: "Your subheading", background_color: "#ffffff" },
    text: { content: "Start typing your message..." },
    image_text: { image_url: "", text: "Describe the image" },
    button: { label: "Click here", url: "#", color: "#000000" },
    divider: { border_color: "#e0e0e0" },
    footer: { text: "You received this email because you signed up." },
  };
  return defaults[type] ?? {};
}

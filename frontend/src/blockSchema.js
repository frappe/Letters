// Declarative property schema for the right-side Inspector panel.
// Each block type lists the editable styling/behaviour props. Text *content*
// stays inline-editable on the canvas (contenteditable); the inspector owns
// everything else. Adding a control to a block = adding an entry here.
//
// Supported control types: "color", "select", "text", "number", "align".

export const BLOCK_SCHEMA = {
  hero: {
    label: "Hero",
    fields: [
      { key: "background_color", label: "Background color", type: "color" },
    ],
  },
  text: {
    label: "Text",
    fields: [
      { key: "align", label: "Alignment", type: "align" },
      {
        key: "font_size",
        label: "Font size",
        type: "select",
        options: [
          { label: "Small", value: "14px" },
          { label: "Normal", value: "16px" },
          { label: "Large", value: "20px" },
        ],
      },
    ],
  },
  image_text: {
    label: "Image + Text",
    fields: [
      { key: "image_url", label: "Image URL", type: "text", placeholder: "https://…" },
      {
        key: "image_position",
        label: "Image position",
        type: "select",
        options: [
          { label: "Left", value: "left" },
          { label: "Right", value: "right" },
        ],
      },
    ],
  },
  button: {
    label: "Button",
    fields: [
      { key: "url", label: "Link URL", type: "text", placeholder: "https://…" },
      { key: "color", label: "Button color", type: "color" },
      { key: "text_color", label: "Text color", type: "color" },
      { key: "align", label: "Alignment", type: "align" },
    ],
  },
  divider: {
    label: "Divider",
    fields: [
      { key: "border_color", label: "Color", type: "color" },
      { key: "thickness", label: "Thickness (px)", type: "number", min: 1, max: 10 },
      {
        key: "style",
        label: "Style",
        type: "select",
        options: [
          { label: "Solid", value: "solid" },
          { label: "Dashed", value: "dashed" },
          { label: "Dotted", value: "dotted" },
        ],
      },
    ],
  },
  footer: {
    label: "Footer",
    fields: [
      { key: "background_color", label: "Background color", type: "color" },
      { key: "text_color", label: "Text color", type: "color" },
    ],
  },
};

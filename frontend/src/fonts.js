// Email-safe font stacks — the single source of truth for the frontend.
// Mirrors letters/letters/utils/fonts.py exactly; keep the two in sync.
//
// Only web-safe fonts are offered. Each is paired with a fallback chain so the
// message still renders sensibly in clients that lack the primary face. The
// stored value is the human font name (e.g. "Arial"); the full CSS stack is
// resolved at render time, so saved campaigns stay readable and we can refine
// the fallbacks later without migrating data.

export const FONT_STACKS = {
  // Sans serif
  "Arial":           "Arial, Helvetica, sans-serif",
  "Helvetica":       "Helvetica, Arial, sans-serif",
  "Verdana":         "Verdana, Geneva, sans-serif",
  "Tahoma":          "Tahoma, Geneva, sans-serif",
  "Trebuchet MS":    "'Trebuchet MS', Helvetica, sans-serif",
  // Serif
  "Georgia":         "Georgia, 'Times New Roman', serif",
  "Times New Roman": "'Times New Roman', Times, serif",
  // Monospace
  "Courier New":     "'Courier New', Courier, monospace",
};

// Ordered options for the Inspector's font <Select> (sans → serif → mono).
export const FONT_OPTIONS = [
  { label: "Arial",            value: "Arial" },
  { label: "Helvetica",        value: "Helvetica" },
  { label: "Verdana",          value: "Verdana" },
  { label: "Tahoma",           value: "Tahoma" },
  { label: "Trebuchet MS",     value: "Trebuchet MS" },
  { label: "Georgia",          value: "Georgia" },
  { label: "Times New Roman",  value: "Times New Roman" },
  { label: "Courier New",      value: "Courier New" },
];

// Resolve a stored font name to its full CSS stack. Unknown / empty names fall
// back to the supplied stack so each call site can preserve its existing look.
export function fontStack(name, fallback = "") {
  return FONT_STACKS[(name || "").trim()] || fallback;
}

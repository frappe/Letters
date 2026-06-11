"""Email-safe font stacks — the single source of truth for the renderer.

Mirrors frontend/src/fonts.js exactly; keep the two in sync.

Only web-safe fonts are offered. Each is paired with a fallback chain so the
message still renders sensibly in clients that lack the primary face. Blocks
store the human font name (e.g. "Arial"); the full CSS stack is resolved here at
render time. Because the value space is a fixed, known set, callers can emit the
resolved stack into a style attribute without escaping — unknown names never
reach the output, they fall through to the caller's default.
"""

FONT_STACKS: dict[str, str] = {
    # Sans serif
    "Arial":           "Arial, Helvetica, sans-serif",
    "Helvetica":       "Helvetica, Arial, sans-serif",
    "Verdana":         "Verdana, Geneva, sans-serif",
    "Tahoma":          "Tahoma, Geneva, sans-serif",
    "Trebuchet MS":    "'Trebuchet MS', Helvetica, sans-serif",
    # Serif
    "Georgia":         "Georgia, 'Times New Roman', serif",
    "Times New Roman": "'Times New Roman', Times, serif",
    # Monospace
    "Courier New":     "'Courier New', Courier, monospace",
}


def font_stack(props: dict, fallback: str) -> str:
    """Resolve a block's chosen font to a full email-safe CSS stack.

    ``props["font_family"]`` holds the human font name. When it is empty or not
    one of the known safe fonts, ``fallback`` is returned unchanged, so blocks
    saved before this feature (and our existing per-element defaults) render
    exactly as before.
    """
    name = (props.get("font_family") or "").strip()
    return FONT_STACKS.get(name, fallback)

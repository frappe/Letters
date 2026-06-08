from typing import Any

from .design_tree_processor import DesignTreeProcessor
from .block_renderers import RENDERER_MAP

_HTML_WRAPPER = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
</head>
<body style="margin:0;padding:0;background-color:#f3f4f6;">
<table width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background-color:#f3f4f6;">
<tr><td align="center" style="padding:24px 0;">
<table width="600" cellpadding="0" cellspacing="0" border="0"
       style="background-color:#ffffff;border-radius:4px;overflow:hidden;">
<tr><td>
{blocks}
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""


class EmailCompiler:
    """Converts a validated block tree to email-safe HTML (no external dependencies)."""

    def __init__(self, blocks_json: str | list):
        self._processor = DesignTreeProcessor(blocks_json)

    def compile(self) -> str:
        self._processor.validate()
        blocks_html = self._render_blocks(self._processor.get_tree())
        return _HTML_WRAPPER.format(blocks=blocks_html)

    def _render_blocks(self, tree: list[dict[str, Any]]) -> str:
        parts = []
        for block in tree:
            renderer = RENDERER_MAP.get(block["type"])
            if renderer:
                parts.append(renderer.render(block))
        return "\n".join(parts)

import subprocess
import tempfile
import os
from typing import Any

from .design_tree_processor import DesignTreeProcessor
from .block_renderers import RENDERER_MAP


class EmailCompiler:
    """Converts a validated block tree to email-safe HTML via MJML."""

    MJML_WRAPPER_OPEN = (
        '<mjml><mj-head><mj-all-attributes mj-class="all" /></mj-head><mj-body>'
    )
    MJML_WRAPPER_CLOSE = "</mj-body></mjml>"

    def __init__(self, blocks_json: str | list):
        self._processor = DesignTreeProcessor(blocks_json)

    def compile(self) -> str:
        self._processor.validate()
        mjml = self._build_mjml(self._processor.get_tree())
        return self._compile_mjml(mjml)

    def _build_mjml(self, tree: list[dict[str, Any]]) -> str:
        sections = []
        for block in tree:
            renderer = RENDERER_MAP.get(block["type"])
            if renderer:
                sections.append(renderer.render(block))
        return self.MJML_WRAPPER_OPEN + "".join(sections) + self.MJML_WRAPPER_CLOSE

    def _compile_mjml(self, mjml_source: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=".mjml", mode="w", delete=False) as f:
            f.write(mjml_source)
            tmp_path = f.name
        try:
            result = subprocess.run(
                ["mjml", tmp_path, "--output", "/dev/stdout"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        finally:
            os.unlink(tmp_path)

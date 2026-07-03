from __future__ import annotations

import json
from typing import Any

from .block_renderers import RENDERER_MAP


class DesignTreeProcessor:
    """Validates and normalises the blocks JSON tree before compilation."""

    # Single source of truth: a block type is valid iff a renderer exists for it.
    # Deriving this from RENDERER_MAP prevents the allowlist from drifting out of
    # sync with the renderers (which previously dropped header/rich_text/link_list).
    VALID_BLOCK_TYPES = frozenset(RENDERER_MAP)

    # Hard caps so an authenticated but malicious/broken client can't submit a
    # deeply nested or huge block tree and burn server CPU/recursion on compile
    # (render_preview / send_test accept arbitrary client-supplied blocks_json).
    MAX_NODES = 2000
    MAX_DEPTH = 40

    def __init__(self, blocks_json: str | list):
        if isinstance(blocks_json, str):
            self._tree = json.loads(blocks_json)
        else:
            self._tree = blocks_json

    def validate(self) -> None:
        if not isinstance(self._tree, list):
            raise ValueError("Design tree must be a list of blocks")
        self._node_count = 0
        for block in self._tree:
            self._validate_block(block, depth=1)

    def get_tree(self) -> list:
        return self._tree

    def _validate_block(self, block: dict[str, Any], depth: int) -> None:
        if depth > self.MAX_DEPTH:
            raise ValueError(f"Design tree exceeds maximum nesting depth of {self.MAX_DEPTH}")
        self._node_count += 1
        if self._node_count > self.MAX_NODES:
            raise ValueError(f"Design tree exceeds maximum of {self.MAX_NODES} blocks")

        block_type = block.get("type")
        if block_type not in self.VALID_BLOCK_TYPES:
            raise ValueError(f"Unknown block type: {block_type!r}")
        # Recurse into every nesting shape so nested blocks are validated too:
        #   - container stores nested blocks under "children"
        #   - columns stores them under "columns"[].blocks
        for child in block.get("children") or []:
            self._validate_block(child, depth + 1)
        for column in block.get("columns") or []:
            for child in column.get("blocks") or []:
                self._validate_block(child, depth + 1)

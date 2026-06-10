"""
Tests for letters/utils/design_tree_processor.py

Run with:  pytest letters/tests/test_design_tree_processor.py -v
"""
import sys
import os
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from letters.letters.utils.design_tree_processor import DesignTreeProcessor
from letters.letters.utils.block_renderers import RENDERER_MAP


def make_block(block_type, **extra):
    b = {"type": block_type}
    b.update(extra)
    return b


# ── Constructor ───────────────────────────────────────────────────────────────

class TestConstructor:
    def test_accepts_list_directly(self):
        tree = [make_block("text")]
        dtp = DesignTreeProcessor(tree)
        assert dtp.get_tree() == tree

    def test_accepts_json_string(self):
        tree = [make_block("text")]
        dtp = DesignTreeProcessor(json.dumps(tree))
        assert dtp.get_tree() == tree

    def test_empty_list_accepted(self):
        dtp = DesignTreeProcessor([])
        assert dtp.get_tree() == []


# ── validate — top-level ──────────────────────────────────────────────────────

class TestValidateTopLevel:
    def test_non_list_raises(self):
        dtp = DesignTreeProcessor.__new__(DesignTreeProcessor)
        dtp._tree = {"type": "text"}           # dict, not list
        with pytest.raises(ValueError, match="must be a list"):
            dtp.validate()

    def test_unknown_top_level_type_raises(self):
        dtp = DesignTreeProcessor([{"type": "unknown_block"}])
        with pytest.raises(ValueError, match="Unknown block type"):
            dtp.validate()

    def test_every_renderable_type_validates(self):
        """C1 regression: every type with a renderer must pass validation.

        Derives the list from RENDERER_MAP so the validator and the renderers
        can never drift apart again (header/rich_text/link_list were previously
        renderable but rejected, breaking preview/test/send for every template)."""
        tree = [make_block(t) for t in RENDERER_MAP]
        DesignTreeProcessor(tree).validate()   # must not raise

    @pytest.mark.parametrize("block_type", ["header", "rich_text", "link_list"])
    def test_previously_broken_types_validate(self, block_type):
        """These three were missing from the old hand-maintained allowlist."""
        DesignTreeProcessor([make_block(block_type)]).validate()   # must not raise

    def test_mixed_valid_and_invalid_raises(self):
        tree = [make_block("text"), make_block("not_a_real_block")]
        with pytest.raises(ValueError):
            DesignTreeProcessor(tree).validate()


# ── validate — nested children (H-04 regression) ─────────────────────────────

class TestValidateChildren:
    def test_valid_children_pass(self):
        block = make_block("container", children=[make_block("text"), make_block("image")])
        DesignTreeProcessor([block]).validate()  # must not raise

    def test_unknown_child_type_raises(self):
        """H-04: DesignTreeProcessor must recurse into container children."""
        block = make_block("container", children=[{"type": "malicious_block"}])
        with pytest.raises(ValueError, match="Unknown block type.*malicious_block"):
            DesignTreeProcessor([block]).validate()

    def test_deeply_nested_unknown_raises(self):
        inner = make_block("container", children=[{"type": "bad_nested"}])
        outer = make_block("container", children=[inner])
        with pytest.raises(ValueError, match="Unknown block type.*bad_nested"):
            DesignTreeProcessor([outer]).validate()

    def test_deeply_nested_valid_passes(self):
        inner = make_block("container", children=[make_block("text")])
        outer = make_block("container", children=[inner])
        DesignTreeProcessor([outer]).validate()  # must not raise

    def test_children_none_treated_as_empty(self):
        block = make_block("container", children=None)
        DesignTreeProcessor([block]).validate()  # must not raise

    def test_missing_children_key_treated_as_empty(self):
        block = make_block("container")          # no "children" key
        DesignTreeProcessor([block]).validate()  # must not raise


# ── validate — nested columns ────────────────────────────────────────────────

class TestValidateColumns:
    def test_valid_column_blocks_pass(self):
        block = make_block("columns", columns=[
            {"blocks": [make_block("text")]},
            {"blocks": [make_block("image")]},
        ])
        DesignTreeProcessor([block]).validate()  # must not raise

    def test_unknown_block_in_column_raises(self):
        block = make_block("columns", columns=[
            {"blocks": [{"type": "not_real"}]},
        ])
        with pytest.raises(ValueError, match="Unknown block type.*not_real"):
            DesignTreeProcessor([block]).validate()


# ── get_tree ──────────────────────────────────────────────────────────────────

class TestGetTree:
    def test_returns_parsed_tree(self):
        tree = [make_block("hero"), make_block("text")]
        assert DesignTreeProcessor(tree).get_tree() == tree

    def test_json_string_is_parsed(self):
        tree = [make_block("footer")]
        assert DesignTreeProcessor(json.dumps(tree)).get_tree() == tree

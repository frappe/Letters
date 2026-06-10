"""
End-to-end tests for letters/utils/email_compiler.py

These are the tests that would have caught C1: the compiler must turn a real
campaign (every block type, and the header-led library templates) into HTML
without raising. Previously header/rich_text/link_list passed through the
renderers but were rejected by the validator, so compile() threw for every
template.

Run with:  pytest letters/tests/test_email_compiler.py -v
(no Frappe bench required)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from letters.letters.utils.email_compiler import EmailCompiler
from letters.letters.utils.block_renderers import RENDERER_MAP


class TestCompileEveryType:
    @pytest.mark.parametrize("block_type", sorted(RENDERER_MAP))
    def test_each_block_type_compiles(self, block_type):
        """Every registered block type must compile end-to-end without raising."""
        html = EmailCompiler([{"type": block_type, "props": {}}]).compile()
        assert "<!DOCTYPE html>" in html

    def test_full_tree_of_all_types_compiles(self):
        blocks = [{"type": t, "props": {}} for t in RENDERER_MAP]
        html = EmailCompiler(blocks).compile()
        assert "<html" in html


class TestCompileLibraryTemplates:
    """Mirror the lead blocks of the frontend TemplateLibrary — all start with a
    header, which is exactly the block C1 rejected."""

    def test_header_led_template_compiles(self):
        blocks = [
            {"type": "header", "props": {"tagline": "Acme Co"}},
            {"type": "hero", "props": {"heading": "Hello"}},
            {"type": "text", "props": {"content": "Body copy"}},
            {"type": "button", "props": {"label": "Read More", "url": "https://x.test"}},
            {"type": "divider", "props": {}},
            {"type": "footer", "props": {"text": "Unsubscribe"}},
        ]
        html = EmailCompiler(blocks, preview_text="Sneak peek").compile()
        assert "Hello" in html
        assert "Read More" in html
        assert "Sneak peek" in html  # preheader rendered

    def test_rich_text_and_link_list_compile(self):
        blocks = [
            {"type": "rich_text", "props": {"html_content": "<p>Hi <strong>there</strong></p>"}},
            {"type": "link_list", "props": {"items": [{"title": "Docs", "url": "https://x.test"}]}},
        ]
        html = EmailCompiler(blocks).compile()
        assert "there" in html
        assert "Docs" in html


class TestCompileRejectsUnknown:
    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown block type"):
            EmailCompiler([{"type": "definitely_not_a_block"}]).compile()

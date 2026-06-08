from abc import ABC, abstractmethod
from html import escape
from typing import Any


class BlockRenderer(ABC):
    @abstractmethod
    def render(self, block: dict[str, Any]) -> str:
        """Return email-safe HTML for this block."""


class HeroRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        p = block.get("props", {})
        bg = escape(p.get("background_color", "#ffffff"))
        heading = escape(p.get("heading", ""))
        subheading = escape(p.get("subheading", ""))
        return (
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0"'
            f' style="background-color:{bg};">'
            f'<tr><td align="center" style="padding:48px 32px 32px;">'
            f'<h1 style="margin:0 0 12px;font-family:Arial,sans-serif;font-size:36px;'
            f'font-weight:bold;color:#111111;line-height:1.2;">{heading}</h1>'
            f'<p style="margin:0;font-family:Arial,sans-serif;font-size:18px;'
            f'color:#444444;line-height:1.5;">{subheading}</p>'
            f'</td></tr></table>'
        )


class TextRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        p = block.get("props", {})
        content = escape(p.get("content", ""))
        align = escape(p.get("align", "left"))
        size = escape(p.get("font_size", "16px"))
        return (
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0">'
            f'<tr><td align="{align}" style="padding:16px 32px;">'
            f'<p style="margin:0;font-family:Arial,sans-serif;font-size:{size};'
            f'color:#333333;line-height:1.6;text-align:{align};">{content}</p>'
            f'</td></tr></table>'
        )


class ImageTextRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        p = block.get("props", {})
        image_url = escape(p.get("image_url", ""))
        text = escape(p.get("text", ""))
        position = p.get("image_position", "left")

        img_cell = (
            f'<td width="180" valign="top" style="padding:16px 8px 16px 32px;">'
            f'<img src="{image_url}" width="160" style="display:block;border:0;" alt="" />'
            f'</td>'
        ) if image_url else (
            f'<td width="180" valign="top" style="padding:16px 8px 16px 32px;">'
            f'<div style="width:160px;height:100px;background:#eeeeee;'
            f'font-family:Arial,sans-serif;font-size:12px;color:#999;'
            f'display:table-cell;vertical-align:middle;text-align:center;">Image</div>'
            f'</td>'
        )
        text_cell = (
            f'<td valign="top" style="padding:16px 32px 16px 8px;">'
            f'<p style="margin:0;font-family:Arial,sans-serif;font-size:15px;'
            f'color:#333333;line-height:1.6;">{text}</p>'
            f'</td>'
        )

        cells = (img_cell + text_cell) if position == "left" else (text_cell + img_cell)
        return (
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0">'
            f'<tr>{cells}</tr></table>'
        )


class ButtonRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        p = block.get("props", {})
        label = escape(p.get("label", "Click here"))
        url = escape(p.get("url", "#"))
        bg = escape(p.get("color", "#6366f1"))
        color = escape(p.get("text_color", "#ffffff"))
        align = escape(p.get("align", "center"))
        return (
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0">'
            f'<tr><td align="{align}" style="padding:16px 32px;">'
            f'<a href="{url}" style="display:inline-block;padding:12px 28px;'
            f'background-color:{bg};color:{color};font-family:Arial,sans-serif;'
            f'font-size:15px;font-weight:bold;text-decoration:none;border-radius:4px;">'
            f'{label}</a>'
            f'</td></tr></table>'
        )


class DividerRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        p = block.get("props", {})
        color = escape(p.get("border_color", "#e0e0e0"))
        thickness = int(p.get("thickness", 1))
        style = escape(p.get("style", "solid"))
        return (
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0">'
            f'<tr><td style="padding:8px 32px;">'
            f'<hr style="border:0;border-top:{thickness}px {style} {color};margin:0;" />'
            f'</td></tr></table>'
        )


class ColumnsRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        p = block.get("props", {})
        bg = escape(p.get("background_color", "#ffffff"))
        heading_color = escape(p.get("heading_color", "#111827"))
        text_color = escape(p.get("text_color", "#6b7280"))
        button_color = escape(p.get("button_color", "#111827"))
        cols = p.get("columns", [])
        count = max(len(cols), 1)
        col_width = round(100 / count)

        cells = ""
        for col in cols:
            heading = escape(col.get("heading", ""))
            text = escape(col.get("text", ""))
            btn_label = escape(col.get("button_label", ""))
            btn_url = escape(col.get("button_url", "#"))
            btn_html = ""
            if btn_label:
                btn_html = (
                    f'<p style="margin:12px 0 0;">'
                    f'<a href="{btn_url}" style="display:inline-block;padding:8px 20px;'
                    f'background-color:{button_color};color:#ffffff;font-family:Arial,sans-serif;'
                    f'font-size:13px;font-weight:bold;text-decoration:none;border-radius:4px;">'
                    f'{btn_label}</a></p>'
                )
            cells += (
                f'<td width="{col_width}%" valign="top"'
                f' style="padding:16px 12px;vertical-align:top;">'
                f'<h3 style="margin:0 0 8px;font-family:Arial,sans-serif;font-size:16px;'
                f'font-weight:600;color:{heading_color};line-height:1.3;">{heading}</h3>'
                f'<p style="margin:0;font-family:Arial,sans-serif;font-size:14px;'
                f'color:{text_color};line-height:1.6;">{text}</p>'
                f'{btn_html}'
                f'</td>'
            )

        return (
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0"'
            f' style="background-color:{bg};">'
            f'<tr>{cells}</tr></table>'
        )


class FooterRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        p = block.get("props", {})
        text = escape(p.get("text", ""))
        bg = escape(p.get("background_color", "#f9fafb"))
        color = escape(p.get("text_color", "#6b7280"))
        return (
            f'<table width="100%" cellpadding="0" cellspacing="0" border="0"'
            f' style="background-color:{bg};">'
            f'<tr><td align="center" style="padding:24px 32px;">'
            f'<p style="margin:0;font-family:Arial,sans-serif;font-size:12px;'
            f'color:{color};line-height:1.5;">{text}</p>'
            f'</td></tr></table>'
        )


RENDERER_MAP: dict[str, BlockRenderer] = {
    "hero": HeroRenderer(),
    "text": TextRenderer(),
    "image_text": ImageTextRenderer(),
    "button": ButtonRenderer(),
    "columns": ColumnsRenderer(),
    "divider": DividerRenderer(),
    "footer": FooterRenderer(),
}

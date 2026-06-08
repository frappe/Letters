from abc import ABC, abstractmethod
from typing import Any


class BlockRenderer(ABC):
    """Base class for all block renderers. Each block type subclasses this."""

    @abstractmethod
    def render(self, block: dict[str, Any]) -> str:
        """Return MJML markup for this block."""


class HeroRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        props = block.get("props", {})
        bg = props.get("background_color", "#ffffff")
        heading = props.get("heading", "")
        subheading = props.get("subheading", "")
        return (
            f'<mj-section background-color="{bg}">'
            f'<mj-column><mj-text font-size="32px" font-weight="bold">{heading}</mj-text>'
            f'<mj-text font-size="18px">{subheading}</mj-text>'
            f"</mj-column></mj-section>"
        )


class TextRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        props = block.get("props", {})
        content = props.get("content", "")
        return f"<mj-section><mj-column><mj-text>{content}</mj-text></mj-column></mj-section>"


class ImageTextRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        props = block.get("props", {})
        image_url = props.get("image_url", "")
        text = props.get("text", "")
        return (
            "<mj-section>"
            f'<mj-column><mj-image src="{image_url}" /></mj-column>'
            f"<mj-column><mj-text>{text}</mj-text></mj-column>"
            "</mj-section>"
        )


class ButtonRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        props = block.get("props", {})
        label = props.get("label", "Click here")
        url = props.get("url", "#")
        color = props.get("color", "#000000")
        return (
            "<mj-section><mj-column>"
            f'<mj-button href="{url}" background-color="{color}">{label}</mj-button>'
            "</mj-column></mj-section>"
        )


class DividerRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        props = block.get("props", {})
        border_color = props.get("border_color", "#e0e0e0")
        return (
            f'<mj-section><mj-column><mj-divider border-color="{border_color}" /></mj-column></mj-section>'
        )


class FooterRenderer(BlockRenderer):
    def render(self, block: dict[str, Any]) -> str:
        props = block.get("props", {})
        text = props.get("text", "")
        return (
            '<mj-section background-color="#f5f5f5">'
            f'<mj-column><mj-text font-size="12px" color="#888888">{text}</mj-text></mj-column>'
            "</mj-section>"
        )


RENDERER_MAP: dict[str, BlockRenderer] = {
    "hero": HeroRenderer(),
    "text": TextRenderer(),
    "image_text": ImageTextRenderer(),
    "button": ButtonRenderer(),
    "divider": DividerRenderer(),
    "footer": FooterRenderer(),
}

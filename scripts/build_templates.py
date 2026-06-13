"""Builds the Letters starter templates.

Each template is a plain list of block dicts (readable here, serialized to the
blocks_json string the fixtures store). Run with plain python3 — the email
compiler renders standalone; `/assets/...` image paths stay relative and resolve
in the browser when served from the Frappe site.

    python3 scripts/build_templates.py            # write preview HTML
    python3 scripts/build_templates.py --fixtures # also rewrite the fixtures

Design system — deliberately tight so every template reads as one voice:
  • ONE font family per template (set on every block).
  • TWO weights: 400 body, 700 headings/wordmark.
  • THREE sizes: 28 hero, 18 section heading, 16 everything else.
  • TWO ink colours (heading ink + body grey); the accent is reserved strictly
    for interactive things (wordmark, links, buttons). Tints are backgrounds.
  • No all-caps, no letter-spacing tricks. Banners/standalone lines are centred,
    paragraphs are left-aligned, emphasis is <strong> (same size, same colour).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from letters.letters.utils.email_compiler import EmailCompiler

IMG = "/assets/letters/images/templates/"
SIDE = 44  # generous, consistent side padding on the 600px card


class Theme:
    def __init__(self, font, ink, body, accent, tint, band=None, hairline="#ececec"):
        self.font, self.ink, self.body, self.accent = font, ink, body, accent
        self.tint, self.band, self.hairline = tint, band or tint, hairline


# ── block helpers (one type role each) ───────────────────────────────────────

def wordmark(T, name):
    """Quiet text wordmark in the accent — no logo box to clash with the bg."""
    return {"type": "text", "props": {
        "html_content": f"<p>{name}</p>", "align": "center", "font_family": T.font,
        "font_size": "16px", "font_weight": "700", "text_color": T.accent,
        "padding_top": 30, "padding_bottom": 6, "padding_left": SIDE, "padding_right": SIDE}}


def hero(T, heading, sub):
    return {"type": "hero", "props": {
        "heading": heading, "subheading": sub, "font_family": T.font,
        "background_color": T.tint, "heading_color": T.ink, "subheading_color": T.body,
        "heading_size": "28px", "text_align": "center",
        "padding_top": 20, "padding_bottom": 36, "padding_left": SIDE, "padding_right": SIDE}}


def heading(T, title):
    """Section heading — 18/700/ink, left aligned."""
    return {"type": "text", "props": {
        "html_content": f"<p>{title}</p>", "align": "left", "font_family": T.font,
        "font_size": "18px", "font_weight": "700", "text_color": T.ink, "line_height": "1.4",
        "padding_top": 20, "padding_bottom": 6, "padding_left": SIDE, "padding_right": SIDE}}


def body(T, html, *, align="left", color=None, bg="#ffffff", pt=8, pb=8):
    return {"type": "text", "props": {
        "html_content": html, "align": align, "font_family": T.font,
        "font_size": "16px", "font_weight": "400", "text_color": color or T.body, "line_height": "1.7",
        "background_color": bg, "padding_top": pt, "padding_bottom": pb,
        "padding_left": SIDE, "padding_right": SIDE}}


def band(T, html):
    """A single centred line on the soft tint — used at most once per template."""
    return body(T, html, align="center", color=T.ink, bg=T.band, pt=22, pb=22)


def image(T, src, *, pt=8, pb=8):
    return {"type": "image", "props": {
        "image_url": IMG + src, "border": "none", "border_radius": "12px",
        "background_color": "#ffffff", "padding_top": pt, "padding_bottom": pb,
        "padding_left": SIDE, "padding_right": SIDE}}


def button(T, label, *, pt=12, pb=24):
    return {"type": "button", "props": {
        "label": label, "url": "#", "color": T.accent, "text_color": "#ffffff",
        "font_family": T.font, "font_size": "15px", "button_padding": "large",
        "border_radius": "8px", "align": "center", "padding_top": pt, "padding_bottom": pb}}


def links(T, items):
    """Resource list — titles are accent links, descriptions body grey. No heading
    (the link_list heading is force-uppercased, which breaks the type system)."""
    return {"type": "link_list", "props": {
        "items": items, "style": "none", "font_family": T.font,
        "link_color": T.accent, "text_color": T.body,
        "padding_top": 4, "padding_bottom": 8, "padding_left": SIDE, "padding_right": SIDE}}


def product(T, src, title, desc, price, btn=""):
    # btn defaults to none — a showcase card, so it doesn't compete with the
    # template's single primary CTA below it.
    return {"type": "product_card", "props": {
        "image_url": IMG + src, "title": title, "description": desc, "price": price,
        "button_label": btn, "button_url": "#", "font_family": T.font,
        "button_color": T.accent, "title_color": T.ink, "text_color": T.body,
        "border_color": T.hairline, "border_radius": "14px",
        "padding_left": SIDE, "padding_right": SIDE}}


def divider(T, *, pt=24, pb=8):
    return {"type": "divider", "props": {
        "border_color": T.hairline, "width": "100%", "padding_top": pt, "padding_bottom": pb,
        "padding_left": SIDE, "padding_right": SIDE}}


def social(T):
    return {"type": "social", "props": {
        "instagram_url": "https://instagram.com", "x_url": "https://x.com",
        "website_url": "https://example.com", "color": T.body, "align": "center",
        "padding_top": 8, "padding_bottom": 8}}


def footer(T, txt):
    return {"type": "footer", "props": {
        "text": txt, "background_color": "#ffffff", "text_color": "#9ca3af",
        "font_family": T.font, "padding_left": SIDE, "padding_right": SIDE}}


# ── Template 1: Welcome & Onboarding — "Lumen" (product analytics SaaS) ────────
# Focus: get them to their first success + the docs/videos that help. No "why
# choose us" marketing — they already signed up.

LUMEN = Theme(font="Inter", ink="#1f2937", body="#4b5563", accent="#4f46e5", tint="#f4f5ff")

welcome_lumen = [
    wordmark(LUMEN, "Lumen"),
    hero(LUMEN, "Welcome to Lumen",
         "You're all set up. Let's get your first insight in about five minutes."),
    image(LUMEN, "lumen-team.jpg"),
    body(LUMEN, "<p>Hi there,</p><p>We're glad you're here. Lumen turns your product "
                "events into dashboards your whole team can read — no SQL, no waiting on "
                "the data team. Here's the quickest path to your first answer.</p>"),
    heading(LUMEN, "Get started in three steps"),
    body(LUMEN, "<ol><li>Connect your data source — most teams drop in the JS snippet.</li>"
                "<li>Choose the events that matter, like Signed up or Created project.</li>"
                "<li>Open your starter dashboard and share it with a teammate.</li></ol>", pt=0),
    image(LUMEN, "lumen-dashboard.jpg", pt=4),
    button(LUMEN, "Open your dashboard →"),
    divider(LUMEN),
    heading(LUMEN, "Learn the essentials"),
    links(LUMEN, [
        {"title": "Read the quickstart guide", "url": "#", "description": "Ten minutes from snippet to your first funnel."},
        {"title": "Watch the 3-minute product tour", "url": "#", "description": "Dashboards, funnels, and sharing at a glance."},
        {"title": "Take the Lumen Academy course", "url": "#", "description": "A short, free course on building metrics that stick."}]),
    divider(LUMEN),
    social(LUMEN),
    footer(LUMEN, "You're receiving this because you created a Lumen account. "
                  "Manage your email preferences or unsubscribe anytime."),
]


# ── Template 2: Promotional Offer — "Wovenly" (knitwear apparel) ──────────────

WOVENLY = Theme(font="Georgia", ink="#3f3a34", body="#6b6258", accent="#b15a3c",
                tint="#f7f3ee", band="#f1e7da", hairline="#ece7e1")

promo_wovenly = [
    wordmark(WOVENLY, "Wovenly"),
    hero(WOVENLY, "The End-of-Season Edit",
         "The knitwear you keep reaching for, now softer on the price."),
    image(WOVENLY, "wovenly-hero.jpg"),
    band(WOVENLY, "<p>Take 25% off everything knit — applied automatically with code "
                  "<strong>SOFT25</strong>.</p>"),
    body(WOVENLY, "<p>Cooler evenings call for softer layers. We've marked down the whole "
                  "knit collection — the oversized cardigans, the fringe ponchos, the merino "
                  "crews you keep reaching for. A few favourites to start with:</p>", pt=20),
    image(WOVENLY, "wovenly-flatlay.jpg", pt=4),
    product(WOVENLY, "wovenly-poncho.jpg", "The Fringe Poncho",
            "Hand-finished open knit in undyed cotton. One size, endlessly layerable.",
            "$78  ·  was $104"),
    body(WOVENLY, "<p><strong>The sale ends Sunday at midnight.</strong></p>",
         align="center", color="#3f3a34", pt=16, pb=4),
    button(WOVENLY, "Shop the sale →"),
    divider(WOVENLY),
    social(WOVENLY),
    footer(WOVENLY, "Free returns within 30 days · carbon-neutral shipping. You're receiving "
                    "this because you shopped with Wovenly or joined our list — unsubscribe anytime."),
]


TEMPLATES = {
    "Welcome & Onboarding": welcome_lumen,
    "Promotional Offer": promo_wovenly,
}


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "letters", "public", "_tpl_preview")
    os.makedirs(out_dir, exist_ok=True)
    for name, blocks in TEMPLATES.items():
        html = EmailCompiler(blocks, preview_text=name).compile()
        slug = name.lower().replace(" & ", "-").replace(" ", "-")
        with open(os.path.join(out_dir, f"{slug}.html"), "w") as f:
            f.write(html)
        print(f"wrote {slug}.html  ({len(blocks)} blocks)")


if __name__ == "__main__":
    main()

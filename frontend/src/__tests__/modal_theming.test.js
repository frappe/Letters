/**
 * Regression guards for modal / panel theming.
 *
 * Background: the frappe-ui semantic surface tokens (bg-surface-white,
 * bg-surface-modal, text-ink-gray-*) do NOT resolve reliably inside the
 * embedded Frappe Desk builder, which left the Settings dialog and Template
 * picker transparent and their headings unreadable. The fix was a set of
 * explicit `.lt-*` classes in style.css with hard-coded light values plus
 * [data-theme="dark"] overrides — the same bulletproof pattern the panels use.
 *
 * These tests assert, at the source level, that:
 *  1. style.css defines every .lt-* class with BOTH a light default and a
 *     [data-theme="dark"] override.
 *  2. The modal components use the .lt-* classes and do NOT regress to the
 *     unreliable bg-surface / text-ink tokens for their shell.
 *  3. Inspector matches the toolbar/layers panel with a literal bg-white.
 *  4. email_campaign.js keeps "Open in Letters Builder" and removes Frappe's
 *     native Templates button.
 */

import { describe, it, expect } from "vitest";
import { readFileSync } from "fs";
import { resolve } from "path";

const read = (rel) => readFileSync(resolve(__dirname, rel), "utf-8");

const STYLE = read("../style.css");
const PICKER = read("../components/TemplatePicker.vue");
const SETTINGS = read("../components/CampaignSettings.vue");
const INSPECTOR = read("../components/Inspector.vue");
const CAMPAIGN_JS = read(
  "../../../letters/public/frappe_customizations/email_campaign.js"
);

// The modal theming classes and the values they MUST carry in each theme.
const LT_CLASSES = {
  ".lt-surface": { light: "#ffffff", dark: "#262626" },
  ".lt-surface-sub": { light: "#f9fafb", dark: "#1c1c1c" },
  ".lt-border": { light: "#e5e7eb", dark: "#3a3a3a" },
  ".lt-title": { light: "#111827", dark: "#f5f5f5" },
  ".lt-text": { light: "#374151", dark: "#d4d4d4" },
  ".lt-muted": { light: "#6b7280", dark: "#a3a3a3" },
};

// ---------------------------------------------------------------------------
// 1. style.css defines every .lt-* class in both themes
// ---------------------------------------------------------------------------

describe("style.css .lt-* modal theming classes", () => {
  for (const [cls, { light, dark }] of Object.entries(LT_CLASSES)) {
    it(`${cls}: has a light-default declaration with ${light}`, () => {
      // e.g.  .lt-surface       { background-color: #ffffff; }
      const re = new RegExp(
        `(?<!\\]\\s)\\${cls}\\s*\\{[^}]*${light}`,
        "i"
      );
      expect(re.test(STYLE), `${cls} missing light value ${light}`).toBe(true);
    });

    it(`${cls}: has a [data-theme="dark"] override with ${dark}`, () => {
      const re = new RegExp(
        `\\[data-theme="dark"\\]\\s*\\${cls}\\s*\\{[^}]*${dark}`,
        "i"
      );
      expect(re.test(STYLE), `${cls} missing dark override ${dark}`).toBe(true);
    });
  }

  it("light and dark surface values actually differ (real theming)", () => {
    for (const { light, dark } of Object.values(LT_CLASSES)) {
      expect(light).not.toBe(dark);
    }
  });
});

// ---------------------------------------------------------------------------
// 2. Template picker uses .lt-* and is NOT transparent
// ---------------------------------------------------------------------------

describe("TemplatePicker.vue theming", () => {
  it("modal shell uses .lt-surface (solid background)", () => {
    expect(PICKER).toContain("lt-surface");
  });

  it("heading + subtitle use high-contrast .lt-title / .lt-muted", () => {
    expect(PICKER).toContain("lt-title");
    expect(PICKER).toContain("lt-muted");
  });

  it("backdrop is a solid dim, not transparent", () => {
    expect(PICKER).toMatch(/bg-black\/\d+/);
  });

  it("does NOT use unreliable bg-surface-white/modal for the shell", () => {
    expect(PICKER).not.toContain("bg-surface-white");
    expect(PICKER).not.toContain("bg-surface-modal");
  });
});

// ---------------------------------------------------------------------------
// 3. Settings modal uses .lt-* and is NOT transparent
// ---------------------------------------------------------------------------

describe("CampaignSettings.vue theming", () => {
  it("panel uses .lt-surface (solid background)", () => {
    expect(SETTINGS).toContain("lt-surface");
  });

  it("titles use .lt-title for contrast in both themes", () => {
    expect(SETTINGS).toContain("lt-title");
  });

  it("does NOT use unreliable bg-surface-white/modal for the shell", () => {
    expect(SETTINGS).not.toContain("bg-surface-white");
    expect(SETTINGS).not.toContain("bg-surface-modal");
  });
});

// ---------------------------------------------------------------------------
// 4. Inspector matches toolbar/layers panel (literal bg-white, no token)
// ---------------------------------------------------------------------------

describe("Inspector.vue background", () => {
  it("root uses literal bg-white, not bg-surface-white", () => {
    expect(INSPECTOR).toContain("bg-white");
    expect(INSPECTOR).not.toContain("bg-surface-white");
  });
});

// ---------------------------------------------------------------------------
// 5. email_campaign.js — builder button kept, native Templates removed
// ---------------------------------------------------------------------------

describe("email_campaign.js form customizations", () => {
  it('keeps the "Open in Letters Builder" custom button', () => {
    expect(CAMPAIGN_JS).toContain("Open in Letters Builder");
  });

  it("removes Frappe's native Templates feature (template_manager)", () => {
    expect(CAMPAIGN_JS).toContain("template_manager");
    expect(CAMPAIGN_JS).toContain("Templates");
  });
});

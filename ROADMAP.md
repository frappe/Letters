# Letters — Product Roadmap

A feature roadmap derived from a competitive comparison against **Beefree**, **Stripo**, and **Unlayer**, adapted to the strengths of the Frappe platform.

> Guiding principle: don't clone every competitor feature. Lean into what Frappe gives us for free (roles, workflow, File store, Jinja, Newsletter/Email Group, background jobs) and ship the things that close the biggest credibility gaps first.

---

## Where Letters stands today (honest baseline)

- ✅ Drag-and-drop blocks (hero, text, image+text, button, divider, footer)
- ✅ Desktop **and** mobile preview toggle
- ✅ Clean, inline-styled, table-based HTML compiler (no MJML dependency)
- ✅ Send to manual + DocType-sourced recipients; Email Send tracking record
- ✅ Inbox preheader / preview text
- ✅ Frappe role-based access
- ⚠️ Single-column only — flat block list, no rows/columns
- ❌ No image upload (URL only) · no merge tags · no templates · no test send · no brand kit

---

## Prioritization model

Each item scored on **Impact** (closes a real gap users notice) × **Effort**, plus whether Frappe gives us a shortcut.

| Tier | Meaning |
|------|---------|
| 🟢 P0 | Table-stakes / unblocks everything else — do first |
| 🟡 P1 | Strong differentiator or high-frequency need |
| 🔵 P2 | Valuable, but depends on P0/P1 or is niche |
| ⚪ Defer | Low ROI for our context, or disproportionate effort |

---

## Phase 2 — Editor foundations (🟢 P0)

The keystone phase. Without multi-column, Letters can't produce layouts users expect, and most later features build on the richer design tree.

### 1. Multi-column / row-column layout engine — 🟢 **keystone**
- Evolve the design tree from a **flat block list** → `rows[] → columns[] → blocks[]`.
- Email-safe rendering = nested `<table>` with `width="50%"` columns, stacking on mobile via inline styles / `<!--[if mso]>` ghost tables.
- Update `DesignTreeProcessor` (validate nested structure) and `EmailCompiler` (render rows → columns → blocks).
- Migration: wrap existing flat blocks as a single full-width column so old campaigns keep rendering.
- **This unblocks** real layouts, reusable modules, and brand-consistent grids.

### 2. Image upload & manager
- Replace URL-only image field with upload → Frappe **File** doctype (`/api/method/upload_file`).
- Reuse Frappe's existing file store; show a simple picker of previously uploaded images (`File` list filtered to images).
- Frappe shortcut: File doctype + `frappe.client.attach` — no new storage layer.

### 3. HTML source view + export
- "View HTML" split panel (read-only) + "Download .html" button.
- Compiler already produces clean HTML; this is mostly UI plumbing.

### 4. Block settings polish
- Padding/spacing controls, background colors per block, link styling — needed once columns exist.

---

## Phase 3 — Personalization & reuse (🟡 P1)

This is where Frappe's Jinja + DocType model becomes a genuine advantage over the SaaS tools.

### 5. Merge tags / variables with live preview
- Insert tokens like `{{ contact.first_name }}` via a **picker** (driven by the recipient DocType's fields — we already enumerate fields for the recipient picker).
- Live preview: render the email through `frappe.render_template` against a **sample record** the user selects, so they see real values, not raw tags.
- Safe-render fallback for missing fields (`{{ x or "there" }}`).

### 6. Template library + save-as-template
- New **Email Template** doctype storing a design tree.
- Ship ~8–12 polished starter templates (newsletter, announcement, welcome, receipt, event).
- "Start from template" on new campaign; "Save as template" from any campaign.

### 7. Saved reusable modules (sections)
- Save a row/section (header, footer, signature) as a reusable **Module** and drop it into any campaign.
- Builds directly on the Phase 2 row structure.

### 8. Brand kit / style guide
- A single **Letters Settings** (or per-brand) record: logo, brand colors, default fonts, footer/address, social links.
- New blocks default to brand values; "apply brand" recolors a design in one click.
- Satisfies CAN-SPAM footer requirements out of the box.

---

## Phase 4 — Testing & delivery (🟡 P1)

### 9. Send test email — 🟢 quick win
- "Send test" to the current user / a typed address, with merge tags resolved against a sample record. Low effort, high daily value.

### 10. Shareable preview link
- Public web page (`www/` route) rendering the compiled HTML behind a tokenized, expiring link — for stakeholder review without desk access.

### 11. UTM tag automation
- Campaign-level UTM defaults auto-appended to all links at compile time (`utm_source/medium/campaign`). Low effort.

### 12. Display conditions (conditional blocks)
- Per-block "show only if" Jinja condition, evaluated at render against recipient context. Reuses the merge-tag engine.

### 13. ESP / Frappe-native delivery integration
- Integrate with Frappe **Email Group** + **Newsletter** and outgoing **Email Account** so Letters slots into existing Frappe mailing infrastructure instead of being a silo.

---

## Phase 5 — Collaboration & governance (🔵 P2)

Frappe hands us most of this — use the platform instead of building from scratch.

### 14. Comments & approvals
- Use Frappe **Workflow** for Draft → In Review → Approved → Ready states.
- Use Frappe's built-in **comments / @mentions** on the Email Campaign doc — no custom UI needed.

### 15. Version history / restore
- Enable `track_changes` (already on) + expose Frappe **Version** diffs; "restore this version" of the design tree.

---

## Phase 6 — AI assist (🔵 P2, high perceived value)

Gated behind a configurable API key (Anthropic Claude). Each is a thin server endpoint + a button.

### 16. AI subject line generator
- Generate 3–5 subject + preheader variants from the email content. Highest-ROI AI feature.

### 17. AI content drafting
- "Write/rewrite this block" — tone, length, polish — on text blocks.

### 18. AI assists (lower priority)
- Spam-score / deliverability hints, layout/design suggestions.

---

## Explicitly deferred (⚪) — and why

| Feature | Why we're skipping (for now) |
|---------|------------------------------|
| **Real-time multi-user co-editing** | Requires CRDT/OT + presence infra; huge effort for a feature most teams approximate with approvals + locking. Revisit only with clear demand. |
| **Inbox client rendering preview (90+ clients)** | Depends on paid 3rd-party (Litmus / Email on Acid). Offer as an *optional* integration later, not core. |
| **AMP interactive email** | Niche; poor client support; only Stripo pushes it. Low ROI. |
| **Embeddable SDK / white-label** | Only relevant if we productize Letters as a standalone embeddable editor. Out of scope while it's a Frappe app. |

---

## Suggested sequencing (next 3 milestones)

1. **M1 — "Real layouts"**: multi-column engine (#1) + image upload (#2) + HTML export (#3) + test send (#9).
2. **M2 — "Personalized & reusable"**: merge tags + live preview (#5) + templates (#6) + brand kit (#8).
3. **M3 — "Team-ready"**: shareable preview (#10) + approvals via Workflow (#14) + AI subject lines (#16).

Each milestone is independently shippable and demoable.

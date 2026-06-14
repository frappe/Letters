from __future__ import annotations

import json

import frappe
from frappe import _


class SendingMixin:
    def send_test_email(self, recipient=None, subject=None, preview_text=None, email_width=None):
        """Compile blocks and send a test email to `recipient` (defaults to session user)."""
        html = self.render_preview_html(
            preview_text=preview_text if preview_text is not None else self.preview_text,
            email_width=email_width,
        )
        subj = subject or self.subject

        session_email = frappe.session.user
        requested = (recipient or "").strip()
        if requested and requested != session_email:
            frappe.throw(_("Test emails can only be sent to your own account ({0}).").format(session_email))
        email = session_email
        if not frappe.utils.validate_email_address(email, throw=False):
            frappe.throw(_("Your account does not have a valid email address."))

        frappe.sendmail(
            recipients=[email],
            subject=f"[TEST] {subj or 'Email Preview'}",
            message=html,
            now=False,
        )
        return {"sent_to": email}

    def schedule(self, scheduled_at: str):
        """Mark this campaign to be sent at `scheduled_at` (ISO-8601, server timezone)."""
        from letters.letters.api.recipients import _recipient_args_from_config

        if self.status in ("Sent", "Sending"):
            frappe.throw(_("This campaign has already been sent or is currently sending."))
        if not self.blocks_json:
            frappe.throw(_("Campaign has no content to send."))
        if not self.subject:
            frappe.throw(_("Campaign has no subject line."))

        recip = _recipient_args_from_config(self)
        if not any(recip):
            frappe.throw(_("Choose recipients before scheduling this campaign."))

        dt = frappe.utils.get_datetime(scheduled_at)
        if dt <= frappe.utils.now_datetime():
            frappe.throw(_("Scheduled time must be in the future."))

        self.db_set("scheduled_at", dt)
        self.db_set("status", "Scheduled")
        frappe.db.commit()
        return {"scheduled_at": str(dt)}

    def send(self, email_group=None, recipients=None, doctype_config=None):
        """
        Compile and send this campaign to the given audience.

        Pass one of:
          - email_group:    name of a Frappe Email Group (respects unsubscribes)
          - recipients:     JSON string or list of email addresses
          - doctype_config: JSON string/dict with keys: doctype, email_field, filters
          - (none):         fall back to the campaign's saved recipient_config

        The per-recipient loop is enqueued as a background job so large lists
        don't block the web request.
        """
        from letters.letters.api.recipients import (
            _recipient_args_from_config, _suppressed_emails, _valid_emails,
        )
        from letters.letters.api.sending import (
            MAX_RECIPIENTS, _bulk_insert_recipients, _enqueue_send, _resume_send,
        )

        if self.status in ("Sent", "Sending"):
            frappe.throw(_("This campaign has already been sent or is currently sending."))
        if not self.blocks_json:
            frappe.throw(_("Campaign has no content to send."))
        if not self.subject:
            frappe.throw(_("Campaign has no subject line."))

        # Resume a prior partial/failed send instead of starting over
        existing = frappe.get_all(
            "Email Send",
            filters={"campaign": self.name},
            fields=["name", "status"],
            order_by="creation desc",
            limit=1,
        )
        if existing and existing[0].status in ("Failed", "Partial"):
            return _resume_send(existing[0].name, self.name, self)

        # Fall back to the campaign's saved audience when no explicit source is passed
        if not (email_group or doctype_config or recipients):
            recipients, email_group, doctype_config = _recipient_args_from_config(self)
            if not (email_group or doctype_config or recipients):
                frappe.throw(_("This campaign has no saved recipients. Open it and choose an audience before sending."))

        # Resolve recipient list synchronously so we can fail fast
        if email_group:
            members = frappe.get_all(
                "Email Group Member",
                filters={"email_group": email_group, "unsubscribed": 0},
                fields=["email"],
            )
            recipient_list = [m.email for m in members if m.email]
            if not recipient_list:
                frappe.throw(_("The selected Email Group has no active subscribers."))
            mode = "email_group"
        elif doctype_config:
            cfg = json.loads(doctype_config) if isinstance(doctype_config, str) else doctype_config
            dt        = cfg.get("doctype")
            email_fld = cfg.get("email_field")
            filters   = cfg.get("filters") or {}
            if not dt or not email_fld:
                frappe.throw(_("doctype_config must include doctype and email_field."))
            frappe.has_permission(dt, "read", throw=True)
            filters[email_fld] = ["!=", ""]
            rows = frappe.get_all(dt, filters=filters, fields=[email_fld], limit=MAX_RECIPIENTS + 1)
            recipient_list = [r.get(email_fld, "").strip() for r in rows if r.get(email_fld, "").strip()]
            if not recipient_list:
                frappe.throw(_("No records match the selected filters."))
            email_group = None
            mode = "direct"
        else:
            if isinstance(recipients, str):
                recipients = json.loads(recipients)
            recipient_list = [r.strip() for r in (recipients or []) if r.strip()]
            if not recipient_list:
                frappe.throw(_("No recipients provided."))
            email_group = None
            mode = "direct"

        # Honour unsubscribes
        suppressed = _suppressed_emails()
        if suppressed:
            recipient_list = [e for e in recipient_list if e not in suppressed]
        if not recipient_list:
            frappe.throw(_("All selected recipients have unsubscribed from this campaign."))

        # Drop malformed addresses
        recipient_list, invalid_count = _valid_emails(recipient_list)
        if not recipient_list:
            frappe.throw(_("No valid email addresses to send to."))

        # Guard against an oversized audience
        if len(recipient_list) > MAX_RECIPIENTS:
            frappe.throw(_(
                "This audience has more than {0} recipients, which is above the "
                "per-campaign limit. Narrow your filters or split the send."
            ).format(MAX_RECIPIENTS))

        # Claim the send synchronously to prevent a race between two requests
        send_doc = frappe.get_doc({
            "doctype": "Email Send",
            "campaign": self.name,
            "status": "Sending",
            "send_mode": mode,
            "email_group": email_group or "",
            "total_recipients": len(recipient_list),
            "sent_count": 0,
        })
        send_doc.insert(ignore_permissions=True)
        _bulk_insert_recipients(send_doc.name, recipient_list)
        frappe.db.commit()

        self.status = "Sending"
        self.save(ignore_permissions=True)
        frappe.db.commit()

        _enqueue_send(send_doc.name, self.name)
        return {
            "queued": True,
            "count": len(recipient_list),
            "mode": mode,
            "skipped_invalid": invalid_count,
        }

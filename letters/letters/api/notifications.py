from __future__ import annotations

import frappe


@frappe.whitelist()
def get_notification_for_letter(letter: str):
    """Return the single Notification linked to this Letter, or None."""
    name = frappe.db.get_value("Notification", {"letter": letter}, "name")
    if not name:
        return None
    return frappe.db.get_value(
        "Notification",
        name,
        ["name", "subject", "document_type", "event", "enabled"],
        as_dict=True,
    )


@frappe.whitelist()
def create_notification_for_letter(letter: str):
    """Create a new disabled Notification linked to this Letter and return its name."""
    frappe.has_permission("Letter", "read", throw=True)

    existing = frappe.db.get_value("Notification", {"letter": letter}, "name")
    if existing:
        return {"name": existing}

    letter_doc = frappe.get_doc("Letter", letter)

    base_name = f"Letters – {letter_doc.title}"
    notif_name = base_name
    if frappe.db.exists("Notification", notif_name):
        notif_name = f"{base_name} ({frappe.generate_hash(length=4)})"

    notification = frappe.get_doc({
        "doctype": "Notification",
        "name": notif_name,
        "subject": letter_doc.subject or letter_doc.title or "Notification",
        "document_type": "User",
        "event": "New",
        "channel": "Email",
        "message": "",
        "enabled": 0,
        "letter": letter,
    })
    notification.flags.ignore_mandatory = True
    notification.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"name": notification.name}


@frappe.whitelist()
def create_letter_for_notification(notification: str):
    """Create a blank Letter, link it to an existing Notification, and return the letter name."""
    frappe.has_permission("Notification", "write", throw=True)

    notif_doc = frappe.get_doc("Notification", notification)

    if notif_doc.get("letter"):
        return {"letter": notif_doc.letter}

    from letters.letters.doctype.letter._content import _unique_letter_title

    letter = frappe.get_doc({
        "doctype": "Letter",
        "title": _unique_letter_title(f"Notification: {notif_doc.name}"),
        "subject": notif_doc.subject or "",
        "status": "Draft",
        "email_width": 600,
        "canvas_background": "#ffffff",
        "blocks_json": "[]",
    })
    letter.insert(ignore_permissions=True)

    frappe.db.set_value("Notification", notification, "letter", letter.name)
    frappe.db.commit()

    return {"letter": letter.name}

import frappe

from letters.letters.permissions import sync_letter_builder_page_roles


def after_install():
    _ensure_letters_manager_role()
    seed_templates()
    _add_notification_letter_field()
    _add_notification_message_type_field()
    sync_letter_builder_page_roles()
    _set_desktop_icon()


def after_migrate():
    _ensure_letters_manager_role()
    seed_templates()
    _add_notification_letter_field()
    _add_notification_message_type_field()
    sync_letter_builder_page_roles()
    _set_desktop_icon()


def _ensure_letters_manager_role():
    """Create the Letters Manager role referenced by this app's DocType permissions."""
    if frappe.db.exists("Role", "Letters Manager"):
        return
    frappe.get_doc({
        "doctype": "Role",
        "role_name": "Letters Manager",
        "desk_access": 1,
    }).insert(ignore_permissions=True)


def seed_templates():
    import json
    import os

    fixture_path = os.path.join(
        frappe.get_app_path('letters'), 
        "letters", "fixtures", 
        "letters_template.json"
    )
    with open(fixture_path) as f:
        templates = json.load(f)

    for tpl in templates:
        name = tpl.get("name")
        if frappe.db.exists("Letters Template", name):
            doc = frappe.get_doc("Letters Template", name)
            doc.update(tpl)
            doc.save(ignore_permissions=True)
        else:
            doc = frappe.get_doc({"doctype": "Letters Template", **tpl})
            doc.insert(ignore_permissions=True)


def _add_notification_message_type_field():
    """Add/update the letter_message_type Select field on Notification (idempotent)."""
    desired = {
        "dt": "Notification",
        "fieldname": "letter_message_type",
        "fieldtype": "Select",
        "options": "Custom Message\nLetter Builder",
        "label": "Email Body",
        "default": "Custom Message",
        "insert_after": "message_sb",
        "translatable": 0,
    }
    if frappe.db.exists("Custom Field", "Notification-letter_message_type"):
        frappe.db.set_value("Custom Field", "Notification-letter_message_type", "insert_after", "message_sb")
    else:
        frappe.get_doc({"doctype": "Custom Field", **desired}).insert(ignore_permissions=True)


def _add_notification_letter_field():
    """Add a Letter link field to Frappe's Notification DocType (idempotent)."""
    if frappe.db.exists("Custom Field", "Notification-letter"):
        return
    frappe.get_doc({
        "doctype": "Custom Field",
        "dt": "Notification",
        "fieldname": "letter",
        "fieldtype": "Link",
        "options": "Letter",
        "label": "Letter",
        "description": "Use a visual Letter design as the email body for this notification",
        "insert_after": "message",
        "translatable": 0,
    }).insert(ignore_permissions=True)


def _set_desktop_icon():
    """Set the custom SVG icon for the Letters workspace / desktop icon."""
    icon_path = "/assets/letters/images/favicon/favicon.svg"
    if frappe.db.exists("Workspace", "Letters"):
        frappe.db.set_value("Workspace", "Letters", "icon", icon_path)
    if frappe.db.exists("Desktop Icon", "Letters"):
        frappe.db.set_value("Desktop Icon", "Letters", "icon", icon_path)

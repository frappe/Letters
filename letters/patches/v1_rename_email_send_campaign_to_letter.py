import frappe
from frappe.model.utils.rename_field import rename_field


def execute():
    """Rename Email Send.campaign → Email Send.letter (fieldname rename)."""
    if frappe.db.has_column("Email Send", "campaign"):
        rename_field("Email Send", "campaign", "letter")

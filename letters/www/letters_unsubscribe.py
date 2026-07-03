import hmac

import frappe
from frappe import _

from letters.letters.api.unsubscribe import _sign_email

no_cache = 1


def get_context(context):
    email  = frappe.utils.cstr(frappe.request.args.get("email", "")).strip().lower()
    letter = frappe.utils.cstr(frappe.request.args.get("letter", "")).strip()
    saved  = frappe.utils.cint(frappe.request.args.get("saved", 0))
    token  = frappe.utils.cstr(frappe.request.args.get("token", "")).strip()

    context.email  = email
    context.letter = letter
    context.saved  = saved
    context.token  = token
    context.title  = _("Email Preferences")
    context.no_sidebar = 1

    context.csrf_token = frappe.session.data.csrf_token or ""

    # A valid HMAC token is required to reveal this address's subscription state.
    # Without it we still render the form (real links always carry a token), but
    # never expose per-category / global status — otherwise anyone could probe
    # whether an arbitrary address is subscribed just by putting it in the URL.
    token_ok = bool(email and token and hmac.compare_digest(token, _sign_email(email)))
    if not token_ok:
        context.folders                  = []
        context.is_globally_unsubscribed = False
        return

    # All Letter Categories
    folders = frappe.get_all("Letter Category", fields=["name", "folder_name"], order_by="folder_name asc", ignore_permissions=True)
    for f in folders:
        f["is_unsubscribed"] = bool(frappe.db.exists("Email Unsubscribe", {
            "email":             email,
            "reference_doctype": "Letter Category",
            "reference_name":    f["name"],
        }))

    context.folders = folders
    context.is_globally_unsubscribed = bool(frappe.db.exists("Email Unsubscribe", {
        "email":             email,
        "global_unsubscribe": 1,
    }))

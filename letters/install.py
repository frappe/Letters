import frappe


def after_install():
    seed_templates()


def after_migrate():
    seed_templates()


def seed_templates():
    if frappe.db.count("Letters Template") > 0:
        return
    frappe.load_fixtures(app="letters")
    frappe.db.commit()

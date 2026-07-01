"""
Regression tests for notification/letter UX improvements.

Covers:
- has_notification flag in as_builder_dict
- create_notification_for_letter: blocks sent/scheduled letters
- create_notification_for_letter: idempotent (returns existing)
- send_letter: blocked when letter has linked notification
- schedule_letter: blocked when letter has linked notification
- LettersNotification.send_an_email: routes by letter_message_type
- Letter DocType: show_title_field_in_link and search_fields set

Run with:
    bench run-tests --app letters --module letters.tests.test_notification_features
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch, call

import frappe
from frappe.tests import IntegrationTestCase

SAMPLE_BLOCKS = json.dumps([{"type": "text", "props": {"html_content": "<p>Hi</p>"}}])


class NotificationFeaturesTestCase(IntegrationTestCase):
    """Base with shared helpers and cleanup."""

    def setUp(self):
        super().setUp()
        self._created = []

    def tearDown(self):
        for doctype, name in reversed(self._created):
            try:
                frappe.delete_doc(doctype, name, force=True, ignore_missing=True)
            except Exception:
                pass
        frappe.db.commit()
        super().tearDown()

    def new_letter(self, status="Draft", subject="Test Subject"):
        doc = frappe.get_doc({
            "doctype": "Letter",
            "title": f"Regression Letter {frappe.generate_hash(length=8)}",
            "subject": subject,
            "status": status,
            "email_width": 600,
            "blocks_json": SAMPLE_BLOCKS,
        })
        doc.insert(ignore_permissions=True)
        self._created.append(("Letter", doc.name))
        return doc

    def new_notification(self, letter_name, subject="Test Notif"):
        notif = frappe.get_doc({
            "doctype": "Notification",
            "name": f"Test Notif {frappe.generate_hash(length=8)}",
            "subject": subject,
            "document_type": "User",
            "event": "New",
            "channel": "Email",
            "message": "Hello",
            "enabled": 0,
            "letter": letter_name,
        })
        notif.flags.ignore_mandatory = True
        notif.insert(ignore_permissions=True)
        self._created.append(("Notification", notif.name))
        return notif


# ---------------------------------------------------------------------------
# as_builder_dict: has_notification flag
# ---------------------------------------------------------------------------

class TestHasNotificationFlag(NotificationFeaturesTestCase):

    def test_false_when_no_notification_linked(self):
        letter = self.new_letter()
        with patch.object(
            frappe, "has_permission", return_value=True
        ):
            d = letter.as_builder_dict()
        self.assertFalse(d["has_notification"])

    def test_true_when_notification_linked(self):
        letter = self.new_letter()
        self.new_notification(letter.name)
        with patch.object(
            frappe, "has_permission", return_value=True
        ):
            d = letter.as_builder_dict()
        self.assertTrue(d["has_notification"])


# ---------------------------------------------------------------------------
# create_notification_for_letter
# ---------------------------------------------------------------------------

class TestCreateNotificationForLetter(NotificationFeaturesTestCase):

    def _call(self, letter_name):
        from letters.letters.api.notifications import create_notification_for_letter
        with patch.object(frappe, "has_permission", return_value=True):
            result = create_notification_for_letter(letter_name)
        # track for cleanup
        if result and result.get("name"):
            self._created.append(("Notification", result["name"]))
        return result

    def test_creates_notification_for_draft_letter(self):
        letter = self.new_letter(subject="Hello World")
        result = self._call(letter.name)
        self.assertIn("name", result)
        notif = frappe.get_doc("Notification", result["name"])
        self.assertEqual(notif.letter, letter.name)
        self.assertEqual(notif.subject, "Hello World")
        self.assertEqual(notif.enabled, 0)

    def test_idempotent_returns_existing(self):
        letter = self.new_letter()
        r1 = self._call(letter.name)
        r2 = self._call(letter.name)
        self.assertEqual(r1["name"], r2["name"])

    def test_blocks_sent_letter(self):
        for status in ("Sent", "Partial", "Failed", "Sending", "Scheduled"):
            letter = self.new_letter(status=status)
            with self.assertRaises(frappe.ValidationError, msg=f"Should block status={status}"):
                self._call(letter.name)

    def test_subject_synced_from_letter(self):
        letter = self.new_letter(subject="My Campaign Subject")
        result = self._call(letter.name)
        notif = frappe.get_doc("Notification", result["name"])
        self.assertEqual(notif.subject, "My Campaign Subject")


# ---------------------------------------------------------------------------
# send_letter / schedule_letter: blocked for notification letters
# ---------------------------------------------------------------------------

class TestSendBlockedForNotificationLetter(NotificationFeaturesTestCase):

    def test_send_letter_blocked_when_notification_linked(self):
        from letters.letters.api.sending import send_letter
        letter = self.new_letter()
        self.new_notification(letter.name)
        with self.assertRaises(frappe.ValidationError):
            with patch.object(frappe, "has_permission", return_value=True):
                send_letter(letter.name, recipients=json.dumps(["a@example.com"]))

    def test_schedule_letter_blocked_when_notification_linked(self):
        from letters.letters.api.sending import schedule_letter
        letter = self.new_letter()
        self.new_notification(letter.name)
        with self.assertRaises(frappe.ValidationError):
            with patch.object(frappe, "has_permission", return_value=True):
                schedule_letter(letter.name, scheduled_at="2099-01-01 09:00:00")

    def test_send_letter_allowed_without_notification(self):
        """send_letter should NOT raise the notification guard for plain letters."""
        from letters.letters.api.sending import send_letter
        letter = self.new_letter()
        # We only test that the notification guard doesn't fire — patch doc.send
        # to avoid actually sending.
        with patch.object(frappe, "has_permission", return_value=True):
            letter_doc = frappe.get_doc("Letter", letter.name)
            with patch.object(letter_doc.__class__, "send", return_value=None) as mock_send:
                with patch.object(frappe, "get_doc", return_value=letter_doc):
                    send_letter(letter.name, recipients=json.dumps(["a@example.com"]))
                mock_send.assert_called_once()


# ---------------------------------------------------------------------------
# LettersNotification.send_an_email routing
# ---------------------------------------------------------------------------

class TestLettersNotificationSendRouting(NotificationFeaturesTestCase):
    """
    Tests for send_an_email routing logic. We instantiate LettersNotification
    without calling __init__ (using object.__new__) and patch the base class
    send_an_email to avoid actual email sending.
    """

    def _make(self, letter_message_type, letter=None, message="original"):
        from letters.letters.overrides.notification import LettersNotification
        notif = object.__new__(LettersNotification)
        notif.letter_message_type = letter_message_type
        notif.letter = letter
        notif.message = message
        return notif

    def _base_patch(self):
        return patch(
            "letters.letters.overrides.notification.Notification.send_an_email"
        )

    def test_custom_message_calls_super(self):
        notif = self._make("Custom Message")
        with self._base_patch() as mock_super:
            notif.send_an_email(MagicMock(), {})
            mock_super.assert_called_once()

    def test_letter_builder_compiles_and_sends(self):
        from letters.letters.overrides.notification import LettersNotification
        letter = self.new_letter()
        notif = self._make("Letter Builder", letter=letter.name)
        compiled_html = "<html>Compiled</html>"

        with patch.object(LettersNotification, "_compile_letter", return_value=compiled_html):
            with self._base_patch() as mock_super:
                notif.send_an_email(MagicMock(), {})
                mock_super.assert_called_once()
                # message restored to original after send
                self.assertEqual(notif.message, "original")

    def test_letter_builder_restores_message_on_exception(self):
        from letters.letters.overrides.notification import LettersNotification
        letter = self.new_letter()
        notif = self._make("Letter Builder", letter=letter.name, message="keep me")

        with patch.object(LettersNotification, "_compile_letter", return_value="<html/>"):
            with self._base_patch() as mock_super:
                mock_super.side_effect = RuntimeError("smtp error")
                with self.assertRaises(RuntimeError):
                    notif.send_an_email(MagicMock(), {})
        self.assertEqual(notif.message, "keep me")

    def test_letter_builder_without_letter_falls_back_to_super(self):
        notif = self._make("Letter Builder", letter=None)
        with self._base_patch() as mock_super:
            notif.send_an_email(MagicMock(), {})
            mock_super.assert_called_once()


# ---------------------------------------------------------------------------
# Letter DocType metadata
# ---------------------------------------------------------------------------

class TestLetterDoctypeMeta(IntegrationTestCase):

    def test_show_title_field_in_link(self):
        meta = frappe.get_meta("Letter")
        self.assertEqual(meta.show_title_field_in_link, 1)

    def test_search_fields_include_title_and_subject(self):
        meta = frappe.get_meta("Letter")
        search_fields = [f.strip() for f in (meta.search_fields or "").split(",")]
        self.assertIn("title", search_fields)
        self.assertIn("subject", search_fields)

    def test_title_field_is_title(self):
        meta = frappe.get_meta("Letter")
        self.assertEqual(meta.title_field, "title")

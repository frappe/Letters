import frappe
from frappe.model.document import Document

from ._analytics import AnalyticsMixin
from ._content import ContentMixin
from ._sending import SendingMixin


class LettersCampaign(ContentMixin, SendingMixin, AnalyticsMixin, Document):
    pass

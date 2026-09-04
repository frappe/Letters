"""
Guards the fieldtype of Email Send.snapshot_blocks.

Run with:  pytest letters/tests/test_snapshot_fieldtype.py -v
"""
from __future__ import annotations

import json
import pathlib

DOCTYPE_JSON = (
    pathlib.Path(__file__).resolve().parents[1]
    / "letters" / "doctype" / "email_send" / "email_send.json"
)


def _field(fieldname):
    fields = json.loads(DOCTYPE_JSON.read_text())["fields"]
    return next(f for f in fields if f["fieldname"] == fieldname)


def test_snapshot_blocks_is_a_code_field():
    assert _field("snapshot_blocks")["fieldtype"] == "Code"


def test_letter_blocks_json_stays_code_too():
    letter_json = (
        pathlib.Path(__file__).resolve().parents[1]
        / "letters" / "doctype" / "letter" / "letter.json"
    )
    fields = json.loads(letter_json.read_text())["fields"]
    blocks = next(f for f in fields if f["fieldname"] == "blocks_json")
    assert blocks["fieldtype"] == "Code"

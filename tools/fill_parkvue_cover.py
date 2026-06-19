#!/usr/bin/env python3
"""Fill the Parkvue Offer Cover Sheet (AcroForm, GUID field names) for each
Parkvue property, and overlay circles on the INVESTOR / NO / CASH options
(those lines have no form fields). Outputs one PDF per property.

Field->label mapping was derived from widget /Rect positions and verified
against the visible labels. POF is NOT included (sourced from doubleclose.com).
"""
import io
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

BLANK = "Parkvue_Offer_Cover_Sheet_BLANK.pdf"

# GUID field name by purpose (verified by position)
F = {
    "property": "Text 1569fe2a-fb84-4eb4-a92b-bb69b6f7e397",
    "buyer_entity": "Text a4c3ae62-23c2-4cac-ad30-f91537a68f67",
    "buyer_addr": "Text cc1b2a01-ffe0-457f-8537-7916c82b4424",
    "buyer_phone": "Text 4b36d36f-d682-4880-ba12-13638205f5fe",
    "buyer_email": "Text 188f6c5c-8a93-4b8d-b8d4-e644002d7edc",
    "lender": "Text 4b3c66d1-5758-4d0d-a37c-de6699942c4f",
    "lender_phone": "Text 59ba91a8-02a7-48e3-8dd3-95e82e55844a",
    "lender_email": "Text c13d8117-81d3-4706-8a68-d2dcec38c6ea",
    "agent_company": "Text f808fedf-2693-463d-89e2-951d8050b07e",
    "agent": "Text a046a325-ddda-4b31-a003-235b7518ba7e",
    "agent_addr": "Text d013b09c-fb1f-4d99-b581-d0156790c335",
    "agent_phone": "Text 23334bc8-ddf6-44a1-a35d-147103a1b550",
    "agent_email": "Text 17288322-1f7b-4925-a69b-793f60c4b0a6",
    "offer_price": "Text 3ab9c346-fe20-4711-9ccd-0284c0fa9a80",
    "earnest": "Text 259eaae0-9e57-4740-95d2-8f6007241ade",
    "down": "Text a4fb3811-c571-4ae9-9ee3-6ccef7a4cd17",
    "closing_date": "Text d2980542-011c-41b0-82b2-35ca9a20510a",
    "credit": "Text 9a4d1dcb-24fd-422a-a0f6-a118c1121e4d",
    "inspection_days": "Text 7bded76a-a264-4c93-a2d1-6157836e1934",
    "financing_days": "Text 1ff36d5c-800f-4784-ac0f-354347119518",
    "attorney_days": "Text 67a70803-f505-42c3-a355-2f8b36f453b6",
    "other": "Text 094ac437-25a3-4e22-b259-3d8fc95e6f7f",
}

CONST = {
    "buyer_entity": "Paragon Government Solutions LLC, and/or assigns",
    "buyer_addr": "11166 Fairfax Blvd STE 500, Fairfax, VA 22030",
    "buyer_phone": "888-495-6935",
    "buyer_email": "charlesp@paragongovsolutions.net",
    "lender": "N/A - All Cash",
    "lender_phone": "N/A",
    "lender_email": "N/A",
    "agent_company": "N/A",
    "agent": "Unrepresented (Principal Buyer)",
    "agent_addr": "N/A",
    "agent_phone": "N/A",
    "agent_email": "N/A",
    "earnest": "$1,000",
    "down": "100% Cash",
    "closing_date": "Within 21 days of acceptance",
    "credit": "None",
    "inspection_days": "10",
    "financing_days": "0",
    "attorney_days": "0",
    "other": "Sold AS-IS, where-is. All-cash purchase, no financing or appraisal contingency. Buyer pays standard closing costs.",
}

PROPS = [
    ("9633 S Princeton Ave, Chicago, IL 60628", "$77,000.00", "Parkvue_Cover_9633_Princeton.pdf"),
    ("8435 S Cregier Ave, Chicago, IL 60617", "$158,500.00", "Parkvue_Cover_8435_Cregier.pdf"),
    ("1328 W 98th St, Chicago, IL 60643", "$134,500.00", "Parkvue_Cover_1328_W98th.pdf"),
    ("12511 S State St, Chicago, IL 60628", "$128,500.00", "Parkvue_Cover_12511_S_State.pdf"),
]

# circle-one option boxes (x0,y0,x1,y1) from pdfminer; pad a little
CIRCLES = [
    (287.1, 344.8, 334.4, 356.3),  # INVESTOR
    (375.9, 323.6, 391.0, 335.2),  # NO (viewed interior)
    (244.3, 302.5, 269.5, 314.0),  # CASH
]


def overlay():
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(612, 792))
    c.setStrokeColor(HexColor("#C00000"))
    c.setLineWidth(1.3)
    for x0, y0, x1, y1 in CIRCLES:
        c.ellipse(x0 - 5, y0 - 4, x1 + 5, y1 + 4)
    c.save()
    buf.seek(0)
    return PdfReader(buf)


def build(addr, price, out):
    reader = PdfReader(BLANK)
    writer = PdfWriter()
    writer.append(reader)
    vals = dict(CONST)
    vals["property"] = addr
    vals["offer_price"] = price
    field_values = {F[k]: v for k, v in vals.items()}
    writer.update_page_form_field_values(writer.pages[0], field_values, auto_regenerate=False)
    # ensure viewers render the values
    try:
        writer.set_need_appearances_writer(True)
    except Exception:
        writer._root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)
    # overlay circles on top
    writer.pages[0].merge_page(overlay().pages[0])
    with open(out, "wb") as f:
        writer.write(f)
    print("Saved:", out)


if __name__ == "__main__":
    for addr, price, out in PROPS:
        build(addr, price, out)

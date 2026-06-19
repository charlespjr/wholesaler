#!/usr/bin/env python3
"""Generate Illinois cash/as-is Purchase Agreements for the 4 Parkvue
properties, matching the Paragon PA format (same as the 1083 Birch PA).
POF not included (doubleclose.com, attached separately)."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable)

NAVY = colors.HexColor("#2E4057")
styles = getSampleStyleSheet()
H = ParagraphStyle("H", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=14, alignment=TA_CENTER, textColor=NAVY, spaceAfter=2)
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontName="Helvetica", fontSize=9, alignment=TA_CENTER, spaceAfter=10)
TITLE = ParagraphStyle("TITLE", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=13, alignment=TA_CENTER, spaceBefore=4, spaceAfter=2)
SUBT = ParagraphStyle("SUBT", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=10, alignment=TA_CENTER, spaceAfter=12)
SEC = ParagraphStyle("SEC", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10.5, spaceBefore=8, spaceAfter=3)
BODY = ParagraphStyle("BODY", parent=styles["Normal"], fontName="Helvetica", fontSize=10, alignment=TA_JUSTIFY, leading=14, spaceAfter=6)
SIG = ParagraphStyle("SIG", parent=styles["Normal"], fontName="Helvetica", fontSize=10, leading=14)

PROPS = [
    ("9633 S Princeton Ave, Chicago, Cook County, IL 60628", "$77,000.00 (Seventy-Seven Thousand and 00/100 Dollars)", "Offer_9633_Princeton_Purchase_Agreement.pdf"),
    ("8435 S Cregier Ave, Chicago, Cook County, IL 60617", "$158,500.00 (One Hundred Fifty-Eight Thousand Five Hundred and 00/100 Dollars)", "Offer_8435_Cregier_Purchase_Agreement.pdf"),
    ("1328 W 98th St, Chicago, Cook County, IL 60643", "$134,500.00 (One Hundred Thirty-Four Thousand Five Hundred and 00/100 Dollars)", "Offer_1328_W98th_Purchase_Agreement.pdf"),
    ("12511 S State St, Chicago, Cook County, IL 60628", "$128,500.00 (One Hundred Twenty-Eight Thousand Five Hundred and 00/100 Dollars)", "Offer_12511_S_State_Purchase_Agreement.pdf"),
]


def build(addr, price_str, out):
    doc = SimpleDocTemplate(out, pagesize=letter, leftMargin=0.85*inch, rightMargin=0.85*inch, topMargin=0.7*inch, bottomMargin=0.6*inch)
    e = []
    e.append(Paragraph("PARAGON GOVERNMENT SOLUTIONS LLC", H))
    e.append(Paragraph("11166 Fairfax Blvd STE 500, Fairfax, VA 22030 &middot; 888-495-6935 &middot; charles@paragongovsolutions.net", SUB))
    e.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceBefore=2, spaceAfter=8))
    e.append(Paragraph("RESIDENTIAL AGREEMENT TO PURCHASE AND SELL", TITLE))
    e.append(Paragraph("(Illinois &mdash; Cash Purchase, As-Is)", SUBT))
    e.append(Paragraph('This Agreement is made on June 19, 2026, between Paragon Government Solutions LLC, and/or assigns ("Buyer") and the Owner(s) of Record of the Property ("Seller").', BODY))
    secs = [
        ("1. PROPERTY", 'Seller agrees to sell and Buyer agrees to purchase the real property and improvements located at %s, together with all fixtures and improvements (the "Property").' % addr),
        ("2. PURCHASE PRICE", "The total purchase price is %s, payable in CASH at closing. This is a cash purchase with NO financing or appraisal contingency." % price_str),
        ("3. EARNEST MONEY", "Buyer shall deposit $1,000.00 in earnest money with the closing agent/title company within three (3) business days after the Date of Acceptance, credited to the price at closing."),
        ("4. AS-IS CONDITION", 'Buyer accepts the Property in its present "AS-IS, WHERE-IS" condition. Seller shall make no repairs, improvements, or warranties as to condition. Buyer acknowledges utilities may not be activated for inspection.'),
        ("5. INSPECTION / DUE DILIGENCE", "Buyer shall have a ten (10) day inspection and feasibility period from the Date of Acceptance to inspect the Property and review title. Buyer may terminate for any reason within this period by written notice, and the earnest money shall be refunded in full."),
        ("6. TITLE", "Seller shall convey good and marketable title by warranty deed, free of liens and encumbrances except those of record acceptable to Buyer. Title work shall be performed by a closing agent of Buyer's designation."),
        ("7. CLOSING", "Closing shall occur on or before twenty-one (21) days after acceptance, or on the seller's preferred timeline, at a title company/closing agent selected by Buyer. Buyer pays standard buyer closing costs; each party bears its customary costs per Cook County practice."),
        ("8. POSSESSION", "Possession shall transfer to Buyer at closing, free of occupants unless otherwise agreed in writing."),
        ("9. ASSIGNMENT", "Buyer may freely assign this Agreement and all rights hereunder to any person or entity without further consent of Seller. Buyer's assignee shall assume Buyer's obligations at closing."),
        ("10. DEFAULT", "If Buyer defaults, Seller's sole remedy is retention of the earnest money as liquidated damages. If Seller defaults, Buyer may seek specific performance or refund of earnest money."),
        ("11. GOVERNING LAW", "This Agreement is governed by the laws of the State of Illinois."),
        ("12. ENTIRE AGREEMENT", "This Agreement constitutes the entire agreement of the parties and may be amended only in writing signed by both parties. This offer expires three (3) business days from the date above if not accepted."),
    ]
    for h, b in secs:
        e.append(Paragraph(h, SEC))
        e.append(Paragraph(b, BODY))
    e.append(Spacer(1, 14))
    sig = Table([
        [Paragraph("<b>BUYER</b>", SIG), Paragraph("<b>SELLER</b>", SIG)],
        [Paragraph("______________________________<br/>Charles Pleasant, Manager<br/>Paragon Government Solutions LLC<br/>Date: __________", SIG),
         Paragraph("______________________________<br/>Owner of Record<br/><br/>Date: __________", SIG)],
    ], colWidths=[3.2*inch, 3.2*inch])
    sig.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 1), (-1, 1), 10)]))
    e.append(sig)
    doc.build(e)
    print("Saved:", out)


if __name__ == "__main__":
    for addr, price, out in PROPS:
        build(addr, price, out)

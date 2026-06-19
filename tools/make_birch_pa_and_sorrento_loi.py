#!/usr/bin/env python3
"""
Generate two deal documents:
  1) Residential Agreement to Purchase and Sell (Georgia, cash, as-is) for
     1083 Birch St SW, Atlanta, GA 30310 @ $92,100 (agent Charles Hard interested).
  2) Letter of Intent (revised, as-is WITH existing occupant) for
     9394 Sorrento St, Detroit, MI 48228 @ $40,000 (agent Robyn Miller).

Matches the existing Paragon PA + LOI formatting/branding. No POF generated —
proof of funds comes from doubleclose.com and is attached manually.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paragon_brand import brand_header, brand_footer

NAVY = colors.HexColor("#2E4057")
styles = getSampleStyleSheet()
H = ParagraphStyle("H", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=14, alignment=TA_CENTER, textColor=NAVY, spaceAfter=2)
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontName="Helvetica", fontSize=9, alignment=TA_CENTER, spaceAfter=10)
TITLE = ParagraphStyle("TITLE", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=13, alignment=TA_CENTER, spaceBefore=4, spaceAfter=2)
SUBT = ParagraphStyle("SUBT", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=10, alignment=TA_CENTER, spaceAfter=12)
SEC = ParagraphStyle("SEC", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10.5, spaceBefore=8, spaceAfter=3)
BODY = ParagraphStyle("BODY", parent=styles["Normal"], fontName="Helvetica", fontSize=10, alignment=TA_JUSTIFY, leading=14, spaceAfter=6)
SIG = ParagraphStyle("SIG", parent=styles["Normal"], fontName="Helvetica", fontSize=10, leading=14)


def birch_pa(out="Offer_1083_Birch_Purchase_Agreement.pdf"):
    doc = SimpleDocTemplate(out, pagesize=letter, leftMargin=0.85*inch, rightMargin=0.85*inch, topMargin=0.7*inch, bottomMargin=0.95*inch)
    e = []
    e.extend(brand_header())
    e.append(Paragraph("RESIDENTIAL AGREEMENT TO PURCHASE AND SELL", TITLE))
    e.append(Paragraph("(Georgia &mdash; Cash Purchase, As-Is)", SUBT))
    e.append(Paragraph('This Agreement is made on June 19, 2026, between Paragon Government Solutions LLC, and/or assigns ("Buyer") and the Owner(s) of Record of the Property ("Seller").', BODY))
    secs = [
        ("1. PROPERTY", 'Seller agrees to sell and Buyer agrees to purchase the real property and improvements located at 1083 Birch St SW, Atlanta, Fulton County, GA 30310, together with all fixtures and improvements (the "Property").'),
        ("2. PURCHASE PRICE", "The total purchase price is $92,100.00 (Ninety-Two Thousand One Hundred and 00/100 Dollars), payable in CASH at closing. This is a cash purchase with NO financing or appraisal contingency."),
        ("3. EARNEST MONEY", "Buyer shall deposit $1,000.00 in earnest money with the closing agent/title company within three (3) business days after the Date of Acceptance, credited to the price at closing."),
        ("4. AS-IS CONDITION", 'Buyer accepts the Property in its present "AS-IS, WHERE-IS" condition. Seller shall make no repairs, improvements, or warranties as to condition.'),
        ("5. INSPECTION / DUE DILIGENCE", "Buyer shall have a ten (10) day inspection and feasibility period from the Date of Acceptance to inspect the Property and review title. Buyer may terminate for any reason within this period by written notice, and the earnest money shall be refunded in full."),
        ("6. TITLE", "Seller shall convey good and marketable title by warranty deed, free of liens and encumbrances except those of record acceptable to Buyer. Title work shall be performed by a closing agent of Buyer's designation."),
        ("7. CLOSING", "Closing shall occur on or before July 10, 2026, or within twenty-one (21) days of acceptance, at a title company/closing attorney selected by Buyer. Buyer pays standard buyer closing costs; each party bears its customary costs."),
        ("8. POSSESSION", "Possession shall transfer to Buyer at closing, free of occupants unless otherwise agreed in writing."),
        ("9. ASSIGNMENT", "Buyer may freely assign this Agreement and all rights hereunder to any person or entity without further consent of Seller. Buyer's assignee shall assume Buyer's obligations at closing."),
        ("10. DEFAULT", "If Buyer defaults, Seller's sole remedy is retention of the earnest money as liquidated damages. If Seller defaults, Buyer may seek specific performance or refund of earnest money."),
        ("11. GOVERNING LAW", "This Agreement is governed by the laws of the State of Georgia."),
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
    doc.build(e, onFirstPage=brand_footer, onLaterPages=brand_footer)
    print("Saved:", out)


def sorrento_loi(out="Offer_9394_Sorrento_LOI.pdf"):
    CELL_L = ParagraphStyle("CL", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=13)
    CELL_R = ParagraphStyle("CR", parent=styles["Normal"], fontName="Helvetica", fontSize=10, leading=13)
    FOOT = ParagraphStyle("FT", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=7.5, textColor=colors.HexColor("#555555"), leading=10)
    BODY2 = ParagraphStyle("B2", parent=styles["Normal"], fontName="Helvetica", fontSize=10, leading=14, spaceAfter=8)
    def row(l, v): return [Paragraph(l, CELL_L), Paragraph(v, CELL_R)]
    doc = SimpleDocTemplate(out, pagesize=letter, leftMargin=0.85*inch, rightMargin=0.85*inch, topMargin=0.7*inch, bottomMargin=0.95*inch)
    e = []
    e.extend(brand_header())
    e.append(Paragraph("LETTER OF INTENT TO PURCHASE", TITLE))
    e.append(Spacer(1, 8))
    e.append(Paragraph("Date: June 19, 2026", BODY2))
    e.append(Paragraph("To: Robyn Miller, Listing Agent &mdash; Detroit Property Exchange (rmiller@detpro.com)", BODY2))
    e.append(Paragraph("Re: Property at 9394 Sorrento St, Detroit, MI 48228", BODY2))
    e.append(Paragraph("This revised Letter of Intent sets forth the principal terms under which the Buyer proposes to purchase the above Property strictly as-is, WITH the existing occupant in place. It is non-binding and intended for presentation to the Seller; upon mutual interest the parties will execute a formal Purchase Agreement.", BODY2))
    e.append(Spacer(1, 4))
    data = [
        row("Buyer", "Paragon Government Solutions LLC, and/or assigns"),
        row("Seller", "Owner(s) of Record"),
        row("Property", "9394 Sorrento St, Detroit, MI 48228 (Single-Family Residence)"),
        row("Purchase Price", "$40,000.00 (Forty Thousand Dollars), ALL CASH"),
        row("Earnest Money", "$1,000.00 deposited to title/escrow within 3 business days of acceptance"),
        row("Condition", "Strictly AS-IS, WHERE-IS; Seller makes no repairs"),
        row("Occupancy", "Property is understood to have an existing occupant. Buyer acquires AS-IS WITH the occupant in place; Seller is NOT required to deliver vacant possession or to remove/evict any occupant. Buyer assumes full responsibility for all occupancy resolution after closing."),
        row("Due Diligence", "10-day inspection/feasibility period; Buyer may cancel for any reason, EMD refundable"),
        row("Closing", "On or before 21 days from acceptance, or the seller's preferred timeline"),
        row("Title", "Seller conveys clear, marketable title by warranty deed"),
        row("Assignment", "This offer and resulting contract are assignable by Buyer"),
        row("Financing", "None &mdash; cash purchase, no financing or appraisal contingency"),
        row("Offer Expires", "5 business days from the date above"),
    ]
    t = Table(data, colWidths=[1.4*inch, 5.0*inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#CCCCCC")), ("BOX", (0, 0), (-1, -1), 0.6, NAVY), ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F4F7")), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7)]))
    e.append(t)
    e.append(Spacer(1, 12))
    e.append(Paragraph("We are direct cash buyers who routinely take on occupied/squatter situations as-is, so the Seller does not have to handle the eviction, cleanout, or holding costs. We can close on the Seller's timeline. Thank you for presenting this offer to your Seller.", BODY2))
    e.append(Spacer(1, 18))
    for ln in ["_______________________________", "Charles Pleasant, Manager", "Paragon Government Solutions LLC", "Buyer"]:
        e.append(Paragraph(ln, BODY2))
    e.append(Spacer(1, 12))
    e.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#999999"), spaceBefore=2, spaceAfter=6))
    e.append(Paragraph("This Letter of Intent is non-binding and does not create a contract of sale. It is an expression of interest only; binding obligations arise only upon a fully executed Purchase Agreement.", FOOT))
    doc.build(e, onFirstPage=brand_footer, onLaterPages=brand_footer)
    print("Saved:", out)


if __name__ == "__main__":
    birch_pa()
    sorrento_loi()

"""Branded cash purchase agreements for the Detroit + Cleveland new-lead offers."""
import os, sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paragon_brand import brand_header, brand_footer

NAVY = colors.HexColor("#2E4057")
s = getSampleStyleSheet()
TITLE = ParagraphStyle('T', parent=s['Title'], fontSize=14, textColor=NAVY, alignment=TA_CENTER, spaceAfter=2)
SUBT = ParagraphStyle('ST', parent=s['Normal'], fontSize=9, textColor=colors.HexColor("#666666"), alignment=TA_CENTER, spaceAfter=10)
H = ParagraphStyle('H', parent=s['Heading2'], fontSize=10.5, textColor=NAVY, spaceBefore=8, spaceAfter=3)
BODY = ParagraphStyle('B', parent=s['Normal'], fontSize=9.5, alignment=TA_JUSTIFY, leading=13, spaceAfter=2)
SIG = ParagraphStyle('SIG', parent=s['Normal'], fontSize=9.5, leading=20)


def build(d):
    e = []
    e.extend(brand_header())
    e.append(Paragraph("RESIDENTIAL AGREEMENT TO PURCHASE AND SELL", TITLE))
    e.append(Paragraph(d['sub'], SUBT))
    e.append(Paragraph("This Agreement is made on %s, between <b>Paragon Government Solutions LLC, "
                       "and/or assigns</b> (\"Buyer\") and the Owner(s) of Record (\"Seller\")." % d['date'], BODY))
    secs = [
        ("1. PROPERTY", "The real property known as <b>%s</b>%s, including all rights and "
                        "appurtenances (the \"Property\")." % (d['addr'], d.get('extra', ''))),
        ("2. PURCHASE PRICE", "<b>%s</b>, payable ALL CASH at closing. This is a cash purchase with "
                              "NO financing or appraisal contingency." % d['price_words']),
        ("3. EARNEST MONEY", "Buyer shall deposit $1,000.00 in earnest money with the closing agent/title "
                             "company within three (3) business days after the Date of Acceptance, credited "
                             "to the purchase price at closing."),
        ("4. CONDITION", "Buyer accepts the Property <b>AS-IS, WHERE-IS</b>. Seller makes no repairs, credits, "
                         "or warranties as to condition." + d.get('tenancy', '')),
        ("5. INSPECTION / DUE DILIGENCE", "Buyer shall have a ten (10) day inspection/feasibility period from the "
                                          "Date of Acceptance to verify condition, title, taxes/liens%s. Buyer may "
                                          "terminate for any reason within this period by written notice, with full "
                                          "refund of earnest money." % d.get('dd', '')),
        ("6. TITLE", "Seller shall convey good and marketable title by warranty deed, free of liens and "
                     "encumbrances except those of record acceptable to Buyer."),
        ("7. CLOSING", "Closing shall occur within twenty-one (21) days after acceptance, or on the Seller's "
                       "preferred timeline, at a title company/closing agent selected by Buyer. Buyer pays "
                       "standard closing costs."),
        ("8. ASSIGNMENT", "Buyer may assign this Agreement and all rights hereunder."),
        ("9. DEFAULT", "If Buyer defaults, Seller's sole remedy is the earnest money as liquidated damages. "
                       "If Seller defaults, the earnest money shall be refunded to Buyer."),
    ]
    for h, b in secs:
        e.append(Paragraph(h, H))
        e.append(Paragraph(b, BODY))
    e.append(Spacer(1, 16))
    e.append(Paragraph("Buyer: Paragon Government Solutions LLC, and/or assigns", SIG))
    e.append(Paragraph("By: ______________________________   Date: ________________", SIG))
    e.append(Spacer(1, 8))
    e.append(Paragraph("Seller: ____________________________   Date: ________________", SIG))
    e.append(Paragraph("Seller: ____________________________   Date: ________________", SIG))
    doc = SimpleDocTemplate(d['out'], pagesize=letter, leftMargin=0.85 * inch, rightMargin=0.85 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.95 * inch)
    doc.build(e, onFirstPage=brand_footer, onLaterPages=brand_footer)
    print("Saved:", d['out'])


DEALS = [
    dict(out="Offer_16093_Liberal_Purchase_Agreement.pdf", addr="16093 Liberal St, Detroit, MI 48205",
         sub="(Michigan — Cash Purchase, As-Is)", date="June 19, 2026",
         price_words="$10,000.00 (Ten Thousand and 00/100 Dollars)", dd=", and utilities", extra=""),
    dict(out="Offer_13595_Wyoming_Purchase_Agreement.pdf", addr="13595 Wyoming Ave, Detroit, MI 48238",
         sub="(Michigan — Cash Purchase, As-Is)", date="June 19, 2026",
         price_words="$8,000.00 (Eight Thousand and 00/100 Dollars)", dd=", and utilities", extra=""),
    dict(out="Offer_716_E160th_Purchase_Agreement.pdf", addr="716 E 160th St, Cleveland, OH 44110",
         sub="(Ohio — Cash Purchase, As-Is, Tenant-Occupied)", date="June 19, 2026",
         price_words="$40,000.00 (Forty Thousand and 00/100 Dollars)",
         dd=", legal unit count, zoning, and utilities", extra=" (a multi-unit/triplex building)",
         tenancy=" The Property is sold subject to existing tenancies; Seller shall provide current leases, "
                 "rent roll, and any Section 8/HAP documentation."),
]
for _d in DEALS:
    build(_d)

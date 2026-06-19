#!/usr/bin/env python3
"""
Generate the Letter of Intent PDF for 511 Solar Dr, San Antonio, TX 78227.
Matches the format used for Offer_5001_Beaucaire_LOI.pdf (branded header,
two-column term table, signature block, non-binding footer).

This deal is a tenant-occupied buy-and-hold: seller is a fellow investor,
property is leased through 7/20/2026 and in good condition, so the LOI is
written to acquire subject to the existing tenancy (no "subject to vacancy").
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable)

OUT = "Offer_511_Solar_LOI.pdf"
NAVY = colors.HexColor("#2E4057")

styles = getSampleStyleSheet()
H = ParagraphStyle("H", parent=styles["Normal"], fontName="Helvetica-Bold",
                   fontSize=14, alignment=TA_CENTER, textColor=NAVY,
                   spaceAfter=2)
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontName="Helvetica",
                     fontSize=9, alignment=TA_CENTER, textColor=colors.black,
                     spaceAfter=10)
TITLE = ParagraphStyle("TITLE", parent=styles["Normal"],
                       fontName="Helvetica-Bold", fontSize=13,
                       alignment=TA_CENTER, spaceBefore=6, spaceAfter=12)
BODY = ParagraphStyle("BODY", parent=styles["Normal"], fontName="Helvetica",
                      fontSize=10, alignment=TA_LEFT, leading=14, spaceAfter=8)
CELL_L = ParagraphStyle("CELL_L", parent=styles["Normal"],
                        fontName="Helvetica-Bold", fontSize=10, leading=13)
CELL_R = ParagraphStyle("CELL_R", parent=styles["Normal"],
                        fontName="Helvetica", fontSize=10, leading=13)
FOOT = ParagraphStyle("FOOT", parent=styles["Normal"], fontName="Helvetica-Oblique",
                      fontSize=7.5, alignment=TA_LEFT, textColor=colors.HexColor("#555555"),
                      leading=10)


def row(label, value):
    return [Paragraph(label, CELL_L), Paragraph(value, CELL_R)]


def build():
    doc = SimpleDocTemplate(OUT, pagesize=letter,
                            leftMargin=0.85 * inch, rightMargin=0.85 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.6 * inch)
    e = []
    e.append(Paragraph("PARAGON GOVERNMENT SOLUTIONS LLC", H))
    e.append(Paragraph("11166 Fairfax Blvd STE 500, Fairfax, VA 22030 &middot; "
                       "888-495-6935 &middot; charles@paragongovsolutions.net", SUB))
    e.append(HRFlowable(width="100%", thickness=1, color=NAVY,
                        spaceBefore=2, spaceAfter=10))

    e.append(Paragraph("LETTER OF INTENT TO PURCHASE", TITLE))
    e.append(Paragraph("Date: June 19, 2026", BODY))
    e.append(Paragraph("To: Mary Nielsen, Listing Agent &mdash; Exquisite "
                       "Properties, LLC (mnielsen@exquisitesa.com)", BODY))
    e.append(Paragraph("Re: Property at 511 Solar Dr, San Antonio, TX 78227", BODY))
    e.append(Paragraph(
        "This Letter of Intent sets forth the principal terms under which the "
        "Buyer proposes to purchase the above Property as a buy-and-hold rental, "
        "subject to the existing tenancy. It is non-binding and intended for "
        "presentation to the Seller; upon mutual interest the parties will "
        "execute a formal Purchase Agreement.", BODY))
    e.append(Spacer(1, 4))

    data = [
        row("Buyer", "Paragon Government Solutions LLC, and/or assigns"),
        row("Seller", "Owner(s) of Record"),
        row("Property", "511 Solar Dr, San Antonio, TX 78227 (Single-Family Residence)"),
        row("Purchase Price", "$160,000.00 (One Hundred Sixty Thousand Dollars), ALL CASH"),
        row("Earnest Money", "$2,500.00 deposited to title/escrow within 3 business days of acceptance"),
        row("Condition", "Strictly AS-IS, WHERE-IS; Seller makes no repairs"),
        row("Tenancy", "Property is tenant-occupied through 7/20/2026. Buyer will "
                       "honor the existing lease and acquire subject to the tenancy. "
                       "Seller to provide a copy of the lease and a tenant estoppel "
                       "prior to closing."),
        row("Due Diligence", "10-day inspection/feasibility period; Buyer may cancel "
                             "for any reason, EMD refundable"),
        row("Closing", "On or before July 20, 2026, or within ~30 days of acceptance"),
        row("Closing Costs", "Buyer pays standard buyer closing costs; each party its customary costs"),
        row("Title", "Seller conveys clear, marketable title by warranty deed"),
        row("Assignment", "This offer and resulting contract are assignable by Buyer"),
        row("Financing", "None &mdash; cash purchase, no financing or appraisal contingency"),
        row("Offer Expires", "5 business days from the date above"),
    ]
    t = Table(data, colWidths=[1.4 * inch, 5.0 * inch])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#CCCCCC")),
        ("BOX", (0, 0), (-1, -1), 0.6, NAVY),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F4F7")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    e.append(t)
    e.append(Spacer(1, 12))

    e.append(Paragraph(
        "We are direct cash buyers underwriting this as a long-term rental and "
        "can close on the Seller's timeline with the tenant in place. We welcome "
        "a virtual meeting to discuss terms. Thank you for presenting this offer "
        "to your Seller.", BODY))
    e.append(Spacer(1, 18))
    e.append(Paragraph("_______________________________", BODY))
    e.append(Paragraph("Charles Pleasant, Manager", BODY))
    e.append(Paragraph("Paragon Government Solutions LLC", BODY))
    e.append(Paragraph("Buyer", BODY))
    e.append(Spacer(1, 14))
    e.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#999999"),
                        spaceBefore=2, spaceAfter=6))
    e.append(Paragraph(
        "This Letter of Intent is non-binding and does not create a contract of "
        "sale. It is an expression of interest only; binding obligations arise "
        "only upon a fully executed Purchase Agreement.", FOOT))

    doc.build(e)
    print("Saved:", OUT)


if __name__ == "__main__":
    build()

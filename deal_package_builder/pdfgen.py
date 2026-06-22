"""Professional wholesale deal-package PDF (ReportLab)."""
from __future__ import annotations

import logging
import os
from typing import List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (HRFlowable, Image, KeepInFrame, PageBreak,
                                Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from images import Photo, caption_for
from models import Property, fmt_money, fmt_plain

log = logging.getLogger("deal_packages.pdf")

NAVY = colors.HexColor("#1F2D3D")     # dark blue / charcoal headings
CHARCOAL = colors.HexColor("#333333")
GREY = colors.HexColor("#666666")
LIGHT = colors.HexColor("#EAEFF4")
RULE = colors.HexColor("#C9D3DD")

_ss = getSampleStyleSheet()
TITLE = ParagraphStyle("t", parent=_ss["Title"], textColor=NAVY, fontSize=22, leading=26)
H1 = ParagraphStyle("h1", parent=_ss["Heading1"], textColor=NAVY, fontSize=16, spaceAfter=6)
H2 = ParagraphStyle("h2", parent=_ss["Heading2"], textColor=NAVY, fontSize=12, spaceBefore=10, spaceAfter=4)
BODY = ParagraphStyle("b", parent=_ss["BodyText"], textColor=CHARCOAL, fontSize=10.5, leading=15)
SMALL = ParagraphStyle("s", parent=_ss["BodyText"], textColor=GREY, fontSize=8.5, leading=11)
CENTER = ParagraphStyle("c", parent=BODY, alignment=TA_CENTER)
CAP = ParagraphStyle("cap", parent=_ss["BodyText"], textColor=GREY, fontSize=8.5,
                     leading=10, alignment=TA_CENTER)


def _header_footer(address: str):
    def draw(canvas, doc):
        canvas.saveState()
        w, h = letter
        # header: property address
        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.setFillColor(NAVY)
        canvas.drawString(0.85 * inch, h - 0.5 * inch, address[:95])
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.5)
        canvas.line(0.85 * inch, h - 0.58 * inch, w - 0.85 * inch, h - 0.58 * inch)
        # footer: page number
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GREY)
        canvas.drawCentredString(w / 2, 0.45 * inch, f"Page {doc.page}")
        canvas.restoreState()
    return draw


def _kv_table(rows, col0=2.0 * inch, col1=4.1 * inch):
    data = [[k, Paragraph(v, BODY)] for k, v in rows]
    t = Table(data, colWidths=[col0, col1])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 10),
        ("FONT", (1, 0), (1, -1), "Helvetica", 10),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("TEXTCOLOR", (1, 0), (1, -1), CHARCOAL),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F7F9FB")]),
    ]))
    return t


def _fit_image(path: str, max_w: float, max_h: float):
    """Return a ReportLab Image scaled to fit a box, preserving aspect ratio."""
    iw, ih = ImageReader(path).getSize()
    ar = ih / float(iw)
    w = max_w
    h = w * ar
    if h > max_h:
        h = max_h
        w = h / ar
    return Image(path, width=w, height=h)


# -----------------------------------------------------------------------------
def build_pdf(prop: Property, photos: List[Photo], out_path: str,
              photos_note: str = "") -> str:
    story = []
    addr = prop.property_address or prop.title

    # ---------- PAGE 1: COVER ----------
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("WHOLESALE INVESTMENT OPPORTUNITY", H2))
    story.append(Paragraph(addr, TITLE))
    if prop.full_location:
        story.append(Paragraph(prop.full_location, BODY))
    story.append(HRFlowable(width="100%", thickness=1.2, color=NAVY, spaceBefore=8, spaceAfter=10))

    cover_photo = next((p for p in photos if p.label.startswith("front")), photos[0] if photos else None)
    if cover_photo:
        img = _fit_image(cover_photo.path, 6.3 * inch, 3.7 * inch)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 6))
    else:
        box = Table([[Paragraph("Listing photos could not be retrieved.", CAP)]],
                    colWidths=[6.3 * inch], rowHeights=[2.2 * inch])
        box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, RULE),
                                 ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                 ("BACKGROUND", (0, 0), (-1, -1), LIGHT)]))
        story.append(box)
        story.append(Spacer(1, 6))

    story.append(_kv_table([
        ("Asking price", fmt_money(prop.asking_price)),
        ("Suggested cash offer", fmt_money(prop.offer_price)),
        ("Estimated ARV", fmt_money(prop.arv)),
        ("Estimated repairs", fmt_money(prop.repair_estimate)),
        ("Estimated assignment fee", fmt_money(prop.assignment_fee)),
    ]))
    story.append(PageBreak())

    # ---------- PAGE 2: PROPERTY SUMMARY ----------
    story.append(Paragraph("Property Summary", H1))
    story.append(HRFlowable(width="100%", thickness=0.8, color=RULE, spaceAfter=8))
    url_disp = prop.listing_url or "Not provided"
    if len(url_disp) > 90:
        url_disp = f'<link href="{prop.listing_url}">{prop.listing_url[:90]}…</link>'
    elif prop.listing_url:
        url_disp = f'<link href="{prop.listing_url}">{prop.listing_url}</link>'
    story.append(_kv_table([
        ("Property type", fmt_plain(prop.property_type)),
        ("Bedrooms", fmt_plain(prop.beds)),
        ("Bathrooms", fmt_plain(prop.baths)),
        ("Square footage", fmt_plain(prop.sqft)),
        ("Lot size", fmt_plain(prop.lot_size)),
        ("Year built", fmt_plain(prop.year_built)),
        ("Listing status", fmt_plain(prop.listing_status)),
        ("Listing source", fmt_plain(prop.source.title() if prop.source and prop.source != "unknown" else "")),
        ("Listing URL", url_disp),
        ("Deal notes", fmt_plain(prop.notes)),
    ]))
    story.append(PageBreak())

    # ---------- PAGE 3: DEAL ANALYSIS ----------
    story.append(Paragraph("Deal Analysis", H1))
    story.append(HRFlowable(width="100%", thickness=0.8, color=RULE, spaceAfter=8))
    rows = [
        ["Metric", "Value"],
        ["Asking price", fmt_money(prop.asking_price)],
        ["Suggested offer", fmt_money(prop.offer_price)],
        ["Repair estimate", fmt_money(prop.repair_estimate)],
        ["After Repair Value (ARV)", fmt_money(prop.arv)],
        ["Maximum Allowable Offer (MAO)", fmt_money(prop.mao)],
        ["Estimated assignment fee", fmt_money(prop.assignment_fee)],
        ["Estimated investor purchase price", fmt_money(prop.investor_purchase_price)],
        ["Estimated investor profit / equity spread", fmt_money(prop.investor_spread)],
    ]
    t = Table(rows, colWidths=[3.6 * inch, 2.5 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 10.5),
        ("FONT", (0, 1), (0, -1), "Helvetica", 10),
        ("FONT", (1, 1), (1, -1), "Helvetica-Bold", 10),
        ("TEXTCOLOR", (0, 1), (-1, -1), CHARCOAL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5F8")]),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    # highlight the MAO row
    t.setStyle(TableStyle([("BACKGROUND", (0, 5), (-1, 5), LIGHT)]))
    story.append(t)
    story.append(Spacer(1, 10))
    story.append(Paragraph("Formula: MAO = (ARV &times; 0.70) &minus; Repairs &minus; Assignment Fee. "
                           "Fields without source data are shown as &ldquo;Not provided&rdquo; and are not estimated.",
                           SMALL))
    if photos_note:
        story.append(Spacer(1, 6))
        story.append(Paragraph(photos_note, SMALL))

    # ---------- PHOTO PAGES (3 per page grid) ----------
    if photos:
        story.append(PageBreak())
        story.append(Paragraph("Property Photos", H1))
        story.append(HRFlowable(width="100%", thickness=0.8, color=RULE, spaceAfter=8))
        cell_w, cell_h = 3.0 * inch, 2.25 * inch
        pending = []

        def flush_row(buf):
            if not buf:
                return
            story.append(Table([buf], colWidths=[cell_w + 0.15 * inch] * len(buf),
                               style=TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                                 ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 10)])))

        per_page, on_page = 4, 0
        row_buf = []
        for ph in photos:
            try:
                img = _fit_image(ph.path, cell_w, cell_h)
            except Exception:
                continue
            cell = KeepInFrame(cell_w + 0.15 * inch, cell_h + 0.4 * inch,
                               [img, Spacer(1, 2), Paragraph(caption_for(ph.label), CAP)],
                               hAlign="CENTER")
            row_buf.append(cell)
            if len(row_buf) == 2:
                flush_row(row_buf)
                row_buf = []
                on_page += 2
                if on_page >= per_page:
                    story.append(PageBreak())
                    on_page = 0
        flush_row(row_buf)

    # ---------- FINAL PAGE: DISCLAIMER ----------
    story.append(PageBreak())
    story.append(Paragraph("Disclaimer", H1))
    story.append(HRFlowable(width="100%", thickness=0.8, color=RULE, spaceAfter=10))
    story.append(Paragraph(
        "This package is provided for informational and investment evaluation purposes only. "
        "Property details, repair estimates, values, availability, and financial projections must be "
        "independently verified. Photos remain the property of their respective owners or listing sources.",
        BODY))

    doc = SimpleDocTemplate(out_path, pagesize=letter, topMargin=0.75 * inch,
                            bottomMargin=0.7 * inch, leftMargin=0.85 * inch, rightMargin=0.85 * inch,
                            title=f"{addr} - Deal Package",
                            author="Paragon Government Solutions LLC")
    hf = _header_footer(addr)
    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    log.info("PDF written: %s", out_path)
    return out_path

"""Professional wholesale deal-package PDF (ReportLab)."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import List, Optional

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
SAY = ParagraphStyle("say", parent=BODY, fontSize=10.5, leading=15, leftIndent=8, rightIndent=8,
                     backColor=LIGHT, borderPadding=8, spaceAfter=8)
BUL = ParagraphStyle("bul", parent=BODY, leftIndent=14, spaceAfter=3)


@dataclass
class Brand:
    """Optional company branding for the package (e.g. Paragon letterhead)."""
    logo_path: Optional[str] = None
    company: str = ""
    line2: str = ""   # address | phone | email
    line3: str = ""   # identifiers | web


def _header_footer(address: str, brand: Optional[Brand] = None):
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

        if brand and (brand.company or brand.line2):
            # branded footer block (company / address / identifiers) + page no.
            base = 0.42 * inch
            canvas.setStrokeColor(NAVY)
            canvas.setLineWidth(0.6)
            canvas.line(0.85 * inch, base + 30, w - 0.85 * inch, base + 30)
            canvas.setFont("Helvetica-Bold", 8)
            canvas.setFillColor(NAVY)
            canvas.drawCentredString(w / 2, base + 20, brand.company)
            canvas.setFont("Helvetica", 7)
            canvas.setFillColor(GREY)
            if brand.line2:
                canvas.drawCentredString(w / 2, base + 10, brand.line2)
            if brand.line3:
                canvas.drawCentredString(w / 2, base, brand.line3)
            canvas.setFont("Helvetica", 7)
            canvas.setFillColor(GREY)
            canvas.drawRightString(w - 0.85 * inch, base + 33, f"Page {doc.page}")
        else:
            # plain footer: page number only
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


def _va_call_script(prop: Property) -> list:
    """VA agent call-script pages, driven by this deal's numbers + standing Q&A.
    Included in every package so the VA has talking points + the agent Q&A."""
    start = fmt_money(prop.offer_price)
    ceiling = fmt_money(prop.mao)
    listp = fmt_money(prop.asking_price)
    agent = prop.listing_agent or "the listing agent"
    agent_line = " — ".join([x for x in [prop.listing_agent, prop.agent_phone, prop.agent_email] if x]) or "Not provided"
    addr = prop.property_address or prop.title

    out = [Paragraph("VA Agent Call Script", H1),
           Paragraph("How to work this deal on the phone with the listing agent. Plain language to relay.", SMALL),
           HRFlowable(width="100%", thickness=1, color=NAVY, spaceBefore=4, spaceAfter=8)]

    out.append(Paragraph("At a glance", H2))
    out.append(_kv_table([
        ("Property", addr),
        ("Listing agent", agent_line),
        ("Their list price", listp),
        ("OUR OFFER", f"{start} cash (start here)"),
        ("Most we can pay", f"{ceiling} cash — NEVER higher. Above that, stop and call Charles."),
    ], col0=1.55 * inch, col1=4.55 * inch))

    out.append(Paragraph("Our terms (have these ready)", H2))
    out.append(_kv_table([
        ("Price", f"{start} cash (opening); {ceiling} absolute max"),
        ("Purchase", "All cash, as-is / where-is — we take all repair risk"),
        ("Earnest money", "$1,000 to title within 3 business days of acceptance"),
        ("Due diligence", "10-day inspection / feasibility period"),
        ("Close", "21 days (about 3 weeks), or the seller's timeline"),
        ("Contingencies", "NONE — no financing, no appraisal"),
        ("Buyer", "Paragon Government Solutions LLC, and/or assigns"),
        ("Proof of funds", "Yes — on request"),
    ]))

    if prop.arv and prop.repair_estimate and prop.builder_max:
        out.append(Paragraph("Why we're offering this number (say it plainly)", H2))
        out.append(Paragraph(
            f"Fixed up it's worth about <b>{fmt_money(prop.arv)}</b>, but it needs roughly "
            f"<b>{fmt_money(prop.repair_estimate)}</b> of work. After that a builder only pays about "
            f"<b>{fmt_money(prop.builder_max)}</b> for it, so to do the deal and make a small fee we buy in the "
            f"<b>{start}–{ceiling}</b> range. It's not a lowball — it's what the rehab allows.", BODY))

    out.append(Paragraph("Call flow", H2))
    out.append(Paragraph("<b>1. Open (returning the agent's call):</b>", BODY))
    out.append(Paragraph(f'"Hi {agent}, this is [your name] with Paragon Government Solutions, returning your call '
                         f'about {addr}. Thanks for getting back to me — is it still available?"', SAY))
    out.append(Paragraph("<b>2. Confirm condition &amp; feel out the seller:</b>", BODY))
    for b in ['"What kind of shape is it in — anything major done recently?"',
              '"How long\'s it been listed, and are there other offers?"',
              '"Is the seller flexible on price for a fast all-cash close? What\'s the lowest they\'d really take?"']:
        out.append(Paragraph("• " + b, BUL))
    out.append(Paragraph("<b>3. Make the offer:</b>", BODY))
    out.append(Paragraph(f'"Here\'s what we can do: {start} cash, as-is. $1,000 earnest to title in 3 days, a 10-day '
                         f'inspection, and we close in about 3 weeks or whenever the seller wants. No bank, no appraisal, '
                         f'no contingencies, proof of funds ready. We take all the repair risk, so that\'s where our number '
                         f'lands. If the seller wants a clean guaranteed close, we\'re ready to sign."', SAY))
    out.append(Paragraph("<b>4. Close the call:</b>", BODY))
    out.append(Paragraph('"What\'s the best email to send the written terms to? I\'ll get them over today."', SAY))

    out.append(Paragraph("The big question: “Are you wholesaling / assigning this?”", H2))
    out.append(Paragraph("Answer it <b>straight</b> — don't dodge, don't lie. Then pivot to performance:", BODY))
    out.append(Paragraph('"I\'m a cash buyer. I buy through my company, Paragon, and it\'s written ‘and/or assigns,’ '
                         'so I may bring in one of my funding partners to close — but either way you get a real close: '
                         'earnest money up front, proof of funds, and we perform. You\'re not chasing me."', SAY))
    for b in ["<b>Never deny it's assignable</b> — the contract literally says ‘and/or assigns.’",
              "<b>Anchor on performance</b> — earnest money + proof of funds + we close. That's what wins agents.",
              "<b>Keep the inspection tight (10 days)</b> — a long window makes agents think we're just shopping it.",
              "<b>REO / bank-owned only:</b> assignment is usually prohibited — there we double-close instead (doubleclose.com)."]:
        out.append(Paragraph("• " + b, BUL))

    out.append(Paragraph("Other questions the agent will ask (and the answers)", H2))
    for b in ['<b>"Proof of funds?"</b> &rarr; "Yes — I\'ll include it with the written terms."',
              '<b>"How much earnest, is it hard?"</b> &rarr; "$1,000 to title in 3 days; happy to make it firm after inspection."',
              '<b>"How fast can you close?"</b> &rarr; "About 3 weeks, or on the seller\'s timeline."',
              '<b>"Cash, no financing?"</b> &rarr; "All cash — no loan, no appraisal contingency."',
              '<b>"Come see it / walk it first?"</b> &rarr; "We don\'t do walkthroughs — we buy off photos and disclosures, then verify in our 10-day inspection."',
              '<b>"Are you actually going to close?"</b> &rarr; "Earnest money and proof of funds up front — we perform. I won\'t tie up your listing and disappear."',
              '<b>"Seller wants full list price."</b> &rarr; "Then we\'re probably not their buyer today — keep my number; if it sits and they get flexible, we close fast in cash."']:
        out.append(Paragraph("• " + b, BUL))

    out.append(Paragraph("Never do", H2))
    for b in [f"Go above <b>{ceiling}</b>. Higher = stop and call Charles.",
              "Promise to visit, tour, or walk the property.",
              "Send written terms before you have the agent's email.",
              "Send a signed offer without Charles okaying it first.",
              "Deny we may assign — be honest, anchor on performance."]:
        out.append(Paragraph("• " + b, BUL))
    return out


# -----------------------------------------------------------------------------
def build_pdf(prop: Property, photos: List[Photo], out_path: str,
              photos_note: str = "", brand: Optional[Brand] = None) -> str:
    story = []
    addr = prop.property_address or prop.title

    # ---------- PAGE 1: COVER ----------
    if brand and brand.logo_path and os.path.exists(brand.logo_path):
        logo = Image(brand.logo_path, width=0.9 * inch, height=0.9 * inch)
        logo.hAlign = "CENTER"
        story.append(logo)
        story.append(Spacer(1, 2))
        story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceBefore=2, spaceAfter=8))
    else:
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

    # ---------- VA AGENT CALL SCRIPT ----------
    story.append(PageBreak())
    story += _va_call_script(prop)

    # ---------- FINAL PAGE: DISCLAIMER ----------
    story.append(PageBreak())
    story.append(Paragraph("Disclaimer", H1))
    story.append(HRFlowable(width="100%", thickness=0.8, color=RULE, spaceAfter=10))
    story.append(Paragraph(
        "This package is provided for informational and investment evaluation purposes only. "
        "Property details, repair estimates, values, availability, and financial projections must be "
        "independently verified. Photos remain the property of their respective owners or listing sources.",
        BODY))

    bottom_margin = 0.95 * inch if (brand and (brand.company or brand.line2)) else 0.7 * inch
    doc = SimpleDocTemplate(out_path, pagesize=letter, topMargin=0.75 * inch,
                            bottomMargin=bottom_margin, leftMargin=0.85 * inch, rightMargin=0.85 * inch,
                            title=f"{addr} - Deal Package",
                            author=(brand.company if brand and brand.company else "Deal Package Builder"))
    hf = _header_footer(addr, brand)
    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    log.info("PDF written: %s", out_path)
    return out_path

"""Paragon Government Solutions LLC branding for offer documents:
logo header (top of first page) + company footer (every page).
Address confirmed by Charles: 11166 Fairfax Blvd, Suite 500, Fairfax, VA 22030.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Image, Spacer, HRFlowable

_HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(_HERE, "..", "assets", "paragon_logo.png")
NAVY = colors.HexColor("#2E4057")
GREY = colors.HexColor("#555555")


def brand_header(logo_in=0.95):
    """Flowables for the branded header: centered logo + navy rule."""
    items = []
    if os.path.exists(LOGO):
        img = Image(LOGO, width=logo_in * inch, height=logo_in * inch)
        img.hAlign = "CENTER"
        items.append(img)
        items.append(Spacer(1, 4))
    items.append(HRFlowable(width="100%", thickness=1, color=NAVY,
                            spaceBefore=2, spaceAfter=10))
    return items


def brand_footer(canvas, doc):
    """Drawn on every page via SimpleDocTemplate onFirstPage/onLaterPages."""
    canvas.saveState()
    w, _ = letter
    base = 0.42 * inch
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.6)
    canvas.line(0.85 * inch, base + 30, w - 0.85 * inch, base + 30)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(NAVY)
    canvas.drawCentredString(w / 2, base + 20, "Paragon Government Solutions LLC")
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(w / 2, base + 10,
                             "11166 Fairfax Blvd, Suite 500, Fairfax, VA 22030  |  Phone: (888) 495-6935  |  Email: charlesp@paragongovsolutions.net")
    canvas.drawCentredString(w / 2, base,
                             "UEI: FSCZBK8CBV82  |  CAGE Code: 9WX69  |  www.paragongovsolutions.net")
    canvas.restoreState()

"""Data models for the wholesale deal-package builder."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


# Columns we accept from the input CSV / Excel (any subset may be present).
KNOWN_COLUMNS = [
    "property_address", "city", "state", "zipcode", "listing_url",
    "asking_price", "offer_price", "arv", "repair_estimate", "assignment_fee",
    "beds", "baths", "sqft", "year_built", "lot_size", "property_type", "notes",
]

_MONEY_RE = re.compile(r"[^\d.\-]")


def parse_money(value) -> Optional[float]:
    """Parse '$1,234', '1234.5', 1234 -> float. Blank/None -> None."""
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.lower() in {"nan", "none", "n/a", "na", "not provided"}:
        return None
    s = _MONEY_RE.sub("", s)
    if not s or s in {"-", "."}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def fmt_money(value: Optional[float]) -> str:
    """Format a float as '$1,234' or 'Not provided' when missing."""
    if value is None:
        return "Not provided"
    return f"${value:,.0f}"


def fmt_plain(value) -> str:
    """Display a raw string field or 'Not provided' when empty."""
    if value is None:
        return "Not provided"
    s = str(value).strip()
    return s if s and s.lower() not in {"nan", "none"} else "Not provided"


def sanitize_filename(text: str, max_len: int = 80) -> str:
    """Make a string safe for use as a file or folder name."""
    text = (text or "").strip()
    text = re.sub(r"[^\w\s.-]", "", text)
    text = re.sub(r"\s+", "_", text)
    text = text.strip("._-")
    return (text or "property")[:max_len]


@dataclass
class Property:
    property_address: str = ""
    city: str = ""
    state: str = ""
    zipcode: str = ""
    listing_url: str = ""
    asking_price: Optional[float] = None
    offer_price: Optional[float] = None
    arv: Optional[float] = None
    repair_estimate: Optional[float] = None
    assignment_fee: Optional[float] = None
    beds: str = ""
    baths: str = ""
    sqft: str = ""
    year_built: str = ""
    lot_size: str = ""
    property_type: str = ""
    notes: str = ""

    # Populated during processing.
    listing_status: str = ""
    source: str = ""  # 'zillow' | 'redfin' | 'unknown'

    @classmethod
    def from_row(cls, row: dict) -> "Property":
        g = lambda k: (str(row[k]).strip() if row.get(k) not in (None, "") else "")
        return cls(
            property_address=g("property_address"),
            city=g("city"),
            state=g("state"),
            zipcode=g("zipcode"),
            listing_url=g("listing_url"),
            asking_price=parse_money(row.get("asking_price")),
            offer_price=parse_money(row.get("offer_price")),
            arv=parse_money(row.get("arv")),
            repair_estimate=parse_money(row.get("repair_estimate")),
            assignment_fee=parse_money(row.get("assignment_fee")),
            beds=g("beds"),
            baths=g("baths"),
            sqft=g("sqft"),
            year_built=g("year_built"),
            lot_size=g("lot_size"),
            property_type=g("property_type"),
            notes=g("notes"),
        )

    # ---- derived display helpers ----

    @property
    def full_location(self) -> str:
        loc = ", ".join(p for p in [self.city, self.state] if p)
        if self.zipcode:
            loc = f"{loc} {self.zipcode}".strip()
        return loc

    @property
    def title(self) -> str:
        return self.property_address or self.listing_url or "Property"

    def package_basename(self) -> str:
        parts = [self.property_address, self.city, self.state]
        stem = "_".join(sanitize_filename(p) for p in parts if p) or "Property"
        return f"{stem}_Deal_Package.pdf"

    def photo_folder_name(self) -> str:
        return sanitize_filename(self.property_address or self.title)

    # ---- deal math ----

    @property
    def mao(self) -> Optional[float]:
        """MAO = (ARV * 0.70) - Repairs - Assignment Fee. Needs all three."""
        if self.arv is None or self.repair_estimate is None or self.assignment_fee is None:
            return None
        return round(self.arv * 0.70 - self.repair_estimate - self.assignment_fee, 2)

    @property
    def investor_purchase_price(self) -> Optional[float]:
        """What the end investor/builder pays = my offer + assignment fee."""
        if self.offer_price is None or self.assignment_fee is None:
            return None
        return round(self.offer_price + self.assignment_fee, 2)

    @property
    def investor_spread(self) -> Optional[float]:
        """Investor equity spread = ARV - repairs - investor purchase price."""
        ipp = self.investor_purchase_price
        if self.arv is None or self.repair_estimate is None or ipp is None:
            return None
        return round(self.arv - self.repair_estimate - ipp, 2)

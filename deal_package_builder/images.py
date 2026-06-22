"""Download, validate, de-duplicate, classify, and save listing photos."""
from __future__ import annotations

import io
import logging
import os
import re
from dataclasses import dataclass
from typing import List, Optional

from PIL import Image

log = logging.getLogger("deal_packages.images")

# Room-type keyword heuristics (matched against URL, alt text, or caption when
# available). Ordered by the priority requested in the spec.
ROOM_PRIORITY = [
    ("front_exterior", ("front", "exterior", "elevation", "curb", "facade", "street")),
    ("rear_exterior", ("rear", "back", "backyard", "back-exterior")),
    ("kitchen", ("kitchen",)),
    ("living_room", ("living", "family-room", "great-room", "den")),
    ("bedroom", ("bed", "bedroom", "primary", "master")),
    ("bathroom", ("bath", "bathroom", "shower", "vanity")),
    ("basement", ("basement", "cellar", "lower-level")),
    ("repair_area", ("repair", "damage", "unfinished", "construction", "gut", "stud")),
    ("yard", ("yard", "lot", "garden", "deck", "patio", "fence")),
]
DEFAULT_LABEL = "property_photo"

_DEF_TIMEOUT = 25


@dataclass
class Photo:
    url: str
    path: str
    label: str
    width: int
    height: int
    ahash: int


# -----------------------------------------------------------------------------
# Download
# -----------------------------------------------------------------------------
def _download_bytes(url: str, referer: str = "") -> Optional[bytes]:
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
        "Accept": "image/avif,image/webp,image/*,*/*;q=0.8",
    }
    if referer:
        headers["Referer"] = referer
    # Prefer httpx; fall back to urllib so the tool runs without httpx installed.
    try:
        import httpx
        with httpx.Client(timeout=_DEF_TIMEOUT, follow_redirects=True, headers=headers) as c:
            r = c.get(url)
            if r.status_code == 200 and r.content:
                return r.content
            log.debug("download %s -> HTTP %s", url, r.status_code)
            return None
    except ImportError:
        pass
    except Exception as exc:  # noqa: BLE001
        log.debug("httpx download failed for %s: %s", url, exc)
        return None
    try:
        import urllib.request
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=_DEF_TIMEOUT) as resp:  # nosec - public images
            return resp.read()
    except Exception as exc:  # noqa: BLE001
        log.debug("urllib download failed for %s: %s", url, exc)
        return None


# -----------------------------------------------------------------------------
# Validation + hashing
# -----------------------------------------------------------------------------
def _average_hash(img: Image.Image, size: int = 8) -> int:
    """Perceptual average-hash (no external deps) for near-duplicate detection."""
    small = img.convert("L").resize((size, size), Image.LANCZOS)
    pixels = list(small.getdata())
    avg = sum(pixels) / len(pixels)
    bits = 0
    for i, px in enumerate(pixels):
        if px >= avg:
            bits |= (1 << i)
    return bits


def _hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def classify(url: str, alt: str = "") -> str:
    hay = f"{url} {alt}".lower()
    for label, keys in ROOM_PRIORITY:
        if any(k in hay for k in keys):
            return label
    return DEFAULT_LABEL


# -----------------------------------------------------------------------------
# Main pipeline
# -----------------------------------------------------------------------------
def collect_photos(urls: List[str], out_dir: str, referer: str = "",
                   max_photos: int = 15, min_width: int = 600,
                   hamming_threshold: int = 6) -> List[Photo]:
    """Download/validate/dedup/classify and save up to `max_photos` images.

    Returns the saved Photo records (already renamed with priority ordering).
    """
    os.makedirs(out_dir, exist_ok=True)
    kept: List[Photo] = []
    hashes: List[int] = []

    for url in urls:
        if len(kept) >= max_photos:
            break
        raw = _download_bytes(url, referer=referer)
        if not raw:
            continue
        try:
            img = Image.open(io.BytesIO(raw))
            img.load()
        except Exception:
            continue
        if img.width < min_width:  # skip thumbnails / icons
            continue
        if img.mode in ("P", "RGBA", "LA"):
            img = img.convert("RGB")

        ah = _average_hash(img)
        if any(_hamming(ah, h) <= hamming_threshold for h in hashes):
            continue  # near-duplicate of one we already kept

        label = classify(url)
        kept.append(Photo(url=url, path="", label=label, width=img.width,
                          height=img.height, ahash=ah))
        kept[-1]._img = img  # type: ignore[attr-defined]
        hashes.append(ah)

    # Order by spec priority, then save with sequential, descriptive filenames.
    priority_index = {label: i for i, (label, _) in enumerate(ROOM_PRIORITY)}
    kept.sort(key=lambda p: priority_index.get(p.label, len(ROOM_PRIORITY)))

    seen_label_counts: dict = {}
    final: List[Photo] = []
    for i, ph in enumerate(kept, start=1):
        label = ph.label
        seen_label_counts[label] = seen_label_counts.get(label, 0) + 1
        suffix = "" if seen_label_counts[label] == 1 else f"_{seen_label_counts[label]}"
        fname = f"{i:02d}_{label}{suffix}.jpg"
        path = os.path.join(out_dir, fname)
        try:
            img = ph._img  # type: ignore[attr-defined]
            # Compress to keep PDF size reasonable while staying crisp.
            img.save(path, "JPEG", quality=82, optimize=True, progressive=True)
        except Exception as exc:  # noqa: BLE001
            log.debug("save failed for %s: %s", path, exc)
            continue
        ph.path = path
        final.append(ph)
        del ph._img  # type: ignore[attr-defined]

    log.info("Saved %d photos to %s", len(final), out_dir)
    return final


def caption_for(label: str) -> str:
    pretty = {
        "front_exterior": "Front exterior",
        "rear_exterior": "Rear exterior",
        "kitchen": "Kitchen",
        "living_room": "Living room",
        "bedroom": "Bedroom",
        "bathroom": "Bathroom",
        "basement": "Basement",
        "repair_area": "Repair area",
        "yard": "Yard / lot",
        "property_photo": "Property photo",
    }
    return pretty.get(re.sub(r"_\d+$", "", label), "Property photo")

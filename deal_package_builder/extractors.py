"""Listing-photo extraction for Zillow and Redfin.

Strategy (no single brittle selector):
  1. Render the page with Playwright + Chromium (real browser, JS executed).
  2. Pull the full HTML and run several independent extraction passes:
       - source-specific JSON/state parsing (Zillow, Redfin)
       - <img> src/srcset and <source> srcset
       - JSON-LD (schema.org) `image` arrays
       - Open Graph `og:image` (fallback)
  3. Union + de-duplicate the candidate URLs, upgrade each to the highest
     resolution the public page exposes, and return them in page order.

This tool only reads images that the public listing page already serves. It does
NOT log in, solve CAPTCHAs, or defeat bot protection. If the page blocks an
anonymous browser, extraction simply returns nothing and the caller proceeds
without photos.
"""
from __future__ import annotations

import json
import logging
import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse

log = logging.getLogger("deal_packages.extract")

# ---- resolution / filtering knobs -------------------------------------------
ZILLOW_HOST = "photos.zillowstatic.com"
REDFIN_HOST = "ssl.cdn-redfin.com"
# Patterns we never want as "property photos".
_EXCLUDE_RE = re.compile(
    r"(logo|sprite|icon|map|static-map|streetview|googleapis|agent|headshot|"
    r"avatar|badge|placeholder|floorplan|floor-plan|/photos/genFloorplan|"
    r"premier|brand|watermark)",
    re.I,
)
_IMG_EXT_RE = re.compile(r"\.(jpe?g|png|webp)(\?|$)", re.I)


def detect_source(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if "zillow.com" in host:
        return "zillow"
    if "redfin.com" in host:
        return "redfin"
    return "unknown"


# -----------------------------------------------------------------------------
# Page rendering
# -----------------------------------------------------------------------------
def render_page(url: str, headless: bool = True, timeout_ms: int = 45000
                ) -> Optional[Tuple[str, list]]:
    """Return (html, network_image_urls) for a listing URL, or None on failure.

    Playwright is imported lazily so the rest of the tool (PDF generation, CSV
    parsing) works even when Playwright/Chromium are not installed.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.error("Playwright not installed - run `pip install -r requirements.txt` "
                  "and `playwright install chromium`. Skipping photo extraction.")
        return None

    ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    network_imgs: list = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            ctx = browser.new_context(user_agent=ua, viewport={"width": 1440, "height": 2200},
                                      locale="en-US")
            page = ctx.new_page()

            # Passively record image responses the page itself requests.
            def _on_response(resp):
                try:
                    u = resp.url
                    if _IMG_EXT_RE.search(u) and (ZILLOW_HOST in u or REDFIN_HOST in u):
                        network_imgs.append(u)
                except Exception:
                    pass
            page.on("response", _on_response)

            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            # Give the gallery a chance to hydrate; best-effort, never fatal.
            for sel in ("img[src*='zillowstatic']", "img[src*='cdn-redfin']",
                        "[data-testid='hollywood-gallery'] img", "script[type='application/ld+json']"):
                try:
                    page.wait_for_selector(sel, timeout=4000)
                    break
                except Exception:
                    continue
            try:
                page.mouse.wheel(0, 6000)
                page.wait_for_timeout(1500)
            except Exception:
                pass
            html = page.content()
            ctx.close()
            browser.close()
            return html, network_imgs
    except Exception as exc:  # noqa: BLE001 - any nav/bot-block failure is non-fatal
        log.warning("Playwright render failed for %s: %s", url, exc)
        return None


# -----------------------------------------------------------------------------
# URL helpers
# -----------------------------------------------------------------------------
def _looks_like_property_photo(u: str) -> bool:
    if not u or not u.startswith("http"):
        return False
    if not _IMG_EXT_RE.search(u):
        return False
    if _EXCLUDE_RE.search(u):
        return False
    return True


def _upgrade_zillow(u: str) -> str:
    """Zillow encodes size in the filename, e.g. '-cc_ft_384.jpg' or '-p_e.jpg'.
    Swap to the largest commonly-served size ('-uncropped_scaled_within_1536_1152'
    is not guessable, so prefer the explicit big variants)."""
    u = re.sub(r"-cc_ft_\d+\.", "-cc_ft_1536.", u)
    u = re.sub(r"-p_[a-z]\.", "-p_f.", u)              # p_f is a large preset
    u = re.sub(r"_\d+\.(jpe?g|webp|png)$", r"_1536.\1", u)
    return u


def _upgrade_redfin(u: str) -> str:
    """Redfin serves sizes via tokens like 'genMid', 'genLgFile', 'bigphoto',
    '/640/' etc. Prefer the large variants."""
    u = re.sub(r"/genMid\.", "/genLgFile.", u)
    u = re.sub(r"/p_\d+/", "/p_0/", u)
    u = re.sub(r"/(\d{2,4})x(\d{2,4})/", "/1280x960/", u)
    return u


def _upgrade(u: str, source: str) -> str:
    if ZILLOW_HOST in u:
        return _upgrade_zillow(u)
    if REDFIN_HOST in u:
        return _upgrade_redfin(u)
    return u


def _normalize_for_dedup(u: str) -> str:
    """Strip size tokens / query strings so the same photo at different sizes
    collapses to one key."""
    base = u.split("?")[0]
    base = re.sub(r"-cc_ft_\d+", "", base)
    base = re.sub(r"-p_[a-z]", "", base)
    base = re.sub(r"_\d+(\.(jpe?g|webp|png))$", r"\1", base)
    base = re.sub(r"/gen\w+\.", "/.", base)
    base = re.sub(r"/\d{2,4}x\d{2,4}/", "/", base)
    base = re.sub(r"/p_\d+/", "/", base)
    return base.lower()


# -----------------------------------------------------------------------------
# Extraction passes
# -----------------------------------------------------------------------------
def _iter_json_strings(html: str):
    """Yield large JSON blobs embedded in the page (Next.js, Apollo, Redux)."""
    for m in re.finditer(
        r'<script[^>]*(?:id="__NEXT_DATA__"|application/json|window\.__[A-Z_]+__\s*=)'
        r'[^>]*>(.*?)</script>', html, re.S):
        yield m.group(1)
    # Inline assignments: window.__INITIAL_STATE__ = {...};
    for m in re.finditer(r'window\.\__[A-Za-z0-9_]+__\s*=\s*(\{.*?\})\s*;', html, re.S):
        yield m.group(1)


def _urls_from_blob(blob: str, host: str) -> List[str]:
    """Regex every host-matching image URL out of a JSON/HTML blob."""
    pat = re.compile(r'https?:\\?/\\?/' + re.escape(host) + r'[^"\\\s]+?\.(?:jpe?g|webp|png)', re.I)
    out = []
    for m in pat.finditer(blob):
        out.append(m.group(0).replace("\\/", "/").replace("\\u002F", "/"))
    return out


def extract_zillow(html: str) -> List[str]:
    urls = _urls_from_blob(html, ZILLOW_HOST)
    # srcset/src attributes
    urls += re.findall(r'(https://' + re.escape(ZILLOW_HOST) + r'[^\s"\']+?\.(?:jpe?g|webp|png))', html)
    return urls


def extract_redfin(html: str) -> List[str]:
    urls = _urls_from_blob(html, REDFIN_HOST)
    urls += re.findall(r'(https://' + re.escape(REDFIN_HOST) + r'[^\s"\']+?\.(?:jpe?g|webp|png))', html)
    return urls


def extract_jsonld_images(html: str) -> List[str]:
    out: List[str] = []
    for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
        try:
            data = json.loads(m.group(1).strip())
        except Exception:
            continue
        for node in (data if isinstance(data, list) else [data]):
            img = node.get("image") if isinstance(node, dict) else None
            if isinstance(img, str):
                out.append(img)
            elif isinstance(img, list):
                out.extend([i for i in img if isinstance(i, str)])
            elif isinstance(img, dict) and isinstance(img.get("url"), str):
                out.append(img["url"])
    return out


def extract_opengraph(html: str) -> List[str]:
    return re.findall(r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)["\']',
                      html, re.I)


def extract_generic_imgs(html: str) -> List[str]:
    """Any <img>/<source> referencing a known photo CDN."""
    out: List[str] = []
    for attr in ("src", "data-src", "srcset", "data-srcset"):
        for m in re.finditer(attr + r'=["\']([^"\']+)["\']', html):
            for part in m.group(1).split(","):
                u = part.strip().split(" ")[0]
                if ZILLOW_HOST in u or REDFIN_HOST in u:
                    out.append(u)
    return out


# -----------------------------------------------------------------------------
# Public entrypoint
# -----------------------------------------------------------------------------
def extract_photo_urls(url: str, headless: bool = True, max_photos: int = 15
                       ) -> Tuple[List[str], str]:
    """Render `url` and return (deduped ordered photo URLs, source)."""
    source = detect_source(url)
    rendered = render_page(url, headless=headless)
    if not rendered:
        return [], source
    html, network_imgs = rendered

    candidates: List[str] = []
    if source == "zillow":
        candidates += extract_zillow(html)
    elif source == "redfin":
        candidates += extract_redfin(html)
    else:
        candidates += extract_zillow(html) + extract_redfin(html)
    # Generic / fallback passes always run and add coverage.
    candidates += extract_generic_imgs(html)
    candidates += extract_jsonld_images(html)
    candidates += extract_opengraph(html)
    candidates += network_imgs

    # Filter, upgrade, dedup (preserve first-seen order).
    seen, ordered = set(), []
    for u in candidates:
        u = u.replace("&amp;", "&").strip()
        if not _looks_like_property_photo(u):
            continue
        up = _upgrade(u, source)
        key = _normalize_for_dedup(up)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(up)

    log.info("%s: %d raw candidates -> %d unique photo URLs", source, len(candidates), len(ordered))
    return ordered[: max_photos * 3], source  # extra headroom; image-hash dedup trims later

"""Helper functions for the WoMgr integration."""

from __future__ import annotations

import hashlib
import re


_MAC_RE = re.compile(r"^[0-9A-Fa-f]{2}([:-]?[0-9A-Fa-f]{2}){5}$")


def parse_mac_address(mac: str) -> bytes:
    """Convert a MAC address string to bytes."""

    cleaned = mac.strip()
    if not _MAC_RE.fullmatch(cleaned):
        raise ValueError("Invalid MAC address")

    cleaned = cleaned.replace(":", "").replace("-", "")

    try:
        return bytes.fromhex(cleaned)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError("Invalid MAC address") from exc


def pastel_color(seed: str) -> str:
    """Generate a deterministic pastel RGB color from a seed."""

    h = hashlib.md5(seed.encode()).hexdigest()
    r = (int(h[0:2], 16) + 255) // 2
    g = (int(h[2:4], 16) + 255) // 2
    b = (int(h[4:6], 16) + 255) // 2
    return f"rgb({r}, {g}, {b})"


__all__ = ["parse_mac_address", "pastel_color"]

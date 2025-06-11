from __future__ import annotations

import re


_MAC_RE = re.compile(r"^[0-9A-Fa-f]{2}([:-]?[0-9A-Fa-f]{2}){5}$")


def parse_mac_address(mac: str) -> bytes:
    """Convert a MAC address string to bytes.

    Separators ``:`` or ``-`` are allowed. Whitespace surrounding the
    address is ignored. The resulting string must contain exactly 12
    hexadecimal characters. ``ValueError`` is raised if validation fails.
    """

    cleaned = mac.strip()
    if not _MAC_RE.fullmatch(cleaned):
        raise ValueError("Invalid MAC address")

    cleaned = cleaned.replace(":", "").replace("-", "")

    try:
        return bytes.fromhex(cleaned)
    except ValueError as exc:
        raise ValueError("Invalid MAC address") from exc

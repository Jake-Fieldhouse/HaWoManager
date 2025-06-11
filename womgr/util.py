from __future__ import annotations


def parse_mac_address(mac: str) -> bytes:
    """Convert a MAC address string to bytes.

    Separators ``:`` or ``-`` are allowed. Whitespace is ignored. The
    resulting string must contain exactly 12 hexadecimal characters.
    ``ValueError`` is raised if validation fails.
    """
    cleaned = mac.replace(':', '').replace('-', '').strip()
    if len(cleaned) != 12:
        raise ValueError("Invalid MAC address")
    try:
        return bytes.fromhex(cleaned)
    except ValueError as exc:
        raise ValueError("Invalid MAC address") from exc

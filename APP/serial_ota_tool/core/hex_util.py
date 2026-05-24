"""十六进制收发工具。"""

from __future__ import annotations


def hex_str_to_bytes(hex_str: str) -> bytes:
    clean = hex_str.replace(" ", "").replace("\n", "").upper().strip()
    if not clean or len(clean) % 2 != 0:
        return b""
    return bytes(int(clean[i : i + 2], 16) for i in range(0, len(clean), 2))


def bytes_to_hex(data: bytes) -> str:
    return data.hex(" ").upper()

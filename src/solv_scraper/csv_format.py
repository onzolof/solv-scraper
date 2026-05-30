"""Detect which o-l.ch result CSV layout a file uses."""

from __future__ import annotations

import re
from typing import Literal

CsvFormat = Literal["standard", "team", "relay_block", "relay_compact", "unknown"]

RELAY_BLOCK_RE = re.compile(r"^[A-Z0-9]+;;.*<b>", re.IGNORECASE)
RELAY_COMPACT_SEMI_RE = re.compile(r"^[A-Za-z0-9*]+;;\s")
RELAY_COMPACT_META_RE = re.compile(r"^[A-Za-z0-9*]+;[\d.]+;")


def detect_csv_format(content: str) -> CsvFormat:
    first_line = content.splitlines()[0] if content else ""
    if not first_line:
        return "unknown"
    if first_line.startswith("Kategorie;Laenge;"):
        if "Name2" in first_line:
            return "team"
        return "standard"
    if RELAY_BLOCK_RE.match(first_line):
        return "relay_block"
    if RELAY_COMPACT_META_RE.match(first_line) or RELAY_COMPACT_SEMI_RE.match(first_line):
        return "relay_compact"
    return "unknown"

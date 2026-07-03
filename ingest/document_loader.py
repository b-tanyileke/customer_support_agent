"""
Helpers for reading and cleaning raw support documents before chunking.
"""

from pathlib import Path
import re


MOJIBAKE_REPLACEMENTS = {
    "â€™": "'",
    "â€˜": "'",
    "â€œ": '"',
    "â€\u009d": '"',
    "â€": '"',
    "â€“": "-",
    "â€”": "-",
    "â€¦": "...",
    "Â": "",
}


def read_text_file(path: Path) -> str:
    """
    Read a text file and return its content as a string, 
    trying multiple encodings to handle different file formats.
    """
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw.decode("utf-8", errors="replace")


def clean_text(text: str) -> str:
    """
    Clean text by replacing mojibake characters, normalizing whitespace, and removing extra newlines.
    """
    for bad, good in MOJIBAKE_REPLACEMENTS.items():
        text = text.replace(bad, good)

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

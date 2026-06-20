"""
============================================================
  utils/helpers.py
  Miscellaneous helper functions.
============================================================
"""

import re
import html


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Clean and truncate user-submitted text.

    - Strips leading/trailing whitespace
    - Removes excessive newlines
    - HTML-escapes to prevent XSS
    - Truncates to max_length characters
    """
    text = text.strip()
    text = re.sub(r"\n{3,}", "\n\n", text)          # collapse triple+ newlines
    text = re.sub(r"[ \t]{2,}", " ", text)           # collapse horizontal whitespace
    text = html.unescape(text)                        # decode HTML entities first
    return text[:max_length]


def format_confidence(confidence: float) -> str:
    """
    Convert confidence float (0.0 – 1.0) to percentage string.
    Example: 0.9731 → "97.31%"
    """
    return f"{confidence * 100:.2f}%"


def label_badge_class(label: str) -> str:
    """Return a CSS class name for a sentiment label badge."""
    mapping = {
        "POSITIVE": "badge-positive",
        "NEGATIVE": "badge-negative",
        "NEUTRAL":  "badge-neutral",
    }
    return mapping.get(label.upper(), "badge-neutral")


def truncate(text: str, length: int = 80) -> str:
    """Truncate text with ellipsis for display in tables."""
    return text if len(text) <= length else text[:length].rstrip() + "…"

def normalize_text(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "ﬀ": "ff",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "ﬅ": "st",
        "ﬆ": "st",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text
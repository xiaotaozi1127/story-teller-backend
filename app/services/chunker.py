import re

# This directly addresses XTTS instability
# Prevents quote-triggered voice resets
BAD_EDGE_CHARS = '\"\'“”‘’():;—–'
MIN_CHUNK_LEN = 80
SENTENCE_END_RE = re.compile(r'(?<=[.!?;:])\s+')
CLAUSE_SPLIT_RE = re.compile(r'\s*,\s*|\s*;\s*|\s*—\s*|\s*–\s*|\s*:\s*')


def clean_chunk(text: str) -> str:
    """Normalize whitespace and trim characters that can destabilize XTTS at edges."""
    text = text.strip()
    text = text.strip(BAD_EDGE_CHARS)
    text = re.sub(r'\s+', ' ', text)
    return text


def _split_long_segment(segment: str, max_len: int) -> list[str]:
    """
    Split a single long sentence/segment into clause-sized pieces, trying
    to respect natural pauses (commas, semicolons, dashes) before falling
    back to hard word-based splits.
    """
    if len(segment) <= max_len:
        return [segment]

    clauses = [c for c in CLAUSE_SPLIT_RE.split(segment) if c]
    if not clauses:
        clauses = [segment]

    parts: list[str] = []
    current = ""

    for clause in clauses:
        if not current:
            current = clause
            continue

        if len(current) + 1 + len(clause) <= max_len:
            current = f"{current} {clause}"
        else:
            parts.append(current)
            current = clause

    if current:
        parts.append(current)

    # If any piece is still too long, do a hard split by words.
    final_parts: list[str] = []
    for p in parts:
        if len(p) <= max_len:
            final_parts.append(p)
            continue

        words = p.split()
        buf = []
        for w in words:
            candidate = " ".join(buf + [w])
            if len(candidate) <= max_len:
                buf.append(w)
            else:
                if buf:
                    final_parts.append(" ".join(buf))
                buf = [w]
        if buf:
            final_parts.append(" ".join(buf))

    return final_parts


def split_text_smart(text: str, max_len: int = 300) -> list[str]:
    """
    Chunk text for XTTS to keep joins natural:
    - Prefer sentence boundaries.
    - Break long sentences on natural pauses (commas/dashes) before hard splits.
    - Avoid very short trailing chunks by merging with the previous one.
    """
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return []

    sentences = [s for s in SENTENCE_END_RE.split(text) if s.strip()]
    segments: list[str] = []

    # First pass: ensure no single segment exceeds max_len
    for sentence in sentences:
        segments.extend(_split_long_segment(sentence, max_len))

    chunks: list[str] = []
    current = ""

    # Build chunks while respecting max_len where possible
    for seg in segments:
        seg = clean_chunk(seg)
        if not seg:
            continue

        if not current:
            current = seg
            continue

        if len(current) + 1 + len(seg) <= max_len:
            current = f"{current} {seg}"
        else:
            chunks.append(clean_chunk(current))
            current = seg

    if current:
        chunks.append(clean_chunk(current))

    # Merge short tail chunks to avoid abrupt tiny clips
    merged: list[str] = []
    for c in chunks:
        if merged and len(c) < MIN_CHUNK_LEN:
            merged[-1] = clean_chunk(f"{merged[-1]} {c}")
        else:
            merged.append(c)

    return merged

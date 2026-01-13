import re
from typing import List


def split_text(text: str, max_len: int = 300) -> List[str]:
    # Chinese + English punctuation
    sentences = re.split(r'(?<=[。！？.!?])', text)
    chunks = []
    current = ""

    for s in sentences:
        if not s.strip():
            continue

        if len(current) + len(s) <= max_len:
            current += s
        else:
            chunks.append(current.strip())
            current = s

    if current.strip():
        chunks.append(current.strip())

    return chunks

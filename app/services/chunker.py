import re

BAD_EDGE_CHARS = '\"\'“”‘’():;—–'

def clean_chunk(text: str) -> str:
    return text.strip().strip(BAD_EDGE_CHARS)

def split_text_smart(text: str, max_len: int = 300) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""

    for s in sentences:
        if len(current) + len(s) <= max_len:
            current += " " + s if current else s
        else:
            chunks.append(clean_chunk(current))
            current = s

    if current:
        chunks.append(clean_chunk(current))

    return chunks

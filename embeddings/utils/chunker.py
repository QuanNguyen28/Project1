from __future__ import annotations

from typing import List

import re

import os

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _clean(s: str) -> str:

    s = s or ""

    s = re.sub(r"[ \t]+", " ", s)

    s = re.sub(r"\n{3,}", "\n\n", s)

    return s.strip()


def split_markdown(
    md: str,
    *,
    max_chars_per_chunk: int = 1200,
    overlap: int = 150,
    min_chars: int = 300,
) -> List[str]:
    """
    Chunk Markdown by headings/paragraphs and hard-split oversized blocks.

    ``min_chars`` is retained for API compatibility. Short final chunks are
    kept deliberately so source content is never silently discarded.
    """

    del min_chars

    return chunk_text(md, max_chars=max_chars_per_chunk, overlap=overlap)


import re

from typing import List

_SENT_SPLIT_RE = re.compile(r"(?<=[\.\?\!。!?])\s+(?=[^\s])")


def _split_into_units(text: str) -> List[str]:
    """
    Tách văn bản thành các "đơn vị" nhỏ trước khi gom chunk:
    - Ưu tiên tách theo heading markdown (#, ##, ...)
    - Sau đó tách theo đoạn (blank line)
    - Nếu block vẫn dài, tách tiếp theo câu
    """

    lines = text.splitlines()

    blocks: List[str] = []

    buf: List[str] = []

    for ln in lines:

        if re.match(r"^\s*#{1,6}\s", ln):

            if buf:

                blocks.append("\n".join(buf).strip())

                buf = []

            blocks.append(ln.strip())

            continue

        if ln.strip() == "":

            if buf:

                blocks.append("\n".join(buf).strip())

                buf = []

            continue

        buf.append(ln)

    if buf:

        blocks.append("\n".join(buf).strip())

    units: List[str] = []

    for b in blocks:

        if len(b) <= 800:

            if b:

                units.append(b)

        else:

            sents = _SENT_SPLIT_RE.split(b)

            for s in sents:

                s = s.strip()

                if s:

                    units.append(s)

    return units


def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    """
    Chunk văn bản theo kích thước ký tự, có overlap, thân thiện Markdown.

    Args:
        text: Nội dung nguồn (Markdown/Plaintext).
        max_chars: Số ký tự tối đa mỗi chunk (>=200).
        overlap: Số ký tự chồng lặp giữa 2 chunk liên tiếp (0..max_chars//2).

    Returns:
        List[str]: Danh sách chunk text.
    """

    text = (text or "").strip()

    if not text:

        return []

    max_chars = max(200, int(max_chars))

    overlap = max(0, min(int(overlap), max_chars // 2))

    units = _split_into_units(text)

    chunks: List[str] = []

    cur = ""

    for u in units:

        if not cur:

            cur = u

            while len(cur) > max_chars:

                head = cur[:max_chars]

                chunks.append(head)

                tail = head[-overlap:] if overlap > 0 else ""

                tail = tail[tail.find(" ") + 1 :] if (" " in tail) else tail

                cur = tail + cur[max_chars:]

            continue

        prospective_len = len(cur) + 1 + len(u)

        if prospective_len <= max_chars:

            cur = f"{cur}\n{u}"

        else:

            chunks.append(cur)

            if overlap > 0 and len(cur) > overlap:

                tail = cur[-overlap:]

                tail = tail[tail.find(" ") + 1 :] if (" " in tail) else tail

                cur = f"{tail}\n{u}"

            else:

                cur = u

            while len(cur) > max_chars:

                head = cur[:max_chars]

                chunks.append(head)

                tail = head[-overlap:] if overlap > 0 else ""

                tail = tail[tail.find(" ") + 1 :] if (" " in tail) else tail

                cur = tail + cur[max_chars:]

    if cur:

        chunks.append(cur)

    return [c.strip() for c in chunks if c.strip()]

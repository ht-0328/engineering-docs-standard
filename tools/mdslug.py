#!/usr/bin/env python3
"""見出しからアンカー（リンクの `#` 以降）を作る規則。

**この規則はこのファイルだけに置く。**
サイト生成（build_site.py）とリンク検査（doc_lint.py）が別々に同じ規則を
持つと、片方だけを直したときに検出漏れか誤検出が起きる。
"""

from __future__ import annotations

import re
import unicodedata

# 取り除く記号。NFKC 正規化のあとに適用するため、全角のかっこも ASCII になっている。
_DROP = re.compile(r"[`*_\[\]()<>#!.,:;?'\"]")
# 区切りとして扱い、ハイフンに置き換える文字。
_SEPARATOR = re.compile(r"[\s、。・：；／/]+")


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = _DROP.sub("", text)
    text = _SEPARATOR.sub("-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "section"


def collect_anchors(lines: list[str]) -> set[str]:
    """Markdown の行から、見出しが作るアンカーの集合を返す。

    コードブロックの中は見出しとして扱わない。
    """
    anchors: set[str] = set()
    in_fence = False
    for raw in lines:
        if re.match(r"^\s*(`{3,}|~{3,})", raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = re.match(r"^#{1,6}\s+(.*)$", raw)
        if heading:
            anchors.add(slugify(heading.group(1)))
    return anchors

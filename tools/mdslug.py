#!/usr/bin/env python3
"""見出しからアンカー（リンクの `#` 以降）を作る規則。

**この規則はこのファイルだけに置く。**
サイト生成（build_site.py）とリンク検査（doc_lint.py）が別々に同じ規則を
持つと、片方だけを直したときに検出漏れか誤検出が起きる。
"""

from __future__ import annotations

import re
import unicodedata
from typing import Callable

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


def slugify_for_toc(value: str, separator: str) -> str:
    """Python-Markdown の toc 拡張が呼ぶ形に合わせた入口。

    toc 拡張は `slugify(値, 区切り文字)` の形で呼ぶ。区切り文字は上の規則で
    決めているため、受け取るが使わない。

    モジュールの直下に置いている。Zensical が設定を pickle で保存するため、
    関数の中で作った関数を渡すと「pickle できない」で止まる。
    """
    return slugify(value)


def toc_slugify() -> Callable[[str, str], str]:
    """toc 拡張に渡す関数を返す。

    Zensical 版のサイト生成（tools/build_site_zensical.py）が使う。
    Zensical は設定に書いた名前を「関数を作る関数」として呼ぶため、
    `slugify_for_toc` をそのまま渡せない。ここで包んで返す。

    ここを経由させると、Zensical 版のアンカーも doc_lint.py と同じ規則になる。
    既定のままだと日本語の見出しが `_2` `_3` のような通し番号になり、
    本文中の `#日本語の見出し` へのリンクがすべて切れる。
    """
    return slugify_for_toc

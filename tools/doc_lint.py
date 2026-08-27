#!/usr/bin/env python3
"""日本語の技術文書を機械的に検査する。

    docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-tools python tools/doc_lint.py

検査するルールは `.doclint.yml` に書いてある。このスクリプトは、そこに書かれた
ことを実行するだけである。ルールを変えるときは設定ファイルを直す。

**このチェッカーを通ったことは、文書の品質の証明ではない。**
機械で判定できるのは、読者適合・結論の妥当性・事実の正しさを除いた、表面的な
部分だけである。詳しくは docs/01-what-is-good.md を参照。
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from mdslug import collect_anchors

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / ".doclint.yml"

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}

# 文末から文体を判定する。どちらにも当たらない文（体言止め、記号で終わる断片）は
# 判定しない。無理に常体へ寄せると誤検出が増える。
POLITE_ENDING = re.compile(
    r"(です|ます|ません|でした|ましょう|ください|でしょう|ですが|ますが|ましたが)$"
)
PLAIN_ENDING = re.compile(
    r"(である|であった|ではない|だ|する|される|した|しない|ある|ない|なる|なった"
    r"|れる|られる|せる|できる|できた|得る|よい|べきである|べきだ)$"
)


@dataclass
class Finding:
    path: Path
    line: int
    rule: str
    doc_rule: str
    severity: str
    message: str
    excerpt: str = ""

    def format(self, root: Path) -> str:
        try:
            rel = self.path.relative_to(root)
        except ValueError:
            rel = self.path
        head = f"{rel}:{self.line}: [{self.severity}] {self.rule}"
        if self.doc_rule:
            head += f" ({self.doc_rule})"
        body = f"  {self.message}"
        if self.excerpt:
            body += f"\n  > {self.excerpt}"
        return f"{head}\n{body}"


@dataclass
class Block:
    """Markdown を行単位で分類した結果。"""

    kind: str  # heading | paragraph | list | table | quote | fence | blank
    line: int  # 1始まりの開始行
    lines: list[str] = field(default_factory=list)
    level: int = 0  # heading のみ
    info: str = ""  # fence のみ（言語名）


# --------------------------------------------------------------------- 文の分割

_CLOSING = "」』）\"'”’"


def split_sentences_pos(text: str) -> list[tuple[int, str]]:
    """日本語の文へ分割し、(開始位置, 文) を返す。

    閉じかっこが句点に続く場合は、かっこの外まで含めて1文とする。
    """
    out: list[tuple[int, str]] = []
    start = 0
    for index, char in enumerate(text):
        if char not in "。！？":
            continue
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if nxt in _CLOSING:
            continue
        raw = text[start : index + 1]
        stripped = raw.strip()
        if stripped:
            out.append((start + (len(raw) - len(raw.lstrip())), stripped))
        start = index + 1
    tail = text[start:]
    if tail.strip():
        out.append((start + (len(tail) - len(tail.lstrip())), tail.strip()))
    return out


def split_sentences(text: str) -> list[str]:
    return [sentence for _, sentence in split_sentences_pos(text)]


# ------------------------------------------------------------------ Markdown解析


def parse_blocks(lines: list[str]) -> list[Block]:
    blocks: list[Block] = []
    in_fence = False
    fence_marker = ""
    current: Block | None = None

    def flush() -> None:
        nonlocal current
        if current is not None:
            blocks.append(current)
            current = None

    for number, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        fence_match = re.match(r"^(\s*)(`{3,}|~{3,})(.*)$", line)

        if in_fence:
            current.lines.append(line)  # type: ignore[union-attr]
            if (
                fence_match
                and fence_match.group(2)[0] == fence_marker[0]
                and len(fence_match.group(2)) >= len(fence_marker)
            ):
                in_fence = False
                flush()
            continue

        if fence_match:
            flush()
            in_fence = True
            fence_marker = fence_match.group(2)
            current = Block(
                kind="fence", line=number, lines=[line], info=fence_match.group(3).strip()
            )
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush()
            blocks.append(
                Block(
                    kind="heading",
                    line=number,
                    lines=[heading.group(2).strip()],
                    level=len(heading.group(1)),
                )
            )
            continue

        if not line.strip():
            flush()
            blocks.append(Block(kind="blank", line=number, lines=[""]))
            continue

        if re.match(r"^\s*>", line):
            kind = "quote"
        elif re.match(r"^\s*([-*+]|\d+\.)\s+", line):
            kind = "list"
        elif line.lstrip().startswith("|"):
            kind = "table"
        else:
            kind = "paragraph"

        if current is None or current.kind != kind:
            flush()
            current = Block(kind=kind, line=number, lines=[line])
        else:
            current.lines.append(line)

    flush()
    return blocks


def strip_inline(text: str) -> str:
    """行内のコード、リンクURL、画像、HTMLコメントを取り除いた本文を返す。

    行内コードは削除せず記号1文字に置き換える。削除すると、コードだけを並べた
    文が読点の列になり、読点の数の検査が誤検出する。
    """
    text = re.sub(r"<!--.*?-->", "", text)
    text = re.sub(r"`[^`]*`", "▪", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return text


LIST_MARKER = re.compile(r"^\s*([-*+]|\d+\.)\s+")


def logical_units(block: Block) -> list[tuple[str, list[int]]]:
    """ブロックを論理単位へ分け、(本文, 各文字の行番号) を返す。

    Markdown のソフト改行で折り返された一文は、表示上は1文である。行ごとに
    解析すると別々の文として数えられ、文長・読点・文体の検査が漏れる。
    段落は全体で1単位、箇条書きは1項目で1単位とする。
    """
    units: list[tuple[list[str], list[int]]] = []

    for offset, raw in enumerate(block.lines):
        line_no = block.line + offset
        starts_item = bool(LIST_MARKER.match(raw))
        text = LIST_MARKER.sub("", strip_inline(raw))

        if not units or (block.kind == "list" and starts_item):
            units.append(([text], [line_no] * len(text)))
        else:
            units[-1][0].append(text)
            units[-1][1].extend([line_no] * len(text))

    return [("".join(parts), owners) for parts, owners in units]


def split_table_row(raw: str) -> list[str]:
    """表の1行をセルへ分割する。

    エスケープした `\\|` と、行内コード内のパイプは区切りとして扱わない。
    """
    text = raw.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]

    cells: list[str] = []
    buf: list[str] = []
    in_code = False
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text) and text[index + 1] == "|":
            buf.append("|")
            index += 2
            continue
        if char == "`":
            in_code = not in_code
            buf.append(char)
            index += 1
            continue
        if char == "|" and not in_code:
            cells.append("".join(buf))
            buf = []
            index += 1
            continue
        buf.append(char)
        index += 1
    cells.append("".join(buf))
    return cells


# ------------------------------------------------------------------- 抑制の解釈

_PATTERN_CACHE: dict[str, re.Pattern[str]] = {}


def word_pattern(word: str) -> re.Pattern[str]:
    """設定に書かれた語を正規表現として扱う。

    設定側で `未定(?!義)` のように書けば、「未定義」を除外できる。
    正規表現として解釈できない語（`???` など）は、そのままの文字列として扱う。
    """
    if word not in _PATTERN_CACHE:
        try:
            _PATTERN_CACHE[word] = re.compile(word)
        except re.error:
            _PATTERN_CACHE[word] = re.compile(re.escape(word))
    return _PATTERN_CACHE[word]


DISABLE_BLOCK = re.compile(r"<!--\s*doclint-disable(?:\s+([\w,\s-]+))?\s*-->")
ENABLE_BLOCK = re.compile(r"<!--\s*doclint-enable\s*-->")
DISABLE_LINE = re.compile(r"<!--\s*doclint-disable-next-line(?:\s+([\w,\s-]+))?\s*-->")


def parse_suppressions(lines: list[str]) -> dict[int, set[str]]:
    """行番号ごとに、抑制するルール名の集合を返す。

    `*` はすべてのルールを意味する。

    - `<!-- doclint-disable -->` から `<!-- doclint-enable -->` までを抑制する。
    - `<!-- doclint-disable-next-line -->` は次の1行だけを抑制する。
    - ルール名を空白またはカンマ区切りで書くと、そのルールだけを抑制する。

    文書の書き方を説明する文書は、悪い例を原文のまま載せる必要がある。
    この仕組みが無いと、悪い例そのものが違反として報告される。
    抑制した範囲は `--report-suppressions` で一覧できる。
    """

    def names(raw: str | None) -> set[str]:
        if not raw or not raw.strip():
            return {"*"}
        return {token for token in re.split(r"[,\s]+", raw.strip()) if token}

    suppressed: dict[int, set[str]] = {}
    active: set[str] = set()
    in_fence = False

    for number, raw in enumerate(lines, start=1):
        # コードブロックの中と行内コードの中にある指示子は、書き方の説明であって
        # 指示ではない。ここを見落とすと、READMEの使用例が本文全体を抑制する。
        if re.match(r"^\s*(`{3,}|~{3,})", raw):
            in_fence = not in_fence
            if active:
                suppressed.setdefault(number, set()).update(active)
            continue
        if in_fence:
            if active:
                suppressed.setdefault(number, set()).update(active)
            continue

        raw = re.sub(r"`[^`]*`", "", raw)

        if ENABLE_BLOCK.search(raw):
            active = set()
            continue

        block = DISABLE_BLOCK.search(raw)
        if block:
            active = names(block.group(1))
            continue

        nxt = DISABLE_LINE.search(raw)
        if nxt:
            suppressed.setdefault(number + 1, set()).update(names(nxt.group(1)))
            continue

        if active:
            suppressed.setdefault(number, set()).update(active)

    return suppressed


# ----------------------------------------------------------------------- 本体


class Linter:
    def __init__(self, config: dict, root: Path) -> None:
        self.config = config
        self.rules = config.get("rules", {})
        self.root = root
        self.findings: list[Finding] = []
        self.suppressions: dict[int, set[str]] = {}
        self.suppressed_lines: dict[Path, int] = {}

    # ------------------------------------------------------------------ utils

    def rule(self, name: str) -> dict | None:
        spec = self.rules.get(name)
        if not spec or not spec.get("enabled", True):
            return None
        return spec

    def add(
        self,
        spec: dict,
        name: str,
        path: Path,
        line: int,
        severity: str,
        message: str | None = None,
        excerpt: str = "",
    ) -> None:
        blocked = self.suppressions.get(line, set())
        if "*" in blocked or name in blocked:
            return
        self.findings.append(
            Finding(
                path=path,
                line=line,
                rule=name,
                doc_rule=spec.get("doc_rule", ""),
                severity=spec.get("severity", severity),
                message=message or spec.get("message", ""),
                excerpt=excerpt[:120],
            )
        )

    # ------------------------------------------------------------------ checks

    def check_file(self, path: Path) -> None:
        lines = path.read_text(encoding="utf-8").splitlines()
        self.suppressions = parse_suppressions(lines)
        self.suppressed_lines[path] = len(self.suppressions)
        blocks = parse_blocks(lines)

        self.check_headings(path, blocks)
        self.check_sentences(path, blocks)
        self.check_style_mixing(path, blocks)
        self.check_list_style(path, blocks)
        self.check_paragraphs(path, blocks)
        self.check_lists(path, blocks)
        self.check_tables(path, blocks)
        self.check_fences(path, blocks)
        self.check_links(path, lines)
        self.check_images(path, lines)
        self.check_words(path, blocks)
        self.check_metadata(path, lines)

    # -- 見出し ------------------------------------------------------------

    def check_headings(self, path: Path, blocks: list[Block]) -> None:
        headings = [b for b in blocks if b.kind == "heading"]

        skip = self.rule("heading_level_skip")
        depth = self.rule("heading_max_depth")
        period = self.rule("heading_no_period")
        vague = self.rule("vague_heading")
        single = self.rule("single_h1")

        if single:
            tops = [b for b in headings if b.level == 1]
            if len(tops) > 1:
                for block in tops[1:]:
                    self.add(
                        single,
                        "single_h1",
                        path,
                        block.line,
                        "error",
                        f"h1 がこのファイルに {len(tops)} 個ある。1個にする",
                        block.lines[0],
                    )
            elif not tops:
                self.add(single, "single_h1", path, 1, "error", "h1 がこのファイルに無い")

        previous = 0
        for block in headings:
            text = block.lines[0]

            if skip and previous and block.level > previous + 1:
                self.add(
                    skip,
                    "heading_level_skip",
                    path,
                    block.line,
                    "error",
                    f"h{previous} の次に h{block.level} が来ている。1段ずつ下げる",
                    text,
                )
            previous = block.level

            if depth and block.level > depth.get("max_depth", 4):
                self.add(depth, "heading_max_depth", path, block.line, "warning", excerpt=text)

            if period and text.endswith("。"):
                self.add(period, "heading_no_period", path, block.line, "error", excerpt=text)

            if vague:
                for word in vague.get("words", []):
                    if text == word or text.replace(" ", "") == word:
                        self.add(vague, "vague_heading", path, block.line, "warning", excerpt=text)
                        break

        empty = self.rule("empty_section")
        if empty:
            for index, block in enumerate(blocks):
                if block.kind != "heading" or block.level == 1:
                    # h1 は文書のタイトルである。直後に h2 が来るのは正しい形。
                    continue
                for follower in blocks[index + 1 :]:
                    if follower.kind == "blank":
                        continue
                    if follower.kind == "heading":
                        self.add(
                            empty,
                            "empty_section",
                            path,
                            block.line,
                            "warning",
                            excerpt=block.lines[0],
                        )
                    break

    # -- 文 ----------------------------------------------------------------

    def check_sentences(self, path: Path, blocks: list[Block]) -> None:
        length = self.rule("sentence_length")
        commas = self.rule("commas_per_sentence")
        negative = self.rule("double_negative")

        for block in blocks:
            if block.kind not in ("paragraph", "list"):
                continue
            for text, owners in logical_units(block):
                for pos, sentence in split_sentences_pos(text):
                    line = owners[pos] if pos < len(owners) else block.line
                    size = len(sentence)

                    # 文の長さは目安であって違反ではない（docs/01-what-is-good.md）。
                    # したがって、どれだけ長くても error にはしない。
                    if length and size > length.get("warn_over", 50):
                        self.add(
                            length,
                            "sentence_length",
                            path,
                            line,
                            "warning",
                            f"一文が {size} 字ある（目安は50字）。主題が複数入っていないか確認する",
                            sentence,
                        )

                    if commas and sentence.count("、") > commas.get("warn_over", 3):
                        self.add(
                            commas,
                            "commas_per_sentence",
                            path,
                            line,
                            "warning",
                            f"読点が {sentence.count('、')} 個ある",
                            sentence,
                        )

                    if negative:
                        for pattern in negative.get("patterns", []):
                            if re.search(pattern, sentence):
                                self.add(
                                    negative,
                                    "double_negative",
                                    path,
                                    line,
                                    "warning",
                                    excerpt=sentence,
                                )
                                break

    @staticmethod
    def classify_style(sentence: str) -> str | None:
        body = sentence.rstrip("。！？")
        if not body:
            return None
        if POLITE_ENDING.search(body):
            return "敬体"
        if PLAIN_ENDING.search(body):
            return "常体"
        return None  # 体言止め・断片は判定しない

    def check_style_mixing(self, path: Path, blocks: list[Block]) -> None:
        """本文の敬体・常体の混在を検出する（S-13、SRC-EXT-003 1.1.1）。"""
        spec = self.rule("style_mixing")
        if not spec:
            return

        samples: list[tuple[int, str, str]] = []
        for block in blocks:
            if block.kind != "paragraph":
                continue
            for text, owners in logical_units(block):
                for pos, sentence in split_sentences_pos(text):
                    style = self.classify_style(sentence)
                    if style:
                        line = owners[pos] if pos < len(owners) else block.line
                        samples.append((line, style, sentence))

        if len(samples) < spec.get("min_sentences", 10):
            return

        polite = sum(1 for _, style, _ in samples if style == "敬体")
        plain = len(samples) - polite
        if polite == 0 or plain == 0:
            return

        minority = "敬体" if polite < plain else "常体"
        majority = "常体" if minority == "敬体" else "敬体"
        for line, style, sentence in samples:
            if style == minority:
                self.add(
                    spec,
                    "style_mixing",
                    path,
                    line,
                    "warning",
                    f"本文全体は{majority}だが、この文は{minority}になっている",
                    sentence,
                )

    def check_list_style(self, path: Path, blocks: list[Block]) -> None:
        """ひとまとまりの箇条書きの中で文体が混ざっていないかを見る。

        SRC-EXT-003 1.1.3「ひとまとまりの箇条書きでは、敬体と常体を混在させません」。
        """
        spec = self.rule("list_style_mixing")
        if not spec:
            return

        for block in blocks:
            if block.kind != "list":
                continue
            seen: list[tuple[int, str, str]] = []
            for text, owners in logical_units(block):
                sentences = split_sentences_pos(text)
                if not sentences:
                    continue
                pos, last = sentences[-1]
                style = self.classify_style(last)
                if style:
                    seen.append((owners[pos] if pos < len(owners) else block.line, style, last))

            styles = {style for _, style, _ in seen}
            if len(styles) > 1:
                for line, style, sentence in seen:
                    self.add(spec, "list_style_mixing", path, line, "warning", excerpt=sentence)

    def check_paragraphs(self, path: Path, blocks: list[Block]) -> None:
        spec = self.rule("paragraph_sentences")
        if not spec:
            return
        limit = spec.get("warn_over", 7)
        for block in blocks:
            if block.kind != "paragraph":
                continue
            text = "".join(strip_inline(line) for line in block.lines)
            count = len(split_sentences(text))
            if count > limit:
                self.add(
                    spec,
                    "paragraph_sentences",
                    path,
                    block.line,
                    "warning",
                    f"段落に {count} 文ある（目安は3〜5文、上限7文）",
                    block.lines[0],
                )

    def check_lists(self, path: Path, blocks: list[Block]) -> None:
        spec = self.rule("list_items")
        if not spec:
            return
        limit = spec.get("warn_over", 7)
        for block in blocks:
            if block.kind != "list":
                continue
            top_level = [line for line in block.lines if re.match(r"^([-*+]|\d+\.)\s+", line)]
            if len(top_level) > limit:
                self.add(
                    spec,
                    "list_items",
                    path,
                    block.line,
                    "warning",
                    f"箇条書きの項目が {len(top_level)} 個ある（目安は7項目以内）",
                    top_level[0],
                )

    # -- 表 ----------------------------------------------------------------

    def check_tables(self, path: Path, blocks: list[Block]) -> None:
        cell_spec = self.rule("table_cell_length")
        col_spec = self.rule("table_columns")

        for block in blocks:
            if block.kind != "table":
                continue

            expected: int | None = None
            for offset, raw in enumerate(block.lines):
                line = block.line + offset
                cells = split_table_row(raw)
                is_divider = bool(re.match(r"^\s*\|?[\s:|-]+\|?\s*$", raw))

                if col_spec and not is_divider:
                    if expected is None:
                        expected = len(cells)
                    elif len(cells) != expected:
                        self.add(
                            col_spec,
                            "table_columns",
                            path,
                            line,
                            "error",
                            f"列数が {len(cells)} 個で、見出し行の {expected} 個と違う",
                            raw.strip(),
                        )

                if cell_spec and not is_divider:
                    limit = cell_spec.get("warn_over", 2)
                    for cell in cells:
                        text = strip_inline(cell).strip()
                        if len(split_sentences(text)) > limit:
                            self.add(
                                cell_spec, "table_cell_length", path, line, "warning", excerpt=text
                            )

    def check_fences(self, path: Path, blocks: list[Block]) -> None:
        spec = self.rule("code_block_language")
        if not spec:
            return
        for block in blocks:
            if block.kind == "fence" and not block.info:
                self.add(spec, "code_block_language", path, block.line, "warning")

    # -- リンクと画像 -------------------------------------------------------

    def check_links(self, path: Path, lines: list[str]) -> None:
        text_spec = self.rule("link_text")
        bare_spec = self.rule("bare_url_link")
        broken_spec = self.rule("broken_local_link")
        anchor_spec = self.rule("broken_anchor")

        anchors = collect_anchors(lines)

        in_fence = False
        for number, raw in enumerate(lines, start=1):
            if re.match(r"^\s*(`{3,}|~{3,})", raw):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            for label, target in re.findall(r"(?<!!)\[([^\]]*)\]\(([^)]*)\)", raw):
                clean = label.strip()

                if text_spec:
                    for word in text_spec.get("words", []):
                        if clean == word or clean.startswith(word):
                            self.add(text_spec, "link_text", path, number, "error", excerpt=clean)
                            break

                if bare_spec and re.match(r"^https?://", clean):
                    self.add(bare_spec, "bare_url_link", path, number, "warning", excerpt=clean)

                dest = target.split()[0] if target.split() else target
                if re.match(r"^(https?:|mailto:)", dest) or not dest:
                    continue

                file_part, _, anchor = dest.partition("#")

                if not file_part:
                    # 同じ文書内のアンカー
                    if anchor_spec and anchor and anchor not in anchors:
                        self.add(
                            anchor_spec,
                            "broken_anchor",
                            path,
                            number,
                            "error",
                            f"この文書に見出し `#{anchor}` が無い",
                            clean,
                        )
                    continue

                if broken_spec:
                    resolved = (path.parent / file_part).resolve()
                    if not resolved.exists():
                        self.add(
                            broken_spec,
                            "broken_local_link",
                            path,
                            number,
                            "error",
                            f"リンク先が存在しない: {file_part}",
                            clean,
                        )
                        continue

                if anchor_spec and anchor:
                    resolved = (path.parent / file_part).resolve()
                    if resolved.is_file() and resolved.suffix == ".md":
                        other = collect_anchors(resolved.read_text(encoding="utf-8").splitlines())
                        if anchor not in other:
                            self.add(
                                anchor_spec,
                                "broken_anchor",
                                path,
                                number,
                                "error",
                                f"{file_part} に見出し `#{anchor}` が無い",
                                clean,
                            )

    def check_images(self, path: Path, lines: list[str]) -> None:
        spec = self.rule("image_alt")
        if not spec:
            return
        in_fence = False
        for number, raw in enumerate(lines, start=1):
            if re.match(r"^\s*(`{3,}|~{3,})", raw):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for alt, target in re.findall(r"!\[([^\]]*)\]\(([^)]*)\)", raw):
                if not alt.strip():
                    self.add(
                        spec, "image_alt", path, number, "warning", excerpt=target.strip()[:80]
                    )

    # -- 語 ----------------------------------------------------------------

    def check_words(self, path: Path, blocks: list[Block]) -> None:
        vague = self.rule("vague_words")
        timeless = self.rule("timeless")
        hiragana = self.rule("open_in_hiragana")
        marker = self.rule("unresolved_marker")
        terms = self.rule("term_consistency")

        # 引用（>）とコードは、原文を改変できないので検査しない。
        checkable = [b for b in blocks if b.kind in ("paragraph", "list", "table", "heading")]

        # 用語のゆれは「1つの文書の中で両方が使われているか」で判定する。
        # 用語集は、既存文書が一方で統一されていればそれを尊重するとしている。
        # 常に片方を正として警告すると、統一済みの文書を誤検出する。
        term_hits: dict[str, dict[str, list[tuple[int, str]]]] = {}

        for block in checkable:
            for offset, raw in enumerate(block.lines):
                line = block.line + offset
                text = strip_inline(raw)

                for spec, name, severity in (
                    (vague, "vague_words", "warning"),
                    (timeless, "timeless", "warning"),
                    (marker, "unresolved_marker", "error"),
                ):
                    if not spec:
                        continue
                    for word in spec.get("words", []):
                        if word_pattern(word).search(text):
                            self.add(
                                spec,
                                name,
                                path,
                                line,
                                severity,
                                excerpt=f"「{word}」 {text.strip()}",
                            )
                            break

                if hiragana:
                    for kanji, kana in hiragana.get("pairs", {}).items():
                        if kanji in text:
                            self.add(
                                hiragana,
                                "open_in_hiragana",
                                path,
                                line,
                                "warning",
                                f"「{kanji}」は「{kana}」と書く",
                                text.strip(),
                            )

                if terms:
                    for group, forms in terms.get("groups", {}).items():
                        remainder = text
                        found: list[str] = []
                        # 長い形から順に取り除く。「ユーザー」を先に消さないと
                        # 「ユーザ」が常に一致してしまう。
                        for form in sorted(forms, key=len, reverse=True):
                            if form in remainder:
                                found.append(form)
                                remainder = remainder.replace(form, "")
                        for form in found:
                            term_hits.setdefault(group, {}).setdefault(form, []).append(
                                (line, text.strip())
                            )

        if terms:
            for group, by_form in term_hits.items():
                if len(by_form) < 2:
                    continue  # 文書内で統一されている
                counts = {form: len(hits) for form, hits in by_form.items()}
                majority = max(counts, key=lambda f: counts[f])
                detail = "、".join(f"{form}={counts[form]}" for form in sorted(counts))
                for form, hits in by_form.items():
                    if form == majority:
                        continue
                    for line, excerpt in hits:
                        self.add(
                            terms,
                            "term_consistency",
                            path,
                            line,
                            "warning",
                            f"この文書は「{form}」と「{majority}」を混在させている（{detail}）。1つに統一する",
                            excerpt,
                        )

    # -- メタ情報 -----------------------------------------------------------

    def check_metadata(self, path: Path, lines: list[str]) -> None:
        """独立した文書に、C-08 と O-02 が求めるメタ情報があるかを見る。

        この標準の本文（docs/）は全体で1つの文書として扱い、メタ情報は
        docs/index.md が持つ。各章に同じ表を置くのは O-04（同じことを2つの
        文書に書かない）に反する。この判断は docs/index.md に書いてある。
        """
        spec = self.rule("document_metadata")
        if not spec:
            return

        rel = path.relative_to(self.root).as_posix() if path.is_relative_to(self.root) else path.name
        targets = spec.get("paths", [])
        if not any(rel == t or rel.startswith(t) for t in targets):
            return

        window = "\n".join(lines[: spec.get("within_lines", 40)])
        missing = [label for label in spec.get("require", []) if label not in window]
        if missing:
            self.add(
                spec,
                "document_metadata",
                path,
                1,
                "error",
                f"冒頭にメタ情報が無い: {'、'.join(missing)}",
            )


# ------------------------------------------------------------------ 実行


def collect_files(config: dict, root: Path) -> list[Path]:
    target = config.get("target", {})
    includes = target.get("include", ["docs/**/*.md"])
    excludes = target.get("exclude", [])

    found: set[Path] = set()
    for pattern in includes:
        for path in root.glob(pattern):
            if path.is_file():
                found.add(path.resolve())

    def excluded(path: Path) -> bool:
        rel = path.relative_to(root).as_posix()
        return any(
            Path(rel).match(pattern) or rel.startswith(pattern.split("*")[0])
            for pattern in excludes
        )

    return sorted(p for p in found if not excluded(p))


def main() -> int:
    parser = argparse.ArgumentParser(description="日本語技術文書のチェッカー")
    parser.add_argument("paths", nargs="*", help="検査するファイル。省略時は設定の対象すべて")
    parser.add_argument("--config", default=str(CONFIG_PATH))
    parser.add_argument("--min-severity", default="info", choices=["error", "warning", "info"])
    parser.add_argument(
        "--report-suppressions",
        action="store_true",
        help="ファイルごとに何行が抑制されているかを表示する",
    )
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    root = ROOT

    files = [Path(p).resolve() for p in args.paths] if args.paths else collect_files(config, root)
    if not files:
        print("検査対象のファイルが見つからない", file=sys.stderr)
        return 2

    linter = Linter(config, root)
    for path in files:
        linter.check_file(path)

    threshold = SEVERITY_ORDER[args.min_severity]
    findings = [f for f in linter.findings if SEVERITY_ORDER[f.severity] <= threshold]
    findings.sort(key=lambda f: (str(f.path), f.line, SEVERITY_ORDER[f.severity]))

    for finding in findings:
        print(finding.format(root))
        print()

    counts = {"error": 0, "warning": 0, "info": 0}
    for finding in findings:
        counts[finding.severity] += 1

    if args.report_suppressions:
        print("抑制している行数")
        for path, count in sorted(linter.suppressed_lines.items()):
            if count:
                rel = path.relative_to(root) if path.is_relative_to(root) else path
                print(f"  {rel}: {count} 行")
        print()

    print(f"検査したファイル: {len(files)}")
    print(f"error: {counts['error']}  warning: {counts['warning']}  info: {counts['info']}")

    # fail_on は「この重大度以上が1件でもあれば失敗」という意味で扱う。
    fail_on = config.get("severity", {}).get("fail_on", "error")
    limit = SEVERITY_ORDER.get(fail_on, 0)
    failed = any(SEVERITY_ORDER[f.severity] <= limit for f in linter.findings)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

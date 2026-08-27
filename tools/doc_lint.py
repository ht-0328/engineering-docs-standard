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

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / ".doclint.yml"

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}

# 敬体（ですます調）の文末。これ以外を常体とみなす。
POLITE_ENDING = re.compile(
    r"(です|ます|ません|でした|ましょう|ください|でしょう|ですが|ますが|ましたが)$"
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
        rel = self.path.relative_to(root)
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


def split_sentences(text: str) -> list[str]:
    """日本語の文に分割する。句点・感嘆符・疑問符で切る。

    閉じかっこが続く場合は、かっこの外まで含めて1文とする。
    """
    sentences: list[str] = []
    buf = ""
    closing = "」』）\"'”’"
    for index, char in enumerate(text):
        buf += char
        if char in "。！？":
            nxt = text[index + 1] if index + 1 < len(text) else ""
            if nxt in closing:
                continue
            sentences.append(buf.strip())
            buf = ""
    if buf.strip():
        sentences.append(buf.strip())
    return [s for s in sentences if s]


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
            if fence_match and fence_match.group(2).startswith(fence_marker[0]) and len(
                fence_match.group(2)
            ) >= len(fence_marker):
                in_fence = False
                flush()
            continue

        if fence_match:
            flush()
            in_fence = True
            fence_marker = fence_match.group(2)
            current = Block(kind="fence", line=number, lines=[line], info=fence_match.group(3).strip())
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush()
            blocks.append(
                Block(kind="heading", line=number, lines=[heading.group(2).strip()], level=len(heading.group(1)))
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
    """行内のコード、リンクURL、画像を取り除いた本文を返す。

    行内コードは削除せず記号1文字に置き換える。削除すると、コードだけを並べた
    文が読点の列になり、読点の数の検査が誤検出する。
    """
    text = re.sub(r"<!--.*?-->", "", text)
    text = re.sub(r"`[^`]*`", "▪", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return text


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
    """

    def names(raw: str | None) -> set[str]:
        if not raw or not raw.strip():
            return {"*"}
        return {token for token in re.split(r"[,\s]+", raw.strip()) if token}

    suppressed: dict[int, set[str]] = {}
    active: set[str] = set()

    for number, raw in enumerate(lines, start=1):
        enable = ENABLE_BLOCK.search(raw)
        if enable:
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


class Linter:
    def __init__(self, config: dict, root: Path) -> None:
        self.config = config
        self.rules = config.get("rules", {})
        self.root = root
        self.findings: list[Finding] = []
        self.suppressions: dict[int, set[str]] = {}

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
        blocks = parse_blocks(lines)

        self.check_headings(path, blocks)
        self.check_sentences(path, blocks)
        self.check_style_mixing(path, blocks)
        self.check_paragraphs(path, blocks)
        self.check_lists(path, blocks)
        self.check_tables(path, blocks)
        self.check_fences(path, blocks)
        self.check_links(path, lines)
        self.check_words(path, blocks)

    def check_headings(self, path: Path, blocks: list[Block]) -> None:
        headings = [b for b in blocks if b.kind == "heading"]

        skip = self.rule("heading_level_skip")
        depth = self.rule("heading_max_depth")
        period = self.rule("heading_no_period")
        vague = self.rule("vague_heading")

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
                if block.kind != "heading":
                    continue
                # h1 は文書のタイトルである。直後に h2 が来るのは正しい形なので除く。
                if block.level == 1:
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

    def check_sentences(self, path: Path, blocks: list[Block]) -> None:
        length = self.rule("sentence_length")
        commas = self.rule("commas_per_sentence")
        negative = self.rule("double_negative")

        for block in blocks:
            if block.kind not in ("paragraph", "list"):
                continue
            for offset, raw in enumerate(block.lines):
                text = strip_inline(raw)
                text = re.sub(r"^\s*([-*+]|\d+\.)\s+", "", text)
                for sentence in split_sentences(text):
                    line = block.line + offset
                    size = len(sentence)

                    if length:
                        if size > length.get("error_over", 100):
                            self.add(
                                length,
                                "sentence_length",
                                path,
                                line,
                                "error",
                                f"一文が {size} 字ある。主題が複数入っていないか確認する",
                                sentence,
                            )
                        elif size > length.get("warn_over", 50):
                            self.add(
                                length,
                                "sentence_length",
                                path,
                                line,
                                "warning",
                                f"一文が {size} 字ある（目安は50字）",
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
                                    negative, "double_negative", path, line, "warning", excerpt=sentence
                                )
                                break

    def check_style_mixing(self, path: Path, blocks: list[Block]) -> None:
        spec = self.rule("style_mixing")
        if not spec:
            return

        samples: list[tuple[int, str, str]] = []  # (line, style, sentence)
        for block in blocks:
            if block.kind != "paragraph":
                continue
            for offset, raw in enumerate(block.lines):
                for sentence in split_sentences(strip_inline(raw)):
                    body = sentence.rstrip("。！？")
                    if not body:
                        continue
                    style = "敬体" if POLITE_ENDING.search(body) else "常体"
                    samples.append((block.line + offset, style, sentence))

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
                    f"文書全体は{majority}だが、この文は{minority}になっている",
                    sentence,
                )

    def check_paragraphs(self, path: Path, blocks: list[Block]) -> None:
        spec = self.rule("paragraph_sentences")
        if not spec:
            return
        limit = spec.get("warn_over", 7)
        for block in blocks:
            if block.kind != "paragraph":
                continue
            text = strip_inline(" ".join(block.lines))
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
            top_level = [
                line
                for line in block.lines
                if re.match(r"^([-*+]|\d+\.)\s+", line)
            ]
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

    def check_tables(self, path: Path, blocks: list[Block]) -> None:
        spec = self.rule("table_cell_length")
        if not spec:
            return
        limit = spec.get("warn_over", 2)
        for block in blocks:
            if block.kind != "table":
                continue
            for offset, raw in enumerate(block.lines):
                if re.match(r"^\s*\|[\s:|-]+\|\s*$", raw):
                    continue
                for cell in raw.strip().strip("|").split("|"):
                    text = strip_inline(cell).strip()
                    if len(split_sentences(text)) > limit:
                        self.add(
                            spec,
                            "table_cell_length",
                            path,
                            block.line + offset,
                            "warning",
                            excerpt=text,
                        )

    def check_fences(self, path: Path, blocks: list[Block]) -> None:
        spec = self.rule("code_block_language")
        if not spec:
            return
        for block in blocks:
            if block.kind == "fence" and not block.info:
                self.add(spec, "code_block_language", path, block.line, "warning")

    def check_links(self, path: Path, lines: list[str]) -> None:
        text_spec = self.rule("link_text")
        bare_spec = self.rule("bare_url_link")
        broken_spec = self.rule("broken_local_link")

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

                if broken_spec:
                    dest = target.split()[0] if target.split() else target
                    if re.match(r"^(https?:|mailto:|#)", dest) or not dest:
                        continue
                    dest = dest.split("#")[0]
                    if not dest:
                        continue
                    resolved = (path.parent / dest).resolve()
                    if not resolved.exists():
                        self.add(
                            broken_spec,
                            "broken_local_link",
                            path,
                            number,
                            "error",
                            f"リンク先が存在しない: {dest}",
                            clean,
                        )

    def check_words(self, path: Path, blocks: list[Block]) -> None:
        vague = self.rule("vague_words")
        timeless = self.rule("timeless")
        hiragana = self.rule("open_in_hiragana")
        marker = self.rule("unresolved_marker")
        terms = self.rule("term_consistency")

        # 引用（>）とコードは、原文を改変できないので検査しない。
        checkable = [b for b in blocks if b.kind in ("paragraph", "list", "table", "heading")]

        seen_variants: dict[str, list[tuple[int, str]]] = {}

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
                            self.add(spec, name, path, line, severity, excerpt=f"「{word}」 {text.strip()}")
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
                    for canonical, variants in terms.get("canonical", {}).items():
                        # 正しい語を先に取り除く。「ユーザ」は「ユーザー」の一部なので、
                        # 取り除かないと正しい表記が誤検出される。
                        remainder = text.replace(canonical, "")
                        for variant in variants:
                            if variant in remainder:
                                seen_variants.setdefault(canonical, []).append((line, variant))

        if terms:
            for canonical, hits in seen_variants.items():
                for line, variant in hits:
                    self.add(
                        terms,
                        "term_consistency",
                        path,
                        line,
                        "warning",
                        f"「{variant}」ではなく「{canonical}」を使う",
                    )


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
        return any(Path(rel).match(pattern) or rel.startswith(pattern.split("*")[0]) for pattern in excludes)

    return sorted(p for p in found if not excluded(p))


def main() -> int:
    parser = argparse.ArgumentParser(description="日本語技術文書のチェッカー")
    parser.add_argument("paths", nargs="*", help="検査するファイル。省略時は設定の対象すべて")
    parser.add_argument("--config", default=str(CONFIG_PATH))
    parser.add_argument("--min-severity", default="info", choices=["error", "warning", "info"])
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    root = ROOT

    if args.paths:
        files = [Path(p).resolve() for p in args.paths]
    else:
        files = collect_files(config, root)

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

    print(f"検査したファイル: {len(files)}")
    print(f"error: {counts['error']}  warning: {counts['warning']}  info: {counts['info']}")

    fail_on = config.get("severity", {}).get("fail_on", "error")
    return 1 if counts.get(fail_on, 0) > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())

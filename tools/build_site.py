#!/usr/bin/env python3
"""docs/ の Markdown から、静的HTMLサイトを生成する。

    docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-tools python tools/build_site.py

正本は `docs/` の Markdown である。`site/` は生成物であり、直接編集しない。

サイトになるのは `docs/` の中だけである。本文から `../README.md` のように
`docs/` の外を指すリンクは、飛び先がサイトに無い。そのため、GitHub の URL
に差し替える。差し替え先は `REPO_URL` で決める。

サイトは、表示のために外部へ通信しない。Mermaid は `tools/vendor/mermaid.min.js`
を同梱する。書体は閲覧環境のものを使う。

`tools/vendor/` は再取得できるため Git で追跡していない。サイトを作る前に
一度だけ `bash tools/fetch_vendor.sh` を実行する。実行していない場合、図は
記法のまま表示される。
"""

from __future__ import annotations

import argparse
import html
import json
import posixpath
import re
import shutil
import sys
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from mdslug import slugify

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "tools" / "vendor"
DIAGRAMS = ROOT / "diagrams" / "export"

# docs/ の外にあるファイル（README.md、CHANGELOG.md、templates/ など）は
# サイトに含めない。そのままだとリンク先が無く、404 になる。
# 代わりに、正本のリポジトリを見に行かせる。fork したときはここを変える。
REPO_URL = "https://github.com/ht-0328/engineering-docs-standard"
REPO_BRANCH = "main"

# 本文で「良いリンク文」を説明するときに使う、飛び先のない例示。
# そのままリンクにすると、押しても何も起きない。
PLACEHOLDER_HREFS = {"...", "URL"}

# サイドバーの並び。ここに無いファイルは末尾に回す。
ORDER = [
    "index.md",
    "01-what-is-good.md",
    "02-before-writing.md",
    "03-structure.md",
    "04-sentences.md",
    "05-presentation.md",
    "06-review.md",
    "07-antipatterns.md",
    "08-templates.md",
    "09-your-instincts.md",
    "10-operations.md",
    "appendix-checklist.md",
    "appendix-glossary.md",
    "adr/ADR-001-diagram-tool.md",
    "adr/ADR-002-site-generator.md",
    "adr/ADR-003-ai-volume.md",
]

SECTIONS = [
    ("はじめに", ["index.md"]),
    ("原則", ["01-what-is-good.md", "02-before-writing.md"]),
    ("書き方", ["03-structure.md", "04-sentences.md", "05-presentation.md"]),
    ("レビュー", ["06-review.md", "07-antipatterns.md"]),
    ("実践", ["08-templates.md", "09-your-instincts.md", "10-operations.md"]),
    (
        "付録",
        [
            "appendix-checklist.md",
            "appendix-glossary.md",
            "adr/ADR-001-diagram-tool.md",
            "adr/ADR-002-site-generator.md",
            "adr/ADR-003-ai-volume.md",
        ],
    ),
]

# AI向けの別冊（docs-ai/）の並び。別冊にした理由は docs/adr/ADR-003-ai-volume.md にある。
AI_ORDER = [
    "index.md",
    "01-how-ai-reads.md",
    "02-ai-readable-docs.md",
    "03-instructions.md",
    "04-skills-and-agents.md",
    "05-both-readers.md",
    "06-verifying-ai-writing.md",
    "07-antipatterns.md",
    "08-templates.md",
    "appendix-checklist.md",
    "appendix-experiments.md",
    "appendix-loanwords.md",
]

AI_SECTIONS = [
    ("はじめに", ["index.md"]),
    ("前提", ["01-how-ai-reads.md"]),
    ("規則", [
        "02-ai-readable-docs.md",
        "03-instructions.md",
        "04-skills-and-agents.md",
        "05-both-readers.md",
        "06-verifying-ai-writing.md",
    ]),
    ("実践", ["07-antipatterns.md", "08-templates.md"]),
    ("付録", [
        "appendix-checklist.md",
        "appendix-experiments.md",
        "appendix-loanwords.md",
    ]),
]

# サイトの組み合わせ。引数を渡さなければ "main" を使う。**既定の動きは変えていない。**
PROFILES: dict[str, dict] = {
    "main": {
        "docs": ROOT / "docs",
        "site": ROOT / "site",
        "order": ORDER,
        "sections": SECTIONS,
        "site_name": "エンジニアのためのドキュメント標準",
        # 同じサイトの中にある別の版。リポジトリ上の場所を、サイト上の位置に対応させる。
        # これが無いと、別冊へのリンクが GitHub に飛んでしまう。
        "siblings": {"docs-ai": "ai"},
    },
    "ai": {
        "docs": ROOT / "docs-ai",
        "site": ROOT / "site" / "ai",
        "order": AI_ORDER,
        "sections": AI_SECTIONS,
        "site_name": "AIに読ませる文書の標準",
        # 別冊は site/ai/ に出る。本編は1つ上にある。
        "siblings": {"docs": ".."},
    },
}

# 実際に使う値。build() の冒頭で選んだプロファイルの値に差し替える。
DOCS = PROFILES["main"]["docs"]
SITE = PROFILES["main"]["site"]
SITE_NAME = PROFILES["main"]["site_name"]
SIBLINGS: dict[str, str] = PROFILES["main"]["siblings"]


@dataclass
class Page:
    source: Path
    rel: str  # docs からの相対パス（例: adr/ADR-001-diagram-tool.md）
    url: str  # site 内のURL（例: adr/ADR-001-diagram-tool.html）
    title: str = ""
    html: str = ""
    toc: list[tuple[int, str, str]] = field(default_factory=list)  # (level, id, text)
    search: list[dict] = field(default_factory=list)


def make_renderer() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": True, "linkify": False})
    md.enable("table")
    md.enable("strikethrough")
    md.use(anchors_plugin, min_level=2, max_level=4, slug_func=slugify, permalink=False)

    formatter = HtmlFormatter(nowrap=False, cssclass="code")

    def fence(self, tokens, idx, options, env):  # noqa: ANN001
        token = tokens[idx]
        info = (token.info or "").strip().split()
        lang = info[0] if info else ""
        code = token.content

        if lang == "mermaid":
            return f'<pre class="mermaid">{html.escape(code)}</pre>\n'

        if lang:
            try:
                lexer = get_lexer_by_name(lang, stripall=False)
                return f'<div class="codeblock" data-lang="{html.escape(lang)}">{highlight(code, lexer, formatter)}</div>\n'
            except ClassNotFound:
                pass

        label = f' data-lang="{html.escape(lang)}"' if lang else ""
        return f'<div class="codeblock"{label}><pre class="code"><code>{html.escape(code)}</code></pre></div>\n'

    md.add_render_rule("fence", fence)
    return md


def drop_placeholder_links(body: str) -> str:
    """飛び先のない例示リンクを、ただの文字にする。

    `[こちら](...)` のような例は、リンク文の良し悪しを示すためのものである。
    リンクのまま出すと、読者が押して 404 に飛ぶ。
    """
    pattern = "|".join(re.escape(h) for h in sorted(PLACEHOLDER_HREFS))
    return re.sub(
        rf'<a href="(?:{pattern})">(.*?)</a>',
        r'<span class="link-example">\1</span>',
        body,
        flags=re.S,
    )


def repo_file(repo_path: str) -> Path:
    """URL 上のパスを、手元のファイルの位置に戻す。"""
    return ROOT / urllib.parse.unquote(repo_path)


def repo_url(repo_path: str, anchor: str) -> str:
    """リポジトリ内のパスを、GitHub で読める URL に直す。

    `repo_path` と `anchor` は markdown-it が符号化したあとの文字列である。
    ここで符号化し直すと `%` が二重になり、リンクが飛べなくなる。
    """
    kind = "tree" if repo_file(repo_path).is_dir() else "blob"
    url = f"{REPO_URL}/{kind}/{REPO_BRANCH}/{repo_path}"
    if anchor:
        url += "#" + anchor
    return url


def rewrite_links(body: str, rel: str, warnings: list[str]) -> str:
    """リンクを、サイトの中で飛べる形に直す。

    docs/ の中を指すリンクは、拡張子を .html に替えるだけでよい。
    同じサイトの中にある別の版（SIBLINGS）を指すリンクは、サイトの中で飛べる形にする。
    それ以外で docs/ の外を指すリンクは、サイトに実体が無いため、GitHub の URL にする。

    `rel` は docs/ から見たこのページの位置である。`../` の解決に使う。
    """
    base = posixpath.dirname(rel)

    def repl(match: re.Match[str]) -> str:
        href = match.group(1)
        if re.match(r"^(https?:|mailto:|#)", href):
            return match.group(0)
        path, _, anchor = href.partition("#")
        if not path:
            return match.group(0)

        # docs/ から見た飛び先。docs/ の外に出ると `../` が残る。
        inside_docs = posixpath.normpath(posixpath.join(base, path))
        if not inside_docs.startswith("../"):
            if path.endswith(".md"):
                path = path[: -len(".md")] + ".html"
            return f'href="{path}{"#" + anchor if anchor else ""}"'

        repo_path = posixpath.normpath(posixpath.join(DOCS.name, base, path))

        # 同じサイトの中にある別の版を指しているなら、サイトの中で飛べる形にする。
        head, _, tail = repo_path.partition("/")
        if head in SIBLINGS and tail.endswith(".md"):
            depth = rel.count("/")
            target = f"{SIBLINGS[head]}/{tail[: -len('.md')]}.html"
            href_out = "../" * depth + target
            return f'href="{href_out}{"#" + anchor if anchor else ""}"'

        if not repo_file(repo_path).exists():
            warnings.append(f"{rel}: リンク先がリポジトリに無い: {href}")
        return f'href="{repo_url(repo_path, anchor)}"'

    return re.sub(r'href="([^"]+)"', repl, body)


def add_rule_badges(body: str) -> str:
    """「規範度: 必須」を見た目のバッジにする。"""

    def repl(match: re.Match[str]) -> str:
        level = match.group(1)
        rest = match.group(2) or ""
        cls = {"必須": "must", "推奨": "should", "任意": "may"}.get(level, "may")
        note = f'<span class="badge-note">{rest.strip()}</span>' if rest.strip() else ""
        return f'<p class="rule-level"><span class="badge badge-{cls}">{level}</span>{note}</p>'

    return re.sub(
        r"<p><strong>規範度: ([必須推奨任意]+)</strong>([^<]*)</p>",
        repl,
        body,
    )


def mark_examples(body: str) -> str:
    """Before / After の見出し段落に印を付ける。"""
    body = re.sub(
        r"<p><strong>(Before[^<]*)</strong></p>",
        r'<p class="ex-label ex-before">\1</p>',
        body,
    )
    body = re.sub(
        r"<p><strong>(After[^<]*)</strong></p>",
        r'<p class="ex-label ex-after">\1</p>',
        body,
    )
    return body


def extract_toc(body: str) -> list[tuple[int, str, str]]:
    items: list[tuple[int, str, str]] = []
    for match in re.finditer(r'<h([234]) id="([^"]+)"[^>]*>(.*?)</h\1>', body, re.S):
        level = int(match.group(1))
        anchor = match.group(2)
        text = re.sub(r"<[^>]+>", "", match.group(3)).strip()
        items.append((level, anchor, text))
    return items


def build_search_entries(page: Page, body: str) -> list[dict]:
    """見出しごとに本文の抜粋を持たせた検索用の索引を作る。"""
    plain = re.sub(r"<(script|style|pre)[^>]*>.*?</\1>", " ", body, flags=re.S)
    chunks = re.split(r'(<h[234] id="[^"]+"[^>]*>.*?</h[234]>)', plain, flags=re.S)

    entries: list[dict] = []
    current = {"anchor": "", "heading": page.title}
    buffer: list[str] = []

    def flush() -> None:
        if not buffer:
            return
        text = re.sub(r"<[^>]+>", " ", " ".join(buffer))
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        if len(text) < 8:
            return
        entries.append(
            {
                "url": page.url + (f"#{current['anchor']}" if current["anchor"] else ""),
                "page": page.title,
                "heading": current["heading"],
                "text": text[:600],
            }
        )

    for chunk in chunks:
        heading = re.match(r'<h[234] id="([^"]+)"[^>]*>(.*?)</h[234]>', chunk, re.S)
        if heading:
            flush()
            buffer = []
            current = {
                "anchor": heading.group(1),
                "heading": re.sub(r"<[^>]+>", "", heading.group(2)).strip(),
            }
        else:
            buffer.append(chunk)
    flush()
    return entries


def collect_pages() -> list[Page]:
    found = {p.relative_to(DOCS).as_posix(): p for p in DOCS.rglob("*.md")}
    ordered = [rel for rel in ORDER if rel in found]
    ordered += sorted(rel for rel in found if rel not in ORDER)
    return [
        Page(source=found[rel], rel=rel, url=rel[: -len(".md")] + ".html")
        for rel in ordered
    ]


def nav_html(pages: list[Page], current: Page) -> str:
    by_rel = {p.rel: p for p in pages}
    out: list[str] = []
    listed: set[str] = set()

    for section, members in SECTIONS:
        items = [by_rel[rel] for rel in members if rel in by_rel]
        if not items:
            continue
        out.append(f'<div class="nav-section"><span class="nav-section-title">{section}</span><ul>')
        for page in items:
            listed.add(page.rel)
            active = " class=\"active\"" if page.rel == current.rel else ""
            href = relative_url(current, page)
            out.append(f'<li><a href="{href}"{active}>{html.escape(page.title)}</a></li>')
        out.append("</ul></div>")

    rest = [p for p in pages if p.rel not in listed]
    if rest:
        out.append('<div class="nav-section"><span class="nav-section-title">その他</span><ul>')
        for page in rest:
            active = " class=\"active\"" if page.rel == current.rel else ""
            out.append(f'<li><a href="{relative_url(current, page)}"{active}>{html.escape(page.title)}</a></li>')
        out.append("</ul></div>")

    return "\n".join(out)


def relative_url(current: Page, target: Page) -> str:
    depth = current.rel.count("/")
    prefix = "../" * depth
    return prefix + target.url


def toc_html(page: Page) -> str:
    if len(page.toc) < 2:
        return ""
    items = [
        f'<li class="lv{level}"><a href="#{anchor}">{html.escape(text)}</a></li>'
        for level, anchor, text in page.toc
    ]
    return (
        '<nav class="toc" aria-label="このページの目次">'
        '<span class="toc-title">このページの内容</span>'
        f'<ul>{"".join(items)}</ul></nav>'
    )


PAGE_TEMPLATE = """<!doctype html>
<html lang="ja" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | {site_name}</title>
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<a class="skip" href="#main">本文へ移動</a>
<header class="topbar">
  <a class="brand" href="{prefix}index.html">ドキュメント標準</a>
  <div class="topbar-tools">
    <label class="search-box">
      <span class="visually-hidden">検索</span>
      <input id="search-input" type="search" placeholder="検索（例: 一文一義、レビュー、見出し）" autocomplete="off">
    </label>
    <button id="theme-toggle" type="button" aria-label="表示テーマを切り替える">◐</button>
    <button id="nav-toggle" type="button" aria-label="目次を開閉する">☰</button>
  </div>
</header>
<div id="search-results" hidden></div>
<div class="layout">
  <nav class="sidebar" id="sidebar" aria-label="章の一覧">{nav}</nav>
  <main id="main">
    <noscript><p class="noscript-note">JavaScript が無効なため、図は記法のまま表示され、検索とテーマ切り替えは動作しない。本文はそのまま読める。</p></noscript>
    <article class="content">{body}</article>
    <nav class="pager">{pager}</nav>
  </main>
  {toc}
</div>
<script src="{prefix}assets/mermaid.min.js"></script>
<script>window.__SEARCH_PREFIX__ = "{prefix}";</script>
<script src="{prefix}assets/search-index.js"></script>
<script src="{prefix}assets/site.js"></script>
</body>
</html>
"""


def pager_html(pages: list[Page], index: int, current: Page) -> str:
    parts: list[str] = []
    if index > 0:
        prev = pages[index - 1]
        parts.append(
            f'<a class="pager-prev" href="{relative_url(current, prev)}">'
            f'<span>前</span>{html.escape(prev.title)}</a>'
        )
    if index < len(pages) - 1:
        nxt = pages[index + 1]
        parts.append(
            f'<a class="pager-next" href="{relative_url(current, nxt)}">'
            f'<span>次</span>{html.escape(nxt.title)}</a>'
        )
    return "".join(parts)


def build(profile: str = "main") -> int:
    """サイトを1つ作る。`profile` は PROFILES の名前である。

    引数を渡さなければ本編を作る。**既定の動きはプロファイル導入の前と同じである。**
    """
    global DOCS, SITE, ORDER, SECTIONS, SITE_NAME, SIBLINGS
    config = PROFILES[profile]
    DOCS = config["docs"]
    SITE = config["site"]
    ORDER = config["order"]
    SECTIONS = config["sections"]
    SITE_NAME = config["site_name"]
    SIBLINGS = config["siblings"]

    md = make_renderer()
    pages = collect_pages()
    link_warnings: list[str] = []

    for page in pages:
        text = page.source.read_text(encoding="utf-8")
        heading = re.search(r"^#\s+(.+)$", text, re.M)
        page.title = heading.group(1).strip() if heading else page.rel

        body = md.render(text)
        body = drop_placeholder_links(body)
        body = rewrite_links(body, page.rel, link_warnings)
        body = add_rule_badges(body)
        body = mark_examples(body)
        page.html = body
        page.toc = extract_toc(body)
        page.search = build_search_entries(page, body)

    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "assets").mkdir(parents=True)

    for index, page in enumerate(pages):
        depth = page.rel.count("/")
        prefix = "../" * depth
        out = SITE / page.url
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            PAGE_TEMPLATE.format(
                title=html.escape(page.title),
                site_name=html.escape(SITE_NAME),
                prefix=prefix,
                nav=nav_html(pages, page),
                body=page.html,
                toc=toc_html(page),
                pager=pager_html(pages, index, page),
            ),
            encoding="utf-8",
        )

    entries: list[dict] = []
    for page in pages:
        entries.extend(page.search)
    (SITE / "assets" / "search-index.js").write_text(
        "window.__SEARCH_INDEX__ = " + json.dumps(entries, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )

    (SITE / "assets" / "style.css").write_text(STYLE, encoding="utf-8")
    (SITE / "assets" / "site.js").write_text(SCRIPT, encoding="utf-8")

    mermaid = VENDOR / "mermaid.min.js"
    if mermaid.exists():
        shutil.copy(mermaid, SITE / "assets" / "mermaid.min.js")
    else:
        (SITE / "assets" / "mermaid.min.js").write_text(
            "/* mermaid.min.js が tools/vendor に無い。図は描画されない。 */\n", encoding="utf-8"
        )
        print("警告: tools/vendor/mermaid.min.js が無い。図は記法のまま表示される。")
        print("      先に `bash tools/fetch_vendor.sh` を実行すること。")

    if DIAGRAMS.exists():
        shutil.copytree(DIAGRAMS, SITE / "diagrams", dirs_exist_ok=True)

    for warning in link_warnings:
        print(f"警告: {warning}")

    print(f"生成したページ: {len(pages)}")
    print(f"検索索引の項目: {len(entries)}")
    print(f"出力先: {SITE}")
    return 0


STYLE = """
:root {
  color-scheme: light dark;
  --bg: #fbfbfd;
  --bg-raised: #ffffff;
  --bg-sunken: #f1f3f7;
  --text: #1a2130;
  --text-dim: #5a6478;
  --line: #dfe3ec;
  --accent: #1a56db;
  --accent-soft: #eaf0ff;
  --must: #b42318;
  --must-bg: #fdecea;
  --should: #b25e09;
  --should-bg: #fff4e5;
  --may: #2f6f4e;
  --may-bg: #e9f6ef;
  --before-bg: #fdecea;
  --before-line: #d0342c;
  --after-bg: #e9f6ef;
  --after-line: #2f855a;
  --measure: 42em;
}
:root[data-theme="dark"], :root[data-theme="auto"] {
  color-scheme: light dark;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0f1420;
    --bg-raised: #161d2c;
    --bg-sunken: #1b2333;
    --text: #dfe6f2;
    --text-dim: #9aa6bd;
    --line: #2a3446;
    --accent: #7aa5ff;
    --accent-soft: #1b2843;
    --must: #ff9d94;
    --must-bg: #3a1c19;
    --should: #ffc06b;
    --should-bg: #3a2a12;
    --may: #86d9ac;
    --may-bg: #123024;
    --before-bg: #3a1c19;
    --before-line: #ff7a70;
    --after-bg: #123024;
    --after-line: #57c98c;
  }
}
:root[data-theme="dark"] {
  --bg: #0f1420;
  --bg-raised: #161d2c;
  --bg-sunken: #1b2333;
  --text: #dfe6f2;
  --text-dim: #9aa6bd;
  --line: #2a3446;
  --accent: #7aa5ff;
  --accent-soft: #1b2843;
  --must: #ff9d94;
  --must-bg: #3a1c19;
  --should: #ffc06b;
  --should-bg: #3a2a12;
  --may: #86d9ac;
  --may-bg: #123024;
  --before-bg: #3a1c19;
  --before-line: #ff7a70;
  --after-bg: #123024;
  --after-line: #57c98c;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 5rem; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic", "Meiryo", system-ui, sans-serif;
  font-size: 16px;
  line-height: 1.9;
  -webkit-text-size-adjust: 100%;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* 本文中の「リンクの例」。飛び先が無いので、押せないことが分かる見た目にする。 */
.link-example {
  color: var(--text-dim);
  text-decoration: underline dotted;
  text-underline-offset: 2px;
}

.skip { position: absolute; left: -999px; }
.skip:focus { left: 1rem; top: 1rem; background: var(--bg-raised); padding: .5rem 1rem; z-index: 100; }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }

.topbar {
  position: sticky; top: 0; z-index: 40;
  display: flex; align-items: center; gap: 1rem;
  padding: .7rem 1.2rem;
  background: color-mix(in srgb, var(--bg-raised) 88%, transparent);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
}
.brand { font-weight: 700; letter-spacing: .02em; color: var(--text); }
.topbar-tools { margin-left: auto; display: flex; align-items: center; gap: .6rem; }
.search-box input {
  width: min(34ch, 46vw);
  padding: .45rem .8rem;
  border: 1px solid var(--line); border-radius: 999px;
  background: var(--bg-sunken); color: var(--text);
  font: inherit; font-size: .9rem;
}
.search-box input:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
.topbar-tools button {
  border: 1px solid var(--line); border-radius: 8px;
  background: var(--bg-sunken); color: var(--text);
  width: 2.2rem; height: 2.2rem; cursor: pointer; font-size: 1rem;
}
#nav-toggle { display: none; }

#search-results {
  position: fixed; top: 3.6rem; left: 50%; transform: translateX(-50%);
  width: min(720px, 92vw); max-height: 70vh; overflow: auto; z-index: 50;
  background: var(--bg-raised); border: 1px solid var(--line);
  border-radius: 12px; box-shadow: 0 20px 50px rgba(0,0,0,.18); padding: .5rem;
}
#search-results .hit { display: block; padding: .6rem .8rem; border-radius: 8px; color: var(--text); }
#search-results .hit:hover { background: var(--accent-soft); text-decoration: none; }
#search-results .hit-head { font-weight: 700; font-size: .95rem; }
#search-results .hit-page { color: var(--text-dim); font-size: .78rem; }
#search-results .hit-text { color: var(--text-dim); font-size: .85rem; line-height: 1.6;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
#search-results .empty { padding: 1rem; color: var(--text-dim); }
mark { background: var(--accent-soft); color: inherit; padding: 0 .1em; border-radius: 3px; }

.layout {
  display: grid;
  grid-template-columns: 17rem minmax(0, 1fr) 15rem;
  gap: 2rem;
  max-width: 96rem; margin: 0 auto; padding: 1.5rem 1.2rem 4rem;
}
.sidebar { position: sticky; top: 4.5rem; align-self: start; max-height: calc(100vh - 6rem); overflow-y: auto; font-size: .92rem; }
.nav-section { margin-bottom: 1.2rem; }
.nav-section-title { display: block; font-size: .72rem; letter-spacing: .12em; text-transform: uppercase;
  color: var(--text-dim); margin-bottom: .35rem; }
.sidebar ul { list-style: none; margin: 0; padding: 0; }
.sidebar li a { display: block; padding: .3rem .6rem; border-radius: 7px; color: var(--text-dim); line-height: 1.5; }
.sidebar li a:hover { background: var(--bg-sunken); color: var(--text); text-decoration: none; }
.sidebar li a.active { background: var(--accent-soft); color: var(--accent); font-weight: 700; }

.toc { position: sticky; top: 4.5rem; align-self: start; max-height: calc(100vh - 6rem); overflow-y: auto;
  font-size: .84rem; border-left: 1px solid var(--line); padding-left: 1rem; }
.toc-title { display: block; font-size: .72rem; letter-spacing: .12em; text-transform: uppercase;
  color: var(--text-dim); margin-bottom: .4rem; }
.toc ul { list-style: none; margin: 0; padding: 0; }
.toc li { margin: .15rem 0; }
.toc li.lv3 { padding-left: .8rem; }
.toc li.lv4 { padding-left: 1.6rem; }
.toc a { color: var(--text-dim); }
.toc a.active { color: var(--accent); font-weight: 700; }

.content { max-width: var(--measure); }
.content h1 { font-size: 1.9rem; line-height: 1.4; margin: .2rem 0 1.4rem; letter-spacing: .01em; }
.content h2 { font-size: 1.35rem; margin: 2.6rem 0 .9rem; padding-top: .6rem; border-top: 1px solid var(--line); }
.content h3 { font-size: 1.1rem; margin: 1.9rem 0 .7rem; }
.content h4 { font-size: 1rem; margin: 1.4rem 0 .6rem; color: var(--text-dim); }
.content p { margin: 0 0 1.05rem; }
.content ul, .content ol { margin: 0 0 1.05rem; padding-left: 1.5rem; }
.content li { margin: .3rem 0; }
.content li::marker { color: var(--text-dim); }
.content strong { font-weight: 700; }
.content hr { border: 0; border-top: 1px solid var(--line); margin: 2.4rem 0; }

.content blockquote {
  margin: 0 0 1.2rem; padding: .8rem 1.1rem;
  border-left: 3px solid var(--accent);
  background: var(--bg-sunken); border-radius: 0 8px 8px 0;
  color: var(--text);
}
.content blockquote p:last-child { margin-bottom: 0; }

.table-scroll, .content table { display: block; overflow-x: auto; }
.content table {
  width: 100%; border-collapse: collapse; margin: 0 0 1.3rem;
  font-size: .92rem; line-height: 1.7;
}
.content th, .content td { border: 1px solid var(--line); padding: .5rem .7rem; text-align: left; vertical-align: top; }
.content th { background: var(--bg-sunken); font-weight: 700; white-space: nowrap; }
.content tbody tr:nth-child(even) { background: color-mix(in srgb, var(--bg-sunken) 45%, transparent); }

.codeblock { margin: 0 0 1.2rem; border: 1px solid var(--line); border-radius: 10px; overflow: hidden; position: relative; }
.codeblock::after {
  content: attr(data-lang); position: absolute; top: .35rem; right: .6rem;
  font-size: .68rem; letter-spacing: .08em; color: var(--text-dim); text-transform: uppercase;
}
.codeblock pre { margin: 0; padding: .9rem 1rem; overflow-x: auto; background: var(--bg-sunken); }
.codeblock code, .content code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace; font-size: .86em; }
.content :not(pre) > code { background: var(--bg-sunken); padding: .12em .38em; border-radius: 5px; border: 1px solid var(--line); }
.codeblock pre code { line-height: 1.75; white-space: pre; }

.rule-level { margin: 0 0 .9rem; }
.badge { display: inline-block; padding: .1rem .6rem; border-radius: 999px; font-size: .78rem; font-weight: 700; letter-spacing: .04em; }
.badge-must { background: var(--must-bg); color: var(--must); }
.badge-should { background: var(--should-bg); color: var(--should); }
.badge-may { background: var(--may-bg); color: var(--may); }
.badge-note { color: var(--text-dim); font-size: .82rem; margin-left: .5rem; }

.ex-label { margin: 0 0 .4rem; font-weight: 700; font-size: .88rem; letter-spacing: .04em; }
.ex-before { color: var(--before-line); }
.ex-after { color: var(--after-line); }
.ex-before + .codeblock { border-left: 4px solid var(--before-line); background: var(--before-bg); }
.ex-after + .codeblock { border-left: 4px solid var(--after-line); background: var(--after-bg); }
.ex-before + .codeblock pre, .ex-after + .codeblock pre { background: transparent; }

pre.mermaid { background: transparent; text-align: center; margin: 0 0 1.4rem; overflow-x: auto; }

.noscript-note { border: 1px solid var(--line); border-left: 4px solid var(--should);
  background: var(--should-bg); color: var(--should); padding: .7rem 1rem; border-radius: 8px;
  margin: 0 0 1.5rem; max-width: var(--measure); font-size: .9rem; }
.pager { display: flex; gap: 1rem; margin-top: 3rem; max-width: var(--measure); }
.pager a { flex: 1; padding: .8rem 1rem; border: 1px solid var(--line); border-radius: 10px;
  background: var(--bg-raised); color: var(--text); line-height: 1.5; }
.pager a:hover { border-color: var(--accent); text-decoration: none; }
.pager span { display: block; font-size: .72rem; color: var(--text-dim); letter-spacing: .1em; }
.pager-next { text-align: right; }

@media (max-width: 1180px) {
  .layout { grid-template-columns: 15rem minmax(0,1fr); }
  .toc { display: none; }
}
@media (max-width: 820px) {
  .layout { grid-template-columns: minmax(0,1fr); padding-top: 1rem; }
  .sidebar { display: none; position: static; max-height: none; }
  .sidebar.open { display: block; margin-bottom: 1.5rem; }
  #nav-toggle { display: inline-block; }
  .search-box input { width: 40vw; }
  .content h2 { font-size: 1.2rem; }
}
"""

SCRIPT = """
(function () {
  var root = document.documentElement;
  var stored = null;
  try { stored = localStorage.getItem('edocs-theme'); } catch (e) { stored = null; }
  if (stored === 'light' || stored === 'dark') { root.setAttribute('data-theme', stored); }

  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      var now = root.getAttribute('data-theme');
      var next;
      if (now === 'light') { next = 'dark'; }
      else if (now === 'dark') { next = 'light'; }
      else { next = dark ? 'light' : 'dark'; }
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('edocs-theme', next); } catch (e) {}
      renderMermaid(next);
    });
  }

  var navToggle = document.getElementById('nav-toggle');
  var sidebar = document.getElementById('sidebar');
  if (navToggle && sidebar) {
    navToggle.addEventListener('click', function () { sidebar.classList.toggle('open'); });
  }

  function currentTheme() {
    var set = root.getAttribute('data-theme');
    if (set === 'light' || set === 'dark') { return set; }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  var mermaidSources = [];
  function renderMermaid(theme) {
    if (typeof mermaid === 'undefined') { return; }
    var nodes = document.querySelectorAll('pre.mermaid');
    if (!mermaidSources.length) {
      nodes.forEach(function (node) { mermaidSources.push(node.textContent); });
    }
    nodes.forEach(function (node, i) {
      node.removeAttribute('data-processed');
      node.innerHTML = mermaidSources[i];
    });
    mermaid.initialize({
      startOnLoad: false,
      theme: (theme || currentTheme()) === 'dark' ? 'dark' : 'default',
      securityLevel: 'strict',
      fontFamily: '"Hiragino Sans", "Noto Sans JP", system-ui, sans-serif'
    });
    try { mermaid.run({ querySelector: 'pre.mermaid' }); } catch (e) {}
  }
  renderMermaid();

  var input = document.getElementById('search-input');
  var panel = document.getElementById('search-results');
  var index = window.__SEARCH_INDEX__ || [];
  var prefix = window.__SEARCH_PREFIX__ || '';

  function escapeHtml(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function excerpt(text, query) {
    var at = text.toLowerCase().indexOf(query.toLowerCase());
    if (at < 0) { return escapeHtml(text.slice(0, 120)); }
    var from = Math.max(0, at - 40);
    var slice = text.slice(from, from + 160);
    return escapeHtml(slice).replace(
      new RegExp(query.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&'), 'gi'),
      function (m) { return '<mark>' + m + '</mark>'; }
    );
  }

  function search(query) {
    if (!query || query.length < 1) { panel.hidden = true; return; }
    var q = query.toLowerCase();
    var hits = [];
    for (var i = 0; i < index.length && hits.length < 40; i++) {
      var entry = index[i];
      var inHeading = entry.heading.toLowerCase().indexOf(q) >= 0;
      var inText = entry.text.toLowerCase().indexOf(q) >= 0;
      if (inHeading || inText) { hits.push({ entry: entry, score: inHeading ? 0 : 1 }); }
    }
    hits.sort(function (a, b) { return a.score - b.score; });
    if (!hits.length) {
      panel.innerHTML = '<div class="empty">「' + escapeHtml(query) + '」に一致する箇所はありません</div>';
      panel.hidden = false;
      return;
    }
    panel.innerHTML = hits.map(function (h) {
      var e = h.entry;
      return '<a class="hit" href="' + prefix + e.url + '">' +
        '<span class="hit-head">' + escapeHtml(e.heading) + '</span> ' +
        '<span class="hit-page">' + escapeHtml(e.page) + '</span>' +
        '<span class="hit-text">' + excerpt(e.text, query) + '</span></a>';
    }).join('');
    panel.hidden = false;
  }

  if (input) {
    input.addEventListener('input', function () { search(this.value.trim()); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { this.value = ''; panel.hidden = true; this.blur(); }
    });
  }
  document.addEventListener('click', function (e) {
    if (panel && !panel.contains(e.target) && e.target !== input) { panel.hidden = true; }
  });
  document.addEventListener('keydown', function (e) {
    if ((e.key === '/' || (e.key === 'k' && (e.metaKey || e.ctrlKey))) && input) {
      if (document.activeElement !== input) { e.preventDefault(); input.focus(); }
    }
  });

  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  if (links.length && 'IntersectionObserver' in window) {
    var map = {};
    links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var a = map[entry.target.id];
        if (!a) { return; }
        if (entry.isIntersecting) {
          links.forEach(function (x) { x.classList.remove('active'); });
          a.classList.add('active');
        }
      });
    }, { rootMargin: '-80px 0px -70% 0px' });
    Object.keys(map).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) { observer.observe(el); }
    });
  }
})();
"""


def main(argv: list[str]) -> int:
    """引数を読み、サイトを作る。

        python tools/build_site.py            本編を site/ に作る
        python tools/build_site.py --profile ai   別冊を site/ai/ に作る
        python tools/build_site.py --all      本編と別冊の両方を作る
    """
    parser = argparse.ArgumentParser(description="docs/ の Markdown から静的サイトを作る")
    parser.add_argument(
        "--profile",
        default="main",
        choices=sorted(PROFILES),
        help="作るサイト。既定は本編（main）",
    )
    parser.add_argument("--all", action="store_true", help="本編と別冊の両方を作る")
    args = parser.parse_args(argv)

    # 本編を先に作る。別冊の出力先 site/ai/ は site/ の中にあるため、
    # 本編が site/ を作り直したあとに別冊を作らないと消える。
    targets = ["main", "ai"] if args.all else [args.profile]
    for name in targets:
        if len(targets) > 1:
            print(f"--- {name} ---")
        code = build(name)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""docs/ の Markdown から、Zensical で静的サイトを生成する。

    docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w \
      edocs-zensical python tools/build_site_zensical.py

既存の `tools/build_site.py` を置き換えるものではない。同じ `docs/` から、
別の道具で作った版を並べて比べるために置いている。どちらを残すかは未決である。

Zensical は `docs_dir` の中だけをサイトにする。本文には `../README.md` のように
`docs/` の外を指すリンクがある。そのままだと「page does not exist」の警告になり、
リンクも切れる。そこで `docs/` を `build/zensical/` に写しながら、外を指すリンクを
GitHub の URL に書き換える。写した側を Zensical に渡す。

サイトは、表示のために外部へ通信しない。Mermaid は `tools/vendor/mermaid.min.js`
を写して同梱する。書体は `zensical.toml` で `font = false` にして読み込ませない。

`tools/vendor/` は再取得できるため Git で追跡していない。サイトを作る前に
一度だけ `bash tools/fetch_vendor.sh` を実行する。
"""

from __future__ import annotations

import os
import posixpath
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BUILD = ROOT / "build" / "zensical"
SITE = ROOT / "site-zensical"
VENDOR = ROOT / "tools" / "vendor"
OVERRIDES = ROOT / "tools" / "zensical"
DIAGRAMS = ROOT / "diagrams" / "export"

# 飛び先の無いリンクの差し替え先。tools/build_site.py と同じ値にしている。
# fork したときは、両方を書き換える。
REPO_URL = "https://github.com/ht-0328/engineering-docs-standard"
REPO_BRANCH = "main"

# 本編のサイト。Zensical 版は比較用であり、正本ではない。
# その旨を最初のページに入れるために使う。
MAIN_SITE_URL = "https://ht-0328.github.io/engineering-docs-standard/"

# 最初のページの見出しの直後に差し込む断り書き。
# 写した側にだけ入れる。docs/ の正本は汚さない。
NOTICE = f"""
!!! warning "これは比較用の版である"

    このページは Zensical で作っている。**正本は [本編のサイト]({MAIN_SITE_URL}) にある。**
    どちらの道具を残すか決めるために、同じ内容を2つの方法で出している。
    決め方は [ADR-002](adr/ADR-002-site-generator.md) にある。
"""

# `](../path)` または `](../path#anchor)` を拾う。`../` で始まるものだけを見る。
# docs/ の中で閉じるリンクは Zensical が解決するため、触らない。
LINK = re.compile(r"\]\((\.\./[^)\s]+)\)")

# コードブロックの開始と終了。中にある例示リンクは書き換えない。
FENCE = re.compile(r"^\s{0,3}(```+|~~~+)")


def repo_file(repo_path: str) -> Path:
    """URL 上のパスを、手元のファイルの位置に戻す。"""
    return ROOT / urllib.parse.unquote(repo_path)


def repo_url(repo_path: str, anchor: str) -> str:
    """リポジトリ内のパスを、GitHub で読める URL に直す。"""
    kind = "tree" if repo_file(repo_path).is_dir() else "blob"
    url = f"{REPO_URL}/{kind}/{REPO_BRANCH}/{repo_path}"
    if anchor:
        url += "#" + anchor
    return url


def rewrite_links(text: str, rel: str, warnings: list[str]) -> str:
    """docs/ の外を指すリンクを、GitHub の URL に書き換える。

    `rel` は docs/ から見たこのファイルの位置である。`../` の解決に使う。
    `docs/adr/ADR-001-diagram-tool.md` の `../05-presentation.md` のように、
    `../` で始まっても docs/ の中に戻るものがある。これは書き換えない。
    """
    base = posixpath.dirname(rel)
    out: list[str] = []
    in_fence = False

    for line in text.splitlines(keepends=True):
        if FENCE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        out.append(LINK.sub(lambda m: replace(m, base, rel, warnings), line))

    return "".join(out)


def replace(match: re.Match[str], base: str, rel: str, warnings: list[str]) -> str:
    href = match.group(1)
    path, _, anchor = href.partition("#")

    # docs/ から見た飛び先。docs/ の中に戻るなら、そのままでよい。
    inside_docs = posixpath.normpath(posixpath.join(base, path))
    if not inside_docs.startswith("../"):
        return match.group(0)

    repo_path = posixpath.normpath(posixpath.join("docs", base, path))
    if not repo_file(repo_path).exists():
        warnings.append(f"{rel}: リンク先がリポジトリに無い: {href}")
    return f"]({repo_url(repo_path, anchor)})"


def add_notice(text: str) -> str:
    """最初の見出しの直後に、比較用であることの断り書きを入れる。

    写した側にだけ入れる。`docs/` の正本には入れない。
    すべてのページの下に出る断り書きは `zensical.toml` の `copyright` にある。
    ここは、最初のページに大きく出すためのものである。
    """
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.startswith("# "):
            return "".join(lines[: index + 1]) + NOTICE + "".join(lines[index + 1 :])
    return NOTICE + text


def stage() -> tuple[int, list[str]]:
    """docs/ を build/zensical/ に写し、リンクを書き換える。"""
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)

    warnings: list[str] = []
    count = 0
    for source in sorted(DOCS.rglob("*.md")):
        rel = source.relative_to(DOCS).as_posix()
        target = BUILD / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        body = rewrite_links(source.read_text(encoding="utf-8"), rel, warnings)
        if rel == "index.md":
            body = add_notice(body)
        target.write_text(body, encoding="utf-8")
        count += 1

    assets = BUILD / "assets"
    assets.mkdir()

    mermaid = VENDOR / "mermaid.min.js"
    if mermaid.exists():
        shutil.copy2(mermaid, assets / "mermaid.min.js")
    else:
        warnings.append("tools/vendor/mermaid.min.js が無い。図が記法のまま出る。"
                        "`bash tools/fetch_vendor.sh` を実行する")
    shutil.copy2(OVERRIDES / "mermaid-init.js", assets / "mermaid-init.js")

    if DIAGRAMS.exists():
        shutil.copytree(DIAGRAMS, BUILD / "diagrams", dirs_exist_ok=True)

    return count, warnings


def add_noindex() -> int:
    """生成したページに、検索避けの指示を入れる。

    本編と Zensical 版は同じ内容である。両方が検索結果に出ると、
    読者はどちらが正本か分からなくなる。**正本は本編の側である。**

    robots.txt は使えない。GitHub Pages のプロジェクトサイトでは、
    その置き場がドメインの直下にあり、このリポジトリからは触れない。
    そのため、ページごとに指示を入れる。
    """
    tag = '<meta name="robots" content="noindex, nofollow">'
    count = 0
    for page in SITE.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        if tag in text or "<head>" not in text:
            continue
        page.write_text(text.replace("<head>", "<head>\n    " + tag, 1), encoding="utf-8")
        count += 1
    return count


def main() -> int:
    count, warnings = stage()
    for message in warnings:
        print(f"警告: {message}")
    print(f"下ごしらえしたページ: {count}")
    print(f"下ごしらえの置き場: {BUILD}")

    # zensical の出力と混ざらないよう、ここまでの表示を先に流す。
    # 出力先が端末でないとき、Python はまとめて書き出すため、順番が入れ替わる。
    sys.stdout.flush()

    # zensical.toml が `mdslug.toc_slugify` を名前で読み込む。
    # tools/ を import の対象に入れておかないと、そこで失敗する。
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(ROOT / "tools"), env["PYTHONPATH"]] if env.get("PYTHONPATH") else [str(ROOT / "tools")]
    )

    # 引数はそのまま zensical に渡す。`--strict` を付けると警告で止まる。
    result = subprocess.run(
        ["zensical", "build", "-f", str(ROOT / "zensical.toml"), *sys.argv[1:]],
        cwd=ROOT,
        env=env,
    )
    if result.returncode != 0:
        return result.returncode

    pages = len(list(SITE.rglob("index.html")))
    print(f"生成したページ: {pages}")
    print(f"検索避けを入れたページ: {add_noindex()}")
    print(f"出力先: {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

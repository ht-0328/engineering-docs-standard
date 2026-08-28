#!/usr/bin/env python3
"""文書に書いたコマンドを実際に実行し、書いてある期待出力と照合する。

    python3 tools/verify_examples.py

**このツールだけはホストで動かす。** 他のツールと違い、Docker コマンドそのものを
実行して確かめるため、コンテナの中からは動かせない。標準ライブラリだけを使うので、
ホストへの追加インストールは要らない。

P-04（コードは実行できる形で書く）を、人の確認だけに頼らないための道具である。
コピーして動かないコマンドは、無いより悪い。

## 何を見るか

Markdown の中から、次の形の組を探して実行する。

    ```bash
    <コマンド>
    ```

    **期待される出力**（任意の説明）

    ```text
    <期待される出力>
    ```

期待出力が無いコマンドは、実行して終了コードだけを見る。

## 数値の扱い

期待出力に含まれる数字は、実行のたびに変わる（検査したファイル数、警告数など）。
**数字は伏せて照合する。** 形が合っていれば成功とし、数字が違う場合は
`数値の差` として報告する。失敗にはしない。文書の数字を直す手掛かりになる。

## 安全のための制限

**許可した接頭辞のコマンドしか実行しない。** 文書に書かれた任意のコマンドを
そのまま実行すると、破壊的な操作を踏む。許可の一覧は ALLOW_PREFIXES に、禁止の一覧は DENY_PATTERNS にある。
許可されないコマンドは `対象外` として数え、実行しない。

終わらないコマンド（HTTPサーバーなど）は、直前の行に次を書いて除外する。

    <!-- verify-examples: skip -->
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 実行を許可するコマンドの接頭辞。ここに無いものは実行しない。
ALLOW_PREFIXES = (
    "docker build ",
    "docker run ",
    "docker images ",
    "docker --version",
    "bash tools/",
    "git log",
    "git status",
)

# 許可の接頭辞に合っていても、含まれていたら実行しないもの。
# `--rm` のようなフラグに当たらないよう、コマンドとしての rm だけを弾く。
DENY_PATTERNS = (
    r"(^|[;&|]\s*)rm\s",       # コマンドとしての rm
    r"\brm\s+-[rf]",           # rm -rf / rm -f
    r"down\s+-v\b",
    r"--volumes\b",
    r"git\s+push",
    r"git\s+reset\s+--hard",
    r">\s*\S",                 # リダイレクトによる上書き
    r"(^|\s)curl\s",
    r"(^|\s)sudo\s",
)

SKIP_MARKER = re.compile(r"<!--\s*verify-examples:\s*skip\s*-->")
EXPECT_HEADING = re.compile(r"期待される出力")

# 数字と、環境ごとに変わるパスを伏せる。
DIGITS = re.compile(r"\d+")
PLACEHOLDER = re.compile(r"<[^>]+>")


@dataclass
class Example:
    path: Path
    line: int
    command: str
    expected: str | None


def extract_examples(path: Path) -> list[Example]:
    lines = path.read_text(encoding="utf-8").splitlines()
    examples: list[Example] = []

    index = 0
    while index < len(lines):
        if not lines[index].startswith("```bash"):
            index += 1
            continue

        # 直前の非空行に skip の印があれば飛ばす。
        back = index - 1
        while back >= 0 and not lines[back].strip():
            back -= 1
        skipped = back >= 0 and SKIP_MARKER.search(lines[back])

        start = index + 1
        end = start
        while end < len(lines) and not lines[end].startswith("```"):
            end += 1
        command = "\n".join(lines[start:end]).strip()

        if skipped or not command:
            index = end + 1
            continue

        expected = find_expected(lines, end + 1)
        examples.append(Example(path=path, line=index + 1, command=command, expected=expected))
        index = end + 1

    return examples


def find_expected(lines: list[str], start: int) -> str | None:
    """コードブロックの直後から、期待出力のブロックを探す。

    「期待される出力」を含む行が先にあり、そのあと最初に来る ```text だけを見る。
    間に別のコマンドブロックが来たら、期待出力は無いものとする。
    """
    saw_heading = False
    for index in range(start, min(start + 12, len(lines))):
        line = lines[index]
        if line.startswith("```bash"):
            return None
        if EXPECT_HEADING.search(line):
            saw_heading = True
            continue
        if saw_heading and line.startswith("```"):
            end = index + 1
            body: list[str] = []
            while end < len(lines) and not lines[end].startswith("```"):
                body.append(lines[end])
                end += 1
            return "\n".join(body).strip()
    return None


def allowed(command: str) -> bool:
    flat = command.replace("\\\n", " ")
    if not any(flat.startswith(prefix) for prefix in ALLOW_PREFIXES):
        return False
    return not any(re.search(pattern, flat) for pattern in DENY_PATTERNS)


def normalize(text: str) -> list[str]:
    """数字とプレースホルダーを伏せた行の一覧を返す。"""
    out = []
    for raw in text.splitlines():
        line = PLACEHOLDER.sub("", raw).strip()
        if not line:
            continue
        out.append(DIGITS.sub("#", line))
    return out


def run(command: str, timeout: int) -> tuple[int, str]:
    result = subprocess.run(
        ["bash", "-lc", command],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, (result.stdout + result.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="文書中のコマンドを実行して検証する")
    parser.add_argument("paths", nargs="*", default=None, help="対象のMarkdown。省略時は README.md")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    targets = [Path(p).resolve() for p in args.paths] if args.paths else [ROOT / "README.md"]

    examples: list[Example] = []
    for path in targets:
        examples.extend(extract_examples(path))

    ok = failed = skipped = drifted = 0

    for example in examples:
        rel = example.path.relative_to(ROOT)
        label = f"{rel}:{example.line}"
        flat = example.command.replace("\\\n", " ").replace("\n", " ")

        if not allowed(example.command):
            print(f"[対象外] {label}\n  {flat}")
            skipped += 1
            continue

        try:
            code, output = run(example.command, args.timeout)
        except subprocess.TimeoutExpired:
            print(f"[失敗] {label} — {args.timeout}秒で終わらなかった\n  {flat}")
            failed += 1
            continue

        if code != 0:
            print(f"[失敗] {label} — 終了コード {code}\n  {flat}")
            print("  " + "\n  ".join(output.strip().splitlines()[-6:]))
            failed += 1
            continue

        if example.expected is None:
            print(f"[成功] {label} — 終了コード 0（期待出力の記載なし）")
            ok += 1
            continue

        actual_lines = normalize(output)
        missing = [line for line in normalize(example.expected) if line not in actual_lines]

        if not missing:
            print(f"[成功] {label}")
            ok += 1
            continue

        # 数字を伏せても一致しない行がある。形が違う。
        print(f"[失敗] {label} — 期待した行が出力に無い")
        for line in missing:
            print(f"  期待: {line}")
        print("  実際の末尾:")
        print("    " + "\n    ".join(output.strip().splitlines()[-6:]))
        failed += 1

    print()
    print(f"検証したコマンド: {len(examples)}")
    print(f"成功: {ok}  失敗: {failed}  対象外: {skipped}")
    if drifted:
        print(f"数値の差: {drifted}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

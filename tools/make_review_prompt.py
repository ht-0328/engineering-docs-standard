#!/usr/bin/env python3
"""独立レビューに投げるプロンプトを、いまの本文から組み立てて出力する。

    python3 tools/make_review_prompt.py 1 | codex exec --skip-git-repo-check \
        --sandbox read-only -o reviews/2026-08-31-codex-raw-1.md -

**プロンプトをファイルとして保存しない。** 本文を複製することになり、
本文を直したそばから古くなるためである。毎回ここから作り直す。

レビュアーにファイルを読ませない。**本文をプロンプトに埋め込んで渡す。**
Codex はファイルを読ませると返ってこないことがあったため、この形にしている。

レビューの結果は `reviews/` に置く。既存の `reviews/2026-08-28-codex-review.md`
と同じ構成にまとめる。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 共通の指示。1番と2番で使う。
COMMON = """あなたは、この標準の独立レビュアーです。日本語で書いてください。

**ファイルを読む必要はありません。** 検査する本文は、このプロンプトの中にすべて貼ってあります。

## 見るところ

1. **言い過ぎ。** 出典が支えていない強さで書いている箇所。「必ず」「すべて」「決定的」などの断定が、示された根拠を超えていないか。
2. **矛盾。** 章のあいだ、規則のあいだで食い違っている箇所。
3. **自分の規則を守れていない箇所。** この別冊は次を自分に課しています。
   - `AD-01` 節はそれだけで意味が通る（前の節を読まないと分からない節が無いか）
   - `AD-03` 節をまたいで「これ」「上記の」「前者」を使わない
   - `AN-05` 確かめられる形で書く（曖昧で検証できない記述が無いか）
4. **数値と用語の不一致。** 同じ数値や用語が、場所によって違う値・違う表記になっていないか。
"""

# 3番だけ、見るところが違う。根拠の扱いを検算させる。
EVIDENCE = """あなたは、この標準の独立レビュアーです。日本語で書いてください。

**ファイルを読む必要はありません。** 検査する本文は、このプロンプトの中にすべて貼ってあります。

## 見るところ

この2つの文書は「根拠」を扱います。次の4点だけを見てください。

1. **実験の結論が、示された数値から言えるか。** 言い過ぎている箇所を挙げてください。特に「最も効く」といった表現が、8問・2モデル・材料1件という規模で言えるかどうか。
2. **数え方が一貫しているか。** 突き合わせの文書は「ベンダー文書は合わせて2出典分まで」という基準を置いています。**その基準が、8つの中核原則すべてに正しく当てはめられているか**を確かめてください。ベンダーに当たるのは X2・X3・X6・X7 と、X9 のうち OpenAI の部分です。**MCP・書籍・査読つき研究・自分の実測はベンダーではありません。**
3. **表の中の数値が、本文の記述と一致しているか。**
4. **実験の弱点が、正直に書かれているか。** 書かれていない弱点があれば挙げてください。
"""

TAIL = """
## 出力の形式

```
## 指摘

### [Major|Minor|Info] 指摘の見出し
- **場所**: 引用（該当する行をそのまま短く引用する）
- **問題**: 何が問題か
- **直し方**: どう直すか
```

## 厳守すること

- **貼られた本文についてだけ書く。** 貼られていない章を推測で評価しない。
- **指摘には必ず該当箇所の引用を付ける。**
- 感想を書かない。**問題を挙げるのが仕事です。**
- 問題が無いと判断した観点は「観点Nは問題なし」と1行で書く。
- 指摘が0件なら、そう書く。無理に作らない。

---

"""

# 何番のプロンプトに、どの文書を載せるか。
PARTS: dict[str, tuple[str, str, list[str]]] = {
    "1": (
        COMMON,
        "検査する本文（2章と3章）",
        ["docs-ai/02-ai-readable-docs.md", "docs-ai/03-instructions.md"],
    ),
    "2": (
        COMMON,
        "検査する本文（4章・5章・6章）",
        [
            "docs-ai/04-skills-and-agents.md",
            "docs-ai/05-both-readers.md",
            "docs-ai/06-verifying-ai-writing.md",
        ],
    ),
    "3": (
        EVIDENCE,
        "検査する本文（根拠の文書）",
        ["research/cross-reference-ai.md", "docs-ai/appendix-experiments.md"],
    ),
}


def build(part: str) -> str:
    head, title, files = PARTS[part]
    chunks = [head, TAIL, f"# {title}\n"]
    for rel in files:
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit(f"見つからない: {rel}")
        chunks.append(f"\n## ここから {rel}\n\n{path.read_text(encoding='utf-8')}")
    return "\n".join(chunks)


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0] not in PARTS:
        print(f"使い方: python3 tools/make_review_prompt.py {{{'|'.join(PARTS)}}}", file=sys.stderr)
        print("  1: 2章と3章   2: 4章・5章・6章   3: 根拠の文書", file=sys.stderr)
        return 1
    sys.stdout.write(build(argv[0]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

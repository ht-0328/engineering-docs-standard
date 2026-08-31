# SRC-AIEXT-002 Effective context engineering for AI agents（Anthropic）

## 出典

| 項目 | 内容 |
|---|---|
| 名称 | Effective context engineering for AI agents |
| 発行 | Anthropic（技術ブログ） |
| URL | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| 確認日 | 2026-08-31 |
| 確認方法 | 本文を直接取得した |
| 種別 | **ベンダーの技術文書。** 自社モデルの使い方を説く立場である |

## この出典の位置づけ

**「AIに何を渡すか」を設計の問題として扱った文書である。** 文の書き方ではなく、**渡す情報の総量と選び方**を扱う。

ベンダー文書であることに注意する。ただし、後述の「注意の予算」の主張は `SRC-AIEXT-005`（Chroma の実測）と独立に一致する。**利害の異なる2者が同じことを言っている点は評価できる。**

---

## 中心の主張

### 文脈は有限の資源である

> "LLMs have an 'attention budget' that they draw on when parsing large volumes of context."
> （LLMは大量の文脈を読むとき、「注意の予算」から引き出している）

理由として、変換器（transformer）の構造上、n個のトークンについて n² 通りの関係を扱うため、列が長くなるほど無理がかかると説明している。

そのうえで「context rot」に言及し、**文脈が長くなるとモデルの正答率が下がる**と述べている。

**これは `SRC-AIEXT-005` の実測と一致する。**

### context engineering の定義

> "the set of strategies for curating and maintaining the optimal set of tokens (information) during LLM inference"
> （推論のあいだ、最適なトークン（情報）の集合を選び、保つための一連のやり方）

**「集める」ではなく「選ぶ」である。** 全部渡すのではなく、選ぶことが仕事だと位置づけている。

---

## 指示文（system prompt）の書き方

### ちょうどよい高さ（right altitude）

指示は次の2つの間を狙う。

| 高すぎる | 低すぎる |
|---|---|
| 抽象的で、何をすべきか決まらない | 場合分けを固く書きすぎて、想定外で壊れる |

> "specific enough to guide behavior yet flexible enough"

### 節に分ける

> organizing prompts into "distinct sections (like `<background_information>`, `<instructions>`, `## Tool guidance`, `## Output description`, etc)"

**見出しで役割ごとに区切ることを推奨している。** 人向けの文書と同じ形（Markdownの見出し）でよいとしている点は重要である。

### 最小限にする

> "the minimal set of information that fully outlines your expected behavior"
> （期待する振る舞いを過不足なく示す、最小の情報の集合）

**「過不足なく」と「最小の」を同時に求めている。** 削ればよいのではない。

---

## 道具（tool）の説明文の書き方

> Tools should be "self-contained, robust to error, and extremely clear with respect to their intended use."
> （道具は、自己完結し、誤りに強く、意図した用途について極めて明確であるべきである）

避けるべきものとして次を挙げる。

> "bloated tool sets that cover too much functionality or lead to ambiguous decision points"
> （機能を盛り込みすぎ、判断が曖昧になる、膨らんだ道具の集合）

推奨は "a minimal viable set of tools"（最小限で用の足りる道具の集合）である。

---

## 必要になったときに読む（just in time）

全部を先に読ませるのではなく、**目印だけを持たせて、必要になったら読ませる**方式を勧めている。

> agents "maintain lightweight identifiers (file paths, stored queries, web links, etc.) and use these references to dynamically load data into context at runtime using tools."

**これは文書の書き方に直接効く。** ファイルの場所と名前が、それ自体で中身を予測できるものでなければ、この方式は成り立たない。

---

## この別冊で使える主張

| # | 主張 | 対応する原文 |
|---|---|---|
| 1 | AIに渡す情報は**選ぶもの**であり、集めるものではない | context engineering の定義 |
| 2 | 指示文は**役割ごとに見出しで区切る** | distinct sections |
| 3 | 指示は**具体的すぎても抽象的すぎてもいけない** | right altitude |
| 4 | 道具の説明文は**自己完結**させ、用途を明確にする | self-contained |
| 5 | 道具の数を絞る。多いと判断が曖昧になる | minimal viable set |
| 6 | 全部を先に渡さず、**目印を渡して必要時に読ませる** | just in time |
| 7 | 文脈が長くなると正答率が落ちる | attention budget / context rot |

## この出典の弱さ

- **数値が示されていない。** 「落ちる」とは言うが、どれだけ落ちるかは書いていない。数値は `SRC-AIEXT-005` から取る。
- 自社モデルを前提とした記述である。他社モデルでの検証は無い。
- 日本語は扱っていない。

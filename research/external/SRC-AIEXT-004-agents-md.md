# SRC-AIEXT-004 AGENTS.md — 道具をまたぐ指示書の形式

## 出典

| 項目 | 内容 |
|---|---|
| 名称 | AGENTS.md |
| 管理 | Agentic AI Foundation（Linux Foundation の傘下） |
| URL | https://agents.md/ |
| 確認日 | 2026-08-31 |
| 確認方法 | 本文を直接取得した |
| 種別 | **公開仕様。** 単一ベンダーのものではなく、複数社の協働から生まれ、財団が管理している |

## この出典の位置づけ

**この別冊の出典のうち、最も「標準」に近い。** OpenAI、Google をはじめ複数社の協働から生まれ、いまは Linux Foundation 傘下の財団が管理している。20を超えるAI開発道具が対応していると述べている。

`SRC-AIEXT-003`（Anthropic のスキル）が1社の製品仕様であるのに対し、こちらは**道具をまたぐ約束事**である。両者は対立しない。層が違う。

---

## 何を定めているか

### 目的

> "a simple, open format for guiding coding agents"

> "a README for agents: a dedicated, predictable place to provide the context and instructions to help AI coding agents work on your project."
> （エージェントのための README。プロジェクトで作業させるために必要な文脈と指示を置く、専用の、予測できる場所）

**「予測できる場所（predictable place）」が要点である。** 内容ではなく、置き場所を決めることに価値を置いている。

### README との住み分け

**この別冊にとって最も重要な一文である。**

> "README.md files are for humans: quick starts, project descriptions, and contribution guidelines"
> （README.md は人のためのものである。手早い始め方、プロジェクトの説明、貢献の手引き）

対して AGENTS.md は次を持つ。

> "the extra, sometimes detailed context coding agents need."
> （エージェントが必要とする、追加の、ときに詳細な文脈）

**読者ごとに文書を分けるという判断が、公開仕様として明文化されている。** 「人とAIの両方が読む一つの文書」を目指さない、という立場である。

### 置き場所と優先順位

- 基本は**リポジトリの根**に置く。
- 単一リポジトリに複数のプロジェクトがある場合は、入れ子にできる。

> "Agents automatically read the nearest file in the directory tree, so the closest one takes precedence."
> （エージェントはディレクトリの木の中で最も近いファイルを自動的に読む。したがって最も近いものが優先される）

### 形式

> "AGENTS.md is just standard Markdown. Use any headings you like; the agent simply parses the text you provide."

**必須の項目は無い。長さの上限も定めていない。** ここは `SRC-AIEXT-003`（`description` は1,024文字以内、本体は500行以内）と対照的である。

### よく使われる節

仕様が「よく選ばれるもの」として挙げるもの。

| 節 |
|---|
| プロジェクトの概要 |
| 組み立てと試験の命令 |
| コードの書き方の決まり |
| 試験のやり方 |
| 安全上の注意 |
| コミットメッセージや変更提案の決まり |

**いずれも「実行できる情報」である。** 設計思想や背景の説明は挙がっていない。

---

## この別冊で使える主張

| # | 主張 | 原文の裏づけ |
|---|---|---|
| 1 | **AIへの指示書は、人向けのREADMEと分ける** | "README.md files are for humans" |
| 2 | 指示書は**決まった名前で、決まった場所**に置く | "a dedicated, predictable place" |
| 3 | 近いところに置いた指示書が優先される。**適用範囲は場所で表す** | "the closest one takes precedence" |
| 4 | 指示書の中身は**実行できる情報**を中心にする | 推奨される節の一覧 |

---

## 確認できなかったこと・注意

- **CLAUDE.md との関係について、このページは何も述べていない。** 「CLAUDE.md の1行目に `@AGENTS.md` と書けばよい」という説明が広く出回っているが、**このページには無い。** 別の出典で裏を取る必要がある。
- **長さの推奨値（「300行以内」など）は、このページに無い。** 出回っている数値は非公式の目安である。
- 効果を測った結果は示されていない。

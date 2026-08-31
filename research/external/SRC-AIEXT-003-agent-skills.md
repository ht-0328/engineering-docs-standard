# SRC-AIEXT-003 Agent Skills — スキル定義の書き方（Anthropic 公式）

## 出典

| 項目 | 内容 |
|---|---|
| 名称 | Skill authoring best practices |
| 発行 | Anthropic（製品の公式文書） |
| URL | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| 確認日 | 2026-08-31 |
| 確認方法 | 本文を直接取得した |
| 種別 | **ベンダーの公式文書。** 特定製品（Claude）の仕様と指針である |

## この出典の位置づけ

**「AIに読ませる文書」の書き方について、数値つきの規定を持つ唯一の出典である。**

他の出典が「簡潔に」と言うところを、この文書は「500行以内」と言う。**根拠の質としては、製品仕様であるがゆえの強さと弱さの両方がある。** 守らないと動かない項目（文字数の上限）と、経験則にすぎない項目（500行）が混ざっているため、下では両者を分けて記録する。

---

## A. 仕様として決まっていること（守らないと動かない）

`SKILL.md` の冒頭（frontmatter）は2つの項目を必須とする。

| 項目 | 制約 |
|---|---|
| `name` | 64文字以内。英小文字・数字・ハイフンのみ。XMLタグ不可。予約語（`anthropic`、`claude`）不可 |
| `description` | 空でないこと。1,024文字以内。XMLタグ不可 |

## B. 指針（経験則。守らなくても動く）

| 指針 | 原文 |
|---|---|
| 本体は500行以内 | "Keep SKILL.md body under 500 lines for optimal performance" |
| 参照は1段階まで | "Keep references one level deep from SKILL.md" |
| 100行を超える参照先には目次を置く | "For reference files longer than 100 lines, include a table of contents at the top" |

---

## 中心の考え方: 文脈の窓は共有財である

> "The context window is a public good."

スキルは、指示文・会話の履歴・他のスキルの見出し情報・利用者の依頼と、同じ窓を分け合う。

### 段階的に開く（progressive disclosure）

読み込みは3段階になっている。

| 段階 | 何が読まれるか | いつ |
|---|---|---|
| 1 | すべてのスキルの `name` と `description` だけ | 起動時 |
| 2 | `SKILL.md` の本体 | そのスキルが関係すると判断されたとき |
| 3 | 参照先のファイル | 必要になったとき |

**この仕組みが、書き方を決める。** `description` は常に読まれるので、そこに「何をするか」と「いつ使うか」の両方が要る。本体は関係すると判断されてから読まれるので、判断のための情報を本体に書いても遅い。

### 「Claude はもう賢い」を既定とする

> "Only add context Claude doesn't already have."

各記述について次を問えとしている。

- この説明は本当に必要か。
- これは知っていると仮定してよいか。
- この段落はトークンの代価に見合うか。

文書には約50トークンの良い例と、約150トークンの悪い例が並べてある。悪い例は「PDFとは何か」「ライブラリとは何か」を説明していた。**一般知識の説明が、悪い例として名指しされている。**

---

## `description` の書き方

### 三人称で書く

> "**Always write in third person**. The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems."

| 判定 | 例 |
|---|---|
| 良い | "Processes Excel files and generates reports" |
| 避ける | "I can help you process Excel files" |
| 避ける | "You can use this to process Excel files" |

### 「何をするか」と「いつ使うか」の両方を書く

公式が挙げる良い例。

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

前半が「何をするか」、`Use when` 以降が「いつ使うか」である。

悪い例として挙がっているもの。

```yaml
description: Helps with documents
description: Processes data
description: Does stuff with files
```

**共通するのは、対象と場面が特定できないことである。**

### 名前の付け方

動名詞（-ing）を勧めている。

- 良い: `processing-pdfs`、`analyzing-spreadsheets`、`writing-documentation`
- 許容: `pdf-processing`（名詞句）、`process-pdfs`（動詞）
- 避ける: `helper`、`utils`、`tools`、`documents`、`data`、`files`

**避ける例に共通するのは、何にでも当てはまることである。**

---

## 指示の細かさを、作業の壊れやすさに合わせる

**この別冊で最も応用が利く考え方である。**

| 自由度 | 使う場面 | 書き方 |
|---|---|---|
| 高い | やり方が複数ある。文脈で決まる | 文章で方針だけ示す |
| 中くらい | 望ましい型がある。多少の幅は許す | 擬似コードや、引数つきの雛形 |
| 低い | 壊れやすい。順序が決まっている | 実行する命令をそのまま書く |

文書はこれを比喩で説明している。

- **両側が崖の細い橋**: 進み方は一つしかない。厳密な手すりと正確な指示を与える。
- **障害物のない広い野原**: 多くの道が成功に至る。方向だけ示して任せる。

低い自由度の例として挙がっている書き方。

```markdown
## Database migration

Run exactly this script:

python scripts/migrate.py --verify --backup

Do not modify the command or add additional flags.
```

---

## 内容についての規定

### 時点に依存する記述を入れない

悪い例として挙がっているもの。

```markdown
If you're doing this before August 2025, use the old API.
After August 2025, use the new API.
```

代わりに「現在の方法」を本文に置き、古い方法は折りたたんだ「古い型（Old patterns）」の節に入れることを勧めている。

**これは本編の O-03（時点に依存する語を使わない）と同じ規則である。** 人向けとAI向けで一致する数少ない規則である。

### 用語を統一する

> "Consistency helps Claude parse and follow instructions."

| 判定 | 例 |
|---|---|
| 良い | 常に "API endpoint"、常に "field"、常に "extract" |
| 悪い | "API endpoint" と "URL" と "API route" と "path" を混ぜる |

**これも本編の S-10（用語を統一する）と一致する。**

### 選択肢を並べない

> **Bad example: Too many choices** (confusing): "You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image, or..."

既定を1つ示し、例外の逃げ道を1つ添える形を勧めている。

### 例は抽象ではなく具体で示す

入力と出力の対を並べる形を勧めている。

> "Examples convey the desired style and level of detail to Claude more clearly than descriptions alone."

---

## 手順と検証の型

### 手順には確認欄を付ける

複雑な作業では、AIが写して進捗を印けるチェックリストを与えることを勧めている。

```markdown
Research Progress:
- [ ] Step 1: Read all source documents
- [ ] Step 2: Identify key themes
...
```

理由として "Clear steps prevent Claude from skipping critical validation" を挙げている。

### 検証の輪（feedback loop）を作る

> **Common pattern:** Run validator → fix errors → repeat

検証器はスクリプトでなくてもよい。文書（スタイルガイド）を検証器として使う例も挙げている。

---

## 評価を先に作る

> "**Create evaluations BEFORE writing extensive documentation.**"

順序が定められている。

1. スキル無しで代表的な作業をやらせ、失敗を記録する。
2. その失敗を突く評価を3件作る。
3. スキル無しの成績を測る（基準値）。
4. 評価を通る最小限の指示だけを書く。
5. 実行し、基準値と比べ、直す。

> "This approach ensures you're solving actual problems rather than anticipating requirements that may never materialize."

**「書いてから測る」ではなく「測ってから書く」である。** この別冊の実験の設計は、この順序に従う。

### 使う予定のモデルすべてで試す

> "What works perfectly for Opus might need more detail for Haiku."

---

## その他の規定

| 規定 | 理由 |
|---|---|
| 経路の区切りは `/` を使う。`\` を使わない | Unix系で壊れるため |
| MCP の道具は `サーバー名:道具名` の完全な形で書く | 前置きが無いと見つけられないことがあるため |
| 道具が入っている前提を置かない。導入手順を書く | — |
| ファイル名は中身が分かる名前にする（`doc2.md` ではなく `form_validation_rules.md`） | AIはファイル体系をたどって探すため |

---

## この別冊で使える主張

| # | 主張 | 種別 |
|---|---|---|
| 1 | 常に読まれる部分（見出し情報）と、必要時に読まれる部分を分けて書く | 仕組みからの帰結 |
| 2 | 説明文には「何をするか」と「いつ使うか」の両方を書く | 公式の指針 |
| 3 | 説明文は三人称で書く | 公式の指針 |
| 4 | 一般知識の説明を書かない | 公式の指針 |
| 5 | 指示の細かさを、作業の壊れやすさに合わせる | 公式の指針 |
| 6 | 選択肢を並べず、既定を1つ示す | 公式の指針 |
| 7 | 用語を統一する | 公式の指針 |
| 8 | 時点に依存する記述を入れない | 公式の指針 |
| 9 | 名前は中身が分かるものにする。汎用の名前を避ける | 公式の指針 |
| 10 | 評価を先に作り、測ってから書く | 公式の指針 |
| 11 | 参照は1段階までにする | 経験則 |
| 12 | 100行を超える参照先には目次を置く | 経験則 |

## この出典の弱さ

- **1社の製品文書である。** 他社のAIに同じことが当てはまる保証は無い。
- 500行、100行、1段階といった数値の**根拠が示されていない**。測定結果は載っていない。
- 日本語での検証は無い。

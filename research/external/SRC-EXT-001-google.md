# SRC-EXT-001 Google developer documentation style guide / Google Technical Writing Courses

## 出典

| 項目 | 内容 |
|---|---|
| 名称 | Google developer documentation style guide、Google Technical Writing Courses |
| 発行元 | Google |
| 種別 | 公開スタイルガイド、公開教材 |
| 確認日 | 2026-08-28 |
| 確認方法 | 各ページを直接取得して本文を読んだ |

## この出典の位置づけ

英語圏で最も広く参照される開発者向け文書のスタイルガイドである。規則が短い命令文で書かれ、各規則に推奨例と非推奨例が付く。**規則そのものより、規則の書き方が参考になる。**

日本語の文書にそのまま適用できない規則もある（冠詞、大文字小文字など）。**採用するのは、言語に依存しない構造と情報設計の規則に限る。**

---

## 数値基準

出典全体で数値が示されているのは段落の長さだけである。**文の長さに数値基準は無い。**

| 対象 | 基準 | 原文 | 出典URL |
|---|---|---|---|
| 段落の文数 | 3〜5文が歓迎される。7文を超えると読者は避ける | "Readers generally welcome paragraphs containing three to five sentences, but will avoid paragraphs containing more than about seven sentences." | https://developers.google.com/tech-writing/one/paragraphs |
| 表のセル | 2文を超えたら別の形式を検討する | "If a table cell holds more than two sentences, ask yourself whether that information belongs in some other format." | https://developers.google.com/tech-writing/one/lists-and-tables |
| 文の長さ | 数値基準なし。「1文1アイデア」で判断する | "Focus each sentence on a single idea, thought, or concept." | https://developers.google.com/tech-writing/one/short-sentences |

**これは重要な発見である。** 英語圏の代表的な出典は、文の長さを字数で縛らず、**内容の単位で縛っている。**

---

## 抽出した規則

### 文と段落

| # | 規則 | 原文 | 出典URL |
|---|---|---|---|
| G-01 | 1つの文には1つの考えだけを入れる | "Focus each sentence on a single idea, thought, or concept." | tech-writing/one/short-sentences |
| G-02 | 接続詞や埋め込みリストを見つけたら、長い文を箇条書きに変換する | "Convert some long sentences to lists" | 同上 |
| G-03 | 冗長な言い回しを短い語に置き換える | "at this point in time" → "now"、"provides a detailed description of" → "describes" | 同上 |
| G-04 | 段落の最初の一文が最も重要である。忙しい読者はそこだけを読む | "The opening sentence is the most important sentence of any paragraph. Busy readers focus on opening sentences and sometimes skip over subsequent sentences." | tech-writing/one/paragraphs |
| G-05 | 段落は独立した論理の単位にする | "represent an independent unit of logic" | 同上 |
| G-06 | 良い段落は3つの問いに答える | 何を伝えているか / なぜ読者が知る必要があるか / 読者はそれをどう使い、どう検証するか | 同上 |

### 語

| # | 規則 | 原文 | 出典URL |
|---|---|---|---|
| G-07 | 新しい用語は定義する。定義が多いなら用語集にまとめる | "Define the term. If your document is introducing many terms, collect the definitions into a glossary" | tech-writing/one/words |
| G-08 | 同じ概念には同じ語を最後まで使う | "the same unambiguous word or term consistently throughout your document" | 同上 |
| G-09 | 略語は初出でフルスペルを書き、括弧に略語を入れる | "Spell out the full term, and then put the acronym in parentheses." | 同上 |
| G-10 | 数回しか使わない略語は定義しない。**略語を使うこと自体をやめる** | "Don't define acronyms used only a few times" | 同上 |
| G-11 | 指示語（it、this、that、they）は、指す名詞から5語以上離れたら名詞を繰り返す | "If five or more words separate the noun from the pronoun, repeat the noun" | 同上 |
| G-12 | 専門用語（jargon）は、読者がその語で検索する場合にだけ価値がある | "It can be valuable to include jargon in a document when you know that readers search for those terms." | style/jargon |
| G-13 | 専門用語を使うなら、初出で平易な説明を括弧で添えるか、信頼できる定義にリンクする | "Briefly describe the term in parentheses on first reference, or link to a trusted definition" | 同上 |

### 態と主語

| # | 規則 | 原文 | 出典URL |
|---|---|---|---|
| G-14 | 能動態を使う。誰が動作しているかを明示する | "Use active voice: make clear who's performing the action" | style/highlights |
| G-15 | 受動態は読者に変換作業を強いる | "Most readers mentally convert passive voice to active voice" | tech-writing/one/active-voice |
| G-16 | 受動態は動作主を消してしまうことがある | 動作主が消えると、読者は推測を強いられる | 同上 |

受動態の見分け方は `be動詞 + 過去分詞` である。後ろに `by` が続くことが多い。

### 見出し

| # | 規則 | 原文 | 出典URL |
|---|---|---|---|
| G-17 | 作業の見出しは動詞の原形で始める | "For a task-based heading, start with a bare infinitive"（例: Create an instance） | style/headings |
| G-18 | 概念の見出しは名詞句にする。`-ing` で始めない | "use a noun phrase that doesn't start with an -ing verb" | 同上 |
| G-19 | 見出しに句読点が増えたら、見出しが複雑すぎる兆候である | "Punctuation can be a sign that your heading is too complicated." | 同上 |
| G-20 | 見出しの階層を飛ばさない。h3はh2の下にだけ置く | "Don't skip levels of the heading hierarchy." | 同上 |
| G-21 | 空の見出しを作らない。見出しの直後には必ず本文を置く | "Don't use empty headings. Make sure headings are followed by content" | 同上 |
| G-22 | 見出しに番号を振って順序を示さない | "Don't use numbers in headings to indicate a sequence of sections" | 同上 |
| G-23 | 見出しにリンクを置かない | "Don't put links in headings." | 同上 |
| G-24 | h1はページに1つだけ置く | "only use a level-1 heading once on a page" | 同上 |

### 箇条書きと表

| # | 規則 | 出典URL |
|---|---|---|
| G-25 | 順序に意味があるなら番号付き、無いなら黒丸を使う | style/highlights、tech-writing/one/lists-and-tables |
| G-26 | 箇条書きの項目は、文法・論理カテゴリ・大文字小文字・句読点をそろえる（並列性） | 同上 |
| G-27 | 最初の項目が読者の期待する型を決める。以降はその型に従う | "The first item in a list establishes a pattern that readers expect to see repeated in subsequent items." | 同上 |
| G-28 | 番号付きリストの各項目は命令形の動詞で始める | 同上 |
| G-29 | 箇条書きと表の直前に、コロンで終わる導入文を置く | 同上 |

### リンク

| # | 規則 | 原文 | 出典URL |
|---|---|---|---|
| G-30 | リンク文字列は、周囲の文が無くても意味が通るようにする | "Write link text that makes sense without the surrounding text." | style/link-text |
| G-31 | `this document`、`this article`、`click here` を使わない | "Don't use phrases such as _this document_, _this article_, or _click here_." | 同上 |
| G-32 | URLそのものをリンク文字列にしない。ページ名か内容の説明を使う | "In general, don't use a URL as link text." | 同上 |

### 古びない書き方

| # | 規則 | 出典URL |
|---|---|---|
| G-33 | 時点に依存する語を書かない | style/timeless-documentation |

避けるべき語の一覧（原文）: `as of this writing`、`currently`、`does not yet`、`eventually`、`existing`、`future, in the future`、`latest`、`new, newer`、`now`、`old, older`、`presently, at present`、`soon`

原則の記述は次のとおりである。

> "Timeless documentation focuses on how the product works right now—not on how it has changed from previous versions, and not how it might change in the future."

### その他の主要な規則（highlights より）

- 二人称（you）を使う。`we` を使わない。
- 文書のタイトルと見出しはセンテンスケースにする。
- **条件は指示の前に置く。後ろに置かない**（"Put conditions before instructions, not after"）。
- 曖昧でない日付形式を使う。
- 画像には代替テキストを付ける。
- 未発表の機能を予告しない。

---

## Before / After の実例（原文のまま）

### 例1: 長い文を分ける（G-01）
- Not recommended: "The late 1950s was a key era for programming languages because IBM introduced Fortran in 1957..."
- Recommended: "The late 1950s was a key era for programming languages. IBM introduced Fortran in 1957..."

### 例2: 長い文を箇条書きにする（G-02）
- Not recommended: "To alter the usual flow of a loop, you may use either a break statement...or a continue statement..."
- Recommended: 箇条書きに変換し、各項目に説明を付ける。

### 例3: 受動態を能動態にする（G-15）

| Passive | Active |
|---|---|
| Code is interpreted by Python, but code is compiled by C++ | Python interprets code, but C++ compiles code |
| The flags weren't parsed by the Mungifier | The Mungifier didn't parse the flags |
| A wrapper is generated by the Op registration process | The Op registration process generates a wrapper |

### 例4: 曖昧な指示語（G-11）
- Before: "Python is interpreted, while C++ is compiled. **It** has an almost cult-like following."
- 問題: `It` が Python と C++ のどちらを指すか読者にはわからない。

- Before: "Running the process configures permissions and generates a user ID. **This** lets users authenticate."
- After: "**This user ID** lets users authenticate."

### 例5: 並列性の崩れ（G-26）
- Nonparallel:
  - Broccoli inspires feelings of love or hate.
  - Potatoes taste delicious.
  - Cabbages.
- 問題: 3つ目だけが完全な文になっていない。

### 例6: 番号付きリストの動詞（G-28）
- Weak:
  1. Instantiate the Froobus class.
  2. Invoke the Froobus.Salmonella() method.
  3. The process stalls.
- Strong:
  1. Stop Frambus.
  2. Open the key configuration file.
- 問題: Weak の3つ目は指示ではなく状態の説明であり、リストの型が崩れている。

### 例7: 古びる語を消す（G-33）
- Not recommended: "These **new** subcommands let you interact with HTTP load balancing."
- Recommended: "These subcommands let you interact with HTTP load balancing."

- Not recommended: "The following command-line options aren't **currently** supported:"
- Recommended: "The following command-line options aren't supported:"

### 例8: リンク文字列（G-31）
- Not recommended: "See [this blog post](...)"
- Recommended: "For more information, see [Load balancing and scaling](...)"

---

## この標準に取り込む点

1. **文の長さを字数で縛る前に、「1文1アイデア」を先に置く。** 字数はその結果として決まる。
2. **段落は3〜5文、7文を超えない。** 日本語でも認知の負荷は同じ構造なので、目安として採用する。
3. **見出しの機械的な規則**（階層を飛ばさない、空見出しを作らない、リンクを置かない、番号を振らない）は、そのまま自動チェックできる。
4. **「条件は指示の前に置く」** は日本語でも有効で、手順書の品質に直結する。
5. **古びる語の一覧**は、日本語版（「現在」「今後」「最新」「新しい」「近日」）を作って自動チェックに載せる。
6. **専門用語の判断基準**が「読者がその語で検索するか」である点は、依頼者の「横文字が嫌い」という直感を検証する材料になる。

## 取り込まない点

- 冠詞、大文字小文字、シリアルカンマなど英語固有の規則。
- 二人称の使用。日本語では主語を省く方が自然な場合があり、別に検討する。

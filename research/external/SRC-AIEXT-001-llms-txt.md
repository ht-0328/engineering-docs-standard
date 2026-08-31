# SRC-AIEXT-001 llms.txt — サイトがAIに向けて置く案内ファイル

## 出典

| 項目 | 内容 |
|---|---|
| 名称 | The /llms.txt file |
| 提案者 | Jeremy Howard（Answer.AI / fast.ai） |
| URL | https://llmstxt.org/ |
| 初出 | 2024-09-03。第2版は 2026-08-10 |
| 確認日 | 2026-08-31 |
| 確認方法 | 本文を直接取得した |
| 種別 | **個人による提案。標準化団体の承認は受けていない。** |

## この出典の位置づけ

**「AIに読ませる文書」を、ファイルの形で定めた最初の広まった提案である。**

規格としての強さは弱い。RFC でも W3C でもない。しかし、何を決めているかを見ると、**AI向けの文書設計の考え方がそのまま形になっている。** そこに価値がある。

---

## 何を定めているか

サイトの根（または任意の階層）に `/llms.txt` という Markdown ファイルを置く。

> "We propose adding a `/llms.txt` markdown file to websites to provide LLM-friendly content."

### ファイルの構造

順序が決められている。

| # | 要素 | 必須か |
|---|---|---|
| 1 | バイト順の印（BOM） | 任意 |
| 2 | **h1 見出し**（プロジェクト名やサイト名） | **唯一の必須要素** |
| 3 | 引用（`>`）による要約 | 任意。推奨 |
| 4 | 見出しを含まない任意の節 | 0個以上 |
| 5 | h2 で区切られたリンクの一覧 | 0個以上 |

リンクの一覧はこの形で書く。

```markdown
## 節の名前

- [名前](URL): 補足の説明
```

`[名前](URL)` の部分は必須で、`:` 以降の説明は任意である。

### `Optional` という予約された節

慣例として `Optional` という名前の h2 を置ける。

> "secondary information: links an agent can skip when shorter context is needed."
> （二次的な情報。文脈を短くしたいとき、エージェントが飛ばしてよいリンク）

**「削ってよい部分を、書き手が先に指定しておく」という考え方である。** 人向けの文書には無い発想である。

---

## なぜ Markdown なのか

提案は2つの理由を挙げる。

### 1. モデルが最もよく理解する形式である

> "At the moment the most widely and easily understood format for language models is Markdown."

**「いま最も」と時点を限っていることに注意する。** この主張は将来変わりうる。

### 2. 人も機械も読める

> "llms.txt markdown is human and LLM readable, but is also in a precise format allowing fixed processing methods."
> （llms.txt の Markdown は人もLLMも読めるが、同時に、決まった処理ができる正確な形式でもある）

### 3. トークンが費用である

> "every wasted token costs time and money. Agents are best served by concise, expert-level information gathered in a single, accessible location."
> （無駄なトークンはすべて時間と金を食う。エージェントに最も役立つのは、簡潔で専門家向けの情報が、たどり着ける一か所にまとまっていることである）

**「簡潔で、専門家向け」という指定が重要である。** 人向けの入門的な説明は、AI向けには冗長になる。

---

## この別冊で使える主張

| # | 主張 | 原文の裏づけ |
|---|---|---|
| 1 | AI向けの入口は、**一か所にまとめる** | "a single, accessible location" |
| 2 | AI向けの記述は**簡潔で専門家向け**にする。入門的な言い換えを入れない | "concise, expert-level information" |
| 3 | **飛ばしてよい部分を書き手が指定する** | `Optional` 節の規定 |
| 4 | 形式は Markdown を使う | "the most widely and easily understood format" |
| 5 | リンクには**行き先の説明を添える** | `: Optional link details` の規定 |

---

## 確認できなかったこと

- **`llms-full.txt` について、この仕様書は何も書いていない。** 各社の文書生成サービスが独自に使っている呼び名であり、この提案の一部ではない。
- 採用状況の統計はこのページには無い。
- **効果を測った結果は示されていない。** この提案は測定ではなく設計の提案である。

## この出典の弱さ

**個人の提案であり、実測の裏づけを持たない。** この別冊では、llms.txt を「そうすべき根拠」としてではなく、「AI向け文書の設計の考え方を示す例」として扱う。単独では中核原則の根拠にしない。

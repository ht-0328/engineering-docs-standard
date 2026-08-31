# SRC-AIEXT-009 道具（ツール）の説明文の書き方 — MCP と OpenAI

## 出典

| 名称 | URL | 確認日 | 種別 |
|---|---|---|---|
| Model Context Protocol 仕様（Tools） | https://modelcontextprotocol.io/ | 2026-08-31 | 公開仕様 |
| OpenAI Function calling ガイド | https://developers.openai.com/api/docs/guides/function-calling | 2026-08-31 | ベンダーの公式文書 |

**調べ方**: Antigravity(agy) に調べさせ、**OpenAI の主要な5点は私（Claude）が原文で確認した。** 5点とも原文にあった。

## この出典の位置づけ

**道具の説明文は、AIだけが読む文書である。** 人向けの文書術がまったく通用しない、最も純粋な「AI向けの文書」である。

`SRC-AIEXT-003`（Anthropic のスキル）と合わせると、**3者（Anthropic、OpenAI、MCP）の指針を比べられる。** 一致するところは強い根拠になり、食い違うところは条件つきで書ける。

---

## MCP が定めていること

### 道具の定義に含めるもの

| 項目 | 内容 |
|---|---|
| `name` | 道具を一意に指す名前 |
| `title` | （任意）人に見せる名前 |
| `description` | 機能を人が読んで分かる説明文 |
| `inputSchema` | 受け取る引数を定める JSON Schema |
| `outputSchema` | （任意）返すものの構造 |
| `annotations` | （任意）振る舞いの性質 |

### 名前の制約

仕様は `SHOULD`（そうすべき）として次を定める。

- 長さは1〜128文字。
- 大文字と小文字を区別する。
- 使ってよい文字は英字・数字・`_`・`-`・`.` だけ。
- 空白やカンマを含めない。
- 1つのサーバーの中で一意にする。

### 名前がぶつかったとき

> "Clients or proxies that aggregate tools from multiple servers **MAY** encounter naming collisions (for example, two servers each exposing a `search` tool) and **SHOULD** implement a disambiguation strategy such as prefixing tool names with a server identifier."

**`search` のような一般的な名前は、他とぶつかる。** サーバー名を前に付けて区別することを勧めている。

これは `SRC-AIEXT-003` の「MCP の道具は `サーバー名:道具名` の完全な形で書く」と同じ問題への、両側からの対処である。

### 説明文がどう使われるか

道具の実行は「モデルが決める（Model-Controlled）」。手順は次のとおりである。

1. 道具の一覧（`name`、`description`、`inputSchema`）を取得する。
2. それをモデルの文脈に渡す。
3. **モデルは利用者の意図と各 `description` を照らし合わせて、道具を選ぶ。**

**つまり `description` は、選ばれるかどうかを決める。** 機能の説明ではなく、選択のための文である。

---

## OpenAI の公式指針（原文で確認ずみ）

### 1. 名前・引数の説明・指示を、明確かつ詳しく書く

- 関数の目的、各引数の目的と形式、出力が何を表すかを**明示的に**書く。
- **いつ使うか（そして、いつ使わないか）は、システムプロンプトに書く。**

> "Use the system prompt to describe when (and when not) to use each function."

- 具体例と境界の場合を入れる。**ただし注意がある。**

> "Adding examples may hurt performance for reasoning models."
> （推論するモデルでは、例を足すと性能を損なうことがある）

### 2. ソフトウェア設計の作法を当てはめる

- 関数を自明で直感的にする（最小驚きの原則）。
- 列挙型や構造を使い、**無効な状態を表現できないようにする。** 悪い例として `toggle_light(on: bool, off: bool)` を挙げている。
- **新人の試験（intern test）を通す。**

> "Can an intern/human correctly use the function given nothing but what you gave the model? (If not, what questions do they ask you? Add the answers to the prompt.)"
> （モデルに与えたものだけで、新人が正しくその関数を使えるか。使えないなら、その人は何を聞いてくるか。その答えをプロンプトに足す）

**これはこの別冊で最も使える判定基準である。** 「AI向けに十分か」を、人を使って測れる形にしている。

### 3. モデルの負担を減らし、できるところはコードでやる

- **すでに分かっている引数を、モデルに埋めさせない。**
- 常に続けて呼ばれる関数は、1つにまとめる。

### 4. 最初に見せる関数の数を少なくする

> "Aim for fewer than 20 functions available at the start of a turn at any one time."
> （一度に、ターンの開始時点で使える関数は20個未満を目指す）

原文は "though this is just a soft suggestion"（あくまで緩い提案である）と付け加えている。

### 5. 説明文はトークンを食い、課金される

> "functions are injected into the system message...callable function definitions count against the model's context limit and are billed as input tokens."

対処として、関数の数を絞る、**説明文を短くする**、必要になるまで読み込まない、の3つを挙げている。

---

## 3者の食い違い

**同じ問いに違う答えを出している点である。この別冊では、両論と条件を書く。**

### 食い違い1: 「いつ使うか」をどこに書くか

| 出典 | 立場 |
|---|---|
| Anthropic（スキル） | **`description` の中に書く。** 「何をするか」と「いつ使うか」の両方を入れることを必須としている |
| OpenAI | **システムプロンプトに書く。** `description` には目的と引数を書く |

**理由が違う。** Anthropic のスキルは、`description` だけが常時読まれる仕組みである。だから選択の手がかりをそこに置くしかない。OpenAI の関数定義は、システムメッセージに一括で入る。だから分けられる。

**仕組みが違えば、置き場所も変わる。** 「どちらが正しいか」ではない。

### 食い違い2: 例を入れるか

| 出典 | 立場 |
|---|---|
| Anthropic | 例を入れることを勧める。「例は説明よりも明確に伝わる」 |
| OpenAI | 入れてよい。**ただし推論するモデルでは性能を損なうことがある** |

**どちらも実測は示していない。**

### 一致していること

| 一致点 | Anthropic | OpenAI | MCP |
|---|---|---|---|
| 道具の数を絞る | ● | ●（20個未満） | — |
| 名前を具体的にする。一般的な名前を避ける | ● | ● | ●（ぶつかるため） |
| 説明文はトークンを食う。短くする | ● | ● | — |
| 使わないものは後から読み込む | ●（段階的な開示） | ●（tool search） | ●（動的な取得） |

**3者が一致する4点は、この別冊の中核原則にできる。**

---

## この別冊で使える主張

| # | 主張 | 支持 |
|---|---|---|
| 1 | 道具の数を絞る。多いと選択を誤る | Anthropic、OpenAI |
| 2 | 名前は具体的にする。`search` のような一般名を避ける | 3者すべて |
| 3 | 説明文は選択のための文である。機能の説明ではない | MCP、Anthropic |
| 4 | 使わないものは後から読み込む | 3者すべて |
| 5 | **新人が読んで使えるかで判定する** | OpenAI |
| 6 | 無効な状態を表現できない形にする | OpenAI |
| 7 | すでに分かっていることを書かせない | OpenAI |

## この出典群の弱さ

- **どれも実測を示していない。** 20個という数値も「緩い提案」と断られている。
- 日本語での検証は無い。
- 仕様は変わる。MCP の仕様は日付つきの版で管理されている。

# SRC-EXT-006 規範語（RFC 2119 / 8174）、決定記録（ADR）、平易な言葉

3つの小さな出典をまとめている。いずれも単独では1ファイルにするほどの分量がないが、この標準の骨組みに使う。

---

## 1. RFC 2119 / RFC 8174 — 規範の強さを表す語

### 出典

| 項目 | 内容 |
|---|---|
| 名称 | RFC 2119（BCP 14）、RFC 8174 |
| 発行元 | IETF |
| URL | https://datatracker.ietf.org/doc/html/rfc2119 、 https://datatracker.ietf.org/doc/html/rfc8174 |
| 確認日 | 2026-08-28 |

### この出典の位置づけ

**ルールの強さを言葉で区別する方法を与える。** これが無いと、標準に書かれた全項目が同じ重みに見え、守れないルールが放置される。

### 定義（原文のまま）

| 語 | 定義 |
|---|---|
| MUST / REQUIRED / SHALL | "the definition is an absolute requirement of the specification." |
| MUST NOT / SHALL NOT | "the definition is an absolute prohibition of the specification." |
| SHOULD / RECOMMENDED | "there may exist valid reasons in particular circumstances to ignore a particular item, but the full implications must be understood and carefully weighed before choosing a different course." |
| SHOULD NOT / NOT RECOMMENDED | "there may exist valid reasons in particular circumstances when the particular behavior is acceptable or even useful, but the full implications should be understood and the case carefully weighed before implementing any behavior described with this label." |
| MAY / OPTIONAL | "an item is truly optional." |

### 見落とされやすい2つの注意

**注意1: 規範語は控えめに使う。**

> "Imperatives of the type defined in this memo must be used with care and sparingly. In particular, they MUST only be used where it is actually required for interoperation or to limit behavior which has potential for causing harm"

**すべての項目を MUST にしてはいけない。** MUST は、守らないと実害が出るものに限る。

**注意2: 大文字のときだけ、この意味になる（RFC 8174）。**

> "The words have the meanings specified herein only when they are in all capitals. When these words are not capitalized, they have their normal English meanings and are not affected by this document."

### この標準への適用

日本語の標準なので、英語の大文字をそのまま使うか、日本語の語を使うかを決める必要がある。**この標準では次の3語を使い、意味を RFC 2119 に合わせる。**

| この標準の語 | 対応 | 意味 |
|---|---|---|
| **必須** | MUST | 守らないと読者に実害が出る。例外を認めない |
| **推奨** | SHOULD | 原則守る。外すなら理由を文書に残す |
| **任意** | MAY | 状況によって選んでよい |

RFC 2119 の趣旨に従い、**必須は最小限にする。** 数が多い標準は守られない。

---

## 2. Architecture Decision Records（ADR）

### 出典

| 項目 | 内容 |
|---|---|
| 名称 | Architectural Decision Records |
| URL | https://adr.github.io/ |
| 確認日 | 2026-08-28 |

### 定義（原文のまま）

> "An Architectural Decision (AD) is a justified design choice that addresses a functional or non-functional requirement that is architecturally significant."
>
> "An Architectural Decision Record (ADR) captures a single AD and its rationale; the collection of ADRs created and maintained in a project constitute its decision log."

要点は3つである。

1. **1レコードに1つの決定だけを書く。**
2. **決定だけでなく、その理由（rationale）を書く。**
3. **積み重ねたADRが決定ログになる。**

さらに、適用範囲を設計に限らないと明言している。

> "ADR usage can be extended to design and other decisions ('any decision record')."

### この標準への適用

- **文書型テンプレートの1つとして ADR を入れる。**
- **この標準自身の決定を ADR で残す。** 最初の1件は「図をどの方式で作るか」である（`docs/adr/ADR-001-diagram-tool.md`）。標準がADRを勧めるなら、標準自身がADRを持っているべきである。

---

## 3. 平易な言葉（Plain language）

### 出典

| 項目 | 内容 |
|---|---|
| 名称 | Plain language guide series（旧 plainlanguage.gov、現 digital.gov） |
| 発行元 | U.S. General Services Administration |
| URL | https://digital.gov/guides/plain-language |
| 確認日 | 2026-08-28 |

### 確認できたこと

> "Plain language – content that is clear and easy to understand – is critical to helping the public to make sense of their obligations and benefits. (中略) Not only is plain language more efficient and effective. It is also the law."

- 米国では **Plain Writing Act of 2010** により、公衆向けの文書を対象読者に合わせて書くことが**法的要件**になっている。
- 「平易に書くこと」は好みではなく、制度として要求されている領域がある。

確認できた具体的な規則は次のとおりである。

| 規則 | 原文 |
|---|---|
| 能動態を使う | "Active voice makes it clear who should do what." 例: "Not 'It must be done,' but 'You must do it.'" |
| 現在形を使う | "The present tense makes your writing simpler, more direct, and more forceful." |
| 動詞を隠さない | 名詞化（`-ment`、`-tion`、`-sion`、`-ance`）を避け、動詞のまま使う |
| 短い語を使う | "Shorter words" |
| 節を短くする | "Short sections" |

### 確認できなかったこと

**旧 plainlanguage.gov の詳細ページ（`/guidelines/concise/` など）は現在すべて digital.gov のポータルへリダイレクトされ、個別の本文を取得できなかった。** Antigravity(agy) にも独立に確認させたが、同じ結果だった。

したがって、**「文は何語以内」といった数値基準を、この出典から引くことはできない。** 原文は GitHub のアーカイブに残っているとポータルに記載があるため、必要になった時点で追加調査する。

### この標準への適用

**依頼者の「難しい言葉が嫌い」という直感を支える、制度レベルの根拠として使う。** ただし数値は引けないため、判断基準は他の出典（`SRC-EXT-001` の専門用語の扱い、`SRC-EXT-003` のひらがな開き）に依拠する。

「動詞を隠さない」は日本語にもそのまま効く。「〜の実施を行う」より「〜を実施する」、「〜の検討が必要である」より「〜を検討する」の方が短く、動作主も明確になる。

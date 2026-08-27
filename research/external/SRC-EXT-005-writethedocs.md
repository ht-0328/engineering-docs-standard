# SRC-EXT-005 Write the Docs — ドキュメントの原則と docs as code

## 出典

| 項目 | 内容 |
|---|---|
| 名称 | Software documentation guide — Write the Docs |
| 発行元 | Write the Docs community |
| URL | https://www.writethedocs.org/guide/ 、 `/guide/docs-as-code/` 、 `/guide/writing/docs-principles/` |
| 確認日 | 2026-08-28 |
| 確認方法 | 私が直接取得。加えて Antigravity(agy) にも独立に確認させ、内容が一致することを確かめた |

## この出典の位置づけ

**文書を「作品」ではなく「運用され続けるもの」として扱う視点を与える。** 手元の4冊は、良い文書を書き上げるところまでを扱う。ここは、書き上げたあとに文書が腐る問題を扱う。

原則が短い名前で整理されており、**レビューで使える語彙**になる。「この文書は Current ではない」と言えるようになる。

---

## 原則の一覧（原文のまま）

### 文書化の進め方

| 名前 | 原文 | 意味 |
|---|---|---|
| Precursory | "Begin documenting before you begin developing." | 開発を始める前に文書化を始める。要求と仕様が文書の初稿になる |
| Participatory | "In the documentation process, include everyone from developers to end users." | 開発者から利用者まで全員を巻き込む |

### 内容の質

| 名前 | 原文 | 意味 |
|---|---|---|
| ARID | "Accept (some) Repetition In Documentation." | 文書ではある程度の重複を受け入れる |
| Skimmable | "Structure content to help readers identify and skip over concepts which they already understand or are not relevant to their immediate questions." | 読者が既知の部分を飛ばせるように構造化する |
| Exemplary | "Include (some) examples and tutorials in content." | 例とチュートリアルを含める。ただし全部ではなく、よくある使い方に絞る |
| Consistent | "Use consistent language and formatting in content." | 言葉と体裁を一貫させる |
| Current | "Consider incorrect documentation to be worse than missing documentation." | **誤った文書は、文書が無いことより悪い** |

### 情報源の置き方

| 名前 | 原文 | 意味 |
|---|---|---|
| Nearby | "Store sources as close as possible to the code which they document." | 説明対象のコードのできるだけ近くに置く |
| Unique | "Eliminate content overlap between separate sources." | 別々の情報源の間で内容を重複させない |

### 出版物としての質

| 名前 | 原文 | 意味 |
|---|---|---|
| Discoverable | "Funnel users intuitively towards publications through all likely pathways." | あらゆる経路から自然にたどり着けるようにする |
| Addressable | "Provide addresses to readers that link directly to content at a granular level." | 細かい単位に直接リンクできるようにする |
| Cumulative | "Content should be ordered to cover prerequisite concepts first." | 前提となる概念を先に置く |
| Complete | "Within each publication, cover concepts in full, or not at all." | 扱うなら全部扱う。中途半端に扱わない |
| Beautiful | "Visual style should be intentional and aesthetically pleasing." | 見た目は意図をもって整える |
| Comprehensive | "Ensure that together, all the publications in the body of documentation can answer all questions the user is likely to have." | 文書群全体で、読者の問いに答えきる |

---

## 特筆すべき2点

### 1. 誤った文書は無い方がまし

> "Consider incorrect documentation to be worse than missing documentation. When software changes faster than its documentation, the users suffer. Keep it up to date."

**この一文は、文書の運用規則の根拠になる。** 更新されない文書を残すことは、善意ではなく害である。だから「削除する」も品質改善の手段として標準に入れる。

### 2. ARID — 文書にDRYを持ち込みすぎない

> "If you want to write good code, Don't Repeat Yourself. But if you adhere strictly to this DRY principle when writing documentation, you won't get far. Some amount of business logic described by your code must be described again in your documentation."

**エンジニアが最も間違えやすい点である。** コードの原則をそのまま文書に持ち込むと、リンクだらけで読めない文書ができる。読者が1か所で用を足せることの方が、重複を消すことより優先される。

ただし `Unique`（情報源の重複を消す）とは矛盾しない。**文の中の重複は許す。情報源としての重複は許さない。** 同じことを説明する文書が2つあると、片方が必ず古くなる。

---

## docs as code

> "Documentation as Code (Docs as Code) refers to a philosophy that you should be writing documentation with the same tools as code: Issue Trackers, Version Control (Git), Plain Text Markup (Markdown, reStructuredText, Asciidoc), Code Reviews, Automated Tests"

構成要素は5つである。

1. 課題管理（Issue Trackers）
2. バージョン管理（Git）
3. プレーンテキストの記法（Markdown など）
4. コードレビュー
5. 自動テスト

**このプロジェクト自身がこの5つを満たすように作る。** 5つ目の「自動テスト」に相当するのが `tools/doc_lint.py` である。

---

## この標準に取り込む点

1. **原則の名前をそのまま語彙として使う。** レビューで「Current が守られていない」と言えるようにする。ただし日本語の説明を必ず添える。
2. **`Current` を運用の章の中心に置く。** 最終確認日とオーナーを文書に持たせる。
3. **`ARID` を明示的に書く。** 「重複を消す」ことを目的化しない。
4. **`Complete` をスコープの規則にする。** 「対象外」を書くことが、中途半端を避ける方法である。
5. **docs as code の5要素を、このリポジトリの構成で実演する。**

## アクセスできなかったページ

- `https://www.writethedocs.org/guide/writing/reviews/` — HTTP 404。レビューに関する記述は取得できなかった。レビューの章は他の出典（`SRC-WRITE-003` 3.7、`SRC-WRITE-004`）に依拠する。

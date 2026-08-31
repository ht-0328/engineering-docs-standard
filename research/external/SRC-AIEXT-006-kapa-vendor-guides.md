# SRC-AIEXT-006 kapa.ai — AIが検索して読む文書の書き方（ベンダーの指針）

## 出典

| 項目 | 内容 |
|---|---|
| 名称 | Writing documentation for AI: best practices |
| 発行 | kapa.ai（文書に対する質問応答の製品を作る会社） |
| URL | https://docs.kapa.ai/improving/writing-best-practices |
| 確認日 | 2026-08-31 |
| 確認方法 | 本文を直接取得した |
| 種別 | **ベンダーの指針。実測の裏づけは示されていない。** |

## この出典の位置づけ

**文書を検索で分割して読む仕組み（いわゆる RAG）を運用している会社が、書き手に何を求めるかを述べたものである。**

実測は示されていない。しかし、**分割される側の文書がどう壊れるかを、具体的に述べている点に価値がある。** 他の出典が抽象的に「構造を整えよ」と言うのに対し、この文書は「なぜ壊れるか」を言う。

利益相反に注意する。自社製品が読みやすい文書の書き方を勧める立場である。

---

## 中心の主張

### 1. 近くに書いたものは、分割後も一緒に残りやすい

> "The closer related information appears in your source content, the more likely it stays together after chunking."

**文書は分割されて読まれる。** 関係する情報が離れて書いてあると、別々の断片になり、片方だけがAIに渡る。

### 2. 各節は、それだけで意味が通るようにする

> "Documentation sections that depend on readers following a linear path or remember details from previous sections become problematic when processed as independent chunks."
> （読者が順に読むこと、前の節の内容を覚えていることを前提とする節は、独立した断片として処理されるときに問題になる）

対策として「前提を節の先頭に出し、必要な情報をその節の内側で完結させる」ことを勧めている。

**これは本編の C-01（結論先出し）とは別の要求である。** 本編は「走査する人のため」に前に出す。ここは「切り離されても意味が通るため」に前に出す。**理由が違うが、結論は同じになる。**

### 3. 見出しは、それだけで文脈を持つようにする

> "Design your content hierarchy so that each section carries sufficient context to be understood independently, while maintaining clear relationships to parent and sibling content."

具体的には、製品名や機能名を見出しに含めることを勧めている。一般的な見出し（「概要」「設定」）を避ける。

**これは本編の C-02（見出しを具体的にする）と一致する。** ただし理由が違う。本編は「走査する読者が予測できるように」であり、ここは「断片になったとき、どの製品の話か分かるように」である。

### 4. 表は、行ごとに独立しているものだけにする

> "Keep simple reference tables where each row is self-contained, but supplement or replace complex tables where relationships between cells convey important meaning."

**セルとセルの関係に意味がある表は、AIには読み取れない。** そういう表は、箇条書きか文章で言い換えるか、補うことを勧めている。

### 5. 図だけに情報を持たせない

> "Always include clear text descriptions for critical visual information such as diagrams, charts, and screenshots."

手順の図には、番号つきの手順の文章を必ず添えるとしている。

**これは本編の P-03（画像に代替テキストを付ける）を、さらに強くした要求である。** 本編は代替テキストを求める。ここは**本文そのもので同じ情報を伝えること**を求める。

### 6. 誤りの記述には、実際の文言をそのまま書く

> "When documenting troubleshooting steps, quote exact error messages and describe observable symptoms alongside solutions."

利用者は誤りの文言をそのまま貼って質問する。文言が文書に無ければ、一致しない。

**これは `SRC-AIEXT-005`（Context Rot）の「質問と答えの語がずれていると見つからない」という実測と、独立に一致する。**

---

## この別冊で使える主張

| # | 主張 | 他の出典との関係 |
|---|---|---|
| 1 | 関係する情報を近くに置く | この出典だけ |
| 2 | 各節を、それだけで意味が通るようにする | 本編 C-01 と結論が同じ。理由は違う |
| 3 | 見出しに、どの製品・機能の話かを入れる | 本編 C-02 と結論が同じ |
| 4 | 行ごとに独立しない表を避ける | 本編 P-02 と方向が同じ |
| 5 | 図だけに情報を持たせない | 本編 P-03 より強い要求 |
| 6 | 誤りの文言を、そのまま本文に書く | `SRC-AIEXT-005` の実測と一致 |

## この出典の弱さ

- **実測が無い。** どの主張も、測った結果は示されていない。
- ベンダーの立場である。自社製品に都合のよい書き方を勧めうる。
- **この出典だけを根拠に中核原則を作らない。** 他の出典との一致を確認したものだけを使う。

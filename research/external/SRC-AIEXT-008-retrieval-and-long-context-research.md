# SRC-AIEXT-008 査読つき研究 — 長い文脈と、分割の仕方が正答率に与える影響

## この文書の位置づけ

**この別冊で最も強い出典である。** 他の出典がベンダーの技術文書や個人の提案であるのに対し、ここに挙げるのは**査読を経た論文**が中心である。

調べ方は次のとおりである。

1. Antigravity(agy) に「実測した研究だけを集めよ。数値は数値のまま記録せよ」と指示して調べさせた。
2. **agy が挙げた論文と数値を、私（Claude）が arXiv の原文に当たって1件ずつ確認した。**
3. 確認できたものと、できなかったものを下で分けている。

**確認の結果、agy の報告には誤りがあった。** 詳しくは末尾の「突き合わせで見つかった誤り」に書く。

---

## A. 裏が取れた研究

### A-1. Lost in the Middle（TACL 2024。査読つき雑誌論文）

| 項目 | 内容 |
|---|---|
| 題名 | Lost in the Middle: How Language Models Use Long Contexts |
| 著者 | Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang |
| arXiv | 2307.03172 |
| 確認日 | 2026-08-31。**要旨を原文で確認した** |

**分かったこと**

> "performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle of long contexts, even for explicitly long-context models."
> （必要な情報が入力の**先頭か末尾**にあるとき、成績が最も高いことが多い。長い文脈の**真ん中**にある情報を使わなければならないとき、成績は大きく落ちる。長い文脈に対応したモデルであってもそうである）

**文書の書き方への意味**

**大事なことは、先頭か末尾に置く。** 真ん中に埋めない。これは本編の C-01（結論先出し）と同じ結論だが、根拠が違う。人向けは「走査するから」、こちらは「真ん中が読み落とされるから」である。

### A-2. NoLiMa（ICML 2025。査読つき国際会議論文）

| 項目 | 内容 |
|---|---|
| 題名 | NoLiMa: Long-Context Evaluation Beyond Literal Matching |
| 著者 | Ali Modarressi, Hanieh Deilamsalehy, Franck Dernoncourt, Trung Bui, Ryan A. Rossi, Seunghyun Yoon, Hinrich Schütze |
| arXiv | 2502.05167（2025-02-07） |
| 確認日 | 2026-08-31。**要旨を原文で確認した** |

**分かったこと**

語句がそのまま一致する手がかりを消し、意味のつながりで探させる課題を作った。13モデルで測った。

> "At 32K, for instance, 11 models drop below 50% of their strong short-length baselines."
> （たとえば32Kトークンでは、11個のモデルが、短い入力での高い基準値の50%を下回るまで落ちる）

**文書の書き方への意味**

**語がそのまま一致しないと、長い文脈では見つけてもらえない。** 言い換えや同義語で書き分けると、探す側が見つけられなくなる。本編の S-10（用語を統一する）が、AIに対しては人向けよりはるかに強い意味を持つ。

### A-3. Large Language Models Can Be Easily Distracted by Irrelevant Context（ICML 2023。査読つき）

| 項目 | 内容 |
|---|---|
| 著者 | Freda Shi, Xinyun Chen, Kanishka Misra, Nathan Scales, David Dohan, Ed Chi, Nathanael Schärli, Denny Zhou |
| arXiv | 2302.00093 |
| 確認日 | 2026-08-31。**要旨を原文で確認した** |

**分かったこと**

算数の文章題に、解答に関係のない文を混ぜた課題（GSM-IC）を作った。

> "the model performance is dramatically decreased when irrelevant information is included."
> （関係のない情報が入ると、モデルの成績は劇的に下がる）

**文書の書き方への意味**

**関係のない記述を、同じ場所に置かない。** 人なら読み飛ばせるが、AIは引きずられる。

### A-4. Dense X Retrieval（EMNLP 2024。査読つき国際会議論文）

| 項目 | 内容 |
|---|---|
| 題名 | Dense X Retrieval: What Retrieval Granularity Should We Use? |
| 著者 | Tong Chen ほか7名 |
| arXiv | 2312.06648 |
| 確認日 | 2026-08-31。**要旨を原文で確認した** |

**分かったこと**

検索の単位を「文書」「段落」「文」「命題（proposition）」で比べた。命題は次のように定義されている。

> "Propositions are defined as atomic expressions within text, each encapsulating a distinct factoid and presented in a concise, self-contained natural language format."
> （命題とは、文章の中の最小の表現である。それぞれが一つの事実を含み、簡潔で**自己完結した**自然言語の形で示される）

> "indexing a corpus by fine-grained units such as propositions significantly outperforms passage-level units in retrieval tasks."

**文書の書き方への意味**

**「自己完結した最小の事実」の単位で書くと、見つけてもらいやすい。** これが `SRC-AIEXT-006`（kapa.ai）の「各節を自己完結させよ」に、査読つきの裏づけを与える。

### A-5. 分割方法の体系的な比較（arXiv 2026。査読前）

| 項目 | 内容 |
|---|---|
| 題名 | A Systematic Investigation of Document Chunking Strategies and Embedding Sensitivity |
| 著者 | Muhammad Arslan Shaukat, Muntasir Adnan, Carlos C. N. Kuhn |
| arXiv | 2603.06976（2026-03-07） |
| 確認日 | 2026-08-31。**要旨を原文で確認した** |
| 区分 | **査読前のプレプリント。** 上の4件より弱い |

**分かったこと**

36通りの分割方法を、6分野・5種類の埋め込みモデルで比べた。

| 分割の仕方 | nDCG@5 |
|---|---|
| 素朴な固定長での分割 | **0.244 未満** |
| 段落のまとまりでの分割（構造を見る） | **約 0.459** |

要旨は "content-aware chunking significantly improves retrieval effectiveness over naive fixed-length splitting" と述べている。

**文書の書き方への意味**

**段落や見出しの区切りが、そのまま検索の単位になる。** 区切りが意味のある場所に無いと、検索の精度が半分近くまで落ちる。

---

## B. 裏が取れなかった数値

**agy が挙げたが、私が原文で確認できなかったものである。この別冊では使わない。**

| 主張 | 出どころとされたもの | 状況 |
|---|---|---|
| 命題単位にすると Recall@5 が17〜25%向上する | Dense X Retrieval | **要旨に数値の記載が無い。** 本文にある可能性はあるが、確認していない |
| 関係ない文を混ぜると Macro Accuracy が30%未満に落ちる | Shi et al. 2023 | **要旨に数値の記載が無い。** 同上 |
| Recall@5 = 1.000、MRR = 0.911 | MDKeyChunker（arXiv 2603.23533） | 原文を確認していない。**査読前であり、単一の小規模な実験（18文書・30問）である** |
| Lost in the Middle で「20ポイント以上低下」 | Lost in the Middle | 要旨は「大きく落ちる」とだけ述べる。**数値は未確認** |

---

## C. 突き合わせで見つかった誤り

**調べ方の記録として残す。**

agy の報告には、原文と食い違う点があった。

| 項目 | agy の報告 | 原文 |
|---|---|---|
| NoLiMa の著者名 | Hosein Deilamsalehy | **Hanieh** Deilamsalehy |
| NoLiMa の著者名 | Tung Bui | **Trung** Bui |
| Dense X Retrieval の数値 | Recall@5 が17〜25%向上 | 要旨に数値の記載なし |

**論文そのものの存在と、中心の主張は正しかった。** 誤っていたのは、細部の転記と、要旨に無い数値の付加である。

**この経験から、この別冊に規則を一つ置く。** AIに調べさせた結果は、**論文名までは信じてよいが、数値と固有名詞は必ず原文に当たる。**

---

## D. この別冊で使える主張

| # | 主張 | 根拠 | 強さ |
|---|---|---|---|
| 1 | 大事なことは先頭か末尾に置く。真ん中に埋めない | A-1 | 査読つき |
| 2 | 用語を統一する。語がずれると長い文脈で見つからない | A-2 | 査読つき |
| 3 | 関係のない記述を同じ場所に置かない | A-3 | 査読つき |
| 4 | 各節を自己完結させる。一つの節に一つの事実 | A-4 | 査読つき |
| 5 | 意味の切れ目と、見出しの切れ目を一致させる | A-5 | 査読前 |
| 6 | 入力が長くなるほど正答率が落ちる | A-2、`SRC-AIEXT-005` | 査読つき＋実測 |

## この出典群の弱さ

- **日本語で測ったものは1件も無い。** すべて英語である。
- 測っているのは「探して答える」課題が中心である。**書かせる課題では測っていない。**
- モデルは日々変わる。**2026-08-31 時点の結果である。**

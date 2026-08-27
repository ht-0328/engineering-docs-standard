# SRC-EXT-004 Diátaxis — 文書を4つの型に分ける枠組み

## 出典

| 項目 | 内容 |
|---|---|
| 名称 | Diátaxis |
| 著者 | Daniele Procida |
| URL | https://diataxis.fr/ |
| 確認日 | 2026-08-28 |
| 確認ページ | `/`、`/start-here/`、`/compass/`、`/quality/` |
| 確認方法 | 各ページを直接取得。加えて Antigravity(agy) にも独立に確認させ、内容が一致することを確かめた |

## この出典の位置づけ

**文書の質を上げる方法のうち、最も効果が大きく、最も見落とされているものを扱う。** 文の書き方ではなく、**文書の種類を混ぜないこと**を扱う枠組みである。

手元の4冊はどれも「1つの文書をどう書くか」を教える。Diátaxis はその手前を問う。**この文書は4つのうちどれなのか。** そこを決めずに書き始めるから、手順書に設計の背景が混ざり、リファレンスにチュートリアルが混ざる。

自らの適用範囲を次のように述べている。

> "solves problems related to documentation *content* (what to write), *style* (how to write it) and *architecture* (how to organise it)"

---

## 4つの型（原文のまま）

| 型 | 原文の定義 | 日本語 |
|---|---|---|
| Tutorial | "A tutorial is a lesson, that takes a student by the hand through a learning experience." | 学習者の手を取って学習体験を通す授業 |
| How-to guide | "A how-to guide addresses a real-world goal or problem, by providing practical directions." | 現実の目標や問題に対し、実際的な指示を与えるもの |
| Reference | "Reference guides contain the technical description - facts - that a user needs in order to do things correctly." | 正しく作業するために必要な、技術的な記述＝事実 |
| Explanation | "Explanatory guides provide context and background." | 文脈と背景を与えるもの |

## 2つの軸

Diátaxis は2つの問いで型を決める。

1. **action か cognition か** — 行動を助けるのか、理解を助けるのか。
2. **acquisition か application か** — 学習（study）を支えるのか、実務（work）を支えるのか。

| 型 | 軸1 | 軸2 |
|---|---|---|
| Tutorial | 行動を助ける（informs action） | 技能の習得（acquisition of skill） |
| How-to guide | 行動を助ける（informs action） | 技能の適用（application of skill） |
| Reference | 理解を助ける（informs cognition） | 技能の適用（application of skill） |
| Explanation | 理解を助ける（informs cognition） | 技能の習得（acquisition of skill） |

### この2軸から導かれる、実務で使える判定

書こうとしている文書について、次の2つを順に答える。

1. 読者はこれを読んで**何かをする**のか、**何かを理解する**のか。
2. 読者は**学んでいる最中**なのか、**仕事の最中**なのか。

答えが決まれば型が決まる。**型が決まらない文書は、まだ書き始めてはいけない。**

---

## 混ぜてはいけない理由

Antigravity による確認では、公式サイトは次の2点を挙げている。

1. **読者の目的が相反するため、読む流れが途切れる。** 手順を進めたい読者にとって、途中の長い背景説明は妨害である。
2. **保守できなくなる。** 境界が曖昧になると、文体と内容が不適切な場所に入り込み、情報の欠落や重複に気づけなくなる。

---

## 品質の定義（`/quality/`）

**この定義は、この標準の品質軸を決めるうえで最も重要な参照点である。** Diátaxis は品質を2層に分ける。

### 機能的品質（functional quality）

> "accuracy, completeness, consistency, usefulness, precision and so on"

- 互いに独立している。正確だが不完全、ということがありうる。
- 現実と突き合わせて**客観的に測れる**。
- 満たしていないことは利用者にすぐ分かる。

### 深い品質（deep quality）

> "feeling good to use, having flow, fitting to human needs, being beautiful, anticipating the user"

- 互いに依存し合っている。ひとつだけ良くすることはできない。
- 数値で測れないが、**あるかどうかは分かる**。
- 人間の必要に照らして判断するしかない。

| 観点 | 機能的品質 | 深い品質 |
|---|---|---|
| 性質 | 客観的。現実に照らして測る | 主観的。人間の必要に照らして判断する |
| 評価 | 数えられる | 判断が要る |
| 相互関係 | 独立している | 互いに強め合う |

**この標準にとっての意味は明確である。** 自動チェッカー（`doc_lint`）で測れるのは機能的品質の一部だけである。**チェッカーを通ったことを品質の証明にしてはいけない。** この一文は、標準の本文にそのまま書く。

---

## この標準に取り込む点

1. **「書く前に型を決める」を最初の規則にする。** 文の書き方より前に置く。
2. **4つの型それぞれについて、「書いてよいこと」と「書いてはいけないこと」を表にする。** 混ざりを見つけるのがレビューの第一歩になる。
3. **品質を2層に分ける考え方を採用する。** 「測れる品質」と「測れないが分かる品質」を分けて説明する。
4. **自動チェックの限界を明記する根拠として使う。**

## 取り込む際の注意

- Diátaxis はオープンソース製品の公開文書を想定している。**社内の設計書・障害報告・議事録は4つの型にきれいに収まらない。** 型を無理に当てはめず、「この文書の主たる型は何か、混ざっている部分はどこか」を問う道具として使う。
- 4つの型の名称は英語のままが定着している。日本語訳を作ると、かえって検索できなくなる。**原語を残し、初出で説明を添える**方針にする。これは `SRC-EXT-001` の専門用語の扱い（読者がその語で検索するなら残す）とも一致する。

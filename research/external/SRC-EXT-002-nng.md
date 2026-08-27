# SRC-EXT-002 Nielsen Norman Group — Webでの読まれ方の実証研究

## 出典

| 項目 | 内容 |
|---|---|
| 名称 | How Users Read on the Web / Inverted Pyramid: Writing for Comprehension |
| 発行元 | Nielsen Norman Group |
| 種別 | ユーザビリティ実験にもとづく記事 |
| 確認日 | 2026-08-28 |
| URL | https://www.nngroup.com/articles/how-users-read-on-the-web/ 、 https://www.nngroup.com/articles/inverted-pyramid/ |

## この出典の位置づけ

**この標準のなかで唯一、「読みやすさ」を実測した数値を持つ出典である。** 他の出典は経験則と説得力に頼っているが、ここには対照実験の結果がある。

「読みやすさは重要だ」という主張を、感覚ではなく数字で支える根拠として使う。

---

## 中核となる数値

### 人はWebを読まない。走査する。

> "79 percent of our test users always scanned any new page they came across; only 16 percent read word-by-word."

- 新しいページを**必ず走査する**利用者: **79%**
- **1語ずつ読む**利用者: **16%**

**この一点が、見出し・箇条書き・結論先出しのすべての根拠になる。** 読者は最初から最後まで読まない、という前提で文書を設計する必要がある。

### 書き方を変えるとユーザビリティが何%上がるか

同一内容の5種類のページを比較した実験の結果である。

| 変更内容 | ユーザビリティの改善 |
|---|---|
| 簡潔にする（Concise text） | **+58%** |
| 走査しやすい体裁にする（Scannable layout） | **+47%** |
| 客観的な言葉にする（Objective language） | **+27%** |
| 上記3つすべて（Combined） | **+124%** |

**3つを同時にやると、単純な足し算（132%）に近い効果が出ている。** どれか1つだけではなく、まとめて適用する価値がある。

### 語数の目安

> "**half the word count** (or less) than conventional writing"

Web向けの文章は、従来の文章の**半分以下**の語数にする。

---

## 抽出した規則

| # | 規則 | 原文 | 出典URL |
|---|---|---|---|
| N-01 | 読者は走査すると前提して設計する | "79 percent of our test users always scanned any new page" | how-users-read-on-the-web |
| N-02 | キーワードを強調する。リンクも強調の一種である | "highlighted **keywords**" | 同上 |
| N-03 | 見出しは意味のあるものにする。**気の利いた見出しにしない** | "meaningful **sub-headings** (not 'clever' ones)" | 同上 |
| N-04 | 箇条書きを使う | "bulleted **lists**" | 同上 |
| N-05 | 1段落に1つの考えだけを入れる。読者は最初の数語で判断し、残りを飛ばす | "**one idea** per paragraph (users will skip over any additional ideas if they are not caught by the first few words)" | 同上 |
| N-06 | 逆ピラミッド型で書く。結論を先に置く | "Inverted pyramid style with conclusions first" | 同上 |
| N-07 | 語数を従来の半分以下にする | "half the word count (or less)" | 同上 |
| N-08 | 誇張した宣伝的な表現を使わない。読者はそれを嫌う | "detested 'marketese'; the promotional writing style with boastful subjective claims" | 同上 |

### 逆ピラミッドの構造

> "The most important information (or what might even be considered the conclusion) is presented first."

1. 主要な事実と結論を最初に置く。
2. 次に、読者の関心が高い順に補足を置く。
3. 最後に、細かく微妙な詳細を置く。

示されている効果は次の4点である。

- 理解を助ける（"Improve comprehension"）— 読者が早く全体像を作れる。
- 読むための労力を減らす（"Decrease interaction cost"）— 長く読まなくても要点が分かる。
- 読み進めさせる（"Encourage scrolling"）。
- 途中でやめる読者を支える（"Support readers who skim"）— **どこで読むのをやめても要点は伝わる。**

---

## 注意点

- この実験は1997年に実施され、以後も参照され続けている古典である。**測定対象はWebページであり、社内の設計書やAPI仕様書ではない。** 数値をそのまま社内文書に当てはめるのは正確ではない。
- ただし「読者は走査する」「結論を先に置くと理解が上がる」という方向は、他の出典（Google、Diátaxis、Write the Docs、SRC-WRITE-001、SRC-WRITE-003）とも一致しており、方向としては信頼できる。
- 「客観的な言葉にすると+27%」は、宣伝的な表現を削るという意味である。技術文書ではもともと宣伝表現が少ないため、社内文書での伸びしろは実験より小さいと考えられる。

## この標準に取り込む点

1. **「読者は読まない。走査する」を標準の前提として冒頭に置く。** 79%という数字を根拠として明示する。
2. **結論先出しを最上位の規則にする。** 「途中でやめても要点が伝わる」ことを判定基準にする。
3. **1段落1アイデアを規則にする。** Google（SRC-EXT-001）の3〜5文と組み合わせる。
4. **見出しは「気が利いている」ことより「内容が予測できる」ことを優先する。** これは自動チェックできないが、レビュー観点として使える。

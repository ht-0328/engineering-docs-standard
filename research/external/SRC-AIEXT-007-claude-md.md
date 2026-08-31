# SRC-AIEXT-007 CLAUDE.md — AIへの指示書の書き方（Claude Code 公式）

## 出典

| 項目 | 内容 |
|---|---|
| 名称 | How Claude remembers your project（Claude Code 公式文書） |
| 発行 | Anthropic |
| URL | https://code.claude.com/docs/en/memory |
| 確認日 | 2026-08-31 |
| 確認方法 | 本文を直接取得した。加えて Antigravity(agy) にも独立に調べさせ、突き合わせた |
| 種別 | **ベンダーの公式文書。** 特定製品（Claude Code）の仕様である |

## この出典の位置づけ

**AIへの指示書の書き方について、数値つきの推奨を持つ数少ない公式文書である。**

`SRC-AIEXT-004`（AGENTS.md）が「必須項目は無い。長さの上限も定めない」としているのに対し、こちらは**行数の目標を明示している**。両者は対立しない。AGENTS.md は道具をまたぐ形式を定め、こちらは1つの製品での効き方を述べている。

---

## 突き合わせで正した誤り

**この節は、調べ方の記録として残す。**

Web検索で上位に出る解説記事の複数が「Claude Code は CLAUDE.md が無ければ AGENTS.md を読む」と書いていた。Antigravity(agy) の調査はこれを否定した。公式文書に当たったところ、agy が正しかった。

> "Claude Code reads `CLAUDE.md`, not `AGENTS.md`."
> （Claude Code は `CLAUDE.md` を読む。`AGENTS.md` は読まない）

**二次情報は誤っていた。** この別冊で「AI関連の情報は一次情報に当たる」という規則を置く根拠の一つである。

AGENTS.md を使っている場合の公式の対処は次の2つである。

```markdown
@AGENTS.md

## Claude Code

Use plan mode for changes under `src/billing/`.
```

または記号連結（symlink）を使う。

```bash
ln -s AGENTS.md CLAUDE.md
```

---

## 数値で定まっていること

| 対象 | 数値 | 原文 |
|---|---|---|
| CLAUDE.md 1ファイルの目標 | **200行以内** | "target under 200 lines per CLAUDE.md file" |
| 読み込みの上限 | 4 MiB。超えると**読まれない** | "loads a CLAUDE.md file of up to 4 MiB in full and skips a larger file" |
| 取り込み（`@`）の深さ | **4段まで** | "with a maximum depth of four hops" |
| 自動メモリの索引 | 先頭200行、または25KBまで | "The first 200 lines of `MEMORY.md`, or the first 25KB, whichever comes first" |

**200行の理由も書かれている。**

> "Longer files consume more context and reduce adherence."
> （長いファイルは文脈をより多く消費し、指示の遵守を下げる）

> "Shorter files produce better adherence."
> （短いファイルのほうが遵守がよい）

**「短いほうが守られる」と明言している。** ただし**測定結果は示されていない。**

---

## 書き方の指針

### 構造: 見出しと箇条書きで区切る

> "use markdown headers and bullets to group related instructions. Claude scans structure the same way readers do: organized sections are easier to follow than dense paragraphs."
> （関係する指示をまとめるのに、Markdownの見出しと箇条書きを使う。Claudeは読者と同じように構造を走査する。整理された節のほうが、詰まった段落より追いやすい）

**「読者と同じように走査する」と明言している点が重要である。** 本編の C-01・C-02（結論先出し、具体的な見出し）が、そのままAIにも効くという主張になっている。

### 具体性: 確かめられる形で書く

公式が挙げる対比。

| 良い | 悪い |
|---|---|
| Use 2-space indentation | Format code properly |
| Run `npm test` before committing | Test your changes |
| API handlers live in `src/api/handlers/` | Keep files organized |

> "write instructions that are concrete enough to verify"
> （確かめられる程度に具体的な指示を書く）

**これは本編の S-07（曖昧な語を数値・固有名詞に置き換える）と同じ規則である。** 人向けとAI向けで一致する。

### 一貫性: 矛盾した指示を置かない

> "if two rules contradict each other, Claude may pick one arbitrarily."
> （2つの規則が矛盾していると、Claudeはどちらかを恣意的に選ぶことがある）

**矛盾は「エラー」にならない。黙ってどちらかが選ばれる。** これは人向けの文書と決定的に違う。人なら質問するが、AIは質問せずに進む。

### 何を書くか

> "Keep it to facts Claude should hold in every session: build commands, conventions, project layout, 'always do X' rules."

書くのをやめる基準も示されている。

- 手順が複数段階にわたるもの → スキルに移す。
- コードの一部にしか関係しないもの → 経路を限った規則（`paths` 付きの `.claude/rules/`）に移す。

**「常に要るもの」と「ときどき要るもの」を分ける。** 常に読まれる場所には、常に要るものだけを置く。

---

## 指示書は強制ではない

**この別冊で必ず書くべき注意である。**

> "Claude treats them as context, not enforced configuration."
> （Claudeはこれらを文脈として扱う。強制される設定としてではない）

> "there's no guarantee of strict compliance, especially for vague or conflicting instructions."
> （厳密な遵守は保証されない。特に曖昧な指示や矛盾した指示では）

必ず実行させたいことは、指示書ではなく仕組み（hook や権限設定）で行うよう案内している。

| 目的 | 使うもの |
|---|---|
| 道具・命令・経路を確実に止める | 権限の設定 |
| 決まった時点で必ず実行する | hook |
| 振る舞いの方針を示す | 指示書（CLAUDE.md） |

**「文書で守らせる」ことには限界がある、と公式が述べている。**

---

## 読み込みの順序と適用範囲

| 範囲 | 置き場所 |
|---|---|
| 組織全体 | `/etc/claude-code/CLAUDE.md`（Linux / WSL）ほか |
| 利用者個人 | `~/.claude/CLAUDE.md` |
| プロジェクト | `./CLAUDE.md` または `./.claude/CLAUDE.md` |
| 個人のプロジェクト設定 | `./CLAUDE.local.md` |

**上書きではなく連結される。**

> "All discovered files are concatenated into context rather than overriding each other."

順序は根に近いほうが先、作業場所に近いほうが後になる。

**サブディレクトリのものは起動時には読まれない。** そのディレクトリのファイルを読むときに読み込まれる。

---

## 細かいが役に立つ規定

| 規定 | 内容 |
|---|---|
| HTML のコメントは除去される | `<!-- 保守者向けの注記 -->` は文脈に入らない。**人向けの注記をトークンを使わずに残せる** |
| 逆引用符で囲んだ `@` は取り込まれない | `` `@README` `` は文字のまま。`@README` は取り込む |
| 取り込みは文脈を減らさない | "Splitting into `@path` imports helps organization but doesn't reduce context" |

**最後の1つは重要である。** ファイルを分けても、`@` で取り込む限り読み込み量は減らない。減らしたいなら、経路を限った規則かスキルにする。

---

## この別冊で使える主張

| # | 主張 | 種別 |
|---|---|---|
| 1 | 指示書は**200行以内**を目標にする | 公式の推奨（数値あり、測定なし） |
| 2 | 短いほうが指示は守られる | 公式の主張（測定なし） |
| 3 | 見出しと箇条書きで区切る。AIも人と同じように走査する | 公式の主張 |
| 4 | 指示は**確かめられる形**で書く | 公式の指針 |
| 5 | 矛盾した指示を置かない。**黙って一方が選ばれる** | 公式の主張 |
| 6 | 常に要るものだけを、常に読まれる場所に置く | 公式の指針 |
| 7 | **指示書に強制力は無い。** 必ず守らせたいことは仕組みで行う | 公式の明言 |
| 8 | 適用範囲は置き場所で表す | 公式の仕様 |

## この出典の弱さ

- **1製品の仕様である。** 他社のAIには当てはまらない部分がある。
- 200行という数値の**測定結果は示されていない**。
- 日本語での検証は無い。

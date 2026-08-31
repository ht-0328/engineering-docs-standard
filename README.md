# エンジニアのためのドキュメント標準

| 項目 | 内容 |
|---|---|
| これは何か | 質の高い技術文書を書き、レビューするための、根拠つきのルール集 |
| Webで読む | [公開サイト](https://ht-0328.github.io/engineering-docs-standard/)（検索・目次つき） |
| **AI向けの別冊** | **[AIに読ませる文書の標準](docs-ai/index.md)**（[公開サイト](https://ht-0328.github.io/engineering-docs-standard/ai/)） |
| 版 | 本編 0.2.0 / 別冊 0.1.0（[変更履歴](CHANGELOG.md)） |
| 作成者 | Claude（Opus 5）。分担は「この標準の作り方」を参照 |
| 機密区分 | 公開可 |
| 想定読者 | 設計書・手順書・報告書・議事録を書く人。および、それらをレビューする人 |
| 読んだあとできること | 良い文書を書ける。レビューで「なぜダメか」と「どう直すか」を説明できる |
| 保守責任者 | このリポジトリの保守担当 |
| 最終確認日 | 2026-08-28 |

## 3行で

1. **良い文書とは、読者が必要な判断と行動を、最小の労力で、正しく行える文書である。**
2. **読者は最初から順に読まない。** Webページの実験では79%が走査し、1語ずつ読んだのは16%だった。
3. **「読みにくい」は指摘ではない。** 品質6軸のどれに当たるかを言うと、直す場所が決まる。

## 何から読むか

**本文は [docs/index.md](docs/index.md) から始まる。** Web で読むなら [公開サイト](https://ht-0328.github.io/engineering-docs-standard/) が同じ内容である。**こちらは全文検索が使える。**

| 目的 | 読むもの |
|---|---|
| 自分の「読みやすさ」の感覚が正しいか確かめたい | [docs/09-your-instincts.md](docs/09-your-instincts.md) |
| レビューで指摘できるようになりたい | [docs/06-review.md](docs/06-review.md) |
| 悪い例と直し方を見たい | [docs/07-antipatterns.md](docs/07-antipatterns.md) |
| いま書く文書の型がほしい | [templates/](templates/) |
| 手元に1枚置きたい | [docs/appendix-checklist.md](docs/appendix-checklist.md) |
| **AIに読ませる文書を書きたい** | **[docs-ai/index.md](docs-ai/index.md)（別冊）** |

## 何が根拠になっているか

書籍4冊と、公開されている標準・実験結果6件を突き合わせた。**中核となる原則は、独立した3出典以上が直接支持するものに限った。** 単一の出典にしか根拠が無いルールと、この標準が運用上決めたルールは、各ルールの出典欄にその旨を書いている。

| ID | 名称 |
|---|---|
| `SRC-WRITE-001` | 大事な順に身につく 説明の「型」（海津佳寿美） |
| `SRC-WRITE-002` | ITエンジニアのためのMarkdown実践入門（平田賀一） |
| `SRC-WRITE-003` | 技術者のためのテクニカルライティング入門講座 第2版 |
| `SRC-WRITE-004` | エンジニアのための文章術 再入門講座 新版 |
| `SRC-EXT-001` | Google developer documentation style guide / Technical Writing Courses |
| `SRC-EXT-002` | Nielsen Norman Group（Webでの読まれ方の実証研究） |
| `SRC-EXT-003` | JTF日本語標準スタイルガイド 第4.0版 |
| `SRC-EXT-004` | Diátaxis |
| `SRC-EXT-005` | Write the Docs |
| `SRC-EXT-006` | RFC 2119 / 8174、ADR、Plain language |

**どの原則を何出典が支持しているかの一覧は [research/cross-reference.md](research/cross-reference.md) にある。**

**AI向けの別冊は、これとは別に13件の出典を持つ。** 書籍3冊、査読つき論文4件を含む研究、公開仕様、そして**自分で測った結果**である。一覧は [docs-ai/index.md](docs-ai/index.md#出典) に、突き合わせは [research/cross-reference-ai.md](research/cross-reference-ai.md) にある。

## 使い方

必要なものを確認し、作業用のイメージを1回作れば、あとはすべて同じ形のコマンドで動く。

### 必要なもの

| 必要なもの | 用途 | 確認方法 |
|---|---|---|
| Docker | 検査・サイト生成・図の書き出しをすべて動かす | `docker --version` が版を表示する |
| `bash` | `tools/` のスクリプトを動かす | 標準で入っている |
| ネットワーク | イメージの作成と Mermaid の取得（各1回だけ） | — |
| ホストの `python3` | **コード例の検証だけ**に使う。他の作業には要らない | `python3 --version` が版を表示する |

**poppler も draw.io も Markdown の変換器も、ホストへは入れない。** すべて Docker の中で動く。

**例外は [tools/verify_examples.py](tools/verify_examples.py) だけである。** このツールは Docker コマンドそのものを実行して確かめるため、コンテナの外から動かす必要がある。標準ライブラリだけで動くので、追加のインストールは要らない。

### 作業用のイメージを作る

最初に1回だけ実行する。

```bash
docker build -t edocs-tools -f tools/Dockerfile tools/
```

**成功したとき**: 最後の行が `Successfully tagged edocs-tools:latest` になる。`docker images edocs-tools` で確認できる。

### 文書を検査する

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-tools python tools/doc_lint.py
```

**期待される出力**（末尾の2行）

```text
検査したファイル: 41
error: 0  warning: 143  info: 0
```

**終了コード**: `error` が0件なら `0`、1件以上あれば `1` を返す。`warning` では失敗しない。

特定のファイルだけを検査する場合は、パスを渡す。

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-tools python tools/doc_lint.py docs/04-sentences.md
```

抑制している行数を確認する場合は `--report-suppressions` を付ける。

検査する内容は [.doclint.yml](.doclint.yml) に書いてある。ルールを変えるときはこのファイルを直す。

**検査を通ったことは品質の証明ではない。** 読者に合っているか、結論が妥当か、事実が正しいかは機械では判定できない。

### 悪い例を載せたいとき

文書の書き方を説明する文書は、悪い例を原文のまま載せる必要がある。その範囲だけ検査を止める。

```markdown
<!-- doclint-disable link_text sentence_length -->
（悪い例をここに書く）
<!-- doclint-enable -->
```

ルール名を書かずに `<!-- doclint-disable -->` とすると、すべてのルールを止める。1行だけなら `<!-- doclint-disable-next-line -->` を使う。

**コードブロックと行内コードの中に書いた指示子は、指示として扱われない。** 上の説明そのものが検査を止めることはない。

### コード例が実際に動くか確かめる

文書に書いたコマンドを取り出して実行し、書いてある期待出力と照合する。
**このツールだけはホストで動かす。** Docker コマンドそのものを確かめるためである。

<!-- verify-examples: skip -->

```bash
python3 tools/verify_examples.py
```

**期待される出力**（末尾）

```text
検証したコマンド: 9
成功: 9  失敗: 0  対象外: 0
```

**終了コード**: 失敗が0件なら `0`、1件以上あれば `1` を返す。
`対象外` は、安全のため実行しないコマンドの件数である。
`<!-- verify-examples: skip -->` を付けたブロック（サーバーの起動など）は、そもそも数えない。

### 図を書き出す

```bash
bash tools/export_diagrams.sh
```

**期待される出力**（末尾）

```text
    176655 bytes  quality-axes-drawio.svg
      4224 bytes  quality-axes.svg
```

図の方式の使い分けは [docs/adr/ADR-001-diagram-tool.md](docs/adr/ADR-001-diagram-tool.md) に記録している。

### サイトを作って見る

**公開ずみのサイトを見るだけなら、この手順は要らない。** [公開サイト](https://ht-0328.github.io/engineering-docs-standard/) が `main` の内容をそのまま出している。手元で作るのは、公開前の変更を確かめるときである。

図の描画に使う Mermaid を先に取得する。クローン直後に一度だけ実行する。

```bash
bash tools/fetch_vendor.sh
```

**期待される出力**: `完了:` の行と `3572661 bytes`。取得済みなら `mermaid.min.js は取得済み（検証値が一致）` と出て何もしない。

そのうえでサイトを作る。

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-tools python tools/build_site.py
```

**期待される出力**

```text
生成したページ: 16
検索索引の項目: 247
出力先: /w/site
```

AI向けの別冊も作る場合は `--all` を付ける。**別冊は `site/ai/` に出る。**

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-tools python tools/build_site.py --all
```

**期待される出力**（末尾の3行）

```text
生成したページ: 12
検索索引の項目: 193
出力先: /w/site/ai
```

開くときも Docker を使う。

<!-- verify-examples: skip -->

```bash
docker run --rm -p 8765:8765 -v "$PWD/site:/site:ro" -w /site edocs-tools \
  python -m http.server 8765 --bind 0.0.0.0
```

ブラウザで `http://127.0.0.1:8765/` を開く。止めるときは `Ctrl+C` を押す。

**生成したサイトは外部への通信を行わない。** そのために、閲覧時ではなくビルド前に Mermaid を取得している。

### Zensical 版のサイトを作って見る（試験中）

同じ `docs/` から、[Zensical](https://zensical.org/) でもサイトを作れるようにした。
**既存の生成と入れ替えたわけではない。** どちらを残すかを決めるために、並べて比べている。
公開しているサイトは、いまも `tools/build_site.py` が作ったものである。

違いと理由は [ADR-002](docs/adr/ADR-002-site-generator.md) にまとめた。

作業用のイメージは、既存のものとは別に作る。最初に1回だけ実行する。

```bash
docker build -t edocs-zensical -f tools/Dockerfile.zensical tools/
```

そのうえでサイトを作る。Mermaid の取得（`bash tools/fetch_vendor.sh`）は先に済ませておく。

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-zensical python tools/build_site_zensical.py
```

**期待される出力**（末尾の2行）

```text
生成したページ: 15
出力先: /w/site-zensical
```

**終了コード**: 生成できれば `0`。`--strict` を付けると、警告が1件でもあれば `1` を返す。

開くときは、出力先だけ替えて既存と同じ手順を使う。

<!-- verify-examples: skip -->

```bash
docker run --rm -p 8766:8766 -v "$PWD/site-zensical:/site:ro" -w /site edocs-zensical \
  python -m http.server 8766 --bind 0.0.0.0
```

`build/zensical/` は `docs/` の写しである。**直接編集しない。** 生成のたびに作り直す。
`docs/` の外を指すリンクを GitHub の URL に書き換えるために、一度写している。

`.cache/` は Zensical が差分で作り直すための控えである。**Zensical が中に `.gitignore` を置くため、Git には入らない。**

### 独立レビューを投げる

**レビューの結果は `reviews/` に置く。** 既存の [reviews/2026-08-28-codex-review.md](reviews/2026-08-28-codex-review.md) と同じ構成にまとめる。

プロンプトはファイルとして保存しない。**本文を複製すると、直したそばから古くなる。** 毎回、いまの本文から組み立てる。

<!-- verify-examples: skip -->

```bash
python3 tools/make_review_prompt.py 1 | codex exec --skip-git-repo-check \
  --sandbox read-only -o reviews/2026-08-31-codex-raw-1.md -
```

引数は3つある。**レビュアーにファイルを読ませず、本文をプロンプトに埋め込んで渡す。**

| 引数 | 渡す本文 | 見させること |
|---|---|---|
| `1` | 2章・3章 | 言い過ぎ、矛盾、自己規則違反、数値の不一致 |
| `2` | 4章・5章・6章 | 同じ観点 |
| `3` | 突き合わせ表・実験の記録 | 実験の結論がデータから言えるか。出典の数え方が一貫しているか |

**Codex にファイルを読ませると返ってこないことがあった。** そのため本文を埋め込む形にしている。

生の指摘（`*-codex-raw-*.md`）は、記録にまとめたあとで消す。

## フォルダ構成

```text
docs/                 本編の本文（Markdown が正本）
docs/adr/             この標準自身の決定記録
docs-ai/              AI向けの別冊の本文
templates/            文書型ごとのテンプレート8種
templates-ai/         AI向けのテンプレート4種
diagrams/src/         図の正本（.mmd / .drawio / 手書き .svg）
diagrams/export/      書き出したSVG（生成物）
research/notes/       書籍から抽出した一次ノート
research/external/    公開標準の調査結果（URLと確認日つき）
research/extracted/   PDFから抽出した本文（Git管理外）
research/cross-reference.md   原則 × 出典の突き合わせ（本編）
research/cross-reference-ai.md  同じもの（AI向けの別冊）
research/experiments/ 自分で測った実験の材料・道具・結果
reviews/              独立レビューの記録（結果はここに置く）
tools/                検査・生成・レビュー用プロンプト組み立てのスクリプト
site/                 生成したHTML（Git管理外）。別冊は site/ai/ に出る
build/zensical/       Zensical に渡す docs/ の写し（生成物・Git管理外）
site-zensical/        Zensical が生成したHTML（Git管理外）
references/           参考書のPDF（Git管理外）
```

## この標準の作り方

3つのAIで分担した。

| 担当 | 作業 |
|---|---|
| Claude（Opus 5） | 全体設計、出典の突き合わせ、標準本文の執筆、検査ツールの作成 |
| Codex（gpt-5.6） | 書籍4冊の一次ノート作成、テンプレートの下書き |
| Antigravity（agy） | 公開標準の一次情報調査（URLと確認日の記録） |

**Codex と Antigravity の出力には、未検証の記述が含まれる可能性がある。** そのため、`research/notes/` の各ファイル冒頭にその旨を明記し、標準本文に載せた主張は原文で裏を取っている。

### AI向けの別冊（0.1.0）での分担

| 担当 | 作業 | 結果 |
|---|---|---|
| Claude（Opus 5） | 全体設計、Web の一次調査、原文での裏取り、実験の設計と実施、本文の執筆 | 完了 |
| Antigravity（agy） | 公開仕様・研究の独立調査（URLと確認日の記録） | **完了。4件中3件** |
| Codex | 書籍3冊の一次ノート | **未完了。45分で1件も返らず、作業を止めた** |
| Codex | 実験での2つ目のモデルとしての回答 | 完了 |
| Antigravity（agy） | **独立レビュー** | 完了。20件を指摘。**数値と集計の誤りに強かった** |
| Codex | **独立レビュー** | **3本すべて完了**（いずれも大きく遅延）。59件を指摘。**論理の整合と、測った範囲を超えた主張の検出に強かった** |

**Codex が書籍ノートを返さなかったため、Claude が抽出テキストを読んでノートを作った。** 各ノートの冒頭に、誰が作ったか、どこまで読んだかを書いている。**3冊とも全体は読んでいない。**

この過程で、補助AIの出力に実際の誤りが出た。**隠さずに記録し、別冊の [06章](docs-ai/06-verifying-ai-writing.md) の根拠として使っている。** 記録は [research/experiments/SRC-AIEXP-002-build-log.md](research/experiments/SRC-AIEXP-002-build-log.md) にある。

**2者の独立レビューで計79件の指摘を受け、78件を直した。** 2者の傾向ははっきり違った。Antigravity は出典の集計誤りを3か所、Codex は規則どうしが両立しない箇所を多く見つけた。**どちらか一方では見つからない指摘が両方にあった。** 判定と対応、および**残っている穴**は [reviews/2026-08-31-ai-volume-review.md](reviews/2026-08-31-ai-volume-review.md) にある。

## 制約

- 参考書のPDFは購入者ウォーターマークを含むため、Git に入れない。長文の転載もしない。
- 出典の無い主張は書かない。私見を書く場合は「出典なし・私見」と明記する。
- 数値（50字、7項目、3階層など）はすべて単一出典に由来する。目安であって合否の基準ではない。
- **AI向けの別冊の根拠は、本編より速く古くなる。** 別冊は再確認の期限（2027-02-28）を冒頭に持つ。

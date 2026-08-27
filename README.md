# エンジニアのためのドキュメント標準

| 項目 | 内容 |
|---|---|
| これは何か | 質の高い技術文書を書き、レビューするための、根拠つきのルール集 |
| 想定読者 | 設計書・手順書・報告書・議事録を書く人。および、それらをレビューする人 |
| 読んだあとできること | 良い文書を書ける。レビューで「なぜダメか」と「どう直すか」を説明できる |
| 保守責任者 | このリポジトリの保守担当 |
| 最終確認日 | 2026-08-28 |

## 3行で

1. **良い文書とは、読者が必要な判断と行動を、最小の労力で、正しく行える文書である。**
2. **読者は最初から順に読まない。** 実測で79%が走査し、1語ずつ読むのは16%である。
3. **「読みにくい」は指摘ではない。** 品質6軸のどれに当たるかを言うと、直す場所が決まる。

## 何から読むか

**本文は [docs/index.md](docs/index.md) から始まる。**

| 目的 | 読むもの |
|---|---|
| 自分の「読みやすさ」の感覚が正しいか確かめたい | [docs/09-your-instincts.md](docs/09-your-instincts.md) |
| レビューで指摘できるようになりたい | [docs/06-review.md](docs/06-review.md) |
| 悪い例と直し方を見たい | [docs/07-antipatterns.md](docs/07-antipatterns.md) |
| いま書く文書の型がほしい | [templates/](templates/) |
| 手元に1枚置きたい | [docs/appendix-checklist.md](docs/appendix-checklist.md) |

## 何が根拠になっているか

書籍4冊と、公開されている標準・実験結果6件を突き合わせた。**独立した3出典以上が支持する原則だけをルールにした。**

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

## 使い方

検査も生成も Docker で完結する。ホストには何もインストールしない。

### 作業用のイメージを作る

```bash
docker build -t edocs-tools -f tools/Dockerfile tools/
```

### 文書を検査する

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-tools python tools/doc_lint.py
```

特定のファイルだけを検査する場合は、パスを渡す。

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-tools python tools/doc_lint.py docs/04-sentences.md
```

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

### 図を書き出す

```bash
bash tools/export_diagrams.sh
```

図の方式の使い分けは [docs/adr/ADR-001-diagram-tool.md](docs/adr/ADR-001-diagram-tool.md) に記録している。

### サイトを作って見る

図の描画に使う Mermaid を先に取得する。クローン直後に一度だけ実行する。

```bash
bash tools/fetch_vendor.sh
```

そのうえでサイトを作り、開く。

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-tools python tools/build_site.py
python3 -m http.server 8765 --directory site
```

`http://127.0.0.1:8765/` を開く。**生成したサイトは外部への通信を行わない。**
そのために、閲覧時ではなくビルド前に Mermaid を取得している。

## フォルダ構成

```
docs/                 標準の本文（Markdown が正本）
docs/adr/             この標準自身の決定記録
templates/            文書型ごとのテンプレート8種
diagrams/src/         図の正本（.mmd / .drawio / 手書き .svg）
diagrams/export/      書き出したSVG（生成物）
research/notes/       書籍から抽出した一次ノート
research/external/    公開標準の調査結果（URLと確認日つき）
research/extracted/   PDFから抽出した本文（Git管理外）
research/cross-reference.md   原則 × 出典の突き合わせ
tools/                検査・生成のためのスクリプト
site/                 生成したHTML（Git管理外）
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

## 制約

- 参考書のPDFは購入者ウォーターマークを含むため、Git に入れない。長文の転載もしない。
- 出典の無い主張は書かない。私見を書く場合は「出典なし・私見」と明記する。
- 数値（50字、7項目、3階層など）はすべて単一出典に由来する。目安であって合否の基準ではない。

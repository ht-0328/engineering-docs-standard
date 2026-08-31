# 参考書について

このフォルダには、ドキュメント標準を検討する際に参照する書籍のPDFを保存します。

ここにあるPDFは、次のいずれにも該当しません。

- このプロジェクトが作成した標準本体
- 3AIの議論記録
- プロジェクトの決定記録
- 書籍を読んで作成した調査結果や要約
- 標準を適用した検証結果

## ファイル名の付け方

**英語の小文字とハイフンで書きます。** 日本語のファイル名は使いません。

翻訳書は**原書名**を使います。日本語独自の本は、書名を英語にしたものを使います。

| 書名 | ファイル名 |
|---|---|
| Prompt Engineering for LLMs（翻訳書） | `prompt-engineering-for-llms.pdf` |
| 技術者のためのテクニカルライティング入門講座 第2版 | `technical-writing-for-engineers-2nd-edition.pdf` |

## 収録している本

### 本編（人が読む文書の標準）で使う4冊

| 出典ID | ファイル名 |
|---|---|
| `SRC-WRITE-001` | `effective-explanation-patterns.pdf` |
| `SRC-WRITE-002` | `practical-markdown-writing-for-it-engineers.pdf` |
| `SRC-WRITE-003` | `technical-writing-for-engineers-2nd-edition.pdf` |
| `SRC-WRITE-004` | `writing-techniques-for-engineers-revised-edition.pdf` |

### AI向けの別冊で使う3冊

| 出典ID | ファイル名 |
|---|---|
| `SRC-AI-001` | `prompt-engineering-for-llms.pdf` |
| `SRC-AI-002` | `building-applications-with-ai-agents.pdf` |
| `SRC-AI-003` | `generative-ai-design-patterns.pdf` |

出典IDとファイル名の対応は [tools/extract_pdf.py](../tools/extract_pdf.py) の `SOURCE_IDS` にあります。**本を足すときは、そこにも追記します。**

## 本文の取り出し方

Docker の中で実行します。ホストには何も入れません。

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-tools python tools/extract_pdf.py
```

追加した本だけを処理する場合は、ファイル名を渡します。

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-tools \
  python tools/extract_pdf.py prompt-engineering-for-llms.pdf
```

出力先は `research/extracted/` です。**原本の複製にあたるためGit管理しません。**

## Git に入れない理由

**PDFは購入者を示す情報を含みます。** そのため [.gitignore](../.gitignore) で除外しています。長文の転載もしません。

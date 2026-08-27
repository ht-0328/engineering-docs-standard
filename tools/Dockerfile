# このプロジェクトの作業用イメージ。ホストには何もインストールしない。
# 用途: PDFからのテキスト抽出、Markdownからの静的サイト生成、文章の機械チェック。
FROM python:3.14-slim-trixie

# poppler-utils は pdftotext を提供する。日本語PDFのレイアウト保持抽出に使う。
# poppler-data は Adobe-Japan1 などのCJK用CIDマッピングを提供する。これが無いと
# 日本語PDFの本文がCID番号のまま出力され、文字化けする。
RUN apt-get update \
 && apt-get install -y --no-install-recommends poppler-utils poppler-data \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
      pypdf==6.1.1 \
      markdown-it-py==3.0.0 \
      mdit-py-plugins==0.4.2 \
      Pygments==2.19.2 \
      PyYAML==6.0.2

WORKDIR /w

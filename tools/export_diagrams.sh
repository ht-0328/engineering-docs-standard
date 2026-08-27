#!/usr/bin/env bash
# 図の正本（diagrams/src/）から、サイトに埋め込む SVG（diagrams/export/）を作る。
#
#   bash tools/export_diagrams.sh
#
# ホストには draw.io をインストールしない。Docker の headless 版を使う。
#
# 注意点が3つある。いずれも実測で分かったことである。
#
# 1. --user を付けないと、書き出したファイルの所有者が root になる。
# 2. --user を付けると HOME が無くなり、Electron が黙って失敗する。HOME=/tmp を渡す。
# 3. 入力にディレクトリを渡すと、draw.io が .mmd まで図として扱い、同名の出力を
#    上書きする。.drawio だけを1件ずつ渡す。

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/diagrams/src"
OUT="$ROOT/diagrams/export"
IMAGE="rlespinasse/drawio-desktop-headless:latest"

mkdir -p "$OUT"
shopt -s nullglob

# --- draw.io → SVG -----------------------------------------------------------
for file in "$SRC"/*.drawio; do
  name="$(basename "$file" .drawio)"
  echo "draw.io: $name.drawio -> $name.svg"
  docker run --rm \
    --user "$(id -u):$(id -g)" \
    -e HOME=/tmp \
    -v "$ROOT/diagrams:/data" \
    "$IMAGE" \
    -x -f svg -o "/data/export/$name.svg" "/data/src/$name.drawio" \
    2>/dev/null
done

# --- 手書きSVG → そのまま複製 -------------------------------------------------
for file in "$SRC"/*.svg; do
  echo "手書きSVG: $(basename "$file")"
  cp "$file" "$OUT/$(basename "$file")"
done

# Mermaid（*.mmd）は変換しない。Markdown 内のフェンスとして書き、閲覧時に描画する。

echo
echo "完了: $OUT"
ls -l "$OUT" | awk 'NR>1 {printf "  %8d bytes  %s\n", $5, $9}'

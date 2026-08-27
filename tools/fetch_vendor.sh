#!/usr/bin/env bash
# サイトへ同梱する外部ライブラリを取得する。
#
#   bash tools/fetch_vendor.sh
#
# 取得したファイルは tools/vendor/ に置く。3.5MB あり、再取得できるため
# Git では追跡しない。サイトを作る前に一度だけ実行する。
#
# 生成したサイトは外部への通信を一切行わない。そのために、閲覧時ではなく
# ビルド前にここで取得しておく。

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR="$ROOT/tools/vendor"

# 版と検証値を固定する。更新するときは、両方を同時に書き換える。
MERMAID_URL="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"
MERMAID_SHA256="581ed7d74bd9048d0e3a91363927d72ef22942d7722546b27f7cc29e35390eb8"

mkdir -p "$VENDOR"
target="$VENDOR/mermaid.min.js"

if [ -f "$target" ] && echo "$MERMAID_SHA256  $target" | sha256sum -c --status; then
  echo "mermaid.min.js は取得済み（検証値が一致）"
  exit 0
fi

echo "取得する: $MERMAID_URL"
curl -sSL -o "$target.tmp" "$MERMAID_URL"

actual="$(sha256sum "$target.tmp" | awk '{print $1}')"
if [ "$actual" != "$MERMAID_SHA256" ]; then
  rm -f "$target.tmp"
  echo "検証値が一致しない。" >&2
  echo "  期待: $MERMAID_SHA256" >&2
  echo "  実際: $actual" >&2
  echo "配布物が更新された可能性がある。内容を確認したうえで、このスクリプトの" >&2
  echo "MERMAID_SHA256 を書き換えること。" >&2
  exit 1
fi

mv "$target.tmp" "$target"
echo "完了: $target"
ls -l "$target" | awk '{printf "  %d bytes\n", $5}'

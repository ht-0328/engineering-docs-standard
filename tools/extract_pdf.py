#!/usr/bin/env python3
"""参考書PDFから本文テキストを取り出す。

このスクリプトはDockerコンテナ内で実行する。ホストには何もインストールしない。

    docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/w" -w /w edocs-tools python tools/extract_pdf.py

引数にPDFのファイル名を渡すと、その本だけを処理する。追加した本だけを抽出するときに使う。

    ... python tools/extract_pdf.py prompt-engineering-for-llms.pdf

対象のPDFは標準セキュリティハンドラで暗号化されているが、ユーザーパスワードは
空である。つまり閲覧は自由で、印刷やコピーだけが制限されている。空文字で復号する。

抽出は2方式で行い、両方を残して比較できるようにする。

- pypdf      : ページ単位の抽出。ページ番号との対応が正確。
- pdftotext  : popplerによる抽出。日本語の段組みと見出しの保持に強い。

出力は research/extracted/ に置く。原本の複製にあたるためGit管理はしない。
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "references"
OUT_DIR = ROOT / "research" / "extracted"

# 出典IDは triad-orchestrator/docs/knowledge/source-catalog.md の採番を継承する。
#
# SRC-WRITE-xxx は人向けの文書術を扱う本編（docs/）の出典である。
# SRC-AI-xxx は AI 向けの別冊（docs-ai/）の出典である。番号は別に振る。
SOURCE_IDS: dict[str, str] = {
    "effective-explanation-patterns.pdf": "SRC-WRITE-001",
    "practical-markdown-writing-for-it-engineers.pdf": "SRC-WRITE-002",
    "technical-writing-for-engineers-2nd-edition.pdf": "SRC-WRITE-003",
    "writing-techniques-for-engineers-revised-edition.pdf": "SRC-WRITE-004",
    "prompt-engineering-for-llms.pdf": "SRC-AI-001",
    "building-applications-with-ai-agents.pdf": "SRC-AI-002",
    "generative-ai-design-patterns.pdf": "SRC-AI-003",
}


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_with_pypdf(pdf_path: Path, out_path: Path) -> tuple[int, int]:
    """pypdfで抽出する。戻り値は (総ページ数, 本文が取れたページ数)。"""
    reader = PdfReader(str(pdf_path))
    if reader.is_encrypted:
        # 空のユーザーパスワードで開く。失敗したら例外を投げて止める。
        if reader.decrypt("") == 0:
            raise RuntimeError(f"{pdf_path.name}: 空パスワードで復号できなかった")

    lines: list[str] = []
    filled = 0
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            filled += 1
        lines.append(f"\n===== PAGE {index} =====\n{text}")

    out_path.write_text("".join(lines), encoding="utf-8")
    return len(reader.pages), filled


def extract_with_pdftotext(pdf_path: Path, out_path: Path) -> bool:
    """popplerのpdftotextで抽出する。使えない環境ではFalseを返す。"""
    try:
        subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), str(out_path)],
            check=True,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        print(f"  pdftotext は使えなかった: {error}", file=sys.stderr)
        return False
    return True


def write_info(pdf_path: Path, out_path: Path, source_id: str, pages: int, filled: int) -> None:
    reader = PdfReader(str(pdf_path))
    if reader.is_encrypted:
        reader.decrypt("")
    meta = reader.metadata or {}

    rows = [
        f"source_id: {source_id}",
        f"file: {pdf_path.name}",
        f"sha256: {sha256_of(pdf_path)}",
        f"pages: {pages}",
        f"pages_with_text: {filled}",
        f"title: {meta.get('/Title', '')}",
        f"author: {meta.get('/Author', '')}",
        f"subject: {meta.get('/Subject', '')}",
        f"creator: {meta.get('/Creator', '')}",
        f"producer: {meta.get('/Producer', '')}",
    ]
    out_path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 引数でPDFのファイル名を指定できる。指定が無ければ references/ の全部を処理する。
    # 抽出ずみの本をやり直さずに、追加した本だけを処理するために使う。
    if argv:
        pdfs = [SRC_DIR / name for name in argv]
        missing = [p for p in pdfs if not p.is_file()]
        if missing:
            for path in missing:
                print(f"見つからない: {path}", file=sys.stderr)
            return 1
    else:
        pdfs = sorted(SRC_DIR.glob("*.pdf"))

    if not pdfs:
        print(f"PDFが見つからない: {SRC_DIR}", file=sys.stderr)
        return 1

    for pdf_path in pdfs:
        source_id = SOURCE_IDS.get(pdf_path.name, pdf_path.stem)
        print(f"{source_id}  {pdf_path.name}")

        pages, filled = extract_with_pypdf(pdf_path, OUT_DIR / f"{source_id}.pypdf.txt")
        print(f"  pypdf     : {filled}/{pages} ページで本文を取得")

        if extract_with_pdftotext(pdf_path, OUT_DIR / f"{source_id}.poppler.txt"):
            size = (OUT_DIR / f"{source_id}.poppler.txt").stat().st_size
            print(f"  pdftotext : {size:,} バイト")

        write_info(pdf_path, OUT_DIR / f"{source_id}.info.txt", source_id, pages, filled)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

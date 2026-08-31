#!/usr/bin/env python3
"""書き方の違いが、AIの正答率を変えるかどうかを実測する。

この道具は、同じ事実を2通りに書いた文書を用意し、同じ質問を投げて、
正答率を比べる。手元にある `agy`（Gemini）と `codex` を呼ぶため、
API鍵は要らない。

    python3 research/experiments/run_experiment.py --exp exp1 --model agy --trials 3

**この道具はホストで動かす。** Docker の中からは agy と codex を呼べない。

## 測るもの

実験1（exp1）は、2つの段階に分けて測る。

1. **検索**: 質問に対して、正しい節が選ばれるか。
2. **解答**: 選ばれた節だけを渡したとき、正しく答えられるか。

検索は決まった手続き（文字2つ組の重なり）で行う。モデルを使わないため、
何度実行しても同じ結果になる。**書き方の違いだけが結果を動かす。**

## 結果の残し方

`research/experiments/results/` に JSON で残す。実施日、モデル名、
試行回数、生の応答をすべて含める。**後から同じ手順で確かめられるようにする。**
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

# 「わからない」と答えたことを検出する語。表記のゆれを吸収する。
UNKNOWN_WORDS = ("わからない", "分からない", "不明", "判断できない", "特定できない")


def split_sections(markdown: str) -> list[tuple[str, str]]:
    """`## ` の見出しで節に分ける。戻り値は (見出し, 節の全文) の一覧。

    節の全文には見出しの行を含める。検索する側は見出しも手がかりにするためである。
    """
    parts: list[tuple[str, str]] = []
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in markdown.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                parts.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = line[3:].strip()
            current_lines = [line]
        elif current_heading is not None:
            current_lines.append(line)

    if current_heading is not None:
        parts.append((current_heading, "\n".join(current_lines).strip()))
    return parts


def bigrams(text: str) -> set[str]:
    """文字2つ組の集合を返す。日本語を語に分けずに重なりを測るための簡便な方法である。"""
    cleaned = re.sub(r"\s+", "", text)
    return {cleaned[i : i + 2] for i in range(len(cleaned) - 1)}


def retrieve(question: str, sections: list[tuple[str, str]]) -> tuple[str, str, float]:
    """質問に最も近い節を1つ返す。戻り値は (見出し, 本文, 得点)。

    得点は、質問の文字2つ組のうち、その節にも現れるものの割合である。
    **モデルを使わない。** そのため何度実行しても同じ節が選ばれる。
    """
    query = bigrams(question)
    best = ("", "", -1.0)
    for heading, body in sections:
        overlap = len(query & bigrams(body))
        score = overlap / len(query) if query else 0.0
        if score > best[2]:
            best = (heading, body, score)
    return best


def build_prompt(chunk: str, question: str) -> str:
    return (
        "次の文章だけを根拠にして、質問に答えてください。\n"
        "あなたの一般知識で補ってはいけません。\n\n"
        "答えの値だけを1行で書いてください。説明を書かないでください。\n"
        "文章から確実に決められない場合は、「わからない」とだけ書いてください。\n\n"
        "--- 文章ここから ---\n"
        f"{chunk}\n"
        "--- 文章ここまで ---\n\n"
        f"質問: {question}\n"
    )


def call_agy(prompt: str, timeout: int) -> str:
    proc = subprocess.run(
        ["agy", "--print-timeout", "10m", "--print", prompt],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.stdout.strip()


def call_codex(prompt: str, timeout: int) -> str:
    with_out = RESULTS / f".codex-out-{time.time_ns()}.txt"
    try:
        subprocess.run(
            [
                "codex",
                "exec",
                "--sandbox",
                "read-only",
                "--skip-git-repo-check",
                "-o",
                str(with_out),
                prompt,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return with_out.read_text(encoding="utf-8").strip() if with_out.exists() else ""
    finally:
        with_out.unlink(missing_ok=True)


CALLERS = {"agy": call_agy, "codex": call_codex}


def judge(answer: str, expected: str) -> str:
    """応答を3つに分ける。correct（正しい）、unknown（わからないと答えた）、wrong（誤り）。

    判定にモデルを使わない。**文字列の一致だけで決める。**
    そのため、期待する答えは数値やアドレスなど、一意に書けるものに限っている。
    """
    if not answer:
        return "empty"
    normalized = answer.replace(",", "").replace("，", "")
    if expected in normalized:
        return "correct"
    if any(word in answer for word in UNKNOWN_WORDS):
        return "unknown"
    return "wrong"


def run_exp1(model: str, trials: int, timeout: int, workers: int) -> dict:
    exp_dir = ROOT / "exp1-self-contained"
    questions = json.loads((exp_dir / "questions.json").read_text(encoding="utf-8"))
    # 2つの要因を組み合わせた4版で測る。
    #   見出し: 具体的か、一般的か
    #   本文  : 自己完結しているか、前の節に依存しているか
    # これにより、**どちらの要因が効いているか**を切り分けられる。
    version_files = {
        "A-具体見出し-自己完結本文": "A-self-contained.md",
        "B-一般見出し-依存本文": "B-dependent.md",
        "C-一般見出し-自己完結本文": "C-generic-heading.md",
        "D-具体見出し-依存本文": "D-heading-only.md",
    }
    versions = {
        name: (exp_dir / "fixtures" / filename).read_text(encoding="utf-8")
        for name, filename in version_files.items()
    }

    jobs = []
    for version, text in versions.items():
        sections = split_sections(text)
        # B版は見出しが一般的なため、答えのある節を機械的に選べない。
        # そこで、期待する答えの文字列を含む節を「正解の節」とする。
        answer_section = {}
        for question in questions:
            for heading, body in sections:
                if question["expect"] in body.replace(",", ""):
                    answer_section[question["id"]] = (heading, body)
                    break

        for question in questions:
            heading, body, score = retrieve(question["q"], sections)
            # 検索が当たったかどうかは、答えのある節が選ばれたかで判定する。
            oracle_heading, oracle_body = answer_section[question["id"]]
            hit = heading == oracle_heading

            # 3つの条件で測る。
            #   retrieved: 検索が返した節を渡す。検索と解答の両方の影響が出る。
            #   oracle   : 答えのある節を必ず渡す。**解答だけの影響が出る。**
            #   mismatch : **もう一方のジョブの節を渡す。** 検索が外したときに何が起きるかを見る。
            #              この条件での正しい振る舞いは「わからない」である。
            #              値を答えたら、それは渡していない事実を作ったことになる。
            conditions = {
                "retrieved": (heading, body),
                "oracle": (oracle_heading, oracle_body),
            }
            partner = question.get("partner")
            if partner and partner in answer_section:
                conditions["mismatch"] = answer_section[partner]
            for condition, (given_heading, given_body) in conditions.items():
                for trial in range(trials):
                    jobs.append(
                        {
                            "version": version,
                            "condition": condition,
                            "question_id": question["id"],
                            "question": question["q"],
                            "expected": question["expect"],
                            "given_heading": given_heading,
                            "retrieval_score": round(score, 4),
                            "retrieval_hit": hit,
                            "trial": trial + 1,
                            "prompt": build_prompt(given_body, question["q"]),
                        }
                    )

    caller = CALLERS[model]

    def execute(job: dict) -> dict:
        started = time.time()
        try:
            answer = caller(job["prompt"], timeout)
            error = None
        except Exception as exc:  # noqa: BLE001 - 失敗もそのまま記録する
            answer, error = "", f"{type(exc).__name__}: {exc}"
        record = {key: value for key, value in job.items() if key != "prompt"}
        record["answer"] = answer
        if job["condition"] == "mismatch":
            # もう一方の節を渡した条件では、「わからない」が正しい振る舞いである。
            # 期待する値を答えたら、それは渡していない事実を作ったことになる。
            raw = judge(answer, job["expected"])
            if raw == "unknown":
                record_verdict = "correct"
            elif raw == "correct":
                record_verdict = "fabricated"
            else:
                record_verdict = "other"
            record["verdict"] = record_verdict
            record["raw_verdict"] = raw
        else:
            record["verdict"] = judge(answer, job["expected"])
        record["error"] = error
        record["seconds"] = round(time.time() - started, 1)
        print(
            f"  {job['version']:<26} {job['condition']:<9} {job['question_id']} "
            f"試行{job['trial']} → {record['verdict']}",
            flush=True,
        )
        return record

    print(f"実験1 を開始する。呼び出し回数: {len(jobs)}  モデル: {model}")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        records = list(pool.map(execute, jobs))

    return {
        "experiment": "exp1-self-contained",
        "question": "節を自己完結させると、AIの検索と解答が正しくなるか",
        "model_cli": model,
        "trials": trials,
        "run_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "records": records,
    }


def summarize(result: dict) -> str:
    lines = []
    by_version: dict[str, list[dict]] = {}
    for record in result["records"]:
        by_version.setdefault(record["version"], []).append(record)

    lines.append(f"実験: {result['experiment']}")
    lines.append(f"モデル: {result['model_cli']}   試行: {result['trials']}   実施: {result['run_at']}")
    lines.append("")
    lines.append("| 版 | 条件 | 呼び出し | 正答 | わからない | 誤答 | 作り話 | 空 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for version, records in sorted(by_version.items()):
        for condition in ("retrieved", "oracle", "mismatch"):
            subset = [r for r in records if r["condition"] == condition]
            if not subset:
                continue
            counts = {
                v: sum(1 for r in subset if r["verdict"] == v)
                for v in ("correct", "unknown", "wrong", "empty", "fabricated", "other")
            }
            lines.append(
                f"| {version} | {condition} | {len(subset)} | "
                f"{counts['correct']} | {counts['unknown']} | {counts['wrong'] + counts['other']} | "
                f"{counts['fabricated']} | {counts['empty']} |"
            )
    lines.append("")
    retrieval = {}
    for version, records in sorted(by_version.items()):
        seen = {}
        for r in records:
            seen[r["question_id"]] = r["retrieval_hit"]
        retrieval[version] = (sum(1 for v in seen.values() if v), len(seen))
    lines.append("検索だけの結果（モデルを使わない決まった手続き）")
    lines.append("")
    lines.append("| 版 | 答えのある節が選ばれた |")
    lines.append("|---|---|")
    for version, (hit, total) in retrieval.items():
        lines.append(f"| {version} | {hit}/{total} |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp", default="exp1", choices=["exp1"])
    parser.add_argument("--model", default="agy", choices=sorted(CALLERS))
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=900, help="1回の呼び出しの制限（秒）")
    parser.add_argument("--workers", type=int, default=4, help="同時に走らせる数")
    args = parser.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    result = run_exp1(args.model, args.trials, args.timeout, args.workers)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = RESULTS / f"{result['experiment']}-{args.model}-{stamp}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(summarize(result))
    print()
    print(f"生の結果: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

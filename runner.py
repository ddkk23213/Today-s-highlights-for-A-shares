#!/usr/bin/env python3
"""三次自动分析运行脚本。

步骤（需开发者补全数据抓取与 LLM 调用）：
1. 获取行情上下文。
2. 载入对应提示词。
3. 调用 LLM 生成 Markdown。
4. 校验输出并写入日志与 CSV。
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
LOG_DIR = BASE_DIR / "logs"
CSV_PATH = BASE_DIR / "tri_daily.csv"


def detect_slot(now: dt.datetime | None = None) -> str:
    """根据当前时间推断 slot。"""
    now = now or dt.datetime.now()
    t = now.time()
    if t < dt.time(11, 30):
        return "morning"
    if t < dt.time(14, 0):
        return "noon"
    return "close"


def load_prompt(slot: str) -> str:
    path = PROMPTS_DIR / f"{slot}_prompt_zh.txt"
    return path.read_text(encoding="utf-8")


def call_llm(prompt: str, context: str) -> str:
    """调用 LLM 返回 Markdown。实际实现需开发者补全。"""
    # TODO: 接入实际的 LLM 服务
    return "# TODO\n"


def validate_close(md: str) -> None:
    """校验收盘报告的格式与字数。"""
    text_len = len(re.sub(r"\s", "", md))
    if not 150 <= text_len <= 250:
        raise ValueError("收盘内容需150-250字")
    lines = md.strip().splitlines()
    if not lines:
        raise ValueError("内容为空")
    if not re.match(r"^\d{4}年\d{2}月\d{2}日", lines[0]):
        raise ValueError("第一行需为日期")
    if len(lines) < 10:
        raise ValueError("行数不足")
    for i in range(1, 4):
        if not lines[i].startswith("结论摘要："):
            raise ValueError("结论摘要行缺失")
    for i in range(6):
        if not lines[4 + i].startswith(f"{i+1}."):
            raise ValueError("六条要点格式错误")


def write_markdown(date: dt.date, slot: str, md: str) -> Path:
    month_dir = LOG_DIR / date.strftime("%Y%m")
    month_dir.mkdir(parents=True, exist_ok=True)
    md_path = month_dir / f"{date.strftime('%Y%m%d')}_{slot}.md"
    md_path.write_text(md, encoding="utf-8")
    return md_path


def update_csv(date: dt.date, slot: str, one_liner: str, md_path: Path, sources: List[str]) -> None:
    rows = []
    if CSV_PATH.exists():
        with CSV_PATH.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    header = ["date", "slot", "one_liner", "md_path", "sources_json"]
    rows = [r for r in rows if not (r["date"] == date.isoformat() and r["slot"] == slot)]
    rows.append(
        {
            "date": date.isoformat(),
            "slot": slot,
            "one_liner": one_liner,
            "md_path": str(md_path),
            "sources_json": json.dumps(sources, ensure_ascii=False),
        }
    )
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Tri-daily analysis runner")
    parser.add_argument("--slot", choices=["morning", "noon", "close"], help="时间段")
    args = parser.parse_args()

    slot = args.slot or detect_slot()
    date = dt.date.today()

    try:
        context = ""  # TODO: 获取行情上下文
        prompt = load_prompt(slot)
        md = call_llm(prompt, context)
        if slot == "close":
            validate_close(md)
        md_path = write_markdown(date, slot, md)
        update_csv(date, slot, "TODO", md_path, [])
    except Exception as e:  # noqa: BLE001
        print(f"错误: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""阶段四：建设故事索引 docs/story_index.json。

为每集维护结构化摘要，支持快速查找角色、设定、伏笔和开放线索。
其中 `summary` 优先使用下一集的“前情回顾”，把它作为当前集的故事梗概。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STORIES_DIR = REPO_ROOT / "stories"
OUTPUT_PATH = REPO_ROOT / "docs" / "story_index.json"

KNOWN_CHARACTERS = [
    "小金", "小彩", "独眼警卫", "黑焰", "小翠", "银星", "临棱", "璃光",
    "欧米伽", "小玉", "铁大钳", "凤眼莲", "老玉米国王", "老玉米王后",
    "小玉米粒", "玉米粒", "小炭", "黄玉米婶婶", "老灰壳爷爷", "紫晶国王",
    "灰羽", "红隼", "甲虫", "蜘蛛", "水黾", "晶孩子", "月尘族",
]

KNOWN_LOCATIONS = [
    "小玉米粒王国", "星芒号", "白塔", "黑海", "天空图书馆", "中央工厂",
    "塑料大陆", "露珠议事桌", "钢铁废墟", "旧玉米田", "未来议会",
    "地球", "月球", "心镜湖", "阳光美食街", "芦苇湾", "铁鱼骨浅滩",
    "泡沫滩", "暗影峡谷", "沉默港口", "共鸣塔", "多元厅",
    "起源之种", "万界共鸣", "潮汐试炼", "月之谜",
]

SEPARATOR = "---"
RECAP_PREFIX = "**前情回顾**："
SUMMARY_MAX_LENGTH = 200
PLACEHOLDER_RECAP_PREFIXES = (
    "无，",
    "无。",
    "无，不过",
    "无，但",
    "暂无",
    "本集为第一集",
)


def parse_season_dir(dirname: str) -> tuple[int, str] | None:
    match = re.match(r"第(\d+)季_(.+)", dirname)
    if not match:
        return None
    return int(match.group(1)), match.group(2)


def parse_episode(filename: str) -> tuple[int, str] | None:
    match = re.match(r"第(\d+)集_(.+)\.md$", filename)
    if not match:
        return None
    return int(match.group(1)), match.group(2)


def truncate_text(text: str, limit: int = SUMMARY_MAX_LENGTH) -> str:
    return text.strip()[:limit]


def has_usable_recap(recap: str) -> bool:
    recap = recap.strip()
    if not recap:
        return False
    return not any(recap.startswith(prefix) for prefix in PLACEHOLDER_RECAP_PREFIXES)


def extract_metadata(filepath: Path, season: int) -> dict:
    content = filepath.read_text(encoding="utf-8")
    lines = content.splitlines()

    ep_num, title = parse_episode(filepath.name) or (0, filepath.stem)

    recap = ""
    body_start_idx = 0
    body_end_idx = len(lines)

    separators = [i for i, line in enumerate(lines) if line == SEPARATOR]
    if len(separators) >= 2:
        body_start_idx = separators[0] + 1
        body_end_idx = separators[-1]

    for line in lines:
        if line.startswith(RECAP_PREFIX):
            recap = line[len(RECAP_PREFIX):]
            break

    body_text = "\n".join(lines[body_start_idx:body_end_idx])

    characters = []
    for char in KNOWN_CHARACTERS:
        if char in body_text:
            characters.append(char)

    locations = []
    for loc in KNOWN_LOCATIONS:
        if loc in body_text:
            locations.append(loc)

    main_events = []
    event_keywords = ["发现", "建立", "签署", "学会", "决定", "出发", "到达",
                      "遭遇", "解决", "修复", "创造", "觉醒", "转化", "迁居"]
    for kw in event_keywords:
        if kw in body_text:
            main_events.append(kw)

    new_rules = []
    rule_keywords = ["规则", "约定", "法则", "定律", "原则", "协议", "协约",
                     "流程", "标准", "边界", "限制"]
    for kw in rule_keywords:
        if kw in body_text:
            new_rules.append(kw)

    ending_text = ""
    if body_end_idx > body_start_idx:
        body_lines = lines[body_start_idx:body_end_idx]
        body_str = "\n".join(body_lines)
        ending_text = body_str[-300:] if len(body_str) > 300 else body_str

    return {
        "file": str(filepath.relative_to(REPO_ROOT)),
        "season": season,
        "episode": ep_num,
        "title": title,
        "summary": "",
        "summary_source": "unavailable",
        "recap": truncate_text(recap),
        "characters": characters,
        "locations": locations,
        "main_events": main_events,
        "new_rules": new_rules,
        "ending_preview": truncate_text(ending_text),
        "_raw_recap": recap.strip(),
    }


def assign_episode_summaries(index: list[dict]) -> None:
    for idx, episode in enumerate(index):
        next_episode = index[idx + 1] if idx + 1 < len(index) else None
        if next_episode is None:
            continue

        next_recap = next_episode.get("_raw_recap", "")
        if not has_usable_recap(next_recap):
            continue

        episode["summary"] = truncate_text(next_recap)
        episode["summary_source"] = "next_episode_recap"


def build_output_index(index: list[dict]) -> list[dict]:
    return [
        {key: value for key, value in episode.items() if not key.startswith("_")}
        for episode in index
    ]


def main() -> int:
    index = []

    season_dirs = sorted(
        d for d in STORIES_DIR.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )

    for season_dir in season_dirs:
        parsed = parse_season_dir(season_dir.name)
        if not parsed:
            continue

        season_num, season_name = parsed

        md_files = sorted(season_dir.glob("*.md"))
        md_files = [f for f in md_files if "_backup" not in str(f)]

        for f in md_files:
            ep = parse_episode(f.name)
            if not ep:
                continue

            meta = extract_metadata(f, season_num)
            index.append(meta)

    index.sort(key=lambda x: (x["season"], x["episode"]))
    assign_episode_summaries(index)
    output_index = build_output_index(index)

    OUTPUT_PATH.write_text(
        json.dumps(output_index, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    total_eps = len(output_index)
    total_chars = len(set(c for ep in output_index for c in ep["characters"]))
    total_locs = len(set(l for ep in output_index for l in ep["locations"]))
    total_summaries = sum(1 for ep in output_index if ep["summary"])

    print(f"故事索引已生成：{OUTPUT_PATH}")
    print(f"  总集数：{total_eps}")
    print(f"  涉及角色：{total_chars}")
    print(f"  涉及地点：{total_locs}")
    print(f"  已生成梗概：{total_summaries}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

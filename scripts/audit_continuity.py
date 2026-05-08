#!/usr/bin/env python3
"""阶段三：相邻集连续性抽检。

对每季抽检 8-10 个相邻窗口，优先覆盖季初、季中、季末和重大设定变化集。
提取关键文本段落，输出结构化报告供人工/LLM 审查。
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STORIES_DIR = REPO_ROOT / "stories"
REPORT_DIR = REPO_ROOT / "docs" / "audit_reports"

SEPARATOR = "---"
RECAP_PREFIX = "**前情回顾**："
INTERACTION_PREFIX = "**互动时刻**"

ENDING_CHARS = 600
OPENING_CHARS = 1000


@dataclass
class EpisodeInfo:
    path: Path
    season: int
    episode: int
    title: str
    recap: str
    body: str
    ending: str


@dataclass
class ContinuityWindow:
    season: int
    prev_ep: int
    curr_ep: int
    prev_ending: str
    curr_recap: str
    curr_opening: str
    curr_ending: str


def parse_filename(filepath: Path) -> tuple[int, int, str]:
    name = filepath.stem
    match = re.match(r"第(\d+)集_(.+)", name)
    if not match:
        return 0, 0, name
    return int(match.group(1)), match.group(2)


def extract_episode_info(filepath: Path, season: int) -> EpisodeInfo:
    content = filepath.read_text(encoding="utf-8")
    lines = content.splitlines()

    ep_num, title = parse_filename(filepath)

    separators = [i for i, line in enumerate(lines) if line == SEPARATOR]

    recap = ""
    body = ""
    ending = ""

    if len(separators) >= 2:
        body_start = separators[0] + 1
        body_end = separators[-1]
        body_lines = lines[body_start:body_end]
        body = "\n".join(body_lines)

        if body_lines:
            ending_text = "\n".join(body_lines)
            ending = ending_text[-ENDING_CHARS:] if len(ending_text) > ENDING_CHARS else ending_text

    for line in lines:
        if line.startswith(RECAP_PREFIX):
            recap = line[len(RECAP_PREFIX):]
            break

    return EpisodeInfo(
        path=filepath,
        season=season,
        episode=ep_num,
        title=title,
        recap=recap,
        body=body,
        ending=ending,
    )


def get_opening(body: str) -> str:
    text = body.strip()
    return text[:OPENING_CHARS] if len(text) > OPENING_CHARS else text


def select_windows(episodes: list[EpisodeInfo]) -> list[tuple[int, int]]:
    """选择 8-10 个相邻窗口，优先覆盖季初、季中、季末。"""
    max_ep = max(ep.episode for ep in episodes)
    ep_map = {ep.episode: ep for ep in episodes}

    candidates = set()

    for start, end in [(1, 3), (max_ep - 2, max_ep)]:
        for ep in range(start, end + 1):
            if ep in ep_map and ep + 1 in ep_map:
                candidates.add((ep, ep + 1))

    mid_start = max(1, max_ep // 2 - 2)
    mid_end = min(max_ep, max_ep // 2 + 2)
    for ep in range(mid_start, mid_end + 1):
        if ep in ep_map and ep + 1 in ep_map:
            candidates.add((ep, ep + 1))

    remaining = []
    for ep in sorted(ep_map.keys()):
        if ep + 1 in ep_map and (ep, ep + 1) not in candidates:
            remaining.append((ep, ep + 1))

    import random
    random.seed(42)
    random.shuffle(remaining)

    target = 9
    selected = list(candidates)
    needed = target - len(selected)
    if needed > 0:
        selected.extend(remaining[:needed])

    selected.sort()
    return selected


def build_window(prev_ep: EpisodeInfo, curr_ep: EpisodeInfo) -> ContinuityWindow:
    return ContinuityWindow(
        season=prev_ep.season,
        prev_ep=prev_ep.episode,
        curr_ep=curr_ep.episode,
        prev_ending=prev_ep.ending,
        curr_recap=curr_ep.recap,
        curr_opening=get_opening(curr_ep.body),
        curr_ending=curr_ep.ending,
    )


def generate_report(season: int, season_name: str, windows: list[ContinuityWindow]) -> str:
    lines = []
    lines.append(f"# 第{season:02d}季 连续性抽检报告")
    lines.append("")
    lines.append(f"**季节**：{season_name}")
    lines.append(f"**抽检窗口数**：{len(windows)}")
    lines.append("")
    lines.append("## 抽检窗口")
    lines.append("")

    for w in windows:
        lines.append(f"### 窗口：第{w.prev_ep:02d}集 → 第{w.curr_ep:02d}集")
        lines.append("")
        lines.append("#### 第 N-1 集结尾")
        lines.append("")
        lines.append(w.prev_ending.strip())
        lines.append("")
        lines.append("#### 第 N 集前情回顾")
        lines.append("")
        lines.append(w.curr_recap.strip())
        lines.append("")
        lines.append("#### 第 N 集开头")
        lines.append("")
        lines.append(w.curr_opening.strip())
        lines.append("")
        lines.append("#### 第 N 集结尾")
        lines.append("")
        lines.append(w.curr_ending.strip())
        lines.append("")
        lines.append("#### 审查问题")
        lines.append("")
        lines.append("1. 第 N 集前情回顾是否准确承接第 N-1 集结尾？")
        lines.append("2. 第 N 集开头是否回应上一段经历留下的悬念？")
        lines.append("3. 本集核心冲突是否有清楚起因、过程和结果？")
        lines.append("4. 解决方案是否有铺垫、代价和限制？")
        lines.append("5. 结尾悬念是否能自然引向下一集？")
        lines.append("6. 是否出现角色能力、人物关系、地点状态或规则前后矛盾？")
        lines.append("")
        lines.append("**审查结论**：")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    season_dirs = sorted(
        d for d in STORIES_DIR.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )

    total_windows = 0

    for season_dir in season_dirs:
        match = re.match(r"第(\d+)季_(.+)", season_dir.name)
        if not match:
            continue

        season_num = int(match.group(1))
        season_name = match.group(2)

        md_files = sorted(season_dir.glob("*.md"))
        md_files = [f for f in md_files if "_backup" not in str(f)]

        episodes = []
        for f in md_files:
            ep = extract_episode_info(f, season_num)
            if ep.episode > 0:
                episodes.append(ep)

        if len(episodes) < 2:
            continue

        episodes.sort(key=lambda e: e.episode)
        ep_map = {ep.episode: ep for ep in episodes}

        window_pairs = select_windows(episodes)
        windows = []

        for prev_ep, curr_ep in window_pairs:
            if prev_ep in ep_map and curr_ep in ep_map:
                w = build_window(ep_map[prev_ep], ep_map[curr_ep])
                windows.append(w)

        if not windows:
            continue

        report = generate_report(season_num, season_name, windows)
        report_path = REPORT_DIR / f"continuity_s{season_num:02d}.md"
        report_path.write_text(report, encoding="utf-8")

        total_windows += len(windows)
        print(f"  第{season_num:02d}季：{len(windows)} 个窗口 → {report_path.name}")

    print(f"\n共生成 {total_windows} 个连续性抽检窗口。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

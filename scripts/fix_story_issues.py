#!/usr/bin/env python3
"""阶段二修复脚本：批量修复故事文件中的格式问题。

修复内容：
1. 多余 Markdown 标记（前情回顾末尾的 **）
2. 互动时刻小标题（非标准标签替换为标准四维度）
3. 文档元信息（"上一集"替换为故事世界内部表达）
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STORIES_DIR = REPO_ROOT / "stories"

INTERACTION_LABEL_MAP = {
    "智慧与知识": "智慧与宽容",
    "自我认知": "自我调节",
    "同理心": "换位思考",
    "情绪调节": "自我调节",
    "团队合作": "智慧与宽容",
    "解决问题": "智慧与宽容",
    "社交礼仪": "换位思考",
    "自我反思": "自我调节",
    "诚实与虚荣": "自我调节",
    "准备好不等于不害怕": "自我调节",
    "变化的证据": "智慧与宽容",
    "活在当下": "自我调节",
    "独立选择": "智慧与宽容",
    "遵守约定": "智慧与宽容",
    "小小的善举": "换位思考",
    "观察力": "智慧与宽容",
    "多样性": "换位思考",
    "情绪与能力": "自我调节",
    "天赋与控制": "自我调节",
    "区分场合": "换位思考",
    "接受不完美": "自我调节",
    "冷静观察": "自我调节",
    "传言与真相": "智慧与宽容",
    "适度谨慎": "自我调节",
    "生态意识": "换位思考",
    "行动力": "自我调节",
    "观察的重要性": "智慧与宽容",
    "安抚也是一种帮助": "换位思考",
    "耐心与陪伴": "自我调节",
    "尊重节奏": "换位思考",
    "倾听的力量": "换位思考",
    "成长思维": "自我调节",
    "保护自然": "换位思考",
    "诚实与谎言": "智慧与宽容",
    "克服拖延": "自我调节",
    "沟通的力量": "换位思考",
    "先问再判断": "智慧与宽容",
    "善意与误会": "换位思考",
    "线索与拼图": "智慧与宽容",
    "担心与害怕": "自我调节",
    "信息不完整时": "智慧与宽容",
    "反思的力量": "自我调节",
    "三秒钟的停顿": "自我调节",
    "规则与灵活": "智慧与宽容",
    "明辨是非": "智慧与宽容",
    "平常心": "自我调节",
    "守夜的意义": "换位思考",
    "不是英雄主义": "自我调节",
    "信息的力量": "智慧与宽容",
    "成长感悟": "自我调节",
    "信息拼图": "智慧与宽容",
    "面对威胁": "自我调节",
    "准备的力量": "自我调节",
    "生态平衡": "换位思考",
    "承认害怕": "自我调节",
    "内心的声音": "自我调节",
    "深呼吸的力量": "自我调节",
    "发现优点": "换位思考",
    "求知态度": "自我调节",
    "情绪表达": "自我调节",
    "共存智慧": "智慧与宽容",
    "信息收集": "智慧与宽容",
    "正视危险": "自我调节",
    "记录的力量": "智慧与宽容",
}

QUESTION_LINE_PATTERN = re.compile(
    r"^(?P<index>[1-4])\. \*\*(?P<label>[^*]+)\*\*：(?P<question>.+)$"
)

RECAP_EXTRA_MARKDOWN_PATTERN = re.compile(r"^(\*\*前情回顾\*\*：.*)\*\*$")

DOC_META_REPLACEMENTS = [
    (re.compile(r"在上一集中，"), "在上一次事件中，"),
    (re.compile(r"上一集中，"), "上一次事件中，"),
    (re.compile(r"上一集，"), "上一次事件，"),
    (re.compile(r"在上一集里"), "在上一次事件里"),
    (re.compile(r"上一集里"), "上一次事件里"),
    (re.compile(r"在上一集$"), "在上一次事件"),
    (re.compile(r"上一集$"), "上一次事件"),
    (re.compile(r"下一集中，"), "下一次事件中，"),
    (re.compile(r"下一集，"), "下一次事件，"),
    (re.compile(r"在下一集里"), "在下一次事件里"),
    (re.compile(r"下一集里"), "下一次事件里"),
    (re.compile(r"下一集"), "下一次事件"),
    (re.compile(r"这一集中，"), "这一次事件中，"),
    (re.compile(r"这一集，"), "这一次事件，"),
    (re.compile(r"在这一集里"), "在这一次事件里"),
    (re.compile(r"这一集里"), "这一次事件里"),
    (re.compile(r"这一集"), "这一次事件"),
]


def fix_file(filepath: Path) -> tuple[int, list[str]]:
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return 0, [f"读取失败: {e}"]

    original = content
    changes = []

    content = fix_extra_markdown(content, changes)
    content = fix_interaction_labels(content, changes)
    content = fix_doc_meta(content, changes)

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return len(changes), changes

    return 0, changes


def fix_extra_markdown(content: str, changes: list[str]) -> str:
    lines = content.splitlines()
    modified = False

    for i, line in enumerate(lines):
        match = RECAP_EXTRA_MARKDOWN_PATTERN.match(line)
        if match:
            lines[i] = match.group(1)
            modified = True
            changes.append(f"  第 {i+1} 行：移除前情回顾末尾多余 **")

    if modified:
        return "\n".join(lines) + "\n"
    return content


def fix_interaction_labels(content: str, changes: list[str]) -> str:
    lines = content.splitlines()
    modified = False

    for i, line in enumerate(lines):
        match = QUESTION_LINE_PATTERN.match(line)
        if not match:
            continue

        label = match.group("label").strip()
        if label in INTERACTION_LABEL_MAP:
            new_label = INTERACTION_LABEL_MAP[label]
            index = match.group("index")
            question = match.group("question")
            lines[i] = f"{index}. **{new_label}**：{question}"
            modified = True
            changes.append(f"  第 {i+1} 行：互动小标题 \"{label}\" → \"{new_label}\"")

    if modified:
        return "\n".join(lines) + "\n"
    return content


def fix_doc_meta(content: str, changes: list[str]) -> str:
    lines = content.splitlines()
    modified = False

    for i, line in enumerate(lines):
        if line.startswith("# "):
            continue

        new_line = line
        for pattern, replacement in DOC_META_REPLACEMENTS:
            if pattern.search(new_line):
                new_line = pattern.sub(replacement, new_line)
                if new_line != line:
                    modified = True
                    changes.append(
                        f"  第 {i+1} 行：文档元信息替换 → \"{replacement}\""
                    )
                    line = new_line

        if modified:
            lines[i] = new_line

    if modified:
        return "\n".join(lines) + "\n"
    return content


def main() -> int:
    files = sorted(STORIES_DIR.rglob("*.md"))
    files = [f for f in files if "_backup" not in f.parts]

    total_fixes = 0
    files_modified = 0

    for filepath in files:
        count, changes = fix_file(filepath)
        if count > 0:
            files_modified += 1
            total_fixes += count
            rel = filepath.relative_to(REPO_ROOT)
            print(f"📝 {rel} ({count} 处修改)")
            for change in changes:
                print(change)

    print(f"\n修复完成：修改 {files_modified} 个文件，共 {total_fixes} 处。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

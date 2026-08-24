#!/usr/bin/env python3
"""按指定模板校验 stories 下正文 Markdown 的头尾格式。"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
import re


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent
DEFAULT_STORIES_DIR = REPO_ROOT / "stories"
EXCLUDED_VALIDATION_FILES = {
    (DEFAULT_STORIES_DIR / "第01季_生存与重生/第01集_灰霉蚧危机.md").resolve(),
}
QUESTION_PATTERN = re.compile(
    r"^(?P<index>[1-4])\. \*\*(?P<label>[^*]+)\*\*：(?P<question>.+)$"
)
EXPECTED_INTERACTION_LABELS = (
    "自我调节",
    "换位思考",
    "智慧与宽容",
    "悬念预测",
)
RECAP_PATTERN = re.compile(r"^\*\*前情回顾\*\*：.+$")


@dataclass(frozen=True)
class ValidationIssue:
    line_no: int | None
    message: str


@dataclass(frozen=True)
class ValidationResult:
    path: Path
    issues: list[ValidationIssue]

    @property
    def passed(self) -> bool:
        return not self.issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="校验故事 Markdown 是否符合“标题 + 前情回顾 + 正文 + 互动时刻”模板。"
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help="待校验的文件或目录；不传时默认扫描 stories/。",
    )
    parser.add_argument(
        "--include-backup",
        action="store_true",
        help="默认会跳过 _backup 目录；添加此参数可一并校验。",
    )
    return parser.parse_args()


def normalize_lines(text: str) -> list[str]:
    text = text.lstrip("\ufeff")
    return [line.rstrip() for line in text.splitlines()]


def collect_files(targets: list[str], include_backup: bool) -> list[Path]:
    raw_targets = [Path(target).expanduser() for target in targets] if targets else [DEFAULT_STORIES_DIR]
    files: set[Path] = set()

    for target in raw_targets:
        resolved = target.resolve()
        if not resolved.exists():
            print(f"警告：路径不存在，已跳过：{target}", file=sys.stderr)
            continue

        if resolved.is_file():
            if resolved.suffix.lower() == ".md" and should_include(resolved, include_backup):
                files.add(resolved)
            continue

        for path in resolved.rglob("*.md"):
            if should_include(path, include_backup):
                files.add(path.resolve())

    return sorted(files)


def should_include(path: Path, include_backup: bool) -> bool:
    resolved = path.resolve()
    return (include_backup or "_backup" not in resolved.parts) and resolved not in EXCLUDED_VALIDATION_FILES


def relative_display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def validate_file(path: Path) -> ValidationResult:
    issues: list[ValidationIssue] = []

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return ValidationResult(path, [ValidationIssue(None, f"文件不是有效的 UTF-8 编码：{exc}")])

    lines = normalize_lines(content)
    while lines and lines[-1] == "":
        lines.pop()

    if not lines:
        return ValidationResult(path, [ValidationIssue(None, "文件为空。")])

    expected_title = f"# {path.stem}"
    issues.extend(validate_unique_sections(lines))
    issues.extend(validate_opening(lines, expected_title))
    issues.extend(validate_body(lines))
    issues.extend(validate_recap_word_count(lines))
    issues.extend(validate_word_count(lines))
    issues.extend(validate_ending(lines))

    return ValidationResult(path, issues)


def validate_unique_sections(lines: list[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    recap_indices = [
        index for index, line in enumerate(lines) if line.startswith("**前情回顾**")
    ]
    interaction_indices = [
        index for index, line in enumerate(lines) if line.startswith("**互动时刻**")
    ]

    if len(recap_indices) > 1:
        issues.append(
            ValidationIssue(
                recap_indices[1] + 1,
                "“前情回顾”区块只能出现一次。",
            )
        )

    if len(interaction_indices) > 1:
        issues.append(
            ValidationIssue(
                interaction_indices[1] + 1,
                "“互动时刻”区块只能出现一次。",
            )
        )

    return issues


def validate_opening(lines: list[str], expected_title: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if line_at(lines, 0) != expected_title:
        issues.append(ValidationIssue(1, f'标题应为 "{expected_title}"。'))

    if line_at(lines, 1) != "":
        issues.append(ValidationIssue(2, "标题后应空一行。"))

    recap_line = line_at(lines, 2)
    if recap_line is None:
        issues.append(ValidationIssue(3, "缺少“前情回顾”行。"))
    elif not RECAP_PATTERN.fullmatch(recap_line):
        issues.append(ValidationIssue(3, '“前情回顾”应写成同一行：`**前情回顾**：内容`。'))

    if line_at(lines, 3) != "":
        issues.append(ValidationIssue(4, "“前情回顾”后应空一行。"))

    if line_at(lines, 4) != "---":
        issues.append(ValidationIssue(5, "正文前应有单独一行的 `---` 分隔线。"))

    return issues


LEFT_DQ = "\u201c"   # “
RIGHT_DQ = "\u201d"  # ”
FORBIDDEN_DOCUMENT_TERMS = (
    "上一集",
    "这一集",
    "下一集",
    "本集",
    "这几集",
    "上一季",
    "这一季",
    "下一季",
)


def validate_body(lines: list[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    separator_indices = [index for index, line in enumerate(lines) if line == "---"]

    if len(separator_indices) < 2:
        issues.append(ValidationIssue(None, "至少需要两处 `---` 分隔线，分别包住正文。"))
        return issues

    last_separator = separator_indices[-1]
    body_lines = lines[5:last_separator]
    if not any(line.strip() for line in body_lines):
        issues.append(ValidationIssue(None, "两处分隔线之间缺少正文内容。"))

    issues.extend(validate_quote_pairs(lines))
    issues.extend(validate_story_world_text(lines))

    return issues


def validate_story_world_text(lines: list[str]) -> list[ValidationIssue]:
    """检查英文直引号和跳出故事世界的文档编号用语。"""
    issues: list[ValidationIssue] = []

    for line_no, line in enumerate(lines, start=1):
        if '"' in line:
            issues.append(
                ValidationIssue(line_no, "正文不得使用英文直引号，应改为中文双引号“”。")
            )

        matched_terms = [term for term in FORBIDDEN_DOCUMENT_TERMS if term in line]
        if matched_terms:
            terms = "、".join(f"“{term}”" for term in matched_terms)
            issues.append(
                ValidationIssue(line_no, f"正文不得出现文档元信息用语：{terms}。")
            )

    return issues


def validate_quote_pairs(lines: list[str]) -> list[ValidationIssue]:
    """用状态机检查中文双引号配对：左引号“与右引号”必须正确开合。

    状态机逻辑：
    - 遇到左引号“：若已打开，则此左引号应为右引号（错配）
    - 遇到右引号”：若未打开，则此右引号应为左引号（错配）
    - 文件结束时，引号应处于关闭状态
    """
    issues: list[ValidationIssue] = []
    in_quote = False

    for line_no, line in enumerate(lines, start=1):
        for col, ch in enumerate(line, start=1):
            if ch == LEFT_DQ:
                if in_quote:
                    issues.append(
                        ValidationIssue(
                            line_no,
                            f"第 {col} 列左引号“应为右引号”（前一个引号尚未关闭）。",
                        )
                    )
                    in_quote = False
                else:
                    in_quote = True
            elif ch == RIGHT_DQ:
                if in_quote:
                    in_quote = False
                else:
                    issues.append(
                        ValidationIssue(
                            line_no,
                            f"第 {col} 列右引号”应为左引号“（此处没有未关闭的引号）。",
                        )
                    )
                    in_quote = True

    if in_quote:
        issues.append(
            ValidationIssue(None, "中文双引号未闭合：文件结束时仍有引号处于打开状态。")
        )

    return issues


RECAP_PREFIX = "**前情回顾**："


def validate_recap_word_count(lines: list[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    recap_line = line_at(lines, 2)
    if recap_line is None or not recap_line.startswith(RECAP_PREFIX):
        return issues

    recap_content = recap_line[len(RECAP_PREFIX):]
    char_count = len(recap_content)

    if char_count < 120:
        issues.append(ValidationIssue(3, f"前情回顾共 {char_count} 字，不足 120 字。"))
    elif char_count > 240:
        issues.append(ValidationIssue(3, f"前情回顾共 {char_count} 字，超过 240 字。"))

    return issues


def validate_word_count(lines: list[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    separator_indices = [index for index, line in enumerate(lines) if line == "---"]

    if len(separator_indices) < 2:
        return issues

    last_separator = separator_indices[-1]
    body_lines = lines[5:last_separator]
    char_count = sum(len(line) for line in body_lines)

    if char_count <= 2500:
        issues.append(ValidationIssue(None, f"正文总字数 {char_count} 字，不足 2500 字。"))
    elif char_count >= 6000:
        issues.append(ValidationIssue(None, f"正文总字数 {char_count} 字，超过 5999 字。"))

    return issues


def validate_ending(lines: list[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    separator_indices = [index for index, line in enumerate(lines) if line == "---"]

    if len(separator_indices) < 2:
        return issues

    last_separator = separator_indices[-1]
    tail = lines[last_separator:]

    expected_length = 8
    if len(tail) < expected_length:
        issues.append(ValidationIssue(last_separator + 1, "结尾结构不完整，应包含互动时刻标题和 4 个问题。"))
        return issues

    if last_separator > 0 and lines[last_separator - 1] != "":
        issues.append(ValidationIssue(last_separator, "`---` 前应空一行。"))

    if tail[1] != "":
        issues.append(ValidationIssue(last_separator + 2, "`---` 后应空一行。"))

    if tail[2] != "**互动时刻**：":
        issues.append(ValidationIssue(last_separator + 3, '结尾标题应为 `**互动时刻**：`。'))

    if tail[3] != "":
        issues.append(ValidationIssue(last_separator + 4, "“互动时刻”后应空一行。"))

    for offset, expected_index in enumerate(range(1, 5), start=4):
        actual = line_at(tail, offset)
        line_no = last_separator + offset + 1
        if actual is None:
            issues.append(ValidationIssue(line_no, f"缺少第 {expected_index} 条互动问题。"))
            continue

        issues.extend(validate_interaction_question(actual, expected_index, line_no))

    if len(tail) > expected_length:
        issues.append(ValidationIssue(last_separator + expected_length + 1, "第 4 条互动问题后不应再有额外内容。"))

    return issues


def line_at(lines: list[str], index: int) -> str | None:
    if 0 <= index < len(lines):
        return lines[index]
    return None


def validate_interaction_question(line: str, expected_index: int, line_no: int) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    matched = QUESTION_PATTERN.fullmatch(line)

    if not matched or int(matched.group("index")) != expected_index:
        issues.append(
            ValidationIssue(
                line_no,
                f"第 {expected_index} 条互动问题格式应与模板一致：`"
                f"{expected_index}. **小标题**：具体问题？`。",
            )
        )
        return issues

    label = matched.group("label").strip()
    question_text = matched.group("question").strip()
    expected_label = EXPECTED_INTERACTION_LABELS[expected_index - 1]

    if not label:
        issues.append(ValidationIssue(line_no, f"第 {expected_index} 条互动问题缺少加粗小标题。"))
    elif label != expected_label:
        issues.append(
            ValidationIssue(
                line_no,
                f"第 {expected_index} 条互动问题标题应为“{expected_label}”，当前为“{label}”。",
            )
        )

    if not question_text:
        issues.append(ValidationIssue(line_no, f"第 {expected_index} 条互动问题缺少具体问题内容。"))
    elif not question_text.endswith("？"):
        issues.append(ValidationIssue(line_no, f"第 {expected_index} 条互动问题应与模板一致，以中文问号“？”结尾。"))

    return issues


def main() -> int:
    args = parse_args()
    files = collect_files(args.targets, args.include_backup)

    if not files:
        print("没有找到可校验的 Markdown 文件。", file=sys.stderr)
        return 2

    results = [validate_file(path) for path in files]
    failed = [result for result in results if not result.passed]

    for result in failed:
        print(f"❌ {relative_display_path(result.path)}")
        for issue in result.issues:
            prefix = f"  - 第 {issue.line_no} 行" if issue.line_no is not None else "  - 文件级错误"
            print(f"{prefix}：{issue.message}")

    passed_count = len(results) - len(failed)
    print(
        f"\n检查完成：共扫描 {len(results)} 篇，"
        f"通过 {passed_count} 篇，未通过 {len(failed)} 篇。"
    )

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

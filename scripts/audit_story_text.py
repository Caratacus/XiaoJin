#!/usr/bin/env python3
"""故事正文文本质量审计脚本。

检测 stories/ 下所有故事文件中可能存在的文本质量问题，包括：
- 文档元信息入文（上一集、这一集、本集等）
- 英文标点混用
- 互动时刻格式问题
- 敏感/不适合儿童表达
- 长句
- 多余 Markdown 标记

输出格式：文件路径:行号 [严重程度] 问题类型：说明
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent
DEFAULT_STORIES_DIR = REPO_ROOT / "stories"

EXCLUDED_FILES: set[Path] = set()

SEVERITY_P0 = "P0"
SEVERITY_P1 = "P1"
SEVERITY_P2 = "P2"

DOC_META_PATTERNS = [
    (re.compile(r"上一集"), "文档元信息", SEVERITY_P1),
    (re.compile(r"这一集"), "文档元信息", SEVERITY_P1),
    (re.compile(r"下一集"), "文档元信息", SEVERITY_P1),
    (re.compile(r"本集[^体]"), "文档元信息", SEVERITY_P1),
    (re.compile(r"上一季"), "文档元信息", SEVERITY_P1),
    (re.compile(r"这一季"), "文档元信息", SEVERITY_P1),
    (re.compile(r"下一季"), "文档元信息", SEVERITY_P1),
]

ENGLISH_PUNCTUATION_CHECKS = [
    (re.compile(r"\.\.\.(?!\.)"), "英文省略号\"...\"", SEVERITY_P1),
    (re.compile(r"\.{4,}"), "英文省略号\"......\"", SEVERITY_P1),
]

SENSITIVE_PATTERNS = [
    (re.compile(r"杀死"), "敏感表达", SEVERITY_P1),
    (re.compile(r"干掉"), "敏感表达", SEVERITY_P1),
    (re.compile(r"尸体"), "敏感表达", SEVERITY_P1),
    (re.compile(r"血腥"), "敏感表达", SEVERITY_P1),
    (re.compile(r"屠杀"), "敏感表达", SEVERITY_P1),
    (re.compile(r"虐杀"), "敏感表达", SEVERITY_P1),
    (re.compile(r"消灭"), "敏感表达", SEVERITY_P2),
]

INTERACTION_LABELS = ["自我调节", "换位思考", "智慧与宽容", "悬念预测"]

QUESTION_PATTERN = re.compile(
    r"^(?P<index>[1-4])\. \*\*(?P<label>[^*]+)\*\*：(?P<question>.+)$"
)

RECAP_PATTERN = re.compile(r"^\*\*前情回顾\*\*：.+$")

LONG_SENTENCE_THRESHOLD = 60

SENTENCE_END_PATTERN = re.compile(r"[。！？…~」』"")】》\n]")

EXTRA_MARKDOWN_PATTERN = re.compile(r"\*\*前情回顾\*\*：.*\*\*$")


@dataclass
class AuditIssue:
    line_no: int | None
    severity: str
    category: str
    message: str


@dataclass
class AuditResult:
    path: Path
    issues: list[AuditIssue] = field(default_factory=list)

    @property
    def p0_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == SEVERITY_P0)

    @property
    def p1_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == SEVERITY_P1)

    @property
    def p2_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == SEVERITY_P2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="审计故事 Markdown 文本质量，检测文档元信息、标点、敏感表达等问题。"
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help="待审计的文件或目录；不传时默认扫描 stories/。",
    )
    parser.add_argument(
        "--include-backup",
        action="store_true",
        help="默认会跳过 _backup 目录；添加此参数可一并审计。",
    )
    parser.add_argument(
        "--severity",
        choices=["P0", "P1", "P2"],
        default="P2",
        help="最低报告严重程度（默认 P2，即报告所有问题）。",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="只输出汇总统计，不输出逐条问题。",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出结果。",
    )
    return parser.parse_args()


def normalize_lines(text: str) -> list[str]:
    text = text.lstrip("\ufeff")
    return [line.rstrip() for line in text.splitlines()]


def collect_files(targets: list[str], include_backup: bool) -> list[Path]:
    raw_targets = (
        [Path(target).expanduser() for target in targets]
        if targets
        else [DEFAULT_STORIES_DIR]
    )
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
    return (include_backup or "_backup" not in resolved.parts) and resolved not in EXCLUDED_FILES


def relative_display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def audit_file(path: Path) -> AuditResult:
    result = AuditResult(path)

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        result.issues.append(
            AuditIssue(None, SEVERITY_P0, "编码错误", f"文件不是有效的 UTF-8 编码：{exc}")
        )
        return result

    lines = normalize_lines(content)
    while lines and lines[-1] == "":
        lines.pop()

    if not lines:
        result.issues.append(AuditIssue(None, SEVERITY_P0, "空文件", "文件为空。"))
        return result

    check_doc_meta_info(lines, result)
    check_english_punctuation(lines, result)
    check_sensitive_expressions(lines, result)
    check_interaction_format(lines, result)
    check_long_sentences(lines, result)
    check_extra_markdown(lines, result)
    check_english_punctuation_inline(lines, result)

    return result


def check_doc_meta_info(lines: list[str], result: AuditResult) -> None:
    for line_no, line in enumerate(lines, start=1):
        if line.startswith("# "):
            continue
        for pattern, category, severity in DOC_META_PATTERNS:
            for match in pattern.finditer(line):
                result.issues.append(
                    AuditIssue(
                        line_no,
                        severity,
                        category,
                        f"发现文档元信息用语\"{match.group()}\"，应替换为故事世界内部表达。",
                    )
                )


def check_english_punctuation(lines: list[str], result: AuditResult) -> None:
    for line_no, line in enumerate(lines, start=1):
        if line.startswith("# "):
            continue
        for pattern, category, severity in ENGLISH_PUNCTUATION_CHECKS:
            for match in pattern.finditer(line):
                result.issues.append(
                    AuditIssue(
                        line_no,
                        severity,
                        category,
                        f"发现英文省略号，应替换为中文省略号\"……\"。",
                    )
                )


def check_sensitive_expressions(lines: list[str], result: AuditResult) -> None:
    for line_no, line in enumerate(lines, start=1):
        if line.startswith("# "):
            continue
        for pattern, category, severity in SENSITIVE_PATTERNS:
            for match in pattern.finditer(line):
                context_start = max(0, match.start() - 10)
                context_end = min(len(line), match.end() + 10)
                context = line[context_start:context_end]
                result.issues.append(
                    AuditIssue(
                        line_no,
                        severity,
                        category,
                        f"发现疑似不适合儿童表达\"{match.group()}\"，上下文：\"…{context}…\"。",
                    )
                )


def check_interaction_format(lines: list[str], result: AuditResult) -> None:
    interaction_start = None
    for idx, line in enumerate(lines):
        if line.startswith("**互动时刻**"):
            interaction_start = idx
            break

    if interaction_start is None:
        return

    tail = lines[interaction_start:]
    question_lines = []
    for line in tail:
        matched = QUESTION_PATTERN.fullmatch(line)
        if matched:
            question_lines.append((interaction_start + tail.index(line) + 1, matched))

    if len(question_lines) != 4:
        result.issues.append(
            AuditIssue(
                interaction_start + 1,
                SEVERITY_P1,
                "互动时刻格式",
                f"互动时刻应有 4 个问题，实际发现 {len(question_lines)} 个。",
            )
        )

    for line_no, matched in question_lines:
        index = int(matched.group("index"))
        label = matched.group("label").strip()
        question_text = matched.group("question").strip()

        expected_label = INTERACTION_LABELS[index - 1]
        if label != expected_label:
            result.issues.append(
                AuditIssue(
                    line_no,
                    SEVERITY_P1,
                    "互动时刻格式",
                    f"第 {index} 条互动问题小标题应为\"{expected_label}\"，实际为\"{label}\"。",
                )
            )

        if not question_text.endswith("？"):
            result.issues.append(
                AuditIssue(
                    line_no,
                    SEVERITY_P1,
                    "互动时刻格式",
                    f"第 {index} 条互动问题应以中文问号\"？\"结尾。",
                )
            )


def check_long_sentences(lines: list[str], result: AuditResult) -> None:
    separator_indices = [idx for idx, line in enumerate(lines) if line == "---"]
    if len(separator_indices) < 2:
        return

    body_start = separator_indices[0] + 1
    body_end = separator_indices[-1]

    for line_no in range(body_start, body_end):
        line = lines[line_no]
        if not line.strip():
            continue
        if line.startswith("# "):
            continue

        sentences = split_sentences(line)
        for sent in sentences:
            char_count = len(sent)
            if char_count > LONG_SENTENCE_THRESHOLD:
                result.issues.append(
                    AuditIssue(
                        line_no + 1,
                        SEVERITY_P2,
                        "长句",
                        f"单句 {char_count} 字，超过建议阈值 {LONG_SENTENCE_THRESHOLD} 字：\"{sent[:40]}…\"",
                    )
                )


def split_sentences(text: str) -> list[str]:
    sentences = []
    current = []
    for ch in text:
        current.append(ch)
        if ch in "。！？…~」』"")】》":
            sentences.append("".join(current))
            current = []
    if current:
        remaining = "".join(current)
        if remaining.strip():
            sentences.append(remaining)
    return sentences


def check_extra_markdown(lines: list[str], result: AuditResult) -> None:
    for line_no, line in enumerate(lines, start=1):
        if EXTRA_MARKDOWN_PATTERN.search(line):
            result.issues.append(
                AuditIssue(
                    line_no,
                    SEVERITY_P1,
                    "多余Markdown标记",
                    "前情回顾末尾异常出现\"**\"，疑似多余 Markdown 标记。",
                )
            )


def check_english_punctuation_inline(lines: list[str], result: AuditResult) -> None:
    """检测中文正文中混用的英文标点。"""
    separator_indices = [idx for idx, line in enumerate(lines) if line == "---"]
    if len(separator_indices) < 2:
        return

    body_start = separator_indices[0] + 1
    body_end = separator_indices[-1]

    english_comma_pattern = re.compile(r"[\u4e00-\u9fff]，[\u4e00-\u9fff]")
    english_colon_in_chinese = re.compile(r"[\u4e00-\u9fff]：[\u4e00-\u9fff]")

    for line_no in range(body_start, body_end):
        line = lines[line_no]
        if not line.strip():
            continue

        display_no = line_no + 1

        for match in re.finditer(r"[!?](?=[\u4e00-\u9fff])", line):
            result.issues.append(
                AuditIssue(
                    display_no,
                    SEVERITY_P1,
                    "英文标点混用",
                    f"中文正文中发现英文标点\"{match.group()}\"，应替换为中文标点。",
                )
            )

        for match in re.finditer(r"(?<=[\u4e00-\u9fff])[!?]", line):
            result.issues.append(
                AuditIssue(
                    display_no,
                    SEVERITY_P1,
                    "英文标点混用",
                    f"中文正文中发现英文标点\"{match.group()}\"，应替换为中文标点。",
                )
            )

        for match in re.finditer(r"(?<=[\u4e00-\u9fff]), (?=[\u4e00-\u9fff])", line):
            result.issues.append(
                AuditIssue(
                    display_no,
                    SEVERITY_P1,
                    "英文标点混用",
                    "中文正文中发现英文逗号\", \"，应替换为中文逗号\"，\"。",
                )
            )

        for match in re.finditer(r"(?<=[\u4e00-\u9fff]): (?=[\u4e00-\u9fff])", line):
            result.issues.append(
                AuditIssue(
                    display_no,
                    SEVERITY_P1,
                    "英文标点混用",
                    "中文正文中发现英文冒号\": \"，应替换为中文冒号\"：\"。",
                )
            )


def filter_by_severity(result: AuditResult, min_severity: str) -> AuditResult:
    severity_order = {SEVERITY_P0: 0, SEVERITY_P1: 1, SEVERITY_P2: 2}
    min_level = severity_order[min_severity]
    filtered = AuditResult(path=result.path)
    filtered.issues = [
        i for i in result.issues if severity_order[i.severity] <= min_level
    ]
    return filtered


def output_text(results: list[AuditResult], min_severity: str, summary_only: bool) -> None:
    total_issues = 0
    p0_total = 0
    p1_total = 0
    p2_total = 0
    files_with_issues = 0

    for result in results:
        filtered = filter_by_severity(result, min_severity)
        if not filtered.issues:
            continue

        files_with_issues += 1
        p0_total += filtered.p0_count
        p1_total += filtered.p1_count
        p2_total += filtered.p2_count
        total_issues += len(filtered.issues)

        if not summary_only:
            print(f"\n{'='*60}")
            print(f"📄 {relative_display_path(result.path)}")
            print(f"{'='*60}")
            for issue in filtered.issues:
                prefix = f"  第 {issue.line_no} 行" if issue.line_no is not None else "  文件级"
                print(f"{prefix} [{issue.severity}] {issue.category}：{issue.message}")

    print(f"\n{'='*60}")
    print(f"审计完成：共扫描 {len(results)} 篇，{files_with_issues} 篇发现问题。")
    print(f"  P0（必须优先处理）：{p0_total}")
    print(f"  P1（应当修复）：{p1_total}")
    print(f"  P2（建议优化）：{p2_total}")
    print(f"  合计：{total_issues}")
    print(f"{'='*60}")


def output_json(results: list[AuditResult], min_severity: str) -> None:
    import json

    output_data = []
    for result in results:
        filtered = filter_by_severity(result, min_severity)
        if not filtered.issues:
            continue

        output_data.append(
            {
                "file": relative_display_path(result.path),
                "issues": [
                    {
                        "line": issue.line_no,
                        "severity": issue.severity,
                        "category": issue.category,
                        "message": issue.message,
                    }
                    for issue in filtered.issues
                ],
            }
        )

    print(json.dumps(output_data, ensure_ascii=False, indent=2))


def main() -> int:
    args = parse_args()
    files = collect_files(args.targets, args.include_backup)

    if not files:
        print("没有找到可审计的 Markdown 文件。", file=sys.stderr)
        return 2

    results = [audit_file(path) for path in files]

    if args.json:
        output_json(results, args.severity)
    else:
        output_text(results, args.severity, args.summary_only)

    has_p0 = any(
        filter_by_severity(r, SEVERITY_P0).issues for r in results
    )
    return 1 if has_p0 else 0


if __name__ == "__main__":
    raise SystemExit(main())

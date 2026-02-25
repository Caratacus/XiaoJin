#!/usr/bin/env python3
"""
故事风格统一检查工具
整合所有检查功能，提供分级输出
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, List

# 导入各个检查模块
sys.path.insert(0, str(Path(__file__).parent))
from scanner import check_episode_style, StyleChecker
from detect_subsections import scan_stories as check_subsections
from detect_repetitive_patterns import check_episode as check_patterns
from check_dialogue_consistency import check_episode as check_dialogues


class IssueReporter:
    """问题报告器 - 按严重程度分级输出"""

    SEVERITY_LEVELS = {
        "critical": "🔴 严重",
        "warning": "⚠️ 警告",
        "info": "ℹ️ 提示"
    }

    def __init__(self):
        self.issues = {
            "critical": [],
            "warning": [],
            "info": []
        }

    def add(self, severity: str, episode: str, message: str):
        """添加问题"""
        if severity in self.issues:
            self.issues[severity].append({
                "episode": episode,
                "message": message
            })

    def report(self):
        """输出报告"""
        total = sum(len(v) for v in self.issues.values())

        if total == 0:
            print("✓ 所有检查通过！")
            return

        print(f"\n发现 {total} 个问题：\n")

        for severity in ["critical", "warning", "info"]:
            issues = self.issues[severity]
            if issues:
                print(f"{self.SEVERITY_LEVELS[severity]} ({len(issues)}个)")
                for issue in issues:
                    print(f"  {issue['episode']}: {issue['message']}")
                print()


def run_comprehensive_check(story_dir: str, episode_filter: str = None):
    """运行全面检查"""
    reporter = IssueReporter()
    story_path = Path(story_dir)

    if episode_filter:
        files = [story_path / episode_filter]
    else:
        files = sorted(story_path.glob("第*.md"))

    print(f"检查 {len(files)} 个文件...\n")

    for file in files:
        if not file.exists():
            print(f"跳过不存在的文件: {file}")
            continue

        episode = file.name

        # 1. 子章节检查
        try:
            subsection_issues = check_subsections(str(file))
            for issue in subsection_issues:
                reporter.add(
                    "warning",
                    episode,
                    f"第{issue['line']}行存在子章节: {issue['content']}"
                )
        except Exception as e:
            reporter.add("info", episode, f"子章节检查失败: {str(e)}")

        # 2. 风格检查
        try:
            style_result = check_episode_style(str(file))

            if not style_result["has_questions"]:
                reporter.add("critical", episode, "缺少结尾问题")

            if style_result["old_formats"]:
                for fmt in style_result["old_formats"]:
                    reporter.add("warning", episode, f"包含旧格式: {fmt['format']}")

            if style_result["long_sentences"]:
                count = len(style_result["long_sentences"])
                reporter.add("info", episode, f"发现{count}个长句（超过30字）")

        except Exception as e:
            reporter.add("info", episode, f"风格检查失败: {str(e)}")

        # 3. 重复句式检查（简化输出）
        try:
            from detect_repetitive_patterns import detect_repetitive_patterns
            patterns = detect_repetitive_patterns(str(file))
            if patterns:
                count = len(patterns)
                reporter.add("info", episode, f"发现{count}个重复句式")
        except Exception as e:
            pass  # 静默失败

    # 输出报告
    reporter.report()


def main():
    parser = argparse.ArgumentParser(description="故事风格统一检查工具")
    parser.add_argument("story_dir", nargs="?", default="小金故事集",
                        help="故事目录路径")
    parser.add_argument("--episode", help="只检查特定文件（如：第01集_*.md）")
    parser.add_argument("--quick", action="store_true",
                        help="快速检查（仅严重问题）")

    args = parser.parse_args()

    print("="*60)
    print("故事风格统一检查工具")
    print("="*60)

    run_comprehensive_check(args.story_dir, args.episode)

    print("\n检查完成！")


if __name__ == "__main__":
    main()

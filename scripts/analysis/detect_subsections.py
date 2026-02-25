#!/usr/bin/env python3
"""
子章节检测脚本
检测故事文件中是否存在子章节划分（二级标题、序章、终章等）
"""

import os
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.scanner import detect_subsections


def scan_stories(story_dir: str):
    """扫描所有故事文件"""
    story_path = Path(story_dir)
    if not story_path.exists():
        print(f"错误：目录不存在 {story_dir}")
        return

    issues = []

    # 遍历所有 .md 文件
    for file in sorted(story_path.glob("第*.md")):
        result = detect_subsections(file)
        if result:
            for issue in result:
                issues.append({
                    "file": file.name,
                    "line": issue["line"],
                    "content": issue["content"],
                    "severity": issue["severity"]
                })

    # 输出结果
    if issues:
        print(f"发现 {len(issues)} 处子章节划分：\n")
        for issue in issues:
            print(f"  {issue['file']}:{issue['line']}")
            print(f"    {issue['content']}")
            print(f"    严重程度: {issue['severity']}\n")
    else:
        print("✓ 未发现子章节划分问题")

    return issues


if __name__ == "__main__":
    story_dir = sys.argv[1] if len(sys.argv) > 1 else "小金故事集"
    scan_stories(story_dir)

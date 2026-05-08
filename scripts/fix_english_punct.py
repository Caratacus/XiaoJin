#!/usr/bin/env python3
"""替换中文正文中的英文标点 ? 和 ! 为中文标点 ？和 ！。

匹配规则与 audit_story_text.py 的 check_english_punctuation_inline 完全一致。
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STORIES_DIR = REPO_ROOT / "stories"

REPLACEMENTS = [
    (re.compile(r"(?<=[\u4e00-\u9fff])[?]"), "？"),
    (re.compile(r"[?](?=[\u4e00-\u9fff])"), "？"),
    (re.compile(r"(?<=[\u4e00-\u9fff])[!]"), "！"),
    (re.compile(r"[!](?=[\u4e00-\u9fff])"), "！"),
]


def fix_file(filepath: Path) -> int:
    content = filepath.read_text(encoding="utf-8")
    original = content

    for pattern, replacement in REPLACEMENTS:
        content = pattern.sub(replacement, content)

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return 1

    return 0


def main():
    files = sorted(STORIES_DIR.rglob("*.md"))
    files = [f for f in files if "_backup" not in str(f)]

    total = 0
    for f in files:
        n = fix_file(f)
        if n > 0:
            total += 1
            print(f"  {f.relative_to(REPO_ROOT)}")

    print(f"\n共修改 {total} 个文件。")


if __name__ == "__main__":
    main()

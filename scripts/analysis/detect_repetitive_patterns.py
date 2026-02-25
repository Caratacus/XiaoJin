#!/usr/bin/env python3
"""
重复句式检测脚本
检测故事中可能存在的重复句式和过度使用的表达
"""

import os
import re
import sys
from pathlib import Path
from collections import Counter
from typing import List, Dict


def extract_sentences(text: str) -> List[str]:
    """提取所有句子"""
    # 移除标题和特殊格式
    text = re.sub(r'^#+\s+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*.*?\*\*', '', text)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)

    # 分割句子
    sentences = re.split(r'[。！？；]', text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]


def detect_repetitive_words(file_path: str, top_n: int = 20) -> Dict[str, int]:
    """检测高频词汇"""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 提取所有中文词汇（简单模式：2-4字的词组）
    words = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)

    # 过滤常见助词
    stopwords = {'的', '了', '是', '在', '有', '和', '就', '不', '人', '都', '一', '一个',
                 '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看',
                 '好', '自己', '这', '那', '里', '后', '为', '可以', '他', '她', '它', '我们'}

    filtered = [w for w in words if w not in stopwords]

    return Counter(filtered).most_common(top_n)


def detect_repetitive_patterns(file_path: str) -> List[Dict]:
    """检测重复的句式模式"""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    sentences = extract_sentences(text)

    # 提取句首模式（前5个字）
    openers = [s[:5] for s in sentences if len(s) >= 5]

    # 统计高频句首
    opener_counts = Counter(openers)

    # 找出出现3次以上的句首
    repetitive = []
    for opener, count in opener_counts.items():
        if count >= 3 and len(opener) >= 3:
            repetitive.append({
                "pattern": opener,
                "count": count,
                "type": "sentence_opener"
            })

    return repetitive


def check_episode(file_path: str):
    """检查单集故事"""
    print(f"\n检查：{Path(file_path).name}")

    # 检测高频词汇
    top_words = detect_repetitive_words(file_path)
    print("\n  高频词汇：")
    for word, count in top_words[:10]:
        print(f"    {word}: {count}次")

    # 检测重复句式
    patterns = detect_repetitive_patterns(file_path)
    if patterns:
        print("\n  重复句式：")
        for p in patterns:
            print(f"    句首'{p['pattern']}': {p['count']}次")
    else:
        print("\n  未发现明显重复句式")


def scan_all(story_dir: str):
    """扫描所有故事"""
    story_path = Path(story_dir)
    files = sorted(story_path.glob("第*.md"))

    print(f"扫描 {len(files)} 个文件...\n")

    for file in files:
        check_episode(file)


if __name__ == "__main__":
    story_dir = sys.argv[1] if len(sys.argv) > 1 else "小金故事集"

    if len(sys.argv) > 2 and sys.argv[2] == "--single":
        # 单文件模式
        check_episode(sys.argv[1])
    else:
        # 批量模式
        scan_all(story_dir)

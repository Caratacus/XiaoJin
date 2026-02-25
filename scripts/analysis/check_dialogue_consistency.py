#!/usr/bin/env python3
"""
角色对话一致性检查脚本
检查角色对话风格和特征是否符合设定
"""

import re
import sys
from pathlib import Path
from typing import Dict, List


# 角色对话特征定义
CHARACTER_PATTERNS = {
    "小金": {
        "keywords": ["智慧", "观察", "分析", "发现", "理解", "原来", "明白"],
        "tone": "冷静、理性、善于分析",
        "check_length": True
    },
    "小彩": {
        "keywords": ["冲", "快", "火", "我来了", "看我的", "哈哈"],
        "tone": "热情、急躁、直率",
        "check_exclamations": True
    },
    "小玉": {
        "keywords": ["记载", "古籍", "历史", "记录", "根据", "查阅"],
        "tone": "博学、温和、知识性",
        "check_citations": True
    },
    "黑焰": {
        "keywords": ["火候", "温度", "热度", "烹饪", "调味"],
        "tone": "专业、成熟、反思",
        "check_culinary": True
    }
}


def extract_dialogues(text: str, character: str) -> List[str]:
    """提取特定角色的对话"""
    # 匹配模式：角色名：对话内容
    pattern = f'{character}["|\"|：|:](.+?)(?=["|\"|：|：]|$)'
    matches = re.findall(pattern, text)

    # 也匹配引号内的对话（需要上下文判断角色）
    quoted = re.findall(r'["|"](.+?)["|"]', text)

    return matches


def check_character_dialogue(file_path: str, character: str, definition: Dict) -> Dict:
    """检查角色对话风格"""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    dialogues = extract_dialogues(text, character)

    if not dialogues:
        return {"character": character, "dialogues_count": 0, "issues": []}

    issues = []

    # 检查关键词出现频率
    keyword_count = 0
    for dialogue in dialogues:
        for keyword in definition["keywords"]:
            if keyword in dialogue:
                keyword_count += 1

    # 统计感叹号使用（小彩）
    if definition.get("check_exclamations"):
        exclamation_count = sum(1 for d in dialogues if "！" in d or "!" in d)
        if len(dialogues) > 3 and exclamation_count < len(dialogues) * 0.3:
            issues.append(f"{character}的对话中感叹号较少（{exclamation_count}/{len(dialogues)}），可能不够急躁直率")

    # 统计对话长度（小金）
    if definition.get("check_length"):
        avg_length = sum(len(d) for d in dialogues) / len(dialogues)
        if avg_length < 15:
            issues.append(f"{character}的对话平均长度较短（{avg_length:.1f}字），可能不够分析性")

    return {
        "character": character,
        "dialogues_count": len(dialogues),
        "keyword_matches": keyword_count,
        "issues": issues
    }


def check_episode(file_path: str):
    """检查单集故事的角色对话"""
    print(f"\n检查：{Path(file_path).name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    results = []
    for character, definition in CHARACTER_PATTERNS.items():
        result = check_character_dialogue(file_path, character, definition)
        if result["dialogues_count"] > 0:
            results.append(result)
            print(f"\n  {character}: {result['dialogues_count']}句对话")
            if result["keyword_matches"] > 0:
                print(f"    关键词匹配: {result['keyword_matches']}次")
            if result["issues"]:
                for issue in result["issues"]:
                    print(f"    ⚠️ {issue}")

    return results


def scan_all(story_dir: str):
    """扫描所有故事"""
    story_path = Path(story_dir)
    files = sorted(story_path.glob("第*.md"))

    print(f"扫描 {len(files)} 个文件...")

    all_issues = {}

    for file in files:
        results = check_episode(file)
        for result in results:
            if result["issues"]:
                if file.name not in all_issues:
                    all_issues[file.name] = []
                all_issues[file.name].extend(result["issues"])

    # 汇总报告
    if all_issues:
        print("\n\n" + "="*50)
        print("汇总报告：发现问题的章节")
        print("="*50)
        for filename, issues in all_issues.items():
            print(f"\n{filename}:")
            for issue in issues:
                print(f"  - {issue}")
    else:
        print("\n✓ 所有角色对话风格检查通过")


if __name__ == "__main__":
    story_dir = sys.argv[1] if len(sys.argv) > 1 else "小金故事集"
    scan_all(story_dir)

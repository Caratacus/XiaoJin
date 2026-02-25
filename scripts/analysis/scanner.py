import re
from typing import Dict, List, Set, Tuple

class LoreScanner:
    def __init__(self):
        # 常见角色名称模式
        self.char_patterns = [
            r"小金", r"小玉", r"小彩", r"黑焰", r"紫晶国王", r"玉米王十三世",
            r"小炭", r"阿勇", r"红隼", r"蚂蚁队长", r"蚯蚓队长", r"龟爷爷",
            r"蝉先生", r"铁大钳", r"西瓜伯伯", r"鼻涕虫", r"风之精灵"
        ]
        # 常见地点模式
        self.loc_patterns = [
            r"小玉米粒王国", r"回声山谷", r"黑暗魔法界", r"风之谷", r"南瓜园",
            r"露珠河", r"阴影森林", r"阳光特色美食街", r"中心广场"
        ]
        # 常见道具/设定模式
        self.item_patterns = [
            r"阳光露珠", r"声音露珠", r"露珠放大镜", r"萤火虫灯笼", r"诚实南瓜饼",
            r"愤怒浓汤", r"极寒冰刺身", r"阳光玉米粥", r"团结之味", r"心之筛"
        ]

    def extract_characters(self, text):
        found = set()
        for pattern in self.char_patterns:
            if re.search(pattern, text):
                found.add(pattern.replace(r"", "")) # 简单清理
        return found

    def extract_locations(self, text):
        found = set()
        for pattern in self.loc_patterns:
            if re.search(pattern, text):
                found.add(pattern)
        return found

    def extract_items(self, text):
        found = set()
        for pattern in self.item_patterns:
            if re.search(pattern, text):
                found.add(pattern)
        return found


class StyleChecker:
    """故事风格检查器 - 检查叙事风格、格式和一致性"""

    def __init__(self):
        # 微观尺度感关键词
        self.micro_scale_keywords = [
            r"露珠", r"玉米叶", r"草叶", r"花瓣", r"根须", r"米粒",
            r"玉米粒", r"昆虫", r"露水", r"花蜜", r"树叶", r"草丛"
        ]
        # 子章节标题模式（应避免）
        self.subsection_patterns = [
            r"^##\s+",  # 二级标题
            r"序章", r"终章", r"第\s*[一二三\d+]\s*章",  # 章节标记
            r"卷\s*[:：]", r"部\s*[:：]"  # 分卷标记
        ]
        # 旧格式标记（应替换）
        self.old_formats = [
            r"互动时刻",
            r"🌟",
            r"思考时间"
        ]

    def check_micro_scale(self, text: str) -> Dict[str, int]:
        """检查微观尺度感描述"""
        stats = {}
        for keyword in self.micro_scale_keywords:
            count = len(re.findall(keyword, text))
            if count > 0:
                stats[keyword] = count
        return stats

    def check_subsections(self, lines: List[str]) -> List[Dict[str, str]]:
        """检查子章节划分"""
        issues = []
        for i, line in enumerate(lines, 1):
            for pattern in self.subsection_patterns:
                if re.search(pattern, line):
                    issues.append({
                        "line": i,
                        "content": line.strip(),
                        "type": "subsection",
                        "severity": "warning"
                    })
        return issues

    def check_old_formats(self, text: str) -> List[Dict[str, str]]:
        """检查旧格式标记"""
        issues = []
        for fmt in self.old_formats:
            if re.search(fmt, text):
                issues.append({
                    "type": "old_format",
                    "format": fmt,
                    "severity": "info"
                })
        return issues

    def check_ending_questions(self, text: str) -> bool:
        """检查是否包含结尾问题"""
        # 检查是否有"思考与探索"部分
        has_questions = re.search(r"\*\*思考与探索\*\*", text)
        if has_questions:
            # 计算问题数量
            questions = re.findall(r"^\d+\.", text, re.MULTILINE)
            return len(questions) >= 3
        return False

    def check_sentence_length(self, lines: List[str]) -> List[Dict[str, str]]:
        """检查句子长度（超过30字为长句）"""
        long_sentences = []
        for i, line in enumerate(lines, 1):
            # 跳过标题和空行
            if line.startswith("#") or not line.strip():
                continue
            # 分割句子
            sentences = re.split(r"[。！？；]", line)
            for sent in sentences:
                if len(sent.strip()) > 30:
                    long_sentences.append({
                        "line": i,
                        "length": len(sent.strip()),
                        "content": sent.strip()[:50] + "..." if len(sent) > 50 else sent
                    })
        return long_sentences

    def check_dialogue_patterns(self, text: str, character: str) -> int:
        """检查特定角色的对话数量"""
        # 简单模式：匹配 "角色名："
        pattern = f"{character}[:：]"
        return len(re.findall(pattern, text))


def detect_subsections(file_path: str) -> List[Dict[str, str]]:
    """检测文件中的子章节划分"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    checker = StyleChecker()
    return checker.check_subsections(lines)


def check_episode_style(file_path: str) -> Dict:
    """检查单集故事的风格"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    checker = StyleChecker()

    return {
        "micro_scale": checker.check_micro_scale(content),
        "subsections": checker.check_subsections(lines),
        "old_formats": checker.check_old_formats(content),
        "has_questions": checker.check_ending_questions(content),
        "long_sentences": checker.check_sentence_length(lines)
    }

import re

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

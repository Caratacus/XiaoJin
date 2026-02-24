import os
import glob
from scanner import LoreScanner

def run_full_scan():
    scanner = LoreScanner()
    story_files = sorted(glob.glob("小金故事集/*.md"))
    
    global_results = {
        "characters": {},
        "locations": set(),
        "items": set()
    }
    
    for filepath in story_files:
        filename = os.path.basename(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 提取角色初登场
            chars = scanner.extract_characters(content)
            for char in chars:
                if char not in global_results["characters"]:
                    global_results["characters"][char] = filename
            
            # 提取地点和道具
            global_results["locations"].update(scanner.extract_locations(content))
            global_results["items"].update(scanner.extract_items(content))

    report = []
    report.append("# 扫描结果汇总\n")
    report.append("## 核心角色初登场")
    for char, first_file in sorted(global_results["characters"].items()):
        report.append(f"- **{char}**: {first_file}")
    
    report.append("\n## 发现的地点")
    for loc in sorted(global_results["locations"]):
        report.append(f"- {loc}")
        
    report.append("\n## 发现的道具与设定")
    for item in sorted(global_results["items"]):
        report.append(f"- {item}")
        
    print("\n".join(report))

if __name__ == "__main__":
    run_full_scan()

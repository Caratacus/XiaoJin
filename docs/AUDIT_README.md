# 审计使用说明

本文档说明如何在本项目中运行故事审计脚本，查看格式问题、文本问题和上下集连续性问题。

## 审计入口

本项目没有单独的“审计开关”或后台服务。所谓“开启审计”，就是直接运行 `scripts/` 下的相关脚本。

## 常用审计命令

### 1. 故事格式校验

检查标题、前情回顾、正文分隔线、正文长度、互动时刻结构是否符合项目模板。

```bash
python3 scripts/validate_story_format.py stories
```

也可以只校验某一季或某一篇：

```bash
python3 scripts/validate_story_format.py "stories/第02季_成长与冒险"
python3 scripts/validate_story_format.py "stories/第02季_成长与冒险/第01集_蓝色迷雾与沉睡的危机.md"
```

### 2. 文本质量审计

检查以下问题：

- 文档元信息入文，例如“上一集”“下一集”“这一集”
- 英文标点混用
- 敏感或不适合儿童表达
- 互动时刻标签或问号格式问题
- 长句
- 多余 Markdown 标记

全量审计：

```bash
python3 scripts/audit_story_text.py stories
```

只看汇总：

```bash
python3 scripts/audit_story_text.py stories --summary-only
```

只看某个严重级别及以上的问题：

```bash
python3 scripts/audit_story_text.py stories --severity P1
```

输出 JSON：

```bash
python3 scripts/audit_story_text.py stories --json
```

只审计某一季：

```bash
python3 scripts/audit_story_text.py "stories/第02季_成长与冒险"
```

### 3. 连续性抽检

抽取相邻两集窗口，检查前情回顾是否准确承接上一集、开头是否回应悬念、结尾是否自然引向下一集。

```bash
python3 scripts/audit_continuity.py
```

生成的报告会写入：

```text
docs/audit_reports/
```

## 推荐审计顺序

完整做一轮审计时，建议按下面顺序执行：

1. 先做格式校验
2. 再做文本质量审计
3. 最后做连续性抽检

命令如下：

```bash
python3 scripts/validate_story_format.py stories
python3 scripts/audit_story_text.py stories --summary-only
python3 scripts/audit_continuity.py
```

## 输出位置说明

| 脚本 | 输出方式 |
| --- | --- |
| `validate_story_format.py` | 直接在终端输出通过/失败结果 |
| `audit_story_text.py` | 直接在终端输出问题列表或汇总 |
| `audit_continuity.py` | 生成 Markdown 报告到 `docs/audit_reports/` |

## 相关脚本

除审计脚本外，项目里还有几个与审计结果处理相关的脚本：

| 脚本 | 作用 |
| --- | --- |
| `scripts/fix_english_punct.py` | 批量把正文中的英文 `?`、`!` 替换为中文 `？`、`！` |
| `scripts/fix_story_issues.py` | 批量修复文档元信息、互动标签、多余 Markdown 标记等问题 |
| `scripts/build_story_index.py` | 生成 `docs/story_index.json`，用于索引和辅助审计 |

## 建议

- 批量修复前，先运行审计，确认问题范围。
- 批量修复后，重新运行 `validate_story_format.py` 和 `audit_story_text.py`。
- 连续性问题更适合结合 `docs/audit_reports/` 中的窗口报告人工复核。

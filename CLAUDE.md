# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 提供在此代码库中工作的指导。

## 核心指令：语言规范
- **首要语言**：本项目使用**简体中文**作为主要语言。
- **涵盖范围**：包括但不限于：
  - 与用户的所有对话和交流
  - 故事内容创作
  - 文档编写（包括 CLAUDE.md 本身）
  - AI 交互提示
  - 元数据维护
  - Git 提交信息
- **例外情况**：仅对技术性代码（如 Python 脚本、Conductor 框架文件）使用英文，但注释和文档应使用中文。

# Conductor Context

If a user mentions a "plan" or asks about the plan, and they have used the conductor extension in the current session, they are likely referring to the `conductor/tracks.md` file or one of the track plans (`conductor/tracks/<track_id>/plan.md`).

## Universal File Resolution Protocol

**PROTOCOL: How to locate files.**
To find a file (e.g., "**Product Definition**") within a specific context (Project Root or a specific Track):

1.  **Identify Index:** Determine the relevant index file:
    -   **Project Context:** `conductor/index.md`
    -   **Track Context:**
        a. Resolve and read the **Tracks Registry** (via Project Context).
        b. Find the entry for the specific `<track_id>`.
        c. Follow the link provided in the registry to locate the track's folder. The index file is `<track_folder>/index.md`.
        d. **Fallback:** If the track is not yet registered (e.g., during creation) or the link is broken:
            1. Resolve the **Tracks Directory** (via Project Context).
            2. The index file is `<Tracks Directory>/<track_id>/index.md`.

2.  **Check Index:** Read the index file and look for a link with a matching or semantically similar label.

3.  **Resolve Path:** If a link is found, resolve its path **relative to the directory containing the `index.md` file**.
    -   *Example:* If `conductor/index.md` links to `./workflow.md`, the full path is `conductor/workflow.md`.

4.  **Fallback:** If the index file is missing or the link is absent, use the **Default Path** keys below.

5.  **Verify:** You MUST verify the resolved file actually exists on the disk.

**Standard Default Paths (Project):**
- **Product Definition**: `conductor/product.md`
- **Tech Stack**: `conductor/tech-stack.md`
- **Workflow**: `conductor/workflow.md`
- **Product Guidelines**: `conductor/product-guidelines.md`
- **Tracks Registry**: `conductor/tracks.md`
- **Tracks Directory**: `conductor/tracks/`

**Standard Default Paths (Track):**
- **Specification**: `conductor/tracks/<track_id>/spec.md`
- **Implementation Plan**: `conductor/tracks/<track_id>/plan.md`
- **Metadata**: `conductor/tracks/<track_id>/metadata.json`


# currentDate
Today's date is 2026-02-25.

      IMPORTANT: This context may may not be relevant to your task.

## 项目概述

这是一个原创儿童故事系列的创意写作项目，题为"小玉米粒王国英雄小金"。项目将创意写作与 Conductor 项目管理框架相结合。

**主要内容：**
- 62 集已完成的故事，采用 Markdown 格式
- 完整的世界观设定和人物志
- 基于 Python 的内容一致性分析工具
- 规范化的创作流程和文档体系

## 项目结构

```
/
├── 小金故事集/           # 62 集故事正文（Markdown 格式）
├── lore/               # 世界观设定、人物志
├── conductor/          # 项目管理框架
│   ├── analysis/       # 逐集分析文件
│   ├── archive/        # 已完成的轨道（Track）存档
│   ├── code_styleguides/ # 写作和风格指南
│   ├── product.md      # 产品定义
│   ├── workflow.md     # 开发流程
│   └── tracks.md       # 轨道注册表
├── scripts/            # Python 分析工具
├── GEMINI.md           # 人物档案和项目上下文
└── README.md           # 项目文档
```

## 常用命令

### 内容分析
```bash
# 运行完整的故事内容分析（提取角色、地点、物品）
python scripts/analysis/run_scan.py
```

### Git 工作流
本项目使用 git notes 记录详细的任务文档：
```bash
# 为提交添加注释
git notes add -m "<注释内容>" <commit_hash>

# 查看提交的注释
git notes show <commit_hash>
```

## 架构与约定

### 内容创作流程
1. **规格驱动开发**：所有内容创作遵循 Conductor 工作流（plan.md → specification → implementation）
2. **TDD 方法**：在实现新内容前先编写分析测试
3. **Git notes**：为提交附加详细摘要以供审计
4. **质量标准**：保持一致性检查覆盖率 >80%

### 文件命名约定
- 故事：`第XX集_标题.md`（按顺序编号）
- 分析：`episode_XX_analysis.md`
- 世界观设定：`/lore/` 中的描述性名称
- 管理：标准 Conductor 框架文件

### 故事结构（62 集，4 季）
1. **第一季（第 1-15 集）**：生存与盟友
2. **第二季（第 16-37 集）**：成长与彩虹桥
3. **第三季（第 38-57 集）**：美食科学与魔法
4. **第四季（第 58-62 集）**：太空探索

### 核心角色
- **小金**：睿智的英雄、发明家，重生后拥有两世记忆
- **小玉**：知识守护者、年迈的顾问
- **小彩**：彩虹战士，性格急躁但忠诚
- **黑焰**：前反派首领，现为王国大厨
- **紫晶国王**：合并王国的统一统治者

完整的人物档案和故事背景请参见 `GEMINI.md`。

### 写作指南
- **冒险导向**：悬念感强、语言生动
- **互动性**：每集结尾设置启发性问题
- **微观奇观**：强调尺寸感知（玉米叶如地毯、雨滴如炸弹）
- **价值观**：智慧胜于武力、包容性、非暴力冲突解决

### 提交信息格式
遵循 conventional commits 规范：
```
<type>(<scope>): <description>

类型：feat, fix, docs, style, refactor, test, chore
```

示例：
- `feat(story): 新增第 63 集 - 水晶洞穴`
- `docs(lore): 更新第五季人物档案`
- `fix(analysis): 修正角色提取正则表达式`

## 在此项目中工作

1. **语言**：故事内容和项目文档始终使用简体中文
2. **阅读顺序**：按照 `小金故事集/` 中的顺序编号
3. **一致性**：使用 Python 分析工具验证角色和设定的一致性
4. **上下文**：参考 `GEMINI.md` 了解人物档案，参考 `conductor/` 进行项目管理

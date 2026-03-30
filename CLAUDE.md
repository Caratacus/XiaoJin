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
├── docs/               # 项目文档
├── GEMINI.md           # 人物档案和项目上下文
└── README.md           # 项目文档
```

## 常用命令

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
2. **Git notes**：为提交附加详细摘要以供审计

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

本指南适用于《小金故事集》的创作和润色工作。

#### 叙事规范

**视角**：
- 采用**第三人称限制视角**，主要聚焦于小金的认知和体验
- 可适度切换到其他关键角色（小玉、小彩、黑焰等）的视角以丰富叙事
- 保持叙述的一致性，避免视角混乱跳跃

**微观世界尺度感**：
- 始终保持玉米粒的微观视角，将日常物品和自然现象以微观尺度重新描述
- 使用玉米粒的尺度参照：露珠如镜、雨滴如炸弹、草叶如地毯、玉米叶如船帆
- 描述物理互动和空间关系时保持微观视角的逻辑一致性

**节奏与张力控制**：
- **冒险场景**：使用短句、动词密集的描述，营造紧迫感
- **温馨场景**：放慢节奏，增加环境描写和内心活动
- 合理控制叙事节奏，在紧张场景后提供喘息空间

#### 语言规范

**语言风格**：
- 生动活泼、富有画面感
- 简洁流畅，适合 7-12 岁儿童阅读
- 避免过长或过于复杂的句式（每句不超过 30 字为佳）

**描写性语言**：
- 使用感官细节（视觉、听觉、触觉、嗅觉），避免抽象描述
- 注重微缩世界的感官体验：玉米叶的清香、露珠的触感、风的声音

**对话语言**：
- 对话应符合角色性格特征，语言自然口语化但不失礼貌
- 每个角色有独特的对话风格（见角色对话规范）

#### 角色对话规范

**小金**：
- 体现冷静、睿智、善于观察的特点
- 常使用分析性语言，善于从现象中归纳规律
- 重生后保留两世记忆，语言中有成熟智慧与少年活力的融合

**小彩**：
- 体现热情、急躁、直率的特点
- 常用感叹词和简短有力的表达
- 成长过程中逐渐学会控制情绪

**小玉**：
- 体现博学、温和、长者风范
- 常用典故和比喻，语言富有知识性
- 作为年迈顾问时带有慈祥的语气

**黑焰**：
- 体现成熟、专业（烹饪/热力学）、改过自新的反思
- 语言中有内省和谦卑，与反派时期形成对比

#### 章节结构规范

**标题格式**：
- 每集使用一级标题（`#`）作为故事标题
- **禁止使用任何形式的子章节划分**，保持叙事流畅性：
  - 禁止使用二级标题（`##`）作为章节标题
  - 禁止在行首直接写"序章"、"序言"、"终章"、"第X章"等标题
  - 禁止使用"卷"、"部"等分卷标记
- 使用段落分隔、过渡句或场景转换标记替代子章节标题
- 保持连续的叙事流，避免打断故事的节奏和沉浸感

**章节衔接**：
- 每集开头简要回顾上一集的关键事件或结尾，提供上下文连贯性
- 上一集留下的悬念必须在新一集前几段内回应或继续
- 明确说明时间的流逝（如"第二天清晨""数日后"）

**互动性结尾**：
- 每集结尾必须包含 1-3 个启发性问题
- 问题应涵盖：价值观思考、情节预测、创意联想等多种类型
- 引导读者思考故事主题或预测后续发展

#### 价值观与教育意义

**核心价值观**：
- 智慧胜于武力：用观察、分析和科学/智慧的妙计解决问题
- 包容与和解：通过"黑玉米"等角色的转变，探讨社会共存与心理治愈
- 非暴力冲突解决：优先基于智慧、沟通、合作而非武力

**知识性与趣味性平衡**：
- 将科学知识、人生智慧自然融入情节
- 用简单易懂的方式解释科学原理，避免说教式科普
- 通过角色行动和对话自然展现价值观，避免直接说教

#### 润色工作规范

**内容完整性保护**：
- 绝对不能删除原有的情节、对话、描写或角色
- 只能调整表达方式，不能改变事件本身
- 遵循"最小化修改原则"，只修改确实需要改进的部分

**润色流程**（四阶段）：
1. **风格统一检查**：叙事视角、语言风格、尺度感、对话风格
2. **衔接性增强**：章节间的衔接和呼应
3. **语言润色**：消除冗余、优化节奏、增强画面感、修正语病
4. **一致性验证**：人工审查角色和设定的一致性

**子章节处理**：
- 检查章节是否使用了 `##` 二级标题作为子章节标题
- 检查章节是否在行首直接写"序章"、"序言"、"终章"、"第X章"等标题
- 将所有子章节内容整合到主叙事流中，保持连续叙事
- 使用段落分隔、过渡句或场景转换标记替代子章节标题
- **已发现需要处理的章节**：
  - 第09集：序章、终章
  - 第10集：纪念碑前的思念、大地的回应、金色嫩芽的破土、永恒的智慧之种
  - 第58-62集：每集4个二级标题章节

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
3. **上下文**：参考 `GEMINI.md` 了解人物档案，参考 `conductor/` 进行项目管理

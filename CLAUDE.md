# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

## Project Overview

This is a creative writing project for an original children's story series titled "小玉米粒王国英雄小金" (Tiny Corn Kingdom Hero Xiao Jin). The project combines creative writing with sophisticated project management using the Conductor framework.

**Primary Language:** Chinese (Simplified) - All story content, documentation, and AI interactions should prioritize Chinese.

## Project Structure

```
/
├── 小金故事集/           # 62 story episodes in Markdown format
├── lore/               # World-building documentation, character profiles
├── conductor/          # Project management framework
│   ├── analysis/       # Episode-by-episode analysis files
│   ├── archive/        # Completed tracks
│   ├── code_styleguides/ # Writing and style guidelines
│   ├── product.md      # Product definition
│   ├── workflow.md     # Development process
│   └── tracks.md       # Tracks registry
├── scripts/            # Python analysis tools
├── GEMINI.md           # Character profiles and project context
└── README.md           # Project documentation
```

## Common Commands

### Content Analysis
```bash
# Run full story content analysis (extracts characters, locations, items)
python scripts/analysis/run_scan.py
```

### Git Workflow
The project uses git notes for detailed task documentation:
```bash
# Attach a note to a commit
git notes add -m "<note content>" <commit_hash>

# View notes on a commit
git notes show <commit_hash>
```

## Architecture & Conventions

### Content Creation Process
1. **Spec-driven development**: All content creation follows the Conductor workflow (plan.md → specification → implementation)
2. **TDD approach**: Write analysis tests before implementing new content
3. **Git notes**: Attach detailed summaries to commits for auditability
4. **Quality gates**: Maintain >80% coverage for consistency checks

### File Naming Conventions
- Stories: `第XX集_标题.md` (sequential numbering)
- Analysis: `episode_XX_analysis.md`
- World-building: Descriptive names in `/lore/`
- Management: Standard Conductor framework files

### Story Structure (62 Episodes, 4 Seasons)
1. **Season 1 (Ep 1-15)**: Survival and alliances
2. **Season 2 (Ep 16-37)**: Growth and rainbow bridge
3. **Season 3 (Ep 38-57)**: Food science vs magic
4. **Season 4 (Ep 58-62)**: Space exploration

### Core Characters
- **Xiao Jin (小金)**: Wise hero, inventor, reborn with dual memories
- **Xiao Yu (小玉)**: Knowledge keeper, elderly advisor
- **Xiao Cai (小彩)**: Rainbow warrior, hot-headed but loyal
- **Heiyan (黑焰)**: Former villain turned chef
- **Purple Crystal King (紫晶国王)**: United ruler of merged kingdoms

See `GEMINI.md` for complete character profiles and story context.

### Writing Guidelines
- **Adventure-oriented**: Suspenseful, dynamic language
- **Interactive**: Each episode ends with thought-provoking questions
- **Micro-scale wonder**: Emphasis on size perception (corn leaves as carpets, raindrops as bombs)
- **Values**: Wisdom over force, inclusivity, non-violent conflict resolution

### Commit Message Format
Follow conventional commits:
```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore
```

Examples:
- `feat(story): Add episode 63 - The Crystal Cave`
- `docs(lore): Update character profiles for Season 5`
- `fix(analysis): Correct character extraction regex`

## Working with This Project

1. **Language**: Always use Chinese (Simplified) for story content and project documentation
2. **Reading order**: Follow the sequential numbering in `小金故事集/`
3. **Consistency**: Use the Python analysis tools to verify character and setting consistency
4. **Context**: Refer to `GEMINI.md` for character profiles and `conductor/` for project management

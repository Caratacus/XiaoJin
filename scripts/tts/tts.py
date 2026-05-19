#!/usr/bin/env python3
"""将小玉米粒王国故事转换为 MP3 语音"""

import asyncio
import os
import re
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import edge_tts
from edge_tts.exceptions import NoAudioReceived

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = "stories/第01季_生存与重生/第01集_灰霉蚧危机.md"

# 可用中文语音列表
VOICES = {
    "yunxi": "zh-CN-YunxiNeural",       # 男声，温和自然
    "yunyang": "zh-CN-YunyangNeural",    # 男声，新闻播报风
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",  # 女声，活泼
    "xiaoyi": "zh-CN-XiaoyiNeural",      # 女声，温柔
}

# 语速预设（百分比，正数加速，负数减速）
DEFAULT_BODY_RATE = "-12%"
RATE_PRESETS = {
    "slow": "-25%",
    "normal": DEFAULT_BODY_RATE,
    "fast": "+0%",
}

DEFAULT_INTRO_TEMPLATE = (
    "亲爱的小朋友们，欢迎来到皮皮爸爸讲故事。"
    "今天我们要讲的故事是《{title}》。小朋友准备好了吗？，我们要开始喽！"
)
DEFAULT_OUTRO_TEMPLATE = (
    "亲爱的小朋友，这一集的故事讲完了。"
    "刚才听到的是《{title}》。感谢你和皮皮爸爸一起听故事，我们下次再见。"
)
DEFAULT_FRAME_RATE = "-20%"
DEFAULT_FRAME_PITCH = "+5Hz"
DEFAULT_FRAME_VOLUME = "+10%"
DEFAULT_BODY_PITCH = "+0Hz"
DEFAULT_BODY_VOLUME = "+0%"

TITLE_RE = re.compile(r"^#\s+(.+?)\s*$")
SECTION_RE = re.compile(r"^\*{0,2}\s*(前情回顾|互动时刻)")
SEPARATOR_RE = re.compile(r"^---+\s*$")


@dataclass(frozen=True)
class SegmentStyle:
    """单段语音的朗读参数。"""

    rate: str
    pitch: str
    volume: str


@dataclass(frozen=True)
class ConversionJob:
    """单个 Markdown 到 MP3 的转换任务。"""

    input_path: Path
    output_path: Path


def extract_title(raw: str, fallback: str) -> str:
    """从 Markdown 中提取标题。"""
    for line in raw.splitlines():
        match = TITLE_RE.match(line)
        if match:
            return match.group(1).strip()
    return fallback


def extract_story(raw: str) -> str:
    """从 Markdown 中提取正文，去掉标题、前情回顾和互动时刻。"""
    lines = raw.splitlines()
    result: list[str] = []
    skip = False
    title_skipped = False

    for line in lines:
        if not title_skipped and TITLE_RE.match(line):
            title_skipped = True
            continue
        # 检测"前情回顾"或"互动时刻"标题，开始跳过
        if SECTION_RE.match(line):
            skip = True
            continue
        # 遇到分隔线 --- 且处于跳过模式，结束跳过
        if skip and SEPARATOR_RE.match(line):
            skip = False
            continue
        # 遇到下一个主标题，结束跳过
        if skip and TITLE_RE.match(line):
            skip = False
            continue
        if not skip:
            result.append(line)

    return "\n".join(result).strip()


def clean_markdown(text: str) -> str:
    """去除 Markdown 格式，保留纯文本"""
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_segment_text(template: str, title: str) -> str:
    """按模板生成片头或片尾文案。"""
    return template.format(title=title).strip()


async def write_segment_audio(
    file_obj, text: str, voice: str, style: SegmentStyle
) -> None:
    """将单段文本按指定风格写入音频文件。"""
    if not text.strip():
        return

    communicate = edge_tts.Communicate(
        text,
        voice,
        rate=style.rate,
        pitch=style.pitch,
        volume=style.volume,
    )
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            file_obj.write(chunk["data"])


def list_story_files(directory: Path) -> list[Path]:
    """列出目录下可转换的故事文件。"""
    return sorted(
        path
        for path in directory.glob("*.md")
        if path.is_file() and not path.name.startswith(".")
    )


def resolve_input_path(path_str: str) -> Path:
    """解析输入路径：优先当前工作目录，其次仓库根目录。"""
    path = Path(path_str)
    if path.is_absolute():
        return path

    cwd_path = path
    if cwd_path.exists():
        return cwd_path

    repo_path = REPO_ROOT / path
    return repo_path


def build_jobs(input_path: Path, output_path: Optional[Path], mode: str) -> list[ConversionJob]:
    """根据模式构建转换任务列表。"""
    if mode == "single":
        if input_path.is_dir():
            raise SystemExit("single 模式下，--input 必须是单个 Markdown 文件。")
        target = output_path if output_path else input_path.with_suffix(".mp3")
        return [ConversionJob(input_path=input_path, output_path=target)]

    if mode == "season":
        season_dir = input_path if input_path.is_dir() else input_path.parent
        if not season_dir.is_dir():
            raise SystemExit("season 模式下，--input 必须是季目录或该季中的 Markdown 文件。")
        stories = list_story_files(season_dir)
        if not stories:
            raise SystemExit(f"目录下没有可转换的 Markdown 文件: {season_dir}")
        output_dir = output_path if output_path else season_dir
        return [
            ConversionJob(input_path=story, output_path=output_dir / story.with_suffix(".mp3").name)
            for story in stories
        ]

    if mode == "all-by-season":
        root_dir = input_path
        if root_dir.is_file():
            raise SystemExit("all-by-season 模式下，--input 必须是 stories 根目录或包含各季目录的目录。")
        season_dirs = sorted(
            path
            for path in root_dir.iterdir()
            if path.is_dir() and not path.name.startswith(".") and path.name != "_backup"
        )
        if not season_dirs:
            raise SystemExit(f"未找到季目录: {root_dir}")

        jobs: list[ConversionJob] = []
        for season_dir in season_dirs:
            stories = list_story_files(season_dir)
            if not stories:
                continue
            season_output_dir = (output_path / season_dir.name) if output_path else season_dir
            jobs.extend(
                ConversionJob(
                    input_path=story,
                    output_path=season_output_dir / story.with_suffix(".mp3").name,
                )
                for story in stories
            )
        if not jobs:
            raise SystemExit(f"未找到可转换的 Markdown 文件: {root_dir}")
        return jobs

    raise SystemExit(f"不支持的 mode: {mode}")


async def convert_story(
    input_path: Path,
    output_path: Path,
    voice: str,
    body_style: SegmentStyle,
    frame_style: SegmentStyle,
    intro_template: str,
    outro_template: str,
    overwrite: bool = False,
) -> tuple[bool, str]:
    """执行单个故事文件转换。返回 (是否成功, 消息)。"""
    if output_path.exists() and not overwrite:
        return False, f"已存在，跳过: {output_path}"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    raw = input_path.read_text(encoding="utf-8")
    title = extract_title(raw, input_path.stem)
    body = clean_markdown(extract_story(raw))
    if not body:
        return False, f"未从文件中提取到正文: {input_path}"
    intro_text = build_segment_text(intro_template, title)
    outro_text = build_segment_text(outro_template, title)
    total_length = len(intro_text) + len(body) + len(outro_text)

    print(f"输入文件: {input_path}")
    print(f"输出文件: {output_path}")
    print(f"故事标题: {title}")
    print(f"文本长度: {total_length} 字符")
    print("开始转换...")

    segments = [
        ("片头", intro_text, frame_style),
        ("正文", body, body_style),
        ("片尾", outro_text, frame_style),
    ]

    try:
        with open(output_path, "wb") as f:
            for seg_name, seg_text, seg_style in segments:
                try:
                    await write_segment_audio(f, seg_text, voice, seg_style)
                except NoAudioReceived:
                    f.close()
                    output_path.unlink(missing_ok=True)
                    return False, f"[{seg_name}] 未收到音频数据，请检查文本内容或网络连接"
                except Exception as e:
                    f.close()
                    output_path.unlink(missing_ok=True)
                    return False, f"[{seg_name}] 转换失败: {e}"
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        output_path.unlink(missing_ok=True)
        return False, f"写入文件失败: {e}"

    size_bytes = output_path.stat().st_size
    size_mb = size_bytes / (1000 * 1000)
    print(f"转换完成！文件大小: {size_mb:.1f} MB ({size_bytes:,} bytes)")
    return True, "成功"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="故事转语音 MP3")
    parser.add_argument(
        "-i", "--input",
        default=DEFAULT_INPUT,
        help="输入的 Markdown 文件路径",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="输出路径；单篇模式可填 MP3 文件，批量模式可填输出目录",
    )
    parser.add_argument(
        "--mode",
        default="single",
        choices=("single", "season", "all-by-season"),
        help="生成模式：single=单篇，season=按季生成，all-by-season=全部生成按季生成",
    )
    parser.add_argument(
        "-v", "--voice",
        default="yunxi",
        choices=VOICES.keys(),
        help="语音角色（默认 yunxi）",
    )
    parser.add_argument(
        "-r", "--rate",
        default="normal",
        choices=RATE_PRESETS.keys(),
        help="正文语速预设（默认 normal，已比 edge_tts 默认语速更慢）",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="列出可用语音角色后退出",
    )
    parser.add_argument(
        "--intro-template",
        default=DEFAULT_INTRO_TEMPLATE,
        help="片头模板，支持 {title} 占位符",
    )
    parser.add_argument(
        "--outro-template",
        default=DEFAULT_OUTRO_TEMPLATE,
        help="片尾模板，支持 {title} 占位符",
    )
    parser.add_argument(
        "--frame-rate",
        default=DEFAULT_FRAME_RATE,
        help="片头片尾语速（默认更慢，示例 -35%%）",
    )
    parser.add_argument(
        "--frame-pitch",
        default=DEFAULT_FRAME_PITCH,
        help="片头片尾音高（默认 +8Hz）",
    )
    parser.add_argument(
        "--frame-volume",
        default=DEFAULT_FRAME_VOLUME,
        help="片头片尾音量（默认 +20%%）",
    )
    parser.add_argument(
        "--body-pitch",
        default=DEFAULT_BODY_PITCH,
        help="正文音高（默认 +0Hz）",
    )
    parser.add_argument(
        "--body-volume",
        default=DEFAULT_BODY_VOLUME,
        help="正文音量（默认 +0%%）",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="覆盖已存在的 MP3 文件（默认跳过）",
    )
    return parser.parse_args()


async def main() -> None:
    """命令行入口。

    主要参数说明：
    - --mode: 生成模式，默认 single；可选值为 single=单篇，season=按季生成，
      all-by-season=全部按季生成
    - -i/--input: 输入文件或目录，默认 stories/第01季_生存与重生/第01集_灰霉蚧危机.md；
      可传单个 Markdown、单季目录或 stories 根目录；相对路径会优先按当前目录解析，
      找不到时再按仓库根目录解析
    - -o/--output: 输出文件或输出目录，默认 None；未传时单篇输出到同名 .mp3，
      批量模式输出到原目录
    - -v/--voice: 语音角色，默认 yunxi；可选 yunxi、yunyang、xiaoxiao、xiaoyi
    - -r/--rate: 正文语速预设，默认 normal；slow=-25%%，normal=-12%%，fast=+0%%
    - --body-pitch: 正文音高，默认 +0Hz
    - --body-volume: 正文音量，默认 +0%%
    - --frame-rate: 片头片尾语速，默认 -20%%
    - --frame-pitch: 片头片尾音高，默认 +5Hz
    - --frame-volume: 片头片尾音量，默认 +10%%
    - --intro-template: 片头模板，默认“亲爱的小朋友们，欢迎来到皮皮爸爸讲故事。
      今天我们要讲的故事是《{title}》。小朋友准备好了吗？，我们要开始喽！”
    - --outro-template: 片尾模板，默认“亲爱的小朋友，这一集的故事讲完了。刚才听到的是
      《{title}》。感谢你和皮皮爸爸一起听故事，我们下次再见。”
    """
    args = parse_args()

    if args.list_voices:
        print("可用语音：")
        for name, voice_id in VOICES.items():
            print(f"  {name:12s} -> {voice_id}")
        return

    input_path = resolve_input_path(args.input)
    if not input_path.exists():
        raise SystemExit(f"文件不存在: {input_path}")
    output_path = Path(args.output) if args.output else None
    voice = VOICES[args.voice]
    body_style = SegmentStyle(
        rate=RATE_PRESETS[args.rate],
        pitch=args.body_pitch,
        volume=args.body_volume,
    )
    frame_style = SegmentStyle(
        rate=args.frame_rate,
        pitch=args.frame_pitch,
        volume=args.frame_volume,
    )
    print(f"语音角色: {voice}")
    print(
        f"正文风格: rate={body_style.rate}, pitch={body_style.pitch}, "
        f"volume={body_style.volume}"
    )
    print(
        f"片头片尾风格: rate={frame_style.rate}, pitch={frame_style.pitch}, "
        f"volume={frame_style.volume}"
    )
    print(f"生成模式: {args.mode}")

    jobs = build_jobs(input_path, output_path, args.mode)
    print(f"待转换文件数: {len(jobs)}")

    succeeded, skipped, failed = 0, 0, 0

    for index, job in enumerate(jobs, start=1):
        print(f"\n[{index}/{len(jobs)}]")
        ok, msg = await convert_story(
            input_path=job.input_path,
            output_path=job.output_path,
            voice=voice,
            body_style=body_style,
            frame_style=frame_style,
            intro_template=args.intro_template,
            outro_template=args.outro_template,
            overwrite=args.overwrite,
        )
        if ok:
            succeeded += 1
        elif "跳过" in msg:
            skipped += 1
            print(f"  跳过: {msg}")
        else:
            failed += 1
            print(f"  失败: {msg}")

    print(f"\n{'='*40}")
    print(f"完成: {succeeded}  跳过: {skipped}  失败: {failed}  共: {len(jobs)}")


if __name__ == "__main__":
    """python3 scripts/tts/tts.py --mode all-by-season -i stories -o mp3"""
    asyncio.run(main())

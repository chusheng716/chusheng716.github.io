#!/usr/bin/env python3
"""把一个 Word .docx 转成 content/fiction/ 下的 Hugo markdown。

一次转一篇（章）。title / weight 每篇不同，所以按篇调用，方便以后新章节复用：

    python3 scripts/docx_to_md.py drafts/野山神（第一篇章）3.docx \
        --title "野山神（第一篇章）" --weight 1 --slug yeshanshen-1

保留段落分隔（段落间空行），只取纯文本、丢掉 Word 的字体/颜色/加粗等格式。
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

try:
    import docx  # python-docx
except ImportError:
    sys.exit("需要 python-docx：pip install python-docx")


def docx_to_paragraphs(path):
    """返回非空段落的纯文本列表（strip 掉首尾空白，丢弃空段落）。"""
    doc = docx.Document(path)
    out = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            out.append(t)
    return out


def yaml_quote(s):
    # 双引号包裹，转义内部双引号和反斜杠，YAML 安全
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_markdown(paragraphs, title, date, weight, fandom):
    fm = [
        "---",
        f"title: {yaml_quote(title)}",
        f"date: {date}",
        "draft: false",
        f"weight: {weight}",
        f"fandom: [{yaml_quote(fandom)}]",
        "---",
        "",
    ]
    # 段落之间用空行分隔 —— markdown 的段落语义
    body = "\n\n".join(paragraphs)
    return "\n".join(fm) + body + "\n"


def default_slug(input_path):
    # 从文件名兜底一个 slug：去掉括号/空格里的噪声，非字母数字转连字符
    stem = Path(input_path).stem
    stem = re.sub(r"[（）()【】\s]+", "-", stem)
    return stem.strip("-").lower()


MARKER = re.compile(r"^(\d{1,2})\.$")  # 独占一行的小节标记，如 "00." "01."


def split_by_marker(paragraphs):
    """按 MARKER 行把段落切成若干小节，返回 [(章号int, [该节正文段落]), ...]。
    第一个标记之前的内容（如标题行）丢弃。"""
    chapters = []
    cur = None
    for p in paragraphs:
        m = MARKER.match(p)
        if m:
            cur = (int(m.group(1)), [])
            chapters.append(cur)
        elif cur is not None:
            cur[1].append(p)
    return chapters


def main():
    ap = argparse.ArgumentParser(description="docx -> Hugo fiction markdown")
    ap.add_argument("input", help="源 .docx 路径")
    ap.add_argument("--title", required=True, help="章节名（--split 时作为各小节标题的前缀）")
    ap.add_argument("--weight", type=int, help="章节序号，翻章节按它升序（不 --split 时必填）")
    ap.add_argument("--fandom", default="七小侠", help="所属圈子（默认 七小侠）")
    ap.add_argument("--date", default=str(datetime.date.today()), help="日期 YYYY-MM-DD，默认今天")
    ap.add_argument("--slug", help="输出文件名（不含 .md），--split 时作为前缀；默认从源文件名推导")
    ap.add_argument("--out-dir", default="content/fiction", help="输出目录")
    ap.add_argument("--split", action="store_true",
                    help="按文中 '00.' '01.' … 小节标记拆成多篇，weight=小节号")
    args = ap.parse_args()

    paras = docx_to_paragraphs(args.input)
    if not paras:
        sys.exit(f"没读到任何段落：{args.input}")

    base_slug = args.slug or default_slug(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.split:
        chapters = split_by_marker(paras)
        if not chapters:
            sys.exit(f"没找到 '00.' 这类小节标记，无法拆分：{args.input}")
        for num, body in chapters:
            title = f"{args.title}·{num:02d}"
            out_path = out_dir / f"{base_slug}-{num:02d}.md"
            # weight = 小节号 + 1：Hugo 把 weight 0 当“未加权”排到最后，所以从 1 起，
            # 保证 00→01→…→05 的翻章顺序正确。
            md = build_markdown(body, title, args.date, num + 1, args.fandom)
            out_path.write_text(md, encoding="utf-8")
            print(f"✓ 第 {num:02d} 节 (weight {num + 1}) -> {out_path}  （{len(body)} 段）")
    else:
        if args.weight is None:
            sys.exit("非 --split 模式需要 --weight")
        out_path = out_dir / f"{base_slug}.md"
        md = build_markdown(paras, args.title, args.date, args.weight, args.fandom)
        out_path.write_text(md, encoding="utf-8")
        print(f"✓ {args.input}\n  -> {out_path}  （{len(paras)} 段, {sum(len(p) for p in paras)} 字）")


if __name__ == "__main__":
    main()

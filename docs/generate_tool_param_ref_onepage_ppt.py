#!/usr/bin/env python3
"""One-slide deck for the tool-result reference scheme, editorial style."""

from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parent / "tool_param_ref_onepage.pptx"
W, H = Inches(13.333), Inches(7.5)

INK = RGBColor(28, 41, 37)
MUTED = RGBColor(107, 122, 116)
FAINT = RGBColor(154, 168, 162)
LINE = RGBColor(221, 229, 225)
TEAL = RGBColor(14, 111, 102)
TEAL_D = RGBColor(11, 84, 78)
WASH = RGBColor(244, 248, 246)
WHITE = RGBColor(255, 255, 255)
FONT = "Microsoft YaHei"

prs = Presentation()
prs.slide_width = W
prs.slide_height = H
slide = prs.slides.add_slide(prs.slide_layouts[6])


def txt(x, y, w, h, runs, align=PP_ALIGN.LEFT, line_spacing=1.15):
    """runs: list of paragraphs; each paragraph is list of (text, size, bold, color)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.clear()
    tf.word_wrap = True
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    first = True
    for para in runs:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.line_spacing = line_spacing
        p.space_after = Pt(2)
        for text, size, bold, color in para:
            r = p.add_run()
            r.text = text
            r.font.name = FONT
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.color.rgb = color
    return tf


def hline(x, y, w, color=LINE, weight=0.75):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Pt(weight))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    return sh


def vline(x, y, h, color=LINE, weight=0.75):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Pt(weight), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    return sh


def sec_heading(x, y, no, title, note=""):
    txt(x, y, 0.55, 0.24, [[(no, 11, True, TEAL)]])
    txt(x + 0.52, y - 0.015, 3.4, 0.26, [[(title, 13, True, INK)]])
    if note:
        txt(x + 3.9, y + 0.02, 8.6, 0.24, [[(note, 9, False, FAINT)]])


# background
bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
bg.fill.solid()
bg.fill.fore_color.rgb = WHITE
bg.line.fill.background()
slide.shapes._spTree.remove(bg._element)
slide.shapes._spTree.insert(2, bg._element)

MX = 0.62          # page margin
CW = 13.333 - 2 * MX

# ---------- header ----------
txt(MX, 0.30, CW, 0.2, [[("A G E N T · T O O L   C A L L I N G", 9, True, TEAL)]])
txt(MX, 0.52, CW, 0.42, [[("工具结果引用：让模型写「引用」，让 Runtime 填「真值」", 21.5, True, INK)]])
txt(MX, 0.98, 11.9, 0.3, [[
    ("上一个工具的结果不再回灌给模型抄写，而是由模型在下游参数里写一个引用；Runtime 在工具执行前从工作记忆取出真值、按需转换、校验合法，再去调用工具。", 10.5, False, INK),
]])
txt(MX, 1.24, 11.6, 0.24, [[
    ("真值全程不经模型之手，存量工具一行不改。", 10.5, True, TEAL_D),
]])
hline(MX, 1.58, CW, INK, 1.6)

# ---------- 01 why ----------
sec_heading(MX, 1.74, "01", "为什么要做")
txt(MX, 2.02, CW, 0.52, [[
    ("下一个工具的参数常来自上一个工具的结果：文件 URI、对象 ID、大段文本、一整个列表。这些值现在要先整段塞回模型上下文，再由模型原样抄进下游参数——长 URI 抄着抄着就断了；结构不一致时还要模型改写大段 JSON。抄写和改写，两件事模型都做不稳，而且每一轮都在烧 Token。", 10, False, INK),
]], line_spacing=1.3)
txt(MX, 2.62, CW, 0.22, [[
    ("抄不准 ", 9.5, True, INK), ("长值复述易截断、改写、漏字符　　", 9.5, False, MUTED),
    ("太昂贵 ", 9.5, True, INK), ("大结果反复回灌，Token和时延一起涨　　", 9.5, False, MUTED),
    ("改不动 ", 9.5, True, INK), ("结构适配靠模型改JSON或逐个改工具，都不划算", 9.5, False, MUTED),
]])

# ---------- 02 pipeline ----------
sec_heading(MX, 3.02, "02", "方案主链路", "Reference → Resolve → Invoke，全部发生在工具执行之前")
nodes = [
    ("工具 A", "结果入库", "返回结果默认写入工作记忆，得到短标识 resultId"),
    ("Runtime", "送模呈现", "指针字段直接换成引用给模型；要推理的内容照常给"),
    ("模型", "只写引用", "下游参数填 ${resultId.path}，不复述真值，所见即所填"),
    ("Runtime", "求值·转换·校验", "查工作记忆回填真值，按策略适配结构，验完Schema与权限"),
    ("工具 B", "真值执行", "校验通过才调用；结果再入库，链路闭环"),
]
NY, NH = 3.32, 1.02
NW, GAP = 2.22, 0.24
for i, (who, what, how) in enumerate(nodes):
    nx = MX + i * (NW + GAP)
    top = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(nx), Inches(NY), Inches(NW), Pt(2.2))
    top.fill.solid(); top.fill.fore_color.rgb = TEAL; top.line.fill.background()
    body = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(nx), Inches(NY + 0.03), Inches(NW), Inches(NH))
    body.fill.solid(); body.fill.fore_color.rgb = WASH; body.line.fill.background()
    txt(nx + 0.1, NY + 0.1, NW - 0.2, 0.17, [[(who, 8, True, FAINT)]])
    txt(nx + 0.1, NY + 0.28, NW - 0.2, 0.2, [[(what, 10.5, True, INK)]])
    txt(nx + 0.1, NY + 0.5, NW - 0.2, 0.5, [[(how, 8.3, False, MUTED)]], line_spacing=1.2)
    if i < len(nodes) - 1:
        txt(nx + NW + 0.015, NY + 0.38, 0.22, 0.26, [[("→", 12, True, TEAL)]], PP_ALIGN.CENTER)

# ---------- 03 three questions ----------
sec_heading(MX, 4.62, "03", "三个关键问题")
COLW = (CW - 0.8) / 3
cols = [
    ("引用怎么写", [
        ("用 ${resultId.path} 指定「哪条结果的哪个字段」：resultId 是入库时分配的短标识，path 支持点号取嵌套字段，如 ${a1b2c3d4.data.fileUri}。", INK),
        ("模型不需要看值时，送模前就换成引用，照抄即可；需要看值时内容照常给，参数仍写引用——「看」与「传」分开。", MUTED),
    ]),
    ("真值从哪来", [
        ("只从工作记忆取：先查全量结果集，未命中再查工具适配视图。resultId 由 Runtime 统一生成，对内保留与 toolCallId 的映射，可追踪、可对账。", INK),
        ("结构不一致时按参数策略转换：[563,728] 自动变成 [{\"file_id\":\"563\"},…]，模型和工具都不用动。", MUTED),
    ]),
    ("出错怎么办", [
        ("引用非法、结果不存在、字段没有、转换失败，一律短路：${…} 原文绝不透传给工具，错误明确回给模型，引导改写后重试。", INK),
        ("结果带会话作用域和有效期，过期或越权即拒绝；并行链路必须显式写 resultId，不允许含糊的「上一条」。", MUTED),
    ]),
]
CY = 4.92
for i, (title, paras) in enumerate(cols):
    cx = MX + i * (COLW + 0.4)
    if i > 0:
        vline(cx - 0.22, CY + 0.03, 1.28)
    txt(cx, CY, COLW, 0.22, [[(title, 11.5, True, TEAL_D)]])
    txt(cx, CY + 0.26, COLW, 1.1, [[(p, 8.6, False, c)] for p, c in paras], line_spacing=1.25)

# ---------- footer ----------
hline(MX, 6.42, CW)
gains = [
    ("省 Token", "大结果不再回灌复述，输入与时延同降"),
    ("抄不错", "真值不经模型之手，杜绝截断改写"),
    ("结构解耦", "上下游 Schema 差异由策略转换消化"),
    ("零改动", "能力在框架层，存量工具无感接入"),
]
GW = CW / 4
for i, (t, d) in enumerate(gains):
    gx = MX + i * GW
    txt(gx, 6.56, GW - 0.2, 0.22, [[(t, 11, True, TEAL_D)]])
    txt(gx, 6.8, GW - 0.2, 0.2, [[(d, 8.5, False, MUTED)]])

txt(MX, 7.08, CW, 0.26, [[
    ("模型决定「引用哪条结果的哪个字段」，Runtime 保证「真实、适配、合法」，然后才执行。", 10.5, True, INK),
]], PP_ALIGN.CENTER)

prs.save(OUT)
print(f"Wrote {OUT}")

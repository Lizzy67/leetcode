#!/usr/bin/env python3
"""Generate a one-slide PPT for the tool-parameter reference scheme (layered)."""

from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parent / "tool_param_ref_onepage.pptx"
W, H = Inches(13.333), Inches(7.5)

prs = Presentation()
prs.slide_width = W
prs.slide_height = H
slide = prs.slides.add_slide(prs.slide_layouts[6])

INK = RGBColor(21, 35, 31)
MUTED = RGBColor(96, 112, 106)
LINE = RGBColor(207, 219, 213)
WHITE = RGBColor(255, 255, 255)
TEAL = RGBColor(15, 118, 110)
TEAL_D = RGBColor(17, 94, 89)
SOFT = RGBColor(236, 248, 244)
BLUE = RGBColor(29, 79, 145)
BLUE_BG = RGBColor(237, 244, 252)
AMBER = RGBColor(138, 90, 0)
AMBER_BG = RGBColor(255, 247, 228)
RED = RGBColor(139, 49, 68)
RED_BG = RGBColor(255, 240, 243)


def fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def stroke(shape, color=LINE, width=1.0):
    shape.line.color.rgb = color
    shape.line.width = Pt(width)


def text_box(x, y, w, h, text="", size=11, bold=False, color=INK, margin=0.04, center=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    p = tf.paragraphs[0]
    if center:
        from pptx.enum.text import PP_ALIGN
        p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    r.font.name = "Microsoft YaHei"
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return tf


def add_line(tf, text, size=9.0, bold=False, color=INK, bullet=False, space=1, center=False):
    p = tf.add_paragraph()
    p.space_after = Pt(space)
    if center:
        from pptx.enum.text import PP_ALIGN
        p.alignment = PP_ALIGN.CENTER
    if bullet:
        text = "• " + text
    r = p.add_run()
    r.text = text
    r.font.name = "Microsoft YaHei"
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return p


def rect(x, y, w, h, bg=WHITE, line_color=LINE, width=1.0, rounded=True):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    fill(sh, bg)
    stroke(sh, line_color, width)
    return sh


def step(x, y, w, h, title, body, arrow=True):
    rect(x, y, w, h, WHITE)
    text_box(x + 0.06, y + 0.05, w - 0.12, 0.2, title, 8.2, True, TEAL_D, 0)
    text_box(x + 0.06, y + 0.27, w - 0.12, h - 0.3, body, 7.4, False, MUTED, 0)
    if arrow:
        text_box(x + w - 0.02, y + h / 2 - 0.13, 0.2, 0.26, "→", 12, True, TEAL, 0)


# Background
bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
fill(bg, WHITE)
bg.line.fill.background()
slide.shapes._spTree.remove(bg._element)
slide.shapes._spTree.insert(2, bg._element)

# ---------- Header ----------
text_box(0.35, 0.15, 7.0, 0.34, "智能体工具参数引用方案", 19, True, TEAL_D, 0)
text_box(
    7.5, 0.22, 5.45, 0.3,
    "结果引用 ${resultId.path}    语义引用 ${namespace.entity.attribute}",
    8.4, False, MUTED, 0,
)
bar = rect(0.35, 0.56, 12.63, 0.035, TEAL, TEAL, 0.5, rounded=False)
bar.line.fill.background()

# ---------- Layer 1: problem -> idea ----------
rect(0.35, 0.7, 6.15, 1.12, RED_BG, RGBColor(231, 196, 204))
tf = text_box(0.47, 0.76, 5.95, 0.22, "问题：模型直接生成业务真值不可靠", 10.5, True, RED, 0)
add_line(tf, "抄不准：长URI/列表照抄易截断改写，Token高", 8.2, bullet=True)
add_line(tf, "会编造：包名等弱语义标识凭记忆幻觉", 8.2, bullet=True)
add_line(tf, "改不动：上下游Schema不同，改长JSON不稳、改工具成本高", 8.2, bullet=True)

text_box(6.52, 1.08, 0.34, 0.36, "→", 18, True, TEAL, 0)

rect(6.88, 0.7, 6.1, 1.12, SOFT, RGBColor(188, 222, 212))
tf = text_box(7.0, 0.76, 5.9, 0.22, "核心思路：职责分离", 10.5, True, TEAL_D, 0)
add_line(tf, "模型只表达“引用谁”，Runtime负责“取真值、做适配、保合法”", 8.8, True, INK)
add_line(tf, "真值只来自可信数据源（工作记忆 / 语义词典）", 8.2, bullet=True)
add_line(tf, "全部处理收敛在工具执行前统一入口，工具零改动", 8.2, bullet=True)

# ---------- Layer 2: pipeline in 3 phases ----------
rect(0.35, 1.94, 12.63, 1.62, RGBColor(245, 251, 248), TEAL, 1.2)
text_box(0.47, 2.0, 5.0, 0.22, "主链路：Reference → Resolve → Invoke", 10.5, True, TEAL_D, 0)

# Phase groups
p1x, p1w = 0.47, 3.5
p2x, p2w = 4.07, 3.5
p3x, p3w = 7.67, 5.2
ph_y, ph_h = 2.28, 1.2

rect(p1x, ph_y, p1w, ph_h, BLUE_BG, BLUE_BG)
text_box(p1x, ph_y + 0.03, p1w, 0.2, "Ⅰ 引用表达（模型侧）", 8.4, True, BLUE, 0, center=True)
rect(p2x, ph_y, p2w, ph_h, AMBER_BG, AMBER_BG)
text_box(p2x, ph_y + 0.03, p2w, 0.2, "Ⅱ 求值与适配（Runtime侧）", 8.4, True, AMBER, 0, center=True)
rect(p3x, ph_y, p3w, ph_h, SOFT, SOFT)
text_box(p3x, ph_y + 0.03, p3w, 0.2, "Ⅲ 校验与执行（工具侧）", 8.4, True, TEAL_D, 0, center=True)

sy, sh_h = ph_y + 0.27, 0.84
step(p1x + 0.07, sy, 1.62, sh_h, "① 结果入库", "工具A返回，写工作记忆并生成resultId")
step(p1x + 0.07 + 1.72, sy, 1.62, sh_h, "② 送模呈现", "指针字段mask；要推理的留内容+引用")
step(p2x + 0.07, sy, 1.62, sh_h, "③ 模型填引用", "下游入参写${…}，不复述真值")
step(p2x + 0.07 + 1.72, sy, 1.62, sh_h, "④ 引用求值", "查记忆/词典，回填真值")
step(p3x + 0.07, sy, 1.62, sh_h, "⑤ 结构适配", "按参数Policy转换（可选）")
step(p3x + 0.07 + 1.7, sy, 1.62, sh_h, "⑥ 校验/短路", "Schema与权限校验；失败不透传")
step(p3x + 0.07 + 3.4, sy, 1.62, sh_h, "⑦ 执行闭环", "真值调工具B；结果再入库", arrow=False)

# ---------- Layer 3: three pillars ----------
py, ph = 3.68, 2.2
rect(0.35, py, 3.55, ph, BLUE_BG, RGBColor(190, 212, 236))
tf = text_box(0.47, py + 0.06, 3.35, 0.22, "支柱Ⅰ：引用怎么写", 10, True, BLUE, 0)
add_line(tf, "两类引用，同一管道", 8.4, True, INK, space=0)
add_line(tf, "结果引用 ${a1b2c3d4.fileUri} → 工作记忆", 7.8, bullet=True)
add_line(tf, "语义引用 ${app.抖音.bundleName} → 词典", 7.8, bullet=True)
add_line(tf, "两种可见性", 8.4, True, INK, space=0)
add_line(tf, "不用看值：mask后所见即所填", 7.8, bullet=True)
add_line(tf, "需要看值：内容供推理，入参仍写引用", 7.8, bullet=True)

rect(4.0, py, 4.2, ph, AMBER_BG, RGBColor(235, 215, 155))
tf = text_box(4.12, py + 0.06, 4.0, 0.22, "支柱Ⅱ：真值怎么来", 10, True, AMBER, 0)
add_line(tf, "可信数据源", 8.4, True, INK, space=0)
add_line(tf, "工作记忆：全量结果集 → 工具适配视图", 7.8, bullet=True)
add_line(tf, "语义词典：别名归一表 + 实体属性映射表", 7.8, bullet=True)
add_line(tf, "结构适配（Policy）", 8.4, True, INK, space=0)
add_line(tf, "${rid.merged_id_list} → [563,728]", 7.8, bullet=True)
add_line(tf, '→ [{"file_id":"563"}, {"file_id":"728"}]', 7.8, bullet=True)

rect(8.3, py, 4.68, ph, RED_BG, RGBColor(231, 196, 204))
tf = text_box(8.42, py + 0.06, 4.48, 0.22, "支柱Ⅲ：错误怎么兜", 10, True, RED, 0)
add_line(tf, "硬约束（Runtime）", 8.4, True, INK, space=0)
add_line(tf, "解析/映射/转换/Schema失败即短路，禁止${…}透传", 7.8, bullet=True)
add_line(tf, "作用域与权限由Runtime校验，模型无权决定", 7.8, bullet=True)
add_line(tf, "可恢复（兜底）", 8.4, True, INK, space=0)
add_line(tf, "多候选返回列表/动态枚举，不静默猜", 7.8, bullet=True)
add_line(tf, "未命中→查询工具→确认后刷新映射→重试", 7.8, bullet=True)

# ---------- Layer 4: benefits ----------
line = rect(0.35, 6.02, 12.63, 0.015, LINE, LINE, 0.5, rounded=False)
line.line.fill.background()
benefits = [
    ("省Token", "长值不回灌不复述，降输入与时延"),
    ("消幻觉", "真值只出自查表，标识不再编造"),
    ("少一轮", "映射命中时业务调用1次Loop完成"),
    ("零改动", "框架层统一生效，存量工具无感"),
]
bw = 3.1
for i, (title, body) in enumerate(benefits):
    x = 0.35 + i * (bw + 0.08)
    text_box(x, 6.12, bw, 0.24, title, 11, True, TEAL_D, 0, center=True)
    text_box(x, 6.38, bw, 0.24, body, 8.0, False, MUTED, 0, center=True)

text_box(
    0.35, 6.78, 12.63, 0.3,
    "一句话：模型决定“引用哪个对象”，Runtime保证“真实、适配、合法”后再执行。",
    10, True, TEAL_D, 0, center=True,
)

prs.save(OUT)
print(f"Wrote {OUT}")

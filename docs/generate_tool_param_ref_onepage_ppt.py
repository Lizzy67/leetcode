#!/usr/bin/env python3
"""Generate a one-slide PPT for the complete tool-parameter reference scheme."""

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
BLUE_BG = RGBColor(237, 244, 252)
AMBER_BG = RGBColor(255, 247, 228)
RED_BG = RGBColor(255, 240, 243)


def fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def stroke(shape, color=LINE, width=1):
    shape.line.color.rgb = color
    shape.line.width = Pt(width)


def text_box(x, y, w, h, text="", size=11, bold=False, color=INK, margin=0.05):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text
    r.font.name = "Microsoft YaHei"
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return tf


def add_line(tf, text, size=9.5, bold=False, color=INK, bullet=False, space=1):
    p = tf.add_paragraph()
    p.space_after = Pt(space)
    p.level = 0
    if bullet:
        text = "• " + text
    r = p.add_run()
    r.text = text
    r.font.name = "Microsoft YaHei"
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return p


def card(x, y, w, h, title, bg=WHITE, title_color=TEAL_D):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    fill(sh, bg)
    stroke(sh)
    tf = text_box(x + 0.12, y + 0.08, w - 0.24, h - 0.16, title, 11, True, title_color)
    return tf


def step(x, y, w, title, body, last=False):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.76)
    )
    fill(sh, WHITE)
    stroke(sh)
    text_box(x + 0.07, y + 0.08, w - 0.14, 0.22, title, 8.6, True, TEAL_D, 0)
    text_box(x + 0.07, y + 0.33, w - 0.14, 0.34, body, 7.7, False, MUTED, 0)
    if not last:
        text_box(x + w - 0.01, y + 0.24, 0.18, 0.25, "→", 13, True, TEAL, 0)


# Background
bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
fill(bg, WHITE)
bg.line.fill.background()
slide.shapes._spTree.remove(bg._element)
slide.shapes._spTree.insert(2, bg._element)

# Header
text_box(0.35, 0.18, 7.6, 0.32, "智能体工具参数引用方案", 19, True, TEAL_D, 0)
text_box(
    0.35, 0.52, 8.2, 0.24,
    "模型表达“引用谁” · Runtime负责“取真值、做转换、再调用” · 工具零改动",
    8.8, False, MUTED, 0
)
text_box(
    8.45, 0.25, 4.5, 0.34,
    "结果引用  ${resultId.path}    语义引用  ${namespace.entity.attribute}",
    8.2, False, MUTED, 0
)
bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.35), Inches(0.82), Inches(12.63), Inches(0.04))
fill(bar, TEAL)
bar.line.fill.background()

# Top cards
tf = card(0.35, 0.98, 3.75, 1.08, "为什么需要", SOFT)
add_line(tf, "长URI/列表照抄：Token高、易截断改写", 8.5, bullet=True)
add_line(tf, "包名等弱语义标识：模型易凭记忆编造", 8.5, bullet=True)
add_line(tf, "上下游Schema不同：模型改长JSON不稳定", 8.5, bullet=True)

tf = card(4.22, 0.98, 5.0, 1.08, "核心原则", BLUE_BG)
add_line(tf, "模型只输出引用意图，业务真值来自工作记忆/语义词典", 8.5, bullet=True)
add_line(tf, "统一Pre-call流水线：求值 → 转换 → 校验 → 调工具", 8.5, bullet=True)
add_line(tf, "存量工具继续接收原有真实参数，对引用协议无感", 8.5, bullet=True)

tf = card(9.34, 0.98, 3.64, 1.08, "可靠性底线", AMBER_BG)
add_line(tf, "解析/映射/转换/Schema失败即短路", 8.3, bullet=True)
add_line(tf, "禁止引用字面量或半成品透传工具", 8.3, bullet=True)
add_line(tf, "权限与作用域由Runtime校验", 8.3, bullet=True)

# Flow title and steps
text_box(0.4, 2.18, 2.0, 0.22, "完整主链路", 10.5, True, TEAL_D, 0)
sx, gap, sw = 0.35, 0.08, 1.73
steps = [
    ("① 工具返回", "工具A产出URI、ID、列表"),
    ("② 默认入库", "写Workmemory并生成resultId"),
    ("③ 送模", "按需mask或内容+引用"),
    ("④ 模型填引用", "下游参数不复述真值"),
    ("⑤ 引用求值", "查记忆或语义词典回填"),
    ("⑥ 转换/校验", "Policy适配结构并校验"),
    ("⑦ 执行闭环", "真值调工具B；结果再入库"),
]
for i, (title, body) in enumerate(steps):
    step(sx + i * (sw + gap), 2.43, sw, title, body, i == len(steps) - 1)

# Middle three cards
tf = card(0.35, 3.34, 4.0, 1.42, "两类引用 · 同一管道", BLUE_BG)
add_line(tf, "A  工具结果引用", 8.7, True, TEAL_D)
add_line(tf, "${a1b2c3d4.fileUri}  →  Workmemory", 8.0)
add_line(tf, "B  语义实体引用", 8.7, True, TEAL_D)
add_line(tf, "${app.抖音.bundleName}  →  别名归一 + 属性映射", 8.0)

tf = card(4.47, 3.34, 4.0, 1.42, "两种可见性", AMBER_BG)
add_line(tf, "模型不用看值：送模前mask为引用，所见即所填", 8.4, bullet=True)
add_line(tf, "模型需要看值：内容/摘要供推理，入参仍写引用", 8.4, bullet=True)
add_line(tf, "约束层级：Runtime硬校验 ＞ Schema/Skill ＞ Prompt", 8.0, True, TEAL_D)

tf = card(8.59, 3.34, 4.39, 1.42, "引用后可做结构适配", SOFT)
add_line(tf, "模型：images=${rid.merged_id_list}", 8.0)
add_line(tf, "Resolve：[563, 728]", 8.0)
add_line(tf, 'Transform：[{"file_id":"563"},{"file_id":"728"}]', 7.6)
add_line(tf, "先求值，再按目标参数Policy转换；模型/工具均不改结构", 7.8, True, TEAL_D)

# Bottom cards
tf = card(0.35, 4.89, 5.0, 1.35, "关键实现约定", WHITE)
add_line(tf, "结果默认写入Workmemory；查询可兼容全量结果集 → 工具适配视图", 8.2, bullet=True)
add_line(tf, "resultId为模型侧短标识；内部toolCallId继续用于追踪", 8.2, bullet=True)
add_line(tf, "通用mask字段（fileUri/fileId等）支持工具级覆盖", 8.2, bullet=True)

tf = card(5.47, 4.89, 3.45, 1.35, "核心收益", SOFT)
add_line(tf, "降Input Token与串行时延", 8.3, bullet=True)
add_line(tf, "减少长值抄错和业务标识幻觉", 8.3, bullet=True)
add_line(tf, "热路径少一次查询Loop；工具零改动", 8.3, bullet=True)

tf = card(9.04, 4.89, 3.94, 1.35, "边界与兜底", RED_BG)
add_line(tf, "多候选不静默猜：返回候选/动态枚举", 8.2, bullet=True)
add_line(tf, "未命中可查询并在确认后刷新映射", 8.2, bullet=True)
add_line(tf, "并行链路必须显式引用，不用含糊“上一条”", 8.2, bullet=True)

# Footer
text_box(
    0.4, 6.48, 9.7, 0.28,
    "一句话：模型只决定“引用哪个对象/结果”，Runtime保证“真实、适配、合法”后再执行。",
    9.3, True, TEAL_D, 0
)
text_box(
    9.85, 6.48, 3.1, 0.28,
    "Reference → Resolve → Transform → Validate → Invoke",
    7.8, False, MUTED, 0
)
line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.35), Inches(6.37), Inches(12.63), Inches(0.015))
fill(line, LINE)
line.line.fill.background()

prs.save(OUT)
print(f"Wrote {OUT}")

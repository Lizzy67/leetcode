#!/usr/bin/env python3
"""单独两页：逻辑架构图 + 运行视图（方案4主路径草稿）"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

W, H = Inches(13.333), Inches(7.5)
prs = Presentation()
prs.slide_width = W
prs.slide_height = H

NAVY = RGBColor(15, 23, 42)
SLATE = RGBColor(51, 65, 85)
TEAL = RGBColor(13, 148, 136)
TEAL_D = RGBColor(15, 118, 110)
LIGHT = RGBColor(248, 250, 252)
WHITE = RGBColor(255, 255, 255)
MUTED = RGBColor(100, 116, 139)
LINE = RGBColor(203, 213, 225)
SOFT = RGBColor(240, 253, 250)
AMBER_BG = RGBColor(255, 251, 235)
BLUE_BG = RGBColor(239, 246, 255)
PURPLE_BG = RGBColor(245, 243, 255)  # only for optional lane, muted
OK_BG = RGBColor(236, 253, 245)
GAP = RGBColor(180, 83, 9)


def fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def stroke(shape, color, w=1.25):
    shape.line.color.rgb = color
    shape.line.width = Pt(w)


def run(p, text, size, bold=False, color=SLATE, font="Calibri"):
    r = p.add_run()
    r.text = text
    r.font.size = size
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = font


def blank():
    return prs.slides.add_slide(prs.slide_layouts[6])


def bg(slide, color=LIGHT):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
    fill(sh, color)
    spTree = slide.shapes._spTree
    el = sh._element
    spTree.remove(el)
    spTree.insert(2, el)


def header(slide, title, sub):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, Inches(0.85))
    fill(bar, NAVY)
    acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(0.85), W, Inches(0.05))
    fill(acc, TEAL)
    tb = slide.shapes.add_textbox(Inches(0.45), Inches(0.18), Inches(12.4), Inches(0.6))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    run(p, title, Pt(20), True, WHITE)
    p2 = tf.add_paragraph()
    run(p2, sub, Pt(11), False, RGBColor(148, 163, 184))


def tbox(slide, l, t, w, h):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    return tf


def card(slide, l, t, w, h, title, lines, fill_c=WHITE, line_c=TEAL, title_c=TEAL_D):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    fill(sh, fill_c)
    stroke(sh, line_c)
    sh.adjustments[0] = 0.08
    tf = tbox(slide, l + Inches(0.12), t + Inches(0.1), w - Inches(0.22), h - Inches(0.16))
    p = tf.paragraphs[0]
    run(p, title, Pt(12), True, title_c)
    for line in lines:
        p2 = tf.add_paragraph()
        run(p2, line, Pt(10), False, SLATE)
        p2.space_before = Pt(2)
    return sh


def lane(slide, l, t, w, h, label, fill_c):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    fill(sh, fill_c)
    stroke(sh, LINE)
    sh.adjustments[0] = 0.03
    tf = tbox(slide, l + Inches(0.12), t + Inches(0.08), w - Inches(0.2), Inches(0.3))
    p = tf.paragraphs[0]
    run(p, label, Pt(11), True, MUTED)
    return sh


def arrow(slide, l, t, w=Inches(0.32), h=Inches(0.18), color=TEAL):
    sh = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, l, t, w, h)
    fill(sh, color)
    return sh


def down_arrow(slide, l, t, w=Inches(0.2), h=Inches(0.28), color=TEAL):
    sh = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, l, t, w, h)
    fill(sh, color)
    return sh


# ───────── Slide 1: Logical Architecture ─────────
s = blank()
bg(s)
header(s, "逻辑架构图（草稿）", "方案 4 主路径：云预览服务出链接 · WebView 直接渲染 | 灰色/虚线为可选增强")

# Layer 1 Client
lane(s, Inches(0.35), Inches(1.05), Inches(12.6), Inches(1.45), "端侧 Client", BLUE_BG)
card(s, Inches(0.55), Inches(1.4), Inches(3.8), Inches(0.95), "对话 UI", ["消息流 / 预览卡片入口"], WHITE, RGBColor(59, 130, 246))
card(s, Inches(4.55), Inches(1.4), Inches(4.0), Inches(0.95), "WebView / iframe", ["loadUrl(preview_url)", "sandbox 隔离策略"], WHITE, TEAL)
card(s, Inches(8.75), Inches(1.4), Inches(3.9), Inches(0.95), "降级：方案 A", ["REST 拉正文 → srcdoc", "（可选兜底）"], AMBER_BG, GAP, GAP)

# Layer 2 Agent
lane(s, Inches(0.35), Inches(2.65), Inches(12.6), Inches(1.7), "Agent 运行时", SOFT)
card(s, Inches(0.55), Inches(3.0), Inches(2.9), Inches(1.15), "LLM", ["生成可视化 HTML"], WHITE, TEAL)
card(s, Inches(3.6), Inches(3.0), Inches(2.9), Inches(1.15), "Skills", ["运动健康数据 Skill", "其它取数 Skill…"], WHITE, TEAL)
card(s, Inches(6.65), Inches(3.0), Inches(2.9), Inches(1.15), "Tools", ["write", "publish_preview ★"], WHITE, TEAL_D)
card(s, Inches(9.7), Inches(3.0), Inches(2.95), Inches(1.15), "会话/编排", ["工具结果回传端侧", "含 preview_url"], WHITE, TEAL)

# Layer 3 Data & Preview
lane(s, Inches(0.35), Inches(4.5), Inches(6.05), Inches(2.6), "文件与同步", OK_BG)
card(s, Inches(0.55), Inches(4.9), Inches(2.7), Inches(1.9), "Workspace", ["Agent 工作区落盘", "artifacts/*.html"], WHITE, OK_BG and TEAL)
card(s, Inches(3.4), Inches(4.9), Inches(2.75), Inches(1.9), "华为云空间", ["源文件仓 KooDrive", "REST 下载/元数据", "与预览域可解耦"], WHITE, TEAL)

lane(s, Inches(6.55), Inches(4.5), Inches(6.4), Inches(2.6), "Web 渲染中台（方案 4）★", SOFT)
card(s, Inches(6.75), Inches(4.9), Inches(5.95), Inches(1.9), "Preview Web Service", [
    "publish → 返回可访问 URL",
    "托管 HTML / 多文件静态资源",
    "Content-Type / CSP / TTL / 鉴权",
    "统一支撑报告、小工具等 Web 预览",
], WHITE, TEAL_D)

note = tbox(s, Inches(0.45), Inches(7.1), Inches(12.4), Inches(0.3))
p = note.paragraphs[0]
run(p, "关系：云空间存「源」· 预览服务出「可渲染链接」· 端只负责打开 URL（流式通道未画入主路径，属 B/C 增强）", Pt(10), False, MUTED)

# ───────── Slide 2: Runtime View ─────────
s = blank()
bg(s)
header(s, "运行视图（草稿）", "健康报告场景时序：Skill 取数 → 生成 HTML → 发布预览链接 → WebView 渲染")

# swimlanes labels
lanes = [
    (Inches(0.3), "用户/端"),
    (Inches(2.7), "Agent"),
    (Inches(5.1), "Skill"),
    (Inches(7.5), "云空间"),
    (Inches(9.9), "预览服务"),
]
for x, name in lanes:
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.05), Inches(2.2), Inches(0.4))
    fill(sh, NAVY)
    sh.adjustments[0] = 0.2
    tf = sh.text_frame
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    run(tf.paragraphs[0], name, Pt(12), True, WHITE)
    # life line
    line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x + Inches(1.05), Inches(1.5), Inches(0.04), Inches(5.5))
    fill(line, LINE)

# steps as horizontal message bars
steps = [
    (1.55, 0, 1, "① 发起：生成健康分析报告", TEAL),
    (2.2, 1, 2, "② 调用运动健康数据 Skill", TEAL),
    (2.85, 2, 1, "③ 返回指标数据", MUTED),
    (3.5, 1, 1, "④ LLM 生成图表化 HTML", TEAL),
    (4.15, 1, 3, "⑤ write 同步源文件（可选但推荐）", MUTED),
    (4.8, 1, 4, "⑥ publish_preview 发布页面", TEAL_D),
    (5.45, 4, 1, "⑦ 返回 preview_url (+ TTL)", TEAL_D),
    (6.1, 1, 0, "⑧ 工具结果带回端侧（含 URL）", TEAL),
    (6.75, 0, 4, "⑨ WebView.loadUrl(preview_url)", TEAL),
    (7.4, 4, 0, "⑩ 返回 text/html 页面完成渲染", TEAL),
]

# map lane index to x center
cx = [Inches(1.4), Inches(3.8), Inches(6.2), Inches(8.6), Inches(11.0)]

for y, src, dst, text, color in steps:
    y = Inches(y)
    x1, x2 = cx[src], cx[dst]
    left = min(x1, x2)
    width = abs(x2 - x1)
    if width < Inches(0.4):
        width = Inches(0.4)
    # message bar
    bar = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, y, width, Inches(0.42))
    fill(bar, color)
    bar.adjustments[0] = 0.25
    # label to the side if short, else on bar
    tf = tbox(s, Inches(0.35), y - Inches(0.02), Inches(12.6), Inches(0.38))
    # put text near destination for readability - actually overlay on full width caption left of bars is crowded
    # Use caption at left margin area spanning
    pass

# Cleaner: numbered list on left + simplified flow on right
# Redraw slide 2 more readably
# Remove previous messy approach by making a new clean slide instead.
# Actually the bars without text are useless. Rebuild slide 2 properly.

# Delete all shapes on slide 2 except we can't easily. Better recreate presentation slide.
# Simplest: create a fresh second slide content by not using the messy bars.
# I'll rebuild the whole presentation more cleanly in a second write.

prs = Presentation()
prs.slide_width = W
prs.slide_height = H

# ===== Logical =====
s = blank()
bg(s)
header(s, "逻辑架构图（草稿 · 请审）", "主路径=方案4；云空间=源文件仓；预览服务=可渲染 URL 入口")

# Client row
lane(s, Inches(0.3), Inches(1.05), Inches(12.7), Inches(1.55), "① 端侧", BLUE_BG)
card(s, Inches(0.5), Inches(1.4), Inches(4.0), Inches(1.0), "对话 UI", ["触发任务 / 展示预览卡片"], WHITE, RGBColor(37, 99, 235), RGBColor(37, 99, 235))
card(s, Inches(4.7), Inches(1.4), Inches(4.1), Inches(1.0), "WebView / iframe ★", ["直接打开 preview_url", "会话内渲染 HTML"], WHITE, TEAL)
card(s, Inches(9.0), Inches(1.4), Inches(3.7), Inches(1.0), "可选兜底 A", ["REST 下载 → srcdoc", "预览服务不可用时"], AMBER_BG, GAP, GAP)

# Agent row
lane(s, Inches(0.3), Inches(2.75), Inches(12.7), Inches(1.7), "② Agent 运行时", SOFT)
card(s, Inches(0.5), Inches(3.15), Inches(2.95), Inches(1.1), "编排 / Session", ["对话上下文", "工具调用编排"], WHITE, TEAL)
card(s, Inches(3.6), Inches(3.15), Inches(2.95), Inches(1.1), "LLM", ["生成图形化 HTML", "报告文案与结构"], WHITE, TEAL)
card(s, Inches(6.7), Inches(3.15), Inches(2.95), Inches(1.1), "Skills", ["运动健康数据", "其它业务取数"], WHITE, TEAL)
card(s, Inches(9.8), Inches(3.15), Inches(2.9), Inches(1.1), "Tools", ["write", "publish_preview ★"], WHITE, TEAL_D)

# Storage + Preview
lane(s, Inches(0.3), Inches(4.6), Inches(6.15), Inches(2.45), "③ 文件域", OK_BG)
card(s, Inches(0.5), Inches(5.0), Inches(2.85), Inches(1.8), "Workspace", ["本地/运行时工作区", "artifacts/ 产物"], WHITE, TEAL)
card(s, Inches(3.5), Inches(5.0), Inches(2.7), Inches(1.8), "华为云空间", ["源文件持久化", "REST 元数据/下载", "非必须当网站主机"], WHITE, TEAL)

lane(s, Inches(6.6), Inches(4.6), Inches(6.4), Inches(2.45), "④ Web 渲染中台（方案4）★", SOFT)
card(s, Inches(6.8), Inches(5.0), Inches(5.95), Inches(1.8), "Preview Web Service", [
    "输入：HTML 或 file_id / 目录",
    "输出：可访问 preview_url",
    "职责：托管、MIME、CSP、TTL、多文件",
], WHITE, TEAL_D)

# ===== Runtime =====
s = blank()
bg(s)
header(s, "运行视图（草稿 · 请审）", "健康报告端到端时序（方案4主路径；⑤ 云空间同步为推荐保留）")

# five columns
cols = ["用户 / 端侧", "Agent 运行时", "Skill", "华为云空间", "预览 Web 服务"]
col_x = [Inches(0.35), Inches(2.9), Inches(5.45), Inches(8.0), Inches(10.55)]
for i, name in enumerate(cols):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, col_x[i], Inches(1.05), Inches(2.35), Inches(0.45))
    fill(sh, NAVY)
    sh.adjustments[0] = 0.2
    tf = sh.text_frame
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    run(tf.paragraphs[0], name, Pt(11), True, WHITE)
    spine = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, col_x[i] + Inches(1.12), Inches(1.55), Inches(0.035), Inches(5.55))
    fill(spine, LINE)

# event cards near actor columns
events = [
    # y, col_index, text, color
    (1.7, 0, "1. 请求健康报告", TEAL),
    (2.25, 1, "2. 编排任务", TEAL),
    (2.8, 2, "3. 取运动健康数据", TEAL),
    (3.35, 1, "4. LLM 生成 HTML", TEAL),
    (3.9, 3, "5. write 同步源文件", MUTED),
    (4.45, 4, "6. publish 页面", TEAL_D),
    (5.0, 4, "7. 签发 preview_url", TEAL_D),
    (5.55, 1, "8. 回传 URL 给端", TEAL),
    (6.1, 0, "9. WebView 打开链接", TEAL),
    (6.65, 4, "10. 返回 HTML 完成渲染", TEAL),
]
for y, col, text, color in events:
    x = col_x[col]
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.08), Inches(y), Inches(2.2), Inches(0.42))
    fill(sh, color)
    sh.adjustments[0] = 0.2
    tf = sh.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    run(tf.paragraphs[0], text, Pt(10), True, WHITE)

# legend
leg = tbox(s, Inches(0.35), Inches(7.15), Inches(12.6), Inches(0.25))
p = leg.paragraphs[0]
run(p, "实心步骤=主路径　　灰色步骤=推荐保留的源文件同步　　箭头语义：从上到下为时间顺序，卡片所在列为执行方", Pt(10), False, MUTED)

out = "/workspace/docs/agent_html_arch_views.pptx"
prs.save(out)
print(f"Saved {out} slides={len(prs.slides)}")

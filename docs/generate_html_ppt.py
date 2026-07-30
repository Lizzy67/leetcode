#!/usr/bin/env python3
"""PPT: Agent 对话内 HTML 渲染方案（按敲定大纲 7 节）"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from copy import deepcopy

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
LINE = RGBColor(226, 232, 240)
SOFT = RGBColor(240, 253, 250)
AMBER_BG = RGBColor(255, 251, 235)
CODE_BG = RGBColor(15, 23, 42)
CODE_FG = RGBColor(226, 232, 240)
GAP = RGBColor(180, 83, 9)
OK = RGBColor(4, 120, 87)


def fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def run(p, text, size, bold=False, color=SLATE, font="Calibri"):
    r = p.add_run()
    r.text = text
    r.font.size = size
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = font
    return r


def blank():
    return prs.slides.add_slide(prs.slide_layouts[6])


def bg(slide, color=LIGHT):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
    fill(sh, color)
    spTree = slide.shapes._spTree
    el = sh._element
    spTree.remove(el)
    spTree.insert(2, el)


def header(slide, title, sub=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, Inches(1.0))
    fill(bar, NAVY)
    acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.0), W, Inches(0.05))
    fill(acc, TEAL)
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(0.22), Inches(12.3), Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run(p, title, Pt(22), True, WHITE)
    if sub:
        p2 = tf.add_paragraph()
        run(p2, sub, Pt(11), False, RGBColor(148, 163, 184))


def box(slide, l, t, w, h):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    return tf


def card(slide, l, t, w, h, title, lines, accent=TEAL, bgc=WHITE):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    fill(sh, bgc)
    sh.line.color.rgb = LINE
    sh.adjustments[0] = 0.06
    tf = box(slide, l + Inches(0.16), t + Inches(0.12), w - Inches(0.28), h - Inches(0.2))
    p = tf.paragraphs[0]
    run(p, title, Pt(13), True, accent)
    for line in lines:
        p2 = tf.add_paragraph()
        run(p2, line, Pt(11), False, SLATE)
        p2.space_before = Pt(3)


def set_cell(cell, text, size=10, bold=False, color=SLATE, fill_color=None, align=PP_ALIGN.LEFT):
    if fill_color:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill_color
    else:
        cell.fill.solid()
        cell.fill.fore_color.rgb = WHITE
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.clear()
    p.alignment = align
    run(p, text, Pt(size), bold, color)


# ─── Cover ───
s = blank()
bg(s, NAVY)
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(5.85), W, Inches(1.65))
fill(band, TEAL_D)
tf = box(s, Inches(0.7), Inches(2.1), Inches(11.8), Inches(2.5))
p = tf.paragraphs[0]
run(p, "对话内 HTML 渲染方案", Pt(34), True, WHITE)
p2 = tf.add_paragraph()
run(p2, "从健康报告场景出发：Skill 取数 → 图形化 HTML → 端侧安全呈现", Pt(16), False, RGBColor(148, 163, 184))
p2.space_before = Pt(12)
tf2 = box(s, Inches(0.7), Inches(6.2), Inches(11.8), Inches(1.0))
p = tf2.paragraphs[0]
run(p, "问题定义  ·  能力路径  ·  竞品对比  ·  Gap  ·  三方案  ·  示例  ·  建议", Pt(13), False, WHITE)

# ─── 1 问题定义 ───
s = blank()
bg(s)
header(s, "01  问题定义", "需要在端侧对话中直接渲染并展示模型生成的 HTML 内容")

card(s, Inches(0.45), Inches(1.3), Inches(7.5), Inches(3.5), "典型场景：个人健康分析报告", [
    "用户：「帮我生成最近的个人健康分析报告」",
    "",
    "1. Agent 调用「运动健康数据」Skill 拉取指标",
    "2. 模型结合数据，用图表/卡片等图形化方式生成 HTML",
    "3. 在对话中直接展示可交互报告（而不是源码或附件）",
    "",
    "成功标准：会话内可见、可交互；无需下载后另开应用。",
], TEAL, SOFT)

card(s, Inches(8.15), Inches(1.3), Inches(4.7), Inches(3.5), "本质诉求", [
    "不是「模型会不会写 HTML」",
    "而是「对话产品能否：",
    "  取数 → 可视化生成",
    "  → 端内安全渲染」",
    "",
    "断点往往在最后一跳：",
    "渲染容器 + 类型识别 + 沙箱",
])

card(s, Inches(0.45), Inches(5.0), Inches(12.4), Inches(2.1), "本次要回答", [
    "能力链上哪些已有、哪些缺口？竞品怎么做？我们与目标差在哪？",
    "下载后渲染 / 流式实时渲染 / 混合方案怎么选？如何落地与验收？",
])

# ─── 2 能力路径 ───
s = blank()
bg(s)
header(s, "02  实现能力路径", "生成 → 落盘 → 同步 → 渲染 → 安全 → 分享（标出已有 / 缺口）")

layers = [
    ("生成", "LLM + Skill 取数\n产出可视化 HTML", "已有", OK),
    ("落盘", "write 写入\nworkspace", "已有", OK),
    ("同步", "workspace →\n华为云空间", "已有", OK),
    ("渲染", "iframe / WebView\n会话内展示", "缺口", GAP),
    ("安全", "sandbox / CSP\n不可信隔离", "缺口", GAP),
    ("分享", "链接 / 回放\n转发", "可选", MUTED),
]
for i, (name, desc, st, col) in enumerate(layers):
    x = Inches(0.4) + Inches(i * 2.15)
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.4), Inches(2.0), Inches(4.0))
    fill(sh, WHITE if st != "缺口" else AMBER_BG)
    sh.line.color.rgb = col
    sh.adjustments[0] = 0.08
    # number
    top = s.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.7), Inches(1.6), Inches(0.55), Inches(0.55))
    fill(top, col)
    tf = box(s, x + Inches(0.7), Inches(1.68), Inches(0.55), Inches(0.45))
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run(p, str(i + 1), Pt(14), True, WHITE)
    tf = box(s, x + Inches(0.12), Inches(2.35), Inches(1.75), Inches(2.8))
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run(p, name, Pt(16), True, NAVY)
    for line in desc.split("\n"):
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        run(p2, line, Pt(11), False, SLATE)
        p2.space_before = Pt(4)
    p3 = tf.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    run(p3, st, Pt(13), True, col)
    p3.space_before = Pt(14)

tf = box(s, Inches(0.5), Inches(5.7), Inches(12.3), Inches(1.4))
p = tf.paragraphs[0]
run(p, "结论：生成 / 落盘 / 同步已通；产品断点在「渲染 + 安全」。分享与流式体验是增强项，不阻塞第一期闭环。", Pt(14), False, SLATE)
p2 = tf.add_paragraph()
run(p2, "健康报告场景映射：Skill 取数 ⊂ 生成层；图形化 HTML ⊂ 生成层；对话内看见 ⊂ 渲染层；防脚本越权 ⊂ 安全层。", Pt(12), False, MUTED)
p2.space_before = Pt(8)

# ─── 3 竞品 ───
s = blank()
bg(s)
header(s, "03  竞品对比", "多维度看「对话内可视化 / HTML 呈现」——对标 Artifact/Widget，而非一上来做全栈 Builder")

rows = [
    ["维度", "OpenClaw", "Cursor", "Claude", "Gemini", "ChatGPT", "Manus"],
    ["对话内\n实时预览", "强\nshow_widget", "弱*\n偏 IDE", "强\nArtifacts", "中～强\nCanvas 预览", "中\nCanvas/\n部分预览", "强\n托管预览"],
    ["呈现形态", "Widget/\nCanvas", "工作区\n文件", "侧栏\nArtifact", "Canvas\n工作区", "Canvas +\n代码解释器", "站点/\nApp 预览"],
    ["数据/工具", "Skill/\n工具调用", "FS/终端\n浏览器", "工具 +\nMCP", "工具 +\nWorkspace", "GPTs/\nADA 取数画图", "Agent\n全流程"],
    ["安全隔离", "双层 iframe\n沙箱", "工作区\n隔离", "独立域\n严 CSP", "平台沙箱", "平台沙箱", "托管隔离"],
    ["分享", "pin/\n渠道", "Git/PR", "Publish\n链接", "分享/\n导出 Docs", "分享链接\n(偏账号)", "一键\npublish"],
    ["对我们\n启示", "widget\n语义+沙箱", "复用 write\n不强造工具", "单文件\n预览体验", "Canvas+\n预览可参考", "取数可视化\n可参考 ADA", "后期分享\n可参考"],
]

table = s.shapes.add_table(len(rows), 7, Inches(0.3), Inches(1.25), Inches(12.7), Inches(5.5)).table
col_w = [Inches(1.35), Inches(1.9), Inches(1.85), Inches(1.9), Inches(1.9), Inches(1.9), Inches(1.9)]
for i, w in enumerate(col_w):
    table.columns[i].width = w

for r, row in enumerate(rows):
    for c, val in enumerate(row):
        cell = table.cell(r, c)
        if r == 0:
            set_cell(cell, val, 10, True, WHITE, NAVY, PP_ALIGN.CENTER)
        elif c == 0:
            set_cell(cell, val, 9, True, NAVY, SOFT, PP_ALIGN.CENTER)
        else:
            set_cell(cell, val, 9, False, SLATE, WHITE, PP_ALIGN.CENTER)

tf = box(s, Inches(0.4), Inches(6.85), Inches(12.5), Inches(0.45))
p = tf.paragraphs[0]
run(p, "* Cursor：强在仓库内工程能力，对话内「小工具预览」不是主路径。综合对标优先级：Claude Artifacts / OpenClaw Widget → 其次 Gemini/ChatGPT Canvas → 分享演进参考 Manus。", Pt(10), False, MUTED)

# ─── 4 Gap ───
s = blank()
bg(s)
header(s, "04  现状与目标架构 Gap", "复用 write + 云空间；补齐「可预览」闭环")

card(s, Inches(0.4), Inches(1.25), Inches(6.2), Inches(3.4), "现状", [
    "Skill 取数 → 模型生成 HTML",
    "→ write 落盘 → 同步华为云空间",
    "→ 端 REST 可下载",
    "",
    "已具备：生成 / 落盘 / 同步",
    "用户感知：多为附件或源码，",
    "「报告」没有在对话里长出来",
])
card(s, Inches(6.8), Inches(1.25), Inches(6.1), Inches(3.4), "目标", [
    "…… → 识别为 HTML 预览",
    "→ sandbox iframe/WebView 渲染",
    "→ 会话内可见可交互",
    "→（可选）分享 / 回放",
    "",
    "健康报告验收：打开会话即可",
    "查看图表化报告并交互",
], TEAL, SOFT)

card(s, Inches(0.4), Inches(4.85), Inches(12.5), Inches(2.3), "Gap 清单（按优先级）", [
    "P0  端侧无 HTML 预览容器（Web：iframe / 原生：WebView）",
    "P0  缺 preview 元数据约定（mime=text/html、preview.kind、sync_status、file_id）",
    "P0  缺安全默认（sandbox=allow-scripts，默认不加 allow-same-origin）",
    "P1  同步就绪信号（避免未 sync 完就拉 404）与刷新/降级策略",
    "P2  流式通道、混合预览、对外分享（签名 URL / TTL）",
])

# ─── 5 三方案 ───
s = blank()
bg(s)
header(s, "05  实现方案对比", "三种路径：完整下载渲染 / 流式实时渲染 / 混合（流式粗预览 + 落盘定稿）")

# table 3 schemes
rows = [
    ["", "方案 A\n下载后推送到端渲染", "方案 B\n模型输出流式到端实时渲染", "方案 C（混合）\n流式粗预览 + 完成后落盘定稿"],
    ["流程", "write→同步云空间\n→REST 下载全文\n→一次加载预览", "token/delta 推送\n→端 buffer\n→边收边刷新 iframe", "流式先出粗画面\n→同时/完成后 write 同步\n→最终以完整版替换"],
    ["优势", "稳、标签完整\n脚本只跑一次\n易刷新/回放/多端\n贴合现有云空间", "首屏快\n体感像流式 MD\n等待焦虑低", "体验接近 B\n正确性兜底靠 A\n适合报告类长 HTML"],
    ["劣势", "需等生成+同步\n才出首屏", "未闭合标签易花屏\n脚本易重复执行\n要单独推送通道", "实现与状态机更复杂\n需明确「粗预览/定稿」切换"],
    ["依赖", "write+云空间\n+端预览容器", "流式协议\n+端节流策略", "A+B 能力叠加"],
    ["建议", "一期默认 ★", "二期体验增强", "报告场景推荐演进 ★"],
]
table = s.shapes.add_table(len(rows), 4, Inches(0.3), Inches(1.2), Inches(12.7), Inches(5.9)).table
widths = [Inches(1.3), Inches(3.8), Inches(3.8), Inches(3.8)]
for i, w in enumerate(widths):
    table.columns[i].width = w
for r, row in enumerate(rows):
    for c, val in enumerate(row):
        cell = table.cell(r, c)
        if r == 0:
            set_cell(cell, val, 11, True, WHITE, NAVY if c == 0 else TEAL_D, PP_ALIGN.CENTER)
        elif c == 0:
            set_cell(cell, val, 11, True, NAVY, SOFT, PP_ALIGN.CENTER)
        elif r == 5:
            set_cell(cell, val, 11, True, OK if "★" in val else SLATE, AMBER_BG if "★" in val else WHITE, PP_ALIGN.CENTER)
        else:
            set_cell(cell, val, 10, False, SLATE, WHITE, PP_ALIGN.LEFT)

# ─── 6 实现示例 ───
s = blank()
bg(s)
header(s, "06  实现示例", "契约 + 健康报告最小闭环（以方案 A 为主，C 为增强）")

card(s, Inches(0.4), Inches(1.2), Inches(6.2), Inches(2.5), "1）工具返回约定（write/同步后）", [
    "path / cloud_file_id / mime=text/html",
    "sync_status=synced|syncing",
    "preview: { kind: \"html\", entry: true }",
    "",
    "端据此展示「预览卡片」而非纯附件行",
])

# code A
sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.2), Inches(6.1), Inches(2.5))
fill(sh, CODE_BG)
sh.adjustments[0] = 0.04
tf = box(s, Inches(6.95), Inches(1.3), Inches(5.8), Inches(2.3))
lines = [
    "// 方案 A：下载后一次渲染",
    "const html = await downloadText(fileId);",
    "iframe.sandbox = 'allow-scripts';",
    "iframe.srcdoc = html;  // 默不加 same-origin",
]
for i, line in enumerate(lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    if i:
        p.clear()
    run(p, line, Pt(11), False, CODE_FG, "Consolas")

card(s, Inches(0.4), Inches(3.9), Inches(6.2), Inches(3.2), "2）健康报告场景串接", [
    "① Skill 获取运动健康数据",
    "② 模型生成含图表的单文件 HTML",
    "   （CSS/JS 尽量内联，降低多文件依赖）",
    "③ write → 云空间同步就绪",
    "④ 端 REST 下载 → sandbox 预览",
    "⑤ 用户在会话内查看/交互报告",
])

sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(3.9), Inches(6.1), Inches(3.2))
fill(sh, CODE_BG)
sh.adjustments[0] = 0.04
tf = box(s, Inches(6.95), Inches(4.0), Inches(5.8), Inches(3.0))
lines = [
    "// 方案 C：流式粗预览 + 定稿",
    "onDelta(t => { buf += t; schedulePaint(buf); })",
    "onDone(async () => {",
    "  await writeAndSync(finalHtml);   // 落盘",
    "  iframe.srcdoc = await downloadText(id);",
    "})",
]
for i, line in enumerate(lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    if i:
        p.clear()
    run(p, line, Pt(11), False, CODE_FG, "Consolas")

# ─── 7 结论 ───
s = blank()
bg(s)
header(s, "07  结论与建议", "用最少改动打通「对话里看得见的健康报告」")

items = [
    ("问题本质", "对话内安全渲染可视化 HTML（Skill 取数 + 图形化生成 + 端呈现），不是再造存储。"),
    ("能力优先级", "先补渲染 + 安全；分享与流式后置。生成/落盘/同步已具备。"),
    ("竞品对标", "Claude Artifacts / OpenClaw Widget；Canvas 类作参考；分享演进看 Manus。"),
    ("方案选择", "一期默认方案 A；报告等待较长时演进方案 C；纯方案 B 不作唯一路径。"),
    ("安全底线", "模型 HTML=不可信；allow-scripts；慎开 allow-same-origin；预览与主站隔离。"),
    ("下一步", "元数据约定 + 端预览卡片 + sandbox；用「健康分析报告」做验收场景。"),
]
tf = box(s, Inches(0.6), Inches(1.3), Inches(12.1), Inches(5.8))
for i, (k, v) in enumerate(items):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    if i:
        p.clear()
    run(p, k + "  ", Pt(15), True, TEAL)
    run(p, v, Pt(15), False, SLATE)
    p.space_after = Pt(12)

out = "/workspace/docs/agent_html_preview_proposal.pptx"
prs.save(out)
print(f"Saved {out}, slides={len(prs.slides)}")

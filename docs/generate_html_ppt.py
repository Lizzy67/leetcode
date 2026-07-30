#!/usr/bin/env python3
"""Generate a systematic PPT on Agent HTML generation & in-chat preview."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
# Canvas 16:9
W, H = Inches(13.333), Inches(7.5)
prs = Presentation()
prs.slide_width = W
prs.slide_height = H

# Palette — slate + teal (avoid purple/cream AI clichés)
NAVY = RGBColor(15, 23, 42)       # #0F172A
SLATE = RGBColor(51, 65, 85)      # #334155
TEAL = RGBColor(13, 148, 136)     # #0D9488
TEAL_DARK = RGBColor(15, 118, 110)
LIGHT = RGBColor(248, 250, 252)   # #F8FAFC
WHITE = RGBColor(255, 255, 255)
MUTED = RGBColor(100, 116, 139)   # #64748B
LINE = RGBColor(226, 232, 240)
CARD = RGBColor(241, 245, 249)
CODE_BG = RGBColor(15, 23, 42)
CODE_FG = RGBColor(226, 232, 240)
WARN = RGBColor(180, 83, 9)


def _set_run(run, text, size, bold=False, color=NAVY, font="Calibri"):
    run.text = text
    run.font.size = size
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def _fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def blank():
    return prs.slides.add_slide(prs.slide_layouts[6])


def add_bg(slide, color=LIGHT):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
    _fill(shape, color)
    # send to back
    spTree = slide.shapes._spTree
    sp = shape._element
    spTree.remove(sp)
    spTree.insert(2, sp)


def header_bar(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, Inches(1.05))
    _fill(bar, NAVY)
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.05), W, Inches(0.06))
    _fill(accent, TEAL)
    tb = slide.shapes.add_textbox(Inches(0.55), Inches(0.22), Inches(12.2), Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    _set_run(r, title, Pt(24), bold=True, color=WHITE)
    if subtitle:
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        _set_run(r2, subtitle, Pt(12), color=RGBColor(148, 163, 184))


def body_box(slide, left, top, width, height):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    return tf


def add_bullets(tf, items, size=Pt(15), color=SLATE, space=8, first=True):
    for i, item in enumerate(items):
        if isinstance(item, tuple):
            text, level = item
        else:
            text, level = item, 0
        if first and i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.clear()
        p.level = level
        p.space_after = Pt(space)
        # allow simple **bold** prefix markers via leading "▸ "
        r = p.add_run()
        _set_run(r, text, size, bold=False, color=color)


def card(slide, left, top, width, height, title, lines, title_color=TEAL):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    _fill(shape, WHITE)
    shape.line.color.rgb = LINE
    shape.adjustments[0] = 0.08
    tf = body_box(slide, left + Inches(0.18), top + Inches(0.12), width - Inches(0.3), height - Inches(0.2))
    p = tf.paragraphs[0]
    r = p.add_run()
    _set_run(r, title, Pt(14), bold=True, color=title_color)
    for line in lines:
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        _set_run(r2, line, Pt(12), color=SLATE)
        p2.space_before = Pt(4)


def code_block(slide, left, top, width, height, lines):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    _fill(shape, CODE_BG)
    shape.adjustments[0] = 0.04
    tf = body_box(slide, left + Inches(0.22), top + Inches(0.15), width - Inches(0.35), height - Inches(0.25))
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if i > 0:
            p.clear()
        r = p.add_run()
        _set_run(r, line, Pt(11), color=CODE_FG, font="Consolas")
        p.space_after = Pt(1)


# ───────────────────────── SLIDES ─────────────────────────

# 1. Cover
s = blank()
add_bg(s, NAVY)
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(5.9), W, Inches(1.6))
_fill(band, TEAL_DARK)
tf = body_box(s, Inches(0.8), Inches(2.0), Inches(11.5), Inches(2.5))
p = tf.paragraphs[0]
r = p.add_run()
_set_run(r, "Agent 对话内 HTML 生成与端侧呈现", Pt(32), bold=True, color=WHITE)
p2 = tf.add_paragraph()
r2 = p2.add_run()
_set_run(r2, "从能力拆解到竞品范式，再到可落地的双路径方案", Pt(18), color=RGBColor(148, 163, 184))
p2.space_before = Pt(14)
tf2 = body_box(s, Inches(0.8), Inches(6.2), Inches(11.5), Inches(1.0))
p = tf2.paragraphs[0]
r = p.add_run()
_set_run(r, "技术分享  ·  系统方案  ·  实现路径建议", Pt(14), color=WHITE)

# 2. Agenda / Frame
s = blank()
add_bg(s)
header_bar(s, "01  先把问题说完整", "不是「会不会写 HTML」，而是「对话产品里如何安全地生成、分发、呈现可执行内容」")
card(s, Inches(0.5), Inches(1.4), Inches(4.0), Inches(5.5), "用户真正要的", [
    "在对话里看到可点可交互的页面",
    "而不是一段只能复制的源码",
    "可刷新、可回看、最好可分享",
    "",
    "体验对标：",
    "Claude Artifacts / OpenClaw Widget",
])
card(s, Inches(4.7), Inches(1.4), Inches(4.0), Inches(5.5), "容易误判的点", [
    "× 需要一个 generate_html 神器",
    "× 云空间「不支持」= 存不了",
    "× 有 write 就等于能预览",
    "× 流式下发 = 必须上存储",
    "",
    "√ 生成是模型能力",
    "√ 呈现是端能力",
    "√ 同步是基础设施",
])
card(s, Inches(8.9), Inches(1.4), Inches(3.9), Inches(5.5), "本次要讲清", [
    "① 能力分层：生成→落盘→同步",
    "   →识别→渲染→安全→分享",
    "② 竞品四类范式与可抄点",
    "③ 我们已有链路与缺口",
    "④ 双路径：完整下载 vs 流式",
    "⑤ 安全边界与落地节奏",
])

# 3. Capability stack
s = blank()
add_bg(s)
header_bar(s, "02  能力分层：支持 HTML 到底需要什么", "把「能生成网页」拆成 7 层，缺哪层体验就断在哪层")

layers = [
    ("1. 生成", "LLM 产出 HTML/CSS/JS 文本", "已有"),
    ("2. 落盘", "write / edit 写入 workspace", "已有"),
    ("3. 同步", "workspace → 华为云空间", "已有"),
    ("4. 识别", "MIME / 扩展名 / preview hint", "待补齐"),
    ("5. 渲染", "iframe（Web）/ WebView（原生）", "缺口"),
    ("6. 安全", "sandbox / CSP / 独立源", "缺口"),
    ("7. 分享", "稳定 URL / TTL / 历史回放", "可选增强"),
]
x0 = Inches(0.45)
for i, (name, desc, status) in enumerate(layers):
    x = x0 + Inches(i * 1.82)
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.55), Inches(1.7), Inches(4.2))
    _fill(box, WHITE if status != "缺口" else RGBColor(254, 243, 199))
    box.line.color.rgb = TEAL if status == "已有" else (WARN if status == "缺口" else LINE)
    box.adjustments[0] = 0.1
    tf = body_box(s, x + Inches(0.1), Inches(1.75), Inches(1.5), Inches(3.8))
    p = tf.paragraphs[0]
    r = p.add_run()
    _set_run(r, name, Pt(14), bold=True, color=NAVY)
    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    _set_run(r2, desc, Pt(11), color=SLATE)
    p2.space_before = Pt(10)
    p3 = tf.add_paragraph()
    r3 = p3.add_run()
    col = TEAL if status == "已有" else (WARN if status == "缺口" else MUTED)
    _set_run(r3, status, Pt(12), bold=True, color=col)
    p3.space_before = Pt(16)

tf = body_box(s, Inches(0.55), Inches(6.0), Inches(12.2), Inches(1.1))
p = tf.paragraphs[0]
r = p.add_run()
_set_run(r, "结论：我们不是从 0 做「生成 HTML」——生成/落盘/同步已通；产品断点在「识别 + 端侧安全渲染」。分享与流式是体验增强，不是第一期阻塞项。", Pt(13), color=SLATE)

# 4. Competitors
s = blank()
add_bg(s)
header_bar(s, "03  竞品范式：行业怎么解决同一问题", "四种产品形态，对应四种「呈现」策略——抄对范式比抄功能名更重要")

card(s, Inches(0.45), Inches(1.35), Inches(6.1), Inches(2.7), "A. Artifact / Widget（Claude · OpenClaw）", [
    "单文件自包含页面 → 会话侧栏 sandbox 预览",
    "独立源 + 严 CSP；可 Publish / pin",
    "适合：计算器、图表、小工具、演示页",
    "可抄：show_widget 语义 + 沙箱 iframe",
])
card(s, Inches(6.75), Inches(1.35), Inches(6.1), Inches(2.7), "B. IDE Agent（Cursor · Claude Code）", [
    "HTML 即普通文件；FS + 终端 + 浏览器",
    "交付物是仓库/PR，不是聊天小部件",
    "适合：进真实代码库改前端",
    "可抄：复用 write，不强造 generate_html",
])
card(s, Inches(0.45), Inches(4.25), Inches(6.1), Inches(2.7), "C. App Builder（Manus · Lovable · Bolt · v0）", [
    "生成工程 + 托管预览 / WebContainer",
    "发布是一等能力（URL、visibility、版本）",
    "适合：Prompt → 可分享站点",
    "可抄：后期的 publish / TTL 预览域",
])
card(s, Inches(6.75), Inches(4.25), Inches(6.1), Inches(2.7), "D. Doc Canvas（ChatGPT Canvas）", [
    "侧栏协作改文档/代码",
    "不是 HTML runtime，不对齐本需求",
    "启示：别把「编辑面」当成「渲染面」",
    "我们应对标 A，必要时向 C 演进",
])

# 5. Current + Target architecture
s = blank()
add_bg(s)
header_bar(s, "04  我们的现状与目标架构", "复用 write + 云空间；补齐「可预览」闭环，而不是新建一套存储")

# left current
card(s, Inches(0.45), Inches(1.35), Inches(6.1), Inches(3.35), "现状链路（已通）", [
    "Agent → write(path, content)",
    "→ workspace 落盘",
    "→ 同步华为云空间（KooDrive）",
    "→ 端 REST 按 file_id 下载",
    "",
    "断点：下载后当附件/源码，",
    "没有「这是网页，请画出来」的产品路径",
])
card(s, Inches(6.75), Inches(1.35), Inches(6.1), Inches(3.35), "目标闭环（要补）", [
    "write 返回：file_id + mime + sync_status",
    "运行时标记：previewable=html",
    "端：REST 取文本 → iframe/WebView 渲染",
    "安全：sandbox=allow-scripts（默不加 same-origin）",
    "",
    "可选：show_widget 薄封装（语义化触发预览）",
    "可选：流式粗预览；最终仍以完整版为准",
])

tf = body_box(s, Inches(0.55), Inches(4.9), Inches(12.2), Inches(2.2))
p = tf.paragraphs[0]
r = p.add_run()
_set_run(r, "端到端目标流", Pt(14), bold=True, color=TEAL)
lines = [
    "用户要交互页 → 模型生成 HTML → write 到 artifacts/*.html → 云空间同步就绪",
    "→ 工具结果带 file_id/mime → 端下载 → sandbox iframe/WebView 呈现 → 用户可交互",
    "→（可选）再次 write 覆盖 → 端刷新预览；（可选）对外分享仍用云空间 URL/签名链",
]
for line in lines:
    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    _set_run(r2, line, Pt(13), color=SLATE)
    p2.space_before = Pt(6)

# 6. Two render paths
s = blank()
add_bg(s)
header_bar(s, "05  两条渲染路径：完整下载 vs 流式增量", "都要有渲染引擎；差别只在「何时把 HTML 喂给引擎」")

card(s, Inches(0.45), Inches(1.35), Inches(6.1), Inches(5.5), "路径 A · 下载后完整渲染（推荐默认）", [
    "时机：sync 完成 → REST 拉全文 → 一次加载",
    "",
    "优点",
    "· 标签完整，不易花屏",
    "· 脚本只执行一次",
    "· 天然可刷新 / 多端 / 回放",
    "· 与现有云空间模型零阻抗",
    "",
    "代价",
    "· 需等生成+同步结束才出画面",
    "",
    "适用：几乎所有一期场景",
])
card(s, Inches(6.75), Inches(1.35), Inches(6.1), Inches(5.5), "路径 B · 流式边传边渲染（体验增强）", [
    "时机：token/delta 推送 → buffer → 节流刷新",
    "",
    "优点",
    "· 首屏更早，体感像流式 Markdown",
    "",
    "挑战（比 Markdown 更挑）",
    "· 未闭合标签破坏 DOM",
    "· srcdoc 重设导致脚本重复跑",
    "· 需要独立推送通道与状态机",
    "",
    "建议策略",
    "· 结构可增量；脚本等 done",
    "· 最终仍 upload/write 定稿",
])

# 7. Security + concepts
s = blank()
add_bg(s)
header_bar(s, "06  关键概念与安全默认", "MIME 决定「当什么打开」；iframe/WebView 决定「在哪画」；sandbox 决定「能闯多大祸」")

card(s, Inches(0.45), Inches(1.35), Inches(4.05), Inches(5.5), "MIME（Content-Type）", [
    "给字节贴类型标签",
    "",
    "text/html → 当网页渲染",
    "text/plain → 当纯文本",
    "octet-stream → 常当附件下载",
    "",
    "实践",
    "· write/同步带 mime=text/html",
    "· REST 尽量返回正确类型",
    "· 若云侧一律 octet-stream：",
    "  端按 .html 自行当 HTML 处理",
])
card(s, Inches(4.65), Inches(1.35), Inches(4.05), Inches(5.5), "iframe / WebView", [
    "同一类能力，不同载体",
    "",
    "Web 控制台 → iframe",
    "（页中嵌小网页）",
    "",
    "原生 App → WebView",
    "（App 内迷你浏览器）",
    "",
    "喂法",
    "· srcdoc / loadData（下载文本）",
    "· src / loadUrl（可打开的 URL）",
    "",
    "没有它们：只能下载或看源码",
])
card(s, Inches(8.85), Inches(1.35), Inches(4.0), Inches(5.5), "安全默认", [
    "HTML 来自模型 = 不可信",
    "",
    "sandbox=allow-scripts",
    "默认不加 allow-same-origin",
    "",
    "限制随意外链 / 白名单 CDN",
    "预览域与主站 cookie 隔离",
    "",
    "体积上限，敏感场景短 TTL",
    "需要时用 postMessage 桥",
    "而不是放开同源",
])

# 8. Implementation examples
s = blank()
add_bg(s)
header_bar(s, "07  建议契约与实现示例", "工具层给足元数据；端侧只做「识别 → 下载 → 沙箱渲染」")

tf = body_box(s, Inches(0.55), Inches(1.25), Inches(12.2), Inches(0.45))
p = tf.paragraphs[0]
r = p.add_run()
_set_run(r, "write / 同步完成后的建议返回（示意）", Pt(13), bold=True, color=TEAL)

code_block(s, Inches(0.45), Inches(1.7), Inches(6.1), Inches(2.35), [
    '{',
    '  "path": "artifacts/demo/index.html",',
    '  "cloud_file_id": "f_xxx",',
    '  "mime": "text/html",',
    '  "sync_status": "synced",',
    '  "preview": { "kind": "html", "entry": true }',
    '}',
])

code_block(s, Inches(6.75), Inches(1.7), Inches(6.1), Inches(2.35), [
    '// 路径 A：下载后一次渲染',
    'const html = await downloadText(fileId);',
    'iframe.sandbox = "allow-scripts";',
    'iframe.srcdoc = html;',
    '',
    '// 路径 B：流式 buffer（节流）',
    'onDelta(t => { buf += t; schedulePaint(); })',
    'onDone(() => { iframe.srcdoc = buf; })',
])

tf = body_box(s, Inches(0.55), Inches(4.25), Inches(12.2), Inches(2.8))
p = tf.paragraphs[0]
r = p.add_run()
_set_run(r, "端侧最小产品行为", Pt(13), bold=True, color=TEAL)
for line in [
    "1. 识别 preview.kind===html 或 path 以 .html/.htm 结尾 → 展示「预览卡片」，而不是纯附件行",
    "2. sync_status!==synced 时显示加载态；就绪后再 REST 拉正文",
    "3. Web 用 sandbox iframe；原生用 WebView loadData/loadUrl；失败则降级「下载 / 外开浏览器」",
    "4.（可选）show_widget({html|html_path|file_id})：对模型暴露「请展示」语义，内部仍走 write+同步",
]:
    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    _set_run(r2, line, Pt(13), color=SLATE)
    p2.space_before = Pt(6)

# 9. Roadmap
s = blank()
add_bg(s)
header_bar(s, "08  落地路径与优先级", "先闭环可见，再优化体感，最后做分享与多文件")

phases = [
    ("Phase 0", "对齐与验通", [
        "确认 write 已可写 .html",
        "手工同步/下载一轮",
        "确认 MIME 或扩展名策略",
    ], TEAL),
    ("Phase 1", "完整下载渲染", [
        "工具返回 mime/file_id/hint",
        "端预览卡片 + iframe/WebView",
        "sandbox 默认策略上线",
    ], TEAL),
    ("Phase 2", "体验与稳定", [
        "同步就绪推送/轮询",
        "刷新预览、错误降级",
        "单文件内联 CSS/JS 约定",
    ], TEAL_DARK),
    ("Phase 3", "流式 + 分享", [
        "delta 通道与节流渲染",
        "脚本延后执行策略",
        "签名 URL / TTL 分享",
    ], MUTED),
]
for i, (ph, title, lines, color) in enumerate(phases):
    x = Inches(0.45) + Inches(i * 3.2)
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.45), Inches(3.0), Inches(5.3))
    _fill(box, WHITE)
    box.line.color.rgb = LINE
    box.adjustments[0] = 0.08
    top = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.45), Inches(3.0), Inches(0.7))
    _fill(top, color)
    tf = body_box(s, x + Inches(0.15), Inches(1.55), Inches(2.7), Inches(0.5))
    p = tf.paragraphs[0]
    r = p.add_run()
    _set_run(r, f"{ph}  {title}", Pt(13), bold=True, color=WHITE)
    tf2 = body_box(s, x + Inches(0.18), Inches(2.35), Inches(2.65), Inches(4.1))
    first = True
    for line in lines:
        p = tf2.paragraphs[0] if first else tf2.add_paragraph()
        if not first:
            p.clear()
        first = False
        r = p.add_run()
        _set_run(r, "• " + line, Pt(13), color=SLATE)
        p.space_after = Pt(10)

# 10. Summary
s = blank()
add_bg(s)
header_bar(s, "09  结论与建议", "用最少改动打通「对话里看得见的网页」")

points = [
    ("定位", "对标 Artifact/Widget，而不是一上来做全栈 App Builder。"),
    ("真相", "生成靠模型；write+云空间已解决分发；缺口在端侧安全渲染。"),
    ("默认方案", "路径 A：同步完成后下载全文，sandbox iframe/WebView 一次渲染。"),
    ("增强方案", "路径 B：流式粗预览提升体感，定稿仍落盘；勿替代 A。"),
    ("安全底线", "模型 HTML 当不可信内容；allow-scripts，慎开 allow-same-origin。"),
    ("下一步", "Phase 0 验通 → Phase 1 预览卡片上线 → 再评估是否做流式。"),
]
tf = body_box(s, Inches(0.7), Inches(1.4), Inches(12.0), Inches(5.5))
for i, (k, v) in enumerate(points):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    if i > 0:
        p.clear()
    r1 = p.add_run()
    _set_run(r1, k + "  ", Pt(16), bold=True, color=TEAL)
    r2 = p.add_run()
    _set_run(r2, v, Pt(16), color=SLATE)
    p.space_after = Pt(14)

out = "/workspace/docs/agent_html_preview_proposal.pptx"
prs.save(out)
print(f"Saved {out} with {len(prs.slides)} slides")

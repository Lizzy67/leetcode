from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Styles
TITLE_SIZE = Pt(34)
SUBTITLE_SIZE = Pt(20)
BODY_SIZE = Pt(18)
SMALL_SIZE = Pt(14)
ACCENT = RGBColor(0, 112, 192)
DARK = RGBColor(40, 40, 40)
LIGHT = RGBColor(255, 255, 255)

def add_title_slide(title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = ACCENT
    tf = slide.shapes.add_textbox(Inches(0.8), Inches(2.4), Inches(11.7), Inches(1.5)).text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = TITLE_SIZE
    p.font.bold = True
    p.font.color.rgb = LIGHT
    p.alignment = PP_ALIGN.LEFT
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = SUBTITLE_SIZE
        p2.font.color.rgb = LIGHT
        p2.alignment = PP_ALIGN.LEFT
    return slide

def add_slide(title, bullets, note=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    # title bar
    bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()
    bar_tf = bar.text_frame
    bar_tf.paragraphs[0].text = title
    bar_tf.paragraphs[0].font.size = Pt(26)
    bar_tf.paragraphs[0].font.bold = True
    bar_tf.paragraphs[0].font.color.rgb = LIGHT
    bar_tf.paragraphs[0].alignment = PP_ALIGN.LEFT
    bar_tf.margin_left = Inches(0.6)

    # body
    body = slide.shapes.add_textbox(Inches(0.7), Inches(1.4), Inches(11.9), Inches(5.8))
    tf = body.text_frame
    tf.word_wrap = True
    for i, line in enumerate(bullets):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.font.size = BODY_SIZE
        p.font.color.rgb = DARK
        p.space_after = Pt(10)
        p.level = 0
    if note:
        p = tf.add_paragraph()
        p.text = note
        p.font.size = SMALL_SIZE
        p.font.color.rgb = RGBColor(100, 100, 100)
        p.space_before = Pt(12)
    return slide

def add_code_slide(title, code_lines, caption):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()
    bar_tf = bar.text_frame
    bar_tf.paragraphs[0].text = title
    bar_tf.paragraphs[0].font.size = Pt(26)
    bar_tf.paragraphs[0].font.bold = True
    bar_tf.paragraphs[0].font.color.rgb = LIGHT
    bar_tf.paragraphs[0].alignment = PP_ALIGN.LEFT
    bar_tf.margin_left = Inches(0.6)

    # code box
    box = slide.shapes.add_shape(1, Inches(0.7), Inches(1.4), Inches(11.9), Inches(5.0))
    box.fill.solid()
    box.fill.fore_color.rgb = RGBColor(245, 247, 250)
    box.line.color.rgb = RGBColor(200, 200, 200)
    tf = box.text_frame
    tf.word_wrap = False
    for i, line in enumerate(code_lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.font.name = "Consolas"
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(50, 50, 50)
        p.space_after = Pt(1)
    # caption
    cap = slide.shapes.add_textbox(Inches(0.7), Inches(6.5), Inches(11.9), Inches(0.6))
    cap_tf = cap.text_frame
    cap_tf.paragraphs[0].text = caption
    cap_tf.paragraphs[0].font.size = SMALL_SIZE
    cap_tf.paragraphs[0].font.color.rgb = RGBColor(100, 100, 100)
    return slide

# Slides
add_title_slide(
    "Agent 生成 HTML 并在端侧显示",
    "竞品调研 + 两条实现路径 + 落地建议"
)

add_slide(
    "我们在讨论什么",
    [
        "用户期望：让 Agent 生成可交互页面，并在对话/端内直接看见。",
        "关键事实：HTML 不是工具写出来的，而是 LLM 文本生成能力。",
        "平台需要：落盘、同步、渲染容器（iframe/WebView）。",
        "本方案围绕 Web 控制台 + 华为云空间同步链路设计。"
    ]
)

add_slide(
    "竞品怎么做：四类模式",
    [
        "1. Artifact 模式（Claude / OpenClaw）：单文件 HTML，侧栏 sandbox iframe 预览，可发布分享。",
        "2. IDE 模式（Cursor）：HTML 当普通文件写入工作区，再启动本地服务或浏览器。",
        "3. 全栈 App Builder（Manus / Lovable / Bolt）：生成工程 + 托管/WebContainer/真机预览。",
        "4. 文档 Canvas（ChatGPT Canvas）：侧重协作编辑，不跑 HTML 预览。"
    ],
    "我们优先对标 Artifact 模式：轻量、可预览、可分享。"
)

add_slide(
    "竞品给我们的核心启示",
    [
        "生成靠 LLM，平台负责：落盘、同步、渲染、安全。",
        "预览必须是沙箱化：独立源、iframe sandbox、CSP。",
        "单文件小工具 → 直接预览；多文件工程 → 托管/静态发布。",
        "外网/数据访问默认收紧：CDN 白名单或平台代理。"
    ]
)

add_slide(
    "我们现状：链路已具备",
    [
        "Agent 内置 write 工具 → workspace 文件。",
        "workspace 同步到华为云空间（KooDrive）。",
        "端侧通过云空间 REST API 下载文件。",
        "目前缺少：端侧 HTML 渲染容器 + 类型识别。"
    ],
    "不需要再造存储/上传，重点在「下载后如何安全地画出来」。"
)

add_slide(
    "方案 A：下载后完整渲染（推荐）",
    [
        "流程：Agent write → 同步云空间 → REST 下载 → 端侧 iframe 加载。",
        "优点：实现稳、无半截标签、脚本只执行一次、可分享/刷新。",
        "做法：下载 HTML 文本后，用 iframe srcdoc 或 WebView loadData。",
        "要求：Content-Type 为 text/html，或端按 .html 扩展名识别。"
    ]
)

add_slide(
    "方案 B：流式边传边渲染（二期优化）",
    [
        "流程：Agent 生成 token → 实时推送给端 → 端侧 buffer 累积 → 定时/完成后刷新 iframe。",
        "优点：首屏更早出现，体验接近流式 Markdown。",
        "挑战：未闭合标签会坏树、script 重复执行、闪烁。",
        "建议：先「收齐再渲染」做稳，再尝试「增量更新 + 脚本完成后执行」。"
    ]
)

add_code_slide(
    "方案 A 示例：Web 控制台 iframe 渲染",
    [
        "async function previewHtml(fileId) {",
        "  const res = await fetch(`/koodrive/files/${fileId}/content`);",
        "  const html = await res.text();",
        "  const iframe = document.createElement('iframe');",
        "  iframe.sandbox = 'allow-scripts';",
        "  iframe.srcdoc = html;",
        "  iframe.style.width = '100%';",
        "  iframe.style.height = '400px';",
        "  document.querySelector('#preview-slot').appendChild(iframe);",
        "}",
        "",
        "// 触发：Agent write 成功后，向端发送 fileId + mime='text/html'"
    ],
    "要点：allow-scripts 允许交互，但默认不要 allow-same-origin。"
)

add_code_slide(
    "方案 B 示例：流式增量预览",
    [
        "let buffer = '';",
        "const iframe = document.createElement('iframe');",
        "iframe.sandbox = 'allow-scripts';",
        "document.body.appendChild(iframe);",
        "",
        "eventSource.onmessage = (e) => {",
        "  buffer += e.data;",
        "  // 先渲染结构（脚本可等 done 后）",
        "  if (buffer.endsWith('</body>') || e.last) {",
        "    iframe.srcdoc = buffer;",
        "  }",
        "};"
    ],
    "要点：避免每 token 都刷新；建议按结构里程碑或完成后刷新。"
)

add_slide(
    "推荐实现路径（分两步）",
    [
        "第一期：下载后完整渲染。",
        "  1. 确认 write 同步 HTML 时 mime=\"text/html\">。",
        "  2. 端侧加 HTML 预览卡片（iframe/WebView）。",
        "  3. 默认 sandbox=\"allow-scripts\"，独立源。",
        "",
        "第二期：流式增量渲染。",
        "  1. 增加 token 级推送通道。",
        "  2. 端侧 buffer 累积 + 安全刷新策略。",
        "  3. 和方案 A 并存，最终仍以稳定版为准。"
    ]
)

add_slide(
    "总结",
    [
        "HTML 生成能力本质是 LLM 文本 + FS 落盘。",
        "我们已有 write + 云空间同步，缺的只是端侧渲染。",
        "先稳后快：先上「下载后完整渲染」，再试水「流式增量」。",
        "安全默认：iframe/WebView sandbox、避免 allow-same-origin、收紧外链。"
    ]
)

out = "/workspace/agent_html_preview_proposal.pptx"
prs.save(out)
print(f"Saved: {out}")

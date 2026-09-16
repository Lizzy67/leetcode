#!/usr/bin/env python3
"""汇报 PPT：小艺 Camera Tab（UEC）预览流 / 稳定帧 / 深度方案（领导评审版）。"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from lxml import etree

C_DARK = RGBColor(0x12, 0x1A, 0x22)
C_CARD = RGBColor(0xF4, 0xF7, 0xF9)
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
C_INK = RGBColor(0x1A, 0x2B, 0x3C)
C_MUTED = RGBColor(0x5A, 0x6B, 0x7C)
C_PRIMARY = RGBColor(0x0E, 0x7C, 0x86)
C_PRIMARY_D = RGBColor(0x0A, 0x5C, 0x64)
C_CAMERA = RGBColor(0x2F, 0x6F, 0xE5)   # 相机 App / 框架 / HAL
C_XIAOYI = RGBColor(0x0E, 0x7C, 0x86)   # 小艺 UEC
C_DEPTH = RGBColor(0xC4, 0x5C, 0x26)    # 深度 / 拍摄旁路
C_WARN = RGBColor(0xB5, 0x6E, 0x1A)
C_RISK = RGBColor(0xB9, 0x3A, 0x3A)
C_LINE = RGBColor(0xD0, 0xD8, 0xE0)
C_SOFT = RGBColor(0xE8, 0xF0, 0xF3)
C_SOFT_B = RGBColor(0xE3, 0xEC, 0xFB)
C_SOFT_T = RGBColor(0xD9, 0xEF, 0xF1)
C_SOFT_M = RGBColor(0xFA, 0xEB, 0xE0)
C_SOFT_R = RGBColor(0xFB, 0xE7, 0xE7)

TOTAL = 11
FONT = "Microsoft YaHei"


def set_run(run, size=18, bold=False, color=C_INK, font=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    r_pr = run._r.get_or_add_rPr()
    ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}ea"
    ea = r_pr.find(ns)
    if ea is None:
        ea = etree.SubElement(r_pr, ns)
    ea.set("typeface", font)


def add_text(shape, text, size=18, bold=False, color=C_INK, align=PP_ALIGN.LEFT):
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=color)
    return tf


def add_para(tf, text, size=14, bold=False, color=C_INK, space_before=6, align=None):
    p = tf.add_paragraph()
    p.space_before = Pt(space_before)
    if align is not None:
        p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=color)
    return p


def rect(slide, x, y, w, h, fill, line=None, radius=False, line_w=1.25):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
    if radius:
        s.adjustments[0] = 0.08
    return s


def box(slide, x, y, w, h, title, subtitle=None, fill=C_CARD, title_color=C_INK,
        sub_color=C_MUTED, title_size=14, sub_size=11, border=None):
    s = rect(slide, x, y, w, h, fill, line=border, radius=True)
    tf = s.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    tf.margin_top = Pt(6)
    tf.margin_bottom = Pt(6)
    tf.margin_left = Pt(6)
    tf.margin_right = Pt(6)
    run = tf.paragraphs[0].add_run()
    run.text = title
    set_run(run, size=title_size, bold=True, color=title_color)
    if subtitle:
        for i, line in enumerate(subtitle.split("\n")):
            p = tf.add_paragraph()
            p.alignment = PP_ALIGN.CENTER
            p.space_before = Pt(3 if i == 0 else 0)
            r = p.add_run()
            r.text = line
            set_run(r, size=sub_size, bold=False, color=sub_color)
    return s


def arrow_right(slide, x, y, w=0.4, h=0.2, color=C_PRIMARY):
    s = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    return s


def arrow_down(slide, x, y, w=0.2, h=0.35, color=C_PRIMARY):
    s = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    return s


def label(slide, x, y, w, h, text, size=12, bold=False, color=C_MUTED, align=PP_ALIGN.CENTER):
    s = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    add_text(s, text, size=size, bold=bold, color=color, align=align)
    return s


def chip(slide, x, y, w, text, fill, size=11):
    s = rect(slide, x, y, w, 0.32, fill, radius=True)
    add_text(s, text, size=size, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    return s


def title_bar(slide, title, subtitle=None, page=None):
    rect(slide, 0, 0, 13.333, 0.08, C_PRIMARY)
    t = slide.shapes.add_textbox(Inches(0.6), Inches(0.26), Inches(11.5), Inches(0.5))
    add_text(t, title, size=26, bold=True, color=C_INK)
    if subtitle:
        s = slide.shapes.add_textbox(Inches(0.6), Inches(0.76), Inches(12.0), Inches(0.35))
        add_text(s, subtitle, size=13, color=C_MUTED)
    if page is not None:
        p = slide.shapes.add_textbox(Inches(12.0), Inches(7.1), Inches(1.0), Inches(0.3))
        add_text(p, f"{page}/{TOTAL}", size=11, color=C_MUTED, align=PP_ALIGN.RIGHT)
    rect(slide, 0.6, 7.0, 12.1, 0.01, C_LINE)


def bullets(slide, x, y, w, h, lines, size=13, color=C_INK, space=7, first_bold=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = add_text(tb, lines[0], size=size, bold=first_bold, color=color)
    for line in lines[1:]:
        add_para(tf, line, size=size, color=color, space_before=space)
    return tf


def blank(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, C_WHITE)
    return slide


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # ---------------- 1 封面 ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, C_DARK)
    rect(slide, 0, 0, 0.18, 7.5, C_PRIMARY)
    rect(slide, 0, 6.9, 13.333, 0.6, C_PRIMARY_D)
    add_text(slide.shapes.add_textbox(Inches(0.9), Inches(1.9), Inches(11.5), Inches(1.0)),
             "小艺 Camera Tab（UEC）智能感知方案", size=36, bold=True, color=C_WHITE)
    add_text(slide.shapes.add_textbox(Inches(0.9), Inches(2.95), Inches(11.5), Inches(0.6)),
             "预览流获取 · 稳定帧门控 · 端侧模型推荐 · 拍摄取 RGB + 深度",
             size=18, color=RGBColor(0xB8, 0xC8, 0xD0))
    add_text(slide.shapes.add_textbox(Inches(0.9), Inches(3.8), Inches(11.5), Inches(0.4)),
             "方案评审 · 架构 / 关键流程 / 接口 / 风险 / 待决策项", size=14, color=C_PRIMARY)
    add_text(slide.shapes.add_textbox(Inches(0.9), Inches(7.05), Inches(10), Inches(0.3)),
             "小艺 × 相机 App × 相机框架/HAL 协同", size=12, color=RGBColor(0xD0, 0xE8, 0xEA))

    # ---------------- 2 背景与目标 ----------------
    slide = blank(prs)
    title_bar(slide, "背景与目标", "在相机内新增「小艺」Tab：看懂画面 → 主动推荐 → 一步执行", 2)

    goals = [
        ("用户价值", "取景时实时理解内容，弹出可点击 chips，\n少操作直达结果（识物 / 推荐 / AR）", C_XIAOYI, C_SOFT_T),
        ("业务价值", "小艺能力以 UEC 形式可插拔进相机，\n独立迭代、不改相机主流程", C_CAMERA, C_SOFT_B),
        ("技术目标", "稳定拿到预览流与运动状态；\n按需拿到对齐的 RGB + 深度；端侧闭环", C_DEPTH, C_SOFT_M),
    ]
    for i, (t, d, c, f) in enumerate(goals):
        x = 0.6 + i * 4.15
        rect(slide, x, 1.35, 3.9, 2.1, f, radius=True)
        chip(slide, x + 0.2, 1.55, 1.5, t, c)
        add_text(slide.shapes.add_textbox(Inches(x + 0.2), Inches(2.0), Inches(3.5), Inches(1.3)),
                 d, size=13, color=C_INK)

    rect(slide, 0.6, 3.75, 12.15, 2.95, C_CARD, radius=True)
    label(slide, 0.8, 3.9, 6, 0.3, "核心能力链路", 14, True, C_PRIMARY, PP_ALIGN.LEFT)
    steps = [
        ("预览流", "相机配流\n小艺消费"),
        ("运动 meta", "随帧实时\n上传应用层"),
        ("稳定帧门控", "独立模块\n判定触发"),
        ("感知 + 端侧模型", "内容识别\n推荐分析"),
        ("分发 / chips", "规则弹出\n点击执行"),
        ("拍摄 RGB+深度", "按需单次\n时间戳对齐"),
    ]
    for i, (t, d) in enumerate(steps):
        x = 0.8 + i * 1.98
        fill = C_SOFT_M if i == 5 else (C_SOFT_T if i in (2, 3, 4) else C_SOFT_B)
        tc = C_DEPTH if i == 5 else (C_XIAOYI if i in (2, 3, 4) else C_CAMERA)
        box(slide, x, 4.35, 1.75, 1.6, t, d, fill=fill, title_color=tc, title_size=13, sub_size=11)
        if i < 5:
            arrow_right(slide, x + 1.77, 5.05, 0.2, 0.16, C_LINE)
    add_text(slide.shapes.add_textbox(Inches(0.8), Inches(6.15), Inches(11.7), Inches(0.4)),
             "原则：摄像头会话只有一个主人（相机 App）；小艺是流的消费者与业务决策者，不直连 HAL / HDI。",
             size=12, bold=True, color=C_MUTED)

    # ---------------- 3 总体架构 ----------------
    slide = blank(prs)
    title_bar(slide, "总体架构", "相机进程握相机；小艺 UEC 进程消费流并做感知、推荐与 AR", 3)

    # 左：相机进程
    rect(slide, 0.5, 1.3, 5.6, 5.4, C_SOFT_B, radius=True)
    label(slide, 0.65, 1.4, 5.3, 0.3, "相机 App 进程（宿主）", 13, True, C_CAMERA, PP_ALIGN.LEFT)
    box(slide, 0.75, 1.85, 5.1, 0.85, "相机业务 + 对接小艺接口层",
        "Start/Stop 预览 · Capture · 抢占通知", fill=C_WHITE, title_color=C_CAMERA, title_size=13)
    arrow_down(slide, 3.2, 2.72, 0.2, 0.28, C_CAMERA)
    box(slide, 0.75, 3.05, 5.1, 0.8, "Camera Framework", "Session / Output 管理", fill=C_WHITE, title_size=13)
    arrow_down(slide, 3.2, 3.87, 0.2, 0.28, C_CAMERA)
    box(slide, 0.75, 4.2, 5.1, 0.55, "HDI（框架 ↔ HAL 接口，应用不直连）",
        fill=C_SOFT, title_color=C_MUTED, title_size=12)
    arrow_down(slide, 3.2, 4.77, 0.2, 0.28, C_CAMERA)
    box(slide, 0.75, 5.1, 5.1, 1.4, "Camera HAL · Sensor / ISP",
        "连续：预览 Buffer + 运动 metadata\n按需：单次深度计算 + 对齐 RGB", fill=C_WHITE,
        title_color=C_CAMERA, title_size=13, sub_size=11)

    # 中：跨进程
    rect(slide, 6.25, 3.0, 1.35, 1.6, C_CARD, radius=True, line=C_LINE)
    add_text(slide.shapes.add_textbox(Inches(6.28), Inches(3.1), Inches(1.3), Inches(1.4)),
             "跨进程\n\nsurfaceId\nBuffer\nfd / handle\nmetadata", size=10, color=C_MUTED, align=PP_ALIGN.CENTER)
    arrow_right(slide, 6.25, 2.6, 1.35, 0.22, C_PRIMARY)
    arrow_right(slide, 6.25, 4.85, 1.35, 0.22, C_DEPTH)

    # 右：小艺 UEC
    rect(slide, 7.75, 1.3, 5.1, 5.4, C_SOFT_T, radius=True)
    label(slide, 7.9, 1.4, 4.8, 0.3, "小艺 UEC 进程（Tab）", 13, True, C_XIAOYI, PP_ALIGN.LEFT)
    box(slide, 7.95, 1.85, 4.7, 0.75, "预览消费 + 三路分发", "显示 · 模型 · AR（限流）",
        fill=C_WHITE, title_color=C_XIAOYI, title_size=13)
    box(slide, 7.95, 2.75, 2.25, 0.9, "稳定帧门控", "独立模块\nmotion meta", fill=C_WHITE, title_size=12, sub_size=10)
    box(slide, 10.4, 2.75, 2.25, 0.9, "感知 / 端侧模型", "稳定后触发", fill=C_WHITE, title_size=12, sub_size=10)
    arrow_right(slide, 10.22, 3.1, 0.16, 0.16, C_XIAOYI)
    box(slide, 7.95, 3.8, 2.25, 0.9, "AR 空间建模", "自有帧率/分辨率", fill=C_WHITE, title_size=12, sub_size=10)
    box(slide, 10.4, 3.8, 2.25, 0.9, "分发服务 + 规则", "chips 弹出 / 点击", fill=C_WHITE, title_size=12, sub_size=10)
    box(slide, 7.95, 4.85, 4.7, 0.8, "拍摄按钮 → CaptureAt(ts)",
        "收 RGB + 深度(fd) + meta，对齐后用于推荐 / AR", fill=C_SOFT_M, title_color=C_DEPTH, title_size=12, sub_size=10)
    box(slide, 7.95, 5.8, 4.7, 0.7, "显示层（XComponent 可用性待实测）",
        fill=C_SOFT_R, title_color=C_RISK, title_size=11)

    # ---------------- 4 预览流获取与分发 ----------------
    slide = blank(prs)
    title_bar(slide, "关键设计 ①｜预览流获取与三路分发", "小艺提供/消费 Surface；配流由相机 App → 框架 → HAL 完成", 4)

    nodes = [
        ("进 Tab", "UEC 拉起", C_WHITE, C_MUTED),
        ("交换 Surface", "surfaceId / 尺寸\nBT709_FULL / fps", C_SOFT_T, C_XIAOYI),
        ("相机配流", "Session 增加\n小艺 Output", C_SOFT_B, C_CAMERA),
        ("HAL 出图", "预览 Buffer +\n运动 meta 同 ts", C_SOFT_B, C_CAMERA),
        ("小艺分发", "显示 / 模型 / AR", C_SOFT_T, C_XIAOYI),
    ]
    for i, (t, d, f, c) in enumerate(nodes):
        x = 0.55 + i * 2.5
        box(slide, x, 1.35, 2.2, 1.25, t, d, fill=f, title_color=c, title_size=14, sub_size=11,
            border=C_LINE)
        if i < 4:
            arrow_right(slide, x + 2.22, 1.88, 0.26, 0.2, C_PRIMARY)

    rect(slide, 0.55, 2.9, 6.0, 3.75, C_SOFT, radius=True)
    label(slide, 0.75, 3.02, 5.5, 0.3, "三路分发怎么做（待拍板 B）", 14, True, C_PRIMARY, PP_ALIGN.LEFT)
    box(slide, 0.8, 3.5, 2.7, 1.35, "方案 B1：多 Output", "相机一次出三路\n各路独立分辨率/帧率\n少拷贝，接口复杂",
        fill=C_WHITE, title_color=C_CAMERA, title_size=12, sub_size=10)
    box(slide, 3.7, 3.5, 2.7, 1.35, "方案 B2：单路再 fork", "小艺收一路后分发\n接口简单，先跑通\n需应用内降采样",
        fill=C_WHITE, title_color=C_XIAOYI, title_size=12, sub_size=10)
    bullets(slide, 0.8, 5.0, 5.6, 1.6, [
        "显示：全分辨率（30fps）",
        "模型：小图 + 低频（1～5fps，稳定帧触发）",
        "AR：按算法需求单独约定",
        "禁止：三路全帧率全分辨率裸拷贝（功耗/发热）",
    ], size=12, space=4)

    rect(slide, 6.8, 2.9, 6.0, 3.75, C_SOFT_M, radius=True)
    label(slide, 7.0, 3.02, 5.5, 0.3, "格式与元数据契约", 14, True, C_DEPTH, PP_ALIGN.LEFT)
    bullets(slide, 7.0, 3.45, 5.6, 3.1, [
        "BT709_FULL = BT.709 色域语义 + Full range；决定「数值怎么解释」",
        "需写死：实际像素格式（RGB / NV12…）、位深、stride、旋转责任方",
        "运动 meta 随预览每帧上传：gyro / accel / 对焦 / 曝光",
        "硬约束：meta.timestamp 与 frame.timestamp 可对齐；meta 缺失不得判稳",
        "Surface 归属（待拍板 A）：谁创建、谁销毁、切 Tab 时谁先停",
    ], size=12, space=6)

    # ---------------- 5 稳定帧门控 ----------------
    slide = blank(prs)
    title_bar(slide, "关键设计 ②｜稳定帧门控 → 感知 → 模型", "门控独立成模块，挂在 Tab 业务层；感知只消费稳定事件", 5)

    flow = [
        ("预览帧 + 运动 meta", "每帧，很轻", C_SOFT_B, C_CAMERA),
        ("StableFrameDetector", "门控：稳不稳\n|gyro|/accel 阈值\n连续 K 帧 / M ms", C_SOFT_T, C_XIAOYI),
        ("感知 Perception", "内容：有什么\n检测 / 识别", C_SOFT_T, C_XIAOYI),
        ("端侧大模型", "推荐分析\n异步 + 过期丢弃", C_SOFT_T, C_XIAOYI),
        ("分发 → chips", "规则 / 冷却 / 去重", C_SOFT_M, C_DEPTH),
    ]
    for i, (t, d, f, c) in enumerate(flow):
        x = 0.55 + i * 2.5
        box(slide, x, 1.35, 2.2, 1.45, t, d, fill=f, title_color=c, title_size=13, sub_size=10,
            border=C_XIAOYI if i == 1 else C_LINE)
        if i < 4:
            arrow_right(slide, x + 2.22, 1.98, 0.26, 0.2, C_PRIMARY)
    label(slide, 3.05, 2.85, 2.2, 0.3, "不稳 → 丢弃 / 取消推理", 10, False, C_RISK)

    rect(slide, 0.55, 3.3, 6.0, 3.35, C_SOFT_T, radius=True)
    label(slide, 0.75, 3.42, 5.5, 0.3, "为什么独立成模块（而非塞进感知前）", 14, True, C_XIAOYI, PP_ALIGN.LEFT)
    rows = [
        ("职责", "稳不稳（传感器） vs 有什么（内容）"),
        ("复用", "模型、AR 关键帧、深度、chips 都订同一事件"),
        ("节奏", "每帧轻量先挡掉大部分重活，可单独调参/关闭"),
        ("测试", "喂假 meta 即可单测，不依赖整条感知链"),
    ]
    for i, (k, v) in enumerate(rows):
        y = 3.85 + i * 0.65
        key = rect(slide, 0.8, y, 1.1, 0.5, C_XIAOYI, radius=True)
        add_text(key, k, size=12, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
        val = rect(slide, 2.0, y, 4.3, 0.5, C_WHITE, radius=True)
        add_text(val, v, size=12, color=C_INK, align=PP_ALIGN.LEFT)

    rect(slide, 6.8, 3.3, 6.0, 3.35, C_CARD, radius=True)
    label(slide, 7.0, 3.42, 5.5, 0.3, "门控输入 / 输出与参数", 14, True, C_PRIMARY, PP_ALIGN.LEFT)
    bullets(slide, 7.0, 3.85, 5.6, 2.7, [
        "输入：MotionMetadata（gyro/accel/afState/exposure，同 ts）",
        "可选辅助：轻量帧差 / 光流，用于无 meta 兜底",
        "输出：OnStableFrame(ts)、OnUnstable()",
        "参数（待拍板 L）：阈值、K 帧、M ms、冷却时间",
        "点击拍摄仍可强制 Capture，不必非稳不可（产品定）",
    ], size=12, space=6)

    # ---------------- 6 拍摄取 RGB + 深度 ----------------
    slide = blank(prs)
    title_bar(slide, "关键设计 ③｜点击拍摄：RGB + 深度 + 运动 meta", "不是从旧预览里「挖」深度，而是按 timestamp 触发一次带深度的 Capture", 6)

    seq = [
        ("① 用户点拍摄", "记录 targetTimestamp = T\n（可先确认稳定）", C_SOFT_T, C_XIAOYI),
        ("② 小艺 → 相机", "CaptureAt(T, needRgb,\nneedDepth, allowPause)", C_SOFT_T, C_XIAOYI),
        ("③ 框架 → HDI → HAL", "抓近 T 的 RGB\n单次算深度\n附运动 meta", C_SOFT_B, C_CAMERA),
        ("④ 回传小艺", "rgb + depth fd/handle\n+ 尺寸/单位/置信度\n同一 timestamp", C_SOFT_M, C_DEPTH),
        ("⑤ 小艺处理", "map fd 读深度\n对齐校验 → 模型/AR\n释放 fd，恢复预览", C_SOFT_T, C_XIAOYI),
    ]
    for i, (t, d, f, c) in enumerate(seq):
        x = 0.55 + i * 2.5
        box(slide, x, 1.35, 2.2, 1.6, t, d, fill=f, title_color=c, title_size=13, sub_size=10, border=C_LINE)
        if i < 4:
            arrow_right(slide, x + 2.22, 2.05, 0.26, 0.2, C_DEPTH)

    rect(slide, 0.55, 3.3, 4.0, 3.35, C_CARD, radius=True)
    label(slide, 0.75, 3.42, 3.6, 0.3, "名词速查", 14, True, C_PRIMARY, PP_ALIGN.LEFT)
    bullets(slide, 0.75, 3.85, 3.6, 2.7, [
        "fd：跨进程共享大块内存的「取货号」",
        "handle：指向 Buffer 的凭证（可含 fd）",
        "HDI：框架 ↔ HAL 接口层，小艺不直连",
        "深度经 HDI 上行 → 框架 → 相机 App → 小艺",
    ], size=12, space=8)

    rect(slide, 4.75, 3.3, 4.0, 3.35, C_SOFT_M, radius=True)
    label(slide, 4.95, 3.42, 3.6, 0.3, "对齐是一等公民", 14, True, C_DEPTH, PP_ALIGN.LEFT)
    bullets(slide, 4.95, 3.85, 3.6, 2.7, [
        "RGB / 深度 / 运动 meta 必须绑同一 timestamp",
        "允许 δt 时需外参与时间补偿（待拍板 H）",
        "对不齐 → TIMESTAMP_MISMATCH，不喂模型/AR",
        "深度 fd 谁 close、超时未释放策略（待拍板 K）",
    ], size=12, space=8)

    rect(slide, 8.95, 3.3, 3.85, 3.35, C_SOFT_B, radius=True)
    label(slide, 9.15, 3.42, 3.5, 0.3, "两个产品/技术选择", 14, True, C_CAMERA, PP_ALIGN.LEFT)
    bullets(slide, 9.15, 3.85, 3.5, 2.7, [
        "C：拍深度时是否短暂停预览？（画面闪 vs 深度质量）",
        "D：RGB 用预览帧还是高质量 Still？（时延 vs 画质）",
        "HAL 已确认：可单次算深度并控制停流；运动状态可入 meta",
    ], size=12, space=8)

    # ---------------- 7 接口清单 ----------------
    slide = blank(prs)
    title_bar(slide, "接口清单（小艺 ↔ 相机 App）", "五组接口；命名可改，语义保留；应用不直接调 HDI", 7)

    groups = [
        ("能力协商", C_CAMERA, C_SOFT_B, [
            "QueryCameraCapability",
            "→ sizes / formats / fps",
            "→ 多 Output / motion meta",
            "→ 按需深度 / 可否 Pause",
        ]),
        ("预览会话", C_XIAOYI, C_SOFT_T, [
            "ProvideSurface（争议 A）",
            "StartPreviewForXiaoyi",
            "OnPreviewStarted / Stopped",
            "Pause / ResumePreview",
        ]),
        ("帧 + 运动 meta", C_XIAOYI, C_SOFT_T, [
            "OnPreviewFrame（或 Surface 隐式）",
            "OnPreviewMetadata（同 ts）",
            "内部：OnStableFrame(ts)",
            "约束：meta 缺失不判稳",
        ]),
        ("拍摄 / 深度", C_DEPTH, C_SOFT_M, [
            "CaptureAt(ts, rgb, depth, pause)",
            "OnCaptureResult(fd/handle, meta)",
            "OnCaptureFailed(code)",
            "CancelCapture",
        ]),
        ("生命周期 / 抢占", C_MUTED, C_CARD, [
            "OnXiaoyiTabShow / Hide",
            "OnHostCameraBusy",
            "ReleaseAll（双向）",
            "错误码统一枚举",
        ]),
    ]
    for i, (t, c, f, items) in enumerate(groups):
        x = 0.5 + i * 2.48
        rect(slide, x, 1.35, 2.3, 4.1, f, radius=True)
        chip(slide, x + 0.15, 1.5, 2.0, t, c, size=12)
        bullets(slide, x + 0.12, 2.0, 2.1, 3.4, ["· " + s for s in items], size=11, space=8)

    rect(slide, 0.5, 5.65, 12.3, 1.0, C_CARD, radius=True)
    add_text(slide.shapes.add_textbox(Inches(0.7), Inches(5.75), Inches(11.9), Inches(0.35)),
             "关键说明：即便「画面画在小艺 Tab 内」，只要 Session 仍在相机 App，预览会话这组接口仍必须保留（争议 F）。",
             size=12, bold=True, color=C_INK)
    add_text(slide.shapes.add_textbox(Inches(0.7), Inches(6.15), Inches(11.9), Inches(0.4)),
             "错误码建议：OK · NO_PERMISSION · CAMERA_IN_USE · SURFACE_INVALID · FORMAT_UNSUPPORTED · TIMEOUT · DEPTH_UNAVAILABLE · TIMESTAMP_MISMATCH · DEVICE_THERMAL",
             size=11, color=C_MUTED)

    # ---------------- 8 风险与应对 ----------------
    slide = blank(prs)
    title_bar(slide, "风险与应对", "最大风险不是 UEC 切 Tab 慢那一下，而是「流归属 + UEC 能力边界 + 实时负载」", 8)

    risks = [
        ("UEC 内起流 / 显示受限", "高", "官方能力表曾列 UEC 不支持 XComponent；显示链路可能不可用",
         "样机实测；备选：宿主画预览，小艺只吃分析流 + 叠 UI"),
        ("与主相机抢会话", "高", "小艺再开一套 Session 会打断主预览或失败",
         "单会话多输出 / Tab 级移交；进出 Tab 明确停启"),
        ("端侧 LLM 跟帧负载", "高", "满帧送模型 → 发热、掉帧、拖垮预览",
         "稳定帧门控 + 降频 + 异步队列 + 过期丢弃"),
        ("推荐迟到 / chips 乱弹", "中高", "检测+LLM 冷路径 1～3s，场景已切换",
         "场景稳定再推；结果带 ts；冷却、去重、置信度门槛"),
        ("UEC 切换体感", "中", "首次进 Tab 冷启 几百 ms～1s，闪白",
         "同色背景 + placeholder；进程保活策略评估"),
        ("生命周期 / 黑屏 / 泄漏", "中高", "Surface 销毁顺序、fd 未释放、后台未停流",
         "显隐/前后台统一停启；fd 所有权写进契约"),
    ]
    for i, (t, lvl, why, act) in enumerate(risks):
        col, row = divmod(i, 3)
        x = 0.5 + col * 6.2
        y = 1.35 + row * 1.8
        lc = C_RISK if lvl == "高" else C_WARN
        rect(slide, x, y, 6.0, 1.65, C_WHITE, line=lc, radius=True)
        chip(slide, x + 0.15, y + 0.15, 0.7, lvl, lc, size=11)
        add_text(slide.shapes.add_textbox(Inches(x + 0.95), Inches(y + 0.12), Inches(4.9), Inches(0.35)),
                 t, size=14, bold=True, color=C_INK)
        add_text(slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 0.55), Inches(5.7), Inches(0.5)),
                 "风险：" + why, size=11, color=C_MUTED)
        add_text(slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 1.05), Inches(5.7), Inches(0.5)),
                 "应对：" + act, size=11, bold=True, color=C_PRIMARY)

    # ---------------- 9 待评审决策点 ----------------
    slide = blank(prs)
    title_bar(slide, "待评审决策点", "建议按顺序拍板：会话主人 → Surface/显示 → 格式/meta → 分发/门控 → 拍摄路径 → 二级跳转", 9)

    headers = ["ID", "议题", "选项", "建议 / 影响"]
    widths = [1.0, 2.5, 4.5, 4.2]
    x0 = 0.5
    rect(slide, x0, 1.3, sum(widths), 0.45, C_DARK)
    xx = x0
    for i, h in enumerate(headers):
        add_text(slide.shapes.add_textbox(Inches(xx), Inches(1.36), Inches(widths[i]), Inches(0.35)),
                 h, 12, True, C_WHITE, PP_ALIGN.CENTER)
        xx += widths[i]
    rows = [
        ["F/M", "会话主人 & 主预览策略", "相机 App 握机（小艺消费）vs 小艺自 openCamera", "建议相机握机；进 Tab 停主预览或双 Output"],
        ["A/G", "Surface 归属 & UEC 显示", "小艺建 vs 相机建；UEC 能否 XComponent", "先实测 G；不可用则宿主显示"],
        ["J/I", "格式 & 运动 meta", "RGB vs YUV；meta 字段集与每帧保障", "写死 pixelFormat/stride/旋转；meta 同 ts"],
        ["B/L", "三路分发 & 门控参数", "多 Output vs 单路 fork；阈值/K 帧/M ms", "先 B2 跑通，能力允许升 B1"],
        ["C/D/H/K", "拍摄路径", "停流否；预览帧 vs Still；δt 补偿；fd 所有权", "允许短暂停；对齐失败不喂模型"],
        ["E", "跳第二个相机 UEC", "宿主切换 vs UEC 内嵌套", "宿主切换 + 先停当前流"],
    ]
    for ri, row in enumerate(rows):
        y = 1.8 + ri * 0.78
        bg = C_SOFT if ri % 2 == 0 else C_WHITE
        rect(slide, x0, y, sum(widths), 0.74, bg)
        xx = x0
        for ci, cell in enumerate(row):
            add_text(slide.shapes.add_textbox(Inches(xx + 0.08), Inches(y + 0.12), Inches(widths[ci] - 0.14), Inches(0.55)),
                     cell, 11, ci in (0, 1), C_PRIMARY if ci == 0 else (C_INK if ci == 1 else C_MUTED),
                     PP_ALIGN.CENTER if ci == 0 else PP_ALIGN.LEFT)
            xx += widths[ci]
    add_text(slide.shapes.add_textbox(Inches(0.5), Inches(6.55), Inches(12.2), Inches(0.35)),
             "另需产品/合规确认 N：预览与深度是否落盘、端侧模型是否出域、权限告知。",
             size=11, color=C_WARN, bold=True)

    # ---------------- 10 验证计划 ----------------
    slide = blank(prs)
    title_bar(slide, "推进与验证计划", "先用样机验证两道硬门，再细化规则与交互", 10)

    phases = [
        ("阶段 1", "技术预研（硬门）", [
            "UEC 进程能否稳定拿到并显示预览",
            "宿主握机 + 小艺 Output 共存",
            "运动 meta 每帧上传与 ts 对齐",
        ], C_RISK, C_SOFT_R),
        ("阶段 2", "闭环打通", [
            "稳定帧门控 → 感知 → 端侧模型",
            "chips 弹出与点击执行",
            "端到端时延 / 发热基线",
        ], C_XIAOYI, C_SOFT_T),
        ("阶段 3", "深度与拍摄", [
            "CaptureAt → RGB + 深度 fd 回传",
            "停流策略与对齐校验",
            "AR 建模接入",
        ], C_DEPTH, C_SOFT_M),
        ("阶段 4", "体验打磨", [
            "UEC 冷启闪白消减",
            "chips 冷却/去重/阈值调优",
            "抢占、后台、异常恢复",
        ], C_CAMERA, C_SOFT_B),
    ]
    for i, (n, t, items, c, f) in enumerate(phases):
        x = 0.5 + i * 3.1
        rect(slide, x, 1.35, 2.9, 3.9, f, radius=True)
        chip(slide, x + 0.2, 1.55, 1.2, n, c, size=12)
        add_text(slide.shapes.add_textbox(Inches(x + 0.2), Inches(2.0), Inches(2.6), Inches(0.4)),
                 t, size=15, bold=True, color=C_INK)
        bullets(slide, x + 0.2, 2.5, 2.6, 2.6, ["· " + s for s in items], size=12, space=8)
        if i < 3:
            arrow_right(slide, x + 2.9, 3.2, 0.2, 0.18, C_LINE)

    rect(slide, 0.5, 5.45, 12.3, 1.2, C_CARD, radius=True)
    label(slide, 0.7, 5.55, 5, 0.3, "阶段 1 通过标准（Go / No-Go）", 13, True, C_PRIMARY, PP_ALIGN.LEFT)
    add_text(slide.shapes.add_textbox(Inches(0.7), Inches(5.9), Inches(11.9), Inches(0.7)),
             "① 小艺 Tab 内连续预览 ≥ 30 min 无黑屏/崩溃；② 进出 Tab 主预览可恢复；③ meta 与帧 ts 对齐率接近 100%；"
             "若 ① 失败则切换到「宿主显示 + 小艺分析」架构，其余设计不变。",
             size=12, color=C_INK)

    # ---------------- 11 结论 ----------------
    slide = blank(prs)
    title_bar(slide, "结论与请求", "方案可行；请评审拍板会话归属、显示位置与拍摄路径三项", 11)

    concl = [
        ("架构", "相机 App 握相机 → 框架 → HDI → HAL；小艺 UEC 消费流、做感知与推荐；不直连 HAL/HDI。", C_CAMERA, C_SOFT_B),
        ("门控", "稳定帧门控独立成模块，挂 Tab 业务层；感知/模型/AR/深度都订同一事件。", C_XIAOYI, C_SOFT_T),
        ("拍摄", "点击拍摄 = 按 timestamp 触发一次带深度的 Capture；RGB/深度/meta 同 ts 对齐。", C_DEPTH, C_SOFT_M),
    ]
    for i, (t, d, c, f) in enumerate(concl):
        y = 1.35 + i * 1.15
        rect(slide, 0.5, y, 12.3, 1.0, f, radius=True)
        chip(slide, 0.7, y + 0.33, 1.1, t, c, size=12)
        add_text(slide.shapes.add_textbox(Inches(2.0), Inches(y + 0.25), Inches(10.6), Inches(0.6)),
                 d, size=14, color=C_INK)

    rect(slide, 0.5, 4.95, 12.3, 1.75, C_DARK, radius=True)
    add_text(slide.shapes.add_textbox(Inches(0.9), Inches(5.1), Inches(11.5), Inches(0.4)),
             "请评审决策", 14, True, C_PRIMARY)
    tb = slide.shapes.add_textbox(Inches(0.9), Inches(5.5), Inches(11.5), Inches(1.15))
    tf = add_text(tb, "1. 同意「相机握机、小艺消费」为基线架构，并授权与相机/HAL 团队对齐接口契约", 13, False, C_WHITE)
    add_para(tf, "2. 同意先做阶段 1 样机预研（UEC 显示 + 会话共存 + meta 对齐）作为 Go/No-Go 门", 13, color=C_WHITE, space_before=6)
    add_para(tf, "3. 明确拍摄路径偏好：允许短暂停流取深度 / RGB 用预览帧还是 Still", 13, color=C_WHITE, space_before=6)

    out_paths = [
        "/workspace/artifacts/小艺CameraTab_UEC感知方案_评审.pptx",
        "/opt/cursor/artifacts/小艺CameraTab_UEC感知方案_评审.pptx",
    ]
    import os
    for path in out_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        prs.save(path)
        print("saved", path)
    print("slides", len(prs.slides))


if __name__ == "__main__":
    build()

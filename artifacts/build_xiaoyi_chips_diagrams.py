"""Render architecture diagrams for the Xiaoyi vision-endpoint chips scheme.

Outputs PNGs to docs/diagrams/ (repo) and /opt/cursor/artifacts/chips/ (preview).
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

plt.rcParams["font.family"] = "WenQuanYi Micro Hei"

ACCENT = "#4F46E5"
CAM = "#2563EB"
XY = "#059669"
CLOUD = "#D97706"
RISK = "#E11D48"
INK = "#1F2937"
MUTED = "#6B7280"
LINE = "#9CA3AF"
PANEL = "#F3F4F6"

REPO_OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "diagrams")
PREVIEW_OUT = "/opt/cursor/artifacts/chips"


def canvas(w=16, h=9):
    fig, ax = plt.subplots(figsize=(w, h), dpi=160)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def node(ax, x, y, w, h, title, sub=None, color=ACCENT, fill="white", fs=12, lw=1.6, ls="-"):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0,rounding_size=0.12",
            fc=fill, ec=color, lw=lw, ls=ls,
        )
    )
    cy = y + h / 2 + (0.16 if sub else 0)
    ax.text(x + w / 2, cy, title, ha="center", va="center", fontsize=fs, color=INK, weight="bold")
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.2, sub, ha="center", va="center", fontsize=fs - 3, color=MUTED)


def panel(ax, x, y, w, h, label, color, label_right=False):
    ax.add_patch(
        FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.18", fc=PANEL, ec=color, lw=1.2, ls=(0, (4, 3)))
    )
    lx, ha = (x + w - 0.2, "right") if label_right else (x + 0.2, "left")
    ax.text(lx, y + h - 0.28, label, ha=ha, va="center", fontsize=11, color=color, weight="bold")


def arrow(ax, p0, p1, color=LINE, label=None, ls="-", lw=1.5, rad=0.0, lx=0, ly=0.16, fs=9.5):
    ax.add_patch(
        FancyArrowPatch(
            p0, p1, arrowstyle="-|>", mutation_scale=14, color=color, lw=lw, ls=ls,
            connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2,
        )
    )
    if label:
        mx, my = (p0[0] + p1[0]) / 2 + lx, (p0[1] + p1[1]) / 2 + ly
        ax.text(mx, my, label, ha="center", va="center", fontsize=fs, color=INK,
                bbox=dict(fc="white", ec="none", pad=1.5))


def title(ax, text, sub=None, w=16, h=9):
    ax.text(0.4, h - 0.45, text, fontsize=18, weight="bold", color=INK, va="center")
    if sub:
        ax.text(0.4, h - 0.9, sub, fontsize=11, color=MUTED, va="center")


def save(fig, name):
    for d in (REPO_OUT, PREVIEW_OUT):
        os.makedirs(d, exist_ok=True)
        fig.savefig(os.path.join(d, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- 1 总览
def overview():
    fig, ax = canvas()
    title(ax, "推荐 chips · 三层拆开看", "起流决定图从哪来；识别决定谁算；出 chip 的规则两条方案共用")

    cols = [
        (0.5, "① 起流", CAM, "两条方案不同，对齐中"),
        (5.75, "② 识别", XY, "稳定帧谁判、模型谁跑"),
        (11.0, "③ 出 chip", ACCENT, "同一套规则"),
    ]
    for x, lab, c, sub in cols:
        panel(ax, x, 0.6, 4.5, 7.1, lab, c)
        ax.text(x + 0.2, 7.05, sub, fontsize=10, color=MUTED)

    # column 1
    node(ax, 0.8, 4.6, 3.9, 1.5, "方案 1 · 录像流", "HAL 对外三路 + 内部一路\n上云 / 显示 / 算法", CAM)
    node(ax, 0.8, 2.2, 3.9, 1.5, "方案 2 · 拍照流 + ARmode", "对外两路：AREngine / 显示\n上云靠 fork 编码", RISK)
    ax.text(2.75, 1.6, "HAL 未接纳", ha="center", fontsize=10, color=RISK, weight="bold")
    ax.text(2.75, 1.0, "差别：稳定帧谁判、HAL 结果有无、能否锚定", ha="center", fontsize=9.5, color=MUTED)

    # column 2
    node(ax, 6.05, 5.5, 3.9, 1.1, "稳定帧", "方案 1 HAL 事件 · 方案 2 视觉端传感器", XY)
    node(ax, 6.05, 3.95, 3.9, 1.1, "码 / 短文本", "二维码解码 · OCR 文本规则", XY)
    node(ax, 6.05, 2.5, 3.9, 1.1, "结构化版式", "HAL 1B · 视觉端 3B", XY)
    node(ax, 6.05, 1.05, 3.9, 1.1, "画面 + 联网", "定类别 · 云模型 · 在线搜索", XY)
    arrow(ax, (8.0, 5.5), (8.0, 5.05), XY)
    arrow(ax, (8.0, 3.95), (8.0, 3.6), LINE)
    arrow(ax, (8.0, 2.5), (8.0, 2.15), LINE)

    # column 3
    node(ax, 11.3, 5.3, 3.9, 1.3, "规则收口", "多类同时命中只收一次\n可执行在前，问答在后", ACCENT)
    node(ax, 11.3, 3.35, 3.9, 1.3, "0～N 颗 chips", "17 类内容 → 18 颗推荐", ACCENT)
    node(ax, 11.3, 1.4, 3.9, 1.3, "用户点击执行", "连 Wifi / 打电话 / 导航 / 翻译…", ACCENT)
    arrow(ax, (13.25, 5.3), (13.25, 4.65), ACCENT)
    arrow(ax, (13.25, 3.35), (13.25, 2.7), ACCENT)

    # cross column arrows
    arrow(ax, (4.7, 5.35), (6.05, 6.2), CAM, "图 + 稳定帧事件", rad=-0.1, lx=-0.45, ly=0.45)
    arrow(ax, (4.7, 2.95), (6.05, 5.75), RISK, "只有图", rad=-0.1, ls="--", lx=-0.45, ly=-0.1)
    arrow(ax, (9.95, 4.5), (11.3, 5.9), XY, "识别结果汇总", rad=-0.15, lx=-0.35, ly=0.3)
    arrow(ax, (9.95, 3.05), (11.3, 5.9), XY, rad=-0.3)
    arrow(ax, (9.95, 1.6), (11.3, 5.9), CLOUD, "云侧结果", rad=-0.4, lx=0.4, ly=-0.4)
    save(fig, "chips_overview.png")


# ---------------------------------------------------------------- 2 方案 1
def scheme1():
    fig, ax = canvas()
    title(ax, "方案 1 · 视觉端起录像流", "HAL 对外三路；另一路只在 HAL 内部跑模型，不占对外名额")

    panel(ax, 0.4, 0.5, 6.2, 7.3, "Camera HAL", CAM)
    panel(ax, 7.3, 3.6, 5.0, 4.2, "小艺视觉端", XY, label_right=True)
    panel(ax, 12.7, 3.6, 2.9, 4.2, "云侧", CLOUD)
    panel(ax, 7.3, 0.5, 8.3, 2.6, "出 chip（同一套规则）", ACCENT)

    node(ax, 0.7, 3.3, 1.7, 2.0, "Sensor\nISP", color=CAM)
    node(ax, 3.2, 6.1, 3.1, 0.9, "VideoOutput", "linear · 连续", CAM)
    node(ax, 3.2, 4.8, 3.1, 0.9, "预览 · 渲染", color=CAM)
    node(ax, 3.2, 3.5, 3.1, 0.9, "预览 · 算法", "按稳定帧事件降频出图", CAM)
    node(ax, 3.2, 1.0, 3.1, 1.9, "HAL 内部流", "二维码小模型 · 1B 内容分析\nCPU 跟踪 · 稳定帧判定", CAM, fill="#EFF6FF")

    for y in (6.55, 5.25, 3.95, 1.95):
        arrow(ax, (2.4, 4.3), (3.2, y), CAM, rad=-0.05)

    node(ax, 7.6, 6.3, 2.0, 0.9, "端侧显示", color=XY)
    node(ax, 10.0, 6.3, 2.0, 0.9, "编码上云", "连续 · linear", XY)
    node(ax, 7.6, 4.0, 4.4, 1.6, "视觉端模型", "HAL 没覆盖的类别 · 3B 问答\n接收 HAL 回传：码内容 / 类别 / 跟踪框", XY)

    node(ax, 12.95, 6.1, 2.4, 1.0, "云模型", "内容推荐", CLOUD)
    node(ax, 12.95, 4.4, 2.4, 1.0, "在线搜索", "知识类卡片", CLOUD)

    arrow(ax, (6.3, 6.7), (10.3, 7.2), CAM, "连续流", rad=-0.3, ly=0.55, lx=0.6)
    arrow(ax, (6.3, 5.25), (7.6, 6.6), CAM, rad=-0.1)
    arrow(ax, (6.3, 3.95), (7.6, 4.6), CAM, "稳定帧出图", ly=-0.3)
    arrow(ax, (6.3, 2.75), (7.6, 4.1), CAM, "码内容 / 类别 / 框", ls="--", lx=-0.9, ly=-0.35)
    arrow(ax, (12.0, 5.1), (12.95, 6.4), XY, "上报稳定帧", rad=-0.2, lx=-0.2, ly=0.25)
    arrow(ax, (12.0, 4.6), (12.95, 4.9), XY)
    arrow(ax, (9.8, 4.0), (9.8, 2.4), XY)
    arrow(ax, (14.15, 4.4), (14.15, 2.4), CLOUD, "推荐 / 卡片", ly=0.0)

    node(ax, 7.6, 1.3, 2.6, 1.1, "规则收口", "视觉端或云预定义", ACCENT)
    node(ax, 10.6, 1.3, 2.3, 1.1, "chips", "用户点击执行", ACCENT)
    node(ax, 13.2, 1.3, 2.2, 1.1, "锚在物体上", "HAL 跟踪框更新", ACCENT)
    arrow(ax, (10.2, 1.85), (10.6, 1.85), ACCENT)
    arrow(ax, (12.9, 1.85), (13.2, 1.85), ACCENT)
    arrow(ax, (14.3, 1.3), (5.0, 1.0), ACCENT, "下发 帧号 + 归一化框", rad=-0.12, ls="--", ly=-0.05)
    save(fig, "chips_scheme1_video.png")


# ---------------------------------------------------------------- 3 方案 2
def scheme2():
    fig, ax = canvas()
    title(ax, "方案 2 · 视觉端起拍照流（ARmode）　HAL 未接纳", "对外只有两路预览；上云和端模都从视觉端手里那一路 buffer 上做")

    panel(ax, 0.4, 0.5, 5.6, 7.3, "Camera HAL（不参与分析）", LINE)
    panel(ax, 6.7, 2.9, 5.5, 4.9, "小艺视觉端", XY)
    panel(ax, 12.7, 2.9, 2.9, 4.9, "云侧", CLOUD)
    panel(ax, 6.7, 0.5, 8.9, 2.0, "出 chip（同一套规则）", ACCENT)

    node(ax, 0.7, 3.5, 1.7, 2.0, "Sensor\nISP", color=CAM)
    node(ax, 3.0, 5.8, 2.7, 1.0, "预览 → AREngine", "ARmode 跟踪流", CAM)
    node(ax, 3.0, 4.0, 2.7, 1.0, "预览 → 显示", "消费者须是视觉端", CAM)
    node(ax, 3.0, 1.3, 2.7, 1.6, "第三路 / 内部模型", "拍照流出不了\n二维码 · 1B · 跟踪都没有", RISK, fill="#FFF1F2", ls="--")
    ax.text(3.2, 2.65, "✕", fontsize=15, color=RISK, weight="bold", ha="center", va="center")
    arrow(ax, (2.4, 4.5), (3.0, 6.3), CAM, rad=-0.1)
    arrow(ax, (2.4, 4.5), (3.0, 4.5), CAM)

    node(ax, 7.0, 6.1, 2.3, 1.1, "AREngine", "空间跟踪（如需要）", MUTED)
    node(ax, 7.0, 4.2, 2.3, 1.2, "持有 buffer", "归还前做完下面两件事", XY, fill="#ECFDF5")
    node(ax, 9.7, 5.2, 2.2, 0.9, "端侧显示", color=XY)
    node(ax, 9.7, 4.0, 2.2, 0.9, "编码上云", "linear，不能 HEBC", XY)
    node(ax, 9.7, 2.95, 2.2, 0.9, "送端模 3B", "同一路，不是第四路", XY)
    node(ax, 7.0, 3.1, 2.3, 0.9, "稳定帧", "视觉端看传感器", XY)

    arrow(ax, (5.7, 6.3), (7.0, 6.65), CAM)
    arrow(ax, (5.7, 4.5), (7.0, 4.8), CAM)
    arrow(ax, (9.3, 5.0), (9.7, 5.65), XY, rad=-0.15)
    arrow(ax, (9.3, 4.7), (9.7, 4.45), XY)
    arrow(ax, (9.3, 4.4), (9.7, 3.4), XY, rad=0.15)
    arrow(ax, (8.15, 4.2), (8.15, 4.0), XY)

    node(ax, 12.95, 5.6, 2.4, 1.0, "云模型", "内容推荐", CLOUD)
    node(ax, 12.95, 3.9, 2.4, 1.0, "在线搜索", "知识类卡片", CLOUD)
    arrow(ax, (11.9, 4.45), (12.95, 6.1), CLOUD, "连续流 + 稳定帧", rad=-0.2, lx=0.55, ly=0.0)
    arrow(ax, (11.9, 4.3), (12.95, 4.4), CLOUD)

    node(ax, 7.0, 0.8, 2.6, 1.1, "缺口", "二维码解码 · 锚在物体上", RISK, fill="#FFF1F2")
    node(ax, 10.0, 0.8, 2.6, 1.1, "规则收口", color=ACCENT)
    node(ax, 12.9, 0.8, 2.5, 1.1, "chips", "问答类 · 文本规则类", ACCENT)
    arrow(ax, (10.8, 2.95), (11.1, 1.9), XY)
    arrow(ax, (14.15, 3.9), (12.1, 1.9), CLOUD)
    arrow(ax, (12.6, 1.35), (12.9, 1.35), ACCENT)
    save(fig, "chips_scheme2_photo_armode.png")


# ---------------------------------------------------------------- 4 内容 → chip
def pipeline():
    fig, ax = canvas(16, 9.5)
    title(ax, "稳定帧之后 · 内容怎么变成 chip", "三条识别线按内容分工，可同时命中；结果汇总后规则只收一次", h=9.5)

    node(ax, 0.4, 3.9, 1.9, 1.4, "稳定的一帧", "方案 1 HAL 事件\n方案 2 传感器", ACCENT)

    lanes = [
        (6.0, "码 / 短文本", XY,
         "二维码（先解码）· 商家 Wifi · 网址\n邮箱 · 电话 · 航班号",
         "连接 Wifi · 打开网址 · 添加到联系人\n识别二维码 · 打开邮箱 · 打电话 · 打开航班查询",
         "字符串 + 规则\n方案 1 HAL 小模型解码；方案 2 无专用解码"),
        (3.5, "结构化版式", CAM,
         "外文 · 题目 · 卡证 · 表格\n联系人 · 地址 · 日程",
         "翻译 · 生成 AI 菜单 · 向店员展示点餐 · 解题\n记录卡证信息 · 表格提取 · 导航 · 添加到日历、闹钟",
         "方案 1 HAL 1B；方案 2 视觉端 3B + 云"),
        (1.0, "画面 + 联网", CLOUD,
         "商品 · 店招 · 动植物 · 景点建筑",
         "购同款 · 商品使用相关问题 · 店铺评分、优惠券\n动植物相关问题 · 景点介绍",
         "定类别后由云模型推荐、在线搜索出知识卡"),
    ]
    for y, lab, c, content, chips, how in lanes:
        node(ax, 3.1, y, 3.6, 2.0, lab, content, c)
        node(ax, 7.4, y, 5.2, 2.0, "chips", chips, c, fs=11)
        ax.text(4.9, y - 0.25, how, ha="center", va="center", fontsize=8.5, color=MUTED)
        arrow(ax, (2.3, 4.6), (3.1, y + 1.0), ACCENT, rad=-0.1 if y > 4 else (0.1 if y < 3 else 0))
        arrow(ax, (6.7, y + 1.0), (7.4, y + 1.0), c)
        arrow(ax, (12.6, y + 1.0), (13.3, 4.6), ACCENT, rad=0.1 if y > 4 else (-0.1 if y < 3 else 0))

    node(ax, 13.3, 3.6, 2.3, 2.0, "规则收口", "一帧多类只收一次\n可执行在前，问答在后\n同一次对准不重复", ACCENT, fill="#EEF2FF")
    node(ax, 13.3, 1.0, 2.3, 1.2, "用户点击执行", color=ACCENT)
    arrow(ax, (14.45, 3.6), (14.45, 2.2), ACCENT)
    node(ax, 13.3, 6.6, 2.3, 1.2, "锚在物体上", "仅方案 1 · HAL 跟踪", CAM, ls="--")
    arrow(ax, (14.45, 5.6), (14.45, 6.6), CAM, ls="--")

    ax.text(0.4, 0.5, "同一帧可以同时是店招、外文和电话。各模型不要各自弹 chip，汇总到规则再决定出哪几颗。",
            fontsize=10, color=MUTED)
    save(fig, "chips_pipeline.png")


if __name__ == "__main__":
    overview()
    scheme1()
    scheme2()
    pipeline()
    print("done", REPO_OUT)

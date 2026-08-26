#!/usr/bin/env python3
"""Generate the editable black-and-white patent system architecture SVG."""

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent / "assets"
SVG = OUT / "patent-system-overall-architecture.svg"
FONT = "WenQuanYi Micro Hei, Microsoft YaHei, PingFang SC, sans-serif"


def text(x, y, value, cls="body", anchor="middle"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{escape(value)}</text>'


def box(x, y, w, h, title, lines=(), cls="box"):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="{cls}"/>']
    out.append(text(x + w / 2, y + 32, title, "module"))
    for i, line in enumerate(lines):
        out.append(text(x + w / 2, y + 62 + i * 25, line, "body"))
    return out


def store(x, y, w, h, title, lines=()):
    out = [
        f'<path d="M{x},{y+12} C{x},{y-4} {x+w},{y-4} {x+w},{y+12} '
        f'L{x+w},{y+h-12} C{x+w},{y+h+4} {x},{y+h+4} {x},{y+h-12} Z" class="box"/>',
        f'<ellipse cx="{x+w/2}" cy="{y+12}" rx="{w/2}" ry="12" class="box"/>',
    ]
    out.append(text(x + w / 2, y + 43, title, "module"))
    for i, line in enumerate(lines):
        out.append(text(x + w / 2, y + 70 + i * 23, line, "body"))
    return out


def arrow(path, label="", lx=None, ly=None, cls="arrow"):
    out = [f'<path d="{path}" class="{cls}"/>']
    if label and lx is not None and ly is not None:
        out.append(text(lx, ly, label, "label"))
    return out


def number(x, y, n):
    return [
        f'<circle cx="{x}" cy="{y}" r="13" class="number"/>',
        text(x, y + 5, str(n), "num"),
    ]


parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="850" viewBox="0 0 1400 850">',
    "<defs>",
    '<marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#000"/></marker>',
    f"""<style>
      .box{{fill:#fff;stroke:#000;stroke-width:2.1}}
      .runtime{{fill:#fff;stroke:#000;stroke-width:2.2;stroke-dasharray:11 7}}
      .pipeline{{fill:#fff;stroke:#000;stroke-width:2.5}}
      .arrow{{fill:none;stroke:#000;stroke-width:2.1;marker-end:url(#arrowhead)}}
      .return{{fill:none;stroke:#000;stroke-width:2.1;stroke-dasharray:8 6;marker-end:url(#arrowhead)}}
      .data{{fill:none;stroke:#000;stroke-width:1.9;stroke-dasharray:3 4;marker-end:url(#arrowhead)}}
      .title{{font:700 27px {FONT};fill:#000}}
      .subtitle{{font:14px {FONT};fill:#000}}
      .module{{font:700 18px {FONT};fill:#000}}
      .body{{font:14px {FONT};fill:#000}}
      .label{{font:700 13px {FONT};fill:#000}}
      .note{{font:14px {FONT};fill:#000}}
      .num{{font:700 14px Arial,sans-serif;fill:#000}}
      .number{{fill:#fff;stroke:#000;stroke-width:1.8}}
    </style>""",
    "</defs>",
    '<rect width="1400" height="850" fill="#fff"/>',
    text(700, 38, "\u56fe2  \u672c\u53d1\u660e\u7cfb\u7edf\u603b\u4f53\u67b6\u6784\u793a\u610f\u56fe", "title"),
    text(700, 65, "\u6a21\u578b\u53ea\u8868\u8fbe\u5f15\u7528\u610f\u56fe\uff1b\u8c03\u5ea6\u5c42\u5728\u5de5\u5177\u6267\u884c\u524d\u6c42\u503c\u3001\u8f6c\u6362\u3001\u6821\u9a8c\u5e76\u56de\u586b\u771f\u503c", "subtitle"),
]

# External terminal
parts += box(28, 130, 205, 125, "\u7528\u6237\u7ec8\u7aef", ("\u624b\u673a / \u7535\u89c6 / \u8f66\u673a", "\u7528\u6237\u8bf7\u6c42 + \u8bbe\u5907\u72b6\u6001"))

# Runtime boundary and label
parts.append('<rect x="275" y="88" width="870" height="650" rx="15" class="runtime"/>')
parts.append('<rect x="310" y="74" width="235" height="31" fill="#fff"/>')
parts.append(text(427, 96, "\u667a\u80fd\u4f53\u8fd0\u884c\u7cfb\u7edf", "module"))

# Top-level runtime modules
parts += box(315, 130, 220, 130, "\u4ea4\u4e92\u4e0e\u4e0a\u4e0b\u6587\u6a21\u5757", ("\u7ec4\u88c5\u5bf9\u8bdd / deviceInfo", "\u5de5\u5177\u7ed3\u679c\u53ef\u9009 mask"))
parts += box(600, 130, 205, 130, "\u5927\u8bed\u8a00\u6a21\u578b", ("\u7406\u89e3\u610f\u56fe", "\u8f93\u51fa\u542b ${\u2026} \u7684 tool call"))
parts += box(870, 130, 225, 130, "\u5de5\u5177\u8c03\u5ea6\u6a21\u5757", ("\u63a5\u6536\u5de5\u5177\u540d\u4e0e\u53c2\u6570", "\u7edf\u4e00\u8c03\u5ea6\u5165\u53e3"))

# Pre-call pipeline frame
parts.append('<rect x="330" y="315" width="750" height="175" rx="12" class="pipeline"/>')
parts.append('<rect x="365" y="301" width="245" height="31" fill="#fff"/>')
parts.append(text(487, 323, "\u8c03\u7528\u524d\u53c2\u6570\u5904\u7406\u6d41\u6c34\u7ebf", "module"))
parts += box(365, 355, 150, 95, "\u2460 \u5f15\u7528\u8bc6\u522b", ("\u626b\u63cf ${\u2026}", "\u5224\u522b\u5f15\u7528\u7c7b\u578b"))
parts += box(540, 355, 150, 95, "\u2461 \u5f15\u7528\u6c42\u503c", ("\u67e5\u8bb0\u5fc6/\u8bcd\u5178", "\u56de\u586b\u4e1a\u52a1\u771f\u503c"))
parts += box(715, 355, 150, 95, "\u2462 \u7b56\u7565\u8f6c\u6362", ("\u5217\u8868 map / \u5bf9\u8c61\u5c01\u88c5", "\u7c7b\u578b/\u5b57\u6bb5\u8f6c\u6362"))
parts += box(890, 355, 155, 95, "\u2463 \u6821\u9a8c/\u77ed\u8def", ("\u6821\u9a8c schema", "\u5931\u8d25\u7981\u6b62\u900f\u4f20"))

# Data stores
parts += store(320, 565, 220, 120, "\u5de5\u4f5c\u8bb0\u5fc6", ("\u5de5\u5177\u7ed3\u679c\u96c6", "resultId \u2192 \u5b57\u6bb5\u771f\u503c"))
parts += store(605, 565, 220, 120, "\u8bed\u4e49\u8bcd\u5178", ("\u540c\u4e49\u8bcd/\u522b\u540d\u8868", "\u5b9e\u4f53\u5c5e\u6027\u6620\u5c04\u8868"))
parts += store(890, 565, 205, 120, "\u53c2\u6570\u7b56\u7565\u4ed3", ("\u901a\u7528\u89c4\u5219 + \u5de5\u5177\u8986\u76d6", "\u683c\u5f0f\u8f6c\u6362 policy"))

# External tool execution
parts += box(1200, 270, 175, 170, "\u5de5\u5177\u6267\u884c\u6a21\u5757", ("\u7aef\u4fa7\u5de5\u5177", "\u4e91\u7aef API / \u7b2c\u4e09\u65b9\u5de5\u5177", "\u4ec5\u63a5\u6536\u6700\u7ec8\u771f\u503c"))

# Main arrows
parts += arrow("M233 192 H315", "\u7528\u6237\u610f\u56fe / \u8bbe\u5907\u4e0a\u4e0b\u6587", 274, 177)
parts += number(274, 211, 1)
parts += arrow("M535 195 H600", "\u6a21\u578b\u4e0a\u4e0b\u6587", 568, 178)
parts += number(568, 211, 2)
parts += arrow("M805 195 H870", "\u542b\u5f15\u7528\u7684\u5de5\u5177\u8c03\u7528", 838, 178)
parts += number(838, 211, 3)
parts += arrow("M982 260 V315", "\u8fdb\u5165 pre-call \u6d41\u6c34\u7ebf", 1040, 294)
parts += number(982, 287, 4)

# Pipeline arrows
parts += arrow("M515 402 H540")
parts += arrow("M690 402 H715")
parts += arrow("M865 402 H890")

# Data-source arrows
parts += arrow("M430 565 V510 H615 V450", "\u7ed3\u679c\u5f15\u7528\u6570\u636e\u6e90", 500, 535, "data")
parts += arrow("M715 565 V510 H645 V450", "\u8bed\u4e49\u5f15\u7528\u6570\u636e\u6e90", 725, 535, "data")
parts += arrow("M992 565 V450", "\u8f6c\u6362/\u6821\u9a8c\u89c4\u5219", 1060, 525, "data")

# Final invoke
parts += arrow("M1045 402 H1200", "\u6700\u7ec8\u771f\u503c\u53c2\u6570", 1122, 385)
parts += number(1122, 418, 5)

# Result return and storage
parts += arrow("M1287 440 V730 H430 V685", "\u5de5\u5177\u7ed3\u679c\u9ed8\u8ba4\u5199\u5165\u5de5\u4f5c\u8bb0\u5fc6", 875, 757, "return")
parts += number(1165, 730, 6)
parts += arrow("M430 565 V520 H425 V260", "\u7ed3\u679c/\u63a9\u7801\u540e\u4e0a\u4e0b\u6587\u56de\u6d41", 330, 520, "return")

# Failure branch
parts += arrow("M967 450 V520 H1165 V520", "\u5931\u8d25\uff1a\u8fd4\u56de\u660e\u786e\u9519\u8bef\uff0c\u4e0d\u8c03\u5de5\u5177", 1060, 545, "return")

# Bottom legend
parts.append('<rect x="35" y="782" width="1330" height="48" rx="7" class="box"/>')
parts.append(text(62, 812, "\u56fe\u4f8b\uff1a", "label", "start"))
parts.append(text(125, 812, "\u5b9e\u7ebf\u7bad\u5934=\u4e3b\u8c03\u7528\u6d41\uff1b\u77ed\u865a\u7ebf=\u6570\u636e/\u7b56\u7565\u8bfb\u53d6\uff1b\u957f\u865a\u7ebf=\u7ed3\u679c\u6216\u9519\u8bef\u56de\u6d41\uff1b\u5de5\u5177\u5b9e\u73b0\u65e0\u9700\u8bc6\u522b\u5f15\u7528\u534f\u8bae\u3002", "note", "start"))

parts.append("</svg>")
OUT.mkdir(parents=True, exist_ok=True)
SVG.write_text("\n".join(parts), encoding="utf-8")
print("Wrote", SVG)

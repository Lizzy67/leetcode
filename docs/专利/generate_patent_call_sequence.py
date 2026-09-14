#!/usr/bin/env python3
"""Generate a standard editable sequence diagram for the patent disclosure."""

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent / "assets"
SVG = OUT / "patent-system-call-sequence.svg"
FONT = "WenQuanYi Micro Hei, Microsoft YaHei, PingFang SC, sans-serif"


def txt(x, y, value, cls="body", anchor="middle"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{escape(value)}</text>'


def actor(x, title, subtitle=""):
    w = 180
    out = [f'<rect x="{x-w/2}" y="82" width="{w}" height="70" rx="7" class="box"/>']
    out.append(txt(x, 113, title, "actor"))
    if subtitle:
        out.append(txt(x, 137, subtitle, "small"))
    out.append(f'<path d="M{x} 152 V885" class="life"/>')
    return out


def arrow(x1, x2, y, label, ret=False):
    cls = "ret" if ret else "msg"
    out = [f'<path d="M{x1} {y} H{x2}" class="{cls}"/>']
    out.append(txt((x1+x2)/2, y-9, label, "label"))
    return out


def activation(x, y, h):
    return f'<rect x="{x-7}" y="{y}" width="14" height="{h}" class="act"/>'


parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="960" viewBox="0 0 1600 960">',
    "<defs>",
    '<marker id="a" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#000"/></marker>',
    '<marker id="open" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L9,3 L0,6" fill="none" stroke="#000" stroke-width="1.5"/></marker>',
    f"""<style>
      .box{{fill:#fff;stroke:#000;stroke-width:2}}
      .life{{fill:none;stroke:#000;stroke-width:1.6;stroke-dasharray:7 6}}
      .msg{{fill:none;stroke:#000;stroke-width:1.9;marker-end:url(#a)}}
      .ret{{fill:none;stroke:#000;stroke-width:1.7;stroke-dasharray:7 5;marker-end:url(#open)}}
      .act{{fill:#fff;stroke:#000;stroke-width:1.6}}
      .frame{{fill:#fff;stroke:#000;stroke-width:2}}
      .divider{{fill:none;stroke:#000;stroke-width:1.5;stroke-dasharray:6 5}}
      .title{{font:700 27px {FONT};fill:#000}}
      .subtitle{{font:14px {FONT};fill:#000}}
      .actor{{font:700 17px {FONT};fill:#000}}
      .body{{font:14px {FONT};fill:#000}}
      .small{{font:12px {FONT};fill:#000}}
      .label{{font:13px {FONT};fill:#000}}
      .frameLabel{{font:700 14px {FONT};fill:#000}}
    </style>""",
    "</defs>",
    '<rect width="1600" height="960" fill="#fff"/>',
    txt(800, 36, "\u56fe3  \u672c\u53d1\u660e\u5de5\u5177\u8c03\u7528\u53c2\u6570\u5f15\u7528\u89e3\u6790\u65f6\u5e8f\u56fe", "title"),
    txt(800, 62, "\u4e3b\u8def\u5f84\uff1a\u5f15\u7528\u8bc6\u522b\u4e0e\u6c42\u503c \u2192 \u53ef\u9009\u7b56\u7565\u8f6c\u6362 \u2192 \u6821\u9a8c\u56de\u586b \u2192 \u5de5\u5177\u6267\u884c \u2192 \u7ed3\u679c\u5165\u5e93", "subtitle"),
]

actors = [
    (90, "\u7528\u6237\u7ec8\u7aef", "\u624b\u673a/\u7535\u89c6/\u8f66\u673a"),
    (310, "\u4ea4\u4e92\u4e0e\u4e0a\u4e0b\u6587", "\u667a\u80fd\u4f53\u8fd0\u884c\u65f6"),
    (530, "\u5927\u8bed\u8a00\u6a21\u578b", "\u610f\u56fe\u4e0e\u5de5\u5177\u51b3\u7b56"),
    (770, "\u8c03\u5ea6/\u5f15\u7528\u62e6\u622a\u5668", "pre-call pipeline"),
    (1020, "\u53ef\u4fe1\u6570\u636e\u6e90", "\u5de5\u4f5c\u8bb0\u5fc6/\u8bed\u4e49\u8bcd\u5178"),
    (1240, "\u53c2\u6570\u7b56\u7565\u4ed3", "transform/validate policy"),
    (1480, "\u5de5\u5177\u6267\u884c\u6a21\u5757", "\u7aef\u4fa7/\u4e91\u7aef\u5de5\u5177"),
]
for x, title, subtitle in actors:
    parts += actor(x, title, subtitle)

# Activation bars
parts.append(activation(310, 182, 730))
parts.append(activation(530, 230, 135))
parts.append(activation(770, 330, 570))
parts.append(activation(1480, 655, 95))

# Main messages
parts += arrow(90, 310, 195, "\u2460 \u63d0\u4ea4\u7528\u6237\u610f\u56fe\u53ca\u53ef\u9009\u8bbe\u5907\u72b6\u6001")
parts += arrow(310, 530, 245, "\u2461 \u53d1\u9001\u4e0a\u4e0b\u6587\u3001Skill \u53ca\u5de5\u5177\u5b9a\u4e49")
parts += arrow(530, 310, 295, "\u2462 \u8fd4\u56de tool call\uff0c\u53c2\u6570\u4e2d\u542b ${\u2026} \u5f15\u7528", True)
parts += arrow(310, 770, 345, "\u2463 \u8fdb\u5165\u7edf\u4e00\u5de5\u5177\u8c03\u5ea6\u5165\u53e3")

# Ref resolution self/lookup
parts += arrow(770, 1020, 395, "\u2464 \u6309\u5f15\u7528\u7c7b\u578b\u67e5\u8be2\u7ed3\u679c\u5b57\u6bb5\u6216\u8bed\u4e49\u5b9e\u4f53\u5c5e\u6027")
parts += arrow(1020, 770, 445, "\u2465 \u8fd4\u56de\u552f\u4e00\u4e1a\u52a1\u771f\u503c", True)

# Policy transformation
parts += arrow(770, 1240, 495, "\u2466 \u67e5\u8be2\u5de5\u5177+\u53c2\u6570\u7ed1\u5b9a\u7684\u8f6c\u6362/\u6821\u9a8c\u7b56\u7565")
parts += arrow(1240, 770, 545, "\u2467 \u8fd4\u56de policy\uff08\u672a\u914d\u7f6e\u65f6\u53ef\u8df3\u8fc7\u8f6c\u6362\uff09", True)
parts.append(txt(770, 585, "\u2468 \u62e6\u622a\u5668\u5bf9\u5df2\u5c55\u5f00\u771f\u503c\u6267\u884c\u53ef\u9009\u683c\u5f0f\u8f6c\u6362\uff0c\u5e76\u6821\u9a8c\u6700\u7ec8 schema", "label"))

# Alt frame around success/failure
parts.append('<rect x="690" y="600" width="860" height="205" class="frame"/>')
parts.append('<path d="M690 633 H1550" class="divider"/>')
parts.append('<path d="M690 710 H1550" class="divider"/>')
parts.append('<path d="M690 600 H805 L825 616 L805 633 H690 Z" class="box"/>')
parts.append(txt(748, 622, "alt", "frameLabel"))
parts.append(txt(845, 624, "\u89e3\u6790\u3001\u8f6c\u6362\u53ca\u6821\u9a8c\u6210\u529f", "frameLabel", "start"))
parts += arrow(770, 1480, 665, "\u2469 \u56de\u586b\u6700\u7ec8\u771f\u503c\u53c2\u6570\u5e76\u8c03\u7528\u5de5\u5177")
parts += arrow(1480, 770, 735, "\u246a \u8fd4\u56de\u5de5\u5177\u7ed3\u679c", True)
parts.append(txt(720, 757, "\u89e3\u6790\u5931\u8d25\u3001\u6620\u5c04\u6b67\u4e49\u3001\u8f6c\u6362\u5931\u8d25\u6216 schema \u4e0d\u5408\u6cd5", "frameLabel", "start"))
parts += arrow(770, 310, 785, "\u246b \u77ed\u8def\uff1a\u8fd4\u56de\u660e\u786e\u9519\u8bef\uff0c\u7981\u6b62\u5f15\u7528\u5b57\u9762\u91cf\u6216\u534a\u6210\u54c1\u53c2\u6570\u900f\u4f20", True)

# Post-success result storage and model/user feedback
parts += arrow(770, 1020, 835, "\u246c \u6210\u529f\u7ed3\u679c\u9ed8\u8ba4\u5199\u5165\u5de5\u4f5c\u8bb0\u5fc6")
parts += arrow(770, 310, 870, "\u246d \u8fd4\u56de\u5de5\u5177\u7ed3\u679c\u6216\u7ed3\u6784\u5316\u9519\u8bef", True)
parts += arrow(310, 90, 905, "\u246e \u8fd4\u56de\u4e1a\u52a1\u7ed3\u679c\uff0c\u6216\u5f15\u5bfc\u7528\u6237/\u6a21\u578b\u6d88\u6b67\u91cd\u8bd5", True)

# Note
parts.append('<rect x="25" y="925" width="1550" height="25" fill="#fff"/>')
parts.append(txt(800, 945, "\u6ce8\uff1a\u865a\u7ebf\u7bad\u5934\u8868\u793a\u8fd4\u56de\u6d88\u606f\uff1b\u6210\u529f\u4e3b\u8def\u5f84\u4e2d\u5de5\u5177\u53ea\u63a5\u6536\u6700\u7ec8\u771f\u503c\uff0c\u5bf9\u5f15\u7528\u534f\u8bae\u53ca\u53c2\u6570\u8f6c\u6362\u8fc7\u7a0b\u65e0\u611f\u77e5\u3002", "small"))

parts.append("</svg>")
OUT.mkdir(parents=True, exist_ok=True)
SVG.write_text("\n".join(parts), encoding="utf-8")
print("Wrote", SVG)

#!/usr/bin/env python3
"""Generate black-and-white editable SVG figures for patent scenarios."""

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent / "assets"
FONT = "WenQuanYi Micro Hei, Microsoft YaHei, PingFang SC, sans-serif"


def base(title: str, subtitle: str = "") -> list[str]:
    return [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 1200 560">',
        "<defs>",
        '<marker id="a" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#000"/></marker>',
        f'<style>.box{{fill:#fff;stroke:#000;stroke-width:2}}.dash{{fill:#fff;stroke:#000;stroke-width:2;stroke-dasharray:8 6}}.arr{{fill:none;stroke:#000;stroke-width:2;marker-end:url(#a)}}.ret{{fill:none;stroke:#000;stroke-width:2;stroke-dasharray:7 5;marker-end:url(#a)}}.t{{font:700 25px {FONT};fill:#000}}.h{{font:700 18px {FONT};fill:#000}}.b{{font:15px {FONT};fill:#000}}.s{{font:13px {FONT};fill:#000}}</style>',
        "</defs>",
        '<rect width="1200" height="560" fill="#fff"/>',
        f'<text x="600" y="38" text-anchor="middle" class="t">{escape(title)}</text>',
        f'<text x="600" y="64" text-anchor="middle" class="s">{escape(subtitle)}</text>',
    ]


def box(x, y, w, h, title, lines=(), dashed=False):
    cls = "dash" if dashed else "box"
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="{cls}"/>']
    out.append(f'<text x="{x+w/2}" y="{y+32}" text-anchor="middle" class="h">{escape(title)}</text>')
    for i, line in enumerate(lines):
        out.append(f'<text x="{x+w/2}" y="{y+62+i*25}" text-anchor="middle" class="b">{escape(line)}</text>')
    return out


def arrow(x1, y1, x2, y2, label="", dashed=False):
    cls = "ret" if dashed else "arr"
    out = [f'<path d="M{x1} {y1} L{x2} {y2}" class="{cls}"/>']
    if label:
        out.append(f'<text x="{(x1+x2)/2}" y="{min(y1,y2)-10}" text-anchor="middle" class="s">{escape(label)}</text>')
    return out


def save(name: str, parts: list[str]):
    parts.append("</svg>")
    (OUT / name).write_text("\n".join(parts), encoding="utf-8")


def app_identifier():
    p = base(
        "\u56fe4  \u8bed\u4e49\u5b9e\u4f53\u5f15\u7528\u5728\u5e94\u7528\u6743\u9650\u63a7\u5236\u573a\u666f\u4e2d\u7684\u6d41\u7a0b",
        "\u6b63\u5e38\u8def\u5f84\u4e00\u6b21\u4e1a\u52a1\u8c03\u7528\uff1b\u771f\u5b9e\u5305\u540d\u7531\u8bcd\u5178\u67e5\u8868\u83b7\u5f97",
    )
    p += box(45, 125, 185, 115, "\u7528\u6237", ("\u7981\u6b62\u6296\u97f3\u4f7f\u7528", "\u9ea6\u514b\u98ce"))
    p += box(285, 125, 230, 115, "\u5927\u8bed\u8a00\u6a21\u578b", ("\u9009\u62e9\u6743\u9650\u5de5\u5177", "\u53ea\u8868\u8fbe\u5f15\u7528\u610f\u56fe"))
    p += box(570, 105, 250, 155, "\u5f15\u7528\u89e3\u6790\u62e6\u622a\u5668", ("\u8bc6\u522b\u8bed\u4e49\u4e09\u6bb5\u5f0f", "${app.\u6296\u97f3.bundleName}", "\u6267\u884c\u524d\u67e5\u8868"))
    p += box(875, 125, 270, 115, "\u6743\u9650\u5de5\u5177", ("bundleName=\u771f\u5b9e\u5305\u540d", "permission=\u9ea6\u514b\u98ce"))
    p += arrow(230, 182, 285, 182, "\u7528\u6237\u610f\u56fe")
    p += arrow(515, 182, 570, 182, "\u542b\u5f15\u7528\u7684\u5de5\u5177\u53c2\u6570")
    p += arrow(820, 182, 875, 182, "\u56de\u586b\u771f\u503c")
    p += box(355, 355, 205, 105, "\u540c\u4e49\u8bcd\u8868", ("douyin / Douyin", "\u2192 \u6296\u97f3"))
    p += box(640, 355, 270, 105, "\u5b9e\u4f53\u5c5e\u6027\u6620\u5c04\u8868", ("(app, \u6296\u97f3, bundleName)", "\u2192 com.ss.android..."))
    p += arrow(670, 260, 500, 355, "\u2460 \u522b\u540d\u5f52\u4e00")
    p += arrow(720, 355, 700, 260, "\u2461 \u5c5e\u6027\u6620\u5c04")
    p.append('<text x="600" y="525" text-anchor="middle" class="b">\u672a\u547d\u4e2d\u6216\u591a\u5019\u9009\uff1a\u77ed\u8def\uff0c\u53ef\u8f6c\u67e5\u8be2\u5df2\u5b89\u88c5\u5e94\u7528\u7684\u515c\u5e95\u8def\u5f84\uff1b\u7981\u6b62\u731c\u6d4b\u6216\u900f\u4f20\u5f15\u7528\u5b57\u9762\u91cf\u3002</text>')
    save("patent-scenario-app-identifier.svg", p)


def result_transfer():
    p = base(
        "\u56fe5  \u8de8\u5de5\u5177\u7ed3\u679c\u5f15\u7528\u4e0e\u9001\u6a21\u63a9\u7801\u6d41\u7a0b",
        "\u6a21\u578b\u4e0d\u9700\u8bfb\u53d6\u6216\u590d\u8ff0\u957f URI\uff0c\u6267\u884c\u524d\u4ece\u5de5\u4f5c\u8bb0\u5fc6\u56de\u586b",
    )
    p += box(50, 115, 190, 120, "\u5de5\u5177 A", ("\u4e0a\u4f20/\u751f\u6210\u6587\u4ef6", "\u8fd4\u56de\u957f fileUri"))
    p += box(305, 100, 245, 150, "\u5de5\u4f5c\u8bb0\u5fc6", ("\u9ed8\u8ba4\u5199\u5165\u5de5\u5177\u7ed3\u679c", "\u5206\u914d resultId", "\u4fdd\u5b58 resultId\u2192\u7ed3\u679c"))
    p += box(615, 115, 210, 120, "\u5927\u8bed\u8a00\u6a21\u578b", ("\u770b\u5230\u5f15\u7528\u800c\u975e URI", "\u539f\u6837\u5199\u5165\u4e0b\u6e38\u53c2\u6570"))
    p += box(890, 100, 255, 150, "\u8c03\u5ea6/\u5f15\u7528\u89e3\u6790", ("\u8bc6\u522b ${resultId.fileUri}", "\u67e5\u5de5\u4f5c\u8bb0\u5fc6", "\u56de\u586b\u771f\u5b9e URI"))
    p += arrow(240, 175, 305, 175, "\u2460 \u7ed3\u679c\u5165\u5e93")
    p += arrow(550, 175, 615, 175, "\u2461 \u9001\u6a21\u524d mask")
    p += arrow(825, 175, 890, 175, "\u2462 \u5de5\u5177 B \u5165\u53c2\u5f15\u7528")
    p += box(890, 365, 255, 110, "\u5de5\u5177 B", ("\u63a5\u6536\u771f\u5b9e fileUri", "\u5de5\u5177\u5b9e\u73b0\u96f6\u6539\u52a8"))
    p += arrow(1017, 250, 1017, 365, "\u2463 \u56de\u586b\u540e\u8c03\u7528")
    p += box(305, 365, 245, 110, "\u63a9\u7801\u540e\u7684\u4e0a\u4e0b\u6587", ("fileUri =", "${a1b2c3d4.fileUri}"))
    p += arrow(427, 250, 427, 365, "\u6240\u89c1\u5373\u6240\u586b", dashed=True)
    p.append('<text x="600" y="525" text-anchor="middle" class="b">\u6280\u672f\u6548\u679c\uff1a\u964d\u4f4e\u957f\u503c\u62c9\u56de\u4e0a\u4e0b\u6587\u53ca\u6a21\u578b\u6284\u5199\u5bfc\u81f4\u7684 token\u3001\u65f6\u5ef6\u548c\u622a\u65ad/\u6539\u5199\u98ce\u9669\u3002</text>')
    save("patent-scenario-result-transfer.svg", p)


def format_transform():
    p = base(
        "\u56fe6  \u5f15\u7528\u5c55\u5f00\u540e\u7684\u5165\u53c2\u7b56\u7565\u5316\u683c\u5f0f\u8f6c\u6362",
        "\u5148\u6c42\u503c\uff0c\u518d\u8f6c\u6362\uff0c\u6700\u540e\u6821\u9a8c\u5e76\u8c03\u7528\u4e0b\u6e38\u5de5\u5177",
    )
    p += box(40, 120, 235, 140, "\u6a21\u578b\u5de5\u5177\u8c03\u7528", ('images="${resultId.', 'merged_id_list}"', "\u4e0d\u751f\u6210\u957f\u5bf9\u8c61\u6570\u7ec4"))
    p += box(325, 120, 220, 140, "\u5f15\u7528\u6c42\u503c\u5355\u5143", ("\u67e5\u8be2\u5de5\u4f5c\u8bb0\u5fc6", "images=[563, 563, \u2026]"))
    p += box(595, 105, 260, 170, "\u53c2\u6570\u8f6c\u6362\u5355\u5143", ("\u8bfb\u53d6\u5de5\u5177+\u53c2\u6570 policy", "\u9010\u5143\u7d20 map", '\u5c01\u88c5 {"file_id": string(item)}'))
    p += box(905, 120, 250, 140, "\u53c2\u6570\u6821\u9a8c\u4e0e\u5de5\u5177 B", ("\u6821\u9a8c\u5bf9\u8c61\u5217\u8868 schema", "\u6210\u529f\u540e\u8c03\u7528", "\u5931\u8d25\u5219\u77ed\u8def"))
    p += arrow(275, 190, 325, 190, "\u2460 resolve")
    p += arrow(545, 190, 595, 190, "\u2461 transform")
    p += arrow(855, 190, 905, 190, "\u2462 validate/invoke")
    p += box(330, 365, 540, 105, "\u8f6c\u6362\u540e\u7684\u6700\u7ec8\u53c2\u6570", ('images=[{"file_id":"563"},', '{"file_id":"563"}, \u2026]'))
    p += arrow(725, 275, 650, 365, "\u8f93\u51fa\u6700\u7ec8\u7ed3\u6784")
    p.append('<text x="600" y="525" text-anchor="middle" class="b">\u6280\u672f\u6548\u679c\uff1a\u4e0a\u4e0b\u6e38 schema \u89e3\u8026\uff1b\u6a21\u578b\u65e0\u9700\u6539\u5199\u957f JSON\uff1b\u5de5\u5177 A/B \u7684\u63a5\u53e3\u4e0e\u5b9e\u73b0\u5747\u53ef\u4fdd\u6301\u4e0d\u53d8\u3002</text>')
    save("patent-scenario-format-transform.svg", p)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    app_identifier()
    result_transfer()
    format_transform()
    print("Generated 3 patent scenario SVG figures in", OUT)

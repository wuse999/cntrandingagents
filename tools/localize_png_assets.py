from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont


FONT_REGULAR = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

ROOT = Path(__file__).resolve().parents[1]
RAW_ASSETS = ROOT.parent / "raw" / "assets"
ASSETS = ROOT / "assets"


Color = tuple[int, int, int]
Box = tuple[int, int, int, int]

TEXT_DARK: Color = (18, 18, 18)
TEXT_MID: Color = (90, 90, 90)
TEXT_SOFT: Color = (78, 78, 78)
TEXT_ON_DARK: Color = (84, 84, 84)
GREEN: Color = (17, 193, 55)
RED: Color = (255, 70, 70)
PURPLE: Color = (127, 75, 255)
WHITE: Color = (255, 255, 255)
BLUE: Color = (83, 121, 255)
BLACK: Color = (0, 0, 0)


@dataclass
class EraseAction:
    box: Box
    radius: int = 18
    fill: Color | None = None
    sample_box: Box | None = None


@dataclass
class OutlineAction:
    box: Box
    outline: Color
    width: int = 1
    radius: int = 18
    fill: Color | None = None


@dataclass
class TextAction:
    box: Box
    text: str
    fill: Color
    font: str = FONT_REGULAR
    max_size: int = 48
    min_size: int = 18
    line_spacing: float = 1.16
    align: str = "left"
    valign: str = "top"


def sample_fill(image: Image.Image, box: Box) -> Color:
    crop = image.crop(box).convert("RGB")
    arr = np.array(crop).reshape(-1, 3)
    median = np.median(arr, axis=0)
    return tuple(int(v) for v in median)


def erase(draw: ImageDraw.ImageDraw, image: Image.Image, action: EraseAction) -> None:
    fill = action.fill if action.fill is not None else sample_fill(image, action.sample_box or action.box)
    draw.rounded_rectangle(action.box, radius=action.radius, fill=fill)


def outline(draw: ImageDraw.ImageDraw, action: OutlineAction) -> None:
    draw.rounded_rectangle(
        action.box,
        radius=action.radius,
        fill=action.fill,
        outline=action.outline,
        width=action.width,
    )


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    wrapped: list[str] = []
    for raw_line in text.splitlines() or [""]:
        if not raw_line:
            wrapped.append("")
            continue
        line = ""
        for ch in raw_line:
            candidate = line + ch
            bbox = draw.textbbox((0, 0), candidate, font=font)
            if bbox[2] - bbox[0] <= max_width or not line:
                line = candidate
            else:
                wrapped.append(line)
                line = ch
        if line:
            wrapped.append(line)
    return wrapped or [""]


def fit_font(
    draw: ImageDraw.ImageDraw,
    box: Box,
    text: str,
    font_path: str,
    max_size: int,
    min_size: int,
    line_spacing: float,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    x1, y1, x2, y2 = box
    max_width = x2 - x1
    max_height = y2 - y1
    best_font = ImageFont.truetype(font_path, min_size)
    best_lines = wrap_text(draw, text, best_font, max_width)
    best_step = int(min_size * line_spacing)

    for size in range(max_size, min_size - 1, -1):
        font = ImageFont.truetype(font_path, size)
        lines = wrap_text(draw, text, font, max_width)
        line_bbox = draw.textbbox((0, 0), "测试Ag", font=font)
        line_height = line_bbox[3] - line_bbox[1]
        step = int(line_height * line_spacing)
        total_height = line_height + max(0, len(lines) - 1) * step
        too_wide = any(draw.textbbox((0, 0), line, font=font)[2] > max_width for line in lines)
        if not too_wide and total_height <= max_height:
            return font, lines, step
        best_font = font
        best_lines = lines
        best_step = step

    return best_font, best_lines, best_step


def draw_text(draw: ImageDraw.ImageDraw, action: TextAction) -> None:
    x1, y1, x2, y2 = action.box
    font, lines, step = fit_font(
        draw,
        action.box,
        action.text,
        action.font,
        action.max_size,
        action.min_size,
        action.line_spacing,
    )
    line_bbox = draw.textbbox((0, 0), "测试Ag", font=font)
    line_height = line_bbox[3] - line_bbox[1]
    total_height = line_height + max(0, len(lines) - 1) * step

    if action.valign == "middle":
        y = y1 + (y2 - y1 - total_height) / 2
    elif action.valign == "bottom":
        y = y2 - total_height
    else:
        y = y1

    for line in lines:
        line_width = draw.textbbox((0, 0), line, font=font)[2]
        if action.align == "center":
            x = x1 + (x2 - x1 - line_width) / 2
        elif action.align == "right":
            x = x2 - line_width
        else:
            x = x1
        draw.text((x, y), line, font=font, fill=action.fill)
        y += step


def render(name: str, actions: Iterable[EraseAction | TextAction]) -> None:
    source = RAW_ASSETS / name
    target = ASSETS / name
    image = Image.open(source).convert("RGBA")
    draw = ImageDraw.Draw(image)

    for action in actions:
        if isinstance(action, EraseAction):
            erase(draw, image, action)
        elif isinstance(action, OutlineAction):
            outline(draw, action)
        else:
            draw_text(draw, action)

    image.save(target)


def analyst_actions() -> list[EraseAction | TextAction]:
    panels = [
        (
            0,
            "市场",
            "目标：",
            "利用技术指标\n分析市场趋势",
            "关键要点：",
            "科技板块走强",
            "RSI：波动偏强，短线有过热迹象，\n需警惕价格回调……（ADX、布林带……）",
        ),
        (
            1265,
            "社交\n媒体",
            "目标：",
            "分析社交媒体\n情绪趋势",
            "关键要点：",
            "苹果社媒情绪\n（2024/11/4-11/19）",
            "正面情绪高点集中在 11 月 15 日与\n11 日……（负面情绪、高互动……）",
        ),
        (
            2530,
            "新闻",
            "目标：",
            "分析影响市场的\n全球经济趋势",
            "关键要点：",
            "全球经济趋势\n与板块观察",
            "美国经济政策引发分化反应……\n（AI 科技、半导体主线……）",
        ),
        (
            3795,
            "基本\n面",
            "目标：",
            "分析并评估公司\n财务与股价表现",
            "关键要点：",
            "苹果公司财务分析",
            "盈利能力强：利润率、ROE、ROA\n表现突出……（估值压力、流动性风险……）",
        ),
    ]

    actions: list[EraseAction | TextAction] = []
    for offset, badge, goal_head, goal_body, summary_head, title, body in panels:
        actions.extend(
            [
                EraseAction((offset + 44, 122, offset + 244, 248), radius=16),
                TextAction((offset + 56, 136, offset + 232, 230), badge, BLACK, FONT_BOLD, 44, 24, 1.04, "center", "middle"),
                EraseAction((offset + 276, 18, offset + 1162, 248), radius=10, fill=BLACK),
                TextAction((offset + 312, 34, offset + 520, 94), goal_head, TEXT_ON_DARK, FONT_BOLD, 48, 26),
                TextAction((offset + 312, 84, offset + 1110, 234), goal_body, TEXT_ON_DARK, FONT_BOLD, 54, 28, 1.18),
                EraseAction((offset + 52, 326, offset + 620, 394), radius=12),
                TextAction((offset + 78, 336, offset + 510, 390), summary_head, TEXT_SOFT, FONT_BOLD, 40, 24),
                EraseAction((offset + 170, 416, offset + 1112, 510), radius=12),
                TextAction((offset + 196, 424, offset + 1080, 500), title, TEXT_DARK, FONT_BOLD, 50, 28, 1.08),
                EraseAction((offset + 42, 516, offset + 1122, 648), radius=12),
                TextAction((offset + 72, 528, offset + 1088, 636), body, TEXT_MID, FONT_BOLD, 34, 20, 1.2),
            ]
        )
    return actions


def researcher_actions() -> list[EraseAction | TextAction]:
    return [
        EraseAction((48, 128, 244, 242), radius=16),
        TextAction((64, 140, 224, 228), "看多\n研究员", GREEN, FONT_BOLD, 42, 24, 1.02, "center", "middle"),
        EraseAction((266, 22, 994, 252), radius=10, fill=BLACK),
        TextAction((292, 40, 520, 96), "目标：", TEXT_ON_DARK, FONT_BOLD, 50, 28),
        TextAction((292, 92, 940, 232), "评估苹果公司的\n投资潜力", TEXT_ON_DARK, FONT_BOLD, 62, 30, 1.16),
        EraseAction((70, 332, 648, 394), radius=12),
        TextAction((92, 340, 470, 388), "关键要点：", TEXT_SOFT, FONT_BOLD, 40, 24),
        EraseAction((150, 430, 996, 526), radius=12),
        TextAction((182, 440, 960, 514), "苹果投资展望", TEXT_DARK, FONT_BOLD, 58, 30),
        EraseAction((68, 542, 1014, 692), radius=12),
        TextAction((96, 556, 984, 678), "增长潜力：AI 驱动的智能家居扩张有望带动营收……\n（基本面强劲、市场情绪改善……）", TEXT_MID, FONT_BOLD, 34, 20, 1.18),
        EraseAction((1452, 128, 1650, 242), radius=16),
        TextAction((1468, 140, 1632, 228), "看空\n研究员", RED, FONT_BOLD, 42, 24, 1.02, "center", "middle"),
        EraseAction((1670, 22, 2406, 252), radius=10, fill=BLACK),
        TextAction((1700, 40, 1928, 96), "目标：", TEXT_ON_DARK, FONT_BOLD, 50, 28),
        TextAction((1700, 92, 2350, 232), "评估投资苹果的\n主要风险", TEXT_ON_DARK, FONT_BOLD, 62, 30, 1.16),
        EraseAction((1112, 272, 1386, 348), radius=14, fill=BLACK),
        TextAction((1120, 280, 1378, 342), "辩论", TEXT_ON_DARK, FONT_BOLD, 52, 28, 1.08, "center", "middle"),
        EraseAction((1072, 344, 1430, 416), radius=14, fill=BLACK),
        EraseAction((1480, 332, 2056, 394), radius=12),
        TextAction((1502, 340, 1880, 388), "关键要点：", TEXT_SOFT, FONT_BOLD, 40, 24),
        EraseAction((1588, 430, 2394, 526), radius=12),
        TextAction((1614, 440, 2360, 514), "苹果投资风险", TEXT_DARK, FONT_BOLD, 58, 30),
        EraseAction((1478, 542, 2416, 692), radius=12),
        TextAction((1504, 556, 2386, 678), "竞争挑战：智能家居布局偏晚……\n（地缘紧张、估值与流动性……）", TEXT_MID, FONT_BOLD, 34, 20, 1.18),
    ]


def risk_actions() -> list[EraseAction | TextAction]:
    return [
        EraseAction((46, 114, 196, 198), radius=14),
        TextAction((54, 124, 186, 184), "激进", WHITE, FONT_BOLD, 36, 20, 1.0, "center", "middle"),
        EraseAction((220, 36, 432, 102), radius=10, fill=BLACK),
        TextAction((224, 46, 428, 98), "目标:", TEXT_ON_DARK, FONT_BOLD, 42, 24),
        EraseAction((220, 102, 1038, 174), radius=10, fill=BLACK),
        EraseAction((220, 160, 870, 226), radius=10, fill=BLACK),
        TextAction((224, 108, 804, 214), "主张高收益、高风险的\n投资策略", TEXT_ON_DARK, FONT_REGULAR, 54, 30, 1.14),
        EraseAction((46, 354, 196, 438), radius=14),
        TextAction((54, 364, 186, 424), "中性", WHITE, FONT_BOLD, 36, 20, 1.0, "center", "middle"),
        EraseAction((220, 276, 432, 342), radius=10, fill=BLACK),
        TextAction((224, 286, 428, 338), "目标:", TEXT_ON_DARK, FONT_BOLD, 42, 24),
        EraseAction((220, 332, 1038, 404), radius=10, fill=BLACK),
        EraseAction((220, 390, 912, 464), radius=10, fill=BLACK),
        TextAction((224, 340, 760, 448), "对苹果投资提供\n均衡视角", TEXT_ON_DARK, FONT_REGULAR, 54, 30, 1.14),
        EraseAction((46, 594, 196, 678), radius=14),
        TextAction((54, 604, 186, 664), "保守", WHITE, FONT_BOLD, 36, 20, 1.0, "center", "middle"),
        EraseAction((220, 516, 432, 582), radius=10, fill=BLACK),
        TextAction((224, 526, 428, 578), "目标:", TEXT_ON_DARK, FONT_BOLD, 42, 24),
        EraseAction((220, 572, 1038, 646), radius=10, fill=BLACK),
        EraseAction((220, 634, 1052, 714), radius=10, fill=BLACK),
        TextAction((224, 580, 860, 696), "强调稳健投资策略\n并注重风险缓释", TEXT_ON_DARK, FONT_REGULAR, 54, 30, 1.14),
        EraseAction((1006, 272, 1272, 354), radius=14, fill=BLACK),
        TextAction((1016, 278, 1260, 346), "报告", TEXT_ON_DARK, FONT_BOLD, 42, 24, 1.0, "center", "middle"),
        EraseAction((1188, 292, 1328, 352), radius=10, fill=BLACK),
        EraseAction((1324, 288, 1368, 344), radius=8, fill=BLACK),
        EraseAction((1320, 308, 1362, 330), radius=6, fill=BLACK),
        EraseAction((1452, 130, 1650, 242), radius=16),
        TextAction((1468, 142, 1634, 228), "经理", BLUE, FONT_BOLD, 42, 24, 1.0, "center", "middle"),
        EraseAction((1668, 32, 1950, 104), radius=10, fill=BLACK),
        TextAction((1690, 44, 1920, 98), "目标:", TEXT_ON_DARK, FONT_BOLD, 50, 28),
        EraseAction((1664, 96, 2486, 174), radius=10, fill=BLACK),
        EraseAction((1664, 166, 2338, 252), radius=10, fill=BLACK),
        TextAction((1690, 104, 2328, 236), "基于市场分析给出\n投资建议", TEXT_ON_DARK, FONT_REGULAR, 62, 30, 1.14),
        EraseAction((1484, 334, 2072, 394), radius=12),
        TextAction((1504, 340, 1896, 388), "关键要点:", TEXT_SOFT, FONT_REGULAR, 40, 24),
        EraseAction((1580, 430, 2422, 522), radius=12),
        TextAction((1608, 438, 2390, 512), "苹果买入建议", TEXT_DARK, FONT_BOLD, 60, 30),
        EraseAction((1484, 544, 2414, 694), radius=12),
        TextAction((1498, 556, 2390, 682), "基本面强劲: 盈利增长与市值表现稳健……\n（创新领先、抗风险韧性……）", TEXT_MID, FONT_REGULAR, 34, 20, 1.16),
    ]


def trader_actions() -> list[EraseAction | TextAction]:
    return [
        EraseAction((78, 158, 274, 292), radius=16),
        TextAction((96, 170, 258, 278), "交易员", PURPLE, FONT_BOLD, 44, 24, 1.02, "center", "middle"),
        EraseAction((312, 48, 1232, 300), radius=10, fill=BLACK),
        TextAction((340, 76, 546, 126), "目标：", TEXT_ON_DARK, FONT_BOLD, 52, 28),
        TextAction((340, 132, 1170, 282), "评估并把握\n市场机会", TEXT_ON_DARK, FONT_BOLD, 66, 32, 1.16),
        EraseAction((102, 394, 648, 466), radius=12),
        TextAction((122, 404, 494, 458), "关键要点：", TEXT_SOFT, FONT_BOLD, 44, 24),
        EraseAction((220, 452, 1120, 558), radius=12),
        TextAction((248, 462, 1082, 544), "苹果交易决策", TEXT_DARK, FONT_BOLD, 62, 32),
        EraseAction((98, 578, 1146, 700), radius=12),
        TextAction((122, 592, 1110, 684), "财务表现强：盈利能力、现金流与利润率稳健……\n（增长潜力、估值风险……）", TEXT_MID, FONT_BOLD, 36, 20, 1.18),
        EraseAction((1362, 88, 1744, 146), radius=12),
        TextAction((1378, 92, 1724, 142), "决策", TEXT_SOFT, FONT_BOLD, 48, 26),
        EraseAction((1450, 166, 2368, 266), radius=12),
        TextAction((1510, 174, 2332, 258), "买入苹果股票", GREEN, FONT_BOLD, 64, 30, 1.08),
        EraseAction((1360, 298, 1778, 356), radius=12),
        TextAction((1374, 304, 1758, 352), "理由：", TEXT_SOFT, FONT_BOLD, 48, 24),
        EraseAction((1486, 332, 1528, 370), radius=10, sample_box=(1538, 332, 1588, 370)),
        EraseAction((1550, 340, 1602, 366), radius=10, sample_box=(1610, 340, 1660, 366)),
        EraseAction((1312, 364, 2392, 532), radius=12),
        TextAction((1384, 378, 2328, 512), "基本面与增长前景\n强于估值和流动性风险。", TEXT_SOFT, FONT_REGULAR, 46, 24, 1.16),
        EraseAction((1360, 520, 1830, 580), radius=12),
        TextAction((1374, 526, 1810, 576), "建议：", TEXT_SOFT, FONT_BOLD, 48, 24),
        EraseAction((1312, 582, 2440, 718), radius=12),
        TextAction((1384, 596, 2362, 700), "尽管短期仍有风险，\n但可为长期增长布局买入。", TEXT_SOFT, FONT_REGULAR, 46, 24, 1.16),
    ]


def main() -> None:
    render("analyst.png", analyst_actions())
    render("researcher.png", researcher_actions())
    render("risk.png", risk_actions())
    render("trader.png", trader_actions())


if __name__ == "__main__":
    main()

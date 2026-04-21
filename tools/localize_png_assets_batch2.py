from __future__ import annotations

from localize_png_assets import (
    BLACK,
    BLUE,
    FONT_BOLD,
    FONT_REGULAR,
    GREEN,
    RED,
    TEXT_MID,
    WHITE,
    EraseAction,
    OutlineAction,
    TextAction,
    render,
)


LIGHT_GRAY = (182, 182, 182)
LIGHT_PANEL = (231, 231, 231)
TRADER_PANEL = (239, 233, 251)
MANAGER_PANEL = (229, 233, 253)
DISCUSSION_PANEL = (246, 222, 178)


def schema_actions() -> list[EraseAction | OutlineAction | TextAction]:
    actions: list[EraseAction | OutlineAction | TextAction] = []

    badges = [
        ((28, 118, 204, 198), "市场"),
        ((18, 330, 210, 452), "社交\n媒体"),
        ((36, 626, 198, 722), "新闻"),
        ((18, 890, 206, 1042), "基本\n面"),
    ]
    for box, text in badges:
        actions.append(EraseAction(box, radius=10))
        actions.append(
            TextAction(
                box,
                text,
                BLACK,
                FONT_BOLD,
                max_size=48,
                min_size=24,
                line_spacing=1.02,
                align="center",
                valign="middle",
            )
        )

    bottom_items = [
        ((284, 884, 556, 1040), "公司\n概况"),
        ((592, 884, 888, 1040), "财务\n历史"),
        ((888, 884, 1198, 1040), "内部人\n交易"),
    ]
    for box, text in bottom_items:
        actions.append(EraseAction(box, radius=8, fill=WHITE))
        actions.append(
            TextAction(
                box,
                text,
                BLACK,
                FONT_REGULAR,
                max_size=42,
                min_size=22,
                line_spacing=1.05,
                align="center",
                valign="middle",
            )
        )

    risk_rows = [
        ((2680, 96, 3028, 172), "激进"),
        ((2680, 200, 2960, 272), "中性"),
        ((2680, 300, 3034, 374), "保守"),
    ]
    overview_rows = [
        ((2212, 844, 2418, 886), (2412, 844, 2688, 886), "分析师：", "收集市场关键要点"),
        ((2212, 882, 2418, 924), (2412, 882, 2688, 924), "研究员：", "评估风险收益"),
        ((2212, 920, 2418, 962), (2412, 920, 2688, 962), "交易员：", "提出交易策略"),
        ((2212, 958, 2476, 1000), (2470, 958, 2688, 1000), "风控团队：", "管理风险敞口"),
        ((2212, 996, 2380, 1034), (2374, 996, 2688, 1034), "经理：", "批准交易执行"),
    ]

    actions.extend(
        [
            EraseAction((1468, 182, 1832, 300), radius=14),
            TextAction((1480, 194, 1820, 292), "看多", GREEN, FONT_BOLD, 72, 34, 1.0, "center", "middle"),
            EraseAction((1488, 424, 1790, 490), radius=30, fill=DISCUSSION_PANEL),
            OutlineAction((1488, 424, 1790, 490), BLACK, width=3, radius=30),
            TextAction((1532, 432, 1758, 486), "讨论", BLACK, FONT_REGULAR, 38, 22, 1.0, "center", "middle"),
            EraseAction((1470, 700, 1834, 852), radius=18),
            TextAction((1482, 714, 1822, 840), "看空", RED, FONT_BOLD, 72, 34, 1.0, "center", "middle"),
            EraseAction((1398, 950, 1866, 1042), radius=6),
            TextAction((1408, 964, 1856, 1030), "研究团队", WHITE, FONT_REGULAR, 38, 22, 1.0, "center", "middle"),
            EraseAction((1936, 82, 2278, 150), radius=6, fill=WHITE),
            TextAction((1958, 86, 2266, 146), "看多依据", BLACK, FONT_REGULAR, 44, 24, 1.0, "left", "middle"),
            EraseAction((1940, 742, 2278, 806), radius=6, fill=WHITE),
            TextAction((1958, 746, 2266, 802), "看空依据", BLACK, FONT_REGULAR, 44, 24, 1.0, "left", "middle"),
            EraseAction((2024, 532, 2274, 612), radius=8, fill=TRADER_PANEL),
            TextAction((2040, 536, 2258, 598), "交易员", BLACK, FONT_REGULAR, 40, 24, 1.0, "center", "middle"),
            EraseAction((2348, 466, 2680, 572), radius=8, fill=WHITE),
            TextAction((2418, 474, 2664, 564), "交易\n提案", BLACK, FONT_REGULAR, 44, 24, 1.06, "center", "middle"),
            EraseAction((2588, 14, 3162, 76), radius=6),
            TextAction((2602, 20, 3148, 70), "风控团队", WHITE, FONT_REGULAR, 36, 22, 1.0, "center", "middle"),
            EraseAction((3194, 346, 3434, 408), radius=8, fill=MANAGER_PANEL),
            TextAction((3202, 348, 3426, 404), "经理", BLACK, FONT_REGULAR, 40, 24, 1.0, "center", "middle"),
            EraseAction((3070, 548, 3286, 618), radius=6, fill=WHITE),
            TextAction((3090, 552, 3268, 610), "决策", BLACK, FONT_REGULAR, 42, 24, 1.0, "left", "middle"),
            EraseAction((2518, 646, 3014, 724), radius=8, fill=LIGHT_PANEL),
            TextAction((2540, 652, 2996, 714), "OpenAI o1 深度思考", TEXT_MID, FONT_REGULAR, 34, 22, 1.0, "left", "middle"),
            EraseAction((2008, 852, 2236, 1024), radius=8, fill=LIGHT_PANEL),
            EraseAction((2210, 842, 2692, 1034), radius=8, fill=LIGHT_PANEL),
            TextAction((2016, 866, 2230, 1012), "团队\n概览", BLACK, FONT_BOLD, 36, 20, 1.0, "center", "middle"),
            EraseAction((2990, 896, 3440, 1040), radius=18),
            TextAction((3004, 910, 3428, 1028), "执行", WHITE, FONT_REGULAR, 78, 34, 1.0, "center", "middle"),
        ]
    )

    for box, text in risk_rows:
        actions.append(EraseAction(box, radius=6, fill=WHITE))
        actions.append(
            TextAction(
                (box[0] + 10, box[1], box[2], box[3]),
                text,
                BLACK,
                FONT_REGULAR,
                40,
                24,
                1.0,
                "left",
                "middle",
            )
        )

    for role_box, desc_box, role, desc in overview_rows:
        actions.append(
            TextAction(
                role_box,
                role,
                BLACK,
                FONT_BOLD,
                28,
                20,
                1.0,
                "left",
                "middle",
            )
        )
        actions.append(
            TextAction(
                desc_box,
                desc,
                BLACK,
                FONT_REGULAR,
                28,
                20,
                1.0,
                "left",
                "middle",
            )
        )

    return actions


def wechat_actions() -> list[EraseAction | TextAction]:
    return [
        EraseAction((318, 112, 914, 280), radius=8, fill=WHITE),
        TextAction((332, 120, 900, 198), "TradingResearch 小助手", BLACK, FONT_REGULAR, 52, 24, 1.0, "left", "middle"),
        TextAction((332, 190, 900, 262), "美国", LIGHT_GRAY, FONT_REGULAR, 42, 22, 1.0, "left", "middle"),
        EraseAction((170, 1180, 926, 1338), radius=8, fill=WHITE),
        TextAction((190, 1204, 906, 1294), "扫描二维码添加好友", LIGHT_GRAY, FONT_REGULAR, 46, 22, 1.0, "center", "middle"),
    ]


def main() -> None:
    render("schema.png", schema_actions())
    render("wechat.png", wechat_actions())


if __name__ == "__main__":
    main()

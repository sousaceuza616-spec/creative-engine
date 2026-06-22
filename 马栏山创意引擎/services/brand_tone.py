"""
品牌调性推导服务
将品牌调性的隐式判断逻辑从 UI 层提取为可测试的服务函数
"""
from typing import Optional


def derive_brand_tone(brief: Optional[str], user_tone: Optional[str] = None) -> str:
    """根据策划需求自动推导品牌调性

    优先使用用户明确指定的调性；如未指定则根据 brief 的关键词自动匹配。
    这是开闭原则友好的设计：新增调性只需在这一个函数中维护映射表。

    Args:
        brief: 策划需求文本（可为空）
        user_tone: 用户手动填写的品牌调性（可选）

    Returns:
        品牌调性描述字符串
    """
    # 用户已明确指定 → 直接使用
    if user_tone and user_tone.strip():
        return user_tone.strip()

    # 未指定 → 根据 brief 关键词自动推导
    brief_lower = (brief or "").lower()

    # 定义关键词 → 调性的映射表（新增调性只需扩展此列表）
    tone_rules: list[tuple[list[str], str]] = [
        (["茶颜", "国潮", "传统", "东方", "文化", "非遗", "古典", "古风", "诗意"],
         "内敛雅致、东方美学、文化底蕴"),
        (["科技", "ai", "智能", "数字化", "创新", "未来", "编程", "算法", "数据"],
         "创新前沿、科技感、未来感"),
        (["年轻", "潮流", "社交", "活力", "时尚", "潮玩", "街头", "hip-hop", "二次元"],
         "年轻活力、时尚潮流、社交属性"),
        (["自然", "环保", "绿色", "可持续", "生态", "有机", "低碳"],
         "自然清新、环保理念、可持续生活"),
        (["高端", "奢华", "精致", "品质", "匠心", "定制", "轻奢"],
         "高端精致、品质生活、匠心美学"),
    ]

    matched_tones: list[str] = []
    for keywords, tone in tone_rules:
        if any(kw in brief_lower for kw in keywords):
            matched_tones.append(tone)

    # 如果匹配到多个，取第一个；否则用默认
    if matched_tones:
        return matched_tones[0]

    return "内敛雅致、东方美学、文化底蕴"

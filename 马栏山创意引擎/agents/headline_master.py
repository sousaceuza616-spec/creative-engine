"""
标题大师 Agent
多风格标题生成 + 自适应迭代优化
日期由 orchestrator 传入，避免重复工具调用
"""
from __future__ import annotations

import logging
from typing import Any

from config import get_client, DEEPSEEK_MODEL, api_call_with_retry
from prompts.headline_master import (
    GENERATE_SYSTEM_PROMPT,
    GENERATE_USER_TEMPLATE,
    REFINE_SYSTEM_PROMPT,
    REFINE_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)
client = get_client()

# 各方向的备用标题（API 调用失败时使用）
_FALLBACK_TITLES: dict[str, list[str]] = {
    "情感向": ["一键心动，治愈心灵的温暖角落", "情感共鸣，触动人心的品牌故事"],
    "科技向": ["颠覆想象，未来已来的智能生活", "科技赋能，创新引领的行业变革"],
    "国潮向": ["千年传承，东方美学的当代演绎", "国潮崛起，传统文化的全新表达"],
}


def generate_headlines(
    brief: str,
    angle: str,
    date_str: str | None = None,
    count: int = 2,
) -> list[str]:
    """生成多个创意标题

    Args:
        brief: 策划需求文本
        angle: 创意方向（情感向 / 科技向 / 国潮向 等）
        date_str: 当前日期字符串（由 orchestrator 传入）
        count: 需要生成的标题数量

    Returns:
        标题字符串列表
    """
    date_hint = f"当前日期：{date_str}。" if date_str else ""

    system_prompt = GENERATE_SYSTEM_PROMPT.format(date_hint=date_hint)
    user_prompt = GENERATE_USER_TEMPLATE.format(
        brief=brief,
        angle=angle,
        count=count,
    )

    try:
        response = api_call_with_retry(
            lambda: client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.8,
                max_tokens=500,
            )
        )
        result = response.choices[0].message.content
        raw_list = result.strip().split("\n")
        result_list: list[str] = []
        for h in raw_list:
            h = h.strip()
            h = h.lstrip("0123456789.-   ")
            if h and h not in result_list:
                result_list.append(h)
        return result_list[:count]

    except Exception as e:
        logger.exception("generate_headlines failed for angle: %s", angle)
        fb_list = _FALLBACK_TITLES.get(angle, ["创意标题 A", "创意标题 B"])
        return fb_list[:count]


def refine_headline(
    feedback: str,
    original_headline: str,
    brief: str,
    angle: str,
    date_str: str | None = None,
) -> str:
    """根据主编意见优化标题

    Args:
        feedback: 主编反馈意见
        original_headline: 原标题
        brief: 策划需求文本
        angle: 创意方向
        date_str: 当前日期字符串（由 orchestrator 传入）

    Returns:
        优化后的标题
    """
    try:
        response = api_call_with_retry(
            lambda: client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": REFINE_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": REFINE_USER_TEMPLATE.format(
                            brief=brief,
                            angle=angle,
                            original_headline=original_headline,
                            feedback=feedback,
                        ),
                    },
                ],
                temperature=0.7,
                max_tokens=200,
            )
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("refine_headline failed for: %s", original_headline[:50])
        return original_headline

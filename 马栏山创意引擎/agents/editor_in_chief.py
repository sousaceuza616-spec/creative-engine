"""
主编 Agent
大纲生成 + 品牌调性理解与质量把控 + 语义级审核
日期由 orchestrator 传入，避免重复工具调用
"""
from __future__ import annotations

import logging
from typing import Any

from config import get_client, DEEPSEEK_MODEL, api_call_with_retry
from prompts.editor_in_chief import (
    OUTLINE_SYSTEM_PROMPT,
    OUTLINE_USER_TEMPLATE,
    REVIEW_SYSTEM_PROMPT,
    REVIEW_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)
client = get_client()


def generate_outline(
    brief: str,
    analysis_results: list[dict[str, Any]],
    date_str: str | None = None,
) -> str:
    """基于 brief 和分析结果生成策创方案大纲

    Args:
        brief: 策划需求文本
        analysis_results: 各数据源分析结果列表
        date_str: 当前日期字符串（由 orchestrator 传入）

    Returns:
        大纲文本（Markdown 格式）
    """
    analyses_text = "\n\n".join([
        f"=== {r['source']}（{r['angle']}）===\n{r.get('analysis', '无分析结果')}"
        for r in analysis_results
    ])

    date_hint = f"\n当前日期：{date_str}。" if date_str else ""
    system_prompt = OUTLINE_SYSTEM_PROMPT.format(date_hint=date_hint)
    user_prompt = OUTLINE_USER_TEMPLATE.format(
        brief=brief,
        analyses_text=analyses_text,
    )

    try:
        response = api_call_with_retry(
            lambda: client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.exception("generate_outline failed for brief: %s", brief[:50])
        return "【方案大纲生成失败】\n\n请检查网络连接后重试。"


def review_headline(
    headline: str,
    brief: str,
    brand_tone: str,
    angle: str,
    date_str: str | None = None,
) -> dict[str, Any]:
    """语义级审核标题：判断是否符合品牌调性

    Args:
        headline: 待审核的标题
        brief: 策划需求文本
        brand_tone: 品牌调性描述
        angle: 创意方向
        date_str: 当前日期字符串（由 orchestrator 传入）

    Returns:
        dict: {approved: bool, result: str, rejected: bool}
    """
    user_prompt = REVIEW_USER_TEMPLATE.format(
        brief=brief,
        brand_tone=brand_tone,
        angle=angle,
        headline=headline,
    )

    try:
        response = api_call_with_retry(
            lambda: client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )
        )
        result = response.choices[0].message.content.strip()
        is_rejected = result.startswith("驳回")
        return {
            "approved": not is_rejected,
            "result": result,
            "rejected": is_rejected,
        }
    except Exception as e:
        logger.exception("review_headline failed for: %s", headline[:50])
        return {
            "approved": False,
            "result": "审核服务异常，标题被驳回（安全兜底）",
            "rejected": True,
        }


def review_batch_headlines(
    headlines_with_meta: list[dict[str, Any]],
    date_str: str | None = None,
) -> list[dict[str, Any]]:
    """批量审核标题，返回每个标题的审核结果

    Args:
        headlines_with_meta: 包含 headline/brief/brand_tone/angle 的字典列表
        date_str: 当前日期字符串（由 orchestrator 传入）

    Returns:
        每个 item 追加 review 字段后的列表
    """
    results: list[dict[str, Any]] = []
    for item in headlines_with_meta:
        review = review_headline(
            headline=item["headline"],
            brief=item["brief"],
            brand_tone=item["brand_tone"],
            angle=item["angle"],
            date_str=date_str,
        )
        results.append({**item, "review": review})
    return results

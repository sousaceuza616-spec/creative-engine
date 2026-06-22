"""
热点分析师 Agent
基于预置数据集分析竞品趋势，提炼爆款逻辑
"""
from __future__ import annotations

import logging
from typing import Any

from config import get_client, DEEPSEEK_MODEL, api_call_with_retry
from data.loader import load_data
from prompts.trend_analyst import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)
client = get_client()


def analyze_trend(
    brief: str,
    data_source_name: str,
    date_str: str | None = None,
) -> dict[str, Any]:
    """基于指定数据源分析趋势

    Args:
        brief: 策划需求文本
        data_source_name: 数据源名称（小红书 / B站 / 抖音）
        date_str: 当前日期字符串（由 orchestrator 传入，避免重复工具调用）

    Returns:
        dict: 包含 source, angle, analysis, posts_count, fallback 字段
    """
    data = load_data(data_source_name)
    if not data:
        return {
            "source": data_source_name,
            "error": f"未找到{data_source_name}数据",
            "fallback": True,
        }

    posts = data.get("posts", [])
    posts_summary = "\n".join([
        f"- 《{p['title']}》| 互动量:{p.get('likes', p.get('plays', 'N/A'))} | "
        f"主题:{p['theme']} | 洞察:{p['key_insight']}"
        for p in posts
    ])

    date_hint = f"当前日期：{date_str}。" if date_str else ""
    angle = data.get("angle", data_source_name)

    system_prompt = SYSTEM_PROMPT.format(
        data_source=data_source_name,
        angle=angle,
        date_hint=date_hint,
    )

    user_prompt = USER_PROMPT_TEMPLATE.format(
        brief=brief,
        data_source=data_source_name,
        angle=angle,
        posts_summary=posts_summary,
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
                max_tokens=1500,
            )
        )
        analysis = response.choices[0].message.content
        fallback = False
    except Exception as e:
        logger.exception("analyze_trend failed for source: %s", data_source_name)
        fallback_insight = posts[0]["key_insight"] if posts else "无"
        analysis = (
            f"（API调用失败，使用本地预置数据兜底）\n\n"
            f"数据源：{data_source_name}\n"
            f"数据量：{len(posts)}条\n"
            f"核心洞察：{fallback_insight}"
        )
        fallback = True

    return {
        "source": data_source_name,
        "angle": angle,
        "analysis": analysis,
        "posts_count": len(posts),
        "fallback": fallback,
    }

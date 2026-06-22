"""
主控 Agent：任务规划、分发与整合
日期在入口处一次性获取，传递给所有 Agent
"""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Callable, Optional

from agents.trend_analyst import analyze_trend
from agents.headline_master import generate_headlines, refine_headline
from agents.editor_in_chief import generate_outline, review_headline

logger = logging.getLogger(__name__)

DATA_SOURCES: list[str] = ["小红书", "B站", "抖音"]

# 每个数据源对应的创意角度
ANGLE_MAP: dict[str, str] = {
    "小红书": "情感向",
    "B站": "科技向",
    "抖音": "国潮向",
}


def _get_date_str() -> str:
    """一次性获取当前日期字符串"""
    now = datetime.now()
    weekdays_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return f"{now.strftime('%Y年%m月%d日')}（{weekdays_cn[now.weekday()]}）"


def _review_with_retry(
    headline: str,
    brief: str,
    brand_tone: str,
    angle: str,
    date_str: str,
    max_iterations: int = 2,
) -> dict[str, Any]:
    """审核标题，若被驳回则迭代优化并二次审核

    最多迭代 max_iterations 轮，最终返回末次审核结果。
    确保重写后的标题也被审核，避免绕过审核流程。

    Args:
        headline: 原标题
        brief: 策划需求
        brand_tone: 品牌调性
        angle: 创意方向
        date_str: 当前日期
        max_iterations: 最大迭代轮数（默认 2）

    Returns:
        dict: 包含 headline, review, refined, iterations 等字段
    """
    current_headline = headline
    iteration_results: list[dict[str, Any]] = []

    for iteration in range(max_iterations + 1):
        review = review_headline(
            headline=current_headline,
            brief=brief,
            brand_tone=brand_tone,
            angle=angle,
            date_str=date_str,
        )

        iteration_results.append({
            "iteration": iteration,
            "headline": current_headline,
            "review": review,
        })

        # 审核通过 → 结束迭代
        if not review["rejected"]:
            break

        # 最后一次迭代被驳回 → 不再重试
        if iteration >= max_iterations:
            break

        # 被驳回 → 优化标题后进入下一轮审核
        refined = refine_headline(
            feedback=review["result"],
            original_headline=current_headline,
            brief=brief,
            angle=angle,
            date_str=date_str,
        )
        current_headline = refined

    return {
        "original_headline": headline,
        "final_headline": current_headline,
        "final_review": iteration_results[-1]["review"],
        "iterations": iteration_results,
        "was_refined": headline != current_headline,
    }


def run_full_pipeline(
    brief: str,
    brand_tone: str = "内敛雅致、东方美学、文化底蕴",
    progress_callback: Optional[Callable[[str, str], None]] = None,
) -> dict[str, Any]:
    """运行完整的策创流水线

    Args:
        brief: 策划需求文本
        brand_tone: 品牌调性描述
        progress_callback: 进度回调函数，接收 (step_id, message)

    Returns:
        dict: 包含 brief, brand_tone, steps, all_analyses,
              all_headlines, reviewed_headlines, rejection_demo, outline
    """
    # 一次性获取当前日期
    date_str = _get_date_str()

    if progress_callback:
        progress_callback("analysis", "Step 1/4: 热点分析师正在分析三路数据源...")

    steps: dict[str, Any] = {}
    all_analyses: list[dict[str, Any]] = []

    # Step 1: 热点分析（三路并行）
    steps["analysis"] = {"status": "running", "detail": {}}
    if progress_callback:
        progress_callback("analysis", "Step 1/4: 热点分析师正在并行分析三路数据源...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(analyze_trend, brief, ds, date_str): ds
            for ds in DATA_SOURCES
        }
        for future in as_completed(futures):
            ds = futures[future]
            result = future.result()
            all_analyses.append(result)
            steps["analysis"]["detail"][ds] = result
    steps["analysis"]["status"] = "completed"
    if progress_callback:
        progress_callback("headlines", "Step 2/4: 标题大师正在生成创意标题...")

    # Step 2: 标题生成
    steps["headlines"] = {"status": "running", "detail": {}}
    all_headlines: list[dict[str, Any]] = []
    for ds in DATA_SOURCES:
        angle = ANGLE_MAP.get(ds, ds)
        headlines = generate_headlines(brief, angle, date_str, count=2)
        for h in headlines:
            all_headlines.append({
                "headline": h,
                "angle": angle,
                "source": ds,
                "brief": brief,
                "brand_tone": brand_tone,
            })
        steps["headlines"]["detail"][ds] = {"angle": angle, "headlines": headlines}
    steps["headlines"]["status"] = "completed"
    if progress_callback:
        progress_callback("review", "Step 3/4: 主编正在进行语义级审核...")

    # Step 3: 主编审核标题（支持迭代优化 + 二次审核）
    steps["review"] = {"status": "running", "detail": {}}
    reviewed: list[dict[str, Any]] = []
    rejection_demo: Optional[dict[str, Any]] = None

    for item in all_headlines:
        # 使用带二次审核的审核流程
        review_result = _review_with_retry(
            headline=item["headline"],
            brief=item["brief"],
            brand_tone=item["brand_tone"],
            angle=item["angle"],
            date_str=date_str,
            max_iterations=2,
        )
        reviewed.append({**item, "review_result": review_result})

        # 记录第一个被驳回且已优化的案例作为 WOW 时刻展示
        if review_result["was_refined"] and rejection_demo is None:
            first_iter = review_result["iterations"][0]
            rejection_demo = {
                "original_headline": review_result["original_headline"],
                "refined_headline": review_result["final_headline"],
                "feedback": first_iter["review"]["result"],
                "angle": item["angle"],
                "source": item["source"],
            }

        steps["review"]["detail"][item["headline"]] = review_result["final_review"]

    steps["review"]["status"] = "completed"
    if progress_callback:
        progress_callback("outline", "Step 4/4: 主编正在生成策创方案大纲...")

    # Step 4: 生成方案大纲
    steps["outline"] = {"status": "running"}
    outline = generate_outline(brief, all_analyses, date_str)
    steps["outline"]["status"] = "completed"
    steps["outline"]["content"] = outline

    return {
        "brief": brief,
        "brand_tone": brand_tone,
        "steps": steps,
        "all_analyses": all_analyses,
        "all_headlines": all_headlines,
        "reviewed_headlines": reviewed,
        "rejection_demo": rejection_demo,
        "outline": outline,
    }

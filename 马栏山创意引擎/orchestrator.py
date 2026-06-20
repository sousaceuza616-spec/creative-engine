"""
主控 Agent：任务规划、分发与整合
日期在入口处一次性获取，传递给所有 Agent
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from agents.trend_analyst import analyze_trend
from agents.headline_master import generate_headlines, refine_headline
from agents.editor_in_chief import generate_outline, review_headline
from datetime import datetime

DATA_SOURCES = ["小红书", "B站", "抖音"]


def _get_date_str():
    """一次性获取当前日期字符串"""
    now = datetime.now()
    weekdays_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return "%s（%s）" % (now.strftime("%Y年%m月%d日"), weekdays_cn[now.weekday()])


def run_full_pipeline(brief, brand_tone="内敛雅致、东方美学、文化底蕴", progress_callback=None):
    # 一次性获取当前日期
    date_str = _get_date_str()

    if progress_callback:
        progress_callback("analysis", "Step 1/4: 热点分析师正在分析三路数据源...")

    steps = {}
    all_analyses = []

    # Step 1: 热点分析（三路并行）
    steps["analysis"] = {"status": "running", "detail": {}}
    if progress_callback:
        progress_callback("analysis", "Step 1/4: 热点分析师正在并行分析三路数据源...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(analyze_trend, brief, ds, date_str): ds for ds in DATA_SOURCES}
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
    all_headlines = []
    for ds in DATA_SOURCES:
        angle_map = {"小红书": "情感向", "B站": "科技向", "抖音": "国潮向"}
        angle = angle_map.get(ds, ds)
        headlines = generate_headlines(brief, angle, date_str, count=2)
        for h in headlines:
            all_headlines.append({
                "headline": h, "angle": angle, "source": ds,
                "brief": brief, "brand_tone": brand_tone
            })
        steps["headlines"]["detail"][ds] = {"angle": angle, "headlines": headlines}
    steps["headlines"]["status"] = "completed"
    if progress_callback:
        progress_callback("review", "Step 3/4: 主编正在进行语义级审核...")

    # Step 3: 主编审核标题
    steps["review"] = {"status": "running", "detail": {}}
    reviewed = []
    rejection_demo = None

    for item in all_headlines:
        review = review_headline(
            headline=item["headline"], brief=item["brief"],
            brand_tone=item["brand_tone"], angle=item["angle"],
            date_str=date_str
        )
        reviewed.append({**item, "review": review})

        if review["rejected"] and rejection_demo is None:
            rejection_demo = {
                "original_headline": item["headline"],
                "feedback": review["result"],
                "angle": item["angle"], "source": item["source"]
            }
            refined = refine_headline(
                feedback=review["result"], original_headline=item["headline"],
                brief=item["brief"], angle=item["angle"], date_str=date_str
            )
            rejection_demo["refined_headline"] = refined

        steps["review"]["detail"][item["headline"]] = review

    steps["review"]["status"] = "completed"
    if progress_callback:
        progress_callback("outline", "Step 4/4: 主编正在生成策创方案大纲...")

    # Step 4: 生成方案大纲
    steps["outline"] = {"status": "running"}
    outline = generate_outline(brief, all_analyses, date_str)
    steps["outline"]["status"] = "completed"
    steps["outline"]["content"] = outline

    return {
        "brief": brief, "brand_tone": brand_tone,
        "steps": steps, "all_analyses": all_analyses,
        "all_headlines": all_headlines, "reviewed_headlines": reviewed,
        "rejection_demo": rejection_demo, "outline": outline
    }

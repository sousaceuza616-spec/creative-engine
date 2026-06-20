"""
主编 Agent
大纲生成 + 品牌调性理解与质量把控 + 语义级审核
日期由 orchestrator 传入，避免重复工具调用
"""
import logging
from config import get_client, DEEPSEEK_MODEL

logger = logging.getLogger(__name__)
client = get_client()


def generate_outline(brief, analysis_results, date_str=None):
    """基于brief和分析结果生成策创方案大纲（date_str 由 orchestrator 传入）"""
    analyses_text = "\n\n".join([
        "=== %s（%s）===\n%s" % (r["source"], r["angle"], r.get("analysis", "无分析结果"))
        for r in analysis_results
    ])

    date_hint = ("当前日期：%s。" % date_str) if date_str else ""
    user_prompt = ("【策划需求】\n%s\n\n"
                   "【市场分析结果】\n%s\n\n"
                   "【任务】\n"
                   "基于以上分析，请生成一份完整的策创方案大纲，包含：\n"
                   "1. 方案主题（一句话）\n"
                   "2. 市场背景与机会\n"
                   "3. 核心策略\n"
                   "4. 三套创意方向（分别对应三个数据源角度）\n"
                   "5. 传播节奏建议\n"
                   "6. 落地执行要点\n\n"
                   "请保持专业、结构清晰、有可执行性。"
                   ) % (brief, analyses_text)

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": (
                    "你是资深的品牌主编。\n\n"
                    "## 角色\n"
                    "品牌策划领域的策略主编，擅长将多源市场分析整合为完整的策创方案。\n\n"
                    "## 大纲结构要求\n"
                    "1. 方案主题：一句话概括核心创意\n"
                    "2. 市场背景与机会：基于分析数据指出市场机会点\n"
                    "3. 核心策略：提出差异化的传播策略\n"
                    "4. 三套创意方向：分别对应三路数据源的角度\n"
                    "5. 传播节奏建议：按时间线给出内容发布节奏\n"
                    "6. 落地执行要点：具体可执行的行动项\n\n"
                    "## 写作风格\n"
                    "- 专业但不晦涩，可直接用于提案\n"
                    "- 每条建议必须有数据或洞察支撑\n"
                    "- 层次分明、结构清晰" + ("\n" + date_hint if date_hint else "")
                )},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.exception("generate_outline failed for brief: %s", brief[:50])
        return "【方案大纲生成失败】\n\n请检查网络连接后重试。"


def review_headline(headline, brief, brand_tone, angle, date_str=None):
    """语义级审核标题：判断是否符合品牌调性"""
    user_prompt = ("【策划需求】\n%s\n\n"
                   "【品牌调性】\n%s\n\n"
                   "【创意方向】\n%s\n\n"
                   "【待审核标题】\n%s\n\n"
                   "【任务】\n"
                   "请从品牌调性的角度审核这个标题，判断它是否符合品牌调性。\n\n"
                   "如果【符合品牌调性】，请回复：\n"
                   "通过\n\n"
                   "如果【不符合品牌调性】，请回复：\n"
                   "驳回。驳回理由：（具体说明为什么不符合品牌调性）\n"
                   "修改方向：（给出2-3个修改方向建议）\n\n"
                   "注意：驳回理由必须展示对品牌调性的深刻理解，而非简单的关键词过滤。"
                   ) % (brief, brand_tone, angle, headline)

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": (
                    "你是资深的品牌主编，负责创意内容的语义级审核。\n\n"
                    "## 审核标准\n"
                    "1. 严格依据设定的品牌调性进行审核，不是简单关键词过滤\n"
                    "2. 判断标题是否真正传达出品牌的核心气质\n"
                    "3. 标题本身是否有传播力和吸引力\n\n"
                    "## 审核流程\n"
                    "1. 理解品牌调性的核心关键词和气质\n"
                    "2. 判断标题的语气、用词是否匹配品牌调性\n"
                    "3. 如果不匹配，给出具体的驳回理由和修改方向\n\n"
                    "## 输出规则\n"
                    "- 符合调性：回复「通过」\n"
                    "- 不符合调性：回复「驳回。驳回理由：（具体说明）」"
                )},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        result = response.choices[0].message.content.strip()
        is_rejected = result.startswith("驳回")
        return {
            "approved": not is_rejected,
            "result": result,
            "rejected": is_rejected
        }
    except Exception as e:
        logger.exception("review_headline failed for: %s", headline[:50])
        return {
            "approved": False,
            "result": "审核服务异常，标题被驳回（安全兜底）",
            "rejected": True
        }


def review_batch_headlines(headlines_with_meta, date_str=None):
    """批量审核标题，返回每个标题的审核结果"""
    results = []
    for item in headlines_with_meta:
        review = review_headline(
            headline=item["headline"],
            brief=item["brief"],
            brand_tone=item["brand_tone"],
            angle=item["angle"],
            date_str=date_str
        )
        results.append({**item, "review": review})
    return results
